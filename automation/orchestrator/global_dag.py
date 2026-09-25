from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "automation" / "queue"))
sys.path.insert(0, str(ROOT / "automation" / "cross_repo"))

from select_job import choose_job  # noqa: E402
from core import load_registry, load_yaml, select_queued_action  # noqa: E402


def yaml_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted([*path.glob("*.yaml"), *path.glob("*.yml")])


def count_states(root: Path) -> dict[str, int]:
    base = root / "research" / "cross_repo" / "actions"
    return {
        name: len(yaml_files(base / name))
        for name in ("queued", "dispatched", "completed", "failed", "quarantined")
    }


def health_alerts(root: Path) -> list[dict[str, Any]]:
    base = root / "research" / "cross_repo" / "health"
    alerts: list[dict[str, Any]] = []
    if not base.exists():
        return alerts
    for path in sorted(base.rglob("*.yaml")):
        data = load_yaml(path)
        if data.get("state") in {"RUNNER_WAIT", "DISPATCH_UNOBSERVED"}:
            alerts.append({
                "action_id": data.get("action_id"),
                "repo_key": data.get("repo_key"),
                "workflow_key": data.get("workflow_key"),
                "state": data.get("state"),
                "since": data.get("since"),
                "wait_threshold_minutes": data.get("wait_threshold_minutes"),
            })
    return alerts


def human_gates(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in yaml_files(root / "research" / "jobs" / "queued"):
        data = load_yaml(path)
        policy = data.get("review_policy")
        if not isinstance(policy, dict):
            continue
        gates = policy.get("required_human_gates", [])
        if isinstance(gates, list) and gates:
            results.append({"job_id": data.get("job_id"), "gates": gates})
    return results


def build_snapshot(root: Path, registry: dict[str, Any], cross_repo_enabled: bool) -> dict[str, Any]:
    selected_job, stats = choose_job(
        root / "research" / "jobs" / "queued",
        root / "research" / "jobs" / "completed",
    )
    local_candidate = None
    if selected_job is not None:
        path, job_id, _, branch = selected_job
        data = load_yaml(path)
        local_candidate = {
            "kind": "LOCAL_RESEARCH",
            "priority": int(data.get("priority", 0)),
            "job_id": job_id,
            "branch": branch,
        }

    claimed_jobs = stats.get("claimed_jobs", [])
    claimed_branches = stats.get("claimed_branches", [])
    intake_candidate = None
    if isinstance(claimed_jobs, list) and isinstance(claimed_branches, list) and claimed_jobs and claimed_branches:
        intake_candidate = {
            "kind": "EVIDENCE_INTAKE",
            "priority": 90,
            "job_id": claimed_jobs[0],
            "branch": claimed_branches[0],
        }

    external_candidate = None
    queued_action = select_queued_action(root, registry) if cross_repo_enabled else None
    if queued_action is not None:
        _, action = queued_action
        external_candidate = {
            "kind": "CROSS_REPO",
            "priority": int(action.get("priority", 0)),
            "action_id": action.get("action_id"),
            "reason": "ready_external_action",
        }

    states = count_states(root)
    if cross_repo_enabled and states["dispatched"] > 0:
        monitor = {
            "kind": "CROSS_REPO",
            "priority": 80,
            "action_id": None,
            "reason": "reconcile_dispatched_action",
        }
        if external_candidate is None or monitor["priority"] > external_candidate["priority"]:
            external_candidate = monitor

    candidates = [c for c in (local_candidate, intake_candidate, external_candidate) if c is not None]
    candidates.sort(key=lambda c: (-int(c["priority"]), str(c["kind"])))
    selected = candidates[0] if candidates else {"kind": "IDLE", "priority": -999}

    return {
        "schema_version": "1.0",
        "selected": selected,
        "local": {
            "ready_job": local_candidate,
            "claimed_jobs": claimed_jobs,
            "claimed_branches": claimed_branches,
            "blocked_count": stats.get("skipped_blocked", 0),
            "dependency_blocked_count": stats.get("skipped_dependency", 0),
            "claimed_count": stats.get("skipped_claimed", 0),
        },
        "cross_repo": {
            "enabled": cross_repo_enabled,
            "states": states,
            "ready_action": external_candidate if external_candidate and external_candidate.get("reason") == "ready_external_action" else None,
            "health_alerts": health_alerts(root),
        },
        "human_gates": human_gates(root),
        "authority": "OPERATIONAL_SCHEDULING_ONLY",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
    }


def write_dashboard(root: Path, snapshot: dict[str, Any]) -> bool:
    out_dir = root / "research" / "health"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "automation-status.json"
    md_path = out_dir / "automation-status.md"

    json_text = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    selected = snapshot["selected"]
    local = snapshot["local"]
    cross = snapshot["cross_repo"]
    states = cross["states"]
    alerts = cross["health_alerts"]
    gates = snapshot["human_gates"]

    lines = [
        "# CIPI Automation Health",
        "",
        "> Operational status only. This is not a sound-quality score or release decision.",
        "",
        f"- Next scheduler action: **{selected['kind']}**",
        f"- Local READY job: **{(local.get('ready_job') or {}).get('job_id', '-')}**",
        f"- Claimed evidence branches: **{local['claimed_count']}**",
        f"- Local blocked / dependency-blocked: **{local['blocked_count']} / {local['dependency_blocked_count']}**",
        f"- Cross-Repo enabled: **{'YES' if cross['enabled'] else 'NO'}**",
        f"- Cross-Repo queued / dispatched / failed / quarantined: **{states['queued']} / {states['dispatched']} / {states['failed']} / {states['quarantined']}**",
        f"- Runner/dispatch alerts: **{len(alerts)}**",
        f"- Declared human-gate jobs: **{len(gates)}**",
        "",
    ]
    if alerts:
        lines += ["## Runner / dispatch alerts", ""]
        for alert in alerts:
            lines.append(
                f"- `{alert.get('action_id')}` — {alert.get('state')} "
                f"({alert.get('repo_key')}/{alert.get('workflow_key')}, since {alert.get('since')})"
            )
        lines.append("")
    if gates:
        lines += ["## Human gates", ""]
        for item in gates:
            lines.append(f"- `{item.get('job_id')}` — " + "; ".join(map(str, item.get("gates", []))))
        lines.append("")
    md_text = "\n".join(lines)

    changed = False
    if not json_path.exists() or json_path.read_text(encoding="utf-8") != json_text:
        json_path.write_text(json_text, encoding="utf-8")
        changed = True
    if not md_path.exists() or md_path.read_text(encoding="utf-8") != md_text:
        md_path.write_text(md_text, encoding="utf-8")
        changed = True
    return changed


def write_outputs(path: str | None, snapshot: dict[str, Any], changed: bool) -> None:
    if not path:
        return
    selected = snapshot["selected"]
    values = {
        "next_kind": selected.get("kind", "IDLE"),
        "next_priority": selected.get("priority", -999),
        "job_id": selected.get("job_id", ""),
        "branch": selected.get("branch", ""),
        "action_id": selected.get("action_id", ""),
        "dashboard_changed": "true" if changed else "false",
    }
    with Path(path).open("a", encoding="utf-8") as h:
        for key, value in values.items():
            h.write(f"{key}={value}\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--registry", default="automation/cross_repo/registry.yaml")
    p.add_argument("--cross-repo-enabled", choices=["true", "false"], default="false")
    p.add_argument("--github-output")
    args = p.parse_args()

    root = Path(args.root).resolve()
    registry = load_registry(root / args.registry)
    snapshot = build_snapshot(root, registry, args.cross_repo_enabled == "true")
    changed = write_dashboard(root, snapshot)
    write_outputs(args.github_output, snapshot, changed)
    print(
        "CIPI Global DAG:",
        f"next={snapshot['selected'].get('kind')}",
        f"priority={snapshot['selected'].get('priority')}",
        f"dashboard_changed={changed}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
