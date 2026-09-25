from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {"nonlinear_continuity_pilot_v1"}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()

def harmonic_amplitudes(samples: list[float], cycles: int = 100) -> list[float]:
    n = len(samples)
    result = []
    for harmonic in range(1, 6):
        k = cycles * harmonic
        re = 0.0
        im = 0.0
        for i, value in enumerate(samples):
            angle = 2.0 * math.pi * k * i / n
            re += value * math.cos(angle)
            im -= value * math.sin(angle)
        result.append(2.0 * math.hypot(re, im) / n)
    return result

def thd_db(model, level_db: float) -> float:
    fs = 48000.0
    freq = 1000.0
    n = 4800
    amp = 10.0 ** (level_db / 20.0)
    samples = [model(amp * math.sin(2.0 * math.pi * freq * i / fs)) for i in range(n)]
    h = harmonic_amplitudes(samples, cycles=100)
    thd = math.sqrt(sum(v * v for v in h[1:])) / max(h[0], 1e-30)
    return 20.0 * math.log10(max(thd, 1e-30))

def run_continuity() -> dict:
    smooth = lambda x: math.tanh(2.0 * x)
    discontinuous = lambda x: math.tanh(2.0 * x) if x >= 0.0 else 0.90 * math.tanh(2.0 * x)
    levels = [-60.0, -40.0, -20.0]
    smooth_thd = {str(int(v)): thd_db(smooth, v) for v in levels}
    disc_thd = {str(int(v)): thd_db(discontinuous, v) for v in levels}
    eps = 1e-7
    right = (discontinuous(eps) - discontinuous(0.0)) / eps
    left = (discontinuous(0.0) - discontinuous(-eps)) / eps
    mismatch = abs(right - left)
    penalty = disc_thd["-60"] - smooth_thd["-60"]
    accepted = penalty >= 20.0 and mismatch >= 0.10
    return {
        "metrics": {
            "smooth_thd_db": smooth_thd,
            "slope_discontinuous_thd_db": disc_thd,
            "low_level_thd_penalty_db": penalty,
            "zero_crossing_derivative_left": left,
            "zero_crossing_derivative_right": right,
            "zero_crossing_derivative_mismatch": mismatch,
            "all_numeric_finite": all(math.isfinite(v) for v in [
                *smooth_thd.values(), *disc_thd.values(), penalty, left, right, mismatch
            ]),
        },
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Synthetic screening pilot only. It tests whether an intentionally slope-discontinuous "
            "memoryless transfer creates a persistent low-level harmonic floor relative to a smooth "
            "tanh baseline. It does not identify any hardware or approve a product model."
        ),
    }

def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def write_checksums(root: Path, names: list[str]) -> None:
    lines = []
    for name in names:
        digest = hashlib.sha256((root / name).read_bytes()).hexdigest()
        lines.append(f"{digest}  {name}")
    (root / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--proposal", required=True)
    p.add_argument("--output-root", default=str(REPO_ROOT))
    p.add_argument("--run-id", default="architect-pilot-0001")
    p.add_argument("--github-output")
    args = p.parse_args()

    proposal = yaml.safe_load(Path(args.proposal).read_text(encoding="utf-8"))
    adapter = proposal.get("pilot_adapter")
    if adapter not in ALLOWED:
        raise SystemExit(f"pilot adapter is not allowlisted: {adapter}")

    if adapter == "nonlinear_continuity_pilot_v1":
        result = run_continuity()
    else:
        raise SystemExit("unreachable adapter")

    root = Path(args.output_root)
    job_id = str(proposal["pilot_job_id"])
    run_rel = Path("research/runs") / job_id / args.run_id
    run_dir = root / run_rel
    if run_dir.exists() and any(run_dir.iterdir()):
        raise SystemExit(f"refusing to overwrite pilot run: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)

    started = utc_now()
    write_json(run_dir / "metrics.json", result["metrics"])
    (run_dir / "summary.md").write_text(
        "# Autonomous Research Architect Pilot\n\n"
        f"- Proposal: {proposal['proposal_id']}\n"
        f"- Adapter: {adapter}\n"
        f"- Acceptance met: {str(result['acceptance_met']).lower()}\n\n"
        f"## Scope\n\n{result['summary']}\n",
        encoding="utf-8",
    )
    completed = utc_now()
    manifest = {
        "schema_version": "1.0",
        "job_id": job_id,
        "run_id": args.run_id,
        "source_commit": git_sha(),
        "worker_version": "cipi-research-architect/0.1",
        "started_at": started,
        "completed_at": completed,
        "random_seed": 0,
        "environment": {"mode": "allowlisted_architect_pilot", "pilot_adapter": adapter},
        "commands": [f"allowlisted pilot: {adapter}"],
        "result": "COMPLETED",
        "acceptance_met": bool(result["acceptance_met"]),
        "rejection_triggered": bool(result["rejection_triggered"]),
        "triggered_criteria": [] if result["acceptance_met"] else list(proposal.get("rejection") or []),
        "checksums_file": "checksums.sha256",
    }
    write_json(run_dir / "manifest.json", manifest)
    write_checksums(run_dir, ["metrics.json", "summary.md", "manifest.json"])

    kc_rel = Path("research/knowledge_candidates") / job_id / f"{args.run_id}.yaml"
    kc_path = root / kc_rel
    kc_path.parent.mkdir(parents=True, exist_ok=True)
    kc = {
        "claim": (
            "In the controlled synthetic pilot, the intentionally slope-discontinuous transfer "
            "retained a materially larger low-level harmonic floor than the smooth tanh baseline."
        ),
        "evidence_type": "MEASURED",
        "scope": (
            "Synthetic screening models only; this supports a reusable diagnostic test and does "
            "not establish hardware identity or the behavior of any production plug-in."
        ),
        "source_run": str(run_rel),
        "promotion_requested": "LIKELY" if result["acceptance_met"] else "HYPOTHESIS",
    }
    kc_path.write_text(yaml.safe_dump(kc, sort_keys=False), encoding="utf-8")

    decision_rel = Path("research/decisions") / job_id / f"{args.run_id}-auto.yaml"
    decision_path = root / decision_rel
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision = {
        "schema_version": "1.0",
        "decision_id": f"{job_id}:{args.run_id}:auto",
        "job_id": job_id,
        "source_run": str(run_rel),
        "event_type": "AUTOMATED_PROPOSAL",
        "authority": "AUTOMATION",
        "decision": "ITERATE" if result["acceptance_met"] else "REJECT",
        "review_status": "PENDING",
        "rationale": (
            "The bounded pilot passed its declared synthetic screening criteria; retain the "
            "diagnostic method for independent cross-product replication."
            if result["acceptance_met"] else
            "The bounded pilot failed its declared screening criteria; preserve the negative evidence."
        ),
        "declared_rejection_criteria": list(proposal.get("rejection") or []),
        "triggered_criteria": [] if result["acceptance_met"] else list(proposal.get("rejection") or []),
        "retained_findings": [
            f"Low-level THD penalty at -60 dBFS: {result['metrics']['low_level_thd_penalty_db']:.3f} dB.",
            f"Zero-crossing derivative mismatch: {result['metrics']['zero_crossing_derivative_mismatch']:.6f}.",
        ],
        "reusable_findings": [
            "A low-level THD sweep plus left/right zero-crossing derivative check is a bounded screening method for suspicious static nonlinear transfers."
        ] if result["acceptance_met"] else [],
        "revisit_if": [
            "A second independent nonlinear product fails to reproduce the screening relationship.",
            "A numerically smoother implementation shows the same low-level floor under matched measurement conditions.",
        ],
        "lineage": {"supersedes": [], "related_jobs": [], "related_decisions": []},
        "created_at": completed,
        "immutable": True,
        "scope": "Research-method pilot only; no product adoption or CONFIRMED promotion.",
        "review_gaps": ["Independent second-product replication is still required."],
    }
    decision_path.write_text(yaml.safe_dump(decision, sort_keys=False), encoding="utf-8")

    print(f"architect pilot wrote {run_rel}")
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"pilot_job_id={job_id}\n")
            handle.write(f"pilot_run_id={args.run_id}\n")
            handle.write(f"pilot_acceptance_met={str(result['acceptance_met']).lower()}\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
