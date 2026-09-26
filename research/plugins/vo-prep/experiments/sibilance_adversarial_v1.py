#!/usr/bin/env python3
"""Deterministic adversarial Sibilance Guard v2.3 boundary screen.

Research only. Compares the current contextual ratio detector against a simple
absolute 4-12 kHz level trigger. No product DSP mutation and no raw audio.
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

POSITIVE_CASES = ("s", "sh", "ch", "t")
NEGATIVE_CASES = (
    "bright_vowel",
    "air",
    "breath",
    "falsetto",
    "female_upper",
    "distorted_vocal",
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
    """Mono replay of current Vo.Prep Sibilance Guard v2.3 detector state."""

    def __init__(self, sr: float) -> None:
        self.sr = sr
        self.high = Band(sr, 4000.0, 12000.0)
        self.mid = Band(sr, 1000.0, 4000.0)
        self.broad = Band(sr, 250.0, 12000.0)
        self.upper = Band(sr, 7000.0, 12000.0)
        self.fast_c = 1.0 - math.exp(-1.0 / (0.008 * sr))
        self.slow_c = 1.0 - math.exp(-1.0 / (0.120 * sr))
        self.high_fast = 1.0e-12
        self.mid_fast = 1.0e-12
        self.broad_fast = 1.0e-12
        self.upper_fast = 1.0e-12
        self.high_slow = 1.0e-12
        self.probability = 0.0
        self.divider = 0
        self.event_samples = 0
        self.startup_inhibit = int(round(0.005 * sr))
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

        high = self.high.process(x)
        mid = self.mid.process(x)
        broad = self.broad.process(x)
        upper = self.upper.process(x)

        hp = high * high
        mp = mid * mid
        bp = broad * broad
        up = upper * upper

        self.high_fast += self.fast_c * (hp - self.high_fast)
        self.mid_fast += self.fast_c * (mp - self.mid_fast)
        self.broad_fast += self.fast_c * (bp - self.broad_fast)
        self.upper_fast += self.fast_c * (up - self.upper_fast)
        self.high_slow += self.slow_c * (hp - self.high_slow)

        broad_db = 10.0 * math.log10(max(self.broad_fast, 1.0e-12))
        if broad_db < -90.0:
            self.active = False
            self.suppress = False
            self.startup_inhibit = int(round(0.005 * self.sr))
        elif self.startup_inhibit > 0:
            self.startup_inhibit -= 1

        self.divider += 1
        if self.divider >= 8:
            self.divider = 0
            high_db = 10.0 * math.log10(max(self.high_fast, 1.0e-12))
            mid_db = 10.0 * math.log10(max(self.mid_fast, 1.0e-12))
            upper_db = 10.0 * math.log10(max(self.upper_fast, 1.0e-12))
            high_slow_db = 10.0 * math.log10(max(self.high_slow, 1.0e-12))

            if broad_db < -90.0:
                self.probability = 0.0
            else:
                c1 = self.sigmoid(((high_db - broad_db) + 4.5) / 1.4)
                c2 = self.sigmoid(((high_db - mid_db) - 2.0) / 2.4)
                c3 = self.sigmoid(((high_db - high_slow_db) - 1.0) / 3.0)
                c4 = self.sigmoid(((upper_db - high_db) + 10.0) / 2.5)
                self.probability = math.exp(
                    0.45 * math.log(max(c1, 1.0e-6))
                    + 0.30 * math.log(max(c2, 1.0e-6))
                    + 0.10 * math.log(max(c3, 1.0e-6))
                    + 0.15 * math.log(max(c4, 1.0e-6))
                )
                self.probability = max(0.0, min(1.0, self.probability))

            if self.startup_inhibit > 0:
                self.active = False
            elif self.suppress:
                if self.probability < 0.35:
                    self.suppress = False
            elif not self.active:
                if self.probability >= 0.65:
                    self.active = True
                    self.event_samples = 0
            elif self.probability < 0.45:
                self.active = False

        if self.active:
            self.event_samples += 1
            if self.event_samples > int(round(0.350 * self.sr)):
                self.active = False
                self.suppress = True

        return self.probability, self.active


class HighBandLevelBaseline:
    """Simple baseline: absolute 4-12 kHz level only."""

    def __init__(self, sr: float) -> None:
        self.sr = sr
        self.high = Band(sr, 4000.0, 12000.0)
        self.fast_c = 1.0 - math.exp(-1.0 / (0.008 * sr))
        self.fast = 1.0e-12
        self.probability = 0.0
        self.active = False
        self.event_samples = 0
        self.suppress = False

    @staticmethod
    def sigmoid(x: float) -> float:
        x = max(-12.0, min(12.0, x))
        return 1.0 / (1.0 + math.exp(-x))

    def process(self, x: float) -> tuple[float, bool]:
        if not math.isfinite(x):
            x = 0.0
        high = self.high.process(max(-64.0, min(64.0, x)))
        p = high * high
        self.fast += self.fast_c * (p - self.fast)
        high_db = 10.0 * math.log10(max(self.fast, 1.0e-12))
        self.probability = self.sigmoid((high_db + 34.0) / 3.0)

        if self.suppress:
            if high_db < -41.0:
                self.suppress = False
        elif not self.active:
            if high_db >= -34.0:
                self.active = True
                self.event_samples = 0
        elif high_db < -38.0:
            self.active = False

        if self.active:
            self.event_samples += 1
            if self.event_samples > int(round(0.350 * self.sr)):
                self.active = False
                self.suppress = True

        return self.probability, self.active


def vowel(t: float, f0: float, harmonics: int = 18, tilt: float = 1.15, amp: float = 0.8) -> float:
    x = 0.0
    for h in range(1, harmonics + 1):
        a = amp / (h ** tilt)
        x += a * math.sin(2.0 * math.pi * f0 * h * t + 0.07 * h)
    return 0.055 * x


def hf_cluster(i: int, sr: float, lo: float, hi: float, amp: float) -> float:
    # Deterministic quasi-noise from incommensurate sinusoid clusters.
    freqs = (lo, lo * 1.19, lo * 1.43, (lo + hi) * 0.5, hi * 0.83, hi)
    x = 0.0
    for k, f in enumerate(freqs):
        x += math.sin(2.0 * math.pi * f * i / sr + 0.41 * k)
    return amp * x / len(freqs)


def envelope(u: float, attack: float, release: float, duration: float) -> float:
    if u < 0.0 or u >= duration:
        return 0.0
    a = min(1.0, u / max(attack, 1.0e-6))
    tail = math.exp(-max(0.0, u - attack) / max(release, 1.0e-6))
    return a * tail


def sample_for(case: str, i: int, sr: float, scale: float = 1.0) -> float:
    t = i / sr
    u = t - EVENT_START_S
    pre = vowel(t, 180.0, harmonics=12, tilt=1.25, amp=0.65)

    if case == "s":
        x = pre + envelope(u, 0.008, 0.060, 0.160) * hf_cluster(i, sr, 5200.0, 10500.0, 0.42)
    elif case == "sh":
        x = pre + envelope(u, 0.008, 0.070, 0.170) * hf_cluster(i, sr, 3400.0, 7600.0, 0.46)
    elif case == "ch":
        x = pre + envelope(u, 0.003, 0.028, 0.075) * hf_cluster(i, sr, 3200.0, 9000.0, 0.62)
    elif case == "t":
        x = pre + envelope(u, 0.0015, 0.012, 0.032) * hf_cluster(i, sr, 4800.0, 11000.0, 0.78)
    elif case == "bright_vowel":
        x = pre if u < 0.0 else vowel(t, 260.0, harmonics=30, tilt=0.82, amp=0.92)
    elif case == "air":
        x = pre
        if u >= 0.0:
            x += 0.030 * hf_cluster(i, sr, 6500.0, 11800.0, 1.0)
    elif case == "breath":
        x = pre if u < 0.0 else (
            0.050 * hf_cluster(i, sr, 1800.0, 10500.0, 1.0)
            + 0.018 * hf_cluster(i, sr, 7000.0, 11800.0, 1.0)
        )
    elif case == "falsetto":
        x = pre if u < 0.0 else vowel(t, 520.0, harmonics=18, tilt=0.90, amp=0.90)
    elif case == "female_upper":
        x = pre if u < 0.0 else vowel(t, 340.0, harmonics=24, tilt=0.95, amp=0.96)
    elif case == "distorted_vocal":
        if u < 0.0:
            x = pre
        else:
            raw = vowel(t, 210.0, harmonics=16, tilt=1.0, amp=1.35)
            x = 0.20 * math.tanh(7.0 * raw)
    else:
        raise ValueError(case)

    return max(-0.98, min(0.98, x * scale))


def run_case(case: str, sr: int, detector_cls, scale: float = 1.0) -> dict[str, float | int | bool | None]:
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
    baseline_neg = [r for r in rows if r["case"] in NEGATIVE_CASES and r["detector"] == "high_level"]

    positive_detection_fraction = sum(bool(r["detected"]) for r in positives) / max(1, len(positives))
    s_sh = [r for r in positives if r["case"] in ("s", "sh")]
    s_sh_all_detected = all(bool(r["detected"]) for r in s_sh)
    onset = [
        float(r["first_onset_latency_ms"])
        for r in positives
        if r["first_onset_latency_ms"] is not None
    ]

    context_neg_occ = [float(r["active_occupancy_pct"]) for r in negatives]
    base_neg_occ = [float(r["active_occupancy_pct"]) for r in baseline_neg]
    context_neg_mean = sum(context_neg_occ) / max(1, len(context_neg_occ))
    base_neg_mean = sum(base_neg_occ) / max(1, len(base_neg_occ))

    sr_spreads = []
    for case in POSITIVE_CASES + NEGATIVE_CASES:
        vals = [
            float(r["max_probability"]) for r in rows
            if r["detector"] == "context" and r["case"] == case
        ]
        sr_spreads.append(max(vals) - min(vals))

    return {
        "positive_detection_fraction": positive_detection_fraction,
        "s_and_sh_detected_all_sample_rates": s_sh_all_detected,
        "max_positive_onset_latency_ms": max(onset) if onset else None,
        "context_negative_occupancy_mean_pct": context_neg_mean,
        "context_negative_occupancy_max_pct": max(context_neg_occ),
        "high_level_negative_occupancy_mean_pct": base_neg_mean,
        "context_to_high_level_false_occupancy_ratio": (
            context_neg_mean / base_neg_mean if base_neg_mean > 1.0e-9 else None
        ),
        "max_context_probability_sample_rate_spread": max(sr_spreads),
        "max_context_active_duration_ms": max(float(r["max_active_duration_ms"]) for r in positives + negatives),
    }


def scale_invariance() -> dict:
    sr = 48000
    scales = (10 ** (-12.0 / 20.0), 1.0, 10 ** (12.0 / 20.0))
    out = {}
    max_prob = 0.0
    max_occ = 0.0
    for case in ("s", "bright_vowel", "breath"):
        vals = [run_case(case, sr, ContextDetector, scale=s) for s in scales]
        prob = [float(v["max_probability"]) for v in vals]
        occ = [float(v["active_occupancy_pct"]) for v in vals]
        out[case] = {
            "probability_spread": max(prob) - min(prob),
            "occupancy_spread_pct": max(occ) - min(occ),
        }
        max_prob = max(max_prob, out[case]["probability_spread"])
        max_occ = max(max_occ, out[case]["occupancy_spread_pct"])
    return {"cases": out, "max_probability_spread": max_prob, "max_occupancy_spread_pct": max_occ}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for sr in SAMPLE_RATES:
        for case in POSITIVE_CASES + NEGATIVE_CASES:
            for name, cls in (("high_level", HighBandLevelBaseline), ("context", ContextDetector)):
                m = run_case(case, sr, cls)
                rows.append({"sample_rate": sr, "case": case, "detector": name, **m})

    agg = aggregate(rows)
    scale = scale_invariance()
    ratio = agg["context_to_high_level_false_occupancy_ratio"]

    gates = {
        "positive_detection_fraction_ge_0_85": agg["positive_detection_fraction"] >= 0.85,
        "s_sh_detected_all_sr": bool(agg["s_and_sh_detected_all_sample_rates"]),
        "positive_onset_latency_le_30ms": (
            agg["max_positive_onset_latency_ms"] is not None
            and agg["max_positive_onset_latency_ms"] <= 30.0
        ),
        "negative_occupancy_mean_le_8pct": agg["context_negative_occupancy_mean_pct"] <= 8.0,
        "negative_occupancy_max_le_20pct": agg["context_negative_occupancy_max_pct"] <= 20.0,
        "false_occupancy_le_35pct_of_high_level": ratio is not None and ratio <= 0.35,
        "event_duration_le_355ms": agg["max_context_active_duration_ms"] <= 355.0,
        "sample_rate_probability_spread_le_0_08": agg["max_context_probability_sample_rate_spread"] <= 0.08,
        "input_scale_probability_spread_le_0_05": scale["max_probability_spread"] <= 0.05,
        "input_scale_occupancy_spread_le_5pct": scale["max_occupancy_spread_pct"] <= 5.0,
    }

    finite = True
    for row in rows:
        for key in ("max_probability", "active_occupancy_pct", "max_active_duration_ms"):
            finite = finite and math.isfinite(float(row[key]))
    gates["all_finite"] = finite

    accepted = all(gates.values())
    result = {
        "decision": "GO_TO_REAL_VOCAL" if accepted else "REVISE",
        "current_detector": "Vo.Prep Sibilance Guard v2.3 contextual detector",
        "simple_baseline": "absolute 4-12 kHz high-band level trigger",
        "sample_rates": list(SAMPLE_RATES),
        "positive_cases": list(POSITIVE_CASES),
        "negative_cases": list(NEGATIVE_CASES),
        "aggregate": agg,
        "scale_invariance": scale,
        "gates": gates,
        "acceptance_met": accepted,
        "raw_audio_persisted": False,
    }

    (out / "sibilance_adversarial_results.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    with (out / "sibilance_adversarial_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "sample_rate", "case", "detector", "max_probability",
            "active_occupancy_pct", "event_count", "max_active_duration_ms",
            "first_onset_latency_ms", "detected",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# Vo.Prep Sibilance Guard adversarial screen",
        "",
        f"Decision: {result['decision']}",
        "",
        "Simple baseline: absolute 4-12 kHz high-band level trigger.",
        "Candidate: current v2.3 contextual ratio detector.",
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
        "Failure keeps the current product baseline unchanged and routes to bounded detector refinement.",
    ]
    (out / "sibilance_adversarial_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print((out / "sibilance_adversarial_report.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
