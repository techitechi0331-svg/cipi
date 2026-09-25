"""CIPI Vocal Resonance v0.4R.5b morphology stability / ablation audit.

Research only. No product DSP and no raw vocal audio persistence.

This audit attacks the positive R5 abstention result by testing:
- ranker/external-clean source-basename overlap;
- two controlled injection seeds;
- run-length-only and distribution-only morphology ablations;
- full morphology with independently tuned C;
- full morphology forced to the static ranker's selected C;
- paired external-clean false-trigger differences with bootstrap intervals.
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
spec = importlib.util.spec_from_file_location("r5_stability_base", R5_PATH)
r5 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r5)
r3 = r5.r3

RUN_FEATURES = r5.STATIC_FEATURES + [
    "rel_longest_active_run_frac",
    "rel_active_run_count_norm",
    "rel_median_active_run_frac",
]
DIST_FEATURES = r5.STATIC_FEATURES + [
    "rel_temporal_entropy",
    "rel_top10_temporal_concentration",
]
FULL_FEATURES = list(r5.MORPH_FEATURES)


def fit_with_c(frame: pd.DataFrame, features: list[str], cval: float, score_name: str):
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    tr = r3.labelled(train)
    if tr.is_target.sum() < 20 or tr.safe_negative.sum() < 50:
        raise RuntimeError("insufficient certain labels")

    weights = np.ones(len(tr), dtype=float)
    pos = tr.is_target.to_numpy() == 1
    eff = tr.physical_effect_db.fillna(0.0).to_numpy()
    weights[pos] = np.clip(eff[pos] / 3.0, 0.25, 2.0)

    pipe = Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=float(cval),
            class_weight="balanced",
            max_iter=3000,
            solver="lbfgs",
            random_state=20260929,
        )),
    ])
    pipe.fit(tr[features], tr.is_target, model__sample_weight=weights)

    valid[score_name] = pipe.predict_proba(valid[features])[:, 1]
    test[score_name] = pipe.predict_proba(test[features])[:, 1]
    threshold = r3.choose_threshold(valid, score_name)

    metrics = r3.rank_metrics(test, score_name)
    metrics["clean_false_trigger"] = r3.clean_false(test, score_name, threshold)
    metrics["threshold_from_valid_95pct"] = threshold

    coef = pd.DataFrame({
        "feature": features,
        "coefficient": pipe.named_steps["model"].coef_[0],
        "model": score_name,
    })
    return pipe, metrics, threshold, coef


def paired_external(static_cases: pd.DataFrame, candidate_cases: pd.DataFrame, seed: int):
    left = static_cases[["case_id", "false_trigger"]].rename(
        columns={"false_trigger": "static_trigger"}
    )
    right = candidate_cases[["case_id", "false_trigger"]].rename(
        columns={"false_trigger": "candidate_trigger"}
    )
    pair = left.merge(right, on="case_id", how="inner")
    delta = (
        pair.candidate_trigger.astype(float)
        - pair.static_trigger.astype(float)
    ).to_numpy()

    rng = np.random.default_rng(seed)
    boots = []
    if len(delta):
        for _ in range(5000):
            idx = rng.integers(0, len(delta), len(delta))
            boots.append(float(np.mean(delta[idx])))

    improvements = int(np.sum(
        (pair.static_trigger == 1) & (pair.candidate_trigger == 0)
    ))
    regressions = int(np.sum(
        (pair.static_trigger == 0) & (pair.candidate_trigger == 1)
    ))
    return {
        "n": int(len(pair)),
        "candidate_minus_static_fpr": float(np.mean(delta)) if len(delta) else None,
        "bootstrap_lo": float(np.quantile(boots, 0.025)) if boots else None,
        "bootstrap_hi": float(np.quantile(boots, 0.975)) if boots else None,
        "improvements": improvements,
        "regressions": regressions,
    }


def evaluate_seed(seed: int, external: pd.DataFrame):
    frame = r5.build_ranker_frame(seed)

    rank_sources = set(frame.source_name.astype(str).unique())
    external_sources = set(external.source_name.astype(str).unique())
    overlap = sorted(rank_sources & external_sources)

    static_pipe, static_c, _, static_test, static_th, static_coef = r5.fit_eval(
        frame, r5.STATIC_FEATURES, f"static_{seed}"
    )
    run_pipe, run_c, _, run_test, run_th, run_coef = r5.fit_eval(
        frame, RUN_FEATURES, f"run_{seed}"
    )
    dist_pipe, dist_c, _, dist_test, dist_th, dist_coef = r5.fit_eval(
        frame, DIST_FEATURES, f"dist_{seed}"
    )
    full_pipe, full_c, _, full_test, full_th, full_coef = r5.fit_eval(
        frame, FULL_FEATURES, f"full_{seed}"
    )
    same_pipe, same_test, same_th, same_coef = fit_with_c(
        frame, FULL_FEATURES, static_c, f"full_same_c_{seed}"
    )

    ext_static = r5.external_clean_metrics(
        external, static_pipe, r5.STATIC_FEATURES, f"static_{seed}", static_th
    )
    ext_run = r5.external_clean_metrics(
        external, run_pipe, RUN_FEATURES, f"run_{seed}", run_th
    )
    ext_dist = r5.external_clean_metrics(
        external, dist_pipe, DIST_FEATURES, f"dist_{seed}", dist_th
    )
    ext_full = r5.external_clean_metrics(
        external, full_pipe, FULL_FEATURES, f"full_{seed}", full_th
    )
    ext_same = r5.external_clean_metrics(
        external, same_pipe, FULL_FEATURES, f"full_same_c_{seed}", same_th
    )

    paired_full = paired_external(ext_static["cases"], ext_full["cases"], seed + 1000)
    paired_same = paired_external(ext_static["cases"], ext_same["cases"], seed + 2000)

    models = {
        "static": (static_c, static_test, ext_static["overall_false_trigger"]),
        "run_only": (run_c, run_test, ext_run["overall_false_trigger"]),
        "dist_only": (dist_c, dist_test, ext_dist["overall_false_trigger"]),
        "full": (full_c, full_test, ext_full["overall_false_trigger"]),
        "full_same_c": (static_c, same_test, ext_same["overall_false_trigger"]),
    }

    rows = []
    for name, (cval, tm, ext_fpr) in models.items():
        rows.append({
            "seed": seed,
            "model": name,
            "C": cval,
            "top3": tm["top3"],
            "top5": tm["top5"],
            "mrr": tm["mrr"],
            "strong_top5": tm["top5_effect_gte3"],
            "internal_clean_false": tm["clean_false_trigger"],
            "external_clean_false": ext_fpr,
        })

    coeff = pd.concat([
        static_coef.assign(seed=seed, variant="static"),
        run_coef.assign(seed=seed, variant="run_only"),
        dist_coef.assign(seed=seed, variant="dist_only"),
        full_coef.assign(seed=seed, variant="full"),
        same_coef.assign(seed=seed, variant="full_same_c"),
    ], ignore_index=True)

    overlap_rows = pd.DataFrame(
        [{"seed": seed, "source_basename": value} for value in overlap],
        columns=["seed", "source_basename"],
    )
    paired_rows = pd.DataFrame([
        {"seed": seed, "variant": "full", **paired_full},
        {"seed": seed, "variant": "full_same_c", **paired_same},
    ])
    return pd.DataFrame(rows), coeff, overlap_rows, paired_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    seeds = [20261003, 20261013]
    external = r5.external_clean_frame()

    rows_all = []
    coef_all = []
    overlap_all = []
    paired_all = []

    for seed in seeds:
        rows, coef, overlap, paired = evaluate_seed(seed, external)
        rows_all.append(rows)
        coef_all.append(coef)
        overlap_all.append(overlap)
        paired_all.append(paired)

    comparison = pd.concat(rows_all, ignore_index=True)
    coefficients = pd.concat(coef_all, ignore_index=True)
    overlap = pd.concat(overlap_all, ignore_index=True)
    paired = pd.concat(paired_all, ignore_index=True)

    checks = {}
    per_seed = {}

    for seed in seeds:
        g = comparison[comparison.seed == seed].set_index("model")
        p = paired[paired.seed == seed].set_index("variant")
        overlap_count = int(np.sum(overlap.seed == seed)) if len(overlap) else 0

        static_top5 = float(g.loc["static", "top5"])
        static_strong = float(g.loc["static", "strong_top5"])
        static_ext = float(g.loc["static", "external_clean_false"])

        full_top5 = float(g.loc["full", "top5"])
        full_strong = float(g.loc["full", "strong_top5"])
        full_ext = float(g.loc["full", "external_clean_false"])

        same_top5 = float(g.loc["full_same_c", "top5"])
        same_strong = float(g.loc["full_same_c", "strong_top5"])
        same_ext = float(g.loc["full_same_c", "external_clean_false"])

        seed_checks = {
            "zero_source_overlap": overlap_count == 0,
            "full_top5_not_worse": full_top5 >= static_top5,
            "full_strong_not_worse": full_strong >= static_strong,
            "full_external_fpr_minus_0_10": full_ext <= static_ext - 0.10,
            "same_c_top5_not_worse": same_top5 >= static_top5,
            "same_c_strong_not_worse": same_strong >= static_strong,
            "same_c_external_fpr_minus_0_05": same_ext <= static_ext - 0.05,
            "full_paired_ci_upper_nonpositive": float(
                p.loc["full", "bootstrap_hi"]
            ) <= 0.0,
            "same_c_paired_ci_upper_nonpositive": float(
                p.loc["full_same_c", "bootstrap_hi"]
            ) <= 0.0,
        }
        checks[str(seed)] = seed_checks
        per_seed[str(seed)] = {
            "overlap_count": overlap_count,
            "static": {
                "top5": static_top5,
                "strong_top5": static_strong,
                "external_clean_false": static_ext,
            },
            "full": {
                "top5": full_top5,
                "strong_top5": full_strong,
                "external_clean_false": full_ext,
            },
            "full_same_c": {
                "top5": same_top5,
                "strong_top5": same_strong,
                "external_clean_false": same_ext,
            },
            "checks": seed_checks,
        }

    retention = all(all(v.values()) for v in checks.values())

    summary = {
        "experiment": "VOCAL_RESONANCE_R5B_MORPH_STABILITY",
        "seeds": seeds,
        "candidate_budget": 20,
        "external_clean_n": int(external.case_id.nunique()),
        "per_seed": per_seed,
        "retention_gate": {
            "accepted": bool(retention),
            "criteria": checks,
            "meaning": (
                "Whether the R5 morphology abstention result survives source-overlap "
                "audit, a second injection seed, morphology-family ablation, a same-C "
                "control and paired external-clean uncertainty. Not a product gate."
            ),
        },
        "raw_audio_persisted": False,
    }

    comparison.to_csv(out / "comparison.csv", index=False)
    coefficients.to_csv(out / "coefficients.csv", index=False)
    overlap.to_csv(out / "source_overlap.csv", index=False)
    paired.to_csv(out / "paired_external_clean.csv", index=False)
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
