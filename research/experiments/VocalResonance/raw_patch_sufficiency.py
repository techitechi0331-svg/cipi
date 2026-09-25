"""CIPI Vocal Resonance v0.4R.12 raw 2D patch sufficiency audit.

Research only. No production DSP and no raw audio / raw patch persistence.

R7 proved that paired causal information can identify the injected target.
R8-R11 showed that several hand-crafted single-view summaries did not recover
that information robustly.

R12 asks a narrower representation question:
Does a candidate-centered, normalized local-residual time-frequency patch
contain useful single-view information that those summaries discarded?

Models:
1) frozen static R2-style baseline;
2) raw-patch linear logistic model;
3) static + raw-patch linear logistic model;
4) tiny one-hidden-layer MLP as a diagnostic nonlinear upper bound only.

The MLP is NOT a product architecture decision.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
R8_PATH = HERE / "local_patch_proxy.py"
spec = importlib.util.spec_from_file_location("r8_rawpatch_base", R8_PATH)
r8 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r8)

r3 = r8.r3
reaudit = r8.reaudit

SEEDS = [20261003, 20261013]
TIME_BINS = 10
FREQ_POINTS = 11
FREQ_LOG2_OFFSETS = np.linspace(-0.14, 0.14, FREQ_POINTS)

PATCH_FEATURES = [
    f"patch_mean_t{t:02d}_f{k:02d}"
    for t in range(TIME_BINS)
    for k in range(FREQ_POINTS)
] + [
    f"patch_occ_t{t:02d}_f{k:02d}"
    for t in range(TIME_BINS)
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


def nearest_index(f: np.ndarray, hz: float) -> int:
    return int(np.argmin(np.abs(f - hz)))


def candidate_patch(
    f: np.ndarray,
    local_frames: np.ndarray,
    idx: int,
) -> dict[str, float]:
    fc = float(f[idx])
    sample_hz = fc * np.power(2.0, FREQ_LOG2_OFFSETS)
    sample_hz = np.clip(sample_hz, float(f[0]), float(f[-1]))
    freq_idx = [nearest_index(f, float(hz)) for hz in sample_hz]

    patch = np.asarray(local_frames[:, freq_idx], dtype=float)
    patch = np.clip(patch, 0.0, 8.0)

    chunks = np.array_split(np.arange(len(patch)), TIME_BINS)
    mean_rows = []
    occ_rows = []

    for chunk in chunks:
        if len(chunk) == 0:
            mean_vec = np.zeros(FREQ_POINTS, dtype=float)
            occ_vec = np.zeros(FREQ_POINTS, dtype=float)
        else:
            seg = patch[chunk, :]
            mean_vec = np.mean(seg, axis=0)
            med = float(np.median(mean_vec))
            mad = float(np.median(np.abs(mean_vec - med))) + 0.25
            mean_vec = (mean_vec - med) / (1.4826 * mad)
            occ_vec = np.mean(seg > 1.0, axis=0)

        mean_rows.append(mean_vec)
        occ_rows.append(occ_vec)

    mean_flat = np.concatenate(mean_rows)
    occ_flat = np.concatenate(occ_rows)

    out: dict[str, float] = {}
    n = 0
    for t in range(TIME_BINS):
        for k in range(FREQ_POINTS):
            out[f"patch_mean_t{t:02d}_f{k:02d}"] = float(mean_flat[n])
            n += 1
    n = 0
    for t in range(TIME_BINS):
        for k in range(FREQ_POINTS):
            out[f"patch_occ_t{t:02d}_f{k:02d}"] = float(occ_flat[n])
            n += 1
    return out


def extract_candidates_rawpatch(x, f0_t, f0, f0_conf):
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
        row.update(candidate_patch(f, local_frames, idx))
        rows.append(row)

    return rows, f, mag


def build_ranker_frame(seed: int) -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_rawpatch
    frame = r3.build_dataset(seed, 2)
    return r3.add_relative(frame)


def build_external_clean_frame() -> pd.DataFrame:
    r3.extract_candidates = extract_candidates_rawpatch
    examples, _, _ = reaudit.collect_examples(10, 5000)
    rows = []
    for ex in examples:
        x = ex["audio"]
        f0_t, f0, f0_conf = r3.estimate_f0_track(x)
        candidates, _, _ = extract_candidates_rawpatch(
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


def fit_mlp(train: pd.DataFrame, features: list[str], seed: int):
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
    weights[positive] *= np.clip(effect[positive] / 3.0, 0.25, 2.0)

    pipe = Pipeline([
        ("scale", StandardScaler()),
        ("mlp", MLPClassifier(
            hidden_layer_sizes=(24,),
            activation="tanh",
            solver="adam",
            alpha=0.05,
            batch_size=64,
            learning_rate_init=0.001,
            max_iter=250,
            tol=1e-4,
            random_state=seed,
        )),
    ])
    pipe.fit(
        labelled[features],
        y,
        mlp__sample_weight=weights,
    )
    return pipe


def add_strong_metric(frame, score_col, metrics):
    strong, n = r8.strong_top5_given_hit(frame, score_col)
    metrics["strong_top5_given_generator_hit"] = strong
    metrics["strong_hit_cases"] = n


def choose_threshold(valid, score_col):
    return r8.choose_threshold(valid, score_col)


def clean_fpr(frame, score_col, threshold):
    return r8.clean_fpr(frame, score_col, threshold)


def model_metrics(test, score_col):
    m = r3.rank_metrics(test, score_col)
    add_strong_metric(test, score_col, m)
    return m


def evaluate_seed(seed: int, external: pd.DataFrame):
    frame = build_ranker_frame(seed)
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    static_pipe, static_c, static_valid = r8.fit_model(
        train, valid, list(r3.STATIC_FEATURES), seed
    )
    patch_pipe, patch_c, patch_valid = r8.fit_model(
        train, valid, PATCH_FEATURES, seed + 121
    )
    combined_pipe, combined_c, combined_valid = r8.fit_model(
        train, valid, COMBINED_FEATURES, seed + 122
    )
    mlp_pipe = fit_mlp(train, COMBINED_FEATURES, seed + 123)

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

    static = model_metrics(test, "static_score")
    patch_linear = model_metrics(test, "patch_linear_score")
    combined_linear = model_metrics(test, "combined_linear_score")
    tiny_mlp = model_metrics(test, "tiny_mlp_score")

    thresholds = {
        "static": choose_threshold(valid, "static_score"),
        "patch_linear": choose_threshold(valid, "patch_linear_score"),
        "combined_linear": choose_threshold(valid, "combined_linear_score"),
        "tiny_mlp": choose_threshold(valid, "tiny_mlp_score"),
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

    fprs = {
        "static": clean_fpr(ext, "static_score", thresholds["static"]),
        "patch_linear": clean_fpr(
            ext, "patch_linear_score", thresholds["patch_linear"]
        ),
        "combined_linear": clean_fpr(
            ext, "combined_linear_score", thresholds["combined_linear"]
        ),
        "tiny_mlp": clean_fpr(
            ext, "tiny_mlp_score", thresholds["tiny_mlp"]
        ),
    }

    oracle = R7_ORACLE_COND_TOP5[seed]
    static_cond = static["top5_given_generator_hit"]
    denom = max(oracle - static_cond, 1e-9)

    def closure(m):
        return float(
            (m["top5_given_generator_hit"] - static_cond) / denom
        )

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
        "static_test": static,
        "patch_linear_test": patch_linear,
        "combined_linear_test": combined_linear,
        "tiny_mlp_test": tiny_mlp,
        "oracle_conditional_top5": oracle,
        "oracle_strong_conditional_top5":
            R7_ORACLE_STRONG_COND_TOP5[seed],
        "gap_closure_patch_linear": closure(patch_linear),
        "gap_closure_combined_linear": closure(combined_linear),
        "gap_closure_tiny_mlp": closure(tiny_mlp),
        "external_clean_fpr": fprs,
        "external_clean_n": int(ext.case_id.nunique()),
        "source_overlap_count": len(overlap),
    }


def model_pass(result: dict, model_key: str, closure_key: str) -> dict:
    static = result["static_test"]
    model = result[model_key]
    fpr_name = {
        "patch_linear_test": "patch_linear",
        "combined_linear_test": "combined_linear",
        "tiny_mlp_test": "tiny_mlp",
    }[model_key]
    return {
        "conditional_top5_improves_by_0_08": bool(
            model["top5_given_generator_hit"]
            >= static["top5_given_generator_hit"] + 0.08
        ),
        "oracle_gap_closure_gte_0_15": bool(
            result[closure_key] >= 0.15
        ),
        "strong_conditional_top5_not_worse_by_0_05": bool(
            model["strong_top5_given_generator_hit"] is not None
            and static["strong_top5_given_generator_hit"] is not None
            and model["strong_top5_given_generator_hit"]
            >= static["strong_top5_given_generator_hit"] - 0.05
        ),
        "external_clean_fpr_not_worse_by_0_05": bool(
            result["external_clean_fpr"][fpr_name]
            <= result["external_clean_fpr"]["static"] + 0.05
        ),
        "generator_ceiling_gte_0_80": bool(
            model["generator_ceiling"] >= 0.80
        ),
        "zero_source_overlap": bool(
            result["source_overlap_count"] == 0
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

    linear_criteria = {}
    nonlinear_criteria = {}
    for r in results:
        seed = str(r["seed"])
        linear_criteria[seed] = model_pass(
            r,
            "combined_linear_test",
            "gap_closure_combined_linear",
        )
        nonlinear_criteria[seed] = model_pass(
            r,
            "tiny_mlp_test",
            "gap_closure_tiny_mlp",
        )

    linear_pass = all(
        all(v.values()) for v in linear_criteria.values()
    )
    nonlinear_pass = all(
        all(v.values()) for v in nonlinear_criteria.values()
    )

    if linear_pass:
        route = "RAW_PATCH_LINEAR_INFORMATION_PRESENT"
    elif nonlinear_pass:
        route = "RAW_PATCH_NONLINEAR_INFORMATION_PRESENT"
    else:
        route = "RAW_PATCH_INFORMATION_NOT_ESTABLISHED"

    summary = {
        "experiment": "VOCAL_RESONANCE_R12_RAW_PATCH_SUFFICIENCY",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "patch_shape": {
            "time_bins": TIME_BINS,
            "frequency_points": FREQ_POINTS,
            "channels": ["normalized_mean_local_residual", "occupancy_gt_1"],
            "feature_count": len(PATCH_FEATURES),
        },
        "raw_patch_persisted": False,
        "per_seed": {str(r["seed"]): r for r in results},
        "diagnostic_gate": {
            "accepted": bool(linear_pass or nonlinear_pass),
            "route": route,
            "linear_criteria": linear_criteria,
            "nonlinear_criteria": nonlinear_criteria,
            "meaning": (
                "Whether candidate-centered raw local-residual patches contain "
                "deployable single-view information discarded by prior summaries. "
                "The tiny MLP is diagnostic only."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "R12 is a representation sufficiency audit. A diagnostic MLP "
                "result is not a product architecture approval."
            ),
        },
        "raw_audio_persisted": False,
    }

    rows = []
    for r in results:
        for model, metrics, fpr, closure in [
            (
                "static",
                r["static_test"],
                r["external_clean_fpr"]["static"],
                0.0,
            ),
            (
                "patch_linear",
                r["patch_linear_test"],
                r["external_clean_fpr"]["patch_linear"],
                r["gap_closure_patch_linear"],
            ),
            (
                "combined_linear",
                r["combined_linear_test"],
                r["external_clean_fpr"]["combined_linear"],
                r["gap_closure_combined_linear"],
            ),
            (
                "tiny_mlp",
                r["tiny_mlp_test"],
                r["external_clean_fpr"]["tiny_mlp"],
                r["gap_closure_tiny_mlp"],
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
                "gap_closure": closure,
                "source_overlap_count": r["source_overlap_count"],
            })
    pd.DataFrame(rows).to_csv(out/"comparison.csv", index=False)

    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
