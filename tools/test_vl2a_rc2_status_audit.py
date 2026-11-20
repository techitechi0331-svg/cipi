from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import yaml

from automation.worker.experiments import run_adapter


ADAPTER = "vl2a_rc2_evidence_continuity_v1"


def seed(root: Path) -> None:
    def write(path: str, contents: str) -> None:
        dest = root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(contents, encoding="utf-8")
    write("research/plugins/vl2a/circuit-lab/autonomous-track-baseline-2026-09-27.md",
          "pluginval 1.0.4 strictness 10: SUCCESS\n"
          "prepared latency 6 samples in tested 44.1/48/96 kHz contexts\n"
          "Cubase Pro 14 real-host: UNVERIFIED\n")
    write("research/autonomous_bridge/tracks/VL2A-CIRCUIT-HA100X-001.yaml",
          yaml.safe_dump({"track_id": "VL2A-CIRCUIT-HA100X-001",
                          "authority_boundaries": {"product_repository_write": False,
                                                   "automatic_knowledge_promotion": False,
                                                   "automatic_final_decision": False}}))
    write("research/autonomous_bridge/tracks/VL2A-CIRCUIT-HA100X-SHORTLIST-002.yaml",
          yaml.safe_dump({"track_id": "VL2A-CIRCUIT-HA100X-SHORTLIST-002",
                          "authority_boundaries": {"product_repository_write": False,
                                                   "automatic_knowledge_promotion": False,
                                                   "automatic_final_decision": False}}))
    write("research/plugins/vl2a/status.yaml",
          yaml.safe_dump({"stages": {"vst3_validation": "in_progress", "final_review": "pending"}}))
    write("research/health/vl2a-prehost.json",
          json.dumps({"state": "CUBASE_READY_HUMAN_GATE",
                      "track_id": "VL2A-CIRCUIT-HA100X-SHORTLIST-002",
                      "candidate_id": "HA100X-R4-012-591362e2",
                      "source_ref": "integration/vl2a-v060-rc2",
                      "automatic_product_decision": False,
                      "automatic_release_decision": False,
                      "cubase": {k: "UNVERIFIED" for k in
                                 ("scan", "insert", "playback", "automation", "save_reload", "pdc")},
                      "listening_judgment": "UNVERIFIED",
                      "release_decision": "UNVERIFIED"}))


class VL2AContinuityTests(unittest.TestCase):
    def test_preserves_human_gate_and_reports_historical_status_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed(root)
            result = run_adapter(ADAPTER, root, 60)
            self.assertTrue(result["acceptance_met"])
            metrics = result["metrics"]
            self.assertTrue(metrics["formal_tracking_scope_reconciliation_recommended"])
            self.assertEqual(metrics["unresolved_human_gate_count"], 8)
            self.assertFalse(metrics["premature_formal_completion"])
            self.assertIn("vl2a_rc2_status_audit.json", result["raw_files"])

    def test_never_accepts_auto_release_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed(root)
            path = root / "research/health/vl2a-prehost.json"
            data = json.loads(path.read_text())
            data["automatic_release_decision"] = True
            path.write_text(json.dumps(data))
            self.assertFalse(run_adapter(ADAPTER, root, 60)["acceptance_met"])

    def test_never_accepts_completed_final_review_with_open_human_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed(root)
            path = root / "research/plugins/vl2a/status.yaml"
            path.write_text(yaml.safe_dump({"stages": {"final_review": "complete"}}))
            result = run_adapter(ADAPTER, root, 60)
            self.assertTrue(result["metrics"]["premature_formal_completion"])
            self.assertFalse(result["acceptance_met"])


if __name__ == "__main__":
    unittest.main()
