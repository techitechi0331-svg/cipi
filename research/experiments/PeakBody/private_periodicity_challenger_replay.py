#!/usr/bin/env python3
from __future__ import annotations

import argparse
from fractions import Fraction
import itertools
import json
import math
import numpy as np
from scipy.signal import resample_poly

import private_real_vocal_guard_measure as base

TARGET_SR = 12000
WINDOW_SEC = 0.040
FMIN = 80.0
FMAX = 1200.0
YIN_THRESHOLD = 0.15


def _resampled_frames(x, sr, ends):
    frac = Fraction(TARGET_SR, sr).limit_denominator(1000)
    y = resample_poly(x, frac.numerator, frac.denominator)
    width = int(round(WINDOW_SEC * TARGET_SR))
    mapped = np.rint((ends / sr) * TARGET_SR).astype(int)
    mapped = np.clip(mapped, width, len(y))
    return y, mapped, width


def _frame_bank(y, ends, width):
    return np.stack([y[e-width:e] for e in ends])


def _fft_autocorr(A, max_lag):
    nfft = 1
    while nfft < 2 * A.shape[1]:
        nfft *= 2
    F = np.fft.rfft(A, n=nfft, axis=1)
    return np.fft.irfft(F * np.conj(F), n=nfft, axis=1)[:, : max_lag + 1]


def yin_confidence(x, sr, ends):
    y, mapped, width = _resampled_frames(x, sr, ends)
    min_lag = max(1, int(TARGET_SR / FMAX))
    max_lag = min(width // 2, int(TARGET_SR / FMIN))
    conf = np.zeros(len(mapped))
    batch = 256

    lags = np.arange(1, max_lag + 1)
    for start in range(0, len(mapped), batch):
        stop = min(len(mapped), start + batch)
        A = _frame_bank(y, mapped[start:stop], width)
        A = A - A.mean(axis=1, keepdims=True)
        row_rms = np.sqrt(np.mean(A * A, axis=1))
        ac = _fft_autocorr(A, max_lag)
        sq = A * A
        cs = np.concatenate([np.zeros((len(A), 1)), np.cumsum(sq, axis=1)], axis=1)

        left = cs[:, width - lags]
        right = cs[:, [width]] - cs[:, lags]
        d = np.maximum(left + right - 2.0 * ac[:, 1 : max_lag + 1], 0.0)
        running = np.cumsum(d, axis=1)
        cmnd = d * lags[None, :] / np.maximum(running, 1.0e-24)

        sub = cmnd[:, min_lag - 1 : max_lag]
        local = np.ones_like(sub, dtype=bool)
        if sub.shape[1] > 2:
            local[:, 1:-1] = (
                (sub[:, 1:-1] <= sub[:, :-2])
                & (sub[:, 1:-1] <= sub[:, 2:])
            )
        under = (sub < YIN_THRESHOLD) & local
        any_under = under.any(axis=1)
        first = np.argmax(under, axis=1)
        global_min = np.argmin(sub, axis=1)
        chosen = np.where(any_under, first, global_min)
        selected = sub[np.arange(len(A)), chosen]
        values = np.clip(1.0 - selected, 0.0, 1.0)
        values = np.where(row_rms <= 1.0e-10, 0.0, values)
        conf[start:stop] = values
    return conf


def mpm_confidence(x, sr, ends):
    y, mapped, width = _resampled_frames(x, sr, ends)
    min_lag = max(1, int(TARGET_SR / FMAX))
    max_lag = min(width // 2, int(TARGET_SR / FMIN))
    conf = np.zeros(len(mapped))
    batch = 256
    lags = np.arange(min_lag, max_lag + 1)

    for start in range(0, len(mapped), batch):
        stop = min(len(mapped), start + batch)
        A = _frame_bank(y, mapped[start:stop], width)
        A = A - A.mean(axis=1, keepdims=True)
        row_rms = np.sqrt(np.mean(A * A, axis=1))
        ac = _fft_autocorr(A, max_lag)
        sq = A * A
        cs = np.concatenate([np.zeros((len(A), 1)), np.cumsum(sq, axis=1)], axis=1)
        left = cs[:, width - lags]
        right = cs[:, [width]] - cs[:, lags]
        nsdf = 2.0 * ac[:, lags] / np.maximum(left + right, 1.0e-24)
        values = np.clip(np.max(nsdf, axis=1), 0.0, 1.0)
        values = np.where(row_rms <= 1.0e-10, 0.0, values)
        conf[start:stop] = values
    return conf


def _retention(candidate, reference, mask):
    values = candidate[mask] / np.maximum(reference[mask], 1.0e-12)
    if not len(values):
        return {"count": 0}
    return {
        "count": int(len(values)),
        "median": float(np.median(values)),
        "p10": float(np.quantile(values, 0.1)),
        "p90": float(np.quantile(values, 0.9)),
        "min": float(np.min(values)),
    }


def analyze(path, detector_name):
    sr, x = base.load_mono(path)
    win = int(round(WINDOW_SEC * sr))
    hop = max(1, int(round(0.005 * sr)))
    ends = np.arange(win, len(x) + 1, hop, dtype=int)

    overall = np.sqrt(np.mean(x * x))
    overall_db = 20.0 * np.log10(max(overall, base.POWER_FLOOR))
    active_threshold_db = max(-60.0, overall_db - 30.0)
    active_threshold = 10.0 ** (active_threshold_db / 20.0)
    cs = np.concatenate([[0.0], np.cumsum(x * x)])
    frame_rms = np.sqrt((cs[ends] - cs[ends - win]) / win)
    active = frame_rms > active_threshold

    t = base.crest_series(x, sr)[ends - 1]
    spec = base.spectral_guard_series(x, sr)[ends - 1]
    low = base.low_ratio_series(x, sr)[ends - 1]
    auto = base.periodicity_frames(x, sr, ends, win)

    if detector_name == "yin":
        challenger_conf = yin_confidence(x, sr, ends)
    elif detector_name == "mpm":
        challenger_conf = mpm_confidence(x, sr, ends)
    else:
        raise ValueError(detector_name)

    auto_guard = t * (1.0 - 0.75 * spec * (1.0 - auto))
    challenger_guard = t * (1.0 - 0.75 * spec * (1.0 - challenger_conf))

    # Candidate-independent masks: all are defined from the frozen baseline features.
    noise = active & (t >= 0.75) & (spec >= 0.5) & (auto <= 0.35)
    body = active & (auto >= 0.80) & (t <= 0.50)
    low_transient = active & (t >= 0.75) & (low >= 0.60)
    bright = active & (t >= 0.75) & (spec >= 0.5) & (auto >= 0.80)

    return {
        "active": active,
        "t": t,
        "auto": auto,
        "challenger_conf": challenger_conf,
        "auto_guard": auto_guard,
        "challenger_guard": challenger_guard,
        "noise": noise,
        "body": body,
        "low": low_transient,
        "bright": bright,
        "finite": bool(
            np.isfinite(t).all()
            and np.isfinite(auto).all()
            and np.isfinite(challenger_conf).all()
            and np.isfinite(challenger_guard).all()
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detector", choices=("yin", "mpm"), required=True)
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    arrays = [analyze(path, args.detector) for path in args.files]

    noise_auto, noise_challenger = [], []
    low_challenger, body_delta = [], []
    noise_conf, auto_noise_conf = [], []
    source_counts = []

    for a in arrays:
        source_counts.append(
            {
                "active": int(a["active"].sum()),
                "noise_like": int(a["noise"].sum()),
                "bright_voiced": int(a["bright"].sum()),
                "periodic_body": int(a["body"].sum()),
                "low_frequency_transient": int(a["low"].sum()),
            }
        )
        noise_auto.extend(
            (a["auto_guard"][a["noise"]] / np.maximum(a["t"][a["noise"]], 1.0e-12)).tolist()
        )
        noise_challenger.extend(
            (a["challenger_guard"][a["noise"]] / np.maximum(a["t"][a["noise"]], 1.0e-12)).tolist()
        )
        low_challenger.extend(
            (a["challenger_guard"][a["low"]] / np.maximum(a["t"][a["low"]], 1.0e-12)).tolist()
        )
        body_delta.extend(np.abs(a["challenger_guard"][a["body"]] - a["t"][a["body"]]).tolist())
        noise_conf.extend(a["challenger_conf"][a["noise"]].tolist())
        auto_noise_conf.extend(a["auto"][a["noise"]].tolist())

    pairs = []
    for i, j in itertools.combinations(range(len(arrays)), 2):
        a, b = arrays[i], arrays[j]
        common = a["active"] & b["active"]
        pairs.append(
            {
                "pair": f"PV{i+1}-PV{j+1}",
                "autocorr_guard_corr": float(
                    np.corrcoef(a["auto_guard"][common], b["auto_guard"][common])[0, 1]
                ),
                "challenger_guard_corr": float(
                    np.corrcoef(
                        a["challenger_guard"][common], b["challenger_guard"][common]
                    )[0, 1]
                ),
            }
        )

    noise_auto = np.asarray(noise_auto)
    noise_challenger = np.asarray(noise_challenger)
    low_challenger = np.asarray(low_challenger)
    body_delta = np.asarray(body_delta)

    auto_corr_med = float(np.median([p["autocorr_guard_corr"] for p in pairs]))
    challenger_corr_med = float(np.median([p["challenger_guard_corr"] for p in pairs]))

    metrics = {
        "noise_count": int(len(noise_challenger)),
        "noise_autocorr_guard_retention_median": float(np.median(noise_auto)),
        "noise_challenger_retention_median": float(np.median(noise_challenger)),
        "noise_challenger_minus_autocorr_median": float(
            np.median(noise_challenger) - np.median(noise_auto)
        ),
        "noise_challenger_retention_p10": float(np.quantile(noise_challenger, 0.1)),
        "noise_challenger_retention_p90": float(np.quantile(noise_challenger, 0.9)),
        "challenger_confidence_on_noise_mask_median": float(np.median(noise_conf)),
        "autocorr_confidence_on_noise_mask_median": float(np.median(auto_noise_conf)),
        "low_count": int(len(low_challenger)),
        "low_retention_median": float(np.median(low_challenger)),
        "low_retention_p10": float(np.quantile(low_challenger, 0.1)),
        "body_count": int(len(body_delta)),
        "body_mean_abs_delta": float(np.mean(body_delta)),
        "autocorr_guard_correlation_median": auto_corr_med,
        "challenger_guard_correlation_median": challenger_corr_med,
        "challenger_minus_autocorr_correlation_median": challenger_corr_med - auto_corr_med,
        "bright_voiced_reference_count": int(sum(x["bright_voiced"] for x in source_counts)),
    }

    criteria = {
        "all_finite": all(a["finite"] for a in arrays),
        "active_frames_each_ge_100": all(x["active"] >= 100 for x in source_counts),
        "noise_count_ge_30": metrics["noise_count"] >= 30,
        "low_count_ge_30": metrics["low_count"] >= 30,
        "body_count_ge_30": metrics["body_count"] >= 30,
        "noise_median_le_0_50": metrics["noise_challenger_retention_median"] <= 0.50,
        "noise_not_more_than_0_02_above_autocorr": (
            metrics["noise_challenger_minus_autocorr_median"] <= 0.02
        ),
        "low_median_ge_0_90": metrics["low_retention_median"] >= 0.90,
        "low_p10_ge_0_80": metrics["low_retention_p10"] >= 0.80,
        "body_mean_abs_delta_le_0_03": metrics["body_mean_abs_delta"] <= 0.03,
        "guard_corr_median_ge_0_80": metrics["challenger_guard_correlation_median"] >= 0.80,
        "guard_corr_drop_le_0_05": (
            metrics["challenger_minus_autocorr_correlation_median"] >= -0.05
        ),
    }

    enough = (
        criteria["noise_count_ge_30"]
        and criteria["low_count_ge_30"]
        and criteria["body_count_ge_30"]
    )
    if not enough:
        decision = "INCONCLUSIVE"
    elif all(criteria.values()):
        decision = "PASS"
    else:
        decision = "REJECT"

    print(
        json.dumps(
            {
                "schema": "peakbody-periodicity-private-replay-01",
                "detector": args.detector,
                "decision": decision,
                "source_counts": source_counts,
                "metrics": metrics,
                "criteria": criteria,
                "privacy": "aggregate non-reversible metrics only; no raw audio/timecodes/per-frame arrays",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
