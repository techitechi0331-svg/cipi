from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import re
import yaml

ACTION_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,95}$")
JOB_ID_RE = ACTION_ID_RE
ACTION_STATES = {"QUEUED", "DISPATCHED", "COMPLETED", "FAILED", "CANCELLED", "QUARANTINED"}
RUNNER_CLASSES = {"self-hosted", "github-hosted"}
ARTIFACT_MODES = {"off", "metadata_only", "metadata_and_text"}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_yaml_if_changed(path: Path, data: dict[str, Any]) -> bool:
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def load_registry(path: Path) -> dict[str, Any]:
    data = load_yaml(path)
    if data.get("schema_version") != "1.0":
        raise ValueError("cross-repo registry schema_version must be 1.0")
    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("cross-repo registry defaults must be a mapping")
    if defaults.get("artifact_ingest", "metadata_and_text") not in ARTIFACT_MODES:
        raise ValueError("registry defaults.artifact_ingest is invalid")
    if not isinstance(defaults.get("auto_retry_transient", True), bool):
        raise ValueError("registry defaults.auto_retry_transient must be bool")
    max_retries = defaults.get("max_retries", 1)
    if isinstance(max_retries, bool) or not isinstance(max_retries, int) or not 0 <= max_retries <= 2:
        raise ValueError("registry defaults.max_retries must be 0..2")
    runner_wait = defaults.get("runner_wait_minutes", 30)
    if isinstance(runner_wait, bool) or not isinstance(runner_wait, int) or not 5 <= runner_wait <= 180:
        raise ValueError("registry defaults.runner_wait_minutes must be 5..180")

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
        runner_class = repo.get("runner_class", "github-hosted")
        if runner_class not in RUNNER_CLASSES:
            raise ValueError(f"registry repository {repo_key}.runner_class is invalid")
        repo_wait = repo.get("runner_wait_minutes", runner_wait)
        if isinstance(repo_wait, bool) or not isinstance(repo_wait, int) or not 5 <= repo_wait <= 180:
            raise ValueError(f"registry repository {repo_key}.runner_wait_minutes must be 5..180")
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
            if workflow.get("runner_class", runner_class) not in RUNNER_CLASSES:
                raise ValueError(f"workflow {repo_key}/{workflow_key}.runner_class is invalid")
            mode = workflow.get("artifact_ingest", defaults.get("artifact_ingest", "metadata_and_text"))
            if mode not in ARTIFACT_MODES:
                raise ValueError(f"workflow {repo_key}/{workflow_key}.artifact_ingest is invalid")
            retry = workflow.get("auto_retry_transient", defaults.get("auto_retry_transient", True))
            if not isinstance(retry, bool):
                raise ValueError(f"workflow {repo_key}/{workflow_key}.auto_retry_transient must be bool")
            allowed_inputs = workflow.get("allowed_inputs")
            required_inputs = workflow.get("required_inputs")
            if allowed_inputs is not None:
                if not isinstance(allowed_inputs, list) or not all(isinstance(x, str) and x for x in allowed_inputs):
                    raise ValueError(f"workflow {repo_key}/{workflow_key}.allowed_inputs must be a string list")
                if len(set(allowed_inputs)) != len(allowed_inputs):
                    raise ValueError(f"workflow {repo_key}/{workflow_key}.allowed_inputs contains duplicates")
            if required_inputs is not None:
                if not isinstance(required_inputs, list) or not all(isinstance(x, str) and x for x in required_inputs):
                    raise ValueError(f"workflow {repo_key}/{workflow_key}.required_inputs must be a string list")
                if len(set(required_inputs)) != len(required_inputs):
                    raise ValueError(f"workflow {repo_key}/{workflow_key}.required_inputs contains duplicates")
                if allowed_inputs is not None and not set(required_inputs) <= set(allowed_inputs):
                    raise ValueError(f"workflow {repo_key}/{workflow_key}.required_inputs must be allowed")
    return data


def workflow_policy(registry: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    defaults = registry.get("defaults", {})
    repo = registry["repositories"][action["repo_key"]]
    workflow = repo["workflows"][action["workflow_key"]]
    return {
        "runner_class": workflow.get("runner_class", repo.get("runner_class", "github-hosted")),
        "runner_wait_minutes": workflow.get(
            "runner_wait_minutes",
            repo.get("runner_wait_minutes", defaults.get("runner_wait_minutes", 30)),
        ),
        "artifact_ingest": workflow.get("artifact_ingest", defaults.get("artifact_ingest", "metadata_and_text")),
        "auto_retry_transient": workflow.get(
            "auto_retry_transient",
            defaults.get("auto_retry_transient", True),
        ),
        "max_retries": workflow.get("max_retries", defaults.get("max_retries", 1)),
    }


def _validate_id_list(action: dict[str, Any], key: str, pattern: re.Pattern[str], errors: list[str]) -> None:
    values = action.get(key, [])
    if not isinstance(values, list):
        errors.append(f"{key} must be a list")
        return
    seen: set[str] = set()
    for value in values:
        text = str(value)
        if not pattern.fullmatch(text):
            errors.append(f"invalid {key} entry {text!r}")
        if text in seen:
            errors.append(f"duplicate {key} entry {text!r}")
        seen.add(text)


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
        allowed_inputs = workflow.get("allowed_inputs")
        if isinstance(allowed_inputs, list):
            unknown = sorted(set(inputs) - set(allowed_inputs))
            if unknown:
                errors.append(f"unsupported workflow inputs: {unknown}")
        required_inputs = workflow.get("required_inputs")
        if isinstance(required_inputs, list):
            missing_inputs = sorted(set(required_inputs) - set(inputs))
            if missing_inputs:
                errors.append(f"missing required workflow inputs: {missing_inputs}")

    _validate_id_list(action, "depends_on_jobs", JOB_ID_RE, errors)
    _validate_id_list(action, "depends_on_actions", ACTION_ID_RE, errors)
    if isinstance(action_id, str) and action_id in action.get("depends_on_actions", []):
        errors.append("action may not depend on itself")

    priority = action.get("priority", 0)
    if isinstance(priority, bool) or not isinstance(priority, int) or not -100 <= priority <= 100:
        errors.append("priority must be an integer from -100 to 100")

    attempts = action.get("attempts", 0)
    max_attempts = action.get("max_attempts", 2)
    retry_count = action.get("retry_count", 0)
    max_retries = action.get("max_retries", workflow_policy(registry, action)["max_retries"])
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
        errors.append("attempts must be a non-negative integer")
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or not 1 <= max_attempts <= 3:
        errors.append("max_attempts must be 1..3")
    if isinstance(attempts, int) and isinstance(max_attempts, int) and attempts > max_attempts:
        errors.append("attempts may not exceed max_attempts")
    if isinstance(retry_count, bool) or not isinstance(retry_count, int) or retry_count < 0:
        errors.append("retry_count must be a non-negative integer")
    if isinstance(max_retries, bool) or not isinstance(max_retries, int) or not 0 <= max_retries <= 2:
        errors.append("max_retries must be 0..2")
    if isinstance(retry_count, int) and isinstance(max_retries, int) and retry_count > max_retries:
        errors.append("retry_count may not exceed max_retries")
    return errors


def workflow_spec(registry: dict[str, Any], action: dict[str, Any]) -> tuple[str, str, str]:
    repo = registry["repositories"][action["repo_key"]]
    workflow = repo["workflows"][action["workflow_key"]]
    return str(repo["repository"]), str(workflow["file"]), str(action.get("ref") or repo["default_ref"])


def completed_job_ids(root: Path) -> set[str]:
    folder = root / "research" / "jobs" / "completed"
    ids: set[str] = set()
    if not folder.exists():
        return ids
    for path in [*folder.glob("*.yaml"), *folder.glob("*.yml")]:
        data = load_yaml(path)
        if data.get("state") == "COMPLETED" and data.get("job_id"):
            ids.add(str(data["job_id"]))
    return ids


def completed_action_ids(root: Path) -> set[str]:
    folder = root / "research" / "cross_repo" / "actions" / "completed"
    ids: set[str] = set()
    if not folder.exists():
        return ids
    for path in folder.glob("*.yaml"):
        data = load_yaml(path)
        if data.get("state") == "COMPLETED" and data.get("action_id"):
            ids.add(str(data["action_id"]))
    return ids


def action_dependencies_ready(root: Path, action: dict[str, Any]) -> bool:
    return (
        set(map(str, action.get("depends_on_jobs", []))) <= completed_job_ids(root)
        and set(map(str, action.get("depends_on_actions", []))) <= completed_action_ids(root)
    )


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
        if not action_dependencies_ready(root, action):
            continue
        key = (str(action["repo_key"]), str(action["workflow_key"]))
        if key in active:
            continue
        priority = int(action.get("priority", 0))
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


def event_path(root: Path, repo_key: str, run_id: int | str, run_attempt: int | str = 1) -> Path:
    return root / "research" / "cross_repo" / "events" / repo_key / f"{run_id}-attempt-{run_attempt}.yaml"


def should_resume_external_job(job: dict[str, Any], completed_actions: set[str]) -> tuple[bool, list[str]]:
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
        if action_id not in completed_actions:
            return False, refs
    return True, refs
