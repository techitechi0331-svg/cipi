from __future__ import annotations

import csv
import io
import json
import math


CASES = [
    # name, vocal presence dB, masker presence dB
    ("heavy_mask_1", -8.0, -3.0),
    ("heavy_mask_2", -7.0, -2.5),
    ("moderate_mask_1", -6.0, -3.5),
    ("moderate_mask_2", -5.0, -3.0),
    ("mild_mask_1", -4.0, -3.0),
    ("mild_mask_2", -3.5, -3.0),
    ("balanced_1", -3.0, -3.0),
    ("balanced_2", -2.5, -3.0),
    ("vocal_forward_1", -2.0, -4.0),
    ("vocal_forward_2", -1.0, -4.0),
    ("bright_unmasked_1", -1.5, -5.0),
    ("bright_unmasked_2", -0.5, -5.0),
]

STATIC_GAIN_DB = 3.0
MAX_CONTEXT_GAIN_DB = 3.0
TARGET_MARGIN_DB = 0.5


def masking_deficit(vocal_db: float, masker_db: float) -> float:
    return max(0.0, masker_db - vocal_db)


def contextual_gain(vocal_db: float, masker_db: float) -> float:
    deficit = masking_deficit(vocal_db, masker_db)
    # Research-only oracle-like context law: move only when the masker actually
    # exceeds the vocal presence band, and cap the movement at the same 3 dB
    # budget as the static baseline.
    return min(MAX_CONTEXT_GAIN_DB, max(0.0, deficit + TARGET_MARGIN_DB))


def proxy_improvement(vocal_db: float, masker_db: float, gain_db: float) -> float:
    before = masking_deficit(vocal_db, masker_db)
    after = masking_deficit(vocal_db + gain_db, masker_db)
    return before - after


def main() -> int:
    rows = []
    for name, vocal_db, masker_db in CASES:
        deficit = masking_deficit(vocal_db, masker_db)
        baseline_gain = STATIC_GAIN_DB
        candidate_gain = contextual_gain(vocal_db, masker_db)
        rows.append({
            "case": name,
            "vocal_presence_db": vocal_db,
            "masker_presence_db": masker_db,
            "masking_deficit_db": deficit,
            "baseline_gain_db": baseline_gain,
            "candidate_gain_db": candidate_gain,
            "baseline_proxy_improvement_db": proxy_improvement(vocal_db, masker_db, baseline_gain),
            "candidate_proxy_improvement_db": proxy_improvement(vocal_db, masker_db, candidate_gain),
            "masked": int(deficit > 0.0),
        })

    masked = [r for r in rows if r["masked"] == 1]
    unmasked = [r for r in rows if r["masked"] == 0]

    baseline_masked_improvement = sum(r["baseline_proxy_improvement_db"] for r in masked) / len(masked)
    candidate_masked_improvement = sum(r["candidate_proxy_improvement_db"] for r in masked) / len(masked)
    improvement_ratio = candidate_masked_improvement / max(1.0e-12, baseline_masked_improvement)

    baseline_non_target = sum(r["baseline_gain_db"] for r in unmasked) / len(unmasked)
    candidate_non_target = sum(r["candidate_gain_db"] for r in unmasked) / len(unmasked)
    candidate_masked_gain = sum(r["candidate_gain_db"] for r in masked) / len(masked)

    all_candidate_gains = [r["candidate_gain_db"] for r in rows]
    mean_gain = sum(all_candidate_gains) / len(all_candidate_gains)
    gain_std = math.sqrt(sum((g - mean_gain) ** 2 for g in all_candidate_gains) / len(all_candidate_gains))

    finite = all(
        math.isfinite(float(value))
        for row in rows
        for key, value in row.items()
        if key != "case"
    )

    metrics = {
        "row_count": len(rows),
        "masked_case_count": len(masked),
        "unmasked_case_count": len(unmasked),
        "matrix_complete": len(rows) == 12 and len(masked) >= 4 and len(unmasked) >= 4,
        "all_numeric_finite": finite,
        "baseline_masked_proxy_improvement_db": baseline_masked_improvement,
        "candidate_masked_proxy_improvement_db": candidate_masked_improvement,
        "masked_proxy_improvement_ratio": improvement_ratio,
        "baseline_non_target_movement_db": baseline_non_target,
        "candidate_non_target_movement_db": candidate_non_target,
        "non_target_movement_ratio": candidate_non_target / max(1.0e-12, baseline_non_target),
        "candidate_masked_mean_gain_db": candidate_masked_gain,
        "candidate_gain_std_db": gain_std,
        "candidate_max_gain_db": max(all_candidate_gains),
    }

    triggered = []
    if not metrics["matrix_complete"]:
        triggered.append("synthetic masking-context matrix is incomplete")
    if not finite:
        triggered.append("non-finite numeric output")
    if improvement_ratio < 0.80:
        triggered.append("candidate retains less than 80 percent of static-EQ masked proxy improvement")
    if candidate_non_target > 1.0:
        triggered.append("candidate non-target movement exceeds 1.0 dB")
    if metrics["non_target_movement_ratio"] > 0.35:
        triggered.append("candidate non-target movement exceeds 35 percent of static-EQ baseline")
    if candidate_masked_gain < 0.50:
        triggered.append("candidate does not produce meaningful movement on masked cases")
    if gain_std < 0.50:
        triggered.append("candidate collapses toward a static gain law")
    if metrics["candidate_max_gain_db"] > MAX_CONTEXT_GAIN_DB + 1.0e-9:
        triggered.append("candidate exceeds declared 3 dB movement budget")

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

    payload = {
        "metrics": metrics,
        "measurement_csv": out.getvalue(),
        "acceptance_met": len(triggered) == 0,
        "triggered_criteria": triggered,
        "scope": (
            "Deterministic synthetic masking-context pilot only. The contextual law uses "
            "known target/masker band levels and therefore behaves like an oracle-style "
            "proof of selectivity, not a deployable masking estimator. It tests whether "
            "context-dependent bounded movement can retain most of a static-EQ masking "
            "proxy benefit while avoiding unnecessary movement on unmasked cases."
        ),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
