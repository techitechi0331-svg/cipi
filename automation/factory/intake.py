from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from juce_factory.factory.contract import canonical_json
from juce_factory.factory.result_bundle import validate_result_bundle

EVIDENCE_SCHEMA_VERSION = "1.1"
SUPPORTED_EVIDENCE_SCHEMA_VERSIONS = {"1.0", "1.1"}
_MODULE_PROVENANCE_FIELDS = {
    "dsp_module_id",
    "dsp_implementation_id",
    "dsp_certification_status",
    "dsp_validation_profile",
    "dsp_module_spec_sha256",
    "dsp_module_registry_sha256",
}
_PLUGIN_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class FactoryEvidenceIntakeError(ValueError):
    pass


def _record_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("record_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def load_bundle(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise FactoryEvidenceIntakeError("Factory Result Bundle must be a JSON object")
    validate_result_bundle(value)
    return value


def build_evidence_record(bundle: dict[str, Any]) -> dict[str, Any]:
    validate_result_bundle(bundle)

    plugin_id = bundle["plugin_id"]
    if not _PLUGIN_ID.fullmatch(plugin_id):
        raise FactoryEvidenceIntakeError("plugin_id is unsafe for evidence storage")

    status = bundle["factory_status"]
    if status == "VALIDATION_PASS":
        claim = (
            f"{plugin_id} passed the declared JUCE Factory manufacturing and host-safety "
            f"validation gates for contract {bundle['contract_sha256']}."
        )
    else:
        claim = (
            f"{plugin_id} was quarantined by JUCE Factory with failure class "
            f"{bundle['failure_class']} for contract {bundle['contract_sha256']}."
        )

    evidence_version = "1.1" if bundle["schema_version"] == "1.1" else "1.0"
    module_provenance = (
        {key: bundle[key] for key in _MODULE_PROVENANCE_FIELDS}
        if evidence_version == "1.1"
        else {}
    )

    record: dict[str, Any] = {
        "schema_version": evidence_version,
        "evidence_id": f"FACTORY-{bundle['bundle_hash'][:16].upper()}",
        "source_system": "JUCE_FACTORY",
        "source_bundle_hash": bundle["bundle_hash"],
        "plugin_id": plugin_id,
        "plugin_version": bundle["plugin_version"],
        "factory_status": status,
        "evidence_type": "MEASURED",
        "scope": "manufacturing_and_host_safety_only",
        "claim": claim,
        "contract_sha256": bundle["contract_sha256"],
        "generated_source_sha256": bundle["generated_source_sha256"],
        "source_revision": bundle["source_revision"],
        "validation_revision": bundle["validation_revision"],
        "validation_base_revision": bundle["validation_base_revision"],
        "dsp_source_revision": bundle["dsp_source_revision"],
        "failure_class": bundle["failure_class"],
        "raw_audio_persisted": False,
        "automatic_final_decision": False,
        "promotion_requested": False,
        "promotion_authority": False,
        "product_release_authority": False,
        "cubase_confirmed": False,
        "listening_confirmed": False,
        **module_provenance,
    }
    record["record_hash"] = _record_hash(record)
    validate_evidence_record(record)
    return record


def validate_evidence_record(record: dict[str, Any]) -> None:
    base_required = {
        "schema_version", "evidence_id", "source_system", "source_bundle_hash",
        "plugin_id", "plugin_version", "factory_status", "evidence_type", "scope",
        "claim", "contract_sha256", "generated_source_sha256", "source_revision",
        "validation_revision", "validation_base_revision", "dsp_source_revision",
        "failure_class", "raw_audio_persisted",
        "automatic_final_decision", "promotion_requested", "promotion_authority",
        "product_release_authority", "cubase_confirmed", "listening_confirmed",
        "record_hash",
    }
    version = record.get("schema_version")
    if version not in SUPPORTED_EVIDENCE_SCHEMA_VERSIONS:
        raise FactoryEvidenceIntakeError("unsupported Factory evidence schema_version")

    required = set(base_required)
    allowed = set(base_required)
    if version == "1.1":
        required |= _MODULE_PROVENANCE_FIELDS
        allowed |= _MODULE_PROVENANCE_FIELDS

    missing = sorted(required - set(record))
    unknown = sorted(set(record) - allowed)
    if missing:
        raise FactoryEvidenceIntakeError(f"Factory evidence record missing fields: {missing}")
    if unknown:
        raise FactoryEvidenceIntakeError(f"Factory evidence record contains unknown fields: {unknown}")
    if record["source_system"] != "JUCE_FACTORY":
        raise FactoryEvidenceIntakeError("unexpected Factory evidence source_system")
    if not isinstance(record["plugin_id"], str) or not _PLUGIN_ID.fullmatch(record["plugin_id"]):
        raise FactoryEvidenceIntakeError("Factory evidence plugin_id is invalid")
    if not isinstance(record["plugin_version"], str) or not record["plugin_version"].strip():
        raise FactoryEvidenceIntakeError("Factory evidence plugin_version must be non-empty")
    for key in ("source_bundle_hash", "contract_sha256", "generated_source_sha256", "record_hash"):
        if not isinstance(record[key], str) or not _SHA256.fullmatch(record[key]):
            raise FactoryEvidenceIntakeError(f"{key} must be a lowercase SHA-256 digest")
    for key in ("source_revision", "validation_revision", "validation_base_revision"):
        if not isinstance(record[key], str) or not _GIT_SHA.fullmatch(record[key]):
            raise FactoryEvidenceIntakeError(f"{key} must be a lowercase 40-character Git SHA")
    if version == "1.1":
        for key in ("dsp_module_spec_sha256", "dsp_module_registry_sha256"):
            if not isinstance(record[key], str) or not _SHA256.fullmatch(record[key]):
                raise FactoryEvidenceIntakeError(f"{key} must be a lowercase SHA-256 digest")
        for key in ("dsp_module_id", "dsp_implementation_id", "dsp_validation_profile"):
            if not isinstance(record[key], str) or not record[key].strip():
                raise FactoryEvidenceIntakeError(f"{key} must be non-empty")
        if record["dsp_certification_status"] != "FACTORY_CERTIFIED":
            raise FactoryEvidenceIntakeError(
                "dsp_certification_status must be FACTORY_CERTIFIED"
            )
    expected_id = f"FACTORY-{record['source_bundle_hash'][:16].upper()}"
    if record["evidence_id"] != expected_id:
        raise FactoryEvidenceIntakeError("Factory evidence_id does not match source bundle hash")
    if not isinstance(record["claim"], str) or len(record["claim"].strip()) < 20:
        raise FactoryEvidenceIntakeError("Factory evidence claim is too short")
    if record["factory_status"] not in {"VALIDATION_PASS", "QUARANTINED"}:
        raise FactoryEvidenceIntakeError("unsupported Factory evidence status")
    if record["evidence_type"] != "MEASURED":
        raise FactoryEvidenceIntakeError("Factory evidence must remain MEASURED")
    if record["scope"] != "manufacturing_and_host_safety_only":
        raise FactoryEvidenceIntakeError("Factory evidence scope must remain bounded")
    for key in (
        "raw_audio_persisted", "automatic_final_decision", "promotion_requested",
        "promotion_authority", "product_release_authority", "cubase_confirmed",
        "listening_confirmed",
    ):
        if record[key] is not False:
            raise FactoryEvidenceIntakeError(f"{key} must be false")
    if record["factory_status"] == "VALIDATION_PASS" and record["failure_class"] is not None:
        raise FactoryEvidenceIntakeError("VALIDATION_PASS evidence must not carry failure_class")
    if record["factory_status"] == "QUARANTINED":
        if not isinstance(record["failure_class"], str) or not record["failure_class"].strip():
            raise FactoryEvidenceIntakeError("QUARANTINED evidence requires failure_class")
    if record["record_hash"] != _record_hash(record):
        raise FactoryEvidenceIntakeError("Factory evidence record hash mismatch")

def write_evidence_record(bundle: dict[str, Any], output_root: str | Path) -> Path:
    record = build_evidence_record(bundle)
    root = Path(output_root)
    target = root / record["plugin_id"] / f"{record['source_bundle_hash']}.json"
    target.parent.mkdir(parents=True, exist_ok=True)

    serialized = json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != serialized:
            raise FactoryEvidenceIntakeError(
                "existing evidence path differs despite identical bundle hash"
            )
        return target

    target.write_text(serialized, encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(prog="cipi-factory-intake")
    parser.add_argument("bundle")
    parser.add_argument(
        "--output-root",
        default="research/factory_evidence",
        help="bounded CIPI Factory evidence root",
    )
    args = parser.parse_args()

    try:
        bundle = load_bundle(args.bundle)
        path = write_evidence_record(bundle, args.output_root)
        print(json.dumps({"status": "FACTORY_EVIDENCE_INTAKE_PASS", "path": str(path)}))
        return 0
    except (FactoryEvidenceIntakeError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FACTORY_EVIDENCE_INTAKE_ERROR", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
