from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from integration.cipi.macro import build_macro_result, export_macro_result


class MacroBridgeTests(unittest.TestCase):
    def _fixture(self, root: Path, *, route: str = "ITERATE") -> Path:
        run = root / "melon-funnel-test"
        run.mkdir(parents=True)
        summary = {
            "run_id": "melon-funnel-test",
            "seed": 100,
            "timestamp": "2026-09-26T00:00:00+00:00",
            "effective_config": {
                "population_size": 6,
                "generations": 2,
                "max_candidates": 12,
                "max_runtime_seconds": 120.0,
                "stage2_limit": 4,
                "stage2_archive_limit": 4,
                "stage2_epsilon_range_fraction": 0.03,
                "stage2_epsilon_spread_multiplier": 0.5,
                "stage3_limit": 1,
                "workers": 1
            },
            "stage1_stop_reason": "MAX_GENERATIONS",
            "stage1_pareto": 3,
            "stage2_pareto": 2,
            "stage2_archive": 2,
            "deep_validation_count": 1,
            "routes": {route: 1},
            "precision_review_passed": True,
            "budget_recommendation": {"action": "HOLD_STANDARD_16X4"}
        }
        manifest = {"run_id": "melon-funnel-test", "commit_sha": "abcdef123", "timestamp": summary["timestamp"]}
        efficiency = {
            "new_semantic_candidate_rate": 0.75,
            "hypervolume_improvement_rate": 0.5,
            "hypervolume_gain": 0.1,
            "duplicate_rate": 0.05,
            "measurements_executed_stage1": 12,
            "stage2_measurement_runs": 12,
            "deep_validation_count": 1,
            "elapsed_seconds": 42.0
        }
        precision = {"passed": True, "checks": {"numerical_stability": True}}
        deep = [{
            "candidate_id": "C-1", "species": "test", "route": route,
            "reason": "needs more evidence" if route == "ITERATE" else "ready",
            "scientific": {}, "automatic_final_decision": False, "promotion_authority": False
        }]
        for name, data in {
            "summary.json": summary,
            "manifest.json": manifest,
            "efficiency_metrics.json": efficiency,
            "precision_review.json": precision,
            "stage3_deep_validation.json": deep,
        }.items():
            (run / name).write_text(json.dumps(data), encoding="utf-8")
        return run

    def _context(self):
        return dict(
            track_id="TRACK-1", research_id="ROOT-1", job_id="JOB-1",
            parent_job_id="", parent_run_id="", loop_depth=1,
            hypothesis_id="HYP-1", experiment_id="EXP-1", research_question="test"
        )

    def test_iterate_exports_proposal_without_authority(self):
        with tempfile.TemporaryDirectory() as td:
            result = build_macro_result(self._fixture(Path(td)), **self._context())
            self.assertEqual(result["route"], "CONTINUE")
            self.assertEqual(len(result["continuation_candidates"]), 1)
            self.assertFalse(result["automatic_final_decision"])
            self.assertFalse(result["cipi_promotion_authority"])
            self.assertFalse(result["product_release_authority"])
            self.assertEqual(result["continuation_candidates"][0]["proposed_experiment"]["inputs"]["seed"], 101)
            self.assertNotIn("seed", result["continuation_candidates"][0]["fingerprint_material"]["tested_parameters"])

    def test_review_candidate_routes_to_human_gate(self):
        with tempfile.TemporaryDirectory() as td:
            result = build_macro_result(self._fixture(Path(td), route="CANDIDATE_FOR_CIPI_REVIEW"), **self._context())
            self.assertEqual(result["route"], "HUMAN_GATE")
            self.assertEqual(result["continuation_candidates"], [])

    def test_rejected_scope_proposes_explicit_replication_only(self):
        with tempfile.TemporaryDirectory() as td:
            result = build_macro_result(self._fixture(Path(td), route="REJECTED_CURRENT_SCOPE"), **self._context())
            self.assertEqual(result["route"], "CONTINUE")
            proposal = result["continuation_candidates"][0]
            self.assertEqual(proposal["experiment_type"], "REPLICATION")

    def test_export_is_deterministic_for_same_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            run = self._fixture(Path(td))
            p1 = export_macro_result(run, **self._context())
            first = json.loads(p1.read_text())
            p2 = export_macro_result(run, **self._context())
            second = json.loads(p2.read_text())
            self.assertEqual(first["bundle_hash"], second["bundle_hash"])


if __name__ == "__main__":
    unittest.main()
