"""CIPI Vocal Resonance v0.4R.7 identifiability / causal-oracle audit.

Research only. No production DSP and no raw audio persistence.

Purpose:
Determine whether current candidate objects are causally identifiable when a
paired clean reference is available during research.

Compare:
1) simple local-prominence baseline;
2) frozen single-view static R2-style ranker;
3) research-only paired clean/injected delta oracle.

The oracle is intentionally NOT available to the final plugin. Its role is to
estimate an upper bound on candidate separability and diagnose whether the main
blocker is single-view feature information versus candidate/label alignment.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
R5_PATH = HERE / "temporal_morphology_ranker.py"
spec = importlib.util.spec_from_file_location("r5_oracle_base", R5_PATH)
r5 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r5)
r3 = r5.r3

SEEDS = [20261003, 20261013]

ORACLE_FEATURES = [
    "delta_local_score",
    "delta_log_score",
    "delta_persistence",
    "delta_q80",
    "delta_variability",
    "delta_norm_q",
    "rank_improvement",
    "frequency_match_norm",
    "new_candidate",
]


def add_oracle_features(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["norm_q"] = (
        frame["candidate_hz"] / frame["local_width_hz"].clip(lower=1.0)
    )
    out = []

    clean_groups = {
        (str(g.singer.iloc[0]), str(g.source_name.iloc[0])): g.copy()
        for _, g in frame[frame.is_clean == 1].groupby("case_id")
    }

    for _, row in frame.iterrows():
        d = row.to_dict()
        if int(row.is_clean) == 1:
            for name in ORACLE_FEATURES:
                d[name] = 0.0
            out.append(d)
            continue

        key = (str(row.singer), str(row.source_name))
        clean = clean_groups.get(key)
        if clean is None or len(clean) == 0:
            nearest = None
        else:
            distances = np.abs(
                clean.candidate_hz.to_numpy(dtype=float)
                - float(row.candidate_hz)
            )
            idx = int(np.argmin(distances))
            tol = max(70.0, 0.025 * float(row.candidate_hz))
            nearest = clean.iloc[idx] if float(distances[idx]) <= tol else None

        if nearest is None:
            d.update({
                "delta_local_score": float(row.local_score),
                "delta_log_score": float(row.log_score),
                "delta_persistence": float(row.local_persistence),
                "delta_q80": float(row.local_q80),
                "delta_variability": float(row.local_variability),
                "delta_norm_q": float(row.norm_q),
                "rank_improvement": 20.0 - float(row.candidate_rank),
                "frequency_match_norm": 1.0,
                "new_candidate": 1.0,
            })
        else:
            freq_delta = abs(
                float(row.candidate_hz) - float(nearest.candidate_hz)
            )
            d.update({
                "delta_local_score": float(row.local_score - nearest.local_score),
                "delta_log_score": float(row.log_score - nearest.log_score),
                "delta_persistence": float(
                    row.local_persistence - nearest.local_persistence
                ),
                "delta_q80": float(row.local_q80 - nearest.local_q80),
                "delta_variability": float(
                    row.local_variability - nearest.local_variability
                ),
                "delta_norm_q": float(row.norm_q - nearest.norm_q),
                "rank_improvement": float(
                    nearest.candidate_rank - row.candidate_rank
                ),
                "frequency_match_norm": float(
                    freq_delta / max(70.0, 0.025 * float(row.candidate_hz))
                ),
                "new_candidate": 0.0,
            })
        out.append(d)

    return pd.DataFrame(out)


def labelled(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[
        (frame.is_clean == 0)
        & ((frame.is_target == 1) | (frame.safe_negative == 1))
    ].copy()


def fit_oracle(train: pd.DataFrame, valid: pd.DataFrame):
    tr = labelled(train)
    if tr.is_target.sum() < 20 or tr.safe_negative.sum() < 50:
        raise RuntimeError("insufficient certain labels for oracle")

    weights = np.ones(len(tr), dtype=float)
    pos = tr.is_target.to_numpy() == 1
    effect = tr.physical_effect_db.fillna(0.0).to_numpy()
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
                random_state=20261031,
            )),
        ])
        pipe.fit(
            tr[ORACLE_FEATURES],
            tr.is_target,
            model__sample_weight=weights,
        )
        trial = valid.copy()
        trial["oracle_score"] = pipe.predict_proba(
            trial[ORACLE_FEATURES]
        )[:, 1]
        m = r3.rank_metrics(trial, "oracle_score")
        key = (
            m["top5_given_generator_hit"],
            m["top5_effect_gte3"] if m["top5_effect_gte3"] is not None else -1.0,
            m["mrr"],
            -cval,
        )
        trials.append((key, cval, pipe, m))

    trials.sort(key=lambda x: x[0], reverse=True)
    _, cval, pipe, valid_metrics = trials[0]
    return pipe, float(cval), valid_metrics


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


def match_diagnostics(frame: pd.DataFrame):
    injected = frame[frame.is_clean == 0]
    target = injected[injected.is_target == 1]
    safe = injected[injected.safe_negative == 1]
    return {
        "injected_candidate_rows": int(len(injected)),
        "target_rows": int(len(target)),
        "safe_negative_rows": int(len(safe)),
        "target_new_candidate_fraction": (
            float(target.new_candidate.mean()) if len(target) else None
        ),
        "safe_negative_new_candidate_fraction": (
            float(safe.new_candidate.mean()) if len(safe) else None
        ),
        "target_abs_delta_local_median": (
            float(np.median(np.abs(target.delta_local_score)))
            if len(target) else None
        ),
        "safe_abs_delta_local_median": (
            float(np.median(np.abs(safe.delta_local_score)))
            if len(safe) else None
        ),
    }


def evaluate_seed(seed: int):
    frame = add_oracle_features(r5.build_ranker_frame(seed))
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    static_pipe, static_c, _, static_test, _, _ = r5.fit_eval(
        frame, r5.STATIC_FEATURES, f"static_{seed}"
    )
    for part in [valid, test]:
        part[f"static_{seed}"] = static_pipe.predict_proba(
            part[r5.STATIC_FEATURES]
        )[:, 1]

    oracle_pipe, oracle_c, oracle_valid = fit_oracle(train, valid)
    test["oracle_score"] = oracle_pipe.predict_proba(
        test[ORACLE_FEATURES]
    )[:, 1]

    test["prominence_score"] = test["local_score"]
    prom = r3.rank_metrics(test, "prominence_score")
    oracle = r3.rank_metrics(test, "oracle_score")

    static_strong_cond, static_strong_n = strong_top5_given_hit(
        test, f"static_{seed}"
    )
    oracle_strong_cond, oracle_strong_n = strong_top5_given_hit(
        test, "oracle_score"
    )
    prom_strong_cond, prom_strong_n = strong_top5_given_hit(
        test, "prominence_score"
    )

    return {
        "seed": seed,
        "static_C": static_c,
        "oracle_C": oracle_c,
        "prominence": {
            **prom,
            "strong_top5_given_generator_hit": prom_strong_cond,
            "strong_hit_cases": prom_strong_n,
        },
        "static": {
            **static_test,
            "strong_top5_given_generator_hit": static_strong_cond,
            "strong_hit_cases": static_strong_n,
        },
        "oracle": {
            **oracle,
            "strong_top5_given_generator_hit": oracle_strong_cond,
            "strong_hit_cases": oracle_strong_n,
        },
        "oracle_validation": oracle_valid,
        "diagnostics": match_diagnostics(test),
    }


def classify(results):
    per_seed = {}
    for r in results:
        static = r["static"]["top5_given_generator_hit"]
        oracle = r["oracle"]["top5_given_generator_hit"]
        strong = r["oracle"]["strong_top5_given_generator_hit"]
        sufficient = (
            r["static"]["generator_ceiling"] >= 0.80
            and r["oracle"]["n_cases"] >= 24
            and r["diagnostics"]["target_rows"] >= 20
        )
        per_seed[str(r["seed"])] = {
            "coverage_sufficient": bool(sufficient),
            "oracle_top5_given_hit_gte_0_80": bool(oracle >= 0.80),
            "oracle_gap_vs_static_gte_0_20": bool(oracle >= static + 0.20),
            "oracle_strong_given_hit_gte_0_85": bool(
                strong is not None and strong >= 0.85
            ),
        }

    coverage = all(v["coverage_sufficient"] for v in per_seed.values())
    oracle_high = all(
        v["oracle_top5_given_hit_gte_0_80"]
        and v["oracle_strong_given_hit_gte_0_85"]
        for v in per_seed.values()
    )
    gap_high = all(
        v["oracle_gap_vs_static_gte_0_20"]
        for v in per_seed.values()
    )

    if coverage and oracle_high and gap_high:
        route = "SINGLE_VIEW_FEATURE_INFORMATION_GAP"
    elif coverage and not oracle_high:
        route = "CANDIDATE_ALIGNMENT_OR_LABEL_LIMIT"
    else:
        route = "AUDIT_COVERAGE_INSUFFICIENT"

    return per_seed, route, coverage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results = [evaluate_seed(seed) for seed in SEEDS]
    criteria, route, coverage = classify(results)

    rows = []
    for r in results:
        for model in ["prominence", "static", "oracle"]:
            m = r[model]
            rows.append({
                "seed": r["seed"],
                "model": model,
                "top1": m["top1"],
                "top3": m["top3"],
                "top5": m["top5"],
                "top5_given_generator_hit": m["top5_given_generator_hit"],
                "strong_top5": m["top5_effect_gte3"],
                "strong_top5_given_generator_hit": m[
                    "strong_top5_given_generator_hit"
                ],
                "mrr": m["mrr"],
                "generator_ceiling": m["generator_ceiling"],
            })
    pd.DataFrame(rows).to_csv(out/"comparison.csv", index=False)

    diag_rows = []
    for r in results:
        diag_rows.append({"seed": r["seed"], **r["diagnostics"]})
    pd.DataFrame(diag_rows).to_csv(out/"diagnostics.csv", index=False)

    summary = {
        "experiment": "VOCAL_RESONANCE_R7_IDENTIFIABILITY_ORACLE",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "oracle_is_research_only": True,
        "per_seed": {str(r["seed"]): r for r in results},
        "diagnostic_gate": {
            "accepted": bool(coverage),
            "route": route,
            "criteria": criteria,
            "meaning": (
                "Acceptance means the audit has enough coverage to diagnose the "
                "next research direction. It is not product or knowledge promotion."
            ),
        },
        "raw_audio_persisted": False,
    }

    (out/"summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
