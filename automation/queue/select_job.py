from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import yaml

def remote_branch_exists(prefix: str) -> bool:
    result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", f"refs/heads/{prefix}*"],
        text=True, capture_output=True, check=True,
    )
    return bool(result.stdout.strip())

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--queued", default="research/jobs/queued")
    p.add_argument("--github-output", required=True)
    args = p.parse_args()
    root = Path(args.queued)
    jobs = sorted([*root.glob("*.yaml"), *root.glob("*.yml")]) if root.exists() else []
    selected = None
    for path in jobs:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        job_id = str(data.get("job_id", ""))
        if not job_id:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        branch = f"research-bot/{job_id}/auto-{digest}"
        if remote_branch_exists(branch):
            continue
        selected = (path, job_id, digest, branch)
        break
    out = Path(args.github_output)
    with out.open("a", encoding="utf-8") as h:
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
