from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from job_loader import load_job
from result_writer import write_checksums, write_json

WORKER_VERSION = "cipi-mock-worker/0.1"

def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception as exc:
        raise RuntimeError("worker requires a checked-out Git commit") from exc

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("job")
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id", default="mock-0001")
    args = parser.parse_args()

    job = load_job(args.job)
    mock = job.get("mock_measurements")
    if not isinstance(mock, dict):
        raise SystemExit("v0.1 mock worker only executes jobs with mock_measurements")

    started = utc_now()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    names = list(job["baseline"]) + list(job["variants"])
    missing = [name for name in names if name not in mock]
    if missing:
        raise SystemExit("missing mock measurement(s): " + ", ".join(missing))

    metrics = {name: mock[name] for name in names}
    baseline = job["baseline"][0]
    candidate = job["variants"][0]
    objective = job["metrics"][0]
    b = float(metrics[baseline][objective])
    c = float(metrics[candidate][objective])
    acceptance_met = c > b
    rejection_triggered = not acceptance_met

    environment = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "mode": "mock_orchestration_only",
    }
    parameters = {
        "job_file": str(args.job),
        "baseline": job["baseline"],
        "variants": job["variants"],
        "metrics": job["metrics"],
    }

    write_json(out / "metrics.json", metrics)
    write_json(out / "environment.json", environment)
    write_json(out / "parameters.json", parameters)

    summary = f"""# Autonomous Research Smoke Run

This run validates orchestration only and is not scientific evidence.

- Job: {job['job_id']}
- Baseline: {baseline} = {b}
- Candidate: {candidate} = {c}
- Acceptance met: {str(acceptance_met).lower()}
- Rejection triggered: {str(rejection_triggered).lower()}
"""
    (out / "summary.md").write_text(summary, encoding="utf-8")

    completed = utc_now()
    manifest = {
        "schema_version": "1.0",
        "job_id": job["job_id"],
        "run_id": args.run_id,
        "source_commit": git_sha(),
        "worker_version": WORKER_VERSION,
        "started_at": started,
        "completed_at": completed,
        "random_seed": int(job.get("random_seed", 0)),
        "environment": environment,
        "commands": ["mock_measurement"],
        "result": "COMPLETED",
        "acceptance_met": acceptance_met,
        "rejection_triggered": rejection_triggered,
        "checksums_file": "checksums.sha256",
    }
    write_json(out / "manifest.json", manifest)
    write_checksums(out, ["metrics.json","environment.json","parameters.json","summary.md","manifest.json"])
    print(f"wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
