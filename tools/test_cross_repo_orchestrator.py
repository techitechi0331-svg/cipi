from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import io
import tempfile
import zipfile
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "cross_repo"))

from core import match_dispatched_run, select_queued_action, should_resume_external_job, validate_action  # noqa: E402
from orchestrate import backfill_completed_artifacts  # noqa: E402


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


def main() -> int:
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

    print("CIPI cross-repo orchestrator tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
