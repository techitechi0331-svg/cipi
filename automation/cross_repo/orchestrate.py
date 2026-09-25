from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from artifacts import (
    MAX_ARCHIVE_BYTES,
    ingest_artifact,
    should_download_text_artifact,
)
from core import (
    action_terminal_dir,
    completed_action_ids,
    event_path,
    load_registry,
    load_yaml,
    match_dispatched_run,
    select_queued_action,
    should_resume_external_job,
    validate_action,
    workflow_policy,
    workflow_spec,
    write_yaml,
    write_yaml_if_changed,
)
from failure import classify_failure
from watchdog import assess_wait


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class GitHubClient:
    def __init__(self, token: str):
        if not token:
            raise ValueError("CIPI_CROSS_REPO_TOKEN is required")
        self.token = token

    def _request(self, method: str, url: str, payload: dict | None = None) -> bytes:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "cipi-cross-repo-orchestrator/2.0",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {url} failed: {exc.code} {detail}") from exc

    def request_json(self, method: str, url: str, payload: dict | None = None) -> dict | list | None:
        raw = self._request(method, url, payload)
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))

    def request_bytes(self, method: str, url: str, max_bytes: int) -> bytes:
        req = urllib.request.Request(
            url,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "cipi-cross-repo-orchestrator/2.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                chunks: list[bytes] = []
                total = 0
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise RuntimeError(f"artifact archive exceeds {max_bytes} byte budget")
                    chunks.append(chunk)
                return b"".join(chunks)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub artifact download failed: {exc.code} {detail}") from exc

    def list_workflow_runs(self, repo: str, workflow_file: str, per_page: int = 10) -> list[dict]:
        quoted = urllib.parse.quote(workflow_file, safe="")
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{quoted}/runs?per_page={per_page}"
        data = self.request_json("GET", url)
        if not isinstance(data, dict):
            return []
        runs = data.get("workflow_runs", [])
        return runs if isinstance(runs, list) else []

    def list_run_jobs(self, repo: str, run_id: int) -> list[dict]:
        url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"
        data = self.request_json("GET", url)
        if not isinstance(data, dict):
            return []
        jobs = data.get("jobs", [])
        return jobs if isinstance(jobs, list) else []

    def list_run_artifacts(self, repo: str, run_id: int) -> list[dict]:
        url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100"
        data = self.request_json("GET", url)
        if not isinstance(data, dict):
            return []
        artifacts = data.get("artifacts", [])
        return artifacts if isinstance(artifacts, list) else []

    def download_artifact_zip(self, repo: str, artifact_id: int) -> bytes:
        url = f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip"
        return self.request_bytes("GET", url, MAX_ARCHIVE_BYTES)

    def dispatch_workflow(self, repo: str, workflow_file: str, ref: str, inputs: dict) -> None:
        quoted = urllib.parse.quote(workflow_file, safe="")
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{quoted}/dispatches"
        payload: dict = {"ref": ref}
        if inputs:
            payload["inputs"] = {
                str(k): str(v).lower() if isinstance(v, bool) else str(v)
                for k, v in inputs.items()
            }
        self.request_json("POST", url, payload)

    def rerun_failed_jobs(self, repo: str, run_id: int) -> None:
        url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/rerun-failed-jobs"
        self.request_json("POST", url)


def append_event(
    root: Path,
    repo_key: str,
    repo: str,
    workflow_key: str,
    workflow_file: str,
    run: dict,
    source: str,
    action_id: str | None = None,
) -> bool:
    run_id = run.get("id")
    if run_id is None:
        return False
    run_attempt = int(run.get("run_attempt") or 1)
    path = event_path(root, repo_key, run_id, run_attempt)
    legacy = root / "research" / "cross_repo" / "events" / repo_key / f"{run_id}.yaml"
    if path.exists() or (run_attempt == 1 and legacy.exists()):
        return False
    event = {
        "schema_version": "1.0",
        "event_id": f"GHARUN-{run_id}-A{run_attempt}",
        "source": source,
        "repository": repo,
        "repo_key": repo_key,
        "workflow_key": workflow_key,
        "workflow_file": workflow_file,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "event": run.get("event"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "head_branch": run.get("head_branch"),
        "head_sha": run.get("head_sha"),
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"),
        "run_started_at": run.get("run_started_at"),
        "html_url": run.get("html_url"),
        "action_id": action_id,
        "authority": "EXTERNAL_WORKFLOW_EVIDENCE_ONLY",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
    }
    write_yaml(path, event)
    return True


def write_failure_record(
    root: Path,
    *,
    repo_key: str,
    action: dict[str, Any],
    run: dict[str, Any],
    classification: dict[str, Any],
    retry_requested: bool,
) -> bool:
    run_id = int(run["id"])
    run_attempt = int(run.get("run_attempt") or 1)
    path = root / "research" / "cross_repo" / "failures" / repo_key / f"{run_id}-attempt-{run_attempt}.yaml"
    if path.exists():
        return False
    payload = {
        "schema_version": "1.0",
        "action_id": action.get("action_id"),
        "repo_key": repo_key,
        "workflow_key": action.get("workflow_key"),
        "run_id": run_id,
        "run_attempt": run_attempt,
        "head_sha": run.get("head_sha"),
        "classification": classification,
        "retry_requested": retry_requested,
        "authority": "AUTOMATED_FAILURE_CLASSIFICATION_ONLY",
        "automatic_product_decision": False,
    }
    write_yaml(path, payload)
    return True


def ingest_run_artifacts(
    root: Path,
    *,
    gh: GitHubClient,
    repo_key: str,
    repo: str,
    run: dict[str, Any],
    mode: str,
) -> int:
    if mode == "off":
        return 0
    run_id = int(run["id"])
    run_attempt = int(run.get("run_attempt") or 1)
    created = 0
    try:
        artifacts = gh.list_run_artifacts(repo, run_id)
    except RuntimeError as exc:
        print(f"artifact listing warning: {repo_key}/{run_id}: {exc}")
        return 0

    for artifact in artifacts:
        archive: bytes | None = None
        name = str(artifact.get("name") or "")
        should_download = (
            mode == "metadata_and_text"
            and not bool(artifact.get("expired"))
            and should_download_text_artifact(name)
        )
        if should_download:
            artifact_id = artifact.get("id")
            size = artifact.get("size_in_bytes")
            if isinstance(size, int) and size <= MAX_ARCHIVE_BYTES and isinstance(artifact_id, int):
                try:
                    archive = gh.download_artifact_zip(repo, artifact_id)
                except RuntimeError as exc:
                    print(f"artifact download warning: {repo_key}/{artifact_id}: {exc}")
                    continue
        if ingest_artifact(
            root,
            repo_key=repo_key,
            repo=repo,
            run_id=run_id,
            run_attempt=run_attempt,
            artifact=artifact,
            archive_bytes=archive,
        ):
            created += 1
    return created


def reconcile_actions(root: Path, registry: dict, gh: GitHubClient) -> dict[str, int]:
    dispatched = root / "research" / "cross_repo" / "actions" / "dispatched"
    stats = {
        "completed": 0,
        "failed": 0,
        "retried": 0,
        "artifacts": 0,
        "health_changes": 0,
        "events": 0,
        "failure_records": 0,
    }
    if not dispatched.exists():
        return stats

    for path in sorted(dispatched.glob("*.yaml")):
        action = load_yaml(path)
        errors = validate_action(action, registry)
        if errors:
            raise ValueError(f"{path}: " + "; ".join(errors))

        repo, workflow_file, _ = workflow_spec(registry, action)
        policy = workflow_policy(registry, action)
        try:
            runs = gh.list_workflow_runs(repo, workflow_file, per_page=15)
        except RuntimeError as exc:
            print(f"cross-repo reconcile warning: {action['action_id']}: {exc}")
            continue

        run = None
        run_id = action.get("run_id")
        if run_id is not None:
            run = next((r for r in runs if r.get("id") == run_id), None)
        if run is None:
            run = match_dispatched_run(action, runs)
            if run is not None:
                action["run_id"] = run.get("id")
                action["run_url"] = run.get("html_url")
                write_yaml(path, action)

        health = assess_wait(
            action,
            run,
            runner_class=str(policy["runner_class"]),
            runner_wait_minutes=int(policy["runner_wait_minutes"]),
        )
        health_path = (
            root / "research" / "cross_repo" / "health" /
            str(action["repo_key"]) / f"{action['action_id']}.yaml"
        )
        if write_yaml_if_changed(health_path, health):
            stats["health_changes"] += 1

        retry_waiting = action.get("retry_waiting_for_attempt")
        current_attempt = int(run.get("run_attempt") or 1) if run is not None else 0
        if isinstance(retry_waiting, int) and current_attempt < retry_waiting:
            continue
        if isinstance(retry_waiting, int) and current_attempt >= retry_waiting:
            action.pop("retry_waiting_for_attempt", None)
            write_yaml(path, action)

        if run is None or run.get("status") != "completed":
            continue

        repo_key = str(action["repo_key"])
        workflow_key = str(action["workflow_key"])
        if append_event(
            root,
            repo_key,
            repo,
            workflow_key,
            workflow_file,
            run,
            "CIPI_DISPATCHED_ACTION",
            str(action["action_id"]),
        ):
            stats["events"] += 1

        stats["artifacts"] += ingest_run_artifacts(
            root,
            gh=gh,
            repo_key=repo_key,
            repo=repo,
            run=run,
            mode=str(policy["artifact_ingest"]),
        )

        try:
            jobs = gh.list_run_jobs(repo, int(run["id"]))
        except RuntimeError as exc:
            print(f"job detail warning: {action['action_id']}: {exc}")
            jobs = []
        classification = classify_failure(run, jobs)

        conclusion = str(run.get("conclusion") or "failure")
        if conclusion != "success":
            retry_count = int(action.get("retry_count", 0))
            max_retries = int(action.get("max_retries", policy["max_retries"]))
            retry_requested = (
                bool(policy["auto_retry_transient"])
                and bool(classification["retry_safe"])
                and retry_count < max_retries
            )
            if write_failure_record(
                root,
                repo_key=repo_key,
                action=action,
                run=run,
                classification=classification,
                retry_requested=retry_requested,
            ):
                stats["failure_records"] += 1

            if retry_requested:
                try:
                    gh.rerun_failed_jobs(repo, int(run["id"]))
                except RuntimeError as exc:
                    print(f"transient retry request failed: {action['action_id']}: {exc}")
                else:
                    action["retry_count"] = retry_count + 1
                    action["last_failure_classification"] = classification
                    action["last_retry_at"] = now_iso()
                    action["retry_waiting_for_attempt"] = int(run.get("run_attempt") or 1) + 1
                    write_yaml(path, action)
                    stats["retried"] += 1
                    continue

        action["state"] = "COMPLETED" if conclusion == "success" else "FAILED"
        action["conclusion"] = conclusion
        action["completed_at"] = run.get("updated_at") or now_iso()
        action["failure_classification"] = classification if conclusion != "success" else None
        dst = action_terminal_dir(root, conclusion) / path.name
        write_yaml(dst, action)
        path.unlink()
        if conclusion == "success":
            stats["completed"] += 1
        else:
            stats["failed"] += 1
    return stats


def observe_latest(root: Path, registry: dict, gh: GitHubClient) -> int:
    created = 0
    for repo_key, repo_spec in registry["repositories"].items():
        repo = str(repo_spec["repository"])
        for workflow_key, workflow in repo_spec["workflows"].items():
            if workflow.get("monitor") is not True:
                continue
            workflow_file = str(workflow["file"])
            try:
                runs = gh.list_workflow_runs(repo, workflow_file, per_page=5)
            except RuntimeError as exc:
                print(f"cross-repo monitor warning: {repo_key}/{workflow_key}: {exc}")
                continue
            completed_runs = [r for r in runs if r.get("status") == "completed"]
            if not completed_runs:
                continue
            latest = completed_runs[0]
            if append_event(
                root,
                str(repo_key),
                repo,
                str(workflow_key),
                workflow_file,
                latest,
                "MONITOR",
            ):
                created += 1
    return created


def resume_jobs(root: Path) -> int:
    queued = root / "research" / "jobs" / "queued"
    if not queued.exists():
        return 0
    completed_ids = completed_action_ids(root)
    count = 0
    for path in sorted([*queued.glob("*.yaml"), *queued.glob("*.yml")]):
        job = load_yaml(path)
        resume, refs = should_resume_external_job(job, completed_ids)
        if not resume:
            continue
        waits = job.pop("external_wait", [])
        history = job.get("external_wait_history")
        if not isinstance(history, list):
            history = []
        history.append({
            "resolved_at": now_iso(),
            "resolved_action_ids": refs,
            "waits": waits,
        })
        job["external_wait_history"] = history
        job["state"] = "QUEUED"
        write_yaml(path, job)
        count += 1
    return count


def dispatch_one(root: Path, registry: dict, gh: GitHubClient) -> str | None:
    selected = select_queued_action(root, registry)
    if selected is None:
        return None
    path, action = selected
    repo, workflow_file, ref = workflow_spec(registry, action)
    attempts = int(action.get("attempts", 0))
    max_attempts = int(action.get("max_attempts", 2))
    if attempts >= max_attempts:
        action["state"] = "QUARANTINED"
        action["quarantined_at"] = now_iso()
        dst = root / "research" / "cross_repo" / "actions" / "quarantined" / path.name
        write_yaml(dst, action)
        path.unlink()
        return None

    prior_runs = gh.list_workflow_runs(repo, workflow_file, per_page=5)
    prior_ids = [r.get("id") for r in prior_runs if isinstance(r.get("id"), int)]
    action["previous_run_id"] = max(prior_ids) if prior_ids else 0
    action.setdefault("retry_count", 0)
    gh.dispatch_workflow(repo, workflow_file, ref, action.get("inputs", {}))
    action["state"] = "DISPATCHED"
    action["attempts"] = attempts + 1
    action["dispatched_at"] = now_iso()
    action["repository"] = repo
    action["workflow_file"] = workflow_file
    action["ref"] = ref
    dst = root / "research" / "cross_repo" / "actions" / "dispatched" / path.name
    write_yaml(dst, action)
    path.unlink()
    return str(action["action_id"])


def write_outputs(path: str | None, values: dict[str, object]) -> None:
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as h:
        for key, value in values.items():
            text = "true" if value is True else "false" if value is False else str(value)
            h.write(f"{key}={text}\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--registry", default="automation/cross_repo/registry.yaml")
    p.add_argument("--github-output")
    args = p.parse_args()

    root = Path(args.root).resolve()
    registry = load_registry(root / args.registry)
    token = os.environ.get("CIPI_CROSS_REPO_TOKEN", "").strip()
    if not token:
        print("CIPI cross-repo orchestrator: DISABLED (CIPI_CROSS_REPO_TOKEN is not configured)")
        write_outputs(args.github_output, {"configured": False, "changed": False, "resumed_jobs": 0})
        return 0

    gh = GitHubClient(token)
    reconciliation = reconcile_actions(root, registry, gh)
    observed = observe_latest(root, registry, gh)
    resumed = resume_jobs(root)
    dispatched = dispatch_one(root, registry, gh)
    changed = any(reconciliation.values()) or observed > 0 or resumed > 0 or dispatched is not None

    print(
        "CIPI cross-repo orchestrator:",
        *(f"{key}={value}" for key, value in reconciliation.items()),
        f"observed={observed}",
        f"resumed={resumed}",
        f"dispatched={dispatched or '-'}",
    )
    write_outputs(
        args.github_output,
        {
            "configured": True,
            "changed": changed,
            "completed_actions": reconciliation["completed"],
            "failed_actions": reconciliation["failed"],
            "retried_actions": reconciliation["retried"],
            "artifact_records": reconciliation["artifacts"],
            "runner_health_changes": reconciliation["health_changes"],
            "observed_events": observed,
            "resumed_jobs": resumed,
            "dispatched_action": dispatched or "",
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
