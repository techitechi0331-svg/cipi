from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"claim", "evidence_type", "scope", "source_run", "promotion_requested"}
EVIDENCE = {"SOURCE_CANDIDATE", "MEASURED", "INFERRED", "HYPOTHESIS"}
PROMOTION = {"HYPOTHESIS", "LIKELY", "PROVISIONAL"}

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
        errors.append(f"{path}: missing keys: {', '.join(missing)}")
        return errors
    if data["evidence_type"] not in EVIDENCE:
        errors.append(f"{path}: invalid evidence_type")
    if data["promotion_requested"] not in PROMOTION:
        errors.append(f"{path}: invalid promotion_requested")
    if not str(data["source_run"]).startswith("research/runs/"):
        errors.append(f"{path}: source_run must point under research/runs/")
    if len(str(data["claim"]).strip()) < 10:
        errors.append(f"{path}: claim is too short")
    return errors

def main() -> int:
    root = ROOT / "research" / "knowledge_candidates"
    files = list(root.rglob("*.yaml")) + list(root.rglob("*.yml")) if root.exists() else []
    errors = []
    for path in files:
        errors.extend(validate(path))
    if errors:
        print("CIPI evidence candidate gate: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print(f"CIPI evidence candidate gate: PASS ({len(files)} file(s))")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
