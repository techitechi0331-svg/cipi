from __future__ import annotations
import json
from pathlib import Path
import shutil, tempfile, unittest
from automation.continuity.core import AUTHORITY,ProjectSpec,build_all,build_project_snapshot,scan_for_secrets,validate_published

class ContinuityLayerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=Path(tempfile.mkdtemp(prefix="cipi-continuity-"));self.addCleanup(lambda:shutil.rmtree(self.tmp,ignore_errors=True))
        for rel in ("automation/cross_repo","research/health","research/jobs/queued","research/jobs/completed","research/decisions","research/reviews","research/continuity"):(self.tmp/rel).mkdir(parents=True,exist_ok=True)
        self._write("automation/cross_repo/registry.yaml",'''schema_version: "1.0"
repositories:
  virtual_guitar:
    repository: techitechi0331-svg/virtual-guitar
    default_ref: main
    workflows: {}
''')
        self._json("research/health/automation-status.json",{"schema_version":"1.0","authority":"OPERATIONAL_SCHEDULING_ONLY","human_gates":[],"autonomous_research":{"track_lifecycle":{}}})
        self._json("research/health/autonomous-bridge.json",{"schema_version":"1.0","authority":"OPERATIONAL_SCHEDULING_ONLY","track_lifecycle":{}})
    def _write(self,rel,text):
        p=self.tmp/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding="utf-8")
    def _json(self,rel,value):self._write(rel,json.dumps(value,indent=2,sort_keys=True))
    @property
    def spec(self):return ProjectSpec("virtual_guitar","techitechi0331-svg/virtual-guitar","main",("VIRTUALGUITAR",))
    @staticmethod
    def resolver(repo,ref,token):return "a"*40

    def test_deterministic_semantics(self):
        self._write("research/jobs/queued/VIRTUAL-GUITAR-READY-001.yaml",'''schema_version: "1.0"
job_id: VIRTUAL-GUITAR-READY-001
state: QUEUED
priority: 10
track: {id: VIRTUAL_GUITAR_READY}
research_question: Can the ready work continue?
depends_on_jobs: []
''')
        one=build_project_snapshot(self.tmp,self.spec,resolver=self.resolver,cipi_sha="b"*40,generated_at="2026-09-29T00:00:00Z")
        two=build_project_snapshot(self.tmp,self.spec,resolver=self.resolver,cipi_sha="b"*40,generated_at="2026-09-29T00:00:00Z")
        self.assertEqual(one,two);self.assertEqual(one["authority"],AUTHORITY);self.assertEqual(one["freshness"],"FRESH");self.assertTrue(one["resume_contract"]["can_autonomously_resume"])

    def test_no_wait_prefers_ready_over_dependency_blocked(self):
        self._write("research/jobs/queued/VIRTUAL-GUITAR-BLOCKED-001.yaml",'''schema_version: "1.0"
job_id: VIRTUAL-GUITAR-BLOCKED-001
state: QUEUED
priority: 99
track: {id: VIRTUAL_GUITAR_BLOCKED}
depends_on_jobs: [VIRTUAL-GUITAR-MISSING-001]
research_question: Blocked question
''')
        self._write("research/jobs/queued/VIRTUAL-GUITAR-READY-001.yaml",'''schema_version: "1.0"
job_id: VIRTUAL-GUITAR-READY-001
state: QUEUED
priority: 20
track: {id: VIRTUAL_GUITAR_READY}
depends_on_jobs: []
research_question: Ready question
''')
        snap=build_project_snapshot(self.tmp,self.spec,resolver=self.resolver,cipi_sha="b"*40)
        self.assertEqual(snap["resume_contract"]["recommended_action"],"VIRTUAL-GUITAR-READY-001");self.assertEqual(len(snap["blocked"]),1);self.assertEqual(len(snap["ready"]),1)

    def test_human_gate_does_not_auto_resume(self):
        self._json("research/health/automation-status.json",{"schema_version":"1.0","authority":"OPERATIONAL_SCHEDULING_ONLY","human_gates":[{"job_id":"VIRTUAL-GUITAR-LISTEN-001","gates":["REAL_AUDIO_AB"]}]})
        self._write("research/jobs/queued/VIRTUAL-GUITAR-LISTEN-001.yaml",'''schema_version: "1.0"
job_id: VIRTUAL-GUITAR-LISTEN-001
state: QUEUED
track: {id: VIRTUAL_GUITAR_LISTEN}
depends_on_jobs: []
review_policy:
  required_human_gates: [REAL_AUDIO_AB]
''')
        snap=build_project_snapshot(self.tmp,self.spec,resolver=self.resolver,cipi_sha="b"*40)
        self.assertEqual(snap["resume_contract"]["resume_mode"],"HUMAN_GATE");self.assertFalse(snap["resume_contract"]["can_autonomously_resume"]);self.assertFalse(snap["ready"])

    def test_completed_research_job_human_gate_becomes_ready(self):
        self._write("research/jobs/queued/VIRTUAL-GUITAR-LISTEN-002.yaml",'''schema_version: "1.0"
job_id: VIRTUAL-GUITAR-LISTEN-002
state: QUEUED
track: {id: VIRTUAL_GUITAR_LISTEN}
depends_on_jobs: []
review_policy:
  required_human_gates: [REAL_AUDIO_AB]
''')
        self._write("research/human_gates/decisions/virtual_guitar/VIRTUAL-GUITAR-LISTEN-002/REAL_AUDIO_AB/1.yaml",'''schema_version: "1.0"
project_id: virtual_guitar
target_type: RESEARCH_JOB
target_id: VIRTUAL-GUITAR-LISTEN-002
gate: REAL_AUDIO_AB
outcome: COMPLETE
operational_effect: RESOLVE_RESEARCH_JOB_GATE
created_at: "2026-09-29T00:00:00Z"
''')
        snap=build_project_snapshot(self.tmp,self.spec,resolver=self.resolver,cipi_sha="b"*40)
        self.assertEqual(snap["phase"],"AUTO_READY")
        self.assertTrue(snap["resume_contract"]["can_autonomously_resume"])
        self.assertEqual(snap["ready"][0]["resolved_human_gates"],["REAL_AUDIO_AB"])
        self.assertFalse(snap["human_gates"])

    def test_unverified_product_ref_is_stale(self):
        snap=build_project_snapshot(self.tmp,self.spec,resolver=lambda repo,ref,token:None,cipi_sha="b"*40)
        self.assertEqual(snap["freshness"],"STALE");self.assertEqual(snap["resume_contract"]["resume_mode"],"REFRESH_REQUIRED");self.assertFalse(snap["resume_contract"]["can_autonomously_resume"])

    def test_track_human_gate_scheduler_conflict(self):
        self._json("research/health/autonomous-bridge.json",{"schema_version":"1.0","track_lifecycle":{"VIRTUAL-GUITAR-PHYSICAL-001":{"state":"HUMAN_GATE","scheduler_eligible":True}}})
        snap=build_project_snapshot(self.tmp,self.spec,resolver=self.resolver,cipi_sha="b"*40)
        self.assertEqual(snap["freshness"],"CONFLICT");self.assertTrue(snap["conflicts"]);self.assertFalse(snap["resume_contract"]["can_resume"])

    def test_secret_scanner(self):
        self.assertTrue(scan_for_secrets({"x":"github_pat_"+"A"*30}));self.assertTrue(scan_for_secrets("-----BEGIN PRIVATE KEY-----"));self.assertFalse(scan_for_secrets({"status":"SAFE","token_count":12}))

    def test_new_source_file_invalidates_old_snapshot(self):
        build_all(self.tmp,resolver=self.resolver,cipi_sha="b"*40,generated_at="2026-09-29T00:00:00Z",publish=True)
        self._write("research/jobs/completed/000-VIRTUAL-GUITAR-NEW-001.yaml",'schema_version: "1.0"\njob_id: VIRTUAL-GUITAR-NEW-001\nstate: DONE\n')
        errors=validate_published(self.tmp);self.assertTrue(any("source hash changed: research/jobs/completed" in x for x in errors))

    def test_rebuild_and_validate_published(self):
        snapshots=build_all(self.tmp,resolver=self.resolver,cipi_sha="b"*40,generated_at="2026-09-29T00:00:00Z",publish=True)
        self.assertIn("virtual_guitar",snapshots)
        self.assertTrue((self.tmp/"research/continuity/projects/virtual_guitar/current.json").exists());self.assertTrue((self.tmp/"research/continuity/projects/virtual_guitar/HANDOFF.md").exists());self.assertEqual(validate_published(self.tmp),[])
        shutil.rmtree(self.tmp/"research/continuity/projects")
        build_all(self.tmp,resolver=self.resolver,cipi_sha="b"*40,generated_at="2026-09-29T00:00:00Z",publish=True)
        self.assertEqual(validate_published(self.tmp),[])

if __name__=="__main__":unittest.main()
