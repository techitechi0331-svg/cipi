from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import subprocess
import sys

from experiments import run_adapter
from job_loader import load_job
from result_writer import write_checksums, write_json

WORKER_VERSION = "cipi-research-worker/0.2"

def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception as exc:
        raise RuntimeError("worker requires a checked-out Git commit") from exc

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def run_mock(job: dict) -> dict:
    mock = job.get("mock_measurements")
    if not isinstance(mock, dict):
        raise ValueError("mock_measurements must be a mapping")

    names = list(job["baseline"]) + list(job["variants"])
    missing = [name for name in names if name not in mock]
    if missing:
        raise ValueError("missing mock measurement(s): " + ", ".join(missing))

    metrics = {name: mock[name] for name in names}
    baseline = job["baseline"][0]
    candidate = job["variants"][0]
    objective = job["metrics"][0]
    b = float(metrics[baseline][objective])
    c = float(metrics[candidate][objective])

    return {
        "metrics": metrics,
        "raw_files": {},
        "commands": ["mock_measurement"],
        "acceptance_met": c > b,
        "rejection_triggered": c <= b,
        "triggered_criteria": [job["rejection"][0]] if c <= b and job.get("rejection") else [],
        "summary": (
            f"Mock orchestration only. {baseline}={b}; {candidate}={c}. "
            "This is not scientific evidence."
        ),
        "mode": "mock_orchestration_only",
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("job")
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-id", default="run-0001")
    args = parser.parse_args()

    job = load_job(args.job)
    started = utc_now()
    out = Path(args.output)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty research run directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]

    if isinstance(job.get("mock_measurements"), dict):
        result = run_mock(job)
    elif isinstance(job.get("experiment_adapter"), str):
        result = run_adapter(
            job["experiment_adapter"],
            repo_root,
            max(1, int(job.get("timeout_minutes", 1))) * 60,
        )
        result["mode"] = "allowlisted_adapter"
    else:
        raise SystemExit(
            "job requires mock_measurements or an allowlisted experiment_adapter"
        )

    environment = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "mode": result["mode"],
    }
    if job.get("experiment_adapter"):
        environment["experiment_adapter"] = job["experiment_adapter"]

    parameters = {
        "job_file": str(args.job),
        "baseline": job["baseline"],
        "variants": job["variants"],
        "metrics": job["metrics"],
        "experiment_adapter": job.get("experiment_adapter"),
    }

    write_json(out / "metrics.json", result["metrics"])
    write_json(out / "environment.json", environment)
    write_json(out / "parameters.json", parameters)

    raw_names = []
    for name, content in result.get("raw_files", {}).items():
        target = out / name
        target.write_text(content, encoding="utf-8")
        raw_names.append(name)

    summary = f"""# Autonomous Research Run

- Job: {job['job_id']}
- Mode: {result['mode']}
- Acceptance met: {str(result['acceptance_met']).lower()}
- Rejection triggered: {str(result['rejection_triggered']).lower()}

## Scope

{result['summary']}
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
        "commands": result["commands"],
        "result": "COMPLETED",
        "acceptance_met": bool(result["acceptance_met"]),
        "rejection_triggered": bool(result["rejection_triggered"]),
        "triggered_criteria": list(result.get("triggered_criteria", [])),
        "checksums_file": "checksums.sha256",
    }
    write_json(out / "manifest.json", manifest)

    checksum_names = [
        "metrics.json",
        "environment.json",
        "parameters.json",
        "summary.md",
        "manifest.json",
        *raw_names,
    ]
    write_checksums(out, checksum_names)
    print(f"wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
