from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .registry import DspModuleSpec


class DspImplementationAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class DspImplementationAdapter:
    implementation_id: str
    module_id: str
    renderer_id: str
    renderer_version: str
    validation_profile: str
    product_release_authority: bool


_IMPLEMENTATIONS: dict[str, DspImplementationAdapter] = {
    "builtin.golden_gain_v1": DspImplementationAdapter(
        implementation_id="builtin.golden_gain_v1",
        module_id="golden_gain_v1",
        renderer_id="renderer.golden_gain_v1",
        renderer_version="1.0",
        validation_profile="golden_gain_v1",
        product_release_authority=False,
    ),
}


def _canonical_json(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def list_implementation_ids() -> tuple[str, ...]:
    return tuple(sorted(_IMPLEMENTATIONS))


def get_implementation_adapter(
    implementation_id: str,
) -> DspImplementationAdapter:
    try:
        return _IMPLEMENTATIONS[implementation_id]
    except KeyError as exc:
        raise DspImplementationAdapterError(
            f"Factory has no implementation adapter for {implementation_id}"
        ) from exc


def require_implementation_adapter(
    module_spec: DspModuleSpec,
) -> DspImplementationAdapter:
    adapter = get_implementation_adapter(module_spec.implementation_id)
    if adapter.module_id != module_spec.module_id:
        raise DspImplementationAdapterError(
            f"{module_spec.module_id}: implementation adapter module mismatch"
        )
    if adapter.validation_profile != module_spec.validation_profile:
        raise DspImplementationAdapterError(
            f"{module_spec.module_id}: implementation adapter validation-profile mismatch"
        )
    if adapter.product_release_authority is not False:
        raise DspImplementationAdapterError(
            f"{module_spec.module_id}: implementation adapter must not grant release authority"
        )
    return adapter


def implementation_adapter_sha256(implementation_id: str) -> str:
    adapter = get_implementation_adapter(implementation_id)
    payload = {
        "implementation_id": adapter.implementation_id,
        "module_id": adapter.module_id,
        "renderer_id": adapter.renderer_id,
        "renderer_version": adapter.renderer_version,
        "validation_profile": adapter.validation_profile,
        "product_release_authority": adapter.product_release_authority,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
