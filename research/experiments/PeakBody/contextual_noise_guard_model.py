#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import math
import random
import statistics

import confounder_guard_model as base

SAMPLE_RATES = base.SAMPLE_RATES
CASES = (
    "voiced_low",
    "voiced_high",
    "voiced_high_bright",
    "noisy_bright_700",
    "sibilant",
    "breath",
    "long_s",
    "steady_vowel",
    "plosive_low",
    "startup_bright",
)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def smoothstep_veto(periodicity: float) -> float:
    u = clamp((periodicity - 0.55) / 0.25, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


class OnePoleBand:
    def __init__(self, sample_rate: int, high_pass_hz: float, low_pass_hz: float):
        dt = 1.0 / sample_rate
        rc = 1.0 / (2.0 * math.pi * max(1.0, high_pass_hz))
        self.high_a = rc / (rc + dt)
        self.low_alpha = 1.0 - math.exp(
            -2.0 * math.pi * max(1.0, low_pass_hz) / sample_rate
        )
        self.prev_x = 0.0
        self.prev_high = 0.0
        self.low = 0.0

    def process(self, x: float) -> float:
        high = self.high_a * (self.prev_high + x - self.prev_x)
        self.prev_x = x
        self.prev_high = high
        self.low += self.low_alpha * (high - self.low)
        return self.low


class ContextualSibilanceProbability:
    def __init__(self, sample_rate: int):
        self.high = OnePoleBand(sample_rate, 4000.0, 12000.0)
        self.mid = OnePoleBand(sample_rate, 1000.0, 4000.0)
        self.broad = OnePoleBand(sample_rate, 250.0, 12000.0)
        self.upper = OnePoleBand(sample_rate, 7000.0, 12000.0)
        self.fast = 1.0 - math.exp(-1.0 / (0.008 * sample_rate))
        self.slow = 1.0 - math.exp(-1.0 / (0.120 * sample_rate))
        self.high_fast = 1.0e-12
        self.mid_fast = 1.0e-12
        self.broad_fast = 1.0e-12
        self.upper_fast = 1.0e-12
        self.high_slow = 1.0e-12

    @staticmethod
    def sigmoid(x: float) -> float:
        x = clamp(x, -12.0, 12.0)
        return 1.0 / (1.0 + math.exp(-x))

    def process(self, x: float) -> float:
        h = self.high.process(x)
        m = self.mid.process(x)
        b = self.broad.process(x)
        u = self.upper.process(x)

        self.high_fast += self.fast * (h * h - self.high_fast)
        self.mid_fast += self.fast * (m * m - self.mid_fast)
        self.broad_fast += self.fast * (b * b - self.broad_fast)
        self.upper_fast += self.fast * (u * u - self.upper_fast)
        self.high_slow += self.slow * (h * h - self.high_slow)

        eps = 1.0e-12
        high_db = 10.0 * math.log10(max(self.high_fast, eps))
        mid_db = 10.0 * math.log10(max(self.mid_fast, eps))
        broad_db = 10.0 * math.log10(max(self.broad_fast, eps))
        upper_db = 10.0 * math.log10(max(self.upper_fast, eps))
        slow_db = 10.0 * math.log10(max(self.high_slow, eps))

        if broad_db < -90.0:
            return 0.0

        c1 = self.sigmoid(((high_db - broad_db) + 4.5) / 1.4)
        c2 = self.sigmoid(((high_db - mid_db) - 2.0) / 2.4)
        c3 = self.sigmoid(((high_db - slow_db) - 1.0) / 3.0)
        c4 = self.sigmoid(((upper_db - high_db) + 10.0) / 2.5)

        log_p = (
            0.45 * math.log(max(c1, 1.0e-6))
            + 0.30 * math.log(max(c2, 1.0e-6))
            + 0.10 * math.log(max(c3, 1.0e-6))
            + 0.15 * math.log(max(c4, 1.0e-6))
        )
        p = math.exp(log_p)
        return clamp(p if math.isfinite(p) else 0.0, 0.0, 1.0)


def rms(values: list[float]) -> float:
    return math.sqrt(sum(x * x for x in values) / max(1, len(values)))


def mix_snr(signal: list[float], noise: list[float], snr_db: float) -> list[float]:
    s = max(rms(signal), 1.0e-12)
    n = max(rms(noise), 1.0e-12)
    gain = (s / (10.0 ** (snr_db / 20.0))) / n
    return [a + gain * b for a, b in zip(signal, noise)]


def make_case(sample_rate: int, case: str) -> list[float]:
    if case in base.CASES:
        return base.make_case(sample_rate, case)

    if case == "noisy_bright_700":
        voiced = base.harmonic_stack(sample_rate, 700.0, 0.080, 0.80, "bright")
        noise = base.high_noise(sample_rate, 0.080, 4100 + sample_rate)
        return mix_snr(voiced, noise, 6.0)

    if case == "long_s":
        return base.high_noise(sample_rate, 0.450, 4200 + sample_rate)

    if case == "startup_bright":
        silence = [0.0] * int(round(0.010 * sample_rate))
        bright = base.harmonic_stack(sample_rate, 700.0, 0.030, 0.80, "bright")
        return silence + bright

    raise ValueError(case)


def evaluate(samples: list[float], sample_rate: int, candidate: str) -> dict[str, float]:
    crest = base.CrestDetector(sample_rate)
    ratio = base.HighBandRatio(sample_rate)
    contextual = ContextualSibilanceProbability(sample_rate)

    periodicity = base.periodicity_confidence(samples, sample_rate)
    veto = smoothstep_veto(periodicity)

    baseline_t: list[float] = []
    candidate_t: list[float] = []
    contextual_p: list[float] = []

    for sample in samples:
        t = crest.process(sample)
        ratio_db = ratio.process(sample)
        spectral = clamp(
            (ratio_db - base.GUARD_THRESHOLD_DB) / base.GUARD_WIDTH_DB,
            0.0,
            1.0,
        )
        p_sib = contextual.process(sample)

        if candidate == "simple_veto":
            noise_evidence = spectral
        elif candidate == "context_veto":
            noise_evidence = max(spectral, p_sib)
        else:
            raise ValueError(candidate)

        guard = base.GUARD_STRENGTH * noise_evidence * (1.0 - veto)
        y = t * (1.0 - guard)

        baseline_t.append(t)
        candidate_t.append(y)
        contextual_p.append(p_sib)

    baseline_high = sum(v > base.HIGH_TRANSIENT_THRESHOLD for v in baseline_t) / len(baseline_t)
    candidate_high = sum(v > base.HIGH_TRANSIENT_THRESHOLD for v in candidate_t) / len(candidate_t)

    finite = all(
        math.isfinite(v)
        for v in (
            *baseline_t,
            *candidate_t,
            *contextual_p,
            periodicity,
            veto,
        )
    )

    return {
        "periodicity": periodicity,
        "veto": veto,
        "baseline_high_fraction": baseline_high,
        "candidate_high_fraction": candidate_high,
        "baseline_mean_t": sum(baseline_t) / len(baseline_t),
        "candidate_mean_t": sum(candidate_t) / len(candidate_t),
        "context_probability_median": statistics.median(contextual_p),
        "context_probability_max": max(contextual_p),
        "finite": 1.0 if finite else 0.0,
    }


def retention(row: dict[str, object]) -> float:
    b = float(row["baseline_high_fraction"])
    c = float(row["candidate_high_fraction"])
    if b <= 1.0e-12:
        return 1.0 if c <= 1.0e-12 else math.inf
    return c / b


def candidate_metrics(rows: list[dict[str, object]], candidate: str) -> dict[str, object]:
    rr = [r for r in rows if r["candidate"] == candidate]
    standard = [r for r in rr if r["case"] in {"voiced_low", "voiced_high"}]
    bright = [r for r in rr if r["case"] in {"voiced_high_bright", "startup_bright"}]
    noisy = [r for r in rr if r["case"] == "noisy_bright_700"]
    noise = [r for r in rr if r["case"] in {"sibilant", "breath", "long_s"}]
    steady = [r for r in rr if r["case"] == "steady_vowel"]
    plosive = [r for r in rr if r["case"] == "plosive_low"]

    metrics = {
        "standard_voiced_retention_min": min(retention(r) for r in standard),
        "bright_high_retention_min": min(retention(r) for r in bright),
        "noisy_voiced_retention_min": min(retention(r) for r in noisy),
        "noise_false_preserve_ratio_max": max(retention(r) for r in noise),
        "plosive_retention_min": min(retention(r) for r in plosive),
        "steady_mean_t_delta_max": max(
            abs(float(r["candidate_mean_t"]) - float(r["baseline_mean_t"]))
            for r in steady
        ),
        "all_finite": all(int(r["finite"]) == 1 for r in rr),
        "context_probability_noise_max": max(
            float(r["context_probability_max"]) for r in noise
        ),
        "context_probability_bright_max": max(
            float(r["context_probability_max"]) for r in bright
        ),
    }

    triggered = []
    if not metrics["all_finite"]:
        triggered.append("non-finite numeric output")
    if metrics["standard_voiced_retention_min"] < 0.90:
        triggered.append("standard voiced retention below 0.90")
    if metrics["bright_high_retention_min"] < 0.95:
        triggered.append("bright/startup voiced retention below 0.95")
    if metrics["noisy_voiced_retention_min"] < 0.90:
        triggered.append("6 dB SNR noisy-voiced retention below 0.90")
    if metrics["noise_false_preserve_ratio_max"] > 0.25:
        triggered.append("sibilant/breath/long-S false preservation above 0.25")
    if metrics["plosive_retention_min"] < 0.85:
        triggered.append("plosive retention below 0.85")
    if metrics["steady_mean_t_delta_max"] > 0.03:
        triggered.append("steady-vowel mean transient-factor delta above 0.03")

    metrics["acceptance_met"] = not triggered
    metrics["triggered_criteria"] = triggered
    return metrics


def main() -> None:
    rows: list[dict[str, object]] = []
    for sample_rate in SAMPLE_RATES:
        for case in CASES:
            samples = make_case(sample_rate, case)
            for candidate in ("simple_veto", "context_veto"):
                m = evaluate(samples, sample_rate, candidate)
                rows.append(
                    {
                        "sample_rate_hz": sample_rate,
                        "case": case,
                        "candidate": candidate,
                        **m,
                    }
                )

    metrics = {
        candidate: candidate_metrics(rows, candidate)
        for candidate in ("simple_veto", "context_veto")
    }
    improvement = (
        metrics["simple_veto"]["noise_false_preserve_ratio_max"]
        - metrics["context_veto"]["noise_false_preserve_ratio_max"]
    )
    metrics["context_incremental_noise_improvement"] = improvement
    metrics["qualified_candidates"] = [
        c for c in ("simple_veto", "context_veto")
        if metrics[c]["acceptance_met"]
    ]

    out = io.StringIO()
    writer = csv.DictWriter(
        out,
        fieldnames=[
            "sample_rate_hz","case","candidate","periodicity","veto",
            "baseline_high_fraction","candidate_high_fraction",
            "baseline_mean_t","candidate_mean_t",
            "context_probability_median","context_probability_max","finite",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)

    print(
        json.dumps(
            {
                "scope": "Synthetic PeakBody strong-periodicity-veto and contextual-noise-evidence comparison.",
                "metrics": metrics,
                "measurement_csv": out.getvalue(),
                "acceptance_met": bool(metrics["qualified_candidates"]),
                "rejection_triggered": not bool(metrics["qualified_candidates"]),
                "triggered_criteria": [] if metrics["qualified_candidates"] else [
                    "neither simple_veto nor context_veto passed all locked synthetic safety gates"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
