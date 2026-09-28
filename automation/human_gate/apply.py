from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")
OUTCOMES = {"COMPLETE", "REJECT", "DEFER"}
TARGET_TYPES = {"RESEARCH_JOB", "AUTONOMOUS_TRACK"}
SOURCES = {"DISCORD", "GITHUB_UI", "CLI"}
SENSITIVE_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\s*[:=]"),
)


def safe_id(value: str) -> str:
    cleaned = SAFE_RE.sub("-", value).strip("-._")
    if not cleaned:
        raise ValueError("identifier becomes empty after sanitization")
    return cleaned[:120]


def ensure_public_safe(label: str, value: str) -> None:
    text = value.strip()
    if any(pattern.search(text) for pattern in SENSITIVE_PATTERNS):
        raise ValueError(f"{label} contains secret-like material; public CIPI records must be redacted")


def load_snapshot(project_id: str) -> dict[str, Any]:
    path = ROOT / "research" / "continuity" / "projects" / project_id / "current.json"
    if not path.exists():
        raise ValueError(f"unknown project or missing Continuity snapshot: {project_id}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Continuity snapshot must be an object")
    return data


def current_gate_exists(snapshot: dict[str, Any], target_type: str, target_id: str, gate: str) -> bool:
    source = "RESEARCH_JOB" if target_type == "RESEARCH_JOB" else "AUTONOMOUS_TRACK"
    for item in snapshot.get("human_gates", []) or []:
        if not isinstance(item, dict):
            continue
        item_target = item.get("job_id") or item.get("track_id")
        if item.get("source") == source and str(item_target or "") == target_id:
            if gate in [str(x) for x in item.get("gates", []) or []]:
                return True
    return False


def decision_root(project_id: str, target_id: str, gate: str) -> Path:
    return (
        ROOT / "research" / "human_gates" / "decisions"
        / safe_id(project_id) / safe_id(target_id) / safe_id(gate)
    )


def load_records(folder: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not folder.exists():
        return records
    for path in sorted([*folder.glob("*.yaml"), *folder.glob("*.yml")]):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            records.append(data)
    records.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("decision_id") or "")))
    return records


def validate_record(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "decision_id", "project_id", "target_type", "target_id",
        "gate", "outcome", "evidence_ref", "rationale", "actor", "source",
        "source_generation_id", "source_state_digest", "authority", "operational_effect",
        "automatic_product_decision", "automatic_knowledge_promotion", "automatic_release",
        "created_at", "immutable",
    }
    missing = sorted(required - set(data))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if data.get("target_type") not in TARGET_TYPES:
        errors.append("invalid target_type")
    if data.get("outcome") not in OUTCOMES:
        errors.append("invalid outcome")
    if data.get("source") not in SOURCES:
        errors.append("invalid source")
    if data.get("authority") != "HUMAN_REVIEW":
        errors.append("authority must be HUMAN_REVIEW")
    for key in ("automatic_product_decision", "automatic_knowledge_promotion", "automatic_release"):
        if data.get(key) is not False:
            errors.append(f"{key} must be false")
    if data.get("immutable") is not True:
        errors.append("immutable must be true")
    digest = str(data.get("source_state_digest") or "")
    if not re.fullmatch(r"[a-f0-9]{64}", digest):
        errors.append("source_state_digest must be sha256 hex")
    if len(str(data.get("rationale") or "").strip()) < 10:
        errors.append("rationale must be at least 10 characters")
    if len(str(data.get("evidence_ref") or "").strip()) < 3:
        errors.append("evidence_ref must be at least 3 characters")
    expected_effect = (
        "RESOLVE_RESEARCH_JOB_GATE"
        if data.get("target_type") == "RESEARCH_JOB" and data.get("outcome") == "COMPLETE"
        else "RECORD_ONLY"
    )
    if data.get("operational_effect") != expected_effect:
        errors.append(f"operational_effect must be {expected_effect}")
    return errors


def validate_all() -> list[str]:
    errors: list[str] = []
    root = ROOT / "research" / "human_gates" / "decisions"
    if not root.exists():
        return errors
    seen: set[str] = set()
    for path in sorted([*root.rglob("*.yaml"), *root.rglob("*.yml")]):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.relative_to(ROOT)}: root must be mapping")
            continue
        errors.extend(f"{path.relative_to(ROOT)}: {item}" for item in validate_record(data))
        decision_id = str(data.get("decision_id") or "")
        if decision_id in seen:
            errors.append(f"{path.relative_to(ROOT)}: duplicate decision_id: {decision_id}")
        seen.add(decision_id)
    return errors


def apply(args: argparse.Namespace) -> Path:
    project_id = safe_id(args.project_id)
    target_type = args.target_type.upper()
    outcome = args.outcome.upper()
    source = args.source.upper()
    target_id = args.target_id.strip()
    gate = args.gate.strip()

    if target_type not in TARGET_TYPES:
        raise ValueError("target_type must be RESEARCH_JOB or AUTONOMOUS_TRACK")
    if outcome not in OUTCOMES:
        raise ValueError("outcome must be COMPLETE, REJECT, or DEFER")
    if source not in SOURCES:
        raise ValueError("source must be DISCORD, GITHUB_UI, or CLI")
    if len(args.rationale.strip()) < 10:
        raise ValueError("rationale must be at least 10 characters")
    if len(args.evidence_ref.strip()) < 3:
        raise ValueError("evidence_ref must be at least 3 characters")
    ensure_public_safe("evidence_ref", args.evidence_ref)
    ensure_public_safe("rationale", args.rationale)
    ensure_public_safe("actor", args.actor)

    snapshot = load_snapshot(project_id)
    if snapshot.get("freshness") != "FRESH":
        raise ValueError(f"snapshot is not FRESH: {snapshot.get('freshness')}")
    if snapshot.get("generation_id") != args.source_generation_id:
        raise ValueError("stale Human Gate submission: generation_id changed")
    if snapshot.get("source_state_digest") != args.source_state_digest:
        raise ValueError("stale Human Gate submission: source_state_digest changed")
    if not current_gate_exists(snapshot, target_type, target_id, gate):
        raise ValueError("target/gate is not present in the current Continuity Human Gate set")

    folder = decision_root(project_id, target_id, gate)
    existing = load_records(folder)
    supersedes = str(existing[-1].get("decision_id")) if existing else None

    run_id = safe_id(args.run_id or os.environ.get("GITHUB_RUN_ID", "manual"))
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    decision_id = f"{project_id}:{safe_id(target_id)}:{safe_id(gate)}:{run_id}"

    record: dict[str, Any] = {
        "schema_version": "1.0",
        "decision_id": decision_id,
        "project_id": project_id,
        "target_type": target_type,
        "target_id": target_id,
        "gate": gate,
        "outcome": outcome,
        "evidence_ref": args.evidence_ref.strip(),
        "rationale": args.rationale.strip(),
        "actor": args.actor.strip(),
        "source": source,
        "source_generation_id": args.source_generation_id,
        "source_state_digest": args.source_state_digest,
        "authority": "HUMAN_REVIEW",
        "operational_effect": (
            "RESOLVE_RESEARCH_JOB_GATE"
            if target_type == "RESEARCH_JOB" and outcome == "COMPLETE"
            else "RECORD_ONLY"
        ),
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
        "automatic_release": False,
        "created_at": created_at,
        "immutable": True,
        "supersedes": supersedes,
    }

    errors = validate_record(record)
    if errors:
        raise ValueError("; ".join(errors))

    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{run_id}.yaml"
    text = yaml.safe_dump(record, sort_keys=False, allow_unicode=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"immutable decision path already exists: {path}")
    else:
        path.write_text(text, encoding="utf-8")

    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"decision_path={path.relative_to(ROOT).as_posix()}\n")
            handle.write(f"operational_effect={record['operational_effect']}\n")
            handle.write(f"outcome={outcome}\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Record or validate CIPI Human Gate decisions.")
    parser.add_argument("--validate-all", action="store_true")
    parser.add_argument("--project-id")
    parser.add_argument("--target-type")
    parser.add_argument("--target-id")
    parser.add_argument("--gate")
    parser.add_argument("--outcome")
    parser.add_argument("--evidence-ref")
    parser.add_argument("--rationale")
    parser.add_argument("--actor")
    parser.add_argument("--source", default="CLI")
    parser.add_argument("--source-generation-id")
    parser.add_argument("--source-state-digest")
    parser.add_argument("--run-id")
    parser.add_argument("--github-output")
    args = parser.parse_args()

    if args.validate_all:
        errors = validate_all()
        if errors:
            print("CIPI Human Gate validation: FAIL")
            for error in errors:
                print("-", error)
            return 1
        print("CIPI Human Gate validation: PASS")
        return 0

    needed = [
        "project_id", "target_type", "target_id", "gate", "outcome",
        "evidence_ref", "rationale", "actor", "source_generation_id",
        "source_state_digest",
    ]
    missing = [name for name in needed if not getattr(args, name)]
    if missing:
        parser.error("missing required arguments: " + ", ".join(missing))

    try:
        path = apply(args)
    except Exception as exc:
        print(f"CIPI Human Gate decision: FAIL\n- {exc}")
        return 1

    print(f"CIPI Human Gate decision: PASS\n- {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
