from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
from typing import Callable
import yaml


def remote_branch_exists(prefix: str) -> bool:
    result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", f"refs/heads/{prefix}*"],
        text=True,
        capture_output=True,
        check=True,
    )
    return bool(result.stdout.strip())


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def completed_job_ids(completed_root: Path) -> set[str]:
    if not completed_root.exists():
        return set()
    ids: set[str] = set()
    for path in sorted([*completed_root.glob("*.yaml"), *completed_root.glob("*.yml")]):
        data = _load_yaml(path)
        if data.get("state") == "COMPLETED" and data.get("job_id"):
            ids.add(str(data["job_id"]))
    return ids


def _decision_files(root: Path, target_id: str, gate: str) -> list[Path]:
    base = root / "research" / "human_gates" / "decisions"
    if not base.exists():
        return []
    files: list[Path] = []
    for project_dir in base.iterdir():
        if not project_dir.is_dir():
            continue
        folder = project_dir / target_id / gate
        if folder.exists():
            files.extend(sorted([*folder.glob("*.yaml"), *folder.glob("*.yml")]))
    return files


def _latest_gate_decision(root: Path | None, target_id: str, gate: str) -> dict | None:
    if root is None:
        return None
    candidates: list[tuple[str, str, dict]] = []
    for path in _decision_files(root, target_id, gate):
        data = _load_yaml(path)
        if data.get("target_type") != "RESEARCH_JOB":
            continue
        if str(data.get("target_id") or "") != target_id:
            continue
        if str(data.get("gate") or "") != gate:
            continue
        candidates.append((str(data.get("created_at") or ""), path.as_posix(), data))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][2]


def _required_human_gates(data: dict) -> list[str]:
    policy = data.get("review_policy")
    if not isinstance(policy, dict):
        return []
    values = policy.get("required_human_gates", [])
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if str(value)]


def _unresolved_human_gates(root: Path | None, data: dict) -> list[str]:
    job_id = str(data.get("job_id") or "")
    unresolved: list[str] = []
    for gate in _required_human_gates(data):
        decision = _latest_gate_decision(root, job_id, gate)
        if not (
            isinstance(decision, dict)
            and str(decision.get("outcome") or "").upper() == "COMPLETE"
            and str(decision.get("operational_effect") or "") == "RESOLVE_RESEARCH_JOB_GATE"
        ):
            unresolved.append(gate)
    return unresolved


def _infer_human_gate_root(queued_root: Path) -> Path | None:
    if (
        queued_root.name == "queued"
        and queued_root.parent.name == "jobs"
        and queued_root.parent.parent.name == "research"
    ):
        return queued_root.parent.parent.parent
    return None


def _priority(data: dict) -> int:
    value = data.get("priority", 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _dependencies(data: dict) -> list[str]:
    values = data.get("depends_on_jobs", [])
    if not isinstance(values, list):
        return []
    return [str(v) for v in values]


def choose_job(
    queued_root: Path,
    completed_root: Path,
    branch_exists: Callable[[str], bool] = remote_branch_exists,
    human_gate_root: Path | None = None,
) -> tuple[
    tuple[Path, str, str, str] | None,
    dict[str, int | bool | list[str]],
]:
    jobs = sorted([*queued_root.glob("*.yaml"), *queued_root.glob("*.yml")]) if queued_root.exists() else []
    parsed = [(path, _load_yaml(path)) for path in jobs]
    parsed.sort(key=lambda item: (-_priority(item[1]), item[0].as_posix()))

    completed = completed_job_ids(completed_root)
    stats: dict[str, int | bool | list[str]] = {
        "skipped_blocked": 0,
        "skipped_dependency": 0,
        "skipped_claimed": 0,
        "skipped_human_gate": 0,
        "blocked_jobs": [],
        "dependency_jobs": [],
        "human_gate_jobs": [],
        "claimed_jobs": [],
        "claimed_branches": [],
        "work_steal": False,
    }

    if human_gate_root is None:
        human_gate_root = _infer_human_gate_root(queued_root)

    skipped_before_selection = False
    for path, data in parsed:
        state = str(data.get("state", ""))
        job_id = str(data.get("job_id", ""))

        if state != "QUEUED":
            stats["skipped_blocked"] = int(stats["skipped_blocked"]) + 1
            blocked_jobs = stats["blocked_jobs"]
            assert isinstance(blocked_jobs, list)
            blocked_jobs.append(job_id or path.stem)
            skipped_before_selection = True
            continue

        if not job_id:
            skipped_before_selection = True
            continue

        unresolved = [dep for dep in _dependencies(data) if dep not in completed]
        if unresolved:
            stats["skipped_dependency"] = int(stats["skipped_dependency"]) + 1
            dependency_jobs = stats["dependency_jobs"]
            assert isinstance(dependency_jobs, list)
            dependency_jobs.append(f"{job_id}<-{','.join(unresolved)}")
            skipped_before_selection = True
            continue

        unresolved_gates = _unresolved_human_gates(human_gate_root, data)
        if unresolved_gates:
            stats["skipped_human_gate"] = int(stats["skipped_human_gate"]) + 1
            human_gate_jobs = stats["human_gate_jobs"]
            assert isinstance(human_gate_jobs, list)
            human_gate_jobs.append(f"{job_id}<-{','.join(unresolved_gates)}")
            skipped_before_selection = True
            continue

        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        branch = f"research-bot/{job_id}/auto-{digest}"
        if branch_exists(branch):
            stats["skipped_claimed"] = int(stats["skipped_claimed"]) + 1
            claimed_jobs = stats["claimed_jobs"]
            claimed_branches = stats["claimed_branches"]
            assert isinstance(claimed_jobs, list)
            assert isinstance(claimed_branches, list)
            claimed_jobs.append(job_id)
            claimed_branches.append(branch)
            skipped_before_selection = True
            continue

        stats["work_steal"] = skipped_before_selection
        return (path, job_id, digest, branch), stats

    stats["work_steal"] = skipped_before_selection
    return None, stats


def _csv(values: int | bool | list[str]) -> str:
    return ",".join(values) if isinstance(values, list) else ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--queued", default="research/jobs/queued")
    p.add_argument("--completed", default="research/jobs/completed")
    p.add_argument("--github-output", required=True)
    args = p.parse_args()

    selected, stats = choose_job(
        Path(args.queued),
        Path(args.completed),
    )

    out = Path(args.github_output)
    with out.open("a", encoding="utf-8") as h:
        h.write(f"skipped_blocked={stats['skipped_blocked']}\n")
        h.write(f"skipped_dependency={stats['skipped_dependency']}\n")
        h.write(f"skipped_claimed={stats['skipped_claimed']}\n")
        h.write(f"skipped_human_gate={stats['skipped_human_gate']}\n")
        h.write(f"blocked_jobs={_csv(stats['blocked_jobs'])}\n")
        h.write(f"dependency_jobs={_csv(stats['dependency_jobs'])}\n")
        h.write(f"human_gate_jobs={_csv(stats['human_gate_jobs'])}\n")
        h.write(f"claimed_jobs={_csv(stats['claimed_jobs'])}\n")
        h.write(f"claimed_branches={_csv(stats['claimed_branches'])}\n")
        claimed_jobs = stats["claimed_jobs"]
        claimed_branches = stats["claimed_branches"]
        assert isinstance(claimed_jobs, list)
        assert isinstance(claimed_branches, list)
        h.write(f"first_claimed_job={claimed_jobs[0] if claimed_jobs else ''}\n")
        h.write(f"first_claimed_branch={claimed_branches[0] if claimed_branches else ''}\n")
        h.write(f"work_steal={'true' if stats['work_steal'] else 'false'}\n")
        if selected is None:
            h.write("has_job=false\n")
        else:
            path, job_id, digest, bot_branch = selected
            h.write("has_job=true\n")
            h.write(f"job_path={path.as_posix()}\n")
            h.write(f"job_id={job_id}\n")
            h.write(f"job_hash={digest}\n")
            h.write(f"branch={bot_branch}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
