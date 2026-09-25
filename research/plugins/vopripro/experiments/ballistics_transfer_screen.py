#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

SAMPLE_RATES = (44100, 48000, 96000, 192000)

RATIO = 2.7
KNEE_DB = 12.0
CAL_GR_DB = 3.0
MAX_GR_DB = 6.0

HPF_HZ = 80.0
HPF_Q = 0.70710678
RMS_TAU_S = 0.025
PEAK_WEIGHT = 0.35

BASELINE_ATTACK_S = 0.020
BASELINE_RELEASE_S = 0.110

CANDIDATE_ATTACK_S = 0.008
CANDIDATE_RELEASE_S = 0.070

SEED = 20260926


def db_to_gain(db: float) -> float:
    return 10.0 ** (db / 20.0)


def gain_to_db(gain: float) -> float:
    return 20.0 * math.log10(max(abs(gain), 1.0e-12))


def one_pole_coeff(seconds: float, sample_rate: float) -> float:
    return math.exp(-1.0 / (seconds * sample_rate))


class HPF:
    def __init__(self, sample_rate: float):
        w0 = 2.0 * math.pi * HPF_HZ / sample_rate
        c = math.cos(w0)
        s = math.sin(w0)
        alpha = s / (2.0 * HPF_Q)
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


class NaturalDetector:
    def __init__(self, sample_rate: float):
        self.sr = float(sample_rate)
        self.hpf = HPF(self.sr)
        self.rms_coeff = one_pole_coeff(RMS_TAU_S, self.sr)
        self.rms_power = 0.0

    def process_db(self, x: float) -> float:
        sc = self.hpf.process(x)
        peak = abs(sc)
        self.rms_power = (
            self.rms_coeff * self.rms_power
            + (1.0 - self.rms_coeff) * sc * sc
        )
        rms = math.sqrt(max(self.rms_power, 0.0))
        amp = PEAK_WEIGHT * peak + (1.0 - PEAK_WEIGHT) * rms
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


def reference_level(sample_rate: int) -> float:
    det = NaturalDetector(sample_rate)
    n = int(round(1.0 * sample_rate))
    start = int(round(0.75 * sample_rate))
    values = []
    amp = db_to_gain(-18.0)
    for i in range(n):
        t = i / sample_rate
        x = amp * math.sin(2.0 * math.pi * 220.0 * t)
        db = det.process_db(x)
        if i >= start:
            values.append(db)
    return sum(values) / len(values)


def tone_burst(sample_rate: int, duration_ms: float, level_db: float = -6.0) -> list[float]:
    pre = int(round(0.20 * sample_rate))
    post = int(round(0.60 * sample_rate))
    dur = int(round(duration_ms * 0.001 * sample_rate))
    out = [0.0] * pre
    amp = db_to_gain(level_db)
    for i in range(dur):
        t = i / sample_rate
        env = math.sin(math.pi * (i + 0.5) / max(1, dur))
        out.append(amp * env * math.sin(2.0 * math.pi * 2200.0 * t))
    out.extend([0.0] * post)
    return out


def body_onset(sample_rate: int, duration_s: float = 0.80, level_db: float = -14.0) -> list[float]:
    pre = int(round(0.20 * sample_rate))
    post = int(round(0.60 * sample_rate))
    dur = int(round(duration_s * sample_rate))
    out = [0.0] * pre
    amp = db_to_gain(level_db)
    for i in range(dur):
        t = i / sample_rate
        fade = min(1.0, (i + 1) / max(1.0, 0.005 * sample_rate))
        out.append(amp * fade * math.sin(2.0 * math.pi * 220.0 * t))
    out.extend([0.0] * post)
    return out


def repeated_phrase(sample_rate: int) -> list[float]:
    pre = int(round(0.20 * sample_rate))
    out = [0.0] * pre
    amp = db_to_gain(-14.0)
    on = int(round(0.12 * sample_rate))
    off = int(round(0.08 * sample_rate))
    for k in range(6):
        for i in range(on):
            t = (k * (on + off) + i) / sample_rate
            fade_in = min(1.0, (i + 1) / max(1.0, 0.004 * sample_rate))
            fade_out = min(1.0, (on - i) / max(1.0, 0.004 * sample_rate))
            env = min(fade_in, fade_out)
            out.append(amp * env * math.sin(2.0 * math.pi * 220.0 * t))
        out.extend([0.0] * off)
    out.extend([0.0] * int(round(0.60 * sample_rate)))
    return out


def process_case(
    sample_rate: int,
    threshold_db: float,
    attack_s: float,
    release_s: float,
    samples: list[float],
) -> dict:
    det = NaturalDetector(sample_rate)
    attack = one_pole_coeff(attack_s, sample_rate)
    release = one_pole_coeff(release_s, sample_rate)
    gr = 0.0
    trajectory = []
    desired_traj = []

    for x in samples:
        detector_db = det.process_db(x)
        desired = min(MAX_GR_DB, soft_knee_gr(detector_db, threshold_db))
        coeff = attack if desired > gr else release
        gr = coeff * gr + (1.0 - coeff) * desired
        if not math.isfinite(gr):
            raise RuntimeError("non-finite GR")
        trajectory.append(gr)
        desired_traj.append(desired)

    return {
        "trajectory": trajectory,
        "desired": desired_traj,
        "peak_gr_db": max(trajectory) if trajectory else 0.0,
        "finite": all(math.isfinite(x) for x in trajectory),
    }


def residual_after_offset(
    sample_rate: int,
    threshold_db: float,
    attack_s: float,
    release_s: float,
    observe_ms: tuple[int, ...] = (50, 100, 200, 500),
) -> dict[int, float]:
    active_dur = int(round(0.60 * sample_rate))
    silence_dur = int(round(0.70 * sample_rate))
    amp = db_to_gain(-12.0)
    samples = []
    for i in range(active_dur):
        t = i / sample_rate
        samples.append(amp * math.sin(2.0 * math.pi * 220.0 * t))
    samples.extend([0.0] * silence_dur)

    result = process_case(sample_rate, threshold_db, attack_s, release_s, samples)
    traj = result["trajectory"]
    out = {}
    for ms in observe_ms:
        idx = min(
            len(traj) - 1,
            active_dur + int(round(ms * 0.001 * sample_rate)),
        )
        out[ms] = traj[idx]
    return out


def active_window_stats(samples: list[float], trajectory: list[float]) -> tuple[float, float]:
    active = [g for x, g in zip(samples, trajectory) if abs(x) > db_to_gain(-55.0)]
    if not active:
        return 0.0, 0.0
    mean = sum(active) / len(active)
    ripple = math.sqrt(sum((x - mean) ** 2 for x in active) / len(active))
    return mean, ripple


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    case_factories = {
        "burst_10ms": lambda sr: tone_burst(sr, 10.0),
        "burst_30ms": lambda sr: tone_burst(sr, 30.0),
        "burst_100ms": lambda sr: tone_burst(sr, 100.0),
        "body_800ms": lambda sr: body_onset(sr, 0.80, -14.0),
        "repeated_phrase": repeated_phrase,
    }

    rows = []
    release_rows = []

    for sr in SAMPLE_RATES:
        ref = reference_level(sr)
        threshold = threshold_for_calibration(ref)

        for case, factory in case_factories.items():
            samples = factory(sr)
            baseline = process_case(
                sr, threshold, BASELINE_ATTACK_S, BASELINE_RELEASE_S, samples
            )
            candidate = process_case(
                sr, threshold, CANDIDATE_ATTACK_S, CANDIDATE_RELEASE_S, samples
            )

            b_mean, b_ripple = active_window_stats(samples, baseline["trajectory"])
            c_mean, c_ripple = active_window_stats(samples, candidate["trajectory"])

            rows.append({
                "sample_rate": sr,
                "case": case,
                "baseline_peak_gr_db": baseline["peak_gr_db"],
                "candidate_peak_gr_db": candidate["peak_gr_db"],
                "delta_peak_gr_db": candidate["peak_gr_db"] - baseline["peak_gr_db"],
                "baseline_active_mean_gr_db": b_mean,
                "candidate_active_mean_gr_db": c_mean,
                "delta_active_mean_gr_db": c_mean - b_mean,
                "baseline_active_ripple_db": b_ripple,
                "candidate_active_ripple_db": c_ripple,
                "delta_active_ripple_db": c_ripple - b_ripple,
                "all_finite": baseline["finite"] and candidate["finite"],
            })

        b_res = residual_after_offset(
            sr, threshold, BASELINE_ATTACK_S, BASELINE_RELEASE_S
        )
        c_res = residual_after_offset(
            sr, threshold, CANDIDATE_ATTACK_S, CANDIDATE_RELEASE_S
        )
        for ms in (50, 100, 200, 500):
            release_rows.append({
                "sample_rate": sr,
                "observe_ms": ms,
                "baseline_residual_gr_db": b_res[ms],
                "candidate_residual_gr_db": c_res[ms],
                "delta_residual_gr_db": c_res[ms] - b_res[ms],
            })

    finite = all(r["all_finite"] for r in rows)

    def case_rows(name: str):
        return [r for r in rows if r["case"] == name]

    burst10_extra = max(r["delta_peak_gr_db"] for r in case_rows("burst_10ms"))
    burst30_extra = max(r["delta_peak_gr_db"] for r in case_rows("burst_30ms"))
    burst100_gain = min(r["delta_peak_gr_db"] for r in case_rows("burst_100ms"))
    body_mean_delta = max(abs(r["delta_active_mean_gr_db"]) for r in case_rows("body_800ms"))
    repeated_ripple_extra = max(r["delta_active_ripple_db"] for r in case_rows("repeated_phrase"))
    release200_delta = max(
        r["delta_residual_gr_db"] for r in release_rows if r["observe_ms"] == 200
    )

    candidate_peak_sr_spread = 0.0
    for case in case_factories:
        cr = case_rows(case)
        spread = max(r["candidate_peak_gr_db"] for r in cr) - min(r["candidate_peak_gr_db"] for r in cr)
        candidate_peak_sr_spread = max(candidate_peak_sr_spread, spread)

    acceptance = {
        "all_finite": finite,
        "burst_10ms_extra_peak_gr_le_0_35db": burst10_extra <= 0.35,
        "burst_30ms_extra_peak_gr_le_0_50db": burst30_extra <= 0.50,
        "burst_100ms_control_gain_ge_0_25db": burst100_gain >= 0.25,
        "body_800ms_active_mean_delta_le_0_15db": body_mean_delta <= 0.15,
        "repeated_phrase_ripple_extra_le_0_10db": repeated_ripple_extra <= 0.10,
        "release_200ms_not_slower_than_baseline": release200_delta <= 0.05,
        "candidate_peak_gr_sample_rate_spread_le_0_10db": candidate_peak_sr_spread <= 0.10,
    }
    accepted = all(acceptance.values())

    with (out_dir / "ballistics_transfer_rows.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with (out_dir / "release_rows.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(release_rows[0].keys()))
        writer.writeheader()
        writer.writerows(release_rows)

    summary = {
        "experiment": "VOPRIPRO_BALLISTICS_TRANSFER_SCREEN_V1",
        "seed": SEED,
        "sample_rates": list(SAMPLE_RATES),
        "shared_conditions": {
            "detector": "current VoPriPro Natural50 35/65 Peak/RMS",
            "sidechain_hpf_hz": HPF_HZ,
            "rms_tau_ms": RMS_TAU_S * 1000.0,
            "ratio": RATIO,
            "knee_db": KNEE_DB,
            "calibration_gr_db": CAL_GR_DB,
            "max_gr_db": MAX_GR_DB,
        },
        "baseline": {
            "attack_ms": BASELINE_ATTACK_S * 1000.0,
            "release_ms": BASELINE_RELEASE_S * 1000.0,
        },
        "candidate": {
            "attack_ms": CANDIDATE_ATTACK_S * 1000.0,
            "release_ms": CANDIDATE_RELEASE_S * 1000.0,
        },
        "aggregate_metrics": {
            "all_finite": finite,
            "burst_10ms_max_extra_peak_gr_db": burst10_extra,
            "burst_30ms_max_extra_peak_gr_db": burst30_extra,
            "burst_100ms_min_extra_peak_gr_db": burst100_gain,
            "body_800ms_max_abs_active_mean_delta_db": body_mean_delta,
            "repeated_phrase_max_extra_ripple_db": repeated_ripple_extra,
            "release_200ms_max_candidate_minus_baseline_residual_db": release200_delta,
            "candidate_max_peak_gr_sample_rate_spread_db": candidate_peak_sr_spread,
        },
        "acceptance": acceptance,
        "acceptance_met": accepted,
        "interpretation": (
            "Passing authorizes only a real-vocal timing comparison. "
            "It does not establish that 8/70 ms is perceptually superior or suitable "
            "for replacing the current Character mapping."
        ),
    }

    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    report = [
        "# VoPriPro Ballistics Transfer Screen v1",
        "",
        f"Decision: **{'ELIGIBLE_FOR_REAL_VOCAL' if accepted else 'REJECT_TRANSFER_V1'}**",
        "",
        "Baseline: current Natural50 20 ms attack / 110 ms release.",
        "Candidate: Vo.Prep transparent-core 8 ms attack / 70 ms release.",
        "Detector, static curve, calibration and max-GR cap are held equal.",
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
        "Passing means only that the fixed 8/70 ms pair deserves a same-corpus "
        "real-vocal comparison; product adoption still requires level-matched listening.",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
