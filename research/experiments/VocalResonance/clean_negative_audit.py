"""CIPI Vocal Resonance v0.4R.4 clean-negative and pitch-coverage audit.

Research-only diagnostic. It adds no product DSP and trains no new model family.
Raw VocalSet audio is streamed and decoded in runner memory only.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
from datasets import Audio, load_dataset

HERE = Path(__file__).resolve().parent
R3_PATH = HERE / "motion_coherence_ranker.py"
spec = importlib.util.spec_from_file_location("r3_motion", R3_PATH)
r3 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r3)

FS = r3.FS
DATASET = r3.DATASET
TEST_SINGERS = set(r3.TEST_SINGERS)


def label_to_name(feature, value):
    try:
        if hasattr(feature, "int2str"):
            return str(feature.int2str(int(value)))
    except Exception:
        pass
    if hasattr(feature, "names"):
        try:
            return str(feature.names[int(value)])
        except Exception:
            pass
    return str(value)


def collect_audit_examples(max_per_singer: int, skip_per_singer: int, scan_limit: int):
    ds = load_dataset(DATASET, split="train", streaming=True)
    ds = ds.cast_column("audio", Audio(decode=False))
    label_feature = ds.features.get("label") if getattr(ds, "features", None) else None

    selected = []
    per_singer = defaultdict(int)
    per_singer_label = defaultdict(int)
    encountered = defaultdict(int)

    for idx, row in enumerate(ds):
        if idx >= scan_limit:
            break
        cell = row.get("audio")
        if not isinstance(cell, dict):
            continue
        source_path = str(cell.get("path") or "")
        singer = r3.singer_id_from_path(source_path)
        if singer not in TEST_SINGERS:
            continue

        if encountered[singer] < skip_per_singer:
            encountered[singer] += 1
            continue
        encountered[singer] += 1

        if per_singer[singer] >= max_per_singer:
            if all(per_singer[s] >= max_per_singer for s in TEST_SINGERS):
                break
            continue

        label_value = row.get("label", "unknown")
        label_name = label_to_name(label_feature, label_value)
        key = (singer, label_name)

        # Promote technique diversity instead of taking a long sorted block.
        if per_singer_label[key] >= 2:
            continue

        data = cell.get("bytes")
        if data is None:
            continue
        try:
            x = r3.to_mono_resampled(data)
        except Exception:
            continue
        if len(x) < FS:
            continue
        x = r3.best_energy_segment(x)
        if float(np.sqrt(np.mean(x*x)+1e-18)) < 1e-4:
            continue

        selected.append({
            "index": idx,
            "singer": singer,
            "label_value": str(label_value),
            "label_name": label_name,
            "source_basename": Path(source_path).name,
            "audio": x,
        })
        per_singer[singer] += 1
        per_singer_label[key] += 1

    mapping = {}
    for ex in selected:
        mapping[ex["label_value"]] = ex["label_name"]
    return selected, mapping


def f0_stats(x):
    _, f0, conf = r3.estimate_f0_track(x)
    valid = np.isfinite(f0) & (conf >= 0.18)
    vals = f0[valid]
    if not len(vals):
        return {
            "f0_median": np.nan,
            "f0_p75": np.nan,
            "f0_p90": np.nan,
            "f0_p95": np.nan,
            "voiced_fraction": 0.0,
        }
    return {
        "f0_median": float(np.median(vals)),
        "f0_p75": float(np.quantile(vals, 0.75)),
        "f0_p90": float(np.quantile(vals, 0.90)),
        "f0_p95": float(np.quantile(vals, 0.95)),
        "voiced_fraction": float(np.mean(valid)),
    }


def audit_candidate_rows(examples):
    rows = []
    case_meta = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = r3.extract_candidates(x, f0_t, f0, f0_conf)
        case_id = f'audit:{ex["singer"]}:{ex["source_basename"]}'
        stats = f0_stats(x)
        case_meta.append({
            "case_id": case_id,
            "singer": ex["singer"],
            "label_value": ex["label_value"],
            "label_name": ex["label_name"],
            "source_basename": ex["source_basename"],
            **stats,
        })
        for c in candidates:
            row = dict(c)
            row.update({
                "split": "audit",
                "singer": ex["singer"],
                "label_name": ex["label_name"],
                "source_name": ex["source_basename"],
                "case_id": case_id,
                "is_clean": 1,
                "target_hz": np.nan,
                "target_q": np.nan,
                "target_gain_db": np.nan,
                "physical_effect_db": np.nan,
                "is_target": 0,
                "safe_negative": 0,
                "generator_hit": 0,
            })
            rows.append(row)
    frame = r3.add_relative(pd.DataFrame(rows))
    return frame, pd.DataFrame(case_meta)


def fit_static_reference(seed: int):
    base = r3.add_relative(r3.build_dataset(seed, 2))
    train = base[base.split == "train"].copy()
    valid = base[base.split == "valid"].copy()
    pipe, selected_c, valid_metrics, _ = r3.fit_ranker(
        train, valid, r3.STATIC_FEATURES
    )
    valid["static_score"] = pipe.predict_proba(valid[r3.STATIC_FEATURES])[:, 1]
    threshold = r3.choose_threshold(valid, "static_score")
    return pipe, threshold, selected_c, valid_metrics


def group_rates(cases: pd.DataFrame, key: str):
    rows = []
    for value, g in cases.groupby(key):
        rows.append({
            key: str(value),
            "n": int(len(g)),
            "false_trigger_rate": float(g.false_trigger.mean()),
            "mean_max_score": float(g.max_score.mean()),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--skip-per-singer", type=int, default=4)
    ap.add_argument("--max-per-singer", type=int, default=8)
    ap.add_argument("--scan-limit", type=int, default=7000)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    pipe, threshold, selected_c, valid_metrics = fit_static_reference(args.seed)
    examples, label_mapping = collect_audit_examples(
        args.max_per_singer, args.skip_per_singer, args.scan_limit
    )
    if not examples:
        raise RuntimeError("No audit examples selected.")

    cand, meta = audit_candidate_rows(examples)
    cand["static_score"] = pipe.predict_proba(cand[r3.STATIC_FEATURES])[:, 1]

    maxima = (
        cand.groupby("case_id")
        .agg(max_score=("static_score", "max"))
        .reset_index()
    )
    cases = meta.merge(maxima, on="case_id", how="left")
    cases["false_trigger"] = (cases.max_score > threshold).astype(int)

    def pitch_bin(row):
        p90 = row.f0_p90
        if not np.isfinite(p90):
            return "unvoiced_or_unresolved"
        if p90 >= 400.0:
            return "p90_ge_400"
        if p90 >= 300.0:
            return "p90_300_400"
        return "p90_lt_300"

    cases["pitch_bin"] = cases.apply(pitch_bin, axis=1)

    by_label = group_rates(cases, "label_name")
    by_singer = group_rates(cases, "singer")
    by_pitch = group_rates(cases, "pitch_bin")

    eligible = by_label[by_label.n >= 2]
    technique_spread = (
        float(eligible.false_trigger_rate.max() - eligible.false_trigger_rate.min())
        if len(eligible) >= 2 else 0.0
    )

    overall = float(cases.false_trigger.mean())
    high = cases[cases.pitch_bin == "p90_ge_400"]
    high_rate = float(high.false_trigger.mean()) if len(high) else None

    names_resolved = any(
        str(k) != str(v) for k, v in label_mapping.items()
    )
    technique_concentration = technique_spread >= 0.20
    high_pitch_elevation = (
        high_rate is not None and high_rate >= overall + 0.15
    )

    audit_sufficient = (
        len(cases) >= 24
        and names_resolved
        and cases.label_name.nunique() >= 4
        and len(high) >= 6
    )

    summary = {
        "experiment": "VOCAL_RESONANCE_R4_CLEAN_NEGATIVE_AUDIT",
        "dataset": DATASET,
        "seed": args.seed,
        "skip_per_singer": args.skip_per_singer,
        "selected_C": selected_c,
        "static_validation_metrics": valid_metrics,
        "validation_threshold_95pct": threshold,
        "audit": {
            "n_cases": int(len(cases)),
            "n_singers": int(cases.singer.nunique()),
            "n_labels": int(cases.label_name.nunique()),
            "label_mapping": label_mapping,
            "label_names_resolved": bool(names_resolved),
            "overall_clean_false_trigger": overall,
            "technique_false_trigger_spread": technique_spread,
            "p90_ge_400_count": int(len(high)),
            "p90_ge_400_false_trigger": high_rate,
            "f0_p90_median_across_cases": (
                float(np.nanmedian(cases.f0_p90.to_numpy()))
                if np.any(np.isfinite(cases.f0_p90.to_numpy())) else None
            ),
        },
        "hypothesis_readout": {
            "technique_concentration_ge_0_20": bool(technique_concentration),
            "high_pitch_false_trigger_elevated_by_0_15": bool(high_pitch_elevation),
            "supported": bool(technique_concentration or high_pitch_elevation),
        },
        "diagnostic_gate": {
            "accepted": bool(audit_sufficient),
            "criteria": {
                "at_least_24_clean_cases": bool(len(cases) >= 24),
                "label_names_resolved": bool(names_resolved),
                "at_least_4_techniques": bool(cases.label_name.nunique() >= 4),
                "at_least_6_p90_ge_400_cases": bool(len(high) >= 6),
            },
            "meaning": "Sufficient adversarial clean-negative and pitch coverage to choose the next ranker research question. This is not a product gate.",
        },
        "raw_audio_persisted": False,
    }

    cases.to_csv(out / "audit_cases.csv", index=False)
    by_label.to_csv(out / "false_trigger_by_technique.csv", index=False)
    by_singer.to_csv(out / "false_trigger_by_singer.csv", index=False)
    by_pitch.to_csv(out / "false_trigger_by_pitch_bin.csv", index=False)
    (out / "label_mapping.json").write_text(
        json.dumps(label_mapping, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
