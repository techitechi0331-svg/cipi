#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import numpy as np
from scipy.signal import lfilter

import private_real_vocal_guard_measure as base


def sigmoid(x):
    x = np.clip(x, -12.0, 12.0)
    return 1.0 / (1.0 + np.exp(-x))


def smoothstep(x):
    u = np.clip(x, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def one_pole_band(x, sr, hp_hz, lp_hz):
    dt = 1.0 / sr
    rc = 1.0 / (2.0 * math.pi * max(1.0, hp_hz))
    a = rc / (rc + dt)
    high = lfilter([a, -a], [1.0, -a], x)
    alpha = 1.0 - math.exp(-2.0 * math.pi * max(1.0, lp_hz) / sr)
    return lfilter([alpha], [1.0, -(1.0 - alpha)], high)


def power_env(x, coeff):
    return lfilter([coeff], [1.0, -(1.0 - coeff)], x * x)


def plosive_evidence(x, sr):
    sub = one_pole_band(x, sr, 20.0, 80.0)
    mid = one_pole_band(x, sr, 250.0, 1000.0)
    broad = one_pole_band(x, sr, 80.0, 4000.0)

    fast = 1.0 - math.exp(-1.0 / (0.008 * sr))
    sub_slow = 1.0 - math.exp(-1.0 / (0.250 * sr))
    broad_slow = 1.0 - math.exp(-1.0 / (0.080 * sr))

    sf = power_env(sub, fast)
    mf = power_env(mid, fast)
    bf = power_env(broad, fast)
    ss = power_env(sub, sub_slow)
    bs = power_env(broad, broad_slow)

    eps = 1.0e-12
    sub_db = 10.0 * np.log10(np.maximum(sf, eps))
    mid_db = 10.0 * np.log10(np.maximum(mf, eps))
    broad_db = 10.0 * np.log10(np.maximum(bf, eps))
    sub_slow_db = 10.0 * np.log10(np.maximum(ss, eps))
    broad_slow_db = 10.0 * np.log10(np.maximum(bs, eps))

    c1 = sigmoid(((sub_db - sub_slow_db) - 7.0) / 2.0)
    c2 = sigmoid(((sub_db - mid_db) - 12.0) / 3.5)
    c3 = sigmoid(((sub_db - broad_db) - 2.5) / 1.8)
    c4 = sigmoid(((broad_db - broad_slow_db) - 1.0) / 3.0)

    full = np.exp(
        0.44 * np.log(np.maximum(c1, 1.0e-6))
        + 0.30 * np.log(np.maximum(c2, 1.0e-6))
        + 0.20 * np.log(np.maximum(c3, 1.0e-6))
        + 0.06 * np.log(np.maximum(c4, 1.0e-6))
    )
    full = np.where(broad_db < -90.0, 0.0, full)
    return np.clip(c3, 0.0, 1.0), np.clip(full, 0.0, 1.0)


def protection_from_probability(q):
    return smoothstep((q - 0.55) / 0.20)


def periodic_veto(p):
    return smoothstep((p - 0.55) / 0.25)


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

    q_simple_all, q_full_all = plosive_evidence(x, sr)
    q_simple = q_simple_all[ends - 1]
    q_full = q_full_all[ends - 1]

    vp = periodic_veto(per)
    v_simple = np.maximum(vp, protection_from_probability(q_simple))
    v_full = np.maximum(vp, protection_from_probability(q_full))

    current = t * (1.0 - 0.75 * spec * (1.0 - per))
    rejected_a = t * (1.0 - 0.75 * spec * (1.0 - vp))
    c1 = t * (1.0 - 0.75 * spec * (1.0 - v_simple))
    c2 = t * (1.0 - 0.75 * spec * (1.0 - v_full))

    noise = active & (t >= 0.75) & (spec >= 0.5) & (per <= 0.35)
    body = active & (per >= 0.80) & (t <= 0.50)
    low_t = active & (t >= 0.75) & (low >= 0.60)
    bright = active & (t >= 0.75) & (spec >= 0.5) & (per >= 0.80)

    return {
        "active": active,
        "t": t,
        "current": current,
        "rejected_a": rejected_a,
        "c1": c1,
        "c2": c2,
        "noise": noise,
        "body": body,
        "low": low_t,
        "bright": bright,
        "q_simple": q_simple,
        "q_full": q_full,
        "finite": bool(
            np.isfinite(t).all()
            and np.isfinite(c1).all()
            and np.isfinite(c2).all()
            and np.isfinite(q_simple).all()
            and np.isfinite(q_full).all()
        ),
    }


def pooled(arrays, key):
    noise, low, body = [], [], []
    q_simple_noise, q_full_noise = [], []
    q_simple_low, q_full_low = [], []

    for a in arrays:
        y = a[key]
        noise.extend((y[a["noise"]] / np.maximum(a["t"][a["noise"]], 1.0e-12)).tolist())
        low.extend((y[a["low"]] / np.maximum(a["t"][a["low"]], 1.0e-12)).tolist())
        body.extend(np.abs(y[a["body"]] - a["t"][a["body"]]).tolist())
        q_simple_noise.extend(a["q_simple"][a["noise"]].tolist())
        q_full_noise.extend(a["q_full"][a["noise"]].tolist())
        q_simple_low.extend(a["q_simple"][a["low"]].tolist())
        q_full_low.extend(a["q_full"][a["low"]].tolist())

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
        "simple_evidence_noise_median": float(np.median(q_simple_noise)),
        "full_evidence_noise_median": float(np.median(q_full_noise)),
        "simple_evidence_low_median": float(np.median(q_simple_low)),
        "full_evidence_low_median": float(np.median(q_full_low)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    arrays = [analyze(path) for path in args.files]
    current = pooled(arrays, "current")
    rejected_a = pooled(arrays, "rejected_a")
    c1 = pooled(arrays, "c1")
    c2 = pooled(arrays, "c2")

    active_counts = [int(a["active"].sum()) for a in arrays]
    bright_count = int(sum(a["bright"].sum() for a in arrays))

    def private_pass(m):
        return (
            all(a["finite"] for a in arrays)
            and min(active_counts) >= 100
            and m["noise_count"] >= 30
            and m["low_count"] >= 30
            and m["body_count"] >= 30
            and m["noise_median"] <= 0.35
            and m["low_median"] >= 0.90
            and m["low_p10"] >= 0.80
            and m["body_mean_abs_delta"] <= 0.03
            and m["pairwise_correlation_median"] >= 0.80
            and m["pairwise_correlation_median"]
                >= current["pairwise_correlation_median"] - 0.05
        )

    c1_pass = private_pass(c1)
    c2_pass = private_pass(c2)
    c2_noise_improvement = c1["noise_median"] - c2["noise_median"]

    print(
        json.dumps(
            {
                "schema": "peakbody-plosive-protection-private-01",
                "active_counts": active_counts,
                "bright_voiced_reference_count": bright_count,
                "current": current,
                "rejected_strong_veto": rejected_a,
                "simple_lf_concentration": c1,
                "full_plosive_context": c2,
                "private_c1_pass": c1_pass,
                "private_c2_pass": c2_pass,
                "full_vs_simple_noise_improvement": c2_noise_improvement,
                "private_full_complexity_justified": bool(
                    c2_pass and (
                        not c1_pass or c2_noise_improvement >= 0.03
                    )
                ),
                "privacy": "aggregate non-reversible metrics only",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
