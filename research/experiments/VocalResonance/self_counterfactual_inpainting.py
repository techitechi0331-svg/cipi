"""CIPI Vocal Resonance v0.4R.11 self-counterfactual spectral inpainting.

Research only. No production suppressor DSP. No raw vocal audio persistence.

R7 showed that true paired clean/injected deltas make the causal target highly
identifiable. R8-R10 failed to recover that information with raw local patch
geometry, fixed-Hz transfer consistency, or a population normative prior.

R11 constructs a pseudo-clean reference from the SAME observation:
- remove the candidate neighborhood conceptually;
- predict the candidate center from robust left/right spectral flanks;
- perform the same reconstruction in the local-residual field;
- use observed-minus-counterfactual deltas as deployable single-view features.

No real clean reference is used by model features. Paired clean information is
used only for research diagnostics against the R7 oracle delta.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent

R8_PATH = HERE / "local_patch_proxy.py"
spec = importlib.util.spec_from_file_location("r8_cf_base", R8_PATH)
r8 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r8)

R7_PATH = HERE / "identifiability_oracle.py"
spec7 = importlib.util.spec_from_file_location("r7_cf_diag", R7_PATH)
r7 = importlib.util.module_from_spec(spec7)
assert spec7.loader is not None
spec7.loader.exec_module(r7)

r3 = r8.r3
reaudit = r8.reaudit

SEEDS = [20261003, 20261013]
SCALES = [0.02, 0.04, 0.08, 0.12]

CF_RAW = [
    "cf_delta_local_s2",
    "cf_delta_local_s4",
    "cf_delta_local_s8",
    "cf_delta_local_s12",
    "cf_delta_q80_s4",
    "cf_delta_q80_s8",
    "cf_delta_persistence_s4",
    "cf_delta_persistence_s8",
    "cf_raw_boost_q80_s4",
    "cf_raw_boost_q80_s8",
    "cf_raw_boost_gt1_s4",
    "cf_raw_boost_gt1_s8",
    "cf_log_delta_s4",
    "cf_log_delta_s8",
    "cf_scale_consistency",
    "cf_relative_suppression",
]
CF_REL = [f"rel_{x}" for x in CF_RAW]
CF_FEATURES = list(r3.STATIC_FEATURES) + CF_REL

R7_ORACLE_COND_TOP5 = {
    20261003: 1.0,
    20261013: 0.9259259259259259,
}
R7_ORACLE_STRONG_COND_TOP5 = {
    20261003: 1.0,
    20261013: 1.0,
}


def nearest_index(f: np.ndarray, hz: float) -> int:
    return int(np.argmin(np.abs(f - hz)))


def robust_flank_track(
    field: np.ndarray,
    f: np.ndarray,
    idx: int,
    frac: float,
    min_hz: float,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    fc = float(f[idx])
    offset = max(float(min_hz), float(frac) * fc)
    li = nearest_index(f, max(float(f[0]), fc - offset))
    ri = nearest_index(f, min(float(f[-1]), fc + offset))
    li = min(li, max(0, idx - 1))
    ri = max(ri, min(len(f) - 1, idx + 1))

    def local_median(center_idx: int) -> np.ndarray:
        lo = max(0, center_idx - 1)
        hi = min(len(f), center_idx + 2)
        return np.median(field[:, lo:hi], axis=1)

    left = local_median(li)
    right = local_median(ri)
    return left, right, li, ri


def reconstruct_track(
    field: np.ndarray,
    f: np.ndarray,
    idx: int,
    frac: float,
    min_hz: float,
) -> tuple[np.ndarray, int, int]:
    left, right, li, ri = robust_flank_track(
        field, f, idx, frac, min_hz
    )
    fc = float(f[idx])
    lf = float(f[li])
    rf = float(f[ri])
    if rf <= lf + 1e-9:
        pred = 0.5 * (left + right)
    else:
        w = float(np.clip((fc - lf) / (rf - lf), 0.0, 1.0))
        pred = (1.0 - w) * left + w * right
    return np.asarray(pred, dtype=float), li, ri


def counterfactual_features(
    f: np.ndarray,
    mag: np.ndarray,
    local_frames: np.ndarray,
    local_score: np.ndarray,
    centers: np.ndarray,
    log_field: np.ndarray,
    idx: int,
) -> dict[str, float]:
    center_mag = np.asarray(mag[:, idx], dtype=float)
    center_local = np.asarray(local_frames[:, idx], dtype=float)
    fc = float(f[idx])

    local_delta_scores: dict[float, float] = {}
    q80_deltas: dict[float, float] = {}
    persistence_deltas: dict[float, float] = {}
    raw_q80: dict[float, float] = {}
    raw_gt1: dict[float, float] = {}
    log_delta: dict[float, float] = {}

    current_local_score = float(local_score[idx])
    current_q80 = float(np.quantile(center_local, 0.80))
    current_persistence = float(np.mean(center_local > 1.0))
    current_log = float(np.interp(fc, centers, log_field))

    for frac in SCALES:
        min_hz = 45.0 if frac <= 0.04 else 90.0
        pred_mag, li, ri = reconstruct_track(
            mag, f, idx, frac, min_hz
        )
        pred_local, _, _ = reconstruct_track(
            local_frames, f, idx, frac, min_hz
        )

        boost = center_mag - pred_mag
        pred_local_pos = np.maximum(pred_local, 0.0)
        pred_local_score = float(np.quantile(pred_local_pos, 0.82))
        pred_q80 = float(np.quantile(pred_local, 0.80))
        pred_persistence = float(np.mean(pred_local > 1.0))

        local_delta_scores[frac] = current_local_score - pred_local_score
        q80_deltas[frac] = current_q80 - pred_q80
        persistence_deltas[frac] = current_persistence - pred_persistence
        raw_q80[frac] = float(np.quantile(boost, 0.80))
        raw_gt1[frac] = float(np.mean(boost > 1.0))

        left_hz = float(f[li])
        right_hz = float(f[ri])
        left_log = float(np.interp(left_hz, centers, log_field))
        right_log = float(np.interp(right_hz, centers, log_field))
        if right_hz <= left_hz + 1e-9:
            pred_log = 0.5 * (left_log + right_log)
        else:
            w = float(np.clip(
                (fc - left_hz) / (right_hz - left_hz), 0.0, 1.0
            ))
            pred_log = (1.0 - w) * left_log + w * right_log
        log_delta[frac] = current_log - pred_log

    deltas = np.asarray(
        [local_delta_scores[x] for x in SCALES], dtype=float
    )
    positive = np.maximum(deltas, 0.0)

    return {
        "cf_delta_local_s2": local_delta_scores[0.02],
        "cf_delta_local_s4": local_delta_scores[0.04],
        "cf_delta_local_s8": local_delta_scores[0.08],
        "cf_delta_local_s12": local_delta_scores[0.12],
        "cf_delta_q80_s4": q80_deltas[0.04],
        "cf_delta_q80_s8": q80_deltas[0.08],
        "cf_delta_persistence_s4": persistence_deltas[0.04],
        "cf_delta_persistence_s8": persistence_deltas[0.08],
        "cf_raw_boost_q80_s4": raw_q80[0.04],
        "cf_raw_boost_q80_s8": raw_q80[0.08],
        "cf_raw_boost_gt1_s4": raw_gt1[0.04],
        "cf_raw_boost_gt1_s8": raw_gt1[0.08],
        "cf_log_delta_s4": log_delta[0.04],
        "cf_log_delta_s8": log_delta[0.08],
        "cf_scale_consistency": float(
            np.mean(positive) / (np.std(deltas) + 0.25)
        ),
        "cf_relative_suppression": float(
            np.max(positive) / (abs(current_local_score) + 0.25)
        ),
    }


def extract_candidates_cf(x, f0_t, f0, f0_conf):
    f, _, mag = r3.stft_db(x)
    local, centers, log_field, local_frames = r3.build_fields(f, mag)
    merged = r3.candidate_sets(f, local, centers, log_field)

    local20 = f[r3.sparse_select(f, local, 20, peaks_only=True)]
    peak_idx = r3.sparse_select(centers, log_field, 15, peaks_only=True)
    dense_idx = r3.sparse_select(centers, log_field, 35, peaks_only=False)
    log_hybrid = list(centers[peak_idx[:10]])
    for fr in centers[dense_idx]:
        if all(
            abs(fr-old) >= max(55, 0.018*max(fr, old))
            for old in log_hybrid
        ):
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
            norm = np.clip(
                np.abs(freq-nearest)/(0.5*vals+1e-9), 0, 1
            )
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
        row.update(counterfactual_features(
            f, mag, local_frames, local, centers, log_field, idx
        ))
        rows.append(row)

    return rows, f, mag


def add_cf_relative(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    grouped = frame.groupby("case_id", sort=False)
    for src, dst in zip(CF_RAW, CF_REL):
        mean = grouped[src].transform("mean")
        std = grouped[src].transform("std").fillna(0.0)
        std = std.where(std > 1e-6, 1.0)
        frame[dst] = (frame[src] - mean) / std
    return frame


def build_ranker_frame(seed: int) -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_cf
    frame = r3.build_dataset(seed, 2)
    frame = r3.add_relative(frame)
    return add_cf_relative(frame)


def build_external_clean_frame() -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_cf
    examples, _, _ = reaudit.collect_examples(10, 5000)
    rows = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = extract_candidates_cf(
            x, f0_t, f0, f0_conf
        )
        case_id = f'cf:{ex["singer"]}:{ex["source_basename"]}'
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
    return add_cf_relative(frame)


def labelled_proxy_diagnostics(frame: pd.DataFrame, seed: int):
    oracle = r7.add_oracle_features(frame)
    labelled = r3.labelled(oracle)
    target = labelled[labelled.is_target == 1]
    safe = labelled[labelled.safe_negative == 1]

    rows = []
    for feature in [
        "cf_delta_local_s4",
        "cf_delta_local_s8",
        "cf_raw_boost_q80_s4",
        "cf_raw_boost_q80_s8",
        "cf_log_delta_s4",
        "cf_log_delta_s8",
    ]:
        t = target[feature].to_numpy(dtype=float)
        s = safe[feature].to_numpy(dtype=float)
        corr = spearmanr(
            labelled[feature].to_numpy(dtype=float),
            np.abs(labelled["delta_local_score"].to_numpy(dtype=float)),
            nan_policy="omit",
        ).statistic
        rows.append({
            "seed": seed,
            "feature": feature,
            "target_median": float(np.median(t)) if len(t) else None,
            "safe_median": float(np.median(s)) if len(s) else None,
            "spearman_vs_abs_true_delta_local": (
                float(corr) if np.isfinite(corr) else 0.0
            ),
        })
    return rows


def strong_top5_given_hit(frame, score_col):
    return r8.strong_top5_given_hit(frame, score_col)


def choose_threshold(valid, score_col):
    return r8.choose_threshold(valid, score_col)


def clean_fpr(frame, score_col, threshold):
    return r8.clean_fpr(frame, score_col, threshold)


def evaluate_seed(seed: int, external: pd.DataFrame):
    frame = build_ranker_frame(seed)
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    static_pipe, static_c, static_valid = r8.fit_model(
        train, valid, list(r3.STATIC_FEATURES), seed
    )
    cf_pipe, cf_c, cf_valid = r8.fit_model(
        train, valid, CF_FEATURES, seed + 113
    )

    for part in [valid, test]:
        part["static_score"] = static_pipe.predict_proba(
            part[r3.STATIC_FEATURES]
        )[:, 1]
        part["cf_score"] = cf_pipe.predict_proba(
            part[CF_FEATURES]
        )[:, 1]
        part["simple_cf_score"] = part["rel_cf_delta_local_s4"]

    static = r3.rank_metrics(test, "static_score")
    combined = r3.rank_metrics(test, "cf_score")
    simple = r3.rank_metrics(test, "simple_cf_score")

    for m, col in [
        (static, "static_score"),
        (combined, "cf_score"),
        (simple, "simple_cf_score"),
    ]:
        strong, n = strong_top5_given_hit(test, col)
        m["strong_top5_given_generator_hit"] = strong
        m["strong_hit_cases"] = n

    static_th = choose_threshold(valid, "static_score")
    cf_th = choose_threshold(valid, "cf_score")
    simple_th = choose_threshold(valid, "simple_cf_score")

    ext = external.copy()
    ext["static_score"] = static_pipe.predict_proba(
        ext[r3.STATIC_FEATURES]
    )[:, 1]
    ext["cf_score"] = cf_pipe.predict_proba(
        ext[CF_FEATURES]
    )[:, 1]
    ext["simple_cf_score"] = ext["rel_cf_delta_local_s4"]

    static_fpr = clean_fpr(ext, "static_score", static_th)
    cf_fpr = clean_fpr(ext, "cf_score", cf_th)
    simple_fpr = clean_fpr(ext, "simple_cf_score", simple_th)

    oracle = R7_ORACLE_COND_TOP5[seed]
    static_cond = static["top5_given_generator_hit"]
    cf_cond = combined["top5_given_generator_hit"]
    gap = max(oracle - static_cond, 1e-9)
    closure = float((cf_cond - static_cond) / gap)

    rank_sources = set(frame.source_name.astype(str).unique())
    external_sources = set(ext.source_name.astype(str).unique())
    overlap = sorted(rank_sources & external_sources)

    return {
        "seed": seed,
        "static_C": static_c,
        "counterfactual_C": cf_c,
        "static_validation": static_valid,
        "counterfactual_validation": cf_valid,
        "static_test": static,
        "counterfactual_test": combined,
        "simple_inpaint_test": simple,
        "oracle_conditional_top5": oracle,
        "oracle_strong_conditional_top5":
            R7_ORACLE_STRONG_COND_TOP5[seed],
        "conditional_top5_gap_closure": closure,
        "external_clean_static_fpr": static_fpr,
        "external_clean_counterfactual_fpr": cf_fpr,
        "external_clean_simple_inpaint_fpr": simple_fpr,
        "external_clean_n": int(ext.case_id.nunique()),
        "source_overlap_count": len(overlap),
        "proxy_diagnostics": labelled_proxy_diagnostics(frame, seed),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    external = build_external_clean_frame()
    results = [evaluate_seed(seed, external) for seed in SEEDS]

    criteria = {}
    for r in results:
        seed = str(r["seed"])
        static = r["static_test"]
        cf = r["counterfactual_test"]
        criteria[seed] = {
            "zero_source_overlap": bool(r["source_overlap_count"] == 0),
            "conditional_top5_improves_by_0_08": bool(
                cf["top5_given_generator_hit"]
                >= static["top5_given_generator_hit"] + 0.08
            ),
            "oracle_gap_closure_gte_0_15": bool(
                r["conditional_top5_gap_closure"] >= 0.15
            ),
            "strong_conditional_top5_not_worse_by_0_05": bool(
                cf["strong_top5_given_generator_hit"] is not None
                and static["strong_top5_given_generator_hit"] is not None
                and cf["strong_top5_given_generator_hit"]
                >= static["strong_top5_given_generator_hit"] - 0.05
            ),
            "external_clean_fpr_not_worse_by_0_025": bool(
                r["external_clean_counterfactual_fpr"]
                <= r["external_clean_static_fpr"] + 0.025
            ),
            "generator_ceiling_gte_0_80": bool(
                cf["generator_ceiling"] >= 0.80
            ),
        }

    retention = all(all(v.values()) for v in criteria.values())

    diag_rows = []
    summary_results = {}
    for r in results:
        diag_rows.extend(r["proxy_diagnostics"])
        rr = dict(r)
        del rr["proxy_diagnostics"]
        summary_results[str(r["seed"])] = rr

    summary = {
        "experiment":
            "VOCAL_RESONANCE_R11_SELF_COUNTERFACTUAL_INPAINTING",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "counterfactual_feature_family": CF_RAW,
        "per_seed": summary_results,
        "retention_gate": {
            "accepted": bool(retention),
            "criteria": criteria,
            "meaning": (
                "Whether same-observation spectral inpainting is worth "
                "retaining as a deployable single-view causal proxy."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "R11 is an information-gap experiment. Existing semantic "
                "ranking product criteria remain downstream."
            ),
        },
        "raw_audio_persisted": False,
    }

    rows = []
    for r in results:
        for model, metrics, fpr in [
            ("static", r["static_test"], r["external_clean_static_fpr"]),
            (
                "self_counterfactual",
                r["counterfactual_test"],
                r["external_clean_counterfactual_fpr"],
            ),
            (
                "simple_inpaint",
                r["simple_inpaint_test"],
                r["external_clean_simple_inpaint_fpr"],
            ),
        ]:
            rows.append({
                "seed": r["seed"],
                "model": model,
                "top1": metrics["top1"],
                "top3": metrics["top3"],
                "top5": metrics["top5"],
                "top5_given_generator_hit":
                    metrics["top5_given_generator_hit"],
                "strong_top5_given_generator_hit":
                    metrics["strong_top5_given_generator_hit"],
                "mrr": metrics["mrr"],
                "generator_ceiling": metrics["generator_ceiling"],
                "external_clean_fpr": fpr,
                "oracle_conditional_top5":
                    r["oracle_conditional_top5"],
                "gap_closure": (
                    r["conditional_top5_gap_closure"]
                    if model == "self_counterfactual"
                    else 0.0
                ),
            })
    pd.DataFrame(rows).to_csv(out/"comparison.csv", index=False)
    pd.DataFrame(diag_rows).to_csv(
        out/"proxy_diagnostics.csv", index=False
    )
    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
