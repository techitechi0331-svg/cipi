"""CIPI Vocal Resonance v0.4R.9 fixed-Hz temporal transfer-consistency.

Research only. No production DSP. No raw vocal audio persistence.

Hypothesis:
A fixed resonance behaves more like a stable transfer-function boost at one
absolute frequency: center-vs-neighborhood relative gain remains biased and
consistent over time. Natural harmonics/formants may be locally narrow but
their fixed-Hz relative-gain relationship should be less stationary.

No clean reference is used at inference.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
R8_PATH = HERE / "local_patch_proxy.py"
spec = importlib.util.spec_from_file_location("r8_transfer_base", R8_PATH)
r8 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r8)

r3 = r8.r3
reaudit = r8.reaudit

SEEDS = [20261003, 20261013]

TRANSFER_RAW = [
    "rel_gain_near_median",
    "rel_gain_near_mad",
    "rel_gain_near_q80",
    "rel_gain_near_pos_frac",
    "rel_gain_near_gt1_frac",
    "rel_gain_near_robust_snr",
    "rel_gain_near_diff_mad",
    "rel_gain_near_lag1_corr",
    "rel_gain_far_median",
    "rel_gain_far_mad",
    "near_far_consistency",
    "center_reference_corr",
    "regression_intercept",
    "regression_slope",
    "regression_resid_mad",
]
TRANSFER_REL = [f"rel_{x}" for x in TRANSFER_RAW]
TRANSFER_FEATURES = list(r3.STATIC_FEATURES) + TRANSFER_REL

R7_ORACLE_COND_TOP5 = {
    20261003: 1.0,
    20261013: 0.9259259259259259,
}
R7_ORACLE_STRONG_COND_TOP5 = {
    20261003: 1.0,
    20261013: 1.0,
}


def robust_mad(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if not len(x):
        return 0.0
    med = float(np.median(x))
    return float(np.median(np.abs(x - med)))


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 4 or np.std(a) < 1e-8 or np.std(b) < 1e-8:
        return 0.0
    c = float(np.corrcoef(a, b)[0, 1])
    return c if np.isfinite(c) else 0.0


def nearest_index(f: np.ndarray, hz: float) -> int:
    return int(np.argmin(np.abs(f - hz)))


def context_indices(f: np.ndarray, idx: int, frac: float, min_hz: float):
    fc = float(f[idx])
    offset = max(min_hz, frac * fc)
    li = nearest_index(f, max(float(f[0]), fc - offset))
    ri = nearest_index(f, min(float(f[-1]), fc + offset))
    if li == idx:
        li = max(0, idx - 1)
    if ri == idx:
        ri = min(len(f) - 1, idx + 1)
    return li, ri


def transfer_features(f: np.ndarray, mag: np.ndarray, idx: int) -> dict[str, float]:
    center = np.asarray(mag[:, idx], dtype=float)

    near_l, near_r = context_indices(f, idx, frac=0.035, min_hz=90.0)
    far_l, far_r = context_indices(f, idx, frac=0.075, min_hz=180.0)

    ref_near = 0.5 * (mag[:, near_l] + mag[:, near_r])
    ref_far = 0.5 * (mag[:, far_l] + mag[:, far_r])

    rel_near = center - ref_near
    rel_far = center - ref_far

    med = float(np.median(rel_near))
    mad = robust_mad(rel_near)
    q80 = float(np.quantile(rel_near, 0.80))
    pos_frac = float(np.mean(rel_near > 0.0))
    gt1_frac = float(np.mean(rel_near > 1.0))
    robust_snr = float(med / (1.4826 * mad + 0.25))

    diff_mad = robust_mad(np.diff(rel_near)) if len(rel_near) > 1 else 0.0
    lag1 = safe_corr(rel_near[:-1], rel_near[1:]) if len(rel_near) > 2 else 0.0

    far_med = float(np.median(rel_far))
    far_mad = robust_mad(rel_far)
    near_far_consistency = safe_corr(rel_near, rel_far)
    center_reference_corr = safe_corr(center, ref_near)

    energetic = ref_near > np.quantile(ref_near, 0.20)
    x = ref_near[energetic]
    y = center[energetic]
    if len(x) >= 8 and np.std(x) > 1e-8:
        A = np.column_stack([np.ones(len(x)), x])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        intercept = float(beta[0])
        slope = float(beta[1])
        resid = y - (intercept + slope * x)
        resid_mad = robust_mad(resid)
    else:
        intercept = med
        slope = 1.0
        resid_mad = mad

    return {
        "rel_gain_near_median": med,
        "rel_gain_near_mad": mad,
        "rel_gain_near_q80": q80,
        "rel_gain_near_pos_frac": pos_frac,
        "rel_gain_near_gt1_frac": gt1_frac,
        "rel_gain_near_robust_snr": robust_snr,
        "rel_gain_near_diff_mad": diff_mad,
        "rel_gain_near_lag1_corr": lag1,
        "rel_gain_far_median": far_med,
        "rel_gain_far_mad": far_mad,
        "near_far_consistency": near_far_consistency,
        "center_reference_corr": center_reference_corr,
        "regression_intercept": intercept,
        "regression_slope": slope,
        "regression_resid_mad": resid_mad,
    }


def extract_candidates_transfer(x, f0_t, f0, f0_conf):
    f, t, mag = r3.stft_db(x)
    local, centers, log_field, local_frames = r3.build_fields(f, mag)
    merged = r3.candidate_sets(f, local, centers, log_field)

    local20 = f[r3.sparse_select(f, local, 20, peaks_only=True)]
    peak_idx = r3.sparse_select(centers, log_field, 15, peaks_only=True)
    dense_idx = r3.sparse_select(centers, log_field, 35, peaks_only=False)
    log_hybrid = list(centers[peak_idx[:10]])
    for fr in centers[dense_idx]:
        if all(abs(fr-old) >= max(55, 0.018*max(fr, old))
               for old in log_hybrid):
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
        row.update(transfer_features(f, mag, idx))
        rows.append(row)

    return rows, f, mag


def add_transfer_relative(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    grouped = frame.groupby("case_id", sort=False)
    for src, dst in zip(TRANSFER_RAW, TRANSFER_REL):
        mean = grouped[src].transform("mean")
        std = grouped[src].transform("std").fillna(0.0)
        std = std.where(std > 1e-6, 1.0)
        frame[dst] = (frame[src] - mean) / std
    return frame


def build_ranker_frame(seed: int) -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_transfer
    frame = r3.build_dataset(seed, 2)
    frame = r3.add_relative(frame)
    return add_transfer_relative(frame)


def build_external_clean_frame() -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_transfer
    examples, _, _ = reaudit.collect_examples(10, 5000)
    rows = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = extract_candidates_transfer(x, f0_t, f0, f0_conf)
        case_id = f'transfer:{ex["singer"]}:{ex["source_basename"]}'
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
    return add_transfer_relative(frame)


def fit_model(train, valid, features, seed):
    return r8.fit_model(train, valid, features, seed)


def strong_top5_given_hit(frame, score_col):
    return r8.strong_top5_given_hit(frame, score_col)


def choose_threshold(valid, score_col):
    return r8.choose_threshold(valid, score_col)


def clean_fpr(frame, score_col, threshold):
    return r8.clean_fpr(frame, score_col, threshold)


def feature_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    labelled = r3.labelled(frame)
    target = labelled[labelled.is_target == 1]
    safe = labelled[labelled.safe_negative == 1]
    rows = []
    for feature in TRANSFER_RAW:
        t = target[feature].to_numpy(dtype=float)
        s = safe[feature].to_numpy(dtype=float)
        t_med = float(np.median(t)) if len(t) else np.nan
        s_med = float(np.median(s)) if len(s) else np.nan
        pooled = np.median(np.abs(
            np.concatenate([t - t_med, s - s_med])
        )) if len(t) and len(s) else np.nan
        rows.append({
            "feature": feature,
            "target_median": t_med,
            "safe_median": s_med,
            "median_delta": t_med - s_med,
            "robust_separation": (
                float((t_med - s_med) / (1.4826*pooled + 1e-6))
                if np.isfinite(pooled) else np.nan
            ),
        })
    return pd.DataFrame(rows)


def evaluate_seed(seed: int, external: pd.DataFrame):
    frame = build_ranker_frame(seed)
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    static_pipe, static_c, static_valid = fit_model(
        train, valid, list(r3.STATIC_FEATURES), seed
    )
    transfer_pipe, transfer_c, transfer_valid = fit_model(
        train, valid, TRANSFER_FEATURES, seed + 91
    )

    for part in [valid, test]:
        part["static_score"] = static_pipe.predict_proba(
            part[r3.STATIC_FEATURES]
        )[:, 1]
        part["transfer_score"] = transfer_pipe.predict_proba(
            part[TRANSFER_FEATURES]
        )[:, 1]

    static = r3.rank_metrics(test, "static_score")
    transfer = r3.rank_metrics(test, "transfer_score")

    static_strong, static_strong_n = strong_top5_given_hit(
        test, "static_score"
    )
    transfer_strong, transfer_strong_n = strong_top5_given_hit(
        test, "transfer_score"
    )
    static["strong_top5_given_generator_hit"] = static_strong
    transfer["strong_top5_given_generator_hit"] = transfer_strong
    static["strong_hit_cases"] = static_strong_n
    transfer["strong_hit_cases"] = transfer_strong_n

    static_th = choose_threshold(valid, "static_score")
    transfer_th = choose_threshold(valid, "transfer_score")

    ext = external.copy()
    ext["static_score"] = static_pipe.predict_proba(
        ext[r3.STATIC_FEATURES]
    )[:, 1]
    ext["transfer_score"] = transfer_pipe.predict_proba(
        ext[TRANSFER_FEATURES]
    )[:, 1]

    static_fpr = clean_fpr(ext, "static_score", static_th)
    transfer_fpr = clean_fpr(ext, "transfer_score", transfer_th)

    oracle = R7_ORACLE_COND_TOP5[seed]
    static_cond = static["top5_given_generator_hit"]
    transfer_cond = transfer["top5_given_generator_hit"]
    gap = max(oracle - static_cond, 1e-9)
    gap_closure = float((transfer_cond - static_cond) / gap)

    return {
        "seed": seed,
        "static_C": static_c,
        "transfer_C": transfer_c,
        "static_validation": static_valid,
        "transfer_validation": transfer_valid,
        "static_test": static,
        "transfer_test": transfer,
        "oracle_conditional_top5": oracle,
        "oracle_strong_conditional_top5":
            R7_ORACLE_STRONG_COND_TOP5[seed],
        "conditional_top5_gap_closure": gap_closure,
        "external_clean_static_fpr": static_fpr,
        "external_clean_transfer_fpr": transfer_fpr,
        "external_clean_n": int(ext.case_id.nunique()),
        "feature_diagnostics": feature_diagnostics(test).to_dict("records"),
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
        transfer = r["transfer_test"]
        criteria[seed] = {
            "conditional_top5_improves_by_0_08": bool(
                transfer["top5_given_generator_hit"]
                >= static["top5_given_generator_hit"] + 0.08
            ),
            "oracle_gap_closure_gte_0_15": bool(
                r["conditional_top5_gap_closure"] >= 0.15
            ),
            "strong_conditional_top5_not_worse_by_0_05": bool(
                transfer["strong_top5_given_generator_hit"] is not None
                and static["strong_top5_given_generator_hit"] is not None
                and transfer["strong_top5_given_generator_hit"]
                    >= static["strong_top5_given_generator_hit"] - 0.05
            ),
            "external_clean_fpr_not_worse_by_0_05": bool(
                r["external_clean_transfer_fpr"]
                <= r["external_clean_static_fpr"] + 0.05
            ),
            "generator_ceiling_gte_0_80": bool(
                transfer["generator_ceiling"] >= 0.80
            ),
        }

    retention = all(all(v.values()) for v in criteria.values())

    diag_rows = []
    for r in results:
        for row in r["feature_diagnostics"]:
            diag_rows.append({"seed": r["seed"], **row})
        del r["feature_diagnostics"]

    summary = {
        "experiment": "VOCAL_RESONANCE_R9_TRANSFER_CONSISTENCY",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "feature_family": TRANSFER_RAW,
        "per_seed": {str(r["seed"]): r for r in results},
        "retention_gate": {
            "accepted": bool(retention),
            "criteria": criteria,
            "meaning": (
                "Whether fixed-Hz temporal transfer-consistency is worth "
                "retaining as a deployable single-view feature family."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "R9 is an information-gap experiment. Existing product "
                "semantic-ranking criteria remain downstream."
            ),
        },
        "raw_audio_persisted": False,
    }

    rows = []
    for r in results:
        for model, m in [
            ("static", r["static_test"]),
            ("transfer", r["transfer_test"]),
        ]:
            rows.append({
                "seed": r["seed"],
                "model": model,
                "top1": m["top1"],
                "top3": m["top3"],
                "top5": m["top5"],
                "top5_given_generator_hit":
                    m["top5_given_generator_hit"],
                "strong_top5": m["top5_effect_gte3"],
                "strong_top5_given_generator_hit":
                    m["strong_top5_given_generator_hit"],
                "mrr": m["mrr"],
                "generator_ceiling": m["generator_ceiling"],
                "external_clean_fpr": (
                    r["external_clean_static_fpr"]
                    if model == "static"
                    else r["external_clean_transfer_fpr"]
                ),
                "oracle_conditional_top5":
                    r["oracle_conditional_top5"],
                "gap_closure": (
                    0.0 if model == "static"
                    else r["conditional_top5_gap_closure"]
                ),
            })
    pd.DataFrame(rows).to_csv(out/"comparison.csv", index=False)
    pd.DataFrame(diag_rows).to_csv(
        out/"feature_diagnostics.csv", index=False
    )

    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
