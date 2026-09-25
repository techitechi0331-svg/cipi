"""CIPI Vocal Resonance v0.4R.10 singer-disjoint clean normative prior.

Research only. No production suppressor DSP and no raw vocal persistence.

Purpose:
Test whether a lightweight prior learned ONLY from clean training singers can
provide deployable information that local single-view features lacked in R8/R9.

At inference, the plugin would need only:
- the current audio candidate features;
- frozen prior statistics learned offline from clean vocals.

No paired clean reference is used at inference.

Comparisons:
1. prominence-only;
2. frozen static R2-style ranker;
3. static ranker + clean normative-prior features;
4. prior-only anomaly score (diagnostic only).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
R5_PATH = HERE / "temporal_morphology_ranker.py"
spec = importlib.util.spec_from_file_location("r5_prior_base", R5_PATH)
r5 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r5)
r3 = r5.r3

SEEDS = [20261003, 20261013]
N_BINS = 8

PRIOR_SOURCE_FEATURES = [
    "local_score",
    "log_score",
    "local_persistence",
    "local_q80",
    "norm_q",
    "prom_x_persist",
    "local_minus_log",
    "cross_agreement",
]

PRIOR_FEATURES = [
    *(f"prior_z_{x}" for x in PRIOR_SOURCE_FEATURES),
    "prior_pos_l2",
    "prior_abs_l2",
    "prior_max_pos",
]

COMBINED_FEATURES = list(r3.STATIC_FEATURES) + PRIOR_FEATURES

R7_ORACLE_COND_TOP5 = {
    20261003: 1.0,
    20261013: 0.9259259259259259,
}
R7_ORACLE_STRONG_COND_TOP5 = {
    20261003: 1.0,
    20261013: 1.0,
}


@dataclass
class BinStats:
    lo: float
    hi: float
    medians: dict[str, float]
    scales: dict[str, float]
    n: int


def robust_scale(values: np.ndarray) -> tuple[float, float]:
    x = np.asarray(values, dtype=float)
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med)))
    scale = max(1.4826 * mad, 1e-3)
    return med, scale


def fit_clean_prior(train: pd.DataFrame):
    clean = train[train.is_clean == 1].copy()
    singers = sorted(set(clean.singer.astype(str)))
    expected = sorted(r3.TRAIN_SINGERS)
    if singers != expected:
        raise RuntimeError(
            f"prior singer leakage/mismatch: got={singers}, expected={expected}"
        )

    q = np.linspace(0.0, 1.0, N_BINS + 1)
    edges = np.quantile(clean.log_frequency.to_numpy(dtype=float), q)
    edges[0] = -np.inf
    edges[-1] = np.inf

    global_stats = {}
    for feature in PRIOR_SOURCE_FEATURES:
        global_stats[feature] = robust_scale(
            clean[feature].to_numpy(dtype=float)
        )

    bins: list[BinStats] = []
    for i in range(N_BINS):
        lo = float(edges[i])
        hi = float(edges[i + 1])
        if i == N_BINS - 1:
            mask = (clean.log_frequency >= lo) & (clean.log_frequency <= hi)
        else:
            mask = (clean.log_frequency >= lo) & (clean.log_frequency < hi)
        g = clean[mask]
        medians = {}
        scales = {}
        for feature in PRIOR_SOURCE_FEATURES:
            if len(g) >= 30:
                med, scale = robust_scale(g[feature].to_numpy(dtype=float))
            else:
                med, scale = global_stats[feature]
            medians[feature] = med
            scales[feature] = scale
        bins.append(BinStats(lo, hi, medians, scales, int(len(g))))

    return {
        "singers": singers,
        "edges": [float(x) for x in edges],
        "bins": bins,
        "clean_rows": int(len(clean)),
    }


def find_bin(prior, log_frequency: float) -> BinStats:
    for b in prior["bins"]:
        if log_frequency >= b.lo and log_frequency < b.hi:
            return b
    return prior["bins"][-1]


def apply_clean_prior(frame: pd.DataFrame, prior) -> pd.DataFrame:
    frame = frame.copy()
    z_matrix = []

    for _, row in frame.iterrows():
        b = find_bin(prior, float(row.log_frequency))
        zs = []
        for feature in PRIOR_SOURCE_FEATURES:
            z = (
                float(row[feature]) - b.medians[feature]
            ) / b.scales[feature]
            z = float(np.clip(z, -8.0, 8.0))
            zs.append(z)
        z_matrix.append(zs)

    zmat = np.asarray(z_matrix, dtype=float)
    for j, feature in enumerate(PRIOR_SOURCE_FEATURES):
        frame[f"prior_z_{feature}"] = zmat[:, j]

    pos = np.maximum(zmat, 0.0)
    frame["prior_pos_l2"] = np.sqrt(np.mean(pos * pos, axis=1))
    frame["prior_abs_l2"] = np.sqrt(np.mean(zmat * zmat, axis=1))
    frame["prior_max_pos"] = np.max(pos, axis=1)
    return frame


def fit_model(train, valid, features, seed):
    labelled = r3.labelled(train)
    if labelled.is_target.sum() < 20 or labelled.safe_negative.sum() < 50:
        raise RuntimeError("insufficient certain labels")

    weights = np.ones(len(labelled), dtype=float)
    pos = labelled.is_target.to_numpy() == 1
    effect = labelled.physical_effect_db.fillna(0.0).to_numpy()
    weights[pos] = np.clip(effect[pos] / 3.0, 0.25, 2.0)

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
            m["top5_effect_gte3"]
            if m["top5_effect_gte3"] is not None else -1.0,
            m["mrr"],
            -cval,
        )
        trials.append((key, cval, pipe, m))

    trials.sort(key=lambda x: x[0], reverse=True)
    _, cval, pipe, metrics = trials[0]
    return pipe, float(cval), metrics


def strong_top5_given_hit(frame, score_col):
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


def choose_threshold(valid, score_col):
    clean = valid[valid.is_clean == 1]
    maxima = clean.groupby("case_id")[score_col].max().to_numpy()
    return float(np.quantile(maxima, 0.95)) if len(maxima) else float("inf")


def clean_fpr(frame, score_col, threshold):
    maxima = frame.groupby("case_id")[score_col].max()
    return float(np.mean(maxima > threshold)) if len(maxima) else 0.0


def evaluate_seed(seed: int, external_raw: pd.DataFrame):
    frame = r5.build_ranker_frame(seed)
    train_raw = frame[frame.split == "train"].copy()
    valid_raw = frame[frame.split == "valid"].copy()
    test_raw = frame[frame.split == "test"].copy()

    prior = fit_clean_prior(train_raw)
    train = apply_clean_prior(train_raw, prior)
    valid = apply_clean_prior(valid_raw, prior)
    test = apply_clean_prior(test_raw, prior)
    external = apply_clean_prior(external_raw, prior)

    static_pipe, static_c, static_valid = fit_model(
        train, valid, list(r3.STATIC_FEATURES), seed
    )
    combined_pipe, combined_c, combined_valid = fit_model(
        train, valid, COMBINED_FEATURES, seed + 101
    )

    for part in [valid, test]:
        part["static_score"] = static_pipe.predict_proba(
            part[r3.STATIC_FEATURES]
        )[:, 1]
        part["combined_score"] = combined_pipe.predict_proba(
            part[COMBINED_FEATURES]
        )[:, 1]
        part["prior_only_score"] = part["prior_pos_l2"]

    static = r3.rank_metrics(test, "static_score")
    combined = r3.rank_metrics(test, "combined_score")
    prior_only = r3.rank_metrics(test, "prior_only_score")

    for name, metrics in [
        ("static_score", static),
        ("combined_score", combined),
        ("prior_only_score", prior_only),
    ]:
        strong, n = strong_top5_given_hit(test, name)
        metrics["strong_top5_given_generator_hit"] = strong
        metrics["strong_hit_cases"] = n

    static_th = choose_threshold(valid, "static_score")
    combined_th = choose_threshold(valid, "combined_score")
    prior_th = choose_threshold(valid, "prior_only_score")

    external["static_score"] = static_pipe.predict_proba(
        external[r3.STATIC_FEATURES]
    )[:, 1]
    external["combined_score"] = combined_pipe.predict_proba(
        external[COMBINED_FEATURES]
    )[:, 1]
    external["prior_only_score"] = external["prior_pos_l2"]

    static_fpr = clean_fpr(external, "static_score", static_th)
    combined_fpr = clean_fpr(external, "combined_score", combined_th)
    prior_fpr = clean_fpr(external, "prior_only_score", prior_th)

    oracle = R7_ORACLE_COND_TOP5[seed]
    static_cond = static["top5_given_generator_hit"]
    combined_cond = combined["top5_given_generator_hit"]
    gap = max(oracle - static_cond, 1e-9)
    gap_closure = float((combined_cond - static_cond) / gap)

    return {
        "seed": seed,
        "prior_fit_singers": prior["singers"],
        "prior_clean_rows": prior["clean_rows"],
        "prior_bin_counts": [b.n for b in prior["bins"]],
        "static_C": static_c,
        "combined_C": combined_c,
        "static_validation": static_valid,
        "combined_validation": combined_valid,
        "static_test": static,
        "combined_test": combined,
        "prior_only_test": prior_only,
        "oracle_conditional_top5": oracle,
        "oracle_strong_conditional_top5":
            R7_ORACLE_STRONG_COND_TOP5[seed],
        "conditional_top5_gap_closure": gap_closure,
        "external_clean_static_fpr": static_fpr,
        "external_clean_combined_fpr": combined_fpr,
        "external_clean_prior_only_fpr": prior_fpr,
        "external_clean_n": int(external.case_id.nunique()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    external = r5.external_clean_frame()
    results = [evaluate_seed(seed, external) for seed in SEEDS]

    criteria = {}
    for r in results:
        static = r["static_test"]
        combined = r["combined_test"]
        seed = str(r["seed"])
        criteria[seed] = {
            "prior_fit_train_singers_only": bool(
                sorted(r["prior_fit_singers"]) == sorted(r3.TRAIN_SINGERS)
            ),
            "conditional_top5_improves_by_0_08": bool(
                combined["top5_given_generator_hit"]
                >= static["top5_given_generator_hit"] + 0.08
            ),
            "oracle_gap_closure_gte_0_15": bool(
                r["conditional_top5_gap_closure"] >= 0.15
            ),
            "strong_conditional_top5_not_worse_by_0_05": bool(
                combined["strong_top5_given_generator_hit"] is not None
                and static["strong_top5_given_generator_hit"] is not None
                and combined["strong_top5_given_generator_hit"]
                    >= static["strong_top5_given_generator_hit"] - 0.05
            ),
            "external_clean_fpr_not_worse_by_0_025": bool(
                r["external_clean_combined_fpr"]
                <= r["external_clean_static_fpr"] + 0.025
            ),
            "generator_ceiling_gte_0_80": bool(
                combined["generator_ceiling"] >= 0.80
            ),
        }

    retention = all(all(v.values()) for v in criteria.values())

    summary = {
        "experiment": "VOCAL_RESONANCE_R10_CLEAN_NORMATIVE_PRIOR",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "prior_source_features": PRIOR_SOURCE_FEATURES,
        "prior_feature_names": PRIOR_FEATURES,
        "prior_frequency_bins": N_BINS,
        "per_seed": {str(r["seed"]): r for r in results},
        "retention_gate": {
            "accepted": bool(retention),
            "criteria": criteria,
            "meaning": (
                "Whether a clean-trained singer-disjoint normative prior is worth "
                "retaining as deployable single-view context. Passing is not a "
                "product gate."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "R10 tests a new information source against the R7 oracle gap. "
                "Existing product ranking criteria remain downstream."
            ),
        },
        "raw_audio_persisted": False,
    }

    rows = []
    for r in results:
        for model, m, fpr in [
            ("static", r["static_test"], r["external_clean_static_fpr"]),
            ("combined_clean_prior", r["combined_test"],
             r["external_clean_combined_fpr"]),
            ("prior_only", r["prior_only_test"],
             r["external_clean_prior_only_fpr"]),
        ]:
            rows.append({
                "seed": r["seed"],
                "model": model,
                "top1": m["top1"],
                "top3": m["top3"],
                "top5": m["top5"],
                "top5_given_generator_hit":
                    m["top5_given_generator_hit"],
                "strong_top5_given_generator_hit":
                    m["strong_top5_given_generator_hit"],
                "mrr": m["mrr"],
                "generator_ceiling": m["generator_ceiling"],
                "external_clean_fpr": fpr,
                "oracle_conditional_top5":
                    r["oracle_conditional_top5"],
                "gap_closure": (
                    r["conditional_top5_gap_closure"]
                    if model == "combined_clean_prior" else 0.0
                ),
            })
    pd.DataFrame(rows).to_csv(out/"comparison.csv", index=False)

    prior_rows = []
    for r in results:
        for i, n in enumerate(r["prior_bin_counts"]):
            prior_rows.append({
                "seed": r["seed"],
                "bin": i,
                "clean_train_rows": n,
            })
    pd.DataFrame(prior_rows).to_csv(
        out/"prior_bin_counts.csv", index=False
    )

    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
