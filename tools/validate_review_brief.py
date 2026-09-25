from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

REQUIRED = {
    "schema_version", "brief_version", "brief_id", "job_id", "run_id",
    "source_run", "route", "candidate_class", "triage_path", "research_question",
    "hypothesis", "counter_hypotheses", "acceptance_criteria", "rejection_criteria",
    "manifest_summary", "metric_snapshot", "source_proposal", "required_human_gates",
    "downstream_gate_signals", "allowed_review_actions", "required_precision_checks",
    "automatic_final_decision", "immutable",
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
    if data.get("schema_version") != "1.0" or data.get("brief_version") != "1.0":
        errors.append(f"{path}: unsupported version")
    if data.get("automatic_final_decision") is not False:
        errors.append(f"{path}: automatic_final_decision must be false")
    if data.get("immutable") is not True:
        errors.append(f"{path}: review brief must be immutable")
    source_run = str(data.get("source_run", ""))
    manifest_path = root / source_run / "manifest.json"
    if not source_run.startswith("research/runs/") or not manifest_path.is_file():
        errors.append(f"{path}: source run manifest missing")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if str(manifest.get("job_id")) != str(data.get("job_id")):
            errors.append(f"{path}: job_id mismatch")
        if str(manifest.get("run_id")) != str(data.get("run_id")):
            errors.append(f"{path}: run_id mismatch")
        summary = data.get("manifest_summary", {})
        if bool(summary.get("acceptance_met")) != bool(manifest.get("acceptance_met")):
            errors.append(f"{path}: acceptance_met mismatch")
        if bool(summary.get("rejection_triggered")) != bool(manifest.get("rejection_triggered")):
            errors.append(f"{path}: rejection_triggered mismatch")
    triage_path = root / str(data.get("triage_path", ""))
    if not triage_path.is_file():
        errors.append(f"{path}: triage_path missing")
    else:
        triage = load_yaml(triage_path)
        if str(triage.get("route")) != str(data.get("route")):
            errors.append(f"{path}: route differs from triage")
        if str(triage.get("candidate_class")) != str(data.get("candidate_class")):
            errors.append(f"{path}: candidate_class differs from triage")
    if not isinstance(data.get("allowed_review_actions"), list) or not data.get("allowed_review_actions"):
        errors.append(f"{path}: allowed_review_actions must be non-empty")
    checks = data.get("required_precision_checks")
    if not isinstance(checks, list) or len(checks) < 5:
        errors.append(f"{path}: required_precision_checks must contain at least five checks")
    metrics = data.get("metric_snapshot")
    if not isinstance(metrics, list) or len(metrics) > 32:
        errors.append(f"{path}: metric_snapshot must be a list of at most 32 items")
    return errors

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    args = p.parse_args()
    root = Path(args.root).resolve()
    review_root = root / "research" / "reviews"
    files = list(review_root.rglob("*-review-brief.yaml")) + list(review_root.rglob("*-review-brief.yml")) if review_root.exists() else []
    errors = []
    ids = set()
    for path in files:
        errors.extend(validate(root, path))
        try:
            data = load_yaml(path)
        except Exception:
            data = {}
        bid = data.get("brief_id") if isinstance(data, dict) else None
        if bid in ids:
            errors.append(f"{path}: duplicate brief_id {bid!r}")
        elif bid:
            ids.add(bid)
    if errors:
        print("CIPI review brief gate: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print(f"CIPI review brief gate: PASS ({len(files)} file(s))")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
