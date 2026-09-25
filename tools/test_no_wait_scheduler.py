from __future__ import annotations

from pathlib import Path
import tempfile
import yaml

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "queue"))

from select_job import choose_job  # noqa: E402


def write_job(root: Path, name: str, job_id: str, *, state: str = "QUEUED", priority: int = 0, deps: list[str] | None = None) -> None:
    payload = {
        "schema_version": "1.0",
        "job_id": job_id,
        "state": state,
        "track": {"id": "TEST", "path": "research/test"},
        "research_question": "Does the no-wait scheduler choose ready work?",
        "hypothesis": "The scheduler skips blocked work and steals a ready task.",
        "counter_hypotheses": ["The scheduler stops at the first blocked task."],
        "baseline": ["baseline"],
        "variants": ["candidate"],
        "metrics": ["score"],
        "acceptance": ["candidate is selected"],
        "rejection": ["no ready job is selected"],
        "max_runs": 1,
        "timeout_minutes": 1,
        "priority": priority,
    }
    if deps:
        payload["depends_on_jobs"] = deps
    (root / name).write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def write_completed(root: Path, name: str, job_id: str) -> None:
    payload = {
        "schema_version": "1.0",
        "job_id": job_id,
        "state": "COMPLETED",
        "track": {"id": "TEST", "path": "research/test"},
        "research_question": "Completed dependency record for scheduler test.",
        "hypothesis": "The dependency is complete for scheduler testing.",
        "counter_hypotheses": ["The dependency is not complete."],
        "baseline": ["baseline"],
        "variants": ["candidate"],
        "metrics": ["score"],
        "acceptance": ["completed"],
        "rejection": ["not completed"],
        "max_runs": 1,
        "timeout_minutes": 1,
    }
    (root / name).write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        queued = base / "queued"
        completed = base / "completed"
        queued.mkdir()
        completed.mkdir()

        write_job(queued, "001-high.yaml", "HIGH-BLOCKED-001", priority=100, deps=["DEP-001"])
        write_job(queued, "002-explicit.yaml", "EXTERNAL-001", state="BLOCKED_EXTERNAL", priority=90)
        write_job(queued, "003-ready.yaml", "READY-001", priority=10)

        selected, stats = choose_job(queued, completed, branch_exists=lambda _: False)
        assert selected is not None and selected[1] == "READY-001"
        assert stats["skipped_dependency"] == 1
        assert stats["skipped_blocked"] == 1
        assert stats["work_steal"] is True

        write_completed(completed, "dep.yaml", "DEP-001")
        selected, stats = choose_job(queued, completed, branch_exists=lambda _: False)
        assert selected is not None and selected[1] == "HIGH-BLOCKED-001"
        assert stats["skipped_dependency"] == 0

        claimed_branch = selected[3]
        selected, stats = choose_job(queued, completed, branch_exists=lambda branch: branch == claimed_branch)
        assert selected is not None and selected[1] == "READY-001"
        assert stats["skipped_claimed"] == 1
        assert stats["work_steal"] is True

    print("CIPI no-wait scheduler tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
