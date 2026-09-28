from __future__ import annotations

from pathlib import Path
import tempfile
import yaml

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "queue"))

from select_job import choose_job  # noqa: E402
from validate_research_job import validate as validate_research_job  # noqa: E402


def write_job(root: Path, name: str, job_id: str, *, state: str = "QUEUED", priority: int = 0, deps: list[str] | None = None, gates: list[str] | None = None) -> None:
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
    if gates:
        payload["review_policy"] = {"required_human_gates": gates}
    if state == "BLOCKED_EXTERNAL":
        payload["external_wait"] = [{
            "kind": "GITHUB_ACTIONS",
            "ref": "run:test",
            "resume_when": "the referenced run completes",
            "resume_step": "re-evaluate the blocked test job",
        }]
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

        for path in queued.glob("*.yaml"):
            assert validate_research_job(path) == []

        invalid = queued / "004-invalid-blocked.yaml"
        write_job(queued, invalid.name, "INVALID-BLOCKED-001", state="BLOCKED_EXTERNAL", priority=-10)
        invalid_data = yaml.safe_load(invalid.read_text(encoding="utf-8"))
        invalid_data.pop("external_wait")
        invalid.write_text(yaml.safe_dump(invalid_data, sort_keys=False), encoding="utf-8")
        assert any("BLOCKED_EXTERNAL requires" in error for error in validate_research_job(invalid))
        invalid.unlink()

        selected, stats = choose_job(queued, completed, branch_exists=lambda _: False)
        assert selected is not None and selected[1] == "READY-001"
        assert stats["skipped_dependency"] == 1
        assert stats["skipped_blocked"] == 1
        assert stats["work_steal"] is True
        assert stats["blocked_jobs"] == ["EXTERNAL-001"]
        assert stats["dependency_jobs"] == ["HIGH-BLOCKED-001<-DEP-001"]

        write_completed(completed, "dep.yaml", "DEP-001")
        selected, stats = choose_job(queued, completed, branch_exists=lambda _: False)
        assert selected is not None and selected[1] == "HIGH-BLOCKED-001"
        assert stats["skipped_dependency"] == 0

        claimed_branch = selected[3]
        selected, stats = choose_job(queued, completed, branch_exists=lambda branch: branch == claimed_branch)
        assert selected is not None and selected[1] == "READY-001"
        assert stats["skipped_claimed"] == 1
        assert stats["claimed_jobs"] == ["HIGH-BLOCKED-001"]
        assert stats["claimed_branches"] == [claimed_branch]
        assert stats["work_steal"] is True

        # Human Gate safety: a high-priority job with unresolved required gates
        # must be skipped, while lower-priority READY work is stolen.
        gated = base / "research" / "jobs" / "queued"
        gated_completed = base / "research" / "jobs" / "completed"
        gated.mkdir(parents=True)
        gated_completed.mkdir(parents=True)
        write_job(gated, "001-gated.yaml", "GATED-001", priority=100, gates=["REAL_AUDIO_AB"])
        write_job(gated, "002-ready.yaml", "READY-002", priority=10)

        selected, stats = choose_job(
            gated,
            gated_completed,
            branch_exists=lambda _: False,
            human_gate_root=base,
        )
        assert selected is not None and selected[1] == "READY-002"
        assert stats["skipped_human_gate"] == 1
        assert stats["human_gate_jobs"] == ["GATED-001<-REAL_AUDIO_AB"]
        assert stats["work_steal"] is True

        decision_dir = base / "research" / "human_gates" / "decisions" / "test" / "GATED-001" / "REAL_AUDIO_AB"
        decision_dir.mkdir(parents=True)
        (decision_dir / "001.yaml").write_text(yaml.safe_dump({
            "schema_version": "1.0",
            "decision_id": "test:GATED-001:REAL_AUDIO_AB:001",
            "project_id": "test",
            "target_type": "RESEARCH_JOB",
            "target_id": "GATED-001",
            "gate": "REAL_AUDIO_AB",
            "outcome": "COMPLETE",
            "operational_effect": "RESOLVE_RESEARCH_JOB_GATE",
            "created_at": "2026-09-29T00:00:00Z",
        }, sort_keys=False), encoding="utf-8")

        selected, stats = choose_job(
            gated,
            gated_completed,
            branch_exists=lambda _: False,
            human_gate_root=base,
        )
        assert selected is not None and selected[1] == "GATED-001"
        assert stats["skipped_human_gate"] == 0

    print("CIPI no-wait scheduler tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
