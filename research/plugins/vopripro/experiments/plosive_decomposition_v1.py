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

VARIANTS = {
    "dry": (0.0, 0.0, 0.0),
    "plosive_only": (0.5, 0.0, 0.0),
    "macro_only": (0.0, 0.5, 0.0),
    "plosive_macro": (0.5, 0.5, 0.0),
}


def process_variant(sr: int, samples: list[float], amounts: tuple[float, float, float]):
    plosive, macro, sibilance = amounts
    if amounts == (0.0, 0.0, 0.0):
        prepped = list(samples)
        traces = {
            "plosive_reduction_db": [0.0] * len(samples),
            "plosive_probability": [0.0] * len(samples),
            "macro_gain_db": [0.0] * len(samples),
            "sibilance_reduction_db": [0.0] * len(samples),
            "sibilance_probability": [0.0] * len(samples),
        }
    else:
        vp = VoPrepMono(sr, plosive, macro, sibilance)
        prepped, traces = vp.process(samples)

    vpp = VoPriProNatural50Mono(sr)
    _, gr = vpp.process(prepped)
    return prepped, traces, gr


def mean(values: list[float]) -> float:
    return sum(values) / max(1, len(values))


def run_sr(sr: int) -> list[dict]:
    source, meta = make_case("plosive_on_body", sr)
    event_a, event_b = meta["event"]
    pre_a, pre_b = 0.45, 0.70
    post_a, post_b = min(4.0, event_b + 0.20), min(4.0, event_b + 0.60)

    processed = {}
    for name, amounts in VARIANTS.items():
        processed[name] = process_variant(sr, source, amounts)

    dry_audio, _, dry_gr = processed["dry"]
    event_dry_rms = rms_db(segment(dry_audio, sr, event_a, event_b))
    pre_dry_rms = rms_db(segment(dry_audio, sr, pre_a, pre_b))
    post_dry_rms = rms_db(segment(dry_audio, sr, post_a, post_b))
    event_dry_peak_gr = max(segment(dry_gr, sr, event_a, event_b))
    post_dry_mean_gr = mean(segment(dry_gr, sr, post_a, post_b))

    rows = []
    for name in VARIANTS:
        audio, traces, gr = processed[name]
        event_rms = rms_db(segment(audio, sr, event_a, event_b))
        pre_rms = rms_db(segment(audio, sr, pre_a, pre_b))
        post_rms = rms_db(segment(audio, sr, post_a, post_b))
        event_peak_gr = max(segment(gr, sr, event_a, event_b))
        post_mean_gr = mean(segment(gr, sr, post_a, post_b))
        rows.append({
            "sample_rate": sr,
            "variant": name,
            "all_finite": all(math.isfinite(x) for x in audio + gr),
            "plosive_max_probability": max(traces["plosive_probability"]),
            "plosive_max_reduction_db": max(traces["plosive_reduction_db"]),
            "macro_max_abs_gain_db": max(abs(x) for x in traces["macro_gain_db"]),
            "event_audio_rms_attenuation_db": event_dry_rms - event_rms,
            "pre_event_audio_rms_delta_db": pre_rms - pre_dry_rms,
            "post_event_audio_rms_delta_db": post_rms - post_dry_rms,
            "event_vopripro_peak_gr_improvement_db": event_dry_peak_gr - event_peak_gr,
            "post_event_vopripro_mean_gr_delta_db": post_mean_gr - post_dry_mean_gr,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = [row for sr in SAMPLE_RATES for row in run_sr(sr)]

    def variant(name: str):
        return [r for r in rows if r["variant"] == name]

    po = variant("plosive_only")
    mo = variant("macro_only")
    pm = variant("plosive_macro")

    full_shift_abs = [abs(r["post_event_vopripro_mean_gr_delta_db"]) for r in pm]
    macro_shift_abs = [abs(r["post_event_vopripro_mean_gr_delta_db"]) for r in mo]
    plosive_shift_abs = [abs(r["post_event_vopripro_mean_gr_delta_db"]) for r in po]

    macro_fraction = [
        m / max(f, 1.0e-9)
        for m, f in zip(macro_shift_abs, full_shift_abs)
    ]
    additive_residual = [
        abs(
            pm_i["post_event_vopripro_mean_gr_delta_db"]
            - (
                po_i["post_event_vopripro_mean_gr_delta_db"]
                + mo_i["post_event_vopripro_mean_gr_delta_db"]
            )
        )
        for po_i, mo_i, pm_i in zip(po, mo, pm)
    ]

    metrics = {
        "all_finite": all(r["all_finite"] for r in rows),
        "plosive_only_min_probability": min(r["plosive_max_probability"] for r in po),
        "plosive_only_min_reduction_db": min(r["plosive_max_reduction_db"] for r in po),
        "plosive_only_min_event_audio_rms_attenuation_db": min(r["event_audio_rms_attenuation_db"] for r in po),
        "plosive_only_max_abs_event_vopripro_peak_gr_change_db": max(abs(r["event_vopripro_peak_gr_improvement_db"]) for r in po),
        "plosive_only_max_abs_post_event_vopripro_mean_gr_delta_db": max(plosive_shift_abs),
        "plosive_only_max_abs_pre_event_audio_rms_delta_db": max(abs(r["pre_event_audio_rms_delta_db"]) for r in po),
        "macro_only_min_abs_post_event_vopripro_mean_gr_delta_db": min(macro_shift_abs),
        "macro_only_min_abs_macro_gain_db": min(r["macro_max_abs_gain_db"] for r in mo),
        "plosive_macro_min_macro_residual_fraction": min(macro_fraction),
        "plosive_macro_max_additive_residual_db": max(additive_residual),
        "plosive_macro_post_event_shift_sr_spread_db": max(
            r["post_event_vopripro_mean_gr_delta_db"] for r in pm
        ) - min(r["post_event_vopripro_mean_gr_delta_db"] for r in pm),
    }

    acceptance = {
        "all_finite": metrics["all_finite"],
        "plosive_positive_control_probability_ge_0_80": metrics["plosive_only_min_probability"] >= 0.80,
        "plosive_guard_reduction_ge_0_50db": metrics["plosive_only_min_reduction_db"] >= 0.50,
        "plosive_event_audio_attenuation_ge_0_25db": metrics["plosive_only_min_event_audio_rms_attenuation_db"] >= 0.25,
        "plosive_only_event_vopripro_gr_change_le_0_10db": metrics["plosive_only_max_abs_event_vopripro_peak_gr_change_db"] <= 0.10,
        "plosive_only_post_event_gr_shift_le_0_15db": metrics["plosive_only_max_abs_post_event_vopripro_mean_gr_delta_db"] <= 0.15,
        "plosive_only_pre_event_audio_delta_le_0_10db": metrics["plosive_only_max_abs_pre_event_audio_rms_delta_db"] <= 0.10,
        "macro_only_post_event_gr_shift_ge_0_25db": metrics["macro_only_min_abs_post_event_vopripro_mean_gr_delta_db"] >= 0.25,
        "macro_engages_ge_0_50db": metrics["macro_only_min_abs_macro_gain_db"] >= 0.50,
        "macro_accounts_for_ge_75pct_of_combined_shift": metrics["plosive_macro_min_macro_residual_fraction"] >= 0.75,
        "decomposition_additive_residual_le_0_10db": metrics["plosive_macro_max_additive_residual_db"] <= 0.10,
        "combined_post_event_shift_sr_spread_le_0_05db": abs(metrics["plosive_macro_post_event_shift_sr_spread_db"]) <= 0.05,
    }
    accepted = all(acceptance.values())

    with (out / "decomposition_rows.csv").open("w", encoding="utf-8", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "VOPRIPRO_VOPREP_PLOSIVE_DECOMPOSITION_V1",
        "sample_rates": list(SAMPLE_RATES),
        "source_product_refs": {
            "voprep_main": "ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6",
            "vopripro_main": "58049696815fcc24067870edd6a1b89c3cfd2163",
        },
        "scope": (
            "Diagnostic source-code-translation decomposition of the v2 plosive case: "
            "dry vs Plosive-only vs Macro-only vs Plosive+Macro feeding VoPriPro Natural50. "
            "This does not alter product DSP or establish perceptual superiority."
        ),
        "aggregate_metrics": metrics,
        "acceptance": acceptance,
        "acceptance_met": accepted,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report = [
        "# VoPriPro / Vo.Prep Plosive Decomposition v1",
        "",
        f"Decision: **{'MACRO_CONFOUNDER_SUPPORTED' if accepted else 'HYPOTHESIS_NOT_CONFIRMED'}**",
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
        "Passing supports only the diagnostic claim that the v2 post-event residual is "
        "primarily associated with Macro Level while Plosive Guard remains localized "
        "and near-neutral to VoPriPro GR on this source-derived stress case.",
    ]
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
