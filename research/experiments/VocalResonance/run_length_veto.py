"""CIPI Vocal Resonance v0.4R.6 run-length veto / abstention gate.

Research only. No production suppressor DSP and no raw vocal audio persistence.

The static R2-style semantic ranker is frozen and remains responsible for
candidate ordering. A separate run-length-only classifier may only veto an
action that the static ranker would otherwise take. It cannot reorder or create
new actions.

Validation chooses the veto threshold under fixed true-target retention
constraints. Locked test and independent external-clean cohorts decide whether
the veto is retained.
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
spec = importlib.util.spec_from_file_location("r5_veto_base", R5_PATH)
r5 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r5)
r3 = r5.r3

RUN_VETO_FEATURES = [
    "rel_longest_active_run_frac",
    "rel_active_run_count_norm",
    "rel_median_active_run_frac",
]
SEEDS = [20261003, 20261013]


def fit_veto_model(train: pd.DataFrame, cval: float):
    labelled = r3.labelled(train)
    if labelled.is_target.sum() < 20 or labelled.safe_negative.sum() < 50:
        raise RuntimeError("insufficient certain labels for veto")

    weights = np.ones(len(labelled), dtype=float)
    pos = labelled.is_target.to_numpy() == 1
    effect = labelled.physical_effect_db.fillna(0.0).to_numpy()
    weights[pos] = np.clip(effect[pos] / 3.0, 0.25, 2.0)

    pipe = Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=float(cval),
            class_weight="balanced",
            max_iter=3000,
            solver="lbfgs",
            random_state=20261023,
        )),
    ])
    pipe.fit(
        labelled[RUN_VETO_FEATURES],
        labelled.is_target,
        model__sample_weight=weights,
    )
    return pipe


def action_stats(frame: pd.DataFrame, static_col: str, static_threshold: float,
                 veto_col: str | None = None, veto_threshold: float = 0.0):
    work = frame[frame.is_clean == 0].copy()

    target = work[work.is_target == 1].copy()
    baseline_target = target[static_col] >= static_threshold
    if veto_col is None:
        veto_target = baseline_target
    else:
        veto_target = baseline_target & (target[veto_col] >= veto_threshold)

    strong = target[target.physical_effect_db >= 3.0].copy()
    baseline_strong = strong[static_col] >= static_threshold
    if veto_col is None:
        veto_strong = baseline_strong
    else:
        veto_strong = baseline_strong & (strong[veto_col] >= veto_threshold)

    base_target_n = int(np.sum(baseline_target))
    veto_target_n = int(np.sum(veto_target))
    base_strong_n = int(np.sum(baseline_strong))
    veto_strong_n = int(np.sum(veto_strong))

    return {
        "baseline_target_actions": base_target_n,
        "veto_target_actions": veto_target_n,
        "target_action_keep": (
            1.0 if base_target_n == 0 else veto_target_n / base_target_n
        ),
        "baseline_strong_actions": base_strong_n,
        "veto_strong_actions": veto_strong_n,
        "strong_action_keep": (
            1.0 if base_strong_n == 0 else veto_strong_n / base_strong_n
        ),
    }


def clean_case_table(frame: pd.DataFrame, static_col: str, static_threshold: float,
                     veto_col: str | None = None, veto_threshold: float = 0.0):
    clean = frame[frame.is_clean == 1].copy()
    clean["baseline_action"] = clean[static_col] >= static_threshold
    if veto_col is None:
        clean["veto_action"] = clean["baseline_action"]
    else:
        clean["veto_action"] = clean["baseline_action"] & (
            clean[veto_col] >= veto_threshold
        )

    rows = []
    for cid, g in clean.groupby("case_id"):
        rows.append({
            "case_id": cid,
            "baseline_trigger": int(g.baseline_action.any()),
            "veto_trigger": int(g.veto_action.any()),
        })
    return pd.DataFrame(rows)


def paired_bootstrap(cases: pd.DataFrame, seed: int):
    delta = (
        cases.veto_trigger.astype(float)
        - cases.baseline_trigger.astype(float)
    ).to_numpy()
    rng = np.random.default_rng(seed)
    boots = []
    if len(delta):
        for _ in range(5000):
            idx = rng.integers(0, len(delta), len(delta))
            boots.append(float(np.mean(delta[idx])))
    return {
        "n": int(len(delta)),
        "baseline_fpr": (
            float(cases.baseline_trigger.mean()) if len(cases) else None
        ),
        "veto_fpr": float(cases.veto_trigger.mean()) if len(cases) else None,
        "veto_minus_baseline": float(np.mean(delta)) if len(delta) else None,
        "bootstrap_lo": float(np.quantile(boots, 0.025)) if boots else None,
        "bootstrap_hi": float(np.quantile(boots, 0.975)) if boots else None,
        "improvements": int(np.sum(
            (cases.baseline_trigger == 1) & (cases.veto_trigger == 0)
        )),
        "regressions": int(np.sum(
            (cases.baseline_trigger == 0) & (cases.veto_trigger == 1)
        )),
    }


def choose_veto(valid: pd.DataFrame, static_col: str, static_threshold: float):
    best = None
    for cval in [0.03, 0.1, 0.3, 1.0, 3.0]:
        model = fit_veto_model(valid[valid.split == "train"], cval) if False else None

    raise AssertionError("choose_veto must be called through select_model_threshold")


def select_model_threshold(train: pd.DataFrame, valid: pd.DataFrame,
                           static_col: str, static_threshold: float):
    candidates = []
    for cval in [0.03, 0.1, 0.3, 1.0, 3.0]:
        model = fit_veto_model(train, cval)
        trial = valid.copy()
        trial["veto_score"] = model.predict_proba(
            trial[RUN_VETO_FEATURES]
        )[:, 1]

        probs = trial.veto_score.to_numpy()
        thresholds = sorted(set(
            [0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
            + [float(x) for x in np.quantile(probs, [0.25, 0.5, 0.75, 0.9])]
        ))

        for threshold in thresholds:
            act = action_stats(
                trial, static_col, static_threshold,
                "veto_score", threshold
            )
            if act["target_action_keep"] < 0.95:
                continue
            if act["strong_action_keep"] < 0.95:
                continue
            clean = clean_case_table(
                trial, static_col, static_threshold,
                "veto_score", threshold
            )
            fpr = float(clean.veto_trigger.mean()) if len(clean) else 1.0
            key = (fpr, -threshold, cval)
            candidates.append((key, cval, threshold, model, act, fpr))

    if not candidates:
        raise RuntimeError("No validation veto threshold met 95% target retention.")

    candidates.sort(key=lambda x: x[0])
    _, cval, threshold, model, act, fpr = candidates[0]
    return model, float(cval), float(threshold), act, fpr


def evaluate_seed(seed: int, external: pd.DataFrame):
    frame = r5.build_ranker_frame(seed)
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    static_pipe, static_c, static_valid, static_test, static_th, _ = r5.fit_eval(
        frame, r5.STATIC_FEATURES, f"static_{seed}"
    )
    for part in [train, valid, test]:
        part[f"static_{seed}"] = static_pipe.predict_proba(
            part[r5.STATIC_FEATURES]
        )[:, 1]

    veto_model, veto_c, veto_th, valid_action, valid_fpr = select_model_threshold(
        train, valid, f"static_{seed}", static_th
    )

    test["veto_score"] = veto_model.predict_proba(
        test[RUN_VETO_FEATURES]
    )[:, 1]
    test_action = action_stats(
        test, f"static_{seed}", static_th, "veto_score", veto_th
    )
    internal_clean = clean_case_table(
        test, f"static_{seed}", static_th, "veto_score", veto_th
    )
    internal_pair = paired_bootstrap(internal_clean, seed + 3000)

    ext = external.copy()
    ext[f"static_{seed}"] = static_pipe.predict_proba(
        ext[r5.STATIC_FEATURES]
    )[:, 1]
    ext["veto_score"] = veto_model.predict_proba(
        ext[RUN_VETO_FEATURES]
    )[:, 1]
    external_cases = clean_case_table(
        ext, f"static_{seed}", static_th, "veto_score", veto_th
    )
    external_pair = paired_bootstrap(external_cases, seed + 4000)

    rank_sources = set(frame.source_name.astype(str).unique())
    external_sources = set(ext.source_name.astype(str).unique())
    overlap = sorted(rank_sources & external_sources)

    return {
        "seed": seed,
        "static_C": static_c,
        "static_threshold": static_th,
        "veto_C": veto_c,
        "veto_threshold": veto_th,
        "static_ranking": static_test,
        "validation_veto": {
            "target_action_keep": valid_action["target_action_keep"],
            "strong_action_keep": valid_action["strong_action_keep"],
            "clean_fpr": valid_fpr,
        },
        "test_action": test_action,
        "internal_clean": internal_pair,
        "external_clean": external_pair,
        "source_overlap_count": len(overlap),
        "source_overlap": overlap,
        "ranking_order_unchanged": True,
        "external_cases": external_cases,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    external = r5.external_clean_frame()
    results = []
    external_rows = []
    action_rows = []
    threshold_rows = []

    for seed in SEEDS:
        result = evaluate_seed(seed, external)
        results.append(result)

        ext = result.pop("external_cases")
        ext["seed"] = seed
        external_rows.append(ext)

        action_rows.append({
            "seed": seed,
            **result["test_action"],
            "internal_baseline_fpr": result["internal_clean"]["baseline_fpr"],
            "internal_veto_fpr": result["internal_clean"]["veto_fpr"],
            "external_baseline_fpr": result["external_clean"]["baseline_fpr"],
            "external_veto_fpr": result["external_clean"]["veto_fpr"],
        })
        threshold_rows.append({
            "seed": seed,
            "static_C": result["static_C"],
            "static_threshold": result["static_threshold"],
            "veto_C": result["veto_C"],
            "veto_threshold": result["veto_threshold"],
            "validation_target_keep": result["validation_veto"]["target_action_keep"],
            "validation_strong_keep": result["validation_veto"]["strong_action_keep"],
            "validation_clean_fpr": result["validation_veto"]["clean_fpr"],
        })

    criteria = {}
    for result in results:
        seed = str(result["seed"])
        ext = result["external_clean"]
        act = result["test_action"]
        criteria[seed] = {
            "zero_source_overlap": result["source_overlap_count"] == 0,
            "ranking_order_unchanged": result["ranking_order_unchanged"],
            "external_fpr_improves_by_0_05": (
                ext["veto_fpr"] <= ext["baseline_fpr"] - 0.05
            ),
            "external_paired_ci_upper_nonpositive": (
                ext["bootstrap_hi"] is not None and ext["bootstrap_hi"] <= 0.0
            ),
            "target_action_keep_gte_0_95": act["target_action_keep"] >= 0.95,
            "strong_action_keep_gte_0_95": act["strong_action_keep"] >= 0.95,
            "no_new_external_false_triggers": ext["regressions"] == 0,
        }

    retention = all(all(v.values()) for v in criteria.values())

    summary = {
        "experiment": "VOCAL_RESONANCE_R6_RUN_LENGTH_VETO",
        "seeds": SEEDS,
        "candidate_budget": 20,
        "veto_features": RUN_VETO_FEATURES,
        "per_seed": {
            str(r["seed"]): {
                k: v for k, v in r.items()
                if k not in {"source_overlap"}
            }
            for r in results
        },
        "retention_gate": {
            "accepted": bool(retention),
            "criteria": criteria,
            "meaning": (
                "Whether run-length morphology is useful only as a post-ranker "
                "veto/abstention stage. Passing does not improve or validate the "
                "semantic ranking product gate."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "The static semantic ranker remains far below the existing "
                "Top-5 / strong-effect product criteria; R6 only tests abstention."
            ),
        },
        "raw_audio_persisted": False,
    }

    pd.concat(external_rows, ignore_index=True).to_csv(
        out / "external_cases.csv", index=False
    )
    pd.DataFrame(action_rows).to_csv(out / "action_metrics.csv", index=False)
    pd.DataFrame(threshold_rows).to_csv(out / "thresholds.csv", index=False)

    comparison = []
    for result in results:
        comparison.append({
            "seed": result["seed"],
            "rank_top5": result["static_ranking"]["top5"],
            "rank_strong_top5": result["static_ranking"]["top5_effect_gte3"],
            "external_baseline_fpr": result["external_clean"]["baseline_fpr"],
            "external_veto_fpr": result["external_clean"]["veto_fpr"],
            "target_action_keep": result["test_action"]["target_action_keep"],
            "strong_action_keep": result["test_action"]["strong_action_keep"],
        })
    pd.DataFrame(comparison).to_csv(out / "comparison.csv", index=False)

    (out / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
