from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

VALIDATOR = Path(__file__).resolve().parent / "validate_research_change_scope.py"

def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)

def git(cwd: Path, *args: str) -> str:
    result = run("git", *args, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()

def commit(cwd: Path, message: str) -> str:
    git(cwd, "add", "-A")
    git(cwd, "commit", "-m", message)
    return git(cwd, "rev-parse", "HEAD")

def check(cwd: Path, base: str, head: str, should_pass: bool, label: str) -> None:
    result = run(sys.executable, str(VALIDATOR), "--base", base, "--head", head, cwd=cwd)
    passed = result.returncode == 0
    if passed != should_pass:
        raise AssertionError(f"{label}: expected pass={should_pass}, got {passed}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        git(root, "init")
        git(root, "config", "user.name", "CIPI Test")
        git(root, "config", "user.email", "cipi-test@example.invalid")

        (root / "research/runs/OLD/run-1").mkdir(parents=True)
        (root / "research/runs/OLD/run-1/metrics.json").write_text("{}\n", encoding="utf-8")
        (root / "research/jobs/queued").mkdir(parents=True)
        (root / "research/jobs/queued/JOB.yaml").write_text("job_id: JOB\nstate: QUEUED\n", encoding="utf-8")
        base = commit(root, "base")

        (root / "research/runs/NEW/run-1").mkdir(parents=True)
        (root / "research/runs/NEW/run-1/metrics.json").write_text("{}\n", encoding="utf-8")
        (root / "research/jobs/completed").mkdir(parents=True)
        (root / "research/jobs/completed/JOB.yaml").write_text("job_id: JOB\nstate: COMPLETED\n", encoding="utf-8")
        (root / "research/jobs/queued/JOB.yaml").unlink()
        (root / "research/cross_repo/actions/queued").mkdir(parents=True)
        (root / "research/cross_repo/actions/queued/ACTION.yaml").write_text("action_id: ACTION-001\nstate: QUEUED\n", encoding="utf-8")
        allowed = commit(root, "allowed append, finalize and cross-repo continuation")
        check(root, base, allowed, True, "append-only addition and queue finalization")

        # Worker branches may add pending proposals but never assert a reviewed
        # promotion, regardless of the claimed actor inside YAML.
        for event_type, authority, review_status, decision, expected in (
            ("AUTOMATED_PROPOSAL", "AUTOMATION", "PENDING", "ITERATE", True),
            ("REVIEW", "HUMAN_REVIEW", "CONFIRMED", "PROMOTE", False),
            ("AUTOMATED_PROPOSAL", "ASSISTANT_REVIEW", "PENDING", "ITERATE", False),
            ("AUTOMATED_PROPOSAL", "AUTOMATION", "PENDING", "PROMOTE", False),
        ):
            git(root, "reset", "--hard", base)
            record = root / "research/decisions/FAKE-001/decision.yaml"
            record.parent.mkdir(parents=True, exist_ok=True)
            record.write_text(
                f"event_type: {event_type}\\nauthority: {authority}\\n"
                f"review_status: {review_status}\\ndecision: {decision}\\n".replace("\\\\n", "\\n"),
                encoding="utf-8",
            )
            proposal = commit(root, f"decision fixture {event_type} {authority} {decision}")
            check(root, base, proposal, expected, f"worker decision {event_type}/{authority}/{decision}")

        git(root, "reset", "--hard", base)
        (root / "research/runs/OLD/run-1/metrics.json").write_text("{\"changed\": true}\n", encoding="utf-8")
        modified = commit(root, "modify old evidence")
        check(root, base, modified, False, "modify prior run")

        git(root, "reset", "--hard", base)
        (root / "research/runs/OLD/run-1/metrics.json").unlink()
        deleted = commit(root, "delete old evidence")
        check(root, base, deleted, False, "delete prior run")

    print("[PASS] append-only research integrity guards")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
