#!/usr/bin/env python3
"""Synthetic confounder stress test for PeakBody crest guards.

Research only. No raw vocal audio, network access, product mutation, or release.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys

SAMPLE_RATES = (44100, 48000, 96000, 192000)
CREST_TAU_SECONDS = 0.080
RATIO_TAU_SECONDS = 0.020
HIGH_BAND_HZ = 5600.0
GUARD_THRESHOLD_DB = -11.0
GUARD_WIDTH_DB = 6.0
GUARD_STRENGTH = 0.75
POWER_FLOOR = 1.0e-12
HIGH_TRANSIENT_THRESHOLD = 0.75

CASES = (
    "voiced_low",
    "voiced_high",
    "voiced_high_bright",
    "sibilant",
    "breath",
    "steady_vowel",
    "plosive_low",
)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class CrestDetector:
    def __init__(self, sample_rate: int):
        self.alpha = math.exp(-1.0 / (CREST_TAU_SECONDS * sample_rate))
        self.rms_power = 0.0
        self.peak_power = 0.0
        self.crest2 = 2.0

    def process(self, sample: float) -> float:
        x2 = sample * sample
        one_minus = 1.0 - self.alpha
        self.rms_power = self.alpha * self.rms_power + one_minus * x2
        self.peak_power = max(
            x2,
            self.alpha * self.peak_power + one_minus * x2,
        )

        if self.rms_power <= POWER_FLOOR:
            self.crest2 = 2.0
        else:
            self.crest2 = clamp(
                self.peak_power / max(self.rms_power, POWER_FLOOR),
                1.0,
                1000.0,
            )

        return self.transient_factor()

    def transient_factor(self) -> float:
        normalised = max(self.crest2, 2.0) / 2.0
        return clamp(math.log2(normalised) * 0.5, 0.0, 1.0)


class BiquadHighPass:
    def __init__(self, sample_rate: int, cutoff_hz: float):
        q = 1.0 / math.sqrt(2.0)
        w0 = 2.0 * math.pi * cutoff_hz / sample_rate
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)
        alpha = sin_w0 / (2.0 * q)

        b0 = (1.0 + cos_w0) * 0.5
        b1 = -(1.0 + cos_w0)
        b2 = (1.0 + cos_w0) * 0.5
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha

        self.b0 = b0 / a0
        self.b1 = b1 / a0
        self.b2 = b2 / a0
        self.a1 = a1 / a0
        self.a2 = a2 / a0

        self.x1 = 0.0
        self.x2 = 0.0
        self.y1 = 0.0
        self.y2 = 0.0

    def process(self, sample: float) -> float:
        y = (
            self.b0 * sample
            + self.b1 * self.x1
            + self.b2 * self.x2
            - self.a1 * self.y1
            - self.a2 * self.y2
        )
        self.x2 = self.x1
        self.x1 = sample
        self.y2 = self.y1
        self.y1 = y
        return y


class HighBandRatio:
    def __init__(self, sample_rate: int):
        self.hp1 = BiquadHighPass(sample_rate, HIGH_BAND_HZ)
        self.hp2 = BiquadHighPass(sample_rate, HIGH_BAND_HZ)
        self.alpha = math.exp(-1.0 / (RATIO_TAU_SECONDS * sample_rate))
        self.full_power = 0.0
        self.high_power = 0.0

    def process(self, sample: float) -> float:
        high = self.hp2.process(self.hp1.process(sample))
        one_minus = 1.0 - self.alpha
        self.full_power = self.alpha * self.full_power + one_minus * sample * sample
        self.high_power = self.alpha * self.high_power + one_minus * high * high

        return 10.0 * math.log10(
            max(self.high_power, POWER_FLOOR)
            / max(self.full_power, POWER_FLOOR)
        )


def harmonic_stack(
    sample_rate: int,
    f0_hz: float,
    duration_seconds: float,
    amplitude: float,
    brightness: str,
) -> list[float]:
    max_harmonic = max(1, int((0.5 * sample_rate - 1000.0) // f0_hz))
    harmonics = list(range(1, max_harmonic + 1))

    if brightness == "bright":
        weights = [1.0 / math.sqrt(h) for h in harmonics]
    else:
        weights = [1.0 / h for h in harmonics]

    normaliser = max(sum(weights), 1.0e-12)
    total = int(round(duration_seconds * sample_rate))

    result: list[float] = []
    for n in range(total):
        value = 0.0
        for harmonic, weight in zip(harmonics, weights):
            value += weight * math.sin(
                2.0 * math.pi * f0_hz * harmonic * n / sample_rate
            )
        result.append(amplitude * value / normaliser)
    return result


def high_noise(
    sample_rate: int,
    duration_seconds: float,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    hp1 = BiquadHighPass(sample_rate, 5000.0)
    hp2 = BiquadHighPass(sample_rate, 5000.0)
    return [
        0.35 * hp2.process(hp1.process(rng.gauss(0.0, 1.0)))
        for _ in range(int(round(duration_seconds * sample_rate)))
    ]


def breath_noise(
    sample_rate: int,
    duration_seconds: float,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    low_hp1 = BiquadHighPass(sample_rate, 700.0)
    low_hp2 = BiquadHighPass(sample_rate, 700.0)
    high_hp1 = BiquadHighPass(sample_rate, 5000.0)
    high_hp2 = BiquadHighPass(sample_rate, 5000.0)

    result: list[float] = []
    for _ in range(int(round(duration_seconds * sample_rate))):
        noise = rng.gauss(0.0, 1.0)
        above_low = low_hp2.process(low_hp1.process(noise))
        above_high = high_hp2.process(high_hp1.process(above_low))
        result.append(0.28 * (above_low - above_high))
    return result


def plosive_low(
    sample_rate: int,
    duration_seconds: float,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    hp1 = BiquadHighPass(sample_rate, 900.0)
    hp2 = BiquadHighPass(sample_rate, 900.0)

    total = int(round(duration_seconds * sample_rate))
    result: list[float] = []
    for n in range(total):
        noise = rng.gauss(0.0, 1.0)
        above = hp2.process(hp1.process(noise))
        low = noise - above
        envelope = math.exp(-6.0 * n / max(1, total))
        result.append(0.65 * envelope * low)
    return result


def make_case(sample_rate: int, case: str) -> list[float]:
    if case == "voiced_low":
        return harmonic_stack(sample_rate, 180.0, 0.030, 0.80, "normal")
    if case == "voiced_high":
        return harmonic_stack(sample_rate, 700.0, 0.030, 0.80, "normal")
    if case == "voiced_high_bright":
        return harmonic_stack(sample_rate, 700.0, 0.030, 0.80, "bright")
    if case == "sibilant":
        return high_noise(sample_rate, 0.080, 1000 + sample_rate)
    if case == "breath":
        return breath_noise(sample_rate, 0.120, 2000 + sample_rate)
    if case == "steady_vowel":
        return harmonic_stack(sample_rate, 220.0, 0.400, 0.30, "normal")
    if case == "plosive_low":
        return plosive_low(sample_rate, 0.025, 3000 + sample_rate)
    raise ValueError(case)


def periodicity_confidence(samples: list[float], sample_rate: int) -> float:
    if not samples:
        return 0.0

    # Analysis-only periodicity proxy. Decimate to roughly 12 kHz and cap the
    # window so the autonomous job remains bounded and deterministic.
    step = max(1, int(sample_rate // 12000))
    down = samples[::step]
    if len(down) > 1800:
        down = down[:1800]

    mean = sum(down) / len(down)
    values = [x - mean for x in down]
    energy = sum(x * x for x in values)

    if energy <= POWER_FLOOR:
        return 0.0

    analysis_rate = sample_rate / step
    min_lag = max(1, int(analysis_rate / 1200.0))
    max_lag = min(len(values) // 2, int(analysis_rate / 80.0))

    best = 0.0
    for lag in range(min_lag, max_lag + 1):
        numerator = 0.0
        left_energy = 0.0
        right_energy = 0.0

        for i in range(lag, len(values)):
            left = values[i]
            right = values[i - lag]
            numerator += left * right
            left_energy += left * left
            right_energy += right * right

        denom = math.sqrt(max(left_energy * right_energy, POWER_FLOOR))
        best = max(best, numerator / denom)

    return clamp(best, 0.0, 1.0)


def evaluate(
    samples: list[float],
    sample_rate: int,
    mode: str,
) -> dict[str, float]:
    crest = CrestDetector(sample_rate)
    ratio = HighBandRatio(sample_rate)

    periodicity = periodicity_confidence(samples, sample_rate)

    baseline: list[float] = []
    candidate: list[float] = []
    ratio_db_values: list[float] = []

    for sample in samples:
        t = crest.process(sample)
        ratio_db = ratio.process(sample)

        spectral_guard = clamp(
            (ratio_db - GUARD_THRESHOLD_DB) / GUARD_WIDTH_DB,
            0.0,
            1.0,
        )

        if mode == "spectral_only":
            effective_guard = spectral_guard
        elif mode == "spectral_periodicity":
            effective_guard = spectral_guard * (1.0 - periodicity)
        else:
            raise ValueError(mode)

        guarded = t * (1.0 - GUARD_STRENGTH * effective_guard)

        baseline.append(t)
        candidate.append(guarded)
        ratio_db_values.append(ratio_db)

    baseline_high = sum(v > HIGH_TRANSIENT_THRESHOLD for v in baseline) / len(baseline)
    candidate_high = sum(v > HIGH_TRANSIENT_THRESHOLD for v in candidate) / len(candidate)

    finite = all(
        math.isfinite(v)
        for v in (
            *baseline,
            *candidate,
            *ratio_db_values,
            periodicity,
        )
    )

    return {
        "baseline_peak_t": max(baseline),
        "candidate_peak_t": max(candidate),
        "baseline_high_fraction": baseline_high,
        "candidate_high_fraction": candidate_high,
        "baseline_mean_t": sum(baseline) / len(baseline),
        "candidate_mean_t": sum(candidate) / len(candidate),
        "median_highband_ratio_db": statistics.median(ratio_db_values),
        "periodicity_confidence": periodicity,
        "finite": 1.0 if finite else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("spectral_only", "spectral_periodicity"),
        required=True,
    )
    args = parser.parse_args()

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow([
        "sample_rate_hz",
        "mode",
        "case",
        "baseline_peak_t",
        "candidate_peak_t",
        "baseline_high_fraction",
        "candidate_high_fraction",
        "baseline_mean_t",
        "candidate_mean_t",
        "median_highband_ratio_db",
        "periodicity_confidence",
        "finite",
    ])

    for sample_rate in SAMPLE_RATES:
        for case in CASES:
            row = evaluate(make_case(sample_rate, case), sample_rate, args.mode)
            writer.writerow([
                sample_rate,
                args.mode,
                case,
                f"{row['baseline_peak_t']:.9f}",
                f"{row['candidate_peak_t']:.9f}",
                f"{row['baseline_high_fraction']:.9f}",
                f"{row['candidate_high_fraction']:.9f}",
                f"{row['baseline_mean_t']:.9f}",
                f"{row['candidate_mean_t']:.9f}",
                f"{row['median_highband_ratio_db']:.9f}",
                f"{row['periodicity_confidence']:.9f}",
                int(row["finite"]),
            ])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
