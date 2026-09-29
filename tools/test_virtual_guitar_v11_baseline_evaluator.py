from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation.virtual_guitar.evaluate_v11_baseline import (
    NEXT_JOB_ID,
    NEXT_TRACK_ID,
    reconcile,
)


def valid_summary() -> dict:
    acceptance = {
        "all_18_raw_coordinates_rendered": True,
        "all_18_manifests_present": True,
        "repeat_render_check_complete": True,
        "wav_validity_pass": True,
        "no_nan_inf": True,
        "same_midi_collision_result_recorded": True,
        "source_tree_unchanged": True,
        "product_repository_persistent_write": False,
        "all_15_pickup_di_requests_explicitly_classified": True,
        "no_raw_to_di_fake_substitution": True,
        "category_level_gap_report_generated": True,
        "no_single_scalar_realism_verdict": True,
    }
    pickup = [
        {"status": "BLOCKED_STAGE_MISMATCH", "raw_to_di_fake_substitution": False}
        for _ in range(15)
    ]
    return {
        "track_id": "VIRTUAL-GUITAR-V11-BASELINE-MEASURE-001",
        "status": "COMPLETED",
        "coordinates": [{} for _ in range(18)],
        "pickup_di_classification": pickup,
        "same_midi_red_team": [],
        "gap_report": {
            "pickup_stage_availability": "BLOCKED_STAGE_MISMATCH",
            "deterministic_repeatability": "PASS",
        },
        "acceptance": acceptance,
        "authority": {
            "product_repository_write": False,
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
            "human_listening_adoption": False,
        },
    }


class EvaluateV11BaselineTests(unittest.TestCase):
    def test_valid_evidence_generates_pickup_di_track_and_job(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = root / "research/cross_repo/artifacts/cipi/1/2/files"
            evidence.mkdir(parents=True)
            (evidence / "baseline-summary.json").write_text(
                json.dumps(valid_summary()), encoding="utf-8"
            )
            result = reconcile(root)
            self.assertEqual(result["continued"], 1)
            self.assertTrue(
                (root / "research/jobs/queued" / f"{NEXT_JOB_ID}.yaml").is_file()
            )
            self.assertTrue(
                (root / "research/plugins/virtual-guitar/research-tracks" / f"{NEXT_TRACK_ID}.yaml").is_file()
            )


if __name__ == "__main__":
    unittest.main()
