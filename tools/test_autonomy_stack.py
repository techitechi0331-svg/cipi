from __future__ import annotations

from datetime import datetime, timezone
import io
from pathlib import Path
import tempfile
import sys
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "cross_repo"))
sys.path.insert(0, str(ROOT / "automation" / "orchestrator"))

from artifacts import extract_text_evidence, ingest_artifact  # noqa: E402
from core import select_queued_action  # noqa: E402
from failure import classify_failure  # noqa: E402
from watchdog import assess_wait  # noqa: E402
from global_dag import write_dashboard  # noqa: E402


REGISTRY = {
    "schema_version": "1.0",
    "defaults": {
        "artifact_ingest": "metadata_and_text",
        "auto_retry_transient": True,
        "max_retries": 1,
        "runner_wait_minutes": 30,
    },
    "repositories": {
        "test": {
            "repository": "techitechi0331-svg/example",
            "default_ref": "main",
            "runner_class": "self-hosted",
            "workflows": {
                "build": {"file": "build.yml", "dispatch": True, "monitor": True},
            },
        }
    },
}


def make_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("metrics.csv", "metric,value\nfoo,1\n")
        zf.writestr("nested/report.json", '{"ok":true}\n')
        zf.writestr("../evil.txt", "nope")
        zf.writestr("plugin.vst3", b"binary")
    return buffer.getvalue()


def main() -> int:
    records, extracted = extract_text_evidence(make_zip())
    assert "metrics.csv" in extracted
    assert "nested/report.json" in extracted
    assert "../evil.txt" not in extracted
    assert "plugin.vst3" not in extracted
    assert all(item["path"] != "../evil.txt" for item in records)

    transient = classify_failure(
        {"conclusion": "failure"},
        [{"steps": [{"name": "Checkout", "conclusion": "failure"}]}],
    )
    assert transient["category"] == "INFRA_TRANSIENT"
    assert transient["retry_safe"] is True

    dsp = classify_failure(
        {"conclusion": "failure"},
        [{"steps": [{"name": "Run DSP Tests Release", "conclusion": "failure"}]}],
    )
    assert dsp["category"] == "PRODUCT_OR_TEST_FAILURE"
    assert dsp["retry_safe"] is False

    action = {
        "action_id": "TEST-ACTION-001",
        "repo_key": "test",
        "workflow_key": "build",
        "dispatched_at": "2026-09-26T00:00:00Z",
    }
    health = assess_wait(
        action,
        {"id": 1, "status": "queued", "created_at": "2026-09-26T00:00:00Z", "conclusion": None},
        runner_class="self-hosted",
        runner_wait_minutes=20,
        now=datetime(2026, 9, 26, 0, 25, tzinfo=timezone.utc),
    )
    assert health["state"] == "RUNNER_WAIT"
    assert "age_minutes" not in health

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        queued = root / "research/cross_repo/actions/queued"
        queued.mkdir(parents=True)
        pending = {
            "schema_version": "1.0",
            "action_id": "TEST-DAG-001",
            "state": "QUEUED",
            "repo_key": "test",
            "workflow_key": "build",
            "ref": "main",
            "inputs": {},
            "priority": 5,
            "attempts": 0,
            "max_attempts": 2,
            "retry_count": 0,
            "max_retries": 1,
            "depends_on_jobs": ["JOB-001"],
        }
        (queued / "action.yaml").write_text(yaml.safe_dump(pending, sort_keys=False), encoding="utf-8")
        assert select_queued_action(root, REGISTRY) is None

        completed = root / "research/jobs/completed"
        completed.mkdir(parents=True)
        (completed / "job.yaml").write_text(
            yaml.safe_dump({"job_id": "JOB-001", "state": "COMPLETED"}),
            encoding="utf-8",
        )
        selected = select_queued_action(root, REGISTRY)
        assert selected is not None and selected[1]["action_id"] == "TEST-DAG-001"

        artifact = {
            "id": 123,
            "name": "measurement-results",
            "expired": False,
            "size_in_bytes": len(make_zip()),
            "created_at": "2026-09-26T00:00:00Z",
            "expires_at": "2026-10-01T00:00:00Z",
        }
        assert ingest_artifact(
            root,
            repo_key="test",
            repo="techitechi0331-svg/example",
            run_id=99,
            run_attempt=1,
            artifact=artifact,
            archive_bytes=make_zip(),
        )
        manifest = root / "research/cross_repo/artifacts/test/99/123/manifest.yaml"
        assert manifest.exists()
        m = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        assert m["authority"] == "EXTERNAL_ARTIFACT_EVIDENCE_ONLY"
        assert m["automatic_knowledge_promotion"] is False

        snapshot = {
            "schema_version": "1.0",
            "selected": {"kind": "IDLE", "priority": -999},
            "local": {
                "ready_job": None,
                "claimed_count": 0,
                "blocked_count": 1,
                "dependency_blocked_count": 1,
                "claimed_jobs": [],
                "claimed_branches": [],
            },
            "cross_repo": {
                "enabled": False,
                "states": {"queued": 1, "dispatched": 0, "completed": 0, "failed": 0, "quarantined": 0},
                "ready_action": None,
                "health_alerts": [],
            },
            "human_gates": [],
            "authority": "OPERATIONAL_SCHEDULING_ONLY",
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
        }
        assert write_dashboard(root, snapshot) is True
        assert write_dashboard(root, snapshot) is False

    print("CIPI autonomy stack tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
