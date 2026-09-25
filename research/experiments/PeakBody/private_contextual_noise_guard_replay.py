#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import numpy as np
from scipy.signal import lfilter

import private_real_vocal_guard_measure as base


def _one_pole_band(x, sr, high_pass_hz, low_pass_hz):
    dt = 1.0 / sr
    rc = 1.0 / (2.0 * math.pi * max(1.0, high_pass_hz))
    a = rc / (rc + dt)
    high = lfilter([a, -a], [1.0, -a], x)
    alpha = 1.0 - math.exp(-2.0 * math.pi * max(1.0, low_pass_hz) / sr)
    return lfilter([alpha], [1.0, -(1.0 - alpha)], high)


def _power_env(x, coeff):
    return lfilter([coeff], [1.0, -(1.0 - coeff)], x * x)


def contextual_probability(x, sr):
    high = _one_pole_band(x, sr, 4000.0, 12000.0)
    mid = _one_pole_band(x, sr, 1000.0, 4000.0)
    broad = _one_pole_band(x, sr, 250.0, 12000.0)
    upper = _one_pole_band(x, sr, 7000.0, 12000.0)

    fast = 1.0 - math.exp(-1.0 / (0.008 * sr))
    slow = 1.0 - math.exp(-1.0 / (0.120 * sr))

    hp = _power_env(high, fast)
    mp = _power_env(mid, fast)
    bp = _power_env(broad, fast)
    up = _power_env(upper, fast)
    hs = _power_env(high, slow)

    eps = 1.0e-12
    high_db = 10.0 * np.log10(np.maximum(hp, eps))
    mid_db = 10.0 * np.log10(np.maximum(mp, eps))
    broad_db = 10.0 * np.log10(np.maximum(bp, eps))
    upper_db = 10.0 * np.log10(np.maximum(up, eps))
    slow_db = 10.0 * np.log10(np.maximum(hs, eps))

    def sigmoid(z):
        z = np.clip(z, -12.0, 12.0)
        return 1.0 / (1.0 + np.exp(-z))

    c1 = sigmoid(((high_db - broad_db) + 4.5) / 1.4)
    c2 = sigmoid(((high_db - mid_db) - 2.0) / 2.4)
    c3 = sigmoid(((high_db - slow_db) - 1.0) / 3.0)
    c4 = sigmoid(((upper_db - high_db) + 10.0) / 2.5)

    log_p = (
        0.45 * np.log(np.maximum(c1, 1.0e-6))
        + 0.30 * np.log(np.maximum(c2, 1.0e-6))
        + 0.10 * np.log(np.maximum(c3, 1.0e-6))
        + 0.15 * np.log(np.maximum(c4, 1.0e-6))
    )
    p = np.exp(log_p)
    p = np.where(broad_db < -90.0, 0.0, p)
    return np.clip(np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0)


def veto(periodicity):
    u = np.clip((periodicity - 0.55) / 0.25, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def retention(candidate, reference, mask):
    values = candidate[mask] / np.maximum(reference[mask], 1.0e-12)
    return {
        "count": int(len(values)),
        "median": float(np.median(values)),
        "p10": float(np.quantile(values, 0.1)),
        "p90": float(np.quantile(values, 0.9)),
        "min": float(np.min(values)),
    }


def analyze(path):
    sr, x = base.load_mono(path)
    win = int(round(0.040 * sr))
    hop = max(1, int(round(0.005 * sr)))
    ends = np.arange(win, len(x) + 1, hop, dtype=int)

    overall = np.sqrt(np.mean(x * x))
    overall_db = 20.0 * np.log10(max(overall, base.POWER_FLOOR))
    active_threshold = 10.0 ** (max(-60.0, overall_db - 30.0) / 20.0)
    cs = np.concatenate([[0.0], np.cumsum(x * x)])
    active = np.sqrt((cs[ends] - cs[ends - win]) / win) > active_threshold

    t = base.crest_series(x, sr)[ends - 1]
    spec = base.spectral_guard_series(x, sr)[ends - 1]
    low = base.low_ratio_series(x, sr)[ends - 1]
    per = base.periodicity_frames(x, sr, ends, win)
    psib = contextual_probability(x, sr)[ends - 1]

    v = veto(per)
    current = t * (1.0 - 0.75 * spec * (1.0 - per))
    simple = t * (1.0 - 0.75 * spec * (1.0 - v))
    context = t * (1.0 - 0.75 * np.maximum(spec, psib) * (1.0 - v))

    noise = active & (t >= 0.75) & (spec >= 0.5) & (per <= 0.35)
    body = active & (per >= 0.80) & (t <= 0.50)
    low_t = active & (t >= 0.75) & (low >= 0.60)
    bright = active & (t >= 0.75) & (spec >= 0.5) & (per >= 0.80)

    return {
        "active": active,
        "t": t,
        "current": current,
        "simple": simple,
        "context": context,
        "noise": noise,
        "body": body,
        "low": low_t,
        "bright": bright,
        "psib": psib,
        "finite": bool(
            np.isfinite(t).all()
            and np.isfinite(simple).all()
            and np.isfinite(context).all()
            and np.isfinite(psib).all()
        ),
    }


def pooled(arrays, key):
    noise = []
    low = []
    body = []
    context_noise = []
    for a in arrays:
        c = a[key]
        noise.extend((c[a["noise"]] / np.maximum(a["t"][a["noise"]], 1.0e-12)).tolist())
        low.extend((c[a["low"]] / np.maximum(a["t"][a["low"]], 1.0e-12)).tolist())
        body.extend(np.abs(c[a["body"]] - a["t"][a["body"]]).tolist())
        context_noise.extend(a["psib"][a["noise"]].tolist())

    pairs = []
    for i, j in itertools.combinations(range(len(arrays)), 2):
        a, b = arrays[i], arrays[j]
        common = a["active"] & b["active"]
        pairs.append(float(np.corrcoef(a[key][common], b[key][common])[0, 1]))

    n = np.asarray(noise)
    l = np.asarray(low)
    bd = np.asarray(body)
    return {
        "noise_count": int(len(n)),
        "noise_median": float(np.median(n)),
        "noise_p10": float(np.quantile(n, 0.1)),
        "noise_p90": float(np.quantile(n, 0.9)),
        "low_count": int(len(l)),
        "low_median": float(np.median(l)),
        "low_p10": float(np.quantile(l, 0.1)),
        "body_count": int(len(bd)),
        "body_mean_abs_delta": float(np.mean(bd)),
        "pairwise_correlation_median": float(np.median(pairs)),
        "context_probability_noise_median": float(np.median(context_noise)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    arrays = [analyze(path) for path in args.files]
    current = pooled(arrays, "current")
    simple = pooled(arrays, "simple")
    context = pooled(arrays, "context")

    bright_count = int(sum(a["bright"].sum() for a in arrays))
    active_counts = [int(a["active"].sum()) for a in arrays]

    simple_pass = (
        all(a["finite"] for a in arrays)
        and min(active_counts) >= 100
        and simple["noise_count"] >= 30
        and simple["low_count"] >= 30
        and simple["body_count"] >= 30
        and simple["noise_median"] <= 0.35
        and simple["low_median"] >= 0.90
        and simple["low_p10"] >= 0.80
        and simple["body_mean_abs_delta"] <= 0.03
        and simple["pairwise_correlation_median"] >= 0.80
        and simple["pairwise_correlation_median"]
            >= current["pairwise_correlation_median"] - 0.05
    )

    context_safety = (
        all(a["finite"] for a in arrays)
        and context["noise_median"] <= 0.35
        and context["low_median"] >= 0.90
        and context["low_p10"] >= 0.80
        and context["body_mean_abs_delta"] <= 0.03
        and context["pairwise_correlation_median"] >= 0.80
        and context["pairwise_correlation_median"]
            >= current["pairwise_correlation_median"] - 0.05
    )

    complexity_improvement = simple["noise_median"] - context["noise_median"]

    print(
        json.dumps(
            {
                "schema": "peakbody-contextual-noise-guard-private-01",
                "active_counts": active_counts,
                "bright_voiced_reference_count": bright_count,
                "current": current,
                "simple_veto": simple,
                "context_veto": context,
                "private_simple_pass": simple_pass,
                "private_context_safety_pass": context_safety,
                "private_context_incremental_noise_improvement": complexity_improvement,
                "private_context_complexity_justified": bool(
                    context_safety and complexity_improvement >= 0.03
                ),
                "privacy": "aggregate non-reversible metrics only",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
