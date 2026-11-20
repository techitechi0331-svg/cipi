from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import io
import json
import hashlib
import tempfile
import zipfile
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "cross_repo"))

from core import match_dispatched_run, select_queued_action, should_resume_external_job, validate_action  # noqa: E402
from orchestrate import _workflow_time_metrics, backfill_completed_artifacts, reconcile_retried_failed_actions, ingest_melon_outbox_recoveries  # noqa: E402
from failure import classify_failure  # noqa: E402
from artifacts import ingest_artifact, extract_public_melon_evidence, project_public_melon_macro  # noqa: E402


REGISTRY = {
    "schema_version": "1.0",
    "repositories": {
        "test": {
            "repository": "techitechi0331-svg/example",
            "default_ref": "main",
            "workflows": {
                "build": {"file": "build.yml", "dispatch": True, "monitor": True},
                "monitor": {"file": "monitor.yml", "dispatch": False, "monitor": True},
            },
        }
    },
}


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def action(action_id: str, workflow: str, priority: int) -> dict:
    return {
        "schema_version": "1.0",
        "action_id": action_id,
        "state": "QUEUED",
        "repo_key": "test",
        "workflow_key": workflow,
        "ref": "main",
        "inputs": {},
        "priority": priority,
        "attempts": 0,
        "max_attempts": 2,
    }


def test_workflow_time_metrics_split_queue_and_runner_wall():
    metrics = _workflow_time_metrics({
        "created_at": "2026-09-26T00:00:00Z",
        "run_started_at": "2026-09-26T00:01:00Z",
        "updated_at": "2026-09-26T00:06:00Z",
    })
    assert metrics["queue_wait_seconds"] == 60.0
    assert metrics["runner_job_seconds"] == 300.0
    assert metrics["total_wall_seconds"] == 360.0
    assert metrics["research_compute_seconds"] is None


class FakeArtifactClient:
    def list_run_artifacts(self, repo: str, run_id: int) -> list[dict]:
        return [{
            "id": 777,
            "name": "measurement-results",
            "expired": False,
            "size_in_bytes": 256,
            "created_at": "2026-09-26T00:00:00Z",
            "expires_at": "2026-10-26T00:00:00Z",
        }]

    def download_artifact_zip(self, repo: str, artifact_id: int) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("macro_result.json", '{"schema_version":"1.0","ok":true}\n')
        return buffer.getvalue()


class FakeRecoveryClient(FakeArtifactClient):
    def list_workflow_runs(self, repo: str, workflow_file: str, per_page: int = 15) -> list[dict]:
        return [{
            "id": 123,
            "run_attempt": 2,
            "status": "completed",
            "conclusion": "success",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": "abc123",
            "created_at": "2026-09-26T00:00:00Z",
            "updated_at": "2026-09-26T00:05:00Z",
            "run_started_at": "2026-09-26T00:01:00Z",
            "html_url": "https://github.com/techitechi0331-svg/example/actions/runs/123",
        }]


def test_public_artifact_redaction() -> None:
    private = {
        "schema_version": "1.0", "result_type": "MELON_MACRO_RESEARCH_RESULT",
        "track_id": "SAFE-TRACK-001", "run_id": "melon-funnel-123",
        "job_id": "SAFE-JOB-001", "parent_run_id": None, "parent_job_id": None,
        "root_research_id": "SAFE-TRACK-001", "research_id": "SAFE-TRACK-001",
        "hypothesis_id": "SAFE-HYP", "experiment_id": "SAFE-EXP",
        "loop_depth": 1, "source_commit": "a" * 40,
        "timestamp": "2026-11-20T00:00:00Z", "route": "CONTINUE",
        "result": {"improvement_signal": 0.123, "deep_validation_count": 1,
                   "precision_review_passed": True,
                   "private_message": "client@example.com PRIVATE KEY DATA"},
        "reason": "client@example.com github_pat_PRIVATE_TOKEN_SHOULD_NEVER_LEAK",
        "research_question": "Confidential client@example.com",
        "evidence_class": "MEASURED", "confidence": 0.85,
        "novelty": 0.21, "regression_status": "NO_REGRESSION_SIGNAL",
        "experiment_cost": {
            "candidates": 8, "deep_validation_count": 1,
            "runtime_seconds": 12.3, "stage2_measurement_runs": 2,
        },
        "elapsed_seconds": 12.3, "measured_candidates": 8,
        "stop_reason": "ITERATION", "unresolved_questions": [
            "private personal info: client@example.com"
        ],
        "continuation_candidates": [{
            "reason": "sensitive client@example.com", "inputs": {"secret": "DO_NOT_PUBLISH"}
        }],
        "automatic_final_decision": False,
        "cipi_promotion_authority": False, "product_release_authority": False,
        "bundle_hash": "placeholder",
    }
    raw = json.dumps(private).encode("utf-8")
    sanitized = project_public_melon_macro(raw)
    assert b"client@example.com" not in sanitized
    assert b"DO_NOT_PUBLISH" not in sanitized
    assert b"PRIVATE_TOKEN" not in sanitized
    summary = json.loads(sanitized)
    assert summary["route"] == "HUMAN_GATE"
    assert summary["continuation_candidates"] == []
    assert summary["private_source_sha256"] == hashlib.sha256(raw).hexdigest()
    digest = summary.pop("bundle_hash")
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert digest == hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("melon-funnel-123/macro_result.json", raw)
        archive.writestr("melon-funnel-123/console.log", "secret@example.com")
    records, extracted = extract_public_melon_evidence(buffer.getvalue())
    assert len(records) == 1 and len(extracted) == 1
    assert all(b"secret@example.com" not in v for v in extracted.values())
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        meta = {"id": 991, "name": "client@example.com private artifact",
                "expired": False, "size_in_bytes": 999}
        assert ingest_artifact(root, repo_key="melon", repo="private/melon",
                               run_id=123, run_attempt=1, artifact=meta,
                               archive_bytes=buffer.getvalue())
        public = (root / "research/cross_repo/artifacts/melon/123/991")
        manifest = yaml.safe_load((public / "manifest.yaml").read_text(encoding="utf-8"))
        assert manifest["artifact_name"] == "PRIVATE_ARTIFACT_REDACTED"
        assert manifest["ingest_status"] == "private_redacted_public_metrics_only"
        files = list((public / "files").rglob("*"))
        assert len([p for p in files if p.is_file()]) == 1
        # A non-MELON private project cannot inject raw logs regardless
        # of the caller erroneously passing an archive.
        assert ingest_artifact(root, repo_key="black76", repo="private/black76",
                               run_id=456, run_attempt=1, artifact=meta,
                               archive_bytes=buffer.getvalue())
        other = root / "research/cross_repo/artifacts/black76/456/991"
        assert not (other / "files").exists()


class FakeOutboxRecoveryClient(FakeArtifactClient):
    def list_workflow_runs(self, repo: str, workflow_file: str, per_page: int = 20) -> list[dict]:
        assert workflow_file == "melon-artifact-recovery.yml"
        return [{
            "id": 901, "run_attempt": 1, "status": "completed",
            "conclusion": "success", "event": "workflow_dispatch",
        }]


def test_melon_outbox_recovery_idempotency() -> None:
    live_registry = yaml.safe_load(
        (ROOT / "automation/cross_repo/registry.yaml").read_text(encoding="utf-8")
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        client = FakeOutboxRecoveryClient()
        ingested, markers = ingest_melon_outbox_recoveries(root, live_registry, client)
        assert (ingested, markers) == (1, 1)
        marker = root / "research/cross_repo/recovery_intake/melon/901.yaml"
        assert marker.exists()
        assert "PRIVATE_OUTBOX_UPLOAD_ONLY_REPLAY" in marker.read_text(encoding="utf-8")
        artifact = root / "research/cross_repo/artifacts/melon/901/777/manifest.yaml"
        assert artifact.exists()
        manifest = yaml.safe_load(artifact.read_text(encoding="utf-8"))
        # The fake private JSON lacks required fields; fail closed.
        assert manifest["ingest_status"] == "private_evidence_quarantined"
        assert ingest_melon_outbox_recoveries(root, live_registry, client) == (0, 0)


def main() -> int:
    test_public_artifact_redaction()
    test_melon_outbox_recovery_idempotency()
    # The legacy VoPriPro workflows must not be dispatched under VL2A.
    live_registry = yaml.safe_load(
        (ROOT / "automation/cross_repo/registry.yaml").read_text(encoding="utf-8")
    )
    vl2a = live_registry["repositories"]["vl2a"]["workflows"]
    vopripro = live_registry["repositories"]["vopripro"]["workflows"]
    assert vl2a["build"]["dispatch"] is False
    assert vl2a["real_vocal"]["dispatch"] is False
    assert vl2a["prehost_stage"]["dispatch"] is True
    assert vopripro["build"]["file"] == "build-windows.yml"
    assert vopripro["real_vocal"]["file"] == "real-vocal-validation.yml"
    wrong_product = action("TEST-WRONG-PRODUCT-001", "build", 10)
    wrong_product["repo_key"] = "vl2a"
    assert any(
        "monitor-only" in err for err in validate_action(wrong_product, live_registry)
    )

    a = action("TEST-ACTION-001", "build", 20)
    assert validate_action(a, REGISTRY) == []
    invalid = action("TEST-ACTION-002", "monitor", 10)
    assert any("monitor-only" in e for e in validate_action(invalid, REGISTRY))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        queued = root / "research/cross_repo/actions/queued"
        dispatched = root / "research/cross_repo/actions/dispatched"
        write(queued / "low.yaml", action("TEST-LOW-001", "build", 1))
        write(queued / "high.yaml", action("TEST-HIGH-001", "build", 10))

        selected = select_queued_action(root, REGISTRY)
        assert selected is not None and selected[1]["action_id"] == "TEST-HIGH-001"

        # Pending per-track policy gates must never dispatch before the Safe Handoff rollout
        # is marked APPLIED. A lower-priority APPLIED action remains eligible.
        for existing in queued.glob("*.yaml"):
            existing.unlink()
        pending_policy = action("TEST-POLICY-PENDING-001", "build", 100)
        pending_policy["policy_gate"] = {
            "policy_id": "VIRTUAL-GUITAR-EFFICIENCY-V2.3",
            "state": "PENDING_REGRESSION",
        }
        applied_policy = action("TEST-POLICY-APPLIED-001", "build", 10)
        applied_policy["policy_gate"] = {
            "policy_id": "VIRTUAL-GUITAR-EFFICIENCY-V2.3",
            "state": "APPLIED",
        }
        write(queued / "pending-policy.yaml", pending_policy)
        write(queued / "applied-policy.yaml", applied_policy)
        selected = select_queued_action(root, REGISTRY)
        assert selected is not None and selected[1]["action_id"] == "TEST-POLICY-APPLIED-001"

        active = action("TEST-ACTIVE-001", "build", 0)
        active["state"] = "DISPATCHED"
        active["dispatched_at"] = "2026-09-26T00:00:00Z"
        write(dispatched / "active.yaml", active)
        assert select_queued_action(root, REGISTRY) is None

        completed = root / "research/cross_repo/actions/completed"
        finished = action("TEST-COMPLETED-001", "build", 0)
        finished["state"] = "COMPLETED"
        finished["run_id"] = 123
        finished["conclusion"] = "success"
        write(completed / "completed.yaml", finished)
        created = backfill_completed_artifacts(root, REGISTRY, FakeArtifactClient())
        assert created == 1
        manifests = list((root / "research/cross_repo/artifacts/test/123").rglob("manifest.yaml"))
        assert len(manifests) == 1
        assert backfill_completed_artifacts(root, REGISTRY, FakeArtifactClient()) == 0

    dispatched_action = action("TEST-RUN-001", "build", 0)
    dispatched_action["state"] = "DISPATCHED"
    dispatched_action["dispatched_at"] = "2026-09-26T00:00:00Z"
    dispatched_action["previous_run_id"] = 10
    dispatched_action["ref"] = "main"
    runs = [
        {"id": 9, "event": "workflow_dispatch", "created_at": "2026-09-26T00:00:10Z", "head_branch": "main"},
        {"id": 11, "event": "push", "created_at": "2026-09-26T00:00:10Z", "head_branch": "main"},
        {"id": 12, "event": "workflow_dispatch", "created_at": "2026-09-26T00:00:20Z", "head_branch": "other"},
        {"id": 13, "event": "workflow_dispatch", "created_at": "2026-09-26T00:00:20Z", "head_branch": "main"},
    ]
    matched = match_dispatched_run(dispatched_action, runs)
    assert matched is not None and matched["id"] == 13

    # Two matching manual dispatches are ambiguous without a dispatch nonce.
    unrelated_manual = dict(runs[-1], id=14, head_sha="different")
    assert match_dispatched_run(dispatched_action, runs + [unrelated_manual]) is None
    pinned_action = dict(dispatched_action, expected_source_sha="expected")
    source_pinned = dict(runs[-1], id=15, head_sha="expected")
    source_match = match_dispatched_run(pinned_action, runs + [unrelated_manual, source_pinned])
    assert source_match is not None and source_match["id"] == 15

    job = {
        "state": "BLOCKED_EXTERNAL",
        "external_wait": [
            {"kind": "GITHUB_ACTIONS", "ref": "action:TEST-RUN-001", "resume_when": "success", "resume_step": "review evidence"}
        ],
    }
    resume, refs = should_resume_external_job(job, {"TEST-RUN-001"})
    assert resume is True and refs == ["TEST-RUN-001"]
    resume, _ = should_resume_external_job(job, set())
    assert resume is False



    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        failed_dir = root / "research/cross_repo/actions/failed"
        failed_action = action("TEST-RECOVERY-001", "build", 0)
        failed_action.update({
            "state": "FAILED",
            "run_id": 123,
            "conclusion": "failure",
            "dispatched_at": "2026-09-26T00:00:00Z",
            "failure_classification": {"category": "INFRA_TRANSIENT"},
        })
        write(failed_dir / "recover.yaml", failed_action)
        write(
            root / "research/cross_repo/failures/test/123-attempt-1.yaml",
            {"schema_version": "1.0", "run_id": 123, "run_attempt": 1},
        )
        recovered = reconcile_retried_failed_actions(root, REGISTRY, FakeRecoveryClient())
        assert recovered["recovered"] == 1
        assert recovered["artifacts"] == 1
        completed_path = root / "research/cross_repo/actions/completed/recover.yaml"
        assert completed_path.exists()
        completed_action = yaml.safe_load(completed_path.read_text(encoding="utf-8"))
        assert completed_action["state"] == "COMPLETED"
        assert completed_action["run_attempt"] == 2
        assert completed_action["recovered_from_failed_attempt"] == 1
        assert not (failed_dir / "recover.yaml").exists()

    # A failed upload is not safe to rerun without the actual cause.
    upload_unknown = classify_failure(
        {"conclusion": "failure"},
        [{"steps": [{"name": "Upload research evidence", "conclusion": "failure"}]}],
    )
    assert upload_unknown["category"] == "ARTIFACT_UPLOAD_FAILURE"
    assert upload_unknown["retry_safe"] is False

    quota_failure = classify_failure(
        {"conclusion": "failure"},
        [{"steps": [{"name": "Upload research evidence", "conclusion": "failure"}]}],
        log_excerpt="##[error]Failed to CreateArtifact: Artifact storage quota has been hit.",
    )
    assert quota_failure["category"] == "STORAGE_QUOTA_EXCEEDED"
    assert quota_failure["retry_safe"] is False
    assert "quota" in quota_failure["reason"].lower()

    mixed_failure = classify_failure(
        {"conclusion": "failure"},
        [{"steps": [
            {"name": "Fetch pinned SDK", "conclusion": "failure"},
            {"name": "Upload Vocal Rider artifact", "conclusion": "failure"},
        ]}],
        log_excerpt="Artifact storage quota has been hit.",
    )
    assert mixed_failure["category"] == "STORAGE_QUOTA_EXCEEDED"
    assert mixed_failure["retry_safe"] is False

    transient = classify_failure(
        {"conclusion": "failure"},
        [{"steps": [{"name": "Download SDK", "conclusion": "failure"}]}],
    )
    assert transient["category"] == "INFRA_TRANSIENT"
    assert transient["retry_safe"] is True

    product_failure = classify_failure(
        {"conclusion": "failure"},
        [{"steps": [{"name": "Validate VST3", "conclusion": "failure"}]}],
    )
    assert product_failure["category"] == "PRODUCT_OR_TEST_FAILURE"
    assert product_failure["retry_safe"] is False
    print("CIPI cross-repo orchestrator tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
