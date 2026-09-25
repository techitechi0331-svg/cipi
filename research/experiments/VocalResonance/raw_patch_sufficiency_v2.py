"""CIPI Vocal Resonance v0.4R.12 raw 2D patch sufficiency audit.

Research-only. No production DSP and no raw audio / raw patch persistence.

R7 showed that paired causal information can rank the injected target near the
ceiling when candidate discovery hits. R8-R11 showed that four hand-crafted
single-view summary families did not recover that information robustly.

R12 asks whether the candidate-aligned local residual field itself contains
single-view information that those summaries discarded.

Models:
1) frozen static R2-style baseline;
2) raw-patch-only linear logistic model;
3) static + raw-patch linear logistic model;
4) tiny one-hidden-layer MLP diagnostic upper bound.

The tiny MLP is diagnostic only and is not a product architecture decision.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
R8_PATH = HERE / "local_patch_proxy.py"
spec = importlib.util.spec_from_file_location("r8_raw_patch_base", R8_PATH)
r8 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r8)

r3 = r8.r3
reaudit = r8.reaudit

SEEDS = [20261003, 20261013]
FREQ_RADIUS = 8
TIME_RADIUS = 12
FREQ_POINTS = 2 * FREQ_RADIUS + 1
TIME_POINTS = 2 * TIME_RADIUS + 1
PATCH_FEATURES = [
    f"raw_patch_t{t:02d}_f{k:02d}"
    for t in range(TIME_POINTS)
    for k in range(FREQ_POINTS)
]
COMBINED_FEATURES = list(r3.STATIC_FEATURES) + PATCH_FEATURES

R7_ORACLE_COND_TOP5 = {
    20261003: 1.0,
    20261013: 0.9259259259259259,
}
R7_ORACLE_STRONG_COND_TOP5 = {
    20261003: 1.0,
    20261013: 1.0,
}


def fixed_raw_patch(local_frames: np.ndarray, freq_idx: int) -> dict[str, float]:
    """Extract a true fixed-size candidate-centered local-residual patch.

    The time center is the maximum of a lightly smoothed candidate residual
    trajectory. The patch then uses direct residual samples, not temporal
    summary bins. Edge indices are clipped deterministically.

    The local residual field is already loudness-relative. Per-patch robust
    normalization removes remaining patch-wide offset/scale while static
    features retain absolute candidate strength for the combined model.
    """
    local_frames = np.asarray(local_frames, dtype=float)
    trajectory = ndimage.gaussian_filter1d(
        local_frames[:, freq_idx], sigma=2.0, mode="nearest"
    )
    time_idx = int(np.argmax(trajectory))

    t_idx = np.clip(
        np.arange(time_idx - TIME_RADIUS, time_idx + TIME_RADIUS + 1),
        0,
        local_frames.shape[0] - 1,
    )
    f_idx = np.clip(
        np.arange(freq_idx - FREQ_RADIUS, freq_idx + FREQ_RADIUS + 1),
        0,
        local_frames.shape[1] - 1,
    )

    patch = local_frames[np.ix_(t_idx, f_idx)]
    med = float(np.median(patch))
    mad = float(np.median(np.abs(patch - med)))
    scale = 1.4826 * mad + 0.35
    patch = np.clip((patch - med) / scale, -4.0, 8.0)

    flat = patch.reshape(-1)
    return {
        name: float(value)
        for name, value in zip(PATCH_FEATURES, flat)
    }


def extract_candidates_raw_patch(x, f0_t, f0, f0_conf):
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
        row.update(fixed_raw_patch(local_frames, idx))
        rows.append(row)

    return rows, f, mag


def build_ranker_frame(seed: int) -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_raw_patch
    frame = r3.build_dataset(seed, 2)
    return r3.add_relative(frame)


def build_external_clean_frame() -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_raw_patch
    examples, _, _ = reaudit.collect_examples(10, 5000)
    rows = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = extract_candidates_raw_patch(
            x, f0_t, f0, f0_conf
        )
        case_id = f'rawpatch:{ex["singer"]}:{ex["source_basename"]}'
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
    return r3.add_relative(pd.DataFrame(rows))


def fit_tiny_mlp(train: pd.DataFrame, features: list[str], seed: int):
    labelled = r3.labelled(train)
    y = labelled.is_target.to_numpy(dtype=int)

    pos_n = max(1, int(np.sum(y == 1)))
    neg_n = max(1, int(np.sum(y == 0)))
    n = len(y)
    weights = np.where(
        y == 1,
        n / (2.0 * pos_n),
        n / (2.0 * neg_n),
    ).astype(float)

    effect = labelled.physical_effect_db.fillna(0.0).to_numpy(dtype=float)
    positive = y == 1
    weights[positive] *= np.clip(
        effect[positive] / 3.0, 0.25, 2.0
    )

    pipe = Pipeline([
        ("scale", StandardScaler()),
        ("mlp", MLPClassifier(
            hidden_layer_sizes=(32,),
            activation="tanh",
            solver="adam",
            alpha=0.05,
            batch_size=64,
            learning_rate_init=0.001,
            max_iter=180,
            tol=1e-4,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=10,
            random_state=seed,
        )),
    ])
    pipe.fit(
        labelled[features],
        y,
        mlp__sample_weight=weights,
    )
    return pipe


def model_metrics(test: pd.DataFrame, score_col: str) -> dict:
    metrics = r3.rank_metrics(test, score_col)
    strong, n = r8.strong_top5_given_hit(test, score_col)
    metrics["strong_top5_given_generator_hit"] = strong
    metrics["strong_hit_cases"] = n
    return metrics


def evaluate_seed(seed: int, external: pd.DataFrame) -> dict:
    frame = build_ranker_frame(seed)
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    static_pipe, static_c, static_valid = r8.fit_model(
        train, valid, list(r3.STATIC_FEATURES), seed
    )
    patch_pipe, patch_c, patch_valid = r8.fit_model(
        train, valid, PATCH_FEATURES, seed + 201
    )
    combined_pipe, combined_c, combined_valid = r8.fit_model(
        train, valid, COMBINED_FEATURES, seed + 202
    )
    mlp_pipe = fit_tiny_mlp(train, COMBINED_FEATURES, seed + 203)

    for part in [valid, test]:
        part["static_score"] = static_pipe.predict_proba(
            part[r3.STATIC_FEATURES]
        )[:, 1]
        part["patch_linear_score"] = patch_pipe.predict_proba(
            part[PATCH_FEATURES]
        )[:, 1]
        part["combined_linear_score"] = combined_pipe.predict_proba(
            part[COMBINED_FEATURES]
        )[:, 1]
        part["tiny_mlp_score"] = mlp_pipe.predict_proba(
            part[COMBINED_FEATURES]
        )[:, 1]

    models = {
        "static": model_metrics(test, "static_score"),
        "patch_linear": model_metrics(test, "patch_linear_score"),
        "combined_linear": model_metrics(test, "combined_linear_score"),
        "tiny_mlp": model_metrics(test, "tiny_mlp_score"),
    }

    thresholds = {
        "static": r8.choose_threshold(valid, "static_score"),
        "patch_linear": r8.choose_threshold(valid, "patch_linear_score"),
        "combined_linear": r8.choose_threshold(valid, "combined_linear_score"),
        "tiny_mlp": r8.choose_threshold(valid, "tiny_mlp_score"),
    }

    ext = external.copy()
    ext["static_score"] = static_pipe.predict_proba(
        ext[r3.STATIC_FEATURES]
    )[:, 1]
    ext["patch_linear_score"] = patch_pipe.predict_proba(
        ext[PATCH_FEATURES]
    )[:, 1]
    ext["combined_linear_score"] = combined_pipe.predict_proba(
        ext[COMBINED_FEATURES]
    )[:, 1]
    ext["tiny_mlp_score"] = mlp_pipe.predict_proba(
        ext[COMBINED_FEATURES]
    )[:, 1]

    fpr = {
        name: r8.clean_fpr(ext, f"{name}_score", thresholds[name])
        if name != "static"
        else r8.clean_fpr(ext, "static_score", thresholds["static"])
        for name in ["static", "patch_linear", "combined_linear", "tiny_mlp"]
    }

    oracle = R7_ORACLE_COND_TOP5[seed]
    static_cond = models["static"]["top5_given_generator_hit"]
    denom = max(oracle - static_cond, 1e-9)

    gap_closure = {
        name: float(
            (models[name]["top5_given_generator_hit"] - static_cond) / denom
        )
        for name in ["patch_linear", "combined_linear", "tiny_mlp"]
    }

    rank_sources = set(frame.source_name.astype(str).unique())
    external_sources = set(ext.source_name.astype(str).unique())
    overlap = sorted(rank_sources & external_sources)

    return {
        "seed": seed,
        "static_C": static_c,
        "patch_C": patch_c,
        "combined_C": combined_c,
        "static_validation": static_valid,
        "patch_validation": patch_valid,
        "combined_validation": combined_valid,
        "models": models,
        "external_clean_fpr": fpr,
        "external_clean_n": int(ext.case_id.nunique()),
        "oracle_conditional_top5": oracle,
        "oracle_strong_conditional_top5":
            R7_ORACLE_STRONG_COND_TOP5[seed],
        "gap_closure": gap_closure,
        "source_overlap_count": len(overlap),
    }


def model_criteria(result: dict, name: str) -> dict:
    static = result["models"]["static"]
    model = result["models"][name]
    return {
        "zero_source_overlap": bool(
            result["source_overlap_count"] == 0
        ),
        "generator_ceiling_gte_0_80": bool(
            model["generator_ceiling"] >= 0.80
        ),
        "conditional_top5_improves_by_0_08": bool(
            model["top5_given_generator_hit"]
            >= static["top5_given_generator_hit"] + 0.08
        ),
        "oracle_gap_closure_gte_0_15": bool(
            result["gap_closure"][name] >= 0.15
        ),
        "strong_conditional_top5_not_worse_by_0_05": bool(
            model["strong_top5_given_generator_hit"] is not None
            and static["strong_top5_given_generator_hit"] is not None
            and model["strong_top5_given_generator_hit"]
                >= static["strong_top5_given_generator_hit"] - 0.05
        ),
        "external_clean_fpr_not_worse_by_0_05": bool(
            result["external_clean_fpr"][name]
            <= result["external_clean_fpr"]["static"] + 0.05
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    external = build_external_clean_frame()
    results = [evaluate_seed(seed, external) for seed in SEEDS]

    criteria = {
        name: {
            str(r["seed"]): model_criteria(r, name)
            for r in results
        }
        for name in ["patch_linear", "combined_linear", "tiny_mlp"]
    }

    passes = {
        name: all(all(x.values()) for x in per_seed.values())
        for name, per_seed in criteria.items()
    }

    if passes["patch_linear"] or passes["combined_linear"]:
        route = "RAW_PATCH_LINEAR_INFORMATION_PRESENT"
    elif passes["tiny_mlp"]:
        route = "RAW_PATCH_NONLINEAR_INFORMATION_PRESENT"
    else:
        route = "RAW_PATCH_INFORMATION_NOT_ESTABLISHED"

    summary = {
        "experiment": "VOCAL_RESONANCE_R12_RAW_PATCH_SUFFICIENCY",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "patch_shape": {
            "time_points": TIME_POINTS,
            "frequency_points": FREQ_POINTS,
            "feature_count": len(PATCH_FEATURES),
            "time_center": "max_smoothed_candidate_local_residual",
            "field": "robust_local_residual",
        },
        "raw_patch_persisted": False,
        "per_seed": {str(r["seed"]): r for r in results},
        "diagnostic_gate": {
            "accepted": bool(any(passes.values())),
            "route": route,
            "model_pass": passes,
            "criteria": criteria,
            "meaning": (
                "Whether candidate-centered raw local-residual patches contain "
                "single-view information that prior summaries discarded. The "
                "tiny MLP is a diagnostic upper bound only."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "R12 is a representation sufficiency audit. A diagnostic MLP "
                "pass would not approve a product architecture."
            ),
        },
        "raw_audio_persisted": False,
    }

    rows = []
    for r in results:
        for name, metrics in r["models"].items():
            rows.append({
                "seed": r["seed"],
                "model": name,
                "top1": metrics["top1"],
                "top3": metrics["top3"],
                "top5": metrics["top5"],
                "top5_given_generator_hit":
                    metrics["top5_given_generator_hit"],
                "strong_top5_given_generator_hit":
                    metrics["strong_top5_given_generator_hit"],
                "mrr": metrics["mrr"],
                "generator_ceiling": metrics["generator_ceiling"],
                "external_clean_fpr":
                    r["external_clean_fpr"][name],
                "oracle_conditional_top5":
                    r["oracle_conditional_top5"],
                "gap_closure":
                    0.0 if name == "static"
                    else r["gap_closure"][name],
                "source_overlap_count":
                    r["source_overlap_count"],
            })
    pd.DataFrame(rows).to_csv(out/"comparison.csv", index=False)

    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
