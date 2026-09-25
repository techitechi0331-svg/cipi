"""CIPI Vocal Resonance v0.4R.8 single-view local-patch proxy experiment.

Research-only. No production suppressor DSP and no raw audio persistence.

Purpose:
Test whether richer deployable single-view candidate context can recover part of
the R7 causal-oracle gap without using a clean reference.

Candidate context is intentionally interpretable:
- multi-scale spectral residual shape;
- symmetric shoulder drop around the candidate;
- shoulder asymmetry;
- center-vs-neighborhood temporal coherence;
- within-case relative normalization.

Baselines:
- simple local prominence;
- frozen v0.4R.2-style static safe-negative ranker.

The paired R7 oracle is NOT used for training and is only referenced as a
diagnostic ceiling when reporting gap closure.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent

R5_PATH = HERE / "temporal_morphology_ranker.py"
spec = importlib.util.spec_from_file_location("r5_patch_base", R5_PATH)
r5 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r5)
r3 = r5.r3
reaudit = r5.reaudit

SEEDS = [20261003, 20261013]

PATCH_RAW = [
    "ms_resid_s2_q80",
    "ms_resid_s4_q80",
    "ms_resid_s8_q80",
    "ms_resid_s12_q80",
    "narrow_minus_broad",
    "shoulder_drop_2_q80",
    "shoulder_drop_4_q80",
    "shoulder_drop_8_q80",
    "shoulder_asym_4_median",
    "center_neighbor_corr_4",
    "center_neighbor_corr_8",
    "patch_stationarity_4",
]
PATCH_REL = [f"rel_{x}" for x in PATCH_RAW]
PATCH_FEATURES = list(r3.STATIC_FEATURES) + PATCH_REL

R7_ORACLE_COND_TOP5 = {
    20261003: 1.0,
    20261013: 0.9259259259259259,
}
R7_ORACLE_STRONG_COND_TOP5 = {
    20261003: 1.0,
    20261013: 1.0,
}


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 4 or np.std(a) < 1e-9 or np.std(b) < 1e-9:
        return 0.0
    c = float(np.corrcoef(a, b)[0, 1])
    return c if np.isfinite(c) else 0.0


def patch_features(mag: np.ndarray, idx: int) -> dict[str, float]:
    # mag shape: time x frequency, in dB.
    n_freq = mag.shape[1]
    center = mag[:, idx]

    residuals = {}
    for sigma in [2, 4, 8, 12]:
        env = ndimage.gaussian_filter1d(mag, sigma, axis=1, mode="nearest")
        residuals[sigma] = mag[:, idx] - env[:, idx]

    def shoulders(offset: int) -> tuple[np.ndarray, np.ndarray]:
        li = max(0, idx - offset)
        ri = min(n_freq - 1, idx + offset)
        return mag[:, li], mag[:, ri]

    l2, r2 = shoulders(2)
    l4, r4 = shoulders(4)
    l8, r8 = shoulders(8)

    sh2 = 0.5 * (l2 + r2)
    sh4 = 0.5 * (l4 + r4)
    sh8 = 0.5 * (l8 + r8)

    q = lambda x: float(np.quantile(np.asarray(x, dtype=float), 0.80))

    patch4 = center - sh4
    return {
        "ms_resid_s2_q80": q(residuals[2]),
        "ms_resid_s4_q80": q(residuals[4]),
        "ms_resid_s8_q80": q(residuals[8]),
        "ms_resid_s12_q80": q(residuals[12]),
        "narrow_minus_broad": q(residuals[2]) - q(residuals[12]),
        "shoulder_drop_2_q80": q(center - sh2),
        "shoulder_drop_4_q80": q(center - sh4),
        "shoulder_drop_8_q80": q(center - sh8),
        "shoulder_asym_4_median": float(np.median(np.abs(l4 - r4))),
        "center_neighbor_corr_4": safe_corr(center, sh4),
        "center_neighbor_corr_8": safe_corr(center, sh8),
        "patch_stationarity_4": float(
            np.mean(np.abs(patch4 - np.median(patch4)))
        ),
    }


def extract_candidates_patch(x, f0_t, f0, f0_conf):
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
            nearest = h * vals
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
        row.update(patch_features(mag, idx))
        rows.append(row)
    return rows, f, mag


def add_patch_relative(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    grouped = frame.groupby("case_id", sort=False)
    for src, dst in zip(PATCH_RAW, PATCH_REL):
        mean = grouped[src].transform("mean")
        std = grouped[src].transform("std").fillna(0.0)
        std = std.where(std > 1e-6, 1.0)
        frame[dst] = (frame[src] - mean) / std
    return frame


def build_ranker_frame(seed: int) -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_patch
    frame = r3.build_dataset(seed, 2)
    frame = r3.add_relative(frame)
    return add_patch_relative(frame)


def build_external_clean_frame() -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_patch
    examples, _, _ = reaudit.collect_examples(10, 5000)
    rows = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = extract_candidates_patch(x, f0_t, f0, f0_conf)
        case_id = f'patch:{ex["singer"]}:{ex["source_basename"]}'
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
    return add_patch_relative(frame)


def fit_model(train: pd.DataFrame, valid: pd.DataFrame,
              features: list[str], seed: int):
    labelled = r3.labelled(train)
    weights = np.ones(len(labelled), dtype=float)
    pos = labelled.is_target.to_numpy() == 1
    effect = labelled.physical_effect_db.fillna(0.0).to_numpy()
    weights[pos] = np.clip(effect[pos]/3.0, 0.25, 2.0)

    trials = []
    for cval in [0.03, 0.1, 0.3, 1.0, 3.0]:
        pipe = Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(
                C=float(cval),
                class_weight="balanced",
                max_iter=3000,
                solver="lbfgs",
                random_state=seed,
            )),
        ])
        pipe.fit(
            labelled[features],
            labelled.is_target,
            model__sample_weight=weights,
        )
        trial = valid.copy()
        trial["score"] = pipe.predict_proba(trial[features])[:, 1]
        m = r3.rank_metrics(trial, "score")
        key = (
            m["top5_given_generator_hit"],
            m["top5_effect_gte3"] if m["top5_effect_gte3"] is not None else -1.0,
            m["mrr"],
            -cval,
        )
        trials.append((key, cval, pipe, m))
    trials.sort(key=lambda x: x[0], reverse=True)
    _, cval, pipe, metrics = trials[0]
    return pipe, float(cval), metrics


def strong_top5_given_hit(frame: pd.DataFrame, score_col: str):
    injected = frame[
        (frame.is_clean == 0)
        & (frame.physical_effect_db >= 3.0)
    ]
    hits = []
    n = 0
    for _, g in injected.groupby("case_id"):
        if int(g.generator_hit.max()) <= 0:
            continue
        n += 1
        ranked = g.sort_values(score_col, ascending=False).head(5)
        hits.append(int(ranked.is_target.max() > 0))
    return (float(np.mean(hits)) if hits else None, n)


def clean_fpr(frame: pd.DataFrame, score_col: str, threshold: float) -> float:
    clean = frame.copy()
    maxima = clean.groupby("case_id")[score_col].max()
    return float(np.mean(maxima > threshold)) if len(maxima) else 0.0


def choose_threshold(valid: pd.DataFrame, score_col: str) -> float:
    clean = valid[valid.is_clean == 1]
    maxima = clean.groupby("case_id")[score_col].max().to_numpy()
    return float(np.quantile(maxima, 0.95)) if len(maxima) else float("inf")


def evaluate_seed(seed: int, external: pd.DataFrame):
    frame = build_ranker_frame(seed)
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    static_pipe, static_c, static_valid = fit_model(
        train, valid, list(r3.STATIC_FEATURES), seed
    )
    patch_pipe, patch_c, patch_valid = fit_model(
        train, valid, PATCH_FEATURES, seed + 77
    )

    for part in [valid, test]:
        part["static_score"] = static_pipe.predict_proba(
            part[r3.STATIC_FEATURES]
        )[:, 1]
        part["patch_score"] = patch_pipe.predict_proba(
            part[PATCH_FEATURES]
        )[:, 1]

    static = r3.rank_metrics(test, "static_score")
    patch = r3.rank_metrics(test, "patch_score")
    static_strong, static_strong_n = strong_top5_given_hit(
        test, "static_score"
    )
    patch_strong, patch_strong_n = strong_top5_given_hit(
        test, "patch_score"
    )
    static["strong_top5_given_generator_hit"] = static_strong
    patch["strong_top5_given_generator_hit"] = patch_strong
    static["strong_hit_cases"] = static_strong_n
    patch["strong_hit_cases"] = patch_strong_n

    static_th = choose_threshold(valid, "static_score")
    patch_th = choose_threshold(valid, "patch_score")

    ext = external.copy()
    ext["static_score"] = static_pipe.predict_proba(
        ext[r3.STATIC_FEATURES]
    )[:, 1]
    ext["patch_score"] = patch_pipe.predict_proba(
        ext[PATCH_FEATURES]
    )[:, 1]

    static_fpr = clean_fpr(ext, "static_score", static_th)
    patch_fpr = clean_fpr(ext, "patch_score", patch_th)

    oracle = R7_ORACLE_COND_TOP5[seed]
    static_cond = static["top5_given_generator_hit"]
    patch_cond = patch["top5_given_generator_hit"]
    gap = max(oracle - static_cond, 1e-9)
    gap_closure = (patch_cond - static_cond) / gap

    return {
        "seed": seed,
        "static_C": static_c,
        "patch_C": patch_c,
        "static_validation": static_valid,
        "patch_validation": patch_valid,
        "static_test": static,
        "patch_test": patch,
        "oracle_conditional_top5": oracle,
        "oracle_strong_conditional_top5": R7_ORACLE_STRONG_COND_TOP5[seed],
        "conditional_top5_gap_closure": float(gap_closure),
        "external_clean_static_fpr": static_fpr,
        "external_clean_patch_fpr": patch_fpr,
        "external_clean_n": int(ext.case_id.nunique()),
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
        patch = r["patch_test"]
        criteria[seed] = {
            "conditional_top5_improves_by_0_08": bool(
                patch["top5_given_generator_hit"]
                >= static["top5_given_generator_hit"] + 0.08
            ),
            "oracle_gap_closure_gte_0_15": bool(
                r["conditional_top5_gap_closure"] >= 0.15
            ),
            "strong_conditional_top5_not_worse_by_0_05": bool(
                patch["strong_top5_given_generator_hit"] is not None
                and static["strong_top5_given_generator_hit"] is not None
                and patch["strong_top5_given_generator_hit"]
                    >= static["strong_top5_given_generator_hit"] - 0.05
            ),
            "external_clean_fpr_not_worse_by_0_05": bool(
                r["external_clean_patch_fpr"]
                <= r["external_clean_static_fpr"] + 0.05
            ),
            "generator_ceiling_gte_0_80": bool(
                patch["generator_ceiling"] >= 0.80
            ),
        }

    retention = all(all(v.values()) for v in criteria.values())

    summary = {
        "experiment": "VOCAL_RESONANCE_R8_SINGLE_VIEW_LOCAL_PATCH",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "feature_family": PATCH_RAW,
        "per_seed": {str(r["seed"]): r for r in results},
        "retention_gate": {
            "accepted": bool(retention),
            "criteria": criteria,
            "meaning": (
                "Whether the local-patch feature family is worth retaining for "
                "further single-view research. Passing is not a product gate."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "R8 is an information-gap experiment. Product semantic-ranking "
                "criteria remain unchanged and downstream."
            ),
        },
        "raw_audio_persisted": False,
    }

    rows = []
    for r in results:
        for model, m in [
            ("static", r["static_test"]),
            ("patch", r["patch_test"]),
        ]:
            rows.append({
                "seed": r["seed"],
                "model": model,
                "top1": m["top1"],
                "top3": m["top3"],
                "top5": m["top5"],
                "top5_given_generator_hit": m["top5_given_generator_hit"],
                "strong_top5": m["top5_effect_gte3"],
                "strong_top5_given_generator_hit":
                    m["strong_top5_given_generator_hit"],
                "mrr": m["mrr"],
                "generator_ceiling": m["generator_ceiling"],
                "external_clean_fpr": (
                    r["external_clean_static_fpr"]
                    if model == "static"
                    else r["external_clean_patch_fpr"]
                ),
                "oracle_conditional_top5": r["oracle_conditional_top5"],
                "gap_closure": (
                    0.0 if model == "static"
                    else r["conditional_top5_gap_closure"]
                ),
            })
    pd.DataFrame(rows).to_csv(out/"comparison.csv", index=False)

    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
