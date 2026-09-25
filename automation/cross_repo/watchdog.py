from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def assess_wait(
    action: dict[str, Any],
    run: dict[str, Any] | None,
    *,
    runner_class: str,
    runner_wait_minutes: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    dispatched_at = parse_time(str(action["dispatched_at"]))
    action_id = str(action.get("action_id", ""))
    repo_key = str(action.get("repo_key", ""))
    workflow_key = str(action.get("workflow_key", ""))

    if run is None:
        age_minutes = max(0.0, (now - dispatched_at).total_seconds() / 60.0)
        state = "DISPATCH_UNOBSERVED" if age_minutes >= 10.0 else "DISPATCH_PROPAGATING"
        return {
            "schema_version": "1.0",
            "action_id": action_id,
            "repo_key": repo_key,
            "workflow_key": workflow_key,
            "runner_class": runner_class,
            "state": state,
            "run_id": None,
            "since": action.get("dispatched_at"),
            "wait_threshold_minutes": 10,
            "blocks_only_dependent_work": True,
        }

    status = str(run.get("status") or "")
    created_at = str(run.get("created_at") or action.get("dispatched_at"))
    age_minutes = max(0.0, (now - parse_time(created_at)).total_seconds() / 60.0)

    if status == "queued" and age_minutes >= float(runner_wait_minutes):
        state = "RUNNER_WAIT"
    elif status == "queued":
        state = "QUEUED"
    elif status == "in_progress":
        state = "RUNNING"
    elif status == "completed":
        state = "COMPLETED"
    else:
        state = "UNKNOWN"

    return {
        "schema_version": "1.0",
        "action_id": action_id,
        "repo_key": repo_key,
        "workflow_key": workflow_key,
        "runner_class": runner_class,
        "state": state,
        "run_id": run.get("id"),
        "run_status": status,
        "run_conclusion": run.get("conclusion"),
        "since": created_at,
        "wait_threshold_minutes": runner_wait_minutes,
        "blocks_only_dependent_work": True,
    }
