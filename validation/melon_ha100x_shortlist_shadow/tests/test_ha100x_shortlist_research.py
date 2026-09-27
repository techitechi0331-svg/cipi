from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from integration.cipi.macro import build_macro_result
from melon.ha100x_shortlist import SHORTLIST, run_ha100x_shortlist_research


class Ha100xShortlistResearchTests(unittest.TestCase):
    def _context(self, loop_depth: int = 1) -> dict:
        return {
            "track_id": "VL2A-CIRCUIT-HA100X-SHORTLIST-002",
            "research_id": "VL2A-CIRCUIT-HA100X-SHORTLIST-002",
            "job_id": f"VL2A-CIRCUIT-HA100X-SHORTLIST-002-R{loop_depth}-TEST",
            "parent_job_id": "",
            "parent_run_id": "",
            "loop_depth": loop_depth,
            "hypothesis_id": "HYP-VL2A-HA100X-SHORTLIST-ROBUSTNESS",
            "experiment_id": f"EXP-VL2A-HA100X-SHORTLIST-R{loop_depth}",
            "research_question": "Which Phase-1 HA-100X survivor is most robust without claiming hardware truth?",
        }

    def _config(self) -> dict:
        return {
            "population": 5,
            "generations": 1,
            "max_candidates": 5,
            "max_runtime_seconds": 90,
            "stage2_limit": 3,
            "stage2_archive_limit": 3,
            "stage2_epsilon_range_fraction": 0.03,
            "stage2_epsilon_spread_multiplier": 0.5,
            "stage3_limit": 1,
            "workers": 1,
        }

    def test_shortlist_is_fixed_and_authority_is_off(self):
        self.assertEqual(len(SHORTLIST), 5)
        with tempfile.TemporaryDirectory() as td:
            result = run_ha100x_shortlist_research(2026092711, td, self._config(), self._context(1))
            run_dir = Path(result["run_dir"])
            evidence = json.loads((run_dir / "ha100x_shortlist_validation.json").read_text(encoding="utf-8"))
            self.assertEqual(len(evidence["candidate_rankings"]), 5)
            self.assertFalse(evidence["automatic_final_decision"])
            self.assertFalse(evidence["cipi_promotion_authority"])
            self.assertFalse(evidence["product_integration_authority"])
            self.assertEqual(
                evidence["stress_profile"]["classification"],
                "SYNTHETIC_PARAMETER_STRESS_NOT_HARDWARE_TOLERANCE",
            )
            self.assertTrue((run_dir / "stage3_deep_validation.json").is_file())

    def test_loop_one_continues_with_shortlist_domain(self):
        with tempfile.TemporaryDirectory() as td:
            context = self._context(1)
            result = run_ha100x_shortlist_research(2026092711, td, self._config(), context)
            bundle = build_macro_result(Path(result["run_dir"]), **context)
            self.assertEqual(bundle["route"], "CONTINUE")
            self.assertEqual(len(bundle["continuation_candidates"]), 1)
            fp = bundle["continuation_candidates"][0]["fingerprint_material"]
            self.assertEqual(fp["architecture"], "HA100X_LINEAR_LTI_LOAD_AWARE_SHORTLIST")
            self.assertEqual(fp["research_domain"], "VL2A_HA100X_INPUT_TRANSFORMER_SHORTLIST")
            self.assertIn("synthetic_parameter_stress_not_hardware_tolerance", fp["relevant_constraints"])

    def test_successive_rounds_have_distinct_semantic_fingerprints(self):
        with tempfile.TemporaryDirectory() as td:
            c1 = self._context(1)
            r1 = run_ha100x_shortlist_research(2026092711, td, self._config(), c1)
            b1 = build_macro_result(Path(r1["run_dir"]), **c1)

            c2 = self._context(2)
            c2["parent_job_id"] = c1["job_id"]
            c2["parent_run_id"] = b1["run_id"]
            r2 = run_ha100x_shortlist_research(2026092712, td, self._config(), c2)
            b2 = build_macro_result(Path(r2["run_dir"]), **c2)

            self.assertEqual(b1["route"], "CONTINUE")
            self.assertEqual(b2["route"], "CONTINUE")
            self.assertNotEqual(
                b1["continuation_candidates"][0]["fingerprint_material"],
                b2["continuation_candidates"][0]["fingerprint_material"],
            )

    def test_loop_three_requires_human_review_when_robust(self):
        with tempfile.TemporaryDirectory() as td:
            context = self._context(3)
            result = run_ha100x_shortlist_research(2026092713, td, self._config(), context)
            bundle = build_macro_result(Path(result["run_dir"]), **context)
            self.assertEqual(bundle["route"], "HUMAN_GATE")
            self.assertEqual(bundle["continuation_candidates"], [])
            deep = json.loads((Path(result["run_dir"]) / "stage3_deep_validation.json").read_text(encoding="utf-8"))
            self.assertEqual(deep[0]["route"], "CANDIDATE_FOR_CIPI_REVIEW")


if __name__ == "__main__":
    unittest.main()
