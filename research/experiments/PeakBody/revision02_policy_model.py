#!/usr/bin/env python3
"""Deterministic model-only regression for PeakBody Revision 02.

This script mirrors the current research specification only. It does not build,
load, or release a VST3 and it never reads raw vocal audio.
"""

from __future__ import annotations

import csv
import math
import sys
import time

SAMPLE_RATES = (44100, 48000, 96000, 192000)
THRESHOLD_DB = -16.0
RATIO = 2.5
KNEE_DB = 6.0
CREST_TAU_SECONDS = 0.080
POWER_FLOOR = 1.0e-12


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def gain_computer_db(input_db: float) -> float:
    half_knee = 0.5 * KNEE_DB
    delta = input_db - THRESHOLD_DB

    if delta <= -half_knee:
        return 0.0
    if delta >= half_knee:
        return (THRESHOLD_DB + delta / RATIO) - input_db

    z = delta + half_knee
    return (1.0 / RATIO - 1.0) * z * z / (2.0 * KNEE_DB)


class CrestDetector:
    def __init__(self, sample_rate: int):
        self.sample_rate = float(sample_rate)
        self.alpha = math.exp(-1.0 / (CREST_TAU_SECONDS * self.sample_rate))
        self.reset()

    def reset(self) -> None:
        self.rms_power = 0.0
        self.peak_power = 0.0
        self.crest2 = 2.0

    def process(self, sample: float) -> float:
        x2 = abs(sample) ** 2
        one_minus = 1.0 - self.alpha
        self.rms_power = self.alpha * self.rms_power + one_minus * x2
        self.peak_power = max(x2, self.alpha * self.peak_power + one_minus * x2)

        if self.rms_power <= POWER_FLOOR:
            self.crest2 = 2.0
        else:
            self.crest2 = clamp(
                self.peak_power / max(self.rms_power, POWER_FLOOR),
                1.0,
                1000.0,
            )
        return self.crest2

    def transient_factor(self) -> float:
        normalised = max(self.crest2, 2.0) / 2.0
        return clamp(math.log2(normalised) * 0.5, 0.0, 1.0)


class GainReduction:
    def __init__(self, sample_rate: int):
        self.sample_rate = float(sample_rate)
        self.gr_db = 0.0

    def reset(self) -> None:
        self.gr_db = 0.0

    def process(self, target_gr_db: float, attack_ms: float, release_ms: float) -> float:
        target_gr_db = max(0.0, target_gr_db)
        time_ms = attack_ms if target_gr_db > self.gr_db else release_ms
        tau = max(0.01, time_ms) * 0.001
        coeff = math.exp(-1.0 / (tau * self.sample_rate))
        self.gr_db = coeff * self.gr_db + (1.0 - coeff) * target_gr_db
        return self.gr_db


def target_reduction(sample: float) -> float:
    mag = abs(sample)
    input_db = -120.0 if mag <= 1.0e-6 else 20.0 * math.log10(mag)
    return -gain_computer_db(input_db)


def timing(detector: CrestDetector) -> tuple[float, float]:
    t = detector.transient_factor()
    return 6.0 + 34.0 * t, 400.0 - 280.0 * t


def run_burst(fs: int, duration_ms: int) -> dict[str, float]:
    detector = CrestDetector(fs)
    adaptive = GainReduction(fs)
    fixed = GainReduction(fs)

    pre = int(round(0.2 * fs))
    burst = int(round(duration_ms * 0.001 * fs))
    post = int(round(0.1 * fs))
    total = pre + burst + post

    adaptive_peak = 0.0
    fixed_peak = 0.0
    attack_min = 999.0
    attack_max = 0.0
    release_min = 999.0
    release_max = 0.0
    finite = True

    for n in range(total):
        x = 0.0
        if pre <= n < pre + burst:
            k = n - pre
            x = 0.8 * math.sin(2.0 * math.pi * 220.0 * k / fs)

        detector.process(x)
        attack_ms, release_ms = timing(detector)
        target = target_reduction(x)
        agr = adaptive.process(target, attack_ms, release_ms)
        fgr = fixed.process(target, 40.0, 400.0)

        finite = finite and all(
            math.isfinite(v)
            for v in (detector.crest2, attack_ms, release_ms, agr, fgr)
        )
        attack_min = min(attack_min, attack_ms)
        attack_max = max(attack_max, attack_ms)
        release_min = min(release_min, release_ms)
        release_max = max(release_max, release_ms)

        if pre <= n < pre + burst:
            adaptive_peak = max(adaptive_peak, agr)
            fixed_peak = max(fixed_peak, fgr)

    return {
        "candidate_max_gr_db": adaptive_peak,
        "baseline_max_gr_db": fixed_peak,
        "extra_gr_db": adaptive_peak - fixed_peak,
        "attack_min_ms": attack_min,
        "attack_max_ms": attack_max,
        "release_min_ms": release_min,
        "release_max_ms": release_max,
        "finite": 1.0 if finite else 0.0,
    }


def run_sustain(fs: int) -> dict[str, float]:
    detector = CrestDetector(fs)
    adaptive = GainReduction(fs)

    pre = int(round(0.2 * fs))
    sustain = int(round(1.5 * fs))
    final_gr = 0.0
    gr_150 = 0.0
    finite = True

    for n in range(pre + sustain):
        x = 0.0
        if n >= pre:
            k = n - pre
            x = 0.3 * math.sin(2.0 * math.pi * 220.0 * k / fs)

        detector.process(x)
        attack_ms, release_ms = timing(detector)
        final_gr = adaptive.process(target_reduction(x), attack_ms, release_ms)
        finite = finite and all(
            math.isfinite(v)
            for v in (detector.crest2, attack_ms, release_ms, final_gr)
        )
        if n == pre + int(round(0.150 * fs)):
            gr_150 = final_gr

    return {
        "final_gr_db": final_gr,
        "gr_150ms_db": gr_150,
        "settled_fraction_150ms": gr_150 / max(final_gr, 1.0e-12),
        "finite": 1.0 if finite else 0.0,
    }


def steady_crest(fs: int, amplitude: float) -> float:
    detector = CrestDetector(fs)
    total = int(round(2.0 * fs))
    for n in range(total):
        x = amplitude * math.sin(2.0 * math.pi * 440.0 * n / fs)
        detector.process(x)
    return detector.crest2


def model_realtime_factor(fs: int) -> float:
    detector = CrestDetector(fs)
    gr = GainReduction(fs)
    total = int(round(1.0 * fs))
    started = time.perf_counter()
    for n in range(total):
        x = 0.3 * math.sin(2.0 * math.pi * 220.0 * n / fs)
        detector.process(x)
        attack_ms, release_ms = timing(detector)
        gr.process(target_reduction(x), attack_ms, release_ms)
    elapsed = max(time.perf_counter() - started, 1.0e-9)
    return 1.0 / elapsed


def main() -> int:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow([
        "sample_rate_hz",
        "test",
        "duration_ms",
        "candidate_value",
        "baseline_value",
        "delta_value",
        "finite",
    ])

    for fs in SAMPLE_RATES:
        for duration_ms in (10, 20, 30, 50, 100):
            result = run_burst(fs, duration_ms)
            writer.writerow([
                fs,
                "burst_max_gr_db",
                duration_ms,
                f"{result['candidate_max_gr_db']:.9f}",
                f"{result['baseline_max_gr_db']:.9f}",
                f"{result['extra_gr_db']:.9f}",
                int(result["finite"]),
            ])

        sustain = run_sustain(fs)
        writer.writerow([
            fs,
            "settled_fraction_150ms",
            150,
            f"{sustain['settled_fraction_150ms']:.9f}",
            "",
            "",
            int(sustain["finite"]),
        ])
        writer.writerow([
            fs,
            "steady_gr_db",
            1500,
            f"{sustain['final_gr_db']:.9f}",
            "",
            "",
            int(sustain["finite"]),
        ])

        crest_hi = steady_crest(fs, 0.8)
        crest_lo = steady_crest(fs, 0.08)
        writer.writerow([
            fs,
            "crest_gain_invariance_abs_diff",
            2000,
            f"{abs(crest_hi - crest_lo):.12f}",
            "",
            "",
            int(math.isfinite(crest_hi) and math.isfinite(crest_lo)),
        ])

        writer.writerow([
            fs,
            "python_model_realtime_factor",
            1000,
            f"{model_realtime_factor(fs):.6f}",
            "",
            "",
            1,
        ])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
