from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from core import (
    action_terminal_dir,
    event_path,
    load_registry,
    load_yaml,
    match_dispatched_run,
    select_queued_action,
    should_resume_external_job,
    validate_action,
    workflow_spec,
    write_yaml,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class GitHubClient:
    def __init__(self, token: str):
        if not token:
            raise ValueError("CIPI_CROSS_REPO_TOKEN is required")
        self.token = token

    def request(self, method: str, url: str, payload: dict | None = None) -> dict | list | None:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "cipi-cross-repo-orchestrator/1.0",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                if not raw:
                    return None
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {url} failed: {exc.code} {detail}") from exc

    def list_workflow_runs(self, repo: str, workflow_file: str, per_page: int = 10) -> list[dict]:
        quoted = urllib.parse.quote(workflow_file, safe="")
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{quoted}/runs?per_page={per_page}"
        data = self.request("GET", url)
        if not isinstance(data, dict):
            return []
        runs = data.get("workflow_runs", [])
        return runs if isinstance(runs, list) else []

    def dispatch_workflow(self, repo: str, workflow_file: str, ref: str, inputs: dict) -> None:
        quoted = urllib.parse.quote(workflow_file, safe="")
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{quoted}/dispatches"
        payload: dict = {"ref": ref}
        if inputs:
            payload["inputs"] = {str(k): str(v).lower() if isinstance(v, bool) else str(v) for k, v in inputs.items()}
        self.request("POST", url, payload)


def append_event(root: Path, repo_key: str, repo: str, workflow_key: str, workflow_file: str, run: dict, source: str, action_id: str | None = None) -> bool:
    run_id = run.get("id")
    if run_id is None:
        return False
    path = event_path(root, repo_key, run_id)
    if path.exists():
        return False
    event = {
        "schema_version": "1.0",
        "event_id": f"GHARUN-{run_id}",
        "source": source,
        "repository": repo,
        "repo_key": repo_key,
        "workflow_key": workflow_key,
        "workflow_file": workflow_file,
        "run_id": run_id,
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
        "observed_at": now_iso(),
        "authority": "EXTERNAL_WORKFLOW_EVIDENCE_ONLY",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
    }
    write_yaml(path, event)
    return True


def reconcile_actions(root: Path, registry: dict, gh: GitHubClient) -> tuple[int, int]:
    dispatched = root / "research" / "cross_repo" / "actions" / "dispatched"
    if not dispatched.exists():
        return 0, 0
    completed = 0
    failed = 0
    for path in sorted(dispatched.glob("*.yaml")):
        action = load_yaml(path)
        errors = validate_action(action, registry)
        if errors:
            raise ValueError(f"{path}: " + "; ".join(errors))
        repo, workflow_file, _ = workflow_spec(registry, action)
        runs = gh.list_workflow_runs(repo, workflow_file, per_page=15)
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
        if run is None or run.get("status") != "completed":
            continue

        conclusion = str(run.get("conclusion") or "failure")
        action["state"] = "COMPLETED" if conclusion == "success" else "FAILED"
        action["conclusion"] = conclusion
        action["completed_at"] = run.get("updated_at") or now_iso()
        repo_key = str(action["repo_key"])
        workflow_key = str(action["workflow_key"])
        append_event(root, repo_key, repo, workflow_key, workflow_file, run, "CIPI_DISPATCHED_ACTION", str(action["action_id"]))

        dst = action_terminal_dir(root, conclusion) / path.name
        write_yaml(dst, action)
        path.unlink()
        if conclusion == "success":
            completed += 1
        else:
            failed += 1
    return completed, failed


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
            if append_event(root, str(repo_key), repo, str(workflow_key), workflow_file, latest, "MONITOR"):
                created += 1
    return created


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
            if isinstance(value, bool):
                text = "true" if value else "false"
            else:
                text = str(value)
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
    completed, failed = reconcile_actions(root, registry, gh)
    observed = observe_latest(root, registry, gh)
    resumed = resume_jobs(root)
    dispatched = dispatch_one(root, registry, gh)
    changed = any((completed, failed, observed, resumed, dispatched is not None))

    print(
        "CIPI cross-repo orchestrator:",
        f"completed={completed}",
        f"failed={failed}",
        f"observed={observed}",
        f"resumed={resumed}",
        f"dispatched={dispatched or '-'}",
    )
    write_outputs(
        args.github_output,
        {
            "configured": True,
            "changed": changed,
            "completed_actions": completed,
            "failed_actions": failed,
            "observed_events": observed,
            "resumed_jobs": resumed,
            "dispatched_action": dispatched or "",
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
