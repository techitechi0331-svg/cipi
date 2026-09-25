from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
TRIAGE = ROOT / "automation" / "review" / "triage.py"

spec = importlib.util.spec_from_file_location("cipi_triage", TRIAGE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source_run = "research/runs/LEGACY-JOB/run-1"
        base = root / "research" / "decisions" / "LEGACY-JOB"

        write_yaml(base / "run-1-auto-backfill.yaml", {
            "decision_id": "LEGACY-JOB:run-1:auto-backfill",
            "job_id": "LEGACY-JOB",
            "source_run": source_run,
            "event_type": "AUTOMATED_PROPOSAL",
            "authority": "AUTOMATION",
            "decision": "ITERATE",
            "review_status": "PENDING",
            "immutable": True,
        })
        write_yaml(base / "later-main-review.yaml", {
            "decision_id": "LEGACY-JOB:review-main",
            "job_id": "LEGACY-JOB",
            "source_run": source_run,
            "event_type": "REVIEW",
            "authority": "ASSISTANT_REVIEW",
            "decision": "ITERATE",
            "review_status": "CONFIRMED",
            "parent_decision_id": "LEGACY-JOB:run-1:auto-original",
            "immutable": True,
            "created_at": "2026-09-25",
        })

        found = mod.find_confirmed_review(
            root,
            "LEGACY-JOB",
            "LEGACY-JOB:run-1:auto-backfill",
            source_run,
        )
        assert found is not None, "same-source-run confirmed review was not found"
        assert found[3]["decision_id"] == "LEGACY-JOB:review-main"

        wrong = mod.find_confirmed_review(
            root,
            "LEGACY-JOB",
            "missing-parent",
            "research/runs/LEGACY-JOB/other-run",
        )
        assert wrong is None, "review from a different source run was incorrectly matched"

    print("[PASS] legacy review source-run lineage matching")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
