from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

TRACK_ID = "VIRTUAL-GUITAR-V11-BASELINE-MEASURE-001"
NEXT_JOB_ID = "VIRTUAL-GUITAR-PICKUP-DI-IMPLEMENTATION-RESEARCH-001"
NEXT_TRACK_ID = "VIRTUAL-GUITAR-PICKUP-DI-IMPLEMENTATION-RESEARCH-001"

REQUIRED_ACCEPTANCE = {
    "all_18_raw_coordinates_rendered",
    "all_18_manifests_present",
    "repeat_render_check_complete",
    "wav_validity_pass",
    "no_nan_inf",
    "same_midi_collision_result_recorded",
    "source_tree_unchanged",
    "all_15_pickup_di_requests_explicitly_classified",
    "no_raw_to_di_fake_substitution",
    "category_level_gap_report_generated",
    "no_single_scalar_realism_verdict",
}


def _write_yaml_if_absent(path: Path, payload: dict[str, Any]) -> bool:
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"immutable record collision: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def _load_summary(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("baseline summary root must be an object")
    return data


def _validate(summary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if summary.get("track_id") != TRACK_ID:
        errors.append("unexpected track_id")
    if summary.get("status") != "COMPLETED":
        errors.append("baseline status must be COMPLETED")
    coordinates = summary.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) != 18:
        errors.append("exactly 18 RAW coordinates are required")
    pickup = summary.get("pickup_di_classification")
    if not isinstance(pickup, list) or len(pickup) != 15:
        errors.append("exactly 15 PICKUP_DI classifications are required")
    else:
        for item in pickup:
            if not isinstance(item, dict):
                errors.append("invalid PICKUP_DI classification entry")
                break
            if item.get("status") not in {"PASS", "BLOCKED_STAGE_MISMATCH"}:
                errors.append("PICKUP_DI request is not explicitly classified")
                break
            if item.get("raw_to_di_fake_substitution") is not False:
                errors.append("RAW-to-DI substitution is forbidden")
                break
    acceptance = summary.get("acceptance")
    if not isinstance(acceptance, dict):
        errors.append("acceptance object missing")
    else:
        missing = sorted(REQUIRED_ACCEPTANCE - set(acceptance))
        if missing:
            errors.append(f"missing acceptance fields: {missing}")
        for key in REQUIRED_ACCEPTANCE:
            if acceptance.get(key) is not True:
                errors.append(f"acceptance failed: {key}")
        if acceptance.get("product_repository_persistent_write") is not False:
            errors.append("product repository write must remain false")
    authority = summary.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority object missing")
    else:
        for key in (
            "product_repository_write",
            "automatic_product_decision",
            "automatic_knowledge_promotion",
            "human_listening_adoption",
        ):
            if authority.get(key) is not False:
                errors.append(f"authority violation: {key}")
    return errors


def _next_track(source_hash: str, summary: dict[str, Any]) -> dict[str, Any]:
    red_team = summary.get("same_midi_red_team", [])
    collapse = [
        item for item in red_team
        if isinstance(item, dict)
        and item.get("classification") == "STRING_FRET_IDENTITY_COLLAPSE_CONFIRMED"
    ]
    return {
        "schema_version": "1.0",
        "track_id": NEXT_TRACK_ID,
        "state": "READY_FOR_RESEARCH",
        "project": "virtual-guitar",
        "source_baseline_evidence_sha256": source_hash,
        "research_question": (
            "Can an evidence-backed physical/electrical Pickup/DI observation path preserve "
            "string/fret identity and reproduce measured pickup-configuration deltas without "
            "using downstream Amp/Cab/Mic coloration or writing to the product repository?"
        ),
        "baseline_findings": {
            "same_midi_identity_collapse_count": len(collapse),
            "pickup_di_stage": summary.get("gap_report", {}).get("pickup_stage_availability"),
            "deterministic_repeatability": summary.get("gap_report", {}).get("deterministic_repeatability"),
        },
        "required_model_scope": [
            "pickup_position",
            "string_displacement_observation",
            "magnetic_observation_model",
            "pickup_R_L_C_behavior",
            "volume_tone_interaction",
            "cable_load",
            "output_impedance",
            "guitar_output_jack_behavior",
        ],
        "reuse_required": [
            "existing CIPI Pickup Observation evidence",
            "existing Pickup electrical evidence",
            "existing Cable/Load research",
            "existing Guitar Electrical Port contract",
            "existing Guitar/Amp electrical architecture",
        ],
        "authority": {
            "product_repository_write": False,
            "product_integration": False,
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
        },
        "human_gate_required_for_research": False,
        "downstream_human_gates": [
            "REAL_DI_AB",
            "FINAL_SUBJECTIVE_PICKUP_TONE",
            "PRODUCT_ADOPTION_DECISION",
        ],
    }


def _next_job(source_hash: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "job_id": NEXT_JOB_ID,
        "state": "QUEUED",
        "priority": 82,
        "track": {
            "id": NEXT_TRACK_ID,
            "path": "research/plugins/virtual-guitar/research-tracks",
        },
        "research_phase": "PICKUP_DI_RESEARCH_CANDIDATE",
        "source_baseline_evidence_sha256": source_hash,
        "research_question": (
            "What minimum physical/electrical Pickup/DI architecture can explain the baseline "
            "string/fret identity and pickup-stage gaps while preserving explicit uncertainty?"
        ),
        "hypothesis": (
            "Separating string-state observation, magnetic pickup behavior, passive R/L/C network, "
            "controls, cable load, output impedance and guitar jack will provide a falsifiable "
            "PICKUP_DI candidate without disguising RAW-string model error."
        ),
        "counter_hypotheses": [
            "A static EQ-only pickup model is sufficient.",
            "String/fret identity can be discarded once MIDI pitch is known.",
            "Amp/Cab/Mic coloration is required to make pickup behavior plausible.",
        ],
        "baseline": [
            f"{TRACK_ID}: COMPLETED MEASURED baseline evidence {source_hash}",
            "current v1.1 collapses both same-MIDI string/fret red-team pairs",
            "current v1.1 has no valid PICKUP_DI stage; 15/15 requests are BLOCKED_STAGE_MISMATCH",
            "product repository write remains false",
        ],
        "variants": [
            "PHYSICAL_MAGNETIC_OBSERVATION_PLUS_PASSIVE_RLC",
            "REDUCED_ORDER_MAGNETIC_OBSERVATION_PLUS_PASSIVE_RLC",
            "STATIC_EQ_ONLY_COUNTER_HYPOTHESIS",
        ],
        "metrics": [
            "pickup_configuration_delta_error",
            "string_fret_identity_preservation",
            "electrical_transfer_consistency",
            "deterministic_output",
            "parameter_identifiability",
            "reference_di_stage_compatibility",
        ],
        "acceptance": [
            "reuse existing CIPI pickup/electrical/cable/output-port evidence before new research",
            "produce an explicit RAW_PHYSICAL_STRING to PICKUP_DI stage contract",
            "no RAW-to-DI fake substitution",
            "no static EQ-only adoption without falsification against electrical alternatives",
            "no product repository write",
            "prepare matched Reference DI validation as a downstream gate",
        ],
        "rejection": [
            "candidate collapses string/fret identity to MIDI pitch only",
            "candidate uses RAW output relabelled as PICKUP_DI",
            "candidate requires Amp/Cab/Mic coloration to hide upstream defects",
            "candidate introduces unsupported electrical constants without evidence classification",
            "candidate performs product repository writes or automatic product adoption",
        ],
        "max_runs": 3,
        "timeout_minutes": 20,
        "experiment_adapter": "virtual_guitar_pickup_electrical_foundation_v1",
        "allowed_operations": [
            "inspect_existing_cipi_pickup_evidence",
            "inspect_existing_guitar_amp_electrical_contracts",
            "perform_bounded_model_discrimination",
            "add_research_side_tests_and_measurement_adapters",
            "prepare_pickup_di_stage_contract",
            "write_research_evidence",
        ],
        "prohibited_operations": [
            "product_repository_write",
            "automatic_product_integration",
            "automatic_knowledge_promotion",
            "raw_to_di_fake_substitution",
            "use_amp_cab_mic_to_hide_string_or_pickup_defects",
            "auto_release",
        ],
        "authority_boundaries": {
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
            "product_repository_write": False,
        },
    }


def reconcile(root: Path) -> dict[str, Any]:
    artifact_root = root / "research" / "cross_repo" / "artifacts" / "cipi"
    output_root = root / "research" / "plugins" / "virtual-guitar" / "baseline"
    changed = False
    processed = 0
    continued = 0
    invalid = 0

    if not artifact_root.exists():
        return {"changed": False, "processed": 0, "continued": 0, "invalid": 0}

    for path in sorted(artifact_root.rglob("baseline-summary.json")):
        raw = path.read_bytes()
        source_hash = hashlib.sha256(raw).hexdigest()
        evaluation_path = output_root / "evaluations" / f"{source_hash[:20]}.yaml"
        if evaluation_path.exists():
            continue

        try:
            summary = _load_summary(path)
            errors = _validate(summary)
        except Exception as exc:
            summary = {}
            errors = [f"parse error: {exc}"]

        decision = "CONTINUE" if not errors else "RE_ENTRY_REQUIRED"
        stop_reason = "BASELINE_MEASURED" if not errors else "INVALID_BASELINE_EVIDENCE"
        evaluation = {
            "schema_version": "1.0",
            "evaluation_id": f"VG-V11-BASELINE-EVAL-{source_hash[:12].upper()}",
            "source_artifact": path.as_posix(),
            "source_sha256": source_hash,
            "track_id": str(summary.get("track_id") or "UNKNOWN"),
            "evidence_class": "MEASURED" if not errors else "INVALID",
            "decision": decision,
            "stop_reason": stop_reason,
            "validation_errors": errors,
            "authority": "CIPI_EVIDENCE_EVALUATION",
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
            "immutable": True,
        }
        changed = _write_yaml_if_absent(evaluation_path, evaluation) or changed
        changed = _write_yaml_if_absent(
            output_root / "decisions" / f"{source_hash[:20]}.yaml",
            {
                "schema_version": "1.0",
                "decision_id": f"VG-V11-BASELINE-DECISION-{source_hash[:12].upper()}",
                "evaluation_id": evaluation["evaluation_id"],
                "decision": decision,
                "stop_reason": stop_reason,
                "next_job_id": NEXT_JOB_ID if decision == "CONTINUE" else None,
                "authority": "CIPI_CONTINUATION_DECISION",
                "automatic_product_decision": False,
                "automatic_knowledge_promotion": False,
                "immutable": True,
            },
        ) or changed
        processed += 1

        if decision == "CONTINUE":
            changed = _write_yaml_if_absent(
                root / "research" / "plugins" / "virtual-guitar" / "research-tracks" / f"{NEXT_TRACK_ID}.yaml",
                _next_track(source_hash, summary),
            ) or changed
            changed = _write_yaml_if_absent(
                root / "research" / "jobs" / "queued" / f"{NEXT_JOB_ID}.yaml",
                _next_job(source_hash, summary),
            ) or changed
            continued += 1
        else:
            invalid += 1

    return {
        "changed": changed,
        "processed": processed,
        "continued": continued,
        "invalid": invalid,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    result = reconcile(Path(args.root).resolve())
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"changed={'true' if result['changed'] else 'false'}\n")
            handle.write(f"processed={result['processed']}\n")
            handle.write(f"continued={result['continued']}\n")
            handle.write(f"invalid={result['invalid']}\n")
    print(
        "Virtual Guitar v1.1 Baseline Evaluation:",
        f"changed={result['changed']}",
        f"processed={result['processed']}",
        f"continued={result['continued']}",
        f"invalid={result['invalid']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
