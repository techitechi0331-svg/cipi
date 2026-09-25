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
        "blocked_jobs": [],
        "dependency_jobs": [],
        "claimed_jobs": [],
        "claimed_branches": [],
        "work_steal": False,
    }

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
        h.write(f"blocked_jobs={_csv(stats['blocked_jobs'])}\n")
        h.write(f"dependency_jobs={_csv(stats['dependency_jobs'])}\n")
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
