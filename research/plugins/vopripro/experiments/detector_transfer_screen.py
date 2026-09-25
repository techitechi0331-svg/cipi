#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path

SAMPLE_RATES = (44100, 48000, 96000, 192000)
RATIO = 2.7
KNEE_DB = 12.0
CAL_GR_DB = 3.0
MAX_GR_DB = 6.0
ATTACK_S = 0.020
RELEASE_S = 0.110
RMS_TAU_S = 0.025
HPF_HZ = 80.0
HPF_Q = 0.70710678
BASELINE_PEAK_WEIGHT = 0.35
CANDIDATE_PEAK_ALLOWANCE_DB = 6.0
SEED = 20260926


def db_to_gain(db: float) -> float:
    return 10.0 ** (db / 20.0)


def gain_to_db(gain: float) -> float:
    return 20.0 * math.log10(max(abs(gain), 1.0e-12))


def one_pole_coeff(seconds: float, sample_rate: float) -> float:
    return math.exp(-1.0 / (seconds * sample_rate))


class HPF:
    def __init__(self, sample_rate: float, cutoff_hz: float = HPF_HZ, q: float = HPF_Q):
        w0 = 2.0 * math.pi * cutoff_hz / sample_rate
        c = math.cos(w0)
        s = math.sin(w0)
        alpha = s / (2.0 * q)
        a0 = 1.0 + alpha
        self.b0 = ((1.0 + c) * 0.5) / a0
        self.b1 = (-(1.0 + c)) / a0
        self.b2 = ((1.0 + c) * 0.5) / a0
        self.a1 = (-2.0 * c) / a0
        self.a2 = (1.0 - alpha) / a0
        self.z1 = 0.0
        self.z2 = 0.0

    def process(self, x: float) -> float:
        y = self.b0 * x + self.z1
        self.z1 = self.b1 * x - self.a1 * y + self.z2
        self.z2 = self.b2 * x - self.a2 * y
        return y


class Detector:
    def __init__(self, sample_rate: float, mode: str):
        self.sr = float(sample_rate)
        self.mode = mode
        self.hpf = HPF(self.sr)
        self.rms_coeff = one_pole_coeff(RMS_TAU_S, self.sr)
        self.rms_power = 0.0

    def process_db(self, x: float) -> float:
        sc = self.hpf.process(x)
        peak = abs(sc)
        self.rms_power = self.rms_coeff * self.rms_power + (1.0 - self.rms_coeff) * sc * sc
        rms = math.sqrt(max(self.rms_power, 0.0))

        if self.mode == "baseline":
            amp = BASELINE_PEAK_WEIGHT * peak + (1.0 - BASELINE_PEAK_WEIGHT) * rms
        elif self.mode == "candidate":
            amp = max(rms, peak * db_to_gain(-CANDIDATE_PEAK_ALLOWANCE_DB))
        else:
            raise ValueError(self.mode)

        return gain_to_db(amp)


def soft_knee_gr(input_db: float, threshold_db: float) -> float:
    k = 1.0 - 1.0 / RATIO
    d = input_db - threshold_db
    half = KNEE_DB * 0.5
    if d <= -half:
        return 0.0
    if d >= half:
        return max(0.0, k * d)
    u = d + half
    return max(0.0, k * u * u / (2.0 * KNEE_DB))


def threshold_for_calibration(level_db: float) -> float:
    k = 1.0 - 1.0 / RATIO
    half = KNEE_DB * 0.5
    gr_at_upper = k * half
    if CAL_GR_DB >= gr_at_upper:
        d = CAL_GR_DB / k
    else:
        d = math.sqrt(max(0.0, 2.0 * KNEE_DB * CAL_GR_DB / k)) - half
    return level_db - d


def measure_reference_level(sample_rate: int, mode: str) -> float:
    det = Detector(sample_rate, mode)
    duration = 1.0
    n = int(round(duration * sample_rate))
    start_collect = int(round(0.75 * sample_rate))
    values = []
    amp = db_to_gain(-18.0)
    for i in range(n):
        t = i / sample_rate
        x = amp * math.sin(2.0 * math.pi * 220.0 * t)
        db = det.process_db(x)
        if i >= start_collect:
            values.append(db)
    return sum(values) / len(values)


def make_case(name: str, sample_rate: int) -> list[float]:
    rng = random.Random(SEED + sample_rate + sum(ord(c) for c in name))
    pre = int(0.20 * sample_rate)
    post = int(0.50 * sample_rate)
    body_amp = db_to_gain(-18.0)
    out = [0.0] * pre

    if name == "sustained_body":
        dur = int(0.80 * sample_rate)
        for i in range(dur):
            t = i / sample_rate
            out.append(body_amp * math.sin(2.0 * math.pi * 220.0 * t))

    elif name in ("transient_10ms", "transient_30ms"):
        dur_ms = 10.0 if name.endswith("10ms") else 30.0
        dur = int(round(dur_ms * 0.001 * sample_rate))
        amp = db_to_gain(-6.0)
        for i in range(dur):
            t = i / sample_rate
            env = math.sin(math.pi * (i + 0.5) / max(1, dur))
            out.append(amp * env * math.sin(2.0 * math.pi * 2200.0 * t))

    elif name == "body_plus_transient":
        dur = int(0.80 * sample_rate)
        burst_start = int(0.30 * sample_rate)
        burst_len = int(0.012 * sample_rate)
        for i in range(dur):
            t = i / sample_rate
            x = body_amp * math.sin(2.0 * math.pi * 220.0 * t)
            if burst_start <= i < burst_start + burst_len:
                j = i - burst_start
                env = math.sin(math.pi * (j + 0.5) / max(1, burst_len))
                x += db_to_gain(-7.0) * env * math.sin(2.0 * math.pi * 2400.0 * t)
            out.append(x)

    elif name == "plosive_low":
        dur = int(0.060 * sample_rate)
        amp = db_to_gain(-5.0)
        for i in range(dur):
            t = i / sample_rate
            env = math.exp(-5.0 * i / max(1, dur))
            out.append(amp * env * math.sin(2.0 * math.pi * 70.0 * t))

    elif name == "sibilant_high":
        dur = int(0.120 * sample_rate)
        amp = db_to_gain(-10.0)
        prev = 0.0
        for i in range(dur):
            white = rng.uniform(-1.0, 1.0)
            high = white - 0.92 * prev
            prev = white
            env = math.sin(math.pi * (i + 0.5) / max(1, dur))
            out.append(amp * env * high)

    elif name == "breath_noise":
        dur = int(0.500 * sample_rate)
        amp = db_to_gain(-28.0)
        for _ in range(dur):
            out.append(amp * rng.uniform(-1.0, 1.0))

    elif name == "body_step":
        dur = int(1.0 * sample_rate)
        for i in range(dur):
            t = i / sample_rate
            amp = db_to_gain(-22.0 if i < dur // 2 else -14.0)
            out.append(amp * math.sin(2.0 * math.pi * 220.0 * t))
    else:
        raise ValueError(name)

    out.extend([0.0] * post)
    return out


def run_case(sample_rate: int, mode: str, threshold_db: float, samples: list[float]) -> dict:
    det = Detector(sample_rate, mode)
    attack = one_pole_coeff(ATTACK_S, sample_rate)
    release = one_pole_coeff(RELEASE_S, sample_rate)
    gr = 0.0
    trajectory = []
    detector_values = []

    for x in samples:
        detector_db = det.process_db(x)
        desired = min(MAX_GR_DB, soft_knee_gr(detector_db, threshold_db))
        coeff = attack if desired > gr else release
        gr = coeff * gr + (1.0 - coeff) * desired
        if not math.isfinite(gr):
            raise RuntimeError("non-finite GR")
        trajectory.append(gr)
        detector_values.append(detector_db)

    peak_gr = max(trajectory) if trajectory else 0.0
    mean_gr = sum(trajectory) / len(trajectory) if trajectory else 0.0

    active = [g for g, x in zip(trajectory, samples) if abs(x) > db_to_gain(-55.0)]
    active_mean_gr = sum(active) / len(active) if active else 0.0

    return {
        "peak_gr_db": peak_gr,
        "mean_gr_db": mean_gr,
        "active_mean_gr_db": active_mean_gr,
        "max_detector_db": max(detector_values) if detector_values else -240.0,
        "finite": all(math.isfinite(v) for v in trajectory + detector_values),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = [
        "sustained_body",
        "transient_10ms",
        "transient_30ms",
        "body_plus_transient",
        "plosive_low",
        "sibilant_high",
        "breath_noise",
        "body_step",
    ]

    rows = []
    refs = []
    for sr in SAMPLE_RATES:
        levels = {
            mode: measure_reference_level(sr, mode)
            for mode in ("baseline", "candidate")
        }
        thresholds = {
            mode: threshold_for_calibration(levels[mode])
            for mode in ("baseline", "candidate")
        }

        refs.append({
            "sample_rate": sr,
            "baseline_reference_db": levels["baseline"],
            "candidate_reference_db": levels["candidate"],
            "baseline_threshold_db": thresholds["baseline"],
            "candidate_threshold_db": thresholds["candidate"],
        })

        for case in cases:
            samples = make_case(case, sr)
            results = {
                mode: run_case(sr, mode, thresholds[mode], samples)
                for mode in ("baseline", "candidate")
            }
            b = results["baseline"]
            c = results["candidate"]
            rows.append({
                "sample_rate": sr,
                "case": case,
                "baseline_peak_gr_db": b["peak_gr_db"],
                "candidate_peak_gr_db": c["peak_gr_db"],
                "delta_peak_gr_db": c["peak_gr_db"] - b["peak_gr_db"],
                "baseline_active_mean_gr_db": b["active_mean_gr_db"],
                "candidate_active_mean_gr_db": c["active_mean_gr_db"],
                "delta_active_mean_gr_db": c["active_mean_gr_db"] - b["active_mean_gr_db"],
                "baseline_max_detector_db": b["max_detector_db"],
                "candidate_max_detector_db": c["max_detector_db"],
                "all_finite": b["finite"] and c["finite"],
            })

    by_case = {}
    for case in cases:
        cr = [r for r in rows if r["case"] == case]
        by_case[case] = {
            "baseline_peak_gr_mean_db": sum(r["baseline_peak_gr_db"] for r in cr) / len(cr),
            "candidate_peak_gr_mean_db": sum(r["candidate_peak_gr_db"] for r in cr) / len(cr),
            "delta_peak_gr_max_db": max(r["delta_peak_gr_db"] for r in cr),
            "delta_peak_gr_min_db": min(r["delta_peak_gr_db"] for r in cr),
            "candidate_peak_gr_sr_spread_db": max(r["candidate_peak_gr_db"] for r in cr) - min(r["candidate_peak_gr_db"] for r in cr),
            "candidate_active_mean_sr_spread_db": max(r["candidate_active_mean_gr_db"] for r in cr) - min(r["candidate_active_mean_gr_db"] for r in cr),
        }

    finite = all(r["all_finite"] for r in rows)
    body_delta = max(abs(r["delta_active_mean_gr_db"]) for r in rows if r["case"] == "sustained_body")
    transient_over = max(r["delta_peak_gr_db"] for r in rows if r["case"] in ("transient_10ms", "transient_30ms"))
    event_over = max(r["delta_peak_gr_db"] for r in rows if r["case"] in ("plosive_low", "sibilant_high", "breath_noise"))
    body_plus_min_ratio = min(
        r["candidate_peak_gr_db"] / max(r["baseline_peak_gr_db"], 1.0e-9)
        for r in rows if r["case"] == "body_plus_transient"
    )
    sr_spread = max(v["candidate_peak_gr_sr_spread_db"] for v in by_case.values())

    acceptance = {
        "finite": finite,
        "sustained_body_mean_delta_le_0_25db": body_delta <= 0.25,
        "short_transient_extra_peak_gr_le_0_25db": transient_over <= 0.25,
        "event_extra_peak_gr_le_0_50db": event_over <= 0.50,
        "body_plus_transient_peak_retention_ge_50pct": body_plus_min_ratio >= 0.50,
        "candidate_peak_gr_sample_rate_spread_le_0_10db": sr_spread <= 0.10,
    }
    accepted = all(acceptance.values())

    with (out_dir / "detector_transfer_rows.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "VOPRIPRO_DETECTOR_TRANSFER_SCREEN_V1",
        "seed": SEED,
        "sample_rates": list(SAMPLE_RATES),
        "shared_conditions": {
            "sidechain_hpf_hz": HPF_HZ,
            "sidechain_hpf_q": HPF_Q,
            "rms_tau_ms": RMS_TAU_S * 1000.0,
            "ratio": RATIO,
            "knee_db": KNEE_DB,
            "calibration_gr_db": CAL_GR_DB,
            "max_gr_db": MAX_GR_DB,
            "attack_ms": ATTACK_S * 1000.0,
            "release_ms": RELEASE_S * 1000.0,
        },
        "baseline": "VoPriPro Natural50 35/65 instantaneous-peak + 25 ms RMS amplitude blend",
        "candidate": "Vo.Prep-derived max(25 ms RMS, instantaneous peak - 6 dB) fusion",
        "reference_calibration": refs,
        "by_case": by_case,
        "aggregate_metrics": {
            "all_finite": finite,
            "sustained_body_max_abs_active_mean_delta_db": body_delta,
            "short_transient_max_extra_peak_gr_db": transient_over,
            "problem_event_max_extra_peak_gr_db": event_over,
            "body_plus_transient_min_peak_gr_ratio": body_plus_min_ratio,
            "candidate_max_peak_gr_sample_rate_spread_db": sr_spread,
        },
        "acceptance": acceptance,
        "acceptance_met": accepted,
        "interpretation": (
            "Passing is only an eligibility screen for real-vocal comparison. "
            "It does not prove perceptual superiority or authorize product integration."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report = [
        "# VoPriPro Detector Transfer Screen v1",
        "",
        f"Decision: **{'ELIGIBLE_FOR_REAL_VOCAL' if accepted else 'REJECT_TRANSFER_V1'}**",
        "",
        "Baseline: current VoPriPro Natural50 detector.",
        "Candidate: Vo.Prep-derived Slow RMS / Fast Peak -6 dB max fusion.",
        "All other gain-computer and ballistics conditions are held equal for this screen.",
        "",
        "## Aggregate metrics",
    ]
    for key, value in summary["aggregate_metrics"].items():
        report.append(f"- {key}: {value}")
    report += ["", "## Gates"]
    for key, value in acceptance.items():
        report.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    report += [
        "",
        "This synthetic screen is deliberately conservative. "
        "Passing means only that the detector transfer is worth a same-corpus real-vocal study.",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
