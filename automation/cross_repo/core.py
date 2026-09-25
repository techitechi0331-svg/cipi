from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import re
import yaml

ACTION_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,95}$")
ACTION_STATES = {"QUEUED", "DISPATCHED", "COMPLETED", "FAILED", "CANCELLED", "QUARANTINED"}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def load_registry(path: Path) -> dict[str, Any]:
    data = load_yaml(path)
    if data.get("schema_version") != "1.0":
        raise ValueError("cross-repo registry schema_version must be 1.0")
    repos = data.get("repositories")
    if not isinstance(repos, dict) or not repos:
        raise ValueError("cross-repo registry requires repositories")
    for repo_key, repo in repos.items():
        if not isinstance(repo, dict):
            raise ValueError(f"registry repository {repo_key} must be a mapping")
        name = str(repo.get("repository", ""))
        if not name.startswith("techitechi0331-svg/"):
            raise ValueError(f"registry repository {repo_key} is outside the approved owner")
        if not str(repo.get("default_ref", "")):
            raise ValueError(f"registry repository {repo_key} needs default_ref")
        workflows = repo.get("workflows")
        if not isinstance(workflows, dict) or not workflows:
            raise ValueError(f"registry repository {repo_key} needs workflows")
        for workflow_key, workflow in workflows.items():
            if not isinstance(workflow, dict):
                raise ValueError(f"workflow {repo_key}/{workflow_key} must be a mapping")
            wf = str(workflow.get("file", ""))
            if not wf.endswith((".yml", ".yaml")) or "/" in wf or ".." in wf:
                raise ValueError(f"unsafe workflow filename {repo_key}/{workflow_key}: {wf!r}")
            if not isinstance(workflow.get("dispatch", False), bool):
                raise ValueError(f"workflow {repo_key}/{workflow_key}.dispatch must be bool")
            if not isinstance(workflow.get("monitor", False), bool):
                raise ValueError(f"workflow {repo_key}/{workflow_key}.monitor must be bool")
    return data


def validate_action(action: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    action_id = action.get("action_id")
    if not isinstance(action_id, str) or not ACTION_ID_RE.fullmatch(action_id):
        errors.append("invalid action_id")
    if action.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if action.get("state") not in ACTION_STATES:
        errors.append("invalid state")

    repo_key = str(action.get("repo_key", ""))
    workflow_key = str(action.get("workflow_key", ""))
    repos = registry.get("repositories", {})
    repo = repos.get(repo_key)
    if not isinstance(repo, dict):
        errors.append(f"unknown repo_key {repo_key!r}")
        return errors
    workflow = repo.get("workflows", {}).get(workflow_key)
    if not isinstance(workflow, dict):
        errors.append(f"unknown workflow_key {repo_key}/{workflow_key}")
        return errors
    if action.get("state") == "QUEUED" and workflow.get("dispatch") is not True:
        errors.append(f"workflow {repo_key}/{workflow_key} is monitor-only")

    ref = action.get("ref", repo.get("default_ref"))
    if not isinstance(ref, str) or not ref or any(ch.isspace() for ch in ref):
        errors.append("invalid ref")
    inputs = action.get("inputs", {})
    if not isinstance(inputs, dict):
        errors.append("inputs must be a mapping")
    else:
        for key, value in inputs.items():
            if not isinstance(key, str) or not key:
                errors.append("input keys must be non-empty strings")
            if not isinstance(value, (str, int, float, bool)):
                errors.append(f"input {key!r} must be scalar")
    attempts = action.get("attempts", 0)
    max_attempts = action.get("max_attempts", 2)
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
        errors.append("attempts must be a non-negative integer")
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or not 1 <= max_attempts <= 3:
        errors.append("max_attempts must be 1..3")
    if isinstance(attempts, int) and isinstance(max_attempts, int) and attempts > max_attempts:
        errors.append("attempts may not exceed max_attempts")
    return errors


def workflow_spec(registry: dict[str, Any], action: dict[str, Any]) -> tuple[str, str, str]:
    repo = registry["repositories"][action["repo_key"]]
    workflow = repo["workflows"][action["workflow_key"]]
    return str(repo["repository"]), str(workflow["file"]), str(action.get("ref") or repo["default_ref"])


def select_queued_action(root: Path, registry: dict[str, Any]) -> tuple[Path, dict[str, Any]] | None:
    queued = root / "research" / "cross_repo" / "actions" / "queued"
    dispatched = root / "research" / "cross_repo" / "actions" / "dispatched"
    active: set[tuple[str, str]] = set()
    if dispatched.exists():
        for path in sorted(dispatched.glob("*.yaml")):
            data = load_yaml(path)
            active.add((str(data.get("repo_key", "")), str(data.get("workflow_key", ""))))

    candidates: list[tuple[int, str, Path, dict[str, Any]]] = []
    if not queued.exists():
        return None
    for path in sorted(queued.glob("*.yaml")):
        action = load_yaml(path)
        errors = validate_action(action, registry)
        if errors:
            raise ValueError(f"{path}: " + "; ".join(errors))
        key = (str(action["repo_key"]), str(action["workflow_key"]))
        if key in active:
            continue
        priority = action.get("priority", 0)
        if isinstance(priority, bool) or not isinstance(priority, int):
            priority = 0
        candidates.append((-priority, str(action["action_id"]), path, action))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1], item[2].as_posix()))
    _, _, path, action = candidates[0]
    return path, action


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def match_dispatched_run(action: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    dispatched_at = parse_time(str(action["dispatched_at"]))
    earliest = dispatched_at - timedelta(seconds=30)
    previous_run_id = action.get("previous_run_id")
    ref = str(action.get("ref", ""))
    candidates = []
    for run in runs:
        if run.get("event") != "workflow_dispatch":
            continue
        run_id = run.get("id")
        if isinstance(previous_run_id, int) and isinstance(run_id, int) and run_id <= previous_run_id:
            continue
        if ref and run.get("head_branch") not in (None, ref):
            continue
        created = run.get("created_at")
        if not isinstance(created, str):
            continue
        if parse_time(created) < earliest:
            continue
        candidates.append(run)
    candidates.sort(key=lambda r: parse_time(str(r["created_at"])))
    return candidates[0] if candidates else None


def action_terminal_dir(root: Path, conclusion: str | None) -> Path:
    return root / "research" / "cross_repo" / "actions" / ("completed" if conclusion == "success" else "failed")


def event_path(root: Path, repo_key: str, run_id: int | str) -> Path:
    return root / "research" / "cross_repo" / "events" / repo_key / f"{run_id}.yaml"


def should_resume_external_job(job: dict[str, Any], completed_action_ids: set[str]) -> tuple[bool, list[str]]:
    if job.get("state") != "BLOCKED_EXTERNAL":
        return False, []
    waits = job.get("external_wait")
    if not isinstance(waits, list) or not waits:
        return False, []
    refs: list[str] = []
    for wait in waits:
        if not isinstance(wait, dict):
            return False, []
        ref = str(wait.get("ref", ""))
        if not ref.startswith("action:"):
            return False, []
        action_id = ref.split(":", 1)[1]
        refs.append(action_id)
        if action_id not in completed_action_ids:
            return False, refs
    return True, refs
