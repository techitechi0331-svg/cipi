"""CIPI Vocal Resonance v0.4R.5 generic temporal morphology experiment.

Research-only. No production suppressor DSP and no raw audio persistence.

Question:
Can generic candidate temporal morphology reduce clean-vocal false triggers
without hurting injected-resonance ranking?

The tested feature family is technique-agnostic and F0-agnostic:
- longest continuous active run;
- active-run fragmentation;
- median active-run duration;
- temporal entropy;
- top-10% temporal concentration.

Baselines:
- simple local prominence;
- unchanged v0.4R.2-style static safe-negative ranker.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent

R3_PATH = HERE / "motion_coherence_ranker.py"
spec = importlib.util.spec_from_file_location("r3_temporal_base", R3_PATH)
r3 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r3)

REAUDIT_PATH = HERE / "clean_negative_reaudit.py"
spec2 = importlib.util.spec_from_file_location("r4b_reaudit", REAUDIT_PATH)
reaudit = importlib.util.module_from_spec(spec2)
assert spec2.loader is not None
spec2.loader.exec_module(reaudit)

STATIC_FEATURES = list(r3.STATIC_FEATURES)
MORPH_RAW = [
    "longest_active_run_frac",
    "active_run_count_norm",
    "median_active_run_frac",
    "temporal_entropy",
    "top10_temporal_concentration",
]
MORPH_REL = [
    "rel_longest_active_run_frac",
    "rel_active_run_count_norm",
    "rel_median_active_run_frac",
    "rel_temporal_entropy",
    "rel_top10_temporal_concentration",
]
MORPH_FEATURES = STATIC_FEATURES + MORPH_REL


def _run_lengths(active: np.ndarray) -> list[int]:
    runs: list[int] = []
    current = 0
    for value in active.astype(bool):
        if value:
            current += 1
        elif current:
            runs.append(current)
            current = 0
    if current:
        runs.append(current)
    return runs


def temporal_morphology(trajectory: np.ndarray) -> dict[str, float]:
    x = np.asarray(trajectory, dtype=float)
    n = max(1, len(x))
    active = x > 1.0
    runs = _run_lengths(active)
    active_count = int(np.sum(active))

    longest = (max(runs) / n) if runs else 0.0
    median_run = (float(np.median(runs)) / n) if runs else 0.0
    run_count_norm = len(runs) / max(active_count, 1)

    weights = np.maximum(x, 0.0)
    total = float(np.sum(weights))
    if total > 1e-12:
        p = weights / total
        entropy = float(-np.sum(p * np.log(p + 1e-18)) / np.log(max(2, len(p))))
        k = max(1, int(np.ceil(0.10 * len(weights))))
        concentration = float(np.sum(np.sort(weights)[-k:]) / total)
    else:
        entropy = 0.0
        concentration = 0.0

    return {
        "longest_active_run_frac": float(longest),
        "active_run_count_norm": float(run_count_norm),
        "median_active_run_frac": float(median_run),
        "temporal_entropy": float(entropy),
        "top10_temporal_concentration": float(concentration),
    }


def extract_candidates_morph(x, f0_t, f0, f0_conf):
    f, t, mag = r3.stft_db(x)
    local, centers, log_field, local_frames = r3.build_fields(f, mag)
    merged = r3.candidate_sets(f, local, centers, log_field)
    local20 = f[r3.sparse_select(f, local, 20, peaks_only=True)]

    peak_idx = r3.sparse_select(centers, log_field, 15, peaks_only=True)
    dense_idx = r3.sparse_select(centers, log_field, 35, peaks_only=False)
    log_hybrid = list(centers[peak_idx[:10]])
    for fr in centers[dense_idx]:
        if all(abs(fr-old) >= max(55, 0.018*max(fr,old)) for old in log_hybrid):
            log_hybrid.append(float(fr))
        if len(log_hybrid) >= 20:
            break
    log_hybrid = np.asarray(log_hybrid[:20])

    rows = []
    for rank, freq in enumerate(merged[:20], 1):
        idx = int(np.argmin(np.abs(f-freq)))
        trajectory = local_frames[:, idx]
        width = r3.contiguous_width(f, local, idx)
        la = r3.nearest_agreement(freq, local20)
        ga = r3.nearest_agreement(freq, log_hybrid)

        valid = np.isfinite(f0) & (f0_conf >= 0.18)
        if np.any(valid):
            vals = f0[valid]
            h = np.maximum(1.0, np.round(freq/vals))
            nearest = h*vals
            norm = np.clip(np.abs(freq-nearest)/(0.5*vals+1e-9), 0, 1)
            harmonic_closeness = 1.0 - float(np.median(norm))
            f0c = float(np.mean(f0_conf[valid]))
            f0med = float(np.median(vals))
        else:
            harmonic_closeness = 0.0
            f0c = 0.0
            f0med = np.nan

        row = {
            "candidate_rank": rank,
            "candidate_hz": float(freq),
            "local_score": float(local[idx]),
            "log_score": float(np.interp(freq, centers, log_field)),
            "local_persistence": float(np.mean(trajectory > 1.0)),
            "local_q80": float(np.quantile(trajectory, 0.80)),
            "local_variability": float(np.std(trajectory)),
            "local_width_hz": width,
            "local_agreement": la,
            "log_agreement": ga,
            "cross_agreement": la*ga,
            "harmonic_closeness": harmonic_closeness,
            "f0_confidence": f0c,
            "case_f0_median": f0med,
        }
        row.update(temporal_morphology(trajectory))
        rows.append(row)
    return rows, f, mag


def add_morph_relative(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    group = frame.groupby("case_id", sort=False)
    for src, dst in zip(MORPH_RAW, MORPH_REL):
        mean = group[src].transform("mean")
        std = group[src].transform("std").fillna(0.0)
        std = std.where(std > 1e-6, 1.0)
        frame[dst] = (frame[src] - mean) / std
    return frame


def build_ranker_frame(seed: int) -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_morph
    frame = r3.build_dataset(seed, 2)
    frame = r3.add_relative(frame)
    return add_morph_relative(frame)


def external_clean_frame() -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_morph
    # Keep the same independent, Audit-001-excluded multi-family selection
    # used by Re-audit-002.
    examples, _, _ = reaudit.collect_examples(10, 5000)
    rows = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = extract_candidates_morph(x, f0_t, f0, f0_conf)
        case_id = f'external:{ex["singer"]}:{ex["source_basename"]}'
        for c in candidates:
            row = dict(c)
            row.update({
                "split": "external_clean",
                "singer": ex["singer"],
                "label_name": ex["label_name"],
                "exercise_family": ex["exercise_family"],
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
    return add_morph_relative(frame)


def fit_eval(frame: pd.DataFrame, features: list[str], score_name: str):
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    pipe, cval, valid_metrics, _ = r3.fit_ranker(train, valid, features)
    valid[score_name] = pipe.predict_proba(valid[features])[:, 1]
    test[score_name] = pipe.predict_proba(test[features])[:, 1]

    threshold = r3.choose_threshold(valid, score_name)
    test_metrics = r3.rank_metrics(test, score_name)
    test_metrics["clean_false_trigger"] = r3.clean_false(test, score_name, threshold)
    test_metrics["threshold_from_valid_95pct"] = threshold

    model = pipe.named_steps["model"]
    coefficients = pd.DataFrame({
        "feature": features,
        "coefficient": model.coef_[0],
        "model": score_name,
    })
    return pipe, cval, valid_metrics, test_metrics, threshold, coefficients


def external_clean_metrics(
    frame: pd.DataFrame,
    pipe,
    features: list[str],
    score_name: str,
    threshold: float,
):
    work = frame.copy()
    work[score_name] = pipe.predict_proba(work[features])[:, 1]
    cases = (
        work.groupby("case_id")
        .agg(
            max_score=(score_name, "max"),
            label_name=("label_name", "first"),
            singer=("singer", "first"),
            exercise_family=("exercise_family", "first"),
        )
        .reset_index()
    )
    cases["false_trigger"] = (cases.max_score > threshold).astype(int)

    def grouped(key: str):
        out = []
        for value, g in cases.groupby(key):
            out.append({
                key: str(value),
                "n": int(len(g)),
                "false_trigger_rate": float(g.false_trigger.mean()),
                "mean_max_score": float(g.max_score.mean()),
            })
        return pd.DataFrame(out)

    return {
        "overall_false_trigger": float(cases.false_trigger.mean()),
        "n_cases": int(len(cases)),
        "cases": cases,
        "by_technique": grouped("label_name"),
        "by_singer": grouped("singer"),
        "by_exercise_family": grouped("exercise_family"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seed", type=int, default=20261003)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    frame = build_ranker_frame(args.seed)
    external = external_clean_frame()

    (
        static_pipe, static_c, static_valid, static_test,
        static_threshold, static_coef
    ) = fit_eval(frame, STATIC_FEATURES, "static_score")

    (
        morph_pipe, morph_c, morph_valid, morph_test,
        morph_threshold, morph_coef
    ) = fit_eval(frame, MORPH_FEATURES, "morph_score")

    ext_static = external_clean_metrics(
        external, static_pipe, STATIC_FEATURES, "static_score", static_threshold
    )
    ext_morph = external_clean_metrics(
        external, morph_pipe, MORPH_FEATURES, "morph_score", morph_threshold
    )

    test = frame[frame.split == "test"].copy()
    test["prominence_score"] = test["local_score"]
    prom_test = r3.rank_metrics(test, "prominence_score")
    valid = frame[frame.split == "valid"].copy()
    prom_threshold = r3.choose_threshold(valid, "local_score")
    prom_test["clean_false_trigger"] = r3.clean_false(
        test, "local_score", prom_threshold
    )

    ext_prom_cases = (
        external.groupby("case_id")
        .agg(
            max_score=("local_score", "max"),
            label_name=("label_name", "first"),
        )
        .reset_index()
    )
    ext_prom_cases["false_trigger"] = (
        ext_prom_cases.max_score > prom_threshold
    ).astype(int)
    ext_prom_fpr = float(ext_prom_cases.false_trigger.mean())

    static_strong = static_test["top5_effect_gte3"] or 0.0
    morph_strong = morph_test["top5_effect_gte3"] or 0.0

    retention = (
        morph_test["top5"] >= static_test["top5"]
        and morph_strong >= static_strong
        and ext_morph["overall_false_trigger"]
            <= ext_static["overall_false_trigger"] - 0.10
    )

    product_gate = (
        morph_test["top5"] >= 0.85
        and morph_strong >= 0.92
        and ext_morph["overall_false_trigger"] <= 0.15
    )

    summary = {
        "experiment": "VOCAL_RESONANCE_R5_TEMPORAL_MORPHOLOGY",
        "seed": args.seed,
        "candidate_budget": 20,
        "models": {
            "prominence": {
                "test": prom_test,
                "external_clean_false_trigger": ext_prom_fpr,
            },
            "static_r2_style": {
                "C": static_c,
                "validation": static_valid,
                "test": static_test,
                "external_clean_false_trigger": ext_static["overall_false_trigger"],
                "external_clean_n": ext_static["n_cases"],
            },
            "temporal_morphology_r5": {
                "C": morph_c,
                "validation": morph_valid,
                "test": morph_test,
                "external_clean_false_trigger": ext_morph["overall_false_trigger"],
                "external_clean_n": ext_morph["n_cases"],
            },
        },
        "retention_gate": {
            "accepted": bool(retention),
            "criteria": {
                "top5_not_worse": bool(morph_test["top5"] >= static_test["top5"]),
                "strong_top5_not_worse": bool(morph_strong >= static_strong),
                "external_clean_fpr_improves_by_0_10": bool(
                    ext_morph["overall_false_trigger"]
                    <= ext_static["overall_false_trigger"] - 0.10
                ),
            },
            "meaning": (
                "Whether generic temporal morphology is worth retaining for further "
                "semantic-ranker research; not a product promotion."
            ),
        },
        "product_gate": {
            "passed": bool(product_gate),
            "criteria": {
                "top5": 0.85,
                "strong_top5": 0.92,
                "external_clean_false_trigger_max": 0.15,
            },
        },
        "raw_audio_persisted": False,
    }

    comparison = []
    for name, block in summary["models"].items():
        row = {"model": name}
        for key, value in block.get("test", {}).items():
            if isinstance(value, (int, float, np.integer, np.floating)) or value is None:
                row[key] = value
        row["external_clean_false_trigger"] = block["external_clean_false_trigger"]
        comparison.append(row)
    pd.DataFrame(comparison).to_csv(out/"comparison.csv", index=False)

    pd.concat([static_coef, morph_coef], ignore_index=True).to_csv(
        out/"coefficients.csv", index=False
    )

    ext_static["by_technique"].assign(model="static_r2_style").to_csv(
        out/"external_clean_static_by_technique.csv", index=False
    )
    ext_morph["by_technique"].assign(model="temporal_morphology_r5").to_csv(
        out/"external_clean_morph_by_technique.csv", index=False
    )
    ext_static["cases"].assign(model="static_r2_style").to_csv(
        out/"external_clean_static_cases.csv", index=False
    )
    ext_morph["cases"].assign(model="temporal_morphology_r5").to_csv(
        out/"external_clean_morph_cases.csv", index=False
    )

    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
