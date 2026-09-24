from __future__ import annotations

from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "schema_version","job_id","state","track","research_question","hypothesis",
    "counter_hypotheses","baseline","variants","metrics","acceptance","rejection",
    "max_runs","timeout_minutes",
}
STATES = {"QUEUED","CLAIMED","RUNNING","COMPLETED","FAILED","REJECTED","CANCELLED"}
ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,95}$")

def validate(path: Path) -> list[str]:
    errors=[]
    try:
        data=yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: root must be a mapping"]
    missing=sorted(REQUIRED-set(data))
    if missing:
        errors.append(f"{path}: missing required keys: {', '.join(missing)}")
        return errors
    if data["schema_version"] != "1.0":
        errors.append(f"{path}: schema_version must be 1.0")
    if not isinstance(data["job_id"], str) or not ID_RE.fullmatch(data["job_id"]):
        errors.append(f"{path}: invalid job_id")
    if data["state"] not in STATES:
        errors.append(f"{path}: invalid state {data['state']!r}")
    track=data["track"]
    if not isinstance(track, dict) or not {"id","path"} <= set(track):
        errors.append(f"{path}: track requires id and path")
    elif not str(track["path"]).startswith("research/"):
        errors.append(f"{path}: track.path must stay under research/")
    for key in ("counter_hypotheses","baseline","variants","metrics","acceptance","rejection"):
        if not isinstance(data[key], list) or not data[key]:
            errors.append(f"{path}: {key} must be a non-empty list")
    if not isinstance(data["max_runs"], int) or not 1 <= data["max_runs"] <= 10000:
        errors.append(f"{path}: max_runs must be 1..10000")
    if not isinstance(data["timeout_minutes"], int) or not 1 <= data["timeout_minutes"] <= 1440:
        errors.append(f"{path}: timeout_minutes must be 1..1440")
    return errors

def main() -> int:
    files=list((ROOT/"research/jobs").rglob("*.yaml")) if (ROOT/"research/jobs").exists() else []
    files += list((ROOT/"research/jobs").rglob("*.yml")) if (ROOT/"research/jobs").exists() else []
    files += [ROOT/"automation/examples/research_job.yaml"]
    errors=[]
    for path in files:
        if path.exists():
            errors += validate(path)
    if errors:
        print("CIPI research job gate: FAIL")
        for e in errors: print("-",e)
        return 1
    print(f"CIPI research job gate: PASS ({len(files)} file(s))")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
