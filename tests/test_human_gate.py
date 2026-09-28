from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from automation.human_gate import apply as hg


class HumanGateDecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cipi-human-gate-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        self.old_root = hg.ROOT
        hg.ROOT = self.tmp
        self.addCleanup(lambda: setattr(hg, "ROOT", self.old_root))

        snap = {
            "project_id": "virtual_guitar",
            "freshness": "FRESH",
            "generation_id": "gen-12345678",
            "source_state_digest": "a" * 64,
            "human_gates": [
                {
                    "source": "RESEARCH_JOB",
                    "job_id": "VG-JOB-001",
                    "gates": ["REAL_AUDIO_AB"],
                    "blocking": True,
                },
                {
                    "source": "AUTONOMOUS_TRACK",
                    "track_id": "VG-TRACK-001",
                    "gates": ["HUMAN_GATE"],
                    "blocking": True,
                },
            ],
        }
        path = self.tmp / "research/continuity/projects/virtual_guitar/current.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snap), encoding="utf-8")

    def args(self, **overrides):
        values = dict(
            project_id="virtual_guitar",
            target_type="RESEARCH_JOB",
            target_id="VG-JOB-001",
            gate="REAL_AUDIO_AB",
            outcome="COMPLETE",
            evidence_ref="discord://verification/123",
            rationale="Matched real-audio A/B was completed and reviewed.",
            actor="tester",
            source="DISCORD",
            source_generation_id="gen-12345678",
            source_state_digest="a" * 64,
            run_id="run-1",
            github_output=None,
        )
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_complete_research_job_gate_has_operational_effect(self):
        path = hg.apply(self.args())
        data = hg.yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(data["outcome"], "COMPLETE")
        self.assertEqual(data["operational_effect"], "RESOLVE_RESEARCH_JOB_GATE")
        self.assertFalse(data["automatic_product_decision"])
        self.assertFalse(data["automatic_release"])
        self.assertEqual(hg.validate_all(), [])

    def test_track_completion_is_record_only(self):
        path = hg.apply(self.args(
            target_type="AUTONOMOUS_TRACK",
            target_id="VG-TRACK-001",
            gate="HUMAN_GATE",
            run_id="run-2",
        ))
        data = hg.yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(data["operational_effect"], "RECORD_ONLY")

    def test_stale_generation_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "generation_id changed"):
            hg.apply(self.args(source_generation_id="old-generation"))

    def test_unknown_gate_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "not present"):
            hg.apply(self.args(gate="NOT_A_REAL_GATE"))

    def test_secret_like_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "secret-like material"):
            hg.apply(self.args(evidence_ref="github_pat_" + "A" * 30))


if __name__ == "__main__":
    unittest.main()
