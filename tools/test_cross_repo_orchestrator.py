from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "cross_repo"))

from core import match_dispatched_run, select_queued_action, should_resume_external_job, validate_action  # noqa: E402


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

    dispatched_action = action("TEST-RUN-001", "build", 0)
    dispatched_action["state"] = "DISPATCHED"
    dispatched_action["dispatched_at"] = "2026-09-26T00:00:00Z"
    runs = [
        {"id": 1, "event": "push", "created_at": "2026-09-26T00:00:10Z"},
        {"id": 2, "event": "workflow_dispatch", "created_at": "2026-09-26T00:00:20Z"},
    ]
    matched = match_dispatched_run(dispatched_action, runs)
    assert matched is not None and matched["id"] == 2

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
