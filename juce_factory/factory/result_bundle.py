from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from .contract import canonical_json

RESULT_BUNDLE_VERSION = "1.0"
_BUNDLE_KIND = "JUCE_FACTORY_RESULT"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SHA_LINE = re.compile(r"^([0-9a-fA-F]{64})  (.+)$")


class ResultBundleError(ValueError):
    pass


def _load_object(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ResultBundleError(f"{path} must contain a JSON object")
    return value


def _require_false(data: dict[str, Any], key: str) -> None:
    if data.get(key) is not False:
        raise ResultBundleError(f"{key} must be false")


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ResultBundleError(f"{label} must be a lowercase SHA-256 hex digest")
    return value


def _require_git_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _GIT_SHA.fullmatch(value):
        raise ResultBundleError(f"{label} must be a lowercase 40-character Git SHA")
    return value


def _normalized_artifact_path(value: str) -> str:
    if not isinstance(value, str):
        raise ResultBundleError("artifact path must be a string")
    normalized = value.replace("\\", "/")
    if not normalized or normalized.startswith("/") or normalized.startswith("//"):
        raise ResultBundleError(f"unsafe artifact path: {value}")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ResultBundleError(f"unsafe artifact path: {value}")
    if re.fullmatch(r"[A-Za-z]:", parts[0]) or re.match(r"^[A-Za-z]:/", normalized):
        raise ResultBundleError(f"unsafe artifact path: {value}")
    path = PurePosixPath(normalized)
    if path.is_absolute():
        raise ResultBundleError(f"unsafe artifact path: {value}")
    return normalized


def read_sha256_manifest(path: str | Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, raw in enumerate(Path(path).read_text(encoding="ascii").splitlines(), start=1):
        if not raw.strip():
            continue
        match = _SHA_LINE.fullmatch(raw)
        if match is None:
            raise ResultBundleError(f"invalid SHA-256 manifest line {line_number}")
        digest = match.group(1).lower()
        artifact = _normalized_artifact_path(match.group(2))
        if artifact in result:
            raise ResultBundleError(f"duplicate artifact hash entry: {artifact}")
        result[artifact] = digest
    if not result:
        raise ResultBundleError("artifact SHA-256 manifest must not be empty")
    return dict(sorted(result.items()))


def _hash_payload(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("bundle_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_result_bundle(data: dict[str, Any]) -> None:
    required = {
        "schema_version", "bundle_kind", "factory_status", "plugin_id", "plugin_version",
        "contract_version", "contract_sha256", "generated_source_sha256",
        "factory_version", "source_revision", "validation_revision",
        "validation_base_revision", "dsp_source_revision", "juce_version",
        "platform", "formats", "validation_matrix", "validators", "artifact_hashes",
        "failure_class", "raw_audio_persisted", "automatic_final_decision",
        "promotion_authority", "product_release_authority", "cubase_confirmed",
        "listening_confirmed", "bundle_hash",
    }
    unknown = sorted(set(data) - required)
    missing = sorted(required - set(data))
    if missing:
        raise ResultBundleError(f"Factory Result Bundle missing fields: {missing}")
    if unknown:
        raise ResultBundleError(f"Factory Result Bundle contains unknown fields: {unknown}")
    if data["schema_version"] != RESULT_BUNDLE_VERSION:
        raise ResultBundleError("unsupported Factory Result Bundle schema_version")
    if data["bundle_kind"] != _BUNDLE_KIND:
        raise ResultBundleError("unexpected Factory Result Bundle kind")
    if data["factory_status"] not in {"VALIDATION_PASS", "QUARANTINED"}:
        raise ResultBundleError("unsupported factory_status")
    for key in ("plugin_id", "plugin_version", "factory_version",
                "dsp_source_revision", "juce_version", "platform"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ResultBundleError(f"{key} must be a non-empty string")
    if not isinstance(data["contract_version"], int) or isinstance(data["contract_version"], bool):
        raise ResultBundleError("contract_version must be an integer")
    _require_git_sha(data["source_revision"], "source_revision")
    _require_git_sha(data["validation_revision"], "validation_revision")
    _require_git_sha(data["validation_base_revision"], "validation_base_revision")
    _require_sha256(data["contract_sha256"], "contract_sha256")
    _require_sha256(data["generated_source_sha256"], "generated_source_sha256")
    _require_sha256(data["bundle_hash"], "bundle_hash")
    if not isinstance(data["formats"], list) or not data["formats"]:
        raise ResultBundleError("formats must be a non-empty array")
    if any(not isinstance(value, str) for value in data["formats"]):
        raise ResultBundleError("formats entries must be strings")
    if len(set(data["formats"])) != len(data["formats"]) or any(
        value != "VST3" for value in data["formats"]
    ):
        raise ResultBundleError("formats must contain only unique supported VST3 entries")
    if data["platform"] != "windows_x64":
        raise ResultBundleError("platform must be windows_x64")
    if not isinstance(data["validation_matrix"], dict):
        raise ResultBundleError("validation_matrix must be an object")
    if not isinstance(data["validators"], dict):
        raise ResultBundleError("validators must be an object")
    allowed_validator_states = {"PASS", "FAIL", "NOT_RUN", "UNKNOWN"}
    for key, value in data["validators"].items():
        if not isinstance(key, str) or not key.strip() or value not in allowed_validator_states:
            raise ResultBundleError("validators contains an invalid key or state")
    if not isinstance(data["artifact_hashes"], dict):
        raise ResultBundleError("artifact_hashes must be an object")
    for artifact, digest in data["artifact_hashes"].items():
        if _normalized_artifact_path(artifact) != artifact:
            raise ResultBundleError(f"artifact path must already be normalized: {artifact}")
        _require_sha256(digest, f"artifact_hashes[{artifact}]")
    if data["raw_audio_persisted"] is not False:
        raise ResultBundleError("raw_audio_persisted must be false")
    for key in (
        "automatic_final_decision", "promotion_authority", "product_release_authority",
        "cubase_confirmed", "listening_confirmed",
    ):
        _require_false(data, key)

    if data["factory_status"] == "VALIDATION_PASS":
        if data["failure_class"] is not None:
            raise ResultBundleError("VALIDATION_PASS must not carry failure_class")
        if not data["artifact_hashes"]:
            raise ResultBundleError("VALIDATION_PASS requires artifact hashes")
        mandatory = {"factory_owned_validation", "pluginval", "steinberg_validator"}
        if not mandatory.issubset(data["validators"]):
            raise ResultBundleError("VALIDATION_PASS is missing mandatory validator results")
        if any(data["validators"][key] != "PASS" for key in mandatory):
            raise ResultBundleError("VALIDATION_PASS requires all mandatory validators to PASS")
    else:
        if not isinstance(data["failure_class"], str) or not data["failure_class"].strip():
            raise ResultBundleError("QUARANTINED requires a non-empty failure_class")
        if data["artifact_hashes"]:
            raise ResultBundleError("QUARANTINED must not expose promoted artifact hashes")

    expected = _hash_payload(data)
    if data["bundle_hash"] != expected:
        raise ResultBundleError("Factory Result Bundle hash mismatch")


def build_pass_bundle(
    manifest_path: str | Path,
    validation_report_path: str | Path,
    provenance_path: str | Path,
    artifact_sha256_path: str | Path,
) -> dict[str, Any]:
    manifest = _load_object(manifest_path)
    report = _load_object(validation_report_path)
    provenance = _load_object(provenance_path)

    if manifest.get("status") != "GENERATED":
        raise ResultBundleError("factory manifest status must be GENERATED")
    _require_false(manifest, "release_authority")
    if report.get("factory_status") != "VALIDATION_PASS":
        raise ResultBundleError("validation report must be VALIDATION_PASS")
    _require_false(report, "release_authority")
    if provenance.get("factory_status") != "VALIDATION_PASS":
        raise ResultBundleError("provenance must be VALIDATION_PASS")
    _require_false(provenance, "release_authority")

    contract_hash = _require_sha256(manifest.get("contract_sha256"), "manifest.contract_sha256")
    if provenance.get("contract_semantic_sha256") != contract_hash:
        raise ResultBundleError("provenance contract hash does not match manifest")
    generated_hash = _require_sha256(
        manifest.get("generated_source_sha256"), "manifest.generated_source_sha256"
    )
    if provenance.get("juce_version") != manifest.get("juce_version"):
        raise ResultBundleError("JUCE version mismatch between manifest and provenance")
    if provenance.get("platform") != manifest.get("target_os"):
        raise ResultBundleError("platform mismatch between manifest and provenance")

    validators = {
        "factory_owned_validation": report.get("factory_owned_validation"),
        "pluginval": report.get("pluginval"),
        "steinberg_validator": report.get("steinberg_validator"),
    }
    if any(value != "PASS" for value in validators.values()):
        raise ResultBundleError("pass bundle requires every mandatory validator to PASS")

    bundle: dict[str, Any] = {
        "schema_version": RESULT_BUNDLE_VERSION,
        "bundle_kind": _BUNDLE_KIND,
        "factory_status": "VALIDATION_PASS",
        "plugin_id": manifest.get("plugin_id"),
        "plugin_version": manifest.get("plugin_version"),
        "contract_version": manifest.get("contract_version"),
        "contract_sha256": contract_hash,
        "generated_source_sha256": generated_hash,
        "factory_version": manifest.get("factory_version"),
        "source_revision": _require_git_sha(
            provenance.get("source_revision"),
            "provenance.source_revision",
        ),
        "validation_revision": _require_git_sha(
            provenance.get("validation_revision"),
            "provenance.validation_revision",
        ),
        "validation_base_revision": _require_git_sha(
            provenance.get("validation_base_revision"),
            "provenance.validation_base_revision",
        ),
        "dsp_source_revision": manifest.get("dsp_source_revision"),
        "juce_version": manifest.get("juce_version"),
        "platform": provenance.get("platform"),
        "formats": manifest.get("formats"),
        "validation_matrix": manifest.get("validation_matrix"),
        "validators": validators,
        "artifact_hashes": read_sha256_manifest(artifact_sha256_path),
        "failure_class": None,
        "raw_audio_persisted": False,
        "automatic_final_decision": False,
        "promotion_authority": False,
        "product_release_authority": False,
        "cubase_confirmed": False,
        "listening_confirmed": False,
    }
    bundle["bundle_hash"] = _hash_payload(bundle)
    validate_result_bundle(bundle)
    return bundle


def build_quarantine_bundle(
    manifest_path: str | Path,
    failure_path: str | Path,
) -> dict[str, Any]:
    manifest = _load_object(manifest_path)
    failure = _load_object(failure_path)
    _require_false(manifest, "release_authority")
    if failure.get("factory_status") != "QUARANTINED":
        raise ResultBundleError("failure record must be QUARANTINED")
    _require_false(failure, "release_authority")
    failure_class = failure.get("failure_class")
    if not isinstance(failure_class, str) or not failure_class.strip():
        raise ResultBundleError("failure record requires failure_class")

    bundle: dict[str, Any] = {
        "schema_version": RESULT_BUNDLE_VERSION,
        "bundle_kind": _BUNDLE_KIND,
        "factory_status": "QUARANTINED",
        "plugin_id": manifest.get("plugin_id"),
        "plugin_version": manifest.get("plugin_version"),
        "contract_version": manifest.get("contract_version"),
        "contract_sha256": _require_sha256(
            manifest.get("contract_sha256"), "manifest.contract_sha256"
        ),
        "generated_source_sha256": _require_sha256(
            manifest.get("generated_source_sha256"), "manifest.generated_source_sha256"
        ),
        "factory_version": manifest.get("factory_version"),
        "source_revision": _require_git_sha(
            failure.get("source_revision"),
            "failure.source_revision",
        ),
        "validation_revision": _require_git_sha(
            failure.get("validation_revision"),
            "failure.validation_revision",
        ),
        "validation_base_revision": _require_git_sha(
            failure.get("validation_base_revision"),
            "failure.validation_base_revision",
        ),
        "dsp_source_revision": manifest.get("dsp_source_revision"),
        "juce_version": manifest.get("juce_version"),
        "platform": manifest.get("target_os"),
        "formats": manifest.get("formats"),
        "validation_matrix": manifest.get("validation_matrix"),
        "validators": dict(failure.get("validators", {})),
        "artifact_hashes": {},
        "failure_class": failure_class,
        "raw_audio_persisted": False,
        "automatic_final_decision": False,
        "promotion_authority": False,
        "product_release_authority": False,
        "cubase_confirmed": False,
        "listening_confirmed": False,
    }
    bundle["bundle_hash"] = _hash_payload(bundle)
    validate_result_bundle(bundle)
    return bundle


def write_result_bundle(path: str | Path, bundle: dict[str, Any]) -> None:
    validate_result_bundle(bundle)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(bundle, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
