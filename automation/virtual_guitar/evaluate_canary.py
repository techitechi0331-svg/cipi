from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FIELDS = {
    "job_id", "track_id", "candidate_id", "git_sha", "workflow_run_id",
    "runner", "test_profile", "inputs", "outputs", "metrics", "failures",
    "warnings", "evidence_class", "artifact_hashes", "continuation_proposal",
}


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    ).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("result bundle root must be an object")
    return data


def _write_yaml_if_absent(path: Path, payload: dict[str, Any]) -> bool:
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"immutable record collision: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def _validate(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(bundle))
    if missing:
        errors.append(f"missing fields: {missing}")
    if bundle.get("evidence_class") != "MEASURED":
        errors.append("evidence_class must be MEASURED for the deterministic canary")
    if not isinstance(bundle.get("failures"), list):
        errors.append("failures must be a list")
    metrics = bundle.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("metrics must be an object")
    proposal = bundle.get("continuation_proposal")
    if not isinstance(proposal, dict):
        errors.append("continuation_proposal must be an object")
    else:
        if proposal.get("automatic_product_integration") is not False:
            errors.append("automatic_product_integration must be false")
        if proposal.get("automatic_knowledge_promotion") is not False:
            errors.append("automatic_knowledge_promotion must be false")
        if proposal.get("authority") != "PROPOSAL_ONLY":
            errors.append("continuation authority must remain PROPOSAL_ONLY")
    return errors


def _decision(bundle: dict[str, Any], validation_errors: list[str]) -> tuple[str, str, list[str]]:
    reasons: list[str] = []
    if validation_errors:
        return "RE_ENTRY_REQUIRED", "INVALID_RESULT_BUNDLE", validation_errors

    failures = bundle.get("failures") or []
    metrics = bundle.get("metrics") or {}
    candidate_count = int(metrics.get("candidate_count", 0) or 0)
    all_finite = metrics.get("all_finite") is True

    if failures:
        reasons.append("canary reported one or more failures")
    if candidate_count < 3:
        reasons.append("fewer than three damping candidates were measured")
    if not all_finite:
        reasons.append("one or more damping candidates produced non-finite output")

    if reasons:
        return "RE_ENTRY_REQUIRED", "CANARY_MEASUREMENT_FAILURE", reasons

    return (
        "CONTINUE",
        "COMPLETE_FOR_NOW",
        [
            "dedicated runner returned a machine-readable Result Bundle",
            "three or more damping candidates were measured",
            "all reported canary outputs were finite",
            "authority boundaries remained proposal-only with production integration disabled",
        ],
    )


def _next_job(bundle: dict[str, Any], source_hash: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "job_id": "GUITAR-EPOCH1-LANES-001",
        "track_id": str(bundle.get("track_id") or "VIRTUAL-GUITAR-PHYSICAL-001"),
        "state": "READY_PROPOSAL",
        "scheduling_mode": "DYNAMIC",
        "max_logical_lanes": 4,
        "max_guitar_runner_jobs": 1,
        "max_integration_epochs_in_flight": 1,
        "source_canary_hash": source_hash,
        "integration_epoch": 1,
        "lanes": [
            {
                "lane": "A",
                "initial_job": "Living String v0.1 refinement",
                "touched_modules": ["Source/PhysicalModel/Strings/"],
                "exit_condition": "persistent state, natural decay, and damping termination are regression-tested",
            },
            {
                "lane": "B",
                "initial_job": "Virtual Guitarist State v0.1",
                "touched_modules": ["Source/Performance/VirtualGuitarist/"],
                "exit_condition": "left/right hand state transitions and Decision Log fields are observable",
            },
            {
                "lane": "C",
                "initial_job": "MIDI Decision Harness v0.1",
                "touched_modules": ["Tests/MidiDecision/"],
                "exit_condition": "deterministic phrase decisions execute and regression expectations are recorded",
            },
            {
                "lane": "D",
                "initial_job": "Fingering v0.1",
                "touched_modules": ["Source/Performance/Fingering/"],
                "exit_condition": "playability and movement-cost decisions are testable before phrase lookahead expansion",
            },
        ],
        "epoch_gate": [
            "build",
            "unit_tests",
            "midi_decision_tests",
            "performance_tests",
            "cpu_measurement",
            "evidence_review",
            "blocker_review",
            "lane_priority_review",
        ],
        "post_epoch_decisions": ["KEEP", "ROTATE", "BLOCK", "RE-ENTER", "COMPLETE_FOR_NOW"],
        "authority": "CIPI_NEXT_JOB_PROPOSAL",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
        "automatic_release": False,
    }


def reconcile(root: Path) -> dict[str, Any]:
    artifact_root = root / "research" / "cross_repo" / "artifacts" / "virtual_guitar"
    output_root = root / "research" / "plugins" / "virtual-guitar" / "canary"
    changed = False
    processed = 0
    invalid = 0
    continued = 0

    if not artifact_root.exists():
        return {"changed": False, "processed": 0, "invalid": 0, "continued": 0}

    for path in sorted(artifact_root.rglob("result_bundle.json")):
        raw = path.read_bytes()
        source_hash = hashlib.sha256(raw).hexdigest()
        evaluation_path = output_root / "evaluations" / f"{source_hash[:20]}.yaml"
        if evaluation_path.exists():
            continue

        try:
            bundle = _load_json(path)
            errors = _validate(bundle)
        except Exception as exc:
            bundle = {}
            errors = [f"parse error: {exc}"]

        decision, stop_reason, reasons = _decision(bundle, errors)
        evaluation = {
            "schema_version": "1.0",
            "evaluation_id": f"GUITAR-CANARY-EVAL-{source_hash[:12].upper()}",
            "source_artifact": path.as_posix(),
            "source_sha256": source_hash,
            "job_id": str(bundle.get("job_id") or "UNKNOWN"),
            "track_id": str(bundle.get("track_id") or "UNKNOWN"),
            "evidence_class": str(bundle.get("evidence_class") or "INVALID"),
            "decision": decision,
            "stop_reason": stop_reason,
            "reasons": reasons,
            "scope": "E2E_RESEARCH_BRIDGE_AND_DETERMINISTIC_DAMPING_CANARY_ONLY",
            "does_not_establish": [
                "production guitar realism",
                "listening preference",
                "Cubase host compatibility",
                "final damping constants",
                "release readiness",
            ],
            "authority": "CIPI_EVIDENCE_EVALUATION",
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
            "immutable": True,
        }
        changed = _write_yaml_if_absent(evaluation_path, evaluation) or changed
        processed += 1

        decision_record = {
            "schema_version": "1.0",
            "decision_id": f"GUITAR-CANARY-DECISION-{source_hash[:12].upper()}",
            "evaluation_id": evaluation["evaluation_id"],
            "decision": decision,
            "stop_reason": stop_reason,
            "next_job_id": "GUITAR-EPOCH1-LANES-001" if decision == "CONTINUE" else None,
            "authority": "CIPI_CONTINUATION_DECISION",
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
            "immutable": True,
        }
        changed = _write_yaml_if_absent(output_root / "decisions" / f"{source_hash[:20]}.yaml", decision_record) or changed

        if decision == "CONTINUE":
            changed = _write_yaml_if_absent(
                output_root / "next_jobs" / "GUITAR-EPOCH1-LANES-001.yaml",
                _next_job(bundle, source_hash),
            ) or changed
            continued += 1
        else:
            invalid += 1

    return {"changed": changed, "processed": processed, "invalid": invalid, "continued": continued}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate virtual-guitar canary evidence under CIPI authority")
    parser.add_argument("--root", default=".")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    result = reconcile(Path(args.root).resolve())
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"changed={'true' if result['changed'] else 'false'}\n")
            handle.write(f"processed={result['processed']}\n")
            handle.write(f"continued={result['continued']}\n")
    print(
        "Virtual Guitar Canary Evaluation:",
        f"changed={result['changed']}",
        f"processed={result['processed']}",
        f"continued={result['continued']}",
        f"invalid={result['invalid']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
