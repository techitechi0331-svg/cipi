"""CIPI Vocal Resonance v0.4R.13 action-equivalence / metric-necessity audit.

Research only. No suppressor implementation and no audio rendering.

Question:
Does exact injected-target Top-K materially overstate the frequency-placement
accuracy needed by a narrow resonance-suppression action?

For each candidate list, the audit compares:
- frozen static R2-style ranking;
- simple local-prominence ranking.

An action-equivalent hit means at least one selected candidate would attenuate
the true injected target by >=1 dB if a fixed analytical -2 dB peaking cut were
centered on that selected candidate.

Q = 8, 12 and 20 are reported. Q=12 / Top-5 is the predeclared primary gate.

This tests the ranking metric, not a product suppressor.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

HERE = Path(__file__).resolve().parent
R5_PATH = HERE / "temporal_morphology_ranker.py"
spec = importlib.util.spec_from_file_location("r5_action_equiv", R5_PATH)
r5 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r5)
r3 = r5.r3

SEEDS = [20261003, 20261013]
TOP_K = [1, 3, 5]
Q_VALUES = [8.0, 12.0, 20.0]
CUT_DB = -2.0
ACTION_THRESHOLD_DB = 1.0


def attenuation_at_target(candidate_hz: float, target_hz: float, q: float) -> float:
    b, a = r3.rbj_peak(float(candidate_hz), float(q), CUT_DB)
    w = 2.0 * np.pi * float(target_hz) / float(r3.FS)
    _, h = signal.freqz(b, a, worN=np.asarray([w], dtype=float))
    response_db = 20.0 * np.log10(np.abs(h[0]) + 1e-18)
    return float(max(0.0, -response_db))


def fit_static_scores(frame: pd.DataFrame, seed: int) -> pd.DataFrame:
    train = frame[frame.split == "train"].copy()
    valid = frame[frame.split == "valid"].copy()
    test = frame[frame.split == "test"].copy()

    pipe, _, _, _ = r3.fit_ranker(train, valid, list(r3.STATIC_FEATURES))
    test["static_score"] = pipe.predict_proba(
        test[r3.STATIC_FEATURES]
    )[:, 1]
    test["prominence_score"] = test["local_score"].astype(float)
    return test


def case_rows(test: pd.DataFrame, policy: str, k: int, q: float):
    score_col = "static_score" if policy == "static" else "prominence_score"
    rows = []

    injected = test[test.is_clean == 0]
    for case_id, group in injected.groupby("case_id", sort=False):
        if int(group.generator_hit.max()) <= 0:
            continue

        target_rows = group[group.is_target == 1]
        if len(target_rows) != 1:
            continue

        target = target_rows.iloc[0]
        target_hz = float(target.target_hz)
        effect = float(target.physical_effect_db)

        ranked = group.sort_values(score_col, ascending=False).head(k)
        exact_hit = int(ranked.is_target.max() > 0)

        attenuations = [
            attenuation_at_target(float(row.candidate_hz), target_hz, q)
            for _, row in ranked.iterrows()
        ]
        best_att = float(max(attenuations)) if attenuations else 0.0

        nearest_idx = int(
            np.argmin(
                np.abs(
                    group.candidate_hz.to_numpy(dtype=float) - target_hz
                )
            )
        )
        nearest = group.iloc[nearest_idx]
        oracle_att = attenuation_at_target(
            float(nearest.candidate_hz), target_hz, q
        )
        ratio = best_att / max(oracle_att, 1e-9)

        rows.append({
            "seed": int(test.attrs.get("seed", 0)),
            "case_id": str(case_id),
            "policy": policy,
            "top_k": int(k),
            "q": float(q),
            "target_hz": target_hz,
            "physical_effect_db": effect,
            "strong_effect": int(effect >= 3.0),
            "exact_hit": exact_hit,
            "action_attenuation_db": best_att,
            "action_equivalent_hit": int(
                best_att >= ACTION_THRESHOLD_DB
            ),
            "oracle_nearest_attenuation_db": oracle_att,
            "oracle_relative_attenuation": float(ratio),
            "selected_min_distance_hz": float(
                np.min(
                    np.abs(
                        ranked.candidate_hz.to_numpy(dtype=float)
                        - target_hz
                    )
                )
            ) if len(ranked) else None,
        })
    return pd.DataFrame(rows)


def summarize(rows: pd.DataFrame) -> dict:
    if len(rows) == 0:
        return {
            "n_cases": 0,
            "exact_hit_rate": None,
            "action_equivalent_rate": None,
            "action_minus_exact": None,
            "strong_n": 0,
            "strong_action_equivalent_rate": None,
            "median_action_attenuation_db": None,
            "median_oracle_relative_attenuation": None,
        }

    strong = rows[rows.strong_effect == 1]
    return {
        "n_cases": int(len(rows)),
        "exact_hit_rate": float(rows.exact_hit.mean()),
        "action_equivalent_rate": float(rows.action_equivalent_hit.mean()),
        "action_minus_exact": float(
            rows.action_equivalent_hit.mean() - rows.exact_hit.mean()
        ),
        "strong_n": int(len(strong)),
        "strong_action_equivalent_rate": (
            float(strong.action_equivalent_hit.mean())
            if len(strong) else None
        ),
        "median_action_attenuation_db": float(
            rows.action_attenuation_db.median()
        ),
        "median_oracle_relative_attenuation": float(
            rows.oracle_relative_attenuation.median()
        ),
    }


def evaluate_seed(seed: int):
    frame = r5.build_ranker_frame(seed)
    test = fit_static_scores(frame, seed)
    test.attrs["seed"] = seed

    all_rows = []
    summaries = {}
    for policy in ["static", "prominence"]:
        summaries[policy] = {}
        for k in TOP_K:
            summaries[policy][str(k)] = {}
            for q in Q_VALUES:
                rows = case_rows(test, policy, k, q)
                all_rows.append(rows)
                summaries[policy][str(k)][str(int(q))] = summarize(rows)

    primary = summaries["static"]["5"]["12"]
    q8 = summaries["static"]["5"]["8"]
    q20 = summaries["static"]["5"]["20"]

    criteria = {
        "action_equivalent_rate_gte_0_70": bool(
            primary["action_equivalent_rate"] is not None
            and primary["action_equivalent_rate"] >= 0.70
        ),
        "action_minus_exact_gte_0_20": bool(
            primary["action_minus_exact"] is not None
            and primary["action_minus_exact"] >= 0.20
        ),
        "strong_action_equivalent_rate_gte_0_70": bool(
            primary["strong_action_equivalent_rate"] is not None
            and primary["strong_action_equivalent_rate"] >= 0.70
        ),
        "median_oracle_relative_attenuation_gte_0_60": bool(
            primary["median_oracle_relative_attenuation"] is not None
            and primary["median_oracle_relative_attenuation"] >= 0.60
        ),
        "q8_action_gain_gte_0_10": bool(
            q8["action_minus_exact"] is not None
            and q8["action_minus_exact"] >= 0.10
        ),
        "q20_action_gain_gte_0_10": bool(
            q20["action_minus_exact"] is not None
            and q20["action_minus_exact"] >= 0.10
        ),
    }

    return summaries, criteria, pd.concat(all_rows, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    per_seed = {}
    criteria = {}
    tables = []

    for seed in SEEDS:
        summaries, seed_criteria, rows = evaluate_seed(seed)
        per_seed[str(seed)] = summaries
        criteria[str(seed)] = seed_criteria
        tables.append(rows)

    accepted = all(all(v.values()) for v in criteria.values())
    route = (
        "EXACT_RANKING_METRIC_OVERSTATES_ACTION_REQUIREMENT"
        if accepted
        else "EXACT_RANKING_REMAINS_ACTION_RELEVANT"
    )

    summary = {
        "experiment": "VOCAL_RESONANCE_R13_ACTION_EQUIVALENCE",
        "seeds": SEEDS,
        "cut_db": CUT_DB,
        "q_values": Q_VALUES,
        "top_k_values": TOP_K,
        "action_equivalent_threshold_db": ACTION_THRESHOLD_DB,
        "primary_gate": {
            "policy": "static",
            "top_k": 5,
            "q": 12,
        },
        "per_seed": per_seed,
        "diagnostic_gate": {
            "accepted": bool(accepted),
            "route": route,
            "criteria": criteria,
            "meaning": (
                "Whether exact causal-target Top-K materially understates the "
                "frequency-placement utility of the selected candidate set. "
                "This does not authorize a suppressor implementation."
            ),
        },
        "product_gate": {
            "passed": False,
            "reason": (
                "R13 audits metric/action equivalence only. No realtime "
                "suppression topology, listening or VST3 gate is evaluated."
            ),
        },
        "raw_audio_persisted": False,
    }

    table = pd.concat(tables, ignore_index=True)
    table.to_csv(out / "case_actions.csv", index=False)

    rows = []
    for seed, seed_data in per_seed.items():
        for policy, by_k in seed_data.items():
            for k, by_q in by_k.items():
                for q, metrics in by_q.items():
                    rows.append({
                        "seed": int(seed),
                        "policy": policy,
                        "top_k": int(k),
                        "q": int(q),
                        **metrics,
                    })
    pd.DataFrame(rows).to_csv(out / "comparison.csv", index=False)

    (out / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
