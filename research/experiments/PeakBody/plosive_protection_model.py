#!/usr/bin/env python3
"""PeakBody independent plosive-protection benchmark.

Research-only deterministic synthetic model.
No raw vocal audio, network access, product mutation, promotion, or release.
"""

from __future__ import annotations

import csv
import io
import json
import math
import random

import confounder_guard_model as base

SAMPLE_RATES = base.SAMPLE_RATES
GUARD_STRENGTH = base.GUARD_STRENGTH

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
    "sustained_low",
    "fry_low",
    "growl_onset",
    "lf_contaminated_sibilant",
)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def smoothstep01(x: float) -> float:
    u = clamp(x, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def periodic_veto(periodicity: float) -> float:
    return smoothstep01((periodicity - 0.55) / 0.25)


def plosive_veto(probability: float) -> float:
    # Vo.Prep v2.2 release/activation interval: 0.55 -> 0.75.
    return smoothstep01((probability - 0.55) / 0.20)


def sigmoid(x: float) -> float:
    x = clamp(x, -12.0, 12.0)
    return 1.0 / (1.0 + math.exp(-x))


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


class PlosiveEvidence:
    """Continuous Vo.Prep v2.2 plosive evidence, without product event state."""

    def __init__(self, sample_rate: int):
        self.sub = OnePoleBand(sample_rate, 20.0, 80.0)
        self.mid = OnePoleBand(sample_rate, 250.0, 1000.0)
        self.broad = OnePoleBand(sample_rate, 80.0, 4000.0)

        self.fast = 1.0 - math.exp(-1.0 / (0.008 * sample_rate))
        self.sub_slow = 1.0 - math.exp(-1.0 / (0.250 * sample_rate))
        self.broad_slow = 1.0 - math.exp(-1.0 / (0.080 * sample_rate))

        self.sub_fast_power = 1.0e-12
        self.mid_fast_power = 1.0e-12
        self.broad_fast_power = 1.0e-12
        self.sub_slow_power = 1.0e-12
        self.broad_slow_power = 1.0e-12

    def process(self, x: float) -> tuple[float, float]:
        s = self.sub.process(x)
        m = self.mid.process(x)
        b = self.broad.process(x)

        self.sub_fast_power += self.fast * (s * s - self.sub_fast_power)
        self.mid_fast_power += self.fast * (m * m - self.mid_fast_power)
        self.broad_fast_power += self.fast * (b * b - self.broad_fast_power)
        self.sub_slow_power += self.sub_slow * (s * s - self.sub_slow_power)
        self.broad_slow_power += self.broad_slow * (
            b * b - self.broad_slow_power
        )

        eps = 1.0e-12
        sub_db = 10.0 * math.log10(max(self.sub_fast_power, eps))
        mid_db = 10.0 * math.log10(max(self.mid_fast_power, eps))
        broad_db = 10.0 * math.log10(max(self.broad_fast_power, eps))
        sub_slow_db = 10.0 * math.log10(max(self.sub_slow_power, eps))
        broad_slow_db = 10.0 * math.log10(max(self.broad_slow_power, eps))

        if broad_db < -90.0:
            return 0.0, 0.0

        sub_onset_db = sub_db - sub_slow_db
        sub_to_mid_db = sub_db - mid_db
        sub_concentration_db = sub_db - broad_db
        broad_onset_db = broad_db - broad_slow_db

        c1 = sigmoid((sub_onset_db - 7.0) / 2.0)
        c2 = sigmoid((sub_to_mid_db - 12.0) / 3.5)
        c3 = sigmoid((sub_concentration_db - 2.5) / 1.8)
        c4 = sigmoid((broad_onset_db - 1.0) / 3.0)

        log_p = (
            0.44 * math.log(max(c1, 1.0e-6))
            + 0.30 * math.log(max(c2, 1.0e-6))
            + 0.20 * math.log(max(c3, 1.0e-6))
            + 0.06 * math.log(max(c4, 1.0e-6))
        )
        full = clamp(math.exp(log_p), 0.0, 1.0)
        return c3, full


def rms(values: list[float]) -> float:
    return math.sqrt(sum(x * x for x in values) / max(1, len(values)))


def mix_snr(signal: list[float], noise: list[float], snr_db: float) -> list[float]:
    sig = max(rms(signal), 1.0e-12)
    noi = max(rms(noise), 1.0e-12)
    gain = (sig / (10.0 ** (snr_db / 20.0))) / noi
    return [a + gain * b for a, b in zip(signal, noise)]


def sustained_low(sample_rate: int, duration: float = 0.250) -> list[float]:
    total = int(round(duration * sample_rate))
    return [
        0.18 * math.sin(2.0 * math.pi * 90.0 * n / sample_rate)
        + 0.06 * math.sin(2.0 * math.pi * 180.0 * n / sample_rate)
        for n in range(total)
    ]


def fry_low(sample_rate: int, duration: float = 0.250) -> list[float]:
    total = int(round(duration * sample_rate))
    out = []
    for n in range(total):
        t = n / sample_rate
        pulse = 1.0 if math.sin(2.0 * math.pi * 70.0 * t) >= 0.0 else -1.0
        out.append(
            0.12
            * pulse
            * (0.70 + 0.30 * math.sin(2.0 * math.pi * 4.0 * t))
        )
    return out


def growl_onset(sample_rate: int, duration: float = 0.120) -> list[float]:
    total = int(round(duration * sample_rate))
    out = []
    for n in range(total):
        t = n / sample_rate
        onset = min(1.0, n / max(1.0, 0.008 * sample_rate))
        y = (
            0.20 * math.sin(2.0 * math.pi * 85.0 * t)
            + 0.10 * math.sin(2.0 * math.pi * 170.0 * t)
            + 0.05 * math.sin(2.0 * math.pi * 340.0 * t)
            + 0.025 * math.sin(2.0 * math.pi * 680.0 * t)
        )
        out.append(onset * y)
    return out


def lf_contaminated_sibilant(sample_rate: int) -> list[float]:
    noise = base.high_noise(sample_rate, 0.100, 5100 + sample_rate)
    out = []
    for n, h in enumerate(noise):
        t = n / sample_rate
        lf = 0.22 * math.sin(2.0 * math.pi * 55.0 * t)
        out.append(h + lf)
    return out


def make_case(sample_rate: int, case: str) -> list[float]:
    if case in base.CASES:
        return base.make_case(sample_rate, case)
    if case == "noisy_bright_700":
        voiced = base.harmonic_stack(
            sample_rate, 700.0, 0.080, 0.80, "bright"
        )
        noise = base.high_noise(sample_rate, 0.080, 4100 + sample_rate)
        return mix_snr(voiced, noise, 6.0)
    if case == "long_s":
        return base.high_noise(sample_rate, 0.450, 4200 + sample_rate)
    if case == "startup_bright":
        return (
            [0.0] * int(round(0.010 * sample_rate))
            + base.harmonic_stack(
                sample_rate, 700.0, 0.030, 0.80, "bright"
            )
        )
    if case == "sustained_low":
        return sustained_low(sample_rate)
    if case == "fry_low":
        return fry_low(sample_rate)
    if case == "growl_onset":
        return growl_onset(sample_rate)
    if case == "lf_contaminated_sibilant":
        return lf_contaminated_sibilant(sample_rate)
    raise ValueError(case)


def evaluate(
    samples: list[float],
    sample_rate: int,
    candidate: str,
) -> dict[str, float]:
    crest = base.CrestDetector(sample_rate)
    spectral_ratio = base.HighBandRatio(sample_rate)
    plosive = PlosiveEvidence(sample_rate)

    periodicity = base.periodicity_confidence(samples, sample_rate)
    vp = periodic_veto(periodicity)

    baseline_t: list[float] = []
    candidate_t: list[float] = []
    simple_evidence: list[float] = []
    full_evidence: list[float] = []
    protection: list[float] = []

    for x in samples:
        t = crest.process(x)
        ratio_db = spectral_ratio.process(x)
        spectral = clamp(
            (ratio_db - base.GUARD_THRESHOLD_DB) / base.GUARD_WIDTH_DB,
            0.0,
            1.0,
        )

        q_simple, q_full = plosive.process(x)

        if candidate == "strong_veto_baseline":
            q = 0.0
        elif candidate == "simple_lf_concentration":
            q = q_simple
        elif candidate == "full_plosive_context":
            q = q_full
        else:
            raise ValueError(candidate)

        v_plosive = plosive_veto(q) if q > 0.0 else 0.0
        v = max(vp, v_plosive)

        guard = GUARD_STRENGTH * spectral * (1.0 - v)
        y = t * (1.0 - guard)

        baseline_t.append(t)
        candidate_t.append(y)
        simple_evidence.append(q_simple)
        full_evidence.append(q_full)
        protection.append(v)

    baseline_high = sum(v > base.HIGH_TRANSIENT_THRESHOLD for v in baseline_t) / len(baseline_t)
    candidate_high = sum(v > base.HIGH_TRANSIENT_THRESHOLD for v in candidate_t) / len(candidate_t)

    finite = all(
        math.isfinite(v)
        for v in (
            *baseline_t,
            *candidate_t,
            *simple_evidence,
            *full_evidence,
            *protection,
            periodicity,
        )
    )

    return {
        "periodicity": periodicity,
        "periodic_veto": vp,
        "baseline_high_fraction": baseline_high,
        "candidate_high_fraction": candidate_high,
        "baseline_mean_t": sum(baseline_t) / len(baseline_t),
        "candidate_mean_t": sum(candidate_t) / len(candidate_t),
        "simple_evidence_max": max(simple_evidence),
        "full_evidence_max": max(full_evidence),
        "protection_max": max(protection),
        "finite": 1.0 if finite else 0.0,
    }


def retention(row: dict[str, object]) -> float:
    b = float(row["baseline_high_fraction"])
    c = float(row["candidate_high_fraction"])
    if b <= 1.0e-12:
        return 1.0 if c <= 1.0e-12 else math.inf
    return c / b


def candidate_metrics(
    rows: list[dict[str, object]],
    candidate: str,
) -> dict[str, object]:
    rr = [r for r in rows if r["candidate"] == candidate]
    standard = [r for r in rr if r["case"] in {"voiced_low", "voiced_high"}]
    bright = [r for r in rr if r["case"] in {"voiced_high_bright", "startup_bright"}]
    noisy_voiced = [r for r in rr if r["case"] == "noisy_bright_700"]
    noise = [r for r in rr if r["case"] in {"sibilant", "breath", "long_s"}]
    contaminated = [r for r in rr if r["case"] == "lf_contaminated_sibilant"]
    steady = [r for r in rr if r["case"] == "steady_vowel"]
    plosive = [r for r in rr if r["case"] == "plosive_low"]
    low_nontarget = [
        r for r in rr
        if r["case"] in {"sustained_low", "fry_low", "growl_onset"}
    ]

    metrics: dict[str, object] = {
        "standard_voiced_retention_min": min(retention(r) for r in standard),
        "bright_high_retention_min": min(retention(r) for r in bright),
        "noisy_voiced_retention_min": min(retention(r) for r in noisy_voiced),
        "noise_false_preserve_ratio_max": max(retention(r) for r in noise),
        "lf_contaminated_sibilant_retention_max": max(
            retention(r) for r in contaminated
        ),
        "plosive_retention_min": min(retention(r) for r in plosive),
        "steady_mean_t_delta_max": max(
            abs(float(r["candidate_mean_t"]) - float(r["baseline_mean_t"]))
            for r in steady
        ),
        "low_nontarget_mean_t_delta_max": max(
            abs(float(r["candidate_mean_t"]) - float(r["baseline_mean_t"]))
            for r in low_nontarget
        ),
        "low_nontarget_protection_max": max(
            float(r["protection_max"]) for r in low_nontarget
        ),
        "plosive_simple_evidence_min": min(
            float(r["simple_evidence_max"]) for r in plosive
        ),
        "plosive_full_evidence_min": min(
            float(r["full_evidence_max"]) for r in plosive
        ),
        "all_finite": all(int(r["finite"]) == 1 for r in rr),
    }

    triggered: list[str] = []
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
    if metrics["lf_contaminated_sibilant_retention_max"] > 0.35:
        triggered.append("LF-contaminated sibilant false preservation above 0.35")
    if metrics["plosive_retention_min"] < 0.85:
        triggered.append("plosive retention below 0.85")
    if metrics["steady_mean_t_delta_max"] > 0.03:
        triggered.append("steady-vowel mean transient-factor delta above 0.03")

    metrics["acceptance_met"] = not triggered
    metrics["triggered_criteria"] = triggered
    return metrics


def main() -> None:
    rows: list[dict[str, object]] = []

    for sr in SAMPLE_RATES:
        for case in CASES:
            samples = make_case(sr, case)
            for candidate in (
                "strong_veto_baseline",
                "simple_lf_concentration",
                "full_plosive_context",
            ):
                rows.append(
                    {
                        "sample_rate_hz": sr,
                        "case": case,
                        "candidate": candidate,
                        **evaluate(samples, sr, candidate),
                    }
                )

    metrics = {
        name: candidate_metrics(rows, name)
        for name in (
            "strong_veto_baseline",
            "simple_lf_concentration",
            "full_plosive_context",
        )
    }

    simple = metrics["simple_lf_concentration"]
    full = metrics["full_plosive_context"]

    metrics["full_vs_simple"] = {
        "plosive_retention_improvement": (
            full["plosive_retention_min"] - simple["plosive_retention_min"]
        ),
        "lf_contaminated_sibilant_improvement": (
            simple["lf_contaminated_sibilant_retention_max"]
            - full["lf_contaminated_sibilant_retention_max"]
        ),
        "complexity_justified_synthetically": bool(
            full["acceptance_met"]
            and (
                not simple["acceptance_met"]
                or full["plosive_retention_min"]
                    - simple["plosive_retention_min"] >= 0.03
                or simple["lf_contaminated_sibilant_retention_max"]
                    - full["lf_contaminated_sibilant_retention_max"] >= 0.03
            )
        ),
    }

    qualified = [
        name
        for name in ("simple_lf_concentration", "full_plosive_context")
        if metrics[name]["acceptance_met"]
    ]
    metrics["qualified_candidates"] = qualified

    out = io.StringIO()
    writer = csv.DictWriter(
        out,
        fieldnames=[
            "sample_rate_hz",
            "case",
            "candidate",
            "periodicity",
            "periodic_veto",
            "baseline_high_fraction",
            "candidate_high_fraction",
            "baseline_mean_t",
            "candidate_mean_t",
            "simple_evidence_max",
            "full_evidence_max",
            "protection_max",
            "finite",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)

    triggered = []
    if not qualified:
        triggered.append(
            "neither simple LF-concentration nor full contextual plosive protection passed all locked synthetic gates"
        )

    print(
        json.dumps(
            {
                "scope": (
                    "Synthetic PeakBody independent plosive-protection comparison "
                    "against the rejected strong-periodicity-veto predecessor."
                ),
                "metrics": metrics,
                "measurement_csv": out.getvalue(),
                "acceptance_met": bool(qualified),
                "rejection_triggered": not bool(qualified),
                "triggered_criteria": triggered,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
