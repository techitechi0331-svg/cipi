#!/usr/bin/env python3
"""Deterministic PeakBody realtime periodicity-family benchmark.

Research only. Synthetic signals only. No raw vocal audio.
"""

from __future__ import annotations

import csv
import io
import json
import math
import random

FS = 12000
FRAME_SECONDS = 0.040
N = int(round(FS * FRAME_SECONDS))
MIN_F = 80.0
MAX_F = 1200.0
MIN_LAG = max(1, int(FS / MAX_F))
MAX_LAG = min(N // 2, int(FS / MIN_F))
SEED = 2026092601
YIN_THRESHOLD = 0.15

VOICED_CASES = (
    "sine_100",
    "harmonic_220",
    "harmonic_700",
    "bright_700",
    "bright_1000",
)
BRIGHT_CASES = ("bright_700", "bright_1000")
NOISE_CASES = ("sibilant_noise", "breath_noise")
NOISY_VOICED_CASE = "bright_700_noise6"
SILENCE_CASE = "silence"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def demean(values: list[float]) -> list[float]:
    mean = sum(values) / len(values)
    return [x - mean for x in values]


def rms(values: list[float]) -> float:
    return math.sqrt(sum(x * x for x in values) / max(1, len(values)))


def sine(f0: float, amp: float = 0.8) -> list[float]:
    return [amp * math.sin(2.0 * math.pi * f0 * n / FS) for n in range(N)]


def harmonic_stack(f0: float, bright: bool = False, amp: float = 0.8) -> list[float]:
    max_h = max(1, int((0.46 * FS) // f0))
    weights = [(1.0 / math.sqrt(h)) if bright else (1.0 / h) for h in range(1, max_h + 1)]
    norm = max(sum(weights), 1.0e-12)
    out = []
    for n in range(N):
        y = 0.0
        for h, w in enumerate(weights, 1):
            y += w * math.sin(2.0 * math.pi * f0 * h * n / FS)
        out.append(amp * y / norm)
    return out


def high_noise(seed: int) -> list[float]:
    rng = random.Random(seed)
    raw = [rng.gauss(0.0, 1.0) for _ in range(N)]
    out = []
    prev = 0.0
    for x in raw:
        # Simple bounded high-frequency emphasis for a deterministic stress proxy.
        y = x - 0.92 * prev
        out.append(y)
        prev = x
    scale = 0.35 / max(rms(out), 1.0e-12)
    return [x * scale for x in out]


def breath_noise(seed: int) -> list[float]:
    rng = random.Random(seed)
    white = [rng.gauss(0.0, 1.0) for _ in range(N)]
    low = 0.0
    out = []
    for x in white:
        low = 0.90 * low + 0.10 * x
        y = x - 0.55 * low
        out.append(y)
    scale = 0.28 / max(rms(out), 1.0e-12)
    return [x * scale for x in out]


def mix_snr(signal: list[float], noise: list[float], snr_db: float) -> list[float]:
    sig_rms = max(rms(signal), 1.0e-12)
    noise_rms = max(rms(noise), 1.0e-12)
    target_noise = sig_rms / (10.0 ** (snr_db / 20.0))
    gain = target_noise / noise_rms
    return [s + gain * n for s, n in zip(signal, noise)]


def make_cases() -> dict[str, tuple[list[float], float | None]]:
    bright700 = harmonic_stack(700.0, bright=True)
    return {
        "sine_100": (sine(100.0), 100.0),
        "harmonic_220": (harmonic_stack(220.0, bright=False), 220.0),
        "harmonic_700": (harmonic_stack(700.0, bright=False), 700.0),
        "bright_700": (bright700, 700.0),
        "bright_1000": (harmonic_stack(1000.0, bright=True), 1000.0),
        "bright_700_noise6": (mix_snr(bright700, high_noise(SEED + 1), 6.0), 700.0),
        "sibilant_noise": (high_noise(SEED + 2), None),
        "breath_noise": (breath_noise(SEED + 3), None),
        "silence": ([0.0] * N, None),
    }


def parabolic_lag(values: list[float], index: int, prefer_min: bool) -> float:
    if index <= 0 or index >= len(values) - 1:
        return float(index)
    y1, y2, y3 = values[index - 1], values[index], values[index + 1]
    denom = y1 - 2.0 * y2 + y3
    if abs(denom) < 1.0e-12:
        return float(index)
    delta = 0.5 * (y1 - y3) / denom
    delta = clamp(delta, -1.0, 1.0)
    if prefer_min and y2 > min(y1, y3):
        return float(index)
    if not prefer_min and y2 < max(y1, y3):
        return float(index)
    return index + delta


def autocorr_detector(frame: list[float]) -> dict[str, float]:
    x = demean(frame)
    if rms(x) <= 1.0e-10:
        return {"confidence": 0.0, "pitch_hz": 0.0, "pair_ops": 0.0}

    best = -1.0
    best_lag = MIN_LAG
    pair_ops = 0
    for lag in range(MIN_LAG, MAX_LAG + 1):
        num = 0.0
        ea = 0.0
        eb = 0.0
        for i in range(lag, len(x)):
            a = x[i]
            b = x[i - lag]
            num += a * b
            ea += a * a
            eb += b * b
            pair_ops += 3
        corr = num / math.sqrt(max(ea * eb, 1.0e-24))
        if corr > best:
            best = corr
            best_lag = lag

    confidence = clamp(best, 0.0, 1.0)
    return {"confidence": confidence, "pitch_hz": FS / best_lag, "pair_ops": float(pair_ops)}


def yin_detector(frame: list[float]) -> dict[str, float]:
    x = demean(frame)
    if rms(x) <= 1.0e-10:
        return {"confidence": 0.0, "pitch_hz": 0.0, "pair_ops": 0.0}

    d = [0.0] * (MAX_LAG + 1)
    pair_ops = 0
    for lag in range(1, MAX_LAG + 1):
        total = 0.0
        for i in range(0, len(x) - lag):
            diff = x[i] - x[i + lag]
            total += diff * diff
            pair_ops += 2
        d[lag] = total

    cmnd = [1.0] * (MAX_LAG + 1)
    running = 0.0
    for lag in range(1, MAX_LAG + 1):
        running += d[lag]
        cmnd[lag] = d[lag] * lag / max(running, 1.0e-24)

    chosen = None
    for lag in range(MIN_LAG, MAX_LAG):
        if cmnd[lag] < YIN_THRESHOLD and cmnd[lag] <= cmnd[lag - 1] and cmnd[lag] <= cmnd[lag + 1]:
            chosen = lag
            break

    if chosen is None:
        chosen = min(range(MIN_LAG, MAX_LAG + 1), key=lambda k: cmnd[k])

    refined = parabolic_lag(cmnd, chosen, True)
    confidence = clamp(1.0 - cmnd[chosen], 0.0, 1.0)
    return {"confidence": confidence, "pitch_hz": FS / max(refined, 1.0), "pair_ops": float(pair_ops)}


def mpm_detector(frame: list[float]) -> dict[str, float]:
    x = demean(frame)
    if rms(x) <= 1.0e-10:
        return {"confidence": 0.0, "pitch_hz": 0.0, "pair_ops": 0.0}

    nsdf = [0.0] * (MAX_LAG + 1)
    pair_ops = 0
    for lag in range(MIN_LAG, MAX_LAG + 1):
        ac = 0.0
        m = 0.0
        for i in range(0, len(x) - lag):
            a = x[i]
            b = x[i + lag]
            ac += a * b
            m += a * a + b * b
            pair_ops += 3
        nsdf[lag] = 2.0 * ac / max(m, 1.0e-24)

    chosen = max(range(MIN_LAG, MAX_LAG + 1), key=lambda k: nsdf[k])
    refined = parabolic_lag(nsdf, chosen, False)
    confidence = clamp(nsdf[chosen], 0.0, 1.0)
    return {"confidence": confidence, "pitch_hz": FS / max(refined, 1.0), "pair_ops": float(pair_ops)}


DETECTORS = {
    "autocorr_baseline": autocorr_detector,
    "yin_cmnd": yin_detector,
    "mpm_nsdf": mpm_detector,
}


def main() -> None:
    cases = make_cases()
    rows = []
    per_detector = {}

    for detector_name, detector in DETECTORS.items():
        results = {}
        for case_name, (samples, true_f0) in cases.items():
            out = detector(samples)
            pitch_error = None
            if true_f0 is not None and out["pitch_hz"] > 0.0:
                pitch_error = abs(out["pitch_hz"] - true_f0) / true_f0
            row = {
                "detector": detector_name,
                "case": case_name,
                "confidence": out["confidence"],
                "pitch_hz": out["pitch_hz"],
                "true_f0_hz": true_f0,
                "pitch_relative_error": pitch_error,
                "pair_ops": out["pair_ops"],
                "finite": all(math.isfinite(v) for v in out.values()),
            }
            rows.append(row)
            results[case_name] = row

        voiced_conf = [results[c]["confidence"] for c in VOICED_CASES]
        bright_conf = [results[c]["confidence"] for c in BRIGHT_CASES]
        noise_conf = [results[c]["confidence"] for c in NOISE_CASES]
        clean_pitch_errors = [
            results[c]["pitch_relative_error"]
            for c in VOICED_CASES
            if results[c]["pitch_relative_error"] is not None
        ]
        per_detector[detector_name] = {
            "clean_voiced_confidence_min": min(voiced_conf),
            "bright_high_confidence_min": min(bright_conf),
            "noisy_voiced_confidence": results[NOISY_VOICED_CASE]["confidence"],
            "noise_like_confidence_max": max(noise_conf),
            "silence_confidence": results[SILENCE_CASE]["confidence"],
            "bright_noise_margin": min(bright_conf) - max(noise_conf),
            "clean_pitch_relative_error_max": max(clean_pitch_errors),
            "pair_ops": results["harmonic_220"]["pair_ops"],
            "all_finite": all(r["finite"] for r in results.values()),
        }

    baseline_ops = max(per_detector["autocorr_baseline"]["pair_ops"], 1.0)
    for name, metrics in per_detector.items():
        metrics["operation_ratio_vs_autocorr"] = metrics["pair_ops"] / baseline_ops

    def qualifies(metrics: dict[str, float]) -> bool:
        return (
            metrics["all_finite"]
            and metrics["clean_voiced_confidence_min"] >= 0.75
            and metrics["bright_high_confidence_min"] >= 0.75
            and metrics["noisy_voiced_confidence"] >= 0.55
            and metrics["noise_like_confidence_max"] <= 0.35
            and metrics["silence_confidence"] <= 0.05
            and metrics["bright_noise_margin"] >= 0.45
            and metrics["operation_ratio_vs_autocorr"] <= 2.5
        )

    qualified = [
        name for name in ("yin_cmnd", "mpm_nsdf")
        if qualifies(per_detector[name])
    ]

    triggered = []
    if not qualified:
        triggered.append("neither YIN-CMND nor MPM-NSDF satisfied all predeclared PeakBody confidence/complexity gates")

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer, lineterminator="\n")
    writer.writerow([
        "detector","case","confidence","pitch_hz","true_f0_hz",
        "pitch_relative_error","pair_ops","finite"
    ])
    for row in rows:
        writer.writerow([
            row["detector"],
            row["case"],
            f"{row['confidence']:.9f}",
            f"{row['pitch_hz']:.9f}",
            "" if row["true_f0_hz"] is None else f"{row['true_f0_hz']:.9f}",
            "" if row["pitch_relative_error"] is None else f"{row['pitch_relative_error']:.9f}",
            f"{row['pair_ops']:.0f}",
            int(row["finite"]),
        ])

    payload = {
        "scope": "Synthetic 12 kHz / 40 ms algorithm-family benchmark for PeakBody periodicity protection; no product or real-vocal claim.",
        "analysis_rate_hz": FS,
        "frame_samples": N,
        "lag_range": [MIN_LAG, MAX_LAG],
        "random_seed": SEED,
        "metrics": per_detector,
        "qualified_candidates": qualified,
        "acceptance_met": bool(qualified),
        "rejection_triggered": not bool(qualified),
        "triggered_criteria": triggered,
        "measurement_csv": csv_buffer.getvalue(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
