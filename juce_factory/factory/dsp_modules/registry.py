from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

_REGISTRY_PATH = Path(__file__).with_name("registry.json")
_MODULE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_IMPLEMENTATION_ID = re.compile(r"^[a-z][a-z0-9_.]*$")
_PARAMETER_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_ALLOWED_LAYOUTS = {"mono", "stereo"}


class DspModuleRegistryError(ValueError):
    pass


@dataclass(frozen=True)
class DspModuleSpec:
    module_id: str
    implementation_id: str
    certification_status: str
    factory_build_eligible: bool
    contract_versions: tuple[int, ...]
    required_parameter_ids: tuple[str, ...]
    supported_layouts: tuple[str, ...]
    validation_profile: str
    source_revision_required: bool
    product_release_authority: bool


def _canonical_json(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _load_registry_raw() -> dict[str, Any]:
    value = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DspModuleRegistryError("DSP Module Registry root must be an object")
    return value


def _parse_spec(value: Any) -> DspModuleSpec:
    if not isinstance(value, dict):
        raise DspModuleRegistryError("DSP module entry must be an object")
    required = {
        "module_id",
        "implementation_id",
        "certification_status",
        "factory_build_eligible",
        "contract_versions",
        "required_parameter_ids",
        "supported_layouts",
        "validation_profile",
        "source_revision_required",
        "product_release_authority",
    }
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required)
    if missing:
        raise DspModuleRegistryError(f"DSP module entry missing fields: {missing}")
    if unknown:
        raise DspModuleRegistryError(f"DSP module entry contains unknown fields: {unknown}")

    module_id = value["module_id"]
    implementation_id = value["implementation_id"]
    if not isinstance(module_id, str) or not _MODULE_ID.fullmatch(module_id):
        raise DspModuleRegistryError("module_id is invalid")
    if not isinstance(implementation_id, str) or not _IMPLEMENTATION_ID.fullmatch(
        implementation_id
    ):
        raise DspModuleRegistryError("implementation_id is invalid")
    if value["certification_status"] != "FACTORY_CERTIFIED":
        raise DspModuleRegistryError(
            f"{module_id}: certification_status must be FACTORY_CERTIFIED"
        )
    if not isinstance(value["factory_build_eligible"], bool):
        raise DspModuleRegistryError(f"{module_id}: factory_build_eligible must be boolean")
    if not isinstance(value["source_revision_required"], bool):
        raise DspModuleRegistryError(f"{module_id}: source_revision_required must be boolean")
    if value["product_release_authority"] is not False:
        raise DspModuleRegistryError(
            f"{module_id}: product_release_authority must remain false"
        )

    versions = value["contract_versions"]
    if (
        not isinstance(versions, list)
        or not versions
        or any(
            not isinstance(version, int)
            or isinstance(version, bool)
            or version < 1
            for version in versions
        )
        or len(set(versions)) != len(versions)
    ):
        raise DspModuleRegistryError(
            f"{module_id}: contract_versions must be unique positive integers"
        )

    parameters = value["required_parameter_ids"]
    if (
        not isinstance(parameters, list)
        or not parameters
        or any(
            not isinstance(parameter, str)
            or not _PARAMETER_ID.fullmatch(parameter)
            for parameter in parameters
        )
        or len(set(parameters)) != len(parameters)
    ):
        raise DspModuleRegistryError(
            f"{module_id}: required_parameter_ids are invalid or duplicated"
        )

    layouts = value["supported_layouts"]
    if (
        not isinstance(layouts, list)
        or not layouts
        or any(layout not in _ALLOWED_LAYOUTS for layout in layouts)
        or len(set(layouts)) != len(layouts)
    ):
        raise DspModuleRegistryError(
            f"{module_id}: supported_layouts are invalid or duplicated"
        )

    profile = value["validation_profile"]
    if not isinstance(profile, str) or not _MODULE_ID.fullmatch(profile):
        raise DspModuleRegistryError(f"{module_id}: validation_profile is invalid")

    return DspModuleSpec(
        module_id=module_id,
        implementation_id=implementation_id,
        certification_status=value["certification_status"],
        factory_build_eligible=value["factory_build_eligible"],
        contract_versions=tuple(versions),
        required_parameter_ids=tuple(parameters),
        supported_layouts=tuple(layouts),
        validation_profile=profile,
        source_revision_required=value["source_revision_required"],
        product_release_authority=value["product_release_authority"],
    )


@lru_cache(maxsize=1)
def load_registry() -> tuple[DspModuleSpec, ...]:
    raw = _load_registry_raw()
    required = {"schema_version", "modules"}
    missing = sorted(required - set(raw))
    unknown = sorted(set(raw) - required)
    if missing:
        raise DspModuleRegistryError(f"DSP Module Registry missing fields: {missing}")
    if unknown:
        raise DspModuleRegistryError(
            f"DSP Module Registry contains unknown fields: {unknown}"
        )
    if raw["schema_version"] != "1.0":
        raise DspModuleRegistryError("unsupported DSP Module Registry schema_version")
    if not isinstance(raw["modules"], list) or not raw["modules"]:
        raise DspModuleRegistryError("DSP Module Registry modules must be non-empty")

    specs = tuple(_parse_spec(value) for value in raw["modules"])
    module_ids = [spec.module_id for spec in specs]
    implementation_ids = [spec.implementation_id for spec in specs]
    if len(set(module_ids)) != len(module_ids):
        raise DspModuleRegistryError("DSP Module Registry contains duplicate module_id")
    if len(set(implementation_ids)) != len(implementation_ids):
        raise DspModuleRegistryError(
            "DSP Module Registry contains duplicate implementation_id"
        )
    return specs


def list_module_ids(*, build_eligible_only: bool = True) -> tuple[str, ...]:
    specs = load_registry()
    if build_eligible_only:
        specs = tuple(spec for spec in specs if spec.factory_build_eligible)
    return tuple(sorted(spec.module_id for spec in specs))


def get_module_spec(module_id: str) -> DspModuleSpec:
    for spec in load_registry():
        if spec.module_id == module_id:
            return spec
    raise DspModuleRegistryError(f"unregistered DSP module: {module_id}")


def require_build_eligible_module(module_id: str, *, contract_version: int) -> DspModuleSpec:
    spec = get_module_spec(module_id)
    if spec.certification_status != "FACTORY_CERTIFIED":
        raise DspModuleRegistryError(f"{module_id}: DSP module is not Factory certified")
    if not spec.factory_build_eligible:
        raise DspModuleRegistryError(f"{module_id}: DSP module is not build eligible")
    if contract_version not in spec.contract_versions:
        raise DspModuleRegistryError(
            f"{module_id}: unsupported Plugin Contract version {contract_version}"
        )
    if spec.product_release_authority is not False:
        raise DspModuleRegistryError(
            f"{module_id}: DSP module registry must not grant release authority"
        )
    return spec


def registry_sha256() -> str:
    raw = _load_registry_raw()
    return hashlib.sha256(_canonical_json(raw).encode("utf-8")).hexdigest()


def module_spec_sha256(module_id: str) -> str:
    spec = get_module_spec(module_id)
    payload = {
        "module_id": spec.module_id,
        "implementation_id": spec.implementation_id,
        "certification_status": spec.certification_status,
        "factory_build_eligible": spec.factory_build_eligible,
        "contract_versions": list(spec.contract_versions),
        "required_parameter_ids": list(spec.required_parameter_ids),
        "supported_layouts": list(spec.supported_layouts),
        "validation_profile": spec.validation_profile,
        "source_revision_required": spec.source_revision_required,
        "product_release_authority": spec.product_release_authority,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
