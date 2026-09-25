from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class MelonAdapterError(ValueError):
    pass


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def load_result_bundle(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_result_bundle(data)
    return data


def validate_result_bundle(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise MelonAdapterError("MELON bundle must be an object")
    required = {
        "schema_version", "bridge_version", "source_system", "target_system",
        "contract_id", "candidate", "measurement", "knowledge_candidate",
        "negative_evidence_retained", "automatic_final_decision",
        "promotion_authority", "product_release_authority", "bundle_hash",
    }
    missing = sorted(required - set(data))
    if missing:
        raise MelonAdapterError(f"MELON bundle missing fields: {missing}")
    if data["source_system"] != "MELON" or data["target_system"] != "CIPI":
        raise MelonAdapterError("unexpected MELON bridge direction")
    if data["automatic_final_decision"] is not False:
        raise MelonAdapterError("MELON must not carry automatic final-decision authority")
    if data["promotion_authority"] is not False:
        raise MelonAdapterError("MELON must not carry promotion authority")
    if data["product_release_authority"] is not False:
        raise MelonAdapterError("MELON must not carry product release authority")
    if data["negative_evidence_retained"] is not True:
        raise MelonAdapterError("negative evidence must be retained")
    expected = str(data["bundle_hash"])
    payload = dict(data)
    payload.pop("bundle_hash", None)
    actual = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    if expected != actual:
        raise MelonAdapterError("MELON bundle_hash mismatch")


def candidate_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Return bounded metadata only.

    This adapter intentionally does not create a Plugin Contract. MELON is not a
    product/release authority; CIPI + Incubator must explicitly approve the DSP
    source before a Factory contract can exist.
    """
    validate_result_bundle(data)
    candidate = data["candidate"]
    if not isinstance(candidate, dict):
        raise MelonAdapterError("candidate must be an object")
    return {
        "source_system": "MELON",
        "bridge_version": data["bridge_version"],
        "contract_id": data["contract_id"],
        "candidate_id": candidate.get("candidate_id"),
        "family": candidate.get("family"),
        "species": candidate.get("species"),
        "benchmark_profile": candidate.get("benchmark_profile"),
        "factory_eligible": False,
        "required_gate": "CIPI_INCUBATOR_PRODUCT_APPROVAL",
    }
