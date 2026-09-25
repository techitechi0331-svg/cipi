from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

ROUTES = {"REJECTION_REVIEW", "PROMOTION_REVIEW", "CONTINUE_RESEARCH", "HUMAN_GATE_REVIEW", "DONE"}
CANDIDATES = {"REJECT_CANDIDATE", "PROMOTION_CANDIDATE", "RESEARCH_MORE", "ALREADY_REVIEWED"}
REQUIRED = {
    "schema_version", "triage_id", "job_id", "run_id", "source_run",
    "source_decision_id", "candidate_class", "route", "final_decision_made",
    "acceptance_met", "rejection_triggered", "review_gaps",
    "required_human_gates", "downstream_gate_signals", "reasons",
    "recommended_action", "created_at", "triage_version", "immutable",
}

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def validate(root: Path, path: Path) -> list[str]:
    errors = []
    try:
        data = load_yaml(path)
    except Exception as exc:
        return [f"{path}: YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: root must be a mapping"]
    missing = sorted(REQUIRED - set(data))
    if missing:
        return [f"{path}: missing keys: {', '.join(missing)}"]
    if data.get("schema_version") != "1.0" or data.get("triage_version") != "1.0":
        errors.append(f"{path}: unsupported schema/triage version")
    if data.get("candidate_class") not in CANDIDATES:
        errors.append(f"{path}: invalid candidate_class")
    if data.get("route") not in ROUTES:
        errors.append(f"{path}: invalid route")
    if data.get("immutable") is not True:
        errors.append(f"{path}: triage artifacts must be immutable")
    source_run = str(data.get("source_run", ""))
    run_dir = root / source_run
    if not source_run.startswith("research/runs/") or not run_dir.is_dir():
        errors.append(f"{path}: invalid or missing source_run")
    else:
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.is_file():
            errors.append(f"{path}: source run has no manifest.json")
        else:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if str(manifest.get("job_id")) != str(data.get("job_id")):
                errors.append(f"{path}: job_id does not match source manifest")
            if str(manifest.get("run_id")) != str(data.get("run_id")):
                errors.append(f"{path}: run_id does not match source manifest")
            if bool(manifest.get("acceptance_met")) != bool(data.get("acceptance_met")):
                errors.append(f"{path}: acceptance_met does not match source manifest")
            if bool(manifest.get("rejection_triggered")) != bool(data.get("rejection_triggered")):
                errors.append(f"{path}: rejection_triggered does not match source manifest")
    decision_root = root / "research" / "decisions" / str(data.get("job_id", ""))
    decision = None
    if decision_root.exists():
        for dp in list(decision_root.glob("*.yaml")) + list(decision_root.glob("*.yml")):
            dd = load_yaml(dp)
            if isinstance(dd, dict) and str(dd.get("decision_id")) == str(data.get("source_decision_id")):
                decision = dd
                break
    if decision is None:
        errors.append(f"{path}: source_decision_id not found")
    else:
        if decision.get("event_type") != "AUTOMATED_PROPOSAL":
            errors.append(f"{path}: source decision must be AUTOMATED_PROPOSAL")
        if decision.get("authority") != "AUTOMATION" or decision.get("review_status") != "PENDING":
            errors.append(f"{path}: source automated decision must remain AUTOMATION/PENDING")
        if decision.get("immutable") is not True:
            errors.append(f"{path}: source automated decision must be immutable")
        expected_decision = "REJECT" if bool(data.get("rejection_triggered")) else "ITERATE"
        if decision.get("decision") != expected_decision:
            errors.append(f"{path}: source automated decision must be {expected_decision} for the manifest")
        if str(decision.get("created_at", "")) != str(manifest.get("completed_at", "")):
            errors.append(f"{path}: source decision created_at must match source manifest completed_at")
        if list(decision.get("triggered_criteria", [])) != list(manifest.get("triggered_criteria", [])):
            errors.append(f"{path}: source decision triggered_criteria must match source manifest")
        if data.get("candidate_class") == "REJECT_CANDIDATE" and decision.get("decision") != "REJECT":
            errors.append(f"{path}: REJECT_CANDIDATE requires REJECT proposal")
        if data.get("route") == "REJECTION_REVIEW" and decision.get("decision") != "REJECT":
            errors.append(f"{path}: REJECTION_REVIEW requires REJECT proposal")
    if data.get("route") == "DONE" and not bool(data.get("final_decision_made")):
        errors.append(f"{path}: DONE requires final_decision_made=true")
    for key in ("review_gaps", "required_human_gates", "downstream_gate_signals", "reasons"):
        if not isinstance(data.get(key), list):
            errors.append(f"{path}: {key} must be a list")
    if len(str(data.get("recommended_action", "")).strip()) < 10:
        errors.append(f"{path}: recommended_action is too short")
    return errors

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    args = p.parse_args()
    root = Path(args.root).resolve()
    review_root = root / "research" / "reviews"
    files = list(review_root.rglob("*-triage*.yaml")) + list(review_root.rglob("*-triage*.yml")) if review_root.exists() else []
    errors = []
    ids = {}
    parsed = []
    for path in files:
        errors.extend(validate(root, path))
        try:
            data = load_yaml(path)
        except Exception:
            data = {}
        if isinstance(data, dict):
            parsed.append((path, data))
        tid = data.get("triage_id") if isinstance(data, dict) else None
        if tid in ids:
            errors.append(f"{path}: duplicate triage_id {tid!r}")
        elif tid:
            ids[tid] = path
    for path, data in parsed:
        supersedes = data.get("supersedes_triage_id")
        if supersedes and supersedes not in ids:
            errors.append(f"{path}: supersedes_triage_id does not reference an existing triage record")
        revision = data.get("triage_revision")
        if revision is not None and (not isinstance(revision, int) or revision < 2):
            errors.append(f"{path}: triage_revision must be integer >=2 when present")
    if errors:
        print("CIPI review triage gate: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print(f"CIPI review triage gate: PASS ({len(files)} file(s))")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
