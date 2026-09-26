from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from integration.cipi.macro import build_macro_result
from melon.ha100x_research import run_ha100x_research


class Ha100xAutonomousResearchTests(unittest.TestCase):
    def _context(self) -> dict:
        return {
            "track_id": "VL2A-CIRCUIT-HA100X-001",
            "research_id": "VL2A-CIRCUIT-HA100X-001",
            "job_id": "VL2A-CIRCUIT-HA100X-001-R1-TEST",
            "parent_job_id": "",
            "parent_run_id": "",
            "loop_depth": 1,
            "hypothesis_id": "HYP-VL2A-HA100X-LINEAR-FIRST",
            "experiment_id": "EXP-VL2A-HA100X-R1-BROAD-LTI",
            "research_question": "Can a bounded linear HA-100X model explain the known source/load constraints?",
        }

    def _config(self) -> dict:
        return {
            "population": 4,
            "generations": 2,
            "max_candidates": 8,
            "max_runtime_seconds": 30,
            "stage2_limit": 3,
            "stage2_archive_limit": 3,
            "stage2_epsilon_range_fraction": 0.03,
            "stage2_epsilon_spread_multiplier": 0.5,
            "stage3_limit": 1,
            "workers": 1,
        }

    def test_domain_adapter_emits_bounded_linear_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_ha100x_research(2026092701, td, self._config(), self._context())
            run_dir = Path(result["run_dir"])
            self.assertTrue(run_dir.is_dir())
            evidence = json.loads((run_dir / "ha100x_measurements.json").read_text(encoding="utf-8"))
            self.assertFalse(evidence["automatic_final_decision"])
            self.assertFalse(evidence["cipi_promotion_authority"])
            self.assertFalse(evidence["product_integration_authority"])
            self.assertEqual(evidence["hard_topology"]["turns_ratio"], 10.0)
            self.assertEqual(evidence["hard_topology"]["nonlinearity"], "LOCKED")
            self.assertEqual(evidence["hard_topology"]["hysteresis"], "LOCKED")
            self.assertLessEqual(len(evidence["candidate_measurements"]), 8)

            first = evidence["candidate_measurements"][0]
            self.assertEqual(set(first["source_load_matrix_rel_db"]), {"50", "150", "250", "600"})
            self.assertEqual(len(first["source_load_matrix_rel_db"]["150"]), 6)
            self.assertTrue(first["finite"])

    def test_macro_bundle_preserves_circuit_domain_and_no_authority(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_ha100x_research(2026092702, td, self._config(), self._context())
            bundle = build_macro_result(Path(result["run_dir"]), **self._context())

            self.assertEqual(bundle["result_type"], "MELON_MACRO_RESEARCH_RESULT")
            self.assertEqual(bundle["evidence_class"], "MEASURED")
            self.assertFalse(bundle["automatic_final_decision"])
            self.assertFalse(bundle["cipi_promotion_authority"])
            self.assertFalse(bundle["product_release_authority"])
            self.assertEqual(bundle["route"], "CONTINUE")
            self.assertGreaterEqual(len(bundle["continuation_candidates"]), 1)

            fp = bundle["continuation_candidates"][0]["fingerprint_material"]
            self.assertEqual(fp["architecture"], "HA100X_LINEAR_LTI_LOAD_AWARE")
            self.assertEqual(fp["research_domain"], "VL2A_HA100X_INPUT_TRANSFORMER")
            self.assertEqual(fp["input_set"], "VL2A_HA100X_SOURCE_LOAD_MATRIX_V1")
            self.assertIn("no_hysteresis_v1", fp["relevant_constraints"])
            self.assertIn("no_saturation_v1", fp["relevant_constraints"])

    def test_loop_five_produces_no_continuation(self):
        with tempfile.TemporaryDirectory() as td:
            context = self._context()
            context["loop_depth"] = 5
            result = run_ha100x_research(2026092705, td, self._config(), context)
            bundle = build_macro_result(Path(result["run_dir"]), **context)
            self.assertEqual(bundle["route"], "STOP")
            self.assertEqual(bundle["continuation_candidates"], [])


if __name__ == "__main__":
    unittest.main()
