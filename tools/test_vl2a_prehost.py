from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import yaml

MODULE_PATH = Path(__file__).resolve().parents[1] / "automation" / "vl2a_prehost" / "promote.py"
spec = importlib.util.spec_from_file_location("vl2a_prehost_promote", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

TRACK = "VL2A-CIRCUIT-HA100X-SHORTLIST-002"
CANDIDATE = {
    "candidate_id": "HA100X-R4-012-591362e2",
    "primary_dcr_ohm": 64.42056271688182,
    "secondary_dcr_ohm": 3031.5360890531933,
    "magnetizing_h": 23.787562773717497,
    "leakage_h": 0.00016910013055046575,
    "secondary_cap_f": 1.8971658271371616e-11,
    "core_loss_ohm": 266576.9148779566,
    "turns_ratio": 10.0,
}

def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")

class PreHostPromoterTests(unittest.TestCase):
    def seed(self, root: Path) -> None:
        write_yaml(
            root / "research/autonomous_bridge/decisions" / TRACK / "R3.yaml",
            {
                "track_id": TRACK,
                "loop_depth": 3,
                "decision": "STOP",
                "stop_reason": "HUMAN_GATE",
                "processed_artifact_hash": "a" * 64,
            },
        )
        write_json(
            root / "research/cross_repo/artifacts/melon/1/2/files/run/ha100x_shortlist_validation.json",
            {
                "track_id": TRACK,
                "loop_depth": 3,
                "leader_candidate_id": CANDIDATE["candidate_id"],
                "candidate_rankings": [{
                    "candidate": CANDIDATE,
                    "stress_summary": {
                        "catalog_pass_fraction": 1.0,
                        "catalog_dev_db": {"p90": 0.03},
                        "source_load_matrix_worst_dev_db": {"p90": 0.06},
                    },
                }],
            },
        )

    def test_queues_once_then_stops_at_cubase_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.seed(root)
            first = mod.reconcile(root)
            self.assertTrue(first["action_created"])
            self.assertEqual(first["health"]["state"], "PREHOST_QUEUED")
            action_id = first["health"]["action_id"]
            action = mod.load_yaml(root / "research/cross_repo/actions/queued" / f"{action_id}.yaml")
            self.assertFalse(action["automatic_product_decision"])
            self.assertTrue(action["research_staging_write_only"])
            self.assertEqual(action["inputs"]["source_ref"], "integration/vl2a-v060-rc2")

            second = mod.reconcile(root)
            self.assertFalse(second["action_created"])
            self.assertEqual(second["health"]["state"], "PREHOST_QUEUED")

            summary = {
                "state": "CUBASE_READY_HUMAN_GATE",
                "track_id": TRACK,
                "candidate_id": CANDIDATE["candidate_id"],
                "staging_branch": "research/prehost/test",
                "cubase": {"scan": "UNVERIFIED"},
                "listening_judgment": "UNVERIFIED",
                "product_adoption": "UNVERIFIED",
                "release_decision": "UNVERIFIED",
            }
            write_json(
                root / "research/cross_repo/artifacts/vl2a/10/20/files/prehost_summary.json",
                summary,
            )
            third = mod.reconcile(root)
            self.assertEqual(third["health"]["state"], "CUBASE_READY_HUMAN_GATE")
            self.assertFalse(third["action_created"])

    def test_rejects_weak_finalist(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.seed(root)
            path = root / "research/cross_repo/artifacts/melon/1/2/files/run/ha100x_shortlist_validation.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["candidate_rankings"][0]["stress_summary"]["catalog_pass_fraction"] = 0.5
            write_json(path, data)
            result = mod.reconcile(root)
            self.assertEqual(result["health"]["state"], "BLOCKED_INVALID_FINALIST")
            self.assertFalse(result["action_created"])

if __name__ == "__main__":
    unittest.main()
