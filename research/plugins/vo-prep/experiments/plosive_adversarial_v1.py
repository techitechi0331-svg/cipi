#!/usr/bin/env python3
"""Deterministic adversarial Plosive Guard v2.2 boundary screen.

Research only. Compares the current context-normalised detector against a
simple LF-onset-only baseline. No product DSP mutation and no raw audio.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

SAMPLE_RATES = (44100, 48000, 96000)
TOTAL_SECONDS = 1.40
EVENT_START_S = 0.45
EVAL_START_S = 0.35
EVAL_END_S = 1.25
RANDOM_SEED = 20260926

POSITIVE_CASES = (
    "plosive_soft",
    "plosive_nominal",
    "plosive_strong",
    "plosive_repeated",
)
NEGATIVE_CASES = (
    "low_vowel",
    "proximity",
    "fry",
    "growl",
    "long_lf_note",
    "male_low",
    "female_bright",
    "breath",
    "word_onset",
)


class Band:
    def __init__(self, sr: float, hp_hz: float, lp_hz: float) -> None:
        dt = 1.0 / sr
        rc = 1.0 / (2.0 * math.pi * max(1.0, hp_hz))
        self.hp_a = rc / (rc + dt)
        self.lp_alpha = 1.0 - math.exp(-2.0 * math.pi * max(1.0, lp_hz) / sr)
        self.prev_x = 0.0
        self.prev_high = 0.0
        self.low = 0.0

    def process(self, x: float) -> float:
        high = self.hp_a * (self.prev_high + x - self.prev_x)
        self.prev_x = x
        self.prev_high = high
        self.low += self.lp_alpha * (high - self.low)
        return self.low


class ContextDetector:
    """Mono replay of current Vo.Prep Plosive Guard v2.2 detector state."""

    def __init__(self, sr: float) -> None:
        self.sr = sr
        self.sub = Band(sr, 20.0, 80.0)
        self.mid = Band(sr, 250.0, 1000.0)
        self.broad = Band(sr, 80.0, 4000.0)
        self.fast_c = 1.0 - math.exp(-1.0 / (0.008 * sr))
        self.sub_slow_c = 1.0 - math.exp(-1.0 / (0.250 * sr))
        self.broad_slow_c = 1.0 - math.exp(-1.0 / (0.080 * sr))
        self.sub_fast = 1.0e-12
        self.mid_fast = 1.0e-12
        self.broad_fast = 1.0e-12
        self.sub_slow = 1.0e-12
        self.broad_slow = 1.0e-12
        self.probability = 0.0
        self.divider = 0
        self.event_samples = 0
        self.active = False
        self.suppress = False

    @staticmethod
    def sigmoid(x: float) -> float:
        x = max(-12.0, min(12.0, x))
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def follow(value: float, state: float, coeff: float) -> float:
        return state + coeff * (value - state)

    def process(self, x: float) -> tuple[float, bool]:
        if not math.isfinite(x):
            x = 0.0
        x = max(-64.0, min(64.0, x))

        sub = self.sub.process(x)
        mid = self.mid.process(x)
        broad = self.broad.process(x)

        self.sub_fast = self.follow(sub * sub, self.sub_fast, self.fast_c)
        self.mid_fast = self.follow(mid * mid, self.mid_fast, self.fast_c)
        self.broad_fast = self.follow(broad * broad, self.broad_fast, self.fast_c)
        self.sub_slow = self.follow(sub * sub, self.sub_slow, self.sub_slow_c)
        self.broad_slow = self.follow(broad * broad, self.broad_slow, self.broad_slow_c)

        self.divider += 1
        if self.divider >= 8:
            self.divider = 0
            sub_db = 10.0 * math.log10(max(self.sub_fast, 1.0e-12))
            mid_db = 10.0 * math.log10(max(self.mid_fast, 1.0e-12))
            broad_db = 10.0 * math.log10(max(self.broad_fast, 1.0e-12))
            sub_slow_db = 10.0 * math.log10(max(self.sub_slow, 1.0e-12))
            broad_slow_db = 10.0 * math.log10(max(self.broad_slow, 1.0e-12))

            if broad_db < -90.0:
                self.probability = 0.0
            else:
                c1 = self.sigmoid(((sub_db - sub_slow_db) - 7.0) / 2.0)
                c2 = self.sigmoid(((sub_db - mid_db) - 12.0) / 3.5)
                c3 = self.sigmoid(((sub_db - broad_db) - 2.5) / 1.8)
                c4 = self.sigmoid(((broad_db - broad_slow_db) - 1.0) / 3.0)
                self.probability = math.exp(
                    0.44 * math.log(max(c1, 1.0e-6))
                    + 0.30 * math.log(max(c2, 1.0e-6))
                    + 0.20 * math.log(max(c3, 1.0e-6))
                    + 0.06 * math.log(max(c4, 1.0e-6))
                )
                self.probability = max(0.0, min(1.0, self.probability))

            if self.suppress:
                if self.probability < 0.45:
                    self.suppress = False
            elif not self.active:
                if self.probability >= 0.75:
                    self.active = True
                    self.event_samples = 0
            elif self.probability < 0.55:
                self.active = False

        if self.active:
            self.event_samples += 1
            if self.event_samples > int(round(0.120 * self.sr)):
                self.active = False
                self.suppress = True

        return self.probability, self.active


class LfOnsetBaseline:
    """Simple baseline: current 20-80 Hz onset feature only."""

    def __init__(self, sr: float) -> None:
        self.sr = sr
        self.sub = Band(sr, 20.0, 80.0)
        self.fast_c = 1.0 - math.exp(-1.0 / (0.008 * sr))
        self.slow_c = 1.0 - math.exp(-1.0 / (0.250 * sr))
        self.fast = 1.0e-12
        self.slow = 1.0e-12
        self.probability = 0.0
        self.divider = 0
        self.event_samples = 0
        self.active = False
        self.suppress = False

    @staticmethod
    def sigmoid(x: float) -> float:
        x = max(-12.0, min(12.0, x))
        return 1.0 / (1.0 + math.exp(-x))

    def process(self, x: float) -> tuple[float, bool]:
        if not math.isfinite(x):
            x = 0.0
        x = max(-64.0, min(64.0, x))
        sub = self.sub.process(x)
        p = sub * sub
        self.fast += self.fast_c * (p - self.fast)
        self.slow += self.slow_c * (p - self.slow)

        self.divider += 1
        if self.divider >= 8:
            self.divider = 0
            fast_db = 10.0 * math.log10(max(self.fast, 1.0e-12))
            slow_db = 10.0 * math.log10(max(self.slow, 1.0e-12))
            self.probability = self.sigmoid(((fast_db - slow_db) - 7.0) / 2.0)

            if self.suppress:
                if self.probability < 0.45:
                    self.suppress = False
            elif not self.active:
                if self.probability >= 0.75:
                    self.active = True
                    self.event_samples = 0
            elif self.probability < 0.55:
                self.active = False

        if self.active:
            self.event_samples += 1
            if self.event_samples > int(round(0.120 * self.sr)):
                self.active = False
                self.suppress = True

        return self.probability, self.active


def base_vowel(t: float, f0: float, amp: float = 1.0) -> float:
    return amp * (
        0.060 * math.sin(2.0 * math.pi * f0 * t)
        + 0.035 * math.sin(2.0 * math.pi * 2.0 * f0 * t + 0.17)
        + 0.018 * math.sin(2.0 * math.pi * 3.0 * f0 * t + 0.31)
        + 0.010 * math.sin(2.0 * math.pi * 4.0 * f0 * t + 0.47)
    )


def deterministic_noise(i: int) -> float:
    # Sum of incommensurate high-frequency sines: deterministic, bounded and
    # sufficient for breath/word-onset confound screening.
    return (
        0.50 * math.sin(0.754877666 * i)
        + 0.31 * math.sin(1.324717957 * i + 0.7)
        + 0.19 * math.sin(2.414213562 * i + 1.2)
    )


def burst(t_rel: float, amp: float) -> float:
    if t_rel < 0.0 or t_rel >= 0.090:
        return 0.0
    env = math.exp(-t_rel / 0.027)
    return amp * env * (
        0.70 * math.sin(2.0 * math.pi * 48.0 * t_rel)
        + 0.30 * math.sin(2.0 * math.pi * 68.0 * t_rel + 0.2)
    )


def sample_for(case: str, i: int, sr: float, scale: float = 1.0) -> float:
    t = i / sr
    u = t - EVENT_START_S
    pre = base_vowel(t, 135.0, 0.55)

    if case == "plosive_soft":
        x = pre + burst(u, 0.38)
    elif case == "plosive_nominal":
        x = pre + burst(u, 0.65)
    elif case == "plosive_strong":
        x = pre + burst(u, 0.92)
    elif case == "plosive_repeated":
        x = pre + burst(u, 0.65) + burst(t - 0.80, 0.62)
    elif case == "low_vowel":
        x = pre if u < 0.0 else base_vowel(t, 86.0, 1.35)
    elif case == "proximity":
        x = pre
        if u >= 0.0:
            ramp = min(1.0, max(0.0, u / 0.025))
            x += ramp * (
                0.095 * math.sin(2.0 * math.pi * 74.0 * t)
                + 0.035 * math.sin(2.0 * math.pi * 148.0 * t)
            )
    elif case == "fry":
        if u < 0.0:
            x = pre
        else:
            pulse = math.sin(2.0 * math.pi * 43.0 * t)
            gate = 1.0 if pulse > 0.78 else 0.10
            x = 0.095 * gate + 0.028 * math.sin(2.0 * math.pi * 86.0 * t)
    elif case == "growl":
        if u < 0.0:
            x = pre
        else:
            a = math.sin(2.0 * math.pi * 72.0 * t)
            b = math.sin(2.0 * math.pi * 145.0 * t + 0.3)
            c = math.sin(2.0 * math.pi * 218.0 * t + 0.5)
            x = 0.28 * math.tanh(3.0 * (0.42 * a + 0.26 * b + 0.16 * c))
    elif case == "long_lf_note":
        x = pre if u < 0.0 else (
            0.12 * math.sin(2.0 * math.pi * 55.0 * t)
            + 0.055 * math.sin(2.0 * math.pi * 110.0 * t)
            + 0.024 * math.sin(2.0 * math.pi * 165.0 * t)
        )
    elif case == "male_low":
        x = pre if u < 0.0 else base_vowel(t, 92.0, 1.10)
    elif case == "female_bright":
        x = pre if u < 0.0 else (
            base_vowel(t, 235.0, 0.95)
            + 0.012 * math.sin(2.0 * math.pi * 4935.0 * t)
            + 0.010 * math.sin(2.0 * math.pi * 7310.0 * t)
        )
    elif case == "breath":
        x = pre if u < 0.0 else 0.045 * (deterministic_noise(i) - deterministic_noise(max(0, i - 1)))
    elif case == "word_onset":
        x = pre
        if 0.0 <= u < 0.050:
            env = math.exp(-u / 0.014)
            x += 0.12 * env * deterministic_noise(i)
        if u >= 0.0:
            x += base_vowel(t, 155.0, 0.55)
    else:
        raise ValueError(case)

    return max(-0.98, min(0.98, x * scale))


def run_case(case: str, sr: int, detector_cls, scale: float = 1.0) -> dict[str, float | int | bool]:
    detector = detector_cls(float(sr))
    n = int(round(TOTAL_SECONDS * sr))
    eval_start = int(round(EVAL_START_S * sr))
    eval_end = int(round(EVAL_END_S * sr))

    max_probability = 0.0
    active_samples = 0
    transitions = 0
    previous_active = False
    first_active_sample = None
    current_run = 0
    max_run = 0

    for i in range(n):
        p, active = detector.process(sample_for(case, i, float(sr), scale))
        if eval_start <= i < eval_end:
            max_probability = max(max_probability, p)
            if active:
                active_samples += 1
                current_run += 1
                max_run = max(max_run, current_run)
                if not previous_active:
                    transitions += 1
                    if first_active_sample is None:
                        first_active_sample = i
            else:
                current_run = 0
            previous_active = active

    eval_samples = max(1, eval_end - eval_start)
    latency_ms = None
    if first_active_sample is not None:
        latency_ms = 1000.0 * (first_active_sample / sr - EVENT_START_S)

    return {
        "max_probability": max_probability,
        "active_occupancy_pct": 100.0 * active_samples / eval_samples,
        "event_count": transitions,
        "max_active_duration_ms": 1000.0 * max_run / sr,
        "first_onset_latency_ms": latency_ms,
        "detected": transitions > 0,
    }


def aggregate(rows: list[dict]) -> dict:
    positives = [r for r in rows if r["case"] in POSITIVE_CASES and r["detector"] == "context"]
    negatives = [r for r in rows if r["case"] in NEGATIVE_CASES and r["detector"] == "context"]
    baseline_neg = [r for r in rows if r["case"] in NEGATIVE_CASES and r["detector"] == "lf_only"]

    positive_detection_fraction = sum(bool(r["detected"]) for r in positives) / max(1, len(positives))
    nominal_required = [
        r for r in positives
        if r["case"] in ("plosive_nominal", "plosive_strong", "plosive_repeated")
    ]
    nominal_all_detected = all(bool(r["detected"]) for r in nominal_required)

    repeated = [r for r in positives if r["case"] == "plosive_repeated"]
    repeated_two_events_all_sr = all(int(r["event_count"]) >= 2 for r in repeated)

    onset_values = [
        float(r["first_onset_latency_ms"])
        for r in positives
        if r["case"] in ("plosive_nominal", "plosive_strong")
        and r["first_onset_latency_ms"] is not None
    ]

    context_neg_occ = [float(r["active_occupancy_pct"]) for r in negatives]
    baseline_neg_occ = [float(r["active_occupancy_pct"]) for r in baseline_neg]
    context_neg_mean = sum(context_neg_occ) / max(1, len(context_neg_occ))
    baseline_neg_mean = sum(baseline_neg_occ) / max(1, len(baseline_neg_occ))

    case_prob_spreads = []
    for case in POSITIVE_CASES + NEGATIVE_CASES:
        vals = [
            float(r["max_probability"]) for r in rows
            if r["detector"] == "context" and r["case"] == case
        ]
        case_prob_spreads.append(max(vals) - min(vals))

    max_duration = max(float(r["max_active_duration_ms"]) for r in positives + negatives)
    neg_max = max(context_neg_occ)

    return {
        "positive_detection_fraction": positive_detection_fraction,
        "nominal_strong_repeated_all_detected": nominal_all_detected,
        "repeated_two_events_all_sample_rates": repeated_two_events_all_sr,
        "max_nominal_strong_onset_latency_ms": max(onset_values) if onset_values else None,
        "context_negative_occupancy_mean_pct": context_neg_mean,
        "context_negative_occupancy_max_pct": neg_max,
        "lf_only_negative_occupancy_mean_pct": baseline_neg_mean,
        "context_to_lf_only_false_occupancy_ratio": (
            context_neg_mean / baseline_neg_mean if baseline_neg_mean > 1.0e-9 else None
        ),
        "max_context_probability_sample_rate_spread": max(case_prob_spreads),
        "max_context_active_duration_ms": max_duration,
    }


def scale_invariance() -> dict:
    sr = 48000
    scales = (10 ** (-12.0 / 20.0), 1.0, 10 ** (12.0 / 20.0))
    out = {}
    max_prob_spread = 0.0
    max_occ_spread = 0.0
    for case in ("plosive_nominal", "low_vowel", "growl"):
        vals = [run_case(case, sr, ContextDetector, scale=s) for s in scales]
        prob = [float(v["max_probability"]) for v in vals]
        occ = [float(v["active_occupancy_pct"]) for v in vals]
        out[case] = {
            "probability_spread": max(prob) - min(prob),
            "occupancy_spread_pct": max(occ) - min(occ),
        }
        max_prob_spread = max(max_prob_spread, out[case]["probability_spread"])
        max_occ_spread = max(max_occ_spread, out[case]["occupancy_spread_pct"])
    return {
        "cases": out,
        "max_probability_spread": max_prob_spread,
        "max_occupancy_spread_pct": max_occ_spread,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for sr in SAMPLE_RATES:
        for case in POSITIVE_CASES + NEGATIVE_CASES:
            for name, cls in (("lf_only", LfOnsetBaseline), ("context", ContextDetector)):
                m = run_case(case, sr, cls)
                rows.append({"sample_rate": sr, "case": case, "detector": name, **m})

    agg = aggregate(rows)
    scale = scale_invariance()

    ratio = agg["context_to_lf_only_false_occupancy_ratio"]
    gates = {
        "positive_detection_fraction_ge_0_90": agg["positive_detection_fraction"] >= 0.90,
        "nominal_strong_repeated_detected_all_sr": bool(agg["nominal_strong_repeated_all_detected"]),
        "repeated_two_events_all_sr": bool(agg["repeated_two_events_all_sample_rates"]),
        "nominal_strong_onset_latency_le_20ms": (
            agg["max_nominal_strong_onset_latency_ms"] is not None
            and agg["max_nominal_strong_onset_latency_ms"] <= 20.0
        ),
        "negative_occupancy_mean_le_5pct": agg["context_negative_occupancy_mean_pct"] <= 5.0,
        "negative_occupancy_max_le_12pct": agg["context_negative_occupancy_max_pct"] <= 12.0,
        "false_occupancy_le_35pct_of_lf_only": ratio is not None and ratio <= 0.35,
        "event_duration_le_125ms": agg["max_context_active_duration_ms"] <= 125.0,
        "sample_rate_probability_spread_le_0_06": agg["max_context_probability_sample_rate_spread"] <= 0.06,
        "input_scale_probability_spread_le_0_05": scale["max_probability_spread"] <= 0.05,
        "input_scale_occupancy_spread_le_3pct": scale["max_occupancy_spread_pct"] <= 3.0,
    }

    finite = True
    for row in rows:
        for key in ("max_probability", "active_occupancy_pct", "max_active_duration_ms"):
            finite = finite and math.isfinite(float(row[key]))
    gates["all_finite"] = finite

    accepted = all(gates.values())
    result = {
        "decision": "GO_TO_REAL_VOCAL" if accepted else "REVISE",
        "current_detector": "Vo.Prep Plosive Guard v2.2 context detector",
        "simple_baseline": "20-80 Hz LF onset only",
        "sample_rates": list(SAMPLE_RATES),
        "positive_cases": list(POSITIVE_CASES),
        "negative_cases": list(NEGATIVE_CASES),
        "aggregate": agg,
        "scale_invariance": scale,
        "gates": gates,
        "acceptance_met": accepted,
        "raw_audio_persisted": False,
    }

    (out / "plosive_adversarial_results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    with (out / "plosive_adversarial_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "sample_rate", "case", "detector", "max_probability",
            "active_occupancy_pct", "event_count", "max_active_duration_ms",
            "first_onset_latency_ms", "detected",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# Vo.Prep Plosive Guard adversarial screen",
        "",
        f"Decision: {result['decision']}",
        "",
        "Simple baseline: 20-80 Hz LF onset only.",
        "Candidate: current v2.2 contextual detector.",
        "",
        "## Aggregate",
        "",
        json.dumps(agg, indent=2),
        "",
        "## Gates",
        "",
        json.dumps(gates, indent=2),
        "",
        "Passing authorizes real-vocal false-positive/false-negative validation only.",
        "Failure keeps the current product baseline unchanged and routes to a bounded detector refinement study.",
    ]
    (out / "plosive_adversarial_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print((out / "plosive_adversarial_report.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
