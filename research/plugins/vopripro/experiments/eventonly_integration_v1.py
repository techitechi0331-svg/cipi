#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from voprep_integration_screen_v2 import (
    SAMPLE_RATES,
    VoPrepMono,
    VoPriProNatural50Mono,
    make_case,
    rms_db,
    segment,
)


def mean(values: list[float]) -> float:
    return sum(values) / max(1, len(values))


def run_case(name: str, sr: int) -> dict:
    dry, meta = make_case(name, sr)

    dry_vpp = VoPriProNatural50Mono(sr)
    _, dry_gr = dry_vpp.process(dry)

    event_only = VoPrepMono(sr, 0.5, 0.0, 0.5)
    prepped, traces = event_only.process(dry)

    prep_vpp = VoPriProNatural50Mono(sr)
    _, prep_gr = prep_vpp.process(prepped)

    row = {
        "case": name,
        "sample_rate": sr,
        "all_finite": all(math.isfinite(x) for x in prepped + dry_gr + prep_gr),
        "plosive_max_probability": max(traces["plosive_probability"]),
        "plosive_max_reduction_db": max(traces["plosive_reduction_db"]),
        "sibilance_max_probability": max(traces["sibilance_probability"]),
        "sibilance_max_reduction_db": max(traces["sibilance_reduction_db"]),
        "macro_max_abs_gain_db": max(abs(x) for x in traces["macro_gain_db"]),
        "dry_vopripro_peak_gr_db": max(dry_gr),
        "prepped_vopripro_peak_gr_db": max(prep_gr),
        "mean_gr_delta_db": mean(prep_gr) - mean(dry_gr),
        "event_audio_rms_attenuation_db": 0.0,
        "event_peak_gr_change_db": 0.0,
        "post_event_mean_gr_delta_db": 0.0,
        "phrase_spread_delta_db": 0.0,
    }

    if "event" in meta:
        a, b = meta["event"]
        dry_event = segment(dry, sr, a, b)
        prep_event = segment(prepped, sr, a, b)
        dry_event_gr = segment(dry_gr, sr, a, b)
        prep_event_gr = segment(prep_gr, sr, a, b)
        row["event_audio_rms_attenuation_db"] = rms_db(dry_event) - rms_db(prep_event)
        row["event_peak_gr_change_db"] = max(dry_event_gr) - max(prep_event_gr)

        pa, pb = b + 0.20, min(4.0, b + 0.60)
        row["post_event_mean_gr_delta_db"] = (
            mean(segment(prep_gr, sr, pa, pb))
            - mean(segment(dry_gr, sr, pa, pb))
        )

    if "segments" in meta:
        dry_levels = [rms_db(segment(dry, sr, a, b)) for a, b in meta["segments"]]
        prep_levels = [rms_db(segment(prepped, sr, a, b)) for a, b in meta["segments"]]
        dry_spread = max(dry_levels) - min(dry_levels)
        prep_spread = max(prep_levels) - min(prep_levels)
        row["phrase_spread_delta_db"] = prep_spread - dry_spread

    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    cases = ("neutral_body", "plosive_on_body", "sibilance_on_body", "phrase_step")
    rows = [run_case(case, sr) for sr in SAMPLE_RATES for case in cases]

    def by_case(name: str):
        return [r for r in rows if r["case"] == name]

    neutral = by_case("neutral_body")
    plosive = by_case("plosive_on_body")
    sibilance = by_case("sibilance_on_body")
    phrase = by_case("phrase_step")

    metrics = {
        "all_finite": all(r["all_finite"] for r in rows),
        "macro_disabled_max_abs_gain_db": max(r["macro_max_abs_gain_db"] for r in rows),
        "neutral_max_abs_mean_gr_delta_db": max(abs(r["mean_gr_delta_db"]) for r in neutral),
        "neutral_max_event_reduction_db": max(
            max(r["plosive_max_reduction_db"], r["sibilance_max_reduction_db"])
            for r in neutral
        ),
        "plosive_min_probability": min(r["plosive_max_probability"] for r in plosive),
        "plosive_min_reduction_db": min(r["plosive_max_reduction_db"] for r in plosive),
        "plosive_min_event_audio_rms_attenuation_db": min(r["event_audio_rms_attenuation_db"] for r in plosive),
        "plosive_max_abs_event_vopripro_peak_gr_change_db": max(abs(r["event_peak_gr_change_db"]) for r in plosive),
        "plosive_max_abs_post_event_mean_gr_delta_db": max(abs(r["post_event_mean_gr_delta_db"]) for r in plosive),
        "sibilance_min_probability": min(r["sibilance_max_probability"] for r in sibilance),
        "sibilance_min_reduction_db": min(r["sibilance_max_reduction_db"] for r in sibilance),
        "sibilance_min_event_audio_rms_attenuation_db": min(r["event_audio_rms_attenuation_db"] for r in sibilance),
        "sibilance_min_event_vopripro_peak_gr_improvement_db": min(r["event_peak_gr_change_db"] for r in sibilance),
        "sibilance_max_abs_post_event_mean_gr_delta_db": max(abs(r["post_event_mean_gr_delta_db"]) for r in sibilance),
        "phrase_max_event_reduction_db": max(
            max(r["plosive_max_reduction_db"], r["sibilance_max_reduction_db"])
            for r in phrase
        ),
        "phrase_max_abs_spread_delta_db": max(abs(r["phrase_spread_delta_db"]) for r in phrase),
        "downstream_peak_gr_sr_spread_db": max(
            max(r["prepped_vopripro_peak_gr_db"] for r in by_case(case))
            - min(r["prepped_vopripro_peak_gr_db"] for r in by_case(case))
            for case in cases
        ),
    }

    acceptance = {
        "all_finite": metrics["all_finite"],
        "macro_disabled_is_unity": metrics["macro_disabled_max_abs_gain_db"] <= 1.0e-6,
        "neutral_mean_gr_shift_le_0_10db": metrics["neutral_max_abs_mean_gr_delta_db"] <= 0.10,
        "neutral_false_event_reduction_le_0_10db": metrics["neutral_max_event_reduction_db"] <= 0.10,
        "plosive_probability_ge_0_80": metrics["plosive_min_probability"] >= 0.80,
        "plosive_reduction_ge_0_50db": metrics["plosive_min_reduction_db"] >= 0.50,
        "plosive_event_audio_attenuation_ge_0_25db": metrics["plosive_min_event_audio_rms_attenuation_db"] >= 0.25,
        "plosive_downstream_event_gr_change_le_0_10db": metrics["plosive_max_abs_event_vopripro_peak_gr_change_db"] <= 0.10,
        "plosive_post_event_gr_shift_le_0_15db": metrics["plosive_max_abs_post_event_mean_gr_delta_db"] <= 0.15,
        "sibilance_probability_ge_0_65": metrics["sibilance_min_probability"] >= 0.65,
        "sibilance_reduction_ge_0_30db": metrics["sibilance_min_reduction_db"] >= 0.30,
        "sibilance_event_audio_attenuation_ge_0_10db": metrics["sibilance_min_event_audio_rms_attenuation_db"] >= 0.10,
        "sibilance_downstream_peak_gr_improves_ge_0_02db": metrics["sibilance_min_event_vopripro_peak_gr_improvement_db"] >= 0.02,
        "sibilance_post_event_gr_shift_le_0_15db": metrics["sibilance_max_abs_post_event_mean_gr_delta_db"] <= 0.15,
        "phrase_false_event_reduction_le_0_10db": metrics["phrase_max_event_reduction_db"] <= 0.10,
        "phrase_spread_delta_le_0_10db": metrics["phrase_max_abs_spread_delta_db"] <= 0.10,
        "downstream_peak_gr_sr_spread_le_0_15db": metrics["downstream_peak_gr_sr_spread_db"] <= 0.15,
    }
    accepted = all(acceptance.values())

    with (out / "eventonly_rows.csv").open("w", encoding="utf-8", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "VOPRIPRO_VOPREP_EVENTONLY_INTEGRATION_V1",
        "sample_rates": list(SAMPLE_RATES),
        "source_product_refs": {
            "voprep_main": "ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6",
            "vopripro_main": "58049696815fcc24067870edd6a1b89c3cfd2163",
        },
        "scope": (
            "Deterministic source-code-translation compatibility screen of Vo.Prep "
            "Plosive 50% + Sibilance 50% with Macro Level OFF feeding VoPriPro Natural50. "
            "Plosive is evaluated as localized cleanup/compatibility rather than required "
            "downstream GR reduction. This is not real-vocal, VST3, listening or Cubase evidence."
        ),
        "aggregate_metrics": metrics,
        "acceptance": acceptance,
        "acceptance_met": accepted,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Vo.Prep Event-Only -> VoPriPro Integration v1",
        "",
        f"Decision: **{'ELIGIBLE_FOR_ACTUAL_INTEGRATION_VALIDATION' if accepted else 'REVISE_OR_REJECT'}**",
        "",
        "## Aggregate metrics",
    ]
    for key, value in metrics.items():
        report.append(f"- {key}: {value}")
    report += ["", "## Gates"]
    for key, value in acceptance.items():
        report.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    report += [
        "",
        "Passing supports only event-only chain compatibility on the deterministic "
        "source-derived matrix. Macro Level remains a separate overlap question.",
    ]
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
