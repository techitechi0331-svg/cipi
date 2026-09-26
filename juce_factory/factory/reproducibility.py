from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .contract import canonical_json
from .result_bundle import ResultBundleError, validate_result_bundle

COMPARISON_VERSION = "1.0"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ReproducibilityComparisonError(ValueError):
    pass


def _load_bundle(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ReproducibilityComparisonError(f"{path} must contain a JSON object")
    validate_result_bundle(value)
    return value


def _report_hash(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("report_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def compare_pass_bundles(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    validate_result_bundle(first)
    validate_result_bundle(second)
    if first["factory_status"] != "VALIDATION_PASS" or second["factory_status"] != "VALIDATION_PASS":
        raise ReproducibilityComparisonError("artifact comparison requires two VALIDATION_PASS bundles")

    same_contract = first["contract_sha256"] == second["contract_sha256"]
    same_generated_source = (
        first["generated_source_sha256"] == second["generated_source_sha256"]
    )

    context_keys = (
        "factory_version",
        "dsp_source_revision",
        "juce_version",
        "platform",
        "formats",
        "validation_matrix",
    )
    module_context_keys = (
        "dsp_module_id",
        "dsp_implementation_id",
        "dsp_certification_status",
        "dsp_validation_profile",
        "dsp_module_spec_sha256",
        "dsp_module_registry_sha256",
    )
    same_recorded_factory_context = (
        first["schema_version"] == second["schema_version"]
        and all(first[key] == second[key] for key in context_keys)
        and (
            first["schema_version"] == "1.0"
            or all(first[key] == second[key] for key in module_context_keys)
        )
    )
    artifact_hash_match = first["artifact_hashes"] == second["artifact_hashes"]

    if not same_contract or not same_generated_source:
        classification = "NOT_COMPARABLE_SOURCE_DIFF"
    elif not same_recorded_factory_context:
        classification = "NOT_COMPARABLE_RECORDED_CONTEXT_DIFF"
    elif artifact_hash_match:
        classification = "ARTIFACT_HASH_MATCH"
    else:
        classification = "ARTIFACT_HASH_DIFF"

    report: dict[str, Any] = {
        "schema_version": COMPARISON_VERSION,
        "comparison_kind": "FACTORY_ARTIFACT_HASH_COMPARISON",
        "first_bundle_hash": first["bundle_hash"],
        "second_bundle_hash": second["bundle_hash"],
        "same_contract": same_contract,
        "same_generated_source": same_generated_source,
        "same_recorded_factory_context": same_recorded_factory_context,
        "artifact_hash_match": artifact_hash_match,
        "classification": classification,
        "automatic_gate_decision": False,
        "bit_reproducibility_confirmed": False,
        "limitations": [
            "This comparison observes promoted artifact hashes only.",
            "It does not prove bit-reproducible builds because compiler, linker, SDK and hosted-runner image identity are not yet fully captured in the Factory Result Bundle.",
            "A hash difference is MEASURED evidence to investigate, not an automatic product or release failure.",
        ],
    }
    report["report_hash"] = _report_hash(report)
    return report


def validate_comparison_report(report: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "comparison_kind",
        "first_bundle_hash",
        "second_bundle_hash",
        "same_contract",
        "same_generated_source",
        "same_recorded_factory_context",
        "artifact_hash_match",
        "classification",
        "automatic_gate_decision",
        "bit_reproducibility_confirmed",
        "limitations",
        "report_hash",
    }
    missing = sorted(required - set(report))
    unknown = sorted(set(report) - required)
    if missing:
        raise ReproducibilityComparisonError(f"comparison report missing fields: {missing}")
    if unknown:
        raise ReproducibilityComparisonError(f"comparison report contains unknown fields: {unknown}")
    if report["schema_version"] != COMPARISON_VERSION:
        raise ReproducibilityComparisonError("unsupported comparison schema_version")
    if report["comparison_kind"] != "FACTORY_ARTIFACT_HASH_COMPARISON":
        raise ReproducibilityComparisonError("unexpected comparison kind")
    for key in ("first_bundle_hash", "second_bundle_hash", "report_hash"):
        if not isinstance(report[key], str) or not _SHA256.fullmatch(report[key]):
            raise ReproducibilityComparisonError(f"{key} must be a lowercase SHA-256 digest")
    for key in (
        "same_contract",
        "same_generated_source",
        "same_recorded_factory_context",
        "artifact_hash_match",
    ):
        if not isinstance(report[key], bool):
            raise ReproducibilityComparisonError(f"{key} must be boolean")
    if report["automatic_gate_decision"] is not False:
        raise ReproducibilityComparisonError("automatic_gate_decision must remain false")
    if report["bit_reproducibility_confirmed"] is not False:
        raise ReproducibilityComparisonError("bit_reproducibility_confirmed must remain false")
    allowed = {
        "NOT_COMPARABLE_SOURCE_DIFF",
        "NOT_COMPARABLE_RECORDED_CONTEXT_DIFF",
        "ARTIFACT_HASH_MATCH",
        "ARTIFACT_HASH_DIFF",
    }
    if report["classification"] not in allowed:
        raise ReproducibilityComparisonError("invalid comparison classification")
    if not isinstance(report["limitations"], list) or not report["limitations"]:
        raise ReproducibilityComparisonError("limitations must be a non-empty array")
    if any(not isinstance(value, str) or not value.strip() for value in report["limitations"]):
        raise ReproducibilityComparisonError("limitations entries must be non-empty strings")

    classification = report["classification"]
    if classification == "ARTIFACT_HASH_MATCH":
        if not (
            report["same_contract"]
            and report["same_generated_source"]
            and report["same_recorded_factory_context"]
            and report["artifact_hash_match"]
        ):
            raise ReproducibilityComparisonError("ARTIFACT_HASH_MATCH invariants are inconsistent")
    elif classification == "ARTIFACT_HASH_DIFF":
        if not (
            report["same_contract"]
            and report["same_generated_source"]
            and report["same_recorded_factory_context"]
            and not report["artifact_hash_match"]
        ):
            raise ReproducibilityComparisonError("ARTIFACT_HASH_DIFF invariants are inconsistent")
    elif classification == "NOT_COMPARABLE_SOURCE_DIFF":
        if report["same_contract"] and report["same_generated_source"]:
            raise ReproducibilityComparisonError("source-diff classification requires a source difference")
    elif classification == "NOT_COMPARABLE_RECORDED_CONTEXT_DIFF":
        if not (
            report["same_contract"]
            and report["same_generated_source"]
            and not report["same_recorded_factory_context"]
        ):
            raise ReproducibilityComparisonError("context-diff classification invariants are inconsistent")

    if report["report_hash"] != _report_hash(report):
        raise ReproducibilityComparisonError("comparison report hash mismatch")


def write_comparison_report(path: str | Path, report: dict[str, Any]) -> None:
    validate_comparison_report(report)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(prog="juce-factory-repro")
    parser.add_argument("first")
    parser.add_argument("second")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        first = _load_bundle(args.first)
        second = _load_bundle(args.second)
        report = compare_pass_bundles(first, second)
        write_comparison_report(args.output, report)
        print(json.dumps({
            "status": "FACTORY_ARTIFACT_COMPARISON_WRITTEN",
            "classification": report["classification"],
            "report_hash": report["report_hash"],
        }))
        return 0
    except (ReproducibilityComparisonError, ResultBundleError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FACTORY_ARTIFACT_COMPARISON_ERROR", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
