from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from juce_factory.factory.contract import canonical_json
from juce_factory.factory.result_bundle import validate_result_bundle

EVIDENCE_SCHEMA_VERSION = "1.0"
_PLUGIN_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


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

    record: dict[str, Any] = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
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
    }
    record["record_hash"] = _record_hash(record)
    validate_evidence_record(record)
    return record


def validate_evidence_record(record: dict[str, Any]) -> None:
    required = {
        "schema_version", "evidence_id", "source_system", "source_bundle_hash",
        "plugin_id", "plugin_version", "factory_status", "evidence_type", "scope",
        "claim", "contract_sha256", "generated_source_sha256", "source_revision",
        "validation_revision", "validation_base_revision", "dsp_source_revision",
        "failure_class", "raw_audio_persisted",
        "automatic_final_decision", "promotion_requested", "promotion_authority",
        "product_release_authority", "cubase_confirmed", "listening_confirmed",
        "record_hash",
    }
    missing = sorted(required - set(record))
    unknown = sorted(set(record) - required)
    if missing:
        raise FactoryEvidenceIntakeError(f"Factory evidence record missing fields: {missing}")
    if unknown:
        raise FactoryEvidenceIntakeError(f"Factory evidence record contains unknown fields: {unknown}")
    if record["schema_version"] != EVIDENCE_SCHEMA_VERSION:
        raise FactoryEvidenceIntakeError("unsupported Factory evidence schema_version")
    if record["source_system"] != "JUCE_FACTORY":
        raise FactoryEvidenceIntakeError("unexpected Factory evidence source_system")
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
