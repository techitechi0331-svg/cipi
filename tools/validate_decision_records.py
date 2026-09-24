from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "schema_version", "decision_id", "job_id", "source_run", "event_type",
    "authority", "decision", "review_status", "rationale", "retained_findings",
    "reusable_findings", "revisit_if", "lineage", "created_at", "immutable",
}
DECISIONS = {"PROMOTE", "ITERATE", "ARCHIVE", "REJECT"}
EVENTS = {"AUTOMATED_PROPOSAL", "REVIEW"}
AUTHORITIES = {"AUTOMATION", "HUMAN_REVIEW", "ASSISTANT_REVIEW"}
REVIEW_STATES = {"PENDING", "CONFIRMED", "SUPERSEDED"}

def validate(path: Path) -> list[str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: root must be a mapping"]
    errors = []
    missing = sorted(REQUIRED - set(data))
    if missing:
        return [f"{path}: missing required keys: {', '.join(missing)}"]
    if data.get("schema_version") != "1.0":
        errors.append(f"{path}: schema_version must be 1.0")
    if data.get("event_type") not in EVENTS:
        errors.append(f"{path}: invalid event_type")
    if data.get("authority") not in AUTHORITIES:
        errors.append(f"{path}: invalid authority")
    if data.get("decision") not in DECISIONS:
        errors.append(f"{path}: invalid decision")
    if data.get("review_status") not in REVIEW_STATES:
        errors.append(f"{path}: invalid review_status")
    if data.get("immutable") is not True:
        errors.append(f"{path}: decision records must be immutable")
    source_run = str(data.get("source_run", ""))
    if not source_run.startswith("research/runs/"):
        errors.append(f"{path}: source_run must point under research/runs/")
    elif not (ROOT / source_run).is_dir():
        errors.append(f"{path}: source_run directory does not exist: {source_run}")
    if data.get("event_type") == "AUTOMATED_PROPOSAL":
        if data.get("authority") != "AUTOMATION":
            errors.append(f"{path}: automated proposals must use AUTOMATION authority")
        if data.get("review_status") != "PENDING":
            errors.append(f"{path}: automated proposals must remain PENDING")
        if data.get("decision") == "PROMOTE":
            errors.append(f"{path}: automation may not propose PROMOTE")
    if data.get("event_type") == "REVIEW":
        if data.get("authority") == "AUTOMATION":
            errors.append(f"{path}: REVIEW may not use AUTOMATION authority")
        if data.get("review_status") == "PENDING":
            errors.append(f"{path}: REVIEW must resolve to CONFIRMED or SUPERSEDED")
        if not str(data.get("parent_decision_id", "")).strip():
            errors.append(f"{path}: REVIEW requires parent_decision_id")
    retained = data.get("retained_findings")
    if not isinstance(retained, list) or not retained:
        errors.append(f"{path}: retained_findings must be a non-empty list")
    reusable = data.get("reusable_findings")
    if not isinstance(reusable, list):
        errors.append(f"{path}: reusable_findings must be a list")
    revisit = data.get("revisit_if")
    if not isinstance(revisit, list):
        errors.append(f"{path}: revisit_if must be a list")
    lineage = data.get("lineage")
    if not isinstance(lineage, dict):
        errors.append(f"{path}: lineage must be a mapping")
    if data.get("decision") == "REJECT":
        declared = data.get("declared_rejection_criteria")
        if not isinstance(declared, list) or not declared:
            errors.append(f"{path}: REJECT requires declared_rejection_criteria")
        if not revisit:
            errors.append(f"{path}: REJECT requires at least one revisit_if condition")
    if len(str(data.get("rationale", "")).strip()) < 10:
        errors.append(f"{path}: rationale is too short")
    return errors

def main() -> int:
    root = ROOT / "research" / "decisions"
    files = []
    if root.exists():
        files = list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))
    errors = []
    for path in files:
        errors.extend(validate(path))
    if errors:
        print("CIPI decision record gate: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print(f"CIPI decision record gate: PASS ({len(files)} file(s))")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
