"""R14: fresh-seed, singer-disjoint resonance failure-attribution audit.

Research only. Reuses the frozen R13 candidate generator and analytical
-2 dB peak response, without product DSP, renders or raw audio persistence.
The nearest-by-Hz candidate is a *proxy*, not a guaranteed action oracle.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "vocal_resonance_r13_for_r14", HERE / "action_equivalence_audit.py"
)
r13 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(r13)

SEEDS = (20261103, 20261113)  # New seeds, distinct from R13's 20261003/20261013.
K_VALUES = (1, 3, 5)
Q_VALUES = (8.0, 12.0, 20.0)
ACTION_DB = 1.0
BOOTSTRAP_REPS = 1000


def singer_overlap_count(frame: pd.DataFrame) -> int:
    sets = {
        name: set(frame.loc[frame["split"] == name, "singer"].astype(str))
        for name in ("train", "valid", "test")
    }
    return len((sets["train"] & sets["valid"]) |
               (sets["train"] & sets["test"]) |
               (sets["valid"] & sets["test"]))


def singer_cluster_ci(rows: pd.DataFrame, metric: str, seed: int) -> list[float]:
    if rows.empty:
        return [0.0, 1.0]
    groups = {
        singer: group[metric].to_numpy(dtype=float)
        for singer, group in rows.groupby("singer", sort=True)
    }
    names = sorted(groups)
    if not names:
        return [0.0, 1.0]
    rng = np.random.default_rng(seed + 777)
    sample_means = []
    for _ in range(BOOTSTRAP_REPS):
        selected = rng.choice(len(names), size=len(names), replace=True)
        pooled = np.concatenate([groups[names[int(i)]] for i in selected])
        sample_means.append(float(np.mean(pooled)))
    return [float(v) for v in np.quantile(sample_means, [0.025, 0.975])]


def evaluate_seed(seed: int) -> tuple[dict, pd.DataFrame]:
    frame = r13.r5.build_ranker_frame(seed)
    overlap = singer_overlap_count(frame)
    test = r13.fit_static_scores(frame, seed)
    test.attrs["seed"] = seed
    injected = test.loc[test["is_clean"] == 0]
    represented = injected.groupby("case_id", sort=False)["generator_hit"].max()
    hit_cases = int((represented > 0).sum())
    represented_cases = int(len(represented))
    generator_rate = (
        hit_cases / represented_cases if represented_cases else 0.0
    )
    singer_by_case = injected.groupby("case_id", sort=False)["singer"].first()

    case_tables = []
    policy_results = {}
    for policy in ("static", "prominence"):
        policy_results[policy] = {}
        for k in K_VALUES:
            policy_results[policy][str(k)] = {}
            for q in Q_VALUES:
                cases = r13.case_rows(test, policy, k, q)
                if not cases.empty:
                    cases = cases.copy()
                    cases["singer"] = cases["case_id"].map(singer_by_case).astype(str)
                    cases["nearest_reachable"] = (
                        cases["oracle_nearest_attenuation_db"] >= ACTION_DB
                    ).astype(int)
                    cases["ranker_actionable_miss"] = (
                        (cases["nearest_reachable"] == 1) &
                        (cases["action_equivalent_hit"] == 0)
                    ).astype(int)
                    cases["strong_ranker_actionable_miss"] = (
                        (cases["ranker_actionable_miss"] == 1) &
                        (cases["strong_effect"] == 1)
                    ).astype(int)
                    case_tables.append(cases)
                n = int(len(cases))
                strong = cases.loc[cases["strong_effect"] == 1] if n else cases
                result = {
                    "n_cases": n,
                    "strong_n": int(len(strong)),
                    "exact_hit_rate": float(cases["exact_hit"].mean()) if n else 0.0,
                    "action_equivalent_rate": (
                        float(cases["action_equivalent_hit"].mean()) if n else 0.0
                    ),
                    "nearest_frequency_reachable_rate": (
                        float(cases["nearest_reachable"].mean()) if n else 0.0
                    ),
                    "ranker_actionable_miss_rate": (
                        float(cases["ranker_actionable_miss"].mean()) if n else 0.0
                    ),
                    "strong_ranker_actionable_miss_rate": (
                        float(strong["ranker_actionable_miss"].mean())
                        if len(strong) else 0.0
                    ),
                    "nearest_actionable_miss_cluster_ci_95": (
                        singer_cluster_ci(cases, "ranker_actionable_miss", seed)
                        if n else [0.0, 1.0]
                    ),
                }
                policy_results[policy][str(k)][str(int(q))] = result

    primary = policy_results["static"]["5"]["12"]
    criteria = {
        "singer_overlap_zero": overlap == 0,
        "represented_generator_hit_gte_0_80": generator_rate >= 0.80,
        "ranker_actionable_miss_gte_0_25": (
            primary["ranker_actionable_miss_rate"] >= 0.25
        ),
        "strong_ranker_actionable_miss_gte_0_20": (
            primary["strong_ranker_actionable_miss_rate"] >= 0.20
        ),
    }
    result = {
        "seed": seed,
        "singer_split_overlap_count": overlap,
        "represented_injected_test_cases": represented_cases,
        "represented_generator_hit_cases": hit_cases,
        "represented_injection_generator_hit_rate": generator_rate,
        "note": (
            "Only injection cases represented in the candidate-row frame are "
            "counted; this is not full-dataset generator recall."
        ),
        "by_policy": policy_results,
        "gate_criteria": criteria,
    }
    return result, (
        pd.concat(case_tables, ignore_index=True) if case_tables
        else pd.DataFrame()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    per_seed = {}
    tables = []
    for seed in SEEDS:
        result, cases = evaluate_seed(seed)
        per_seed[str(seed)] = result
        if not cases.empty:
            tables.append(cases)
    accepted = all(
        all(v for v in per_seed[str(seed)]["gate_criteria"].values())
        for seed in SEEDS
    )
    summary = {
        "experiment": "VOCAL_RESONANCE_R14_ERROR_ATTRIBUTION",
        "seeds": list(SEEDS),
        "q_values": list(Q_VALUES),
        "top_k_values": list(K_VALUES),
        "cut_db": -2.0,
        "action_threshold_db": ACTION_DB,
        "bootstrap": "1000 singer-cluster resamples per seed, descriptive intervals only",
        "note": (
            "Fresh injection randomness, same fixed singer-disjoint source protocol; "
            "not an independent singer cohort. No external clean false-trigger, "
            "high-F0/formant listening, runtime, or product DSP validation."
        ),
        "diagnostic_gate": {
            "accepted": accepted,
            "route": (
                "TEST_RANKER_ACTION_SELECTION_FURTHER"
                if accepted else "REVISIT_GENERATOR_VS_RANKER_FAILURE_SCOPE"
            ),
        },
        "per_seed": per_seed,
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    if tables:
        pd.concat(tables, ignore_index=True).to_csv(
            out / "case_attribution.csv", index=False
        )
    else:
        (out / "case_attribution.csv").write_text(
            "seed,case_id,policy,top_k,q\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
