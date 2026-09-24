"""CIPI Vocal Resonance v0.4R.4b independent clean-negative re-audit.

Research-only diagnostic. No product DSP and no new ranker family.

Goals:
1. replicate/attack the technique-concentration finding on excerpts disjoint from
   R4-CLEAN-AUDIT-001 and across more than one exercise family;
2. replace the previous high-pitch bin with a conservative YIN-style pitch proxy;
3. report disagreement against the legacy ACF proxy instead of silently trusting
   either frontend.

Raw VocalSet audio is streamed and decoded in runner memory only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from datasets import Audio, load_dataset
from scipy import signal

HERE = Path(__file__).resolve().parent
AUDIT1_PATH = HERE / "clean_negative_audit.py"
spec = importlib.util.spec_from_file_location("audit1", AUDIT1_PATH)
audit1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit1)

r3 = audit1.r3
FS = r3.FS
DATASET = r3.DATASET
TEST_SINGERS = set(r3.TEST_SINGERS)
PREVIOUS_AUDIT = (
    HERE.parent.parent
    / "runs"
    / "VOCAL-RESONANCE-R4-CLEAN-AUDIT-001"
    / "gha-36070450907-1"
    / "audit_cases.csv"
)


def exercise_family(name: str) -> str:
    s = name.lower()
    if "arpeggio" in s:
        return "arpeggio"
    if "scale" in s:
        return "scale"
    if "long" in s and "tone" in s:
        return "long_tone"
    if "excerpt" in s:
        return "excerpt"
    return "other"


def prior_basenames() -> set[str]:
    if not PREVIOUS_AUDIT.is_file():
        return set()
    frame = pd.read_csv(PREVIOUS_AUDIT)
    if "source_basename" not in frame:
        return set()
    return set(frame.source_basename.astype(str))


def collect_examples(max_per_singer: int, scan_limit: int):
    excluded = prior_basenames()
    ds = load_dataset(DATASET, split="train", streaming=True)
    ds = ds.cast_column("audio", Audio(decode=False))
    label_feature = ds.features.get("label") if getattr(ds, "features", None) else None

    selected = []
    per_singer = defaultdict(int)
    per_singer_family = defaultdict(int)
    per_singer_label = defaultdict(int)
    per_pair = defaultdict(int)

    for idx, row in enumerate(ds):
        if idx >= scan_limit:
            break
        cell = row.get("audio")
        if not isinstance(cell, dict):
            continue
        source_path = str(cell.get("path") or "")
        basename = Path(source_path).name
        if basename in excluded:
            continue

        singer = r3.singer_id_from_path(source_path)
        if singer not in TEST_SINGERS:
            continue
        if per_singer[singer] >= max_per_singer:
            if all(per_singer[s] >= max_per_singer for s in TEST_SINGERS):
                break
            continue

        label_value = row.get("label", "unknown")
        label_name = audit1.label_to_name(label_feature, label_value)
        family = exercise_family(basename)

        if per_singer_family[(singer, family)] >= 4:
            continue
        if per_singer_label[(singer, label_name)] >= 2:
            continue
        if per_pair[(singer, family, label_name)] >= 1:
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
            "exercise_family": family,
            "source_basename": basename,
            "audio": x,
        })
        per_singer[singer] += 1
        per_singer_family[(singer, family)] += 1
        per_singer_label[(singer, label_name)] += 1
        per_pair[(singer, family, label_name)] += 1

    mapping = {}
    for ex in selected:
        mapping[ex["label_value"]] = ex["label_name"]
    return selected, mapping, excluded


def yin_proxy_track(x: np.ndarray):
    """Conservative YIN-style CMNDF proxy, without extra dependencies."""
    frame = int(0.080 * FS)
    hop = int(0.020 * FS)
    min_lag = max(2, int(FS / 1100.0))
    max_lag = min(frame - 2, int(FS / 70.0))
    window = np.hanning(frame)

    values = []
    confidence = []
    for start in range(0, max(1, len(x)-frame+1), hop):
        seg = np.asarray(x[start:start+frame], dtype=float)
        if len(seg) < frame:
            break
        seg = (seg - np.mean(seg)) * window
        rms = float(np.sqrt(np.mean(seg*seg) + 1e-18))
        if rms < 1e-4:
            values.append(np.nan)
            confidence.append(0.0)
            continue

        ac = signal.correlate(seg, seg, mode="full", method="fft")[frame-1:]
        sq = seg*seg
        prefix = np.concatenate(([0.0], np.cumsum(sq)))
        tau = np.arange(max_lag+1)
        d = prefix[frame-tau] + (prefix[frame] - prefix[tau]) - 2.0*ac[:max_lag+1]
        d = np.maximum(d, 0.0)

        cmnd = np.ones(max_lag+1, dtype=float)
        cumulative = np.cumsum(d[1:])
        cmnd[1:] = d[1:] * np.arange(1, max_lag+1) / (cumulative + 1e-18)
        region = cmnd[min_lag:max_lag+1]

        below = np.flatnonzero(region < 0.15)
        if len(below):
            idx = int(below[0] + min_lag)
            while idx + 1 <= max_lag and cmnd[idx+1] < cmnd[idx]:
                idx += 1
        else:
            idx = int(np.argmin(region) + min_lag)

        lag = float(idx)
        if 1 <= idx < max_lag:
            ym, y0, yp = cmnd[idx-1], cmnd[idx], cmnd[idx+1]
            denom = ym - 2.0*y0 + yp
            if abs(denom) > 1e-12:
                lag += float(np.clip(0.5*(ym-yp)/denom, -0.5, 0.5))

        conf = float(np.clip(1.0-cmnd[idx], 0.0, 1.0))
        values.append(FS/lag if conf >= 0.75 else np.nan)
        confidence.append(conf)

    return np.asarray(values), np.asarray(confidence)


def pitch_stats(x: np.ndarray):
    _, old_f0, old_conf = r3.estimate_f0_track(x)
    old_valid = np.isfinite(old_f0) & (old_conf >= 0.18)
    old_vals = old_f0[old_valid]

    yin_f0, yin_conf = yin_proxy_track(x)
    yin_valid = np.isfinite(yin_f0) & (yin_conf >= 0.75)
    yin_vals = yin_f0[yin_valid]

    n = min(len(old_f0), len(yin_f0))
    both = (
        np.isfinite(old_f0[:n]) & (old_conf[:n] >= 0.18)
        & np.isfinite(yin_f0[:n]) & (yin_conf[:n] >= 0.75)
    )
    if np.any(both):
        cents = 1200.0*np.abs(np.log2(yin_f0[:n][both] / old_f0[:n][both]))
        disagreement = float(np.mean(cents > 300.0))
        median_cents = float(np.median(cents))
    else:
        disagreement = np.nan
        median_cents = np.nan

    def q(vals, p):
        return float(np.quantile(vals, p)) if len(vals) else np.nan

    return {
        "old_f0_p90": q(old_vals, 0.90),
        "old_f0_p95": q(old_vals, 0.95),
        "old_voiced_fraction": float(np.mean(old_valid)) if len(old_valid) else 0.0,
        "yin_f0_median": q(yin_vals, 0.50),
        "yin_f0_p75": q(yin_vals, 0.75),
        "yin_f0_p90": q(yin_vals, 0.90),
        "yin_f0_p95": q(yin_vals, 0.95),
        "yin_reliable_fraction": float(np.mean(yin_valid)) if len(yin_valid) else 0.0,
        "acf_yin_disagreement_gt300c": disagreement,
        "acf_yin_median_abs_cents": median_cents,
    }


def candidate_rows(examples):
    rows = []
    case_meta = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = r3.extract_candidates(x, f0_t, f0, f0_conf)
        case_id = f'reaudit:{ex["singer"]}:{ex["source_basename"]}'
        stats = pitch_stats(x)
        case_meta.append({
            "case_id": case_id,
            "singer": ex["singer"],
            "label_value": ex["label_value"],
            "label_name": ex["label_name"],
            "exercise_family": ex["exercise_family"],
            "source_basename": ex["source_basename"],
            **stats,
        })
        for c in candidates:
            row = dict(c)
            row.update({
                "split": "reaudit",
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
    return r3.add_relative(pd.DataFrame(rows)), pd.DataFrame(case_meta)


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
    ap.add_argument("--max-per-singer", type=int, default=10)
    ap.add_argument("--scan-limit", type=int, default=5000)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    pipe, threshold, selected_c, valid_metrics = audit1.fit_static_reference(20260930)

    examples, label_mapping, excluded = collect_examples(
        args.max_per_singer, args.scan_limit
    )
    if not examples:
        raise RuntimeError("No independent re-audit examples selected.")

    cand, meta = candidate_rows(examples)
    cand["static_score"] = pipe.predict_proba(cand[r3.STATIC_FEATURES])[:, 1]
    maxima = cand.groupby("case_id").agg(max_score=("static_score", "max")).reset_index()
    cases = meta.merge(maxima, on="case_id", how="left")
    cases["false_trigger"] = (cases.max_score > threshold).astype(int)

    def pitch_bin(row):
        if row.yin_reliable_fraction < 0.35 or not np.isfinite(row.yin_f0_p90):
            return "yin_unresolved"
        if row.yin_f0_p90 >= 400.0:
            return "yin_p90_ge_400"
        if row.yin_f0_p90 >= 300.0:
            return "yin_p90_300_400"
        return "yin_p90_lt_300"

    cases["pitch_bin"] = cases.apply(pitch_bin, axis=1)

    by_label = group_rates(cases, "label_name")
    by_singer = group_rates(cases, "singer")
    by_pitch = group_rates(cases, "pitch_bin")
    by_family = group_rates(cases, "exercise_family")

    eligible = by_label[by_label.n >= 2]
    technique_spread = (
        float(eligible.false_trigger_rate.max()-eligible.false_trigger_rate.min())
        if len(eligible) >= 2 else 0.0
    )

    fast = cases[cases.label_name.isin(["fast_piano", "fast_forte"])]
    other = cases[~cases.label_name.isin(["fast_piano", "fast_forte"])]
    fast_rate = float(fast.false_trigger.mean()) if len(fast) else None
    other_rate = float(other.false_trigger.mean()) if len(other) else None
    fast_minus_other = None if fast_rate is None or other_rate is None else float(fast_rate-other_rate)

    high = cases[cases.pitch_bin == "yin_p90_ge_400"]
    unresolved = cases[cases.pitch_bin == "yin_unresolved"]
    old_p90_saturated = int(np.sum(cases.old_f0_p90 >= 900.0))
    old_p95_saturated = int(np.sum(cases.old_f0_p95 >= 900.0))

    disagreement_values = cases.acf_yin_disagreement_gt300c.to_numpy(dtype=float)
    disagreement_values = disagreement_values[np.isfinite(disagreement_values)]

    audit_sufficient = (
        len(cases) >= 24
        and cases.label_name.nunique() >= 4
        and cases.exercise_family.nunique() >= 2
        and int(np.sum(cases.yin_reliable_fraction >= 0.35)) >= 20
        and len(high) >= 6
        and len(set(cases.source_basename) & excluded) == 0
    )

    technique_replication = (
        technique_spread >= 0.20
        and fast_minus_other is not None
        and fast_minus_other >= 0.15
    )

    summary = {
        "experiment": "VOCAL_RESONANCE_R4_CLEAN_NEGATIVE_REAUDIT",
        "dataset": DATASET,
        "reference_ranker_seed": 20260930,
        "candidate_budget": 20,
        "selected_C": selected_c,
        "validation_threshold_95pct": threshold,
        "static_validation_metrics": valid_metrics,
        "audit": {
            "n_cases": int(len(cases)),
            "n_singers": int(cases.singer.nunique()),
            "n_labels": int(cases.label_name.nunique()),
            "n_exercise_families": int(cases.exercise_family.nunique()),
            "label_mapping": label_mapping,
            "excluded_prior_basenames": int(len(excluded)),
            "prior_overlap_count": int(len(set(cases.source_basename) & excluded)),
            "overall_clean_false_trigger": float(cases.false_trigger.mean()),
            "technique_false_trigger_spread": technique_spread,
            "fast_piano_forte_false_trigger": fast_rate,
            "other_techniques_false_trigger": other_rate,
            "fast_minus_other": fast_minus_other,
            "yin_p90_ge_400_count": int(len(high)),
            "yin_p90_ge_400_false_trigger": float(high.false_trigger.mean()) if len(high) else None,
            "yin_unresolved_count": int(len(unresolved)),
            "old_acf_p90_ge900_count": old_p90_saturated,
            "old_acf_p95_ge900_count": old_p95_saturated,
            "median_acf_yin_disagreement_gt300c": float(np.median(disagreement_values)) if len(disagreement_values) else None,
        },
        "hypothesis_readout": {
            "technique_concentration_replicated": bool(technique_replication),
            "high_pitch_coverage_sufficient": bool(len(high) >= 6),
        },
        "diagnostic_gate": {
            "accepted": bool(audit_sufficient),
            "criteria": {
                "at_least_24_clean_cases": bool(len(cases) >= 24),
                "at_least_4_techniques": bool(cases.label_name.nunique() >= 4),
                "at_least_2_exercise_families": bool(cases.exercise_family.nunique() >= 2),
                "at_least_20_yin_resolved_cases": bool(int(np.sum(cases.yin_reliable_fraction >= 0.35)) >= 20),
                "at_least_6_yin_p90_ge400_cases": bool(len(high) >= 6),
                "zero_overlap_with_audit1": bool(len(set(cases.source_basename) & excluded) == 0),
            },
            "meaning": "Evidence sufficiency for deciding whether event-context research or a dedicated high-note cohort is justified. This is not a product gate.",
        },
        "raw_audio_persisted": False,
    }

    cases.to_csv(out/"audit_cases.csv", index=False)
    by_label.to_csv(out/"false_trigger_by_technique.csv", index=False)
    by_singer.to_csv(out/"false_trigger_by_singer.csv", index=False)
    by_pitch.to_csv(out/"false_trigger_by_pitch_bin.csv", index=False)
    by_family.to_csv(out/"false_trigger_by_exercise_family.csv", index=False)
    cases[[
        "case_id","old_f0_p90","old_f0_p95","yin_f0_median","yin_f0_p90","yin_f0_p95",
        "yin_reliable_fraction","acf_yin_disagreement_gt300c","acf_yin_median_abs_cents","pitch_bin"
    ]].to_csv(out/"pitch_frontend_diagnostics.csv", index=False)
    (out/"label_mapping.json").write_text(json.dumps(label_mapping, indent=2, sort_keys=True), encoding="utf-8")
    (out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
