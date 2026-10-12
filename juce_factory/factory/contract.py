from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .dsp_modules.registry import (
    DspModuleRegistryError,
    list_module_ids,
    require_build_eligible_module,
)

CONTRACT_VERSION = 1
SUPPORTED_FORMATS = {"VST3"}
SUPPORTED_LAYOUTS = {"mono", "stereo"}
SUPPORTED_DSP_TEMPLATES = set(list_module_ids())

_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_CODE4 = re.compile(r"^[A-Za-z0-9]{4}$")
_BUNDLE = re.compile(r"^[A-Za-z][A-Za-z0-9.-]+$")
_SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


class ContractError(ValueError):
    pass


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def contract_sha256(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def load_contract(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractError("plugin contract must be a JSON object")
    validate_contract(data)
    return data


def _require_object(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ContractError(f"{key} must be an object")
    return value


def _require_list(parent: dict[str, Any], key: str) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        raise ContractError(f"{key} must be an array")
    return value


def validate_contract(data: dict[str, Any]) -> None:
    required = {"contract_version", "plugin", "target", "audio", "parameters", "dsp", "ui", "validation"}
    missing = sorted(required - set(data))
    if missing:
        raise ContractError(f"missing top-level fields: {missing}")
    if data["contract_version"] != CONTRACT_VERSION:
        raise ContractError(f"unsupported contract_version: {data['contract_version']}")

    plugin = _require_object(data, "plugin")
    for key in ("id", "name", "vendor", "version", "bundle_id", "manufacturer_code", "plugin_code"):
        if not isinstance(plugin.get(key), str) or not plugin[key].strip():
            raise ContractError(f"plugin.{key} must be a non-empty string")
    if not _ID.fullmatch(plugin["id"]):
        raise ContractError("plugin.id must match ^[A-Za-z][A-Za-z0-9_]*$")
    if not _SEMVER.fullmatch(plugin["version"]):
        raise ContractError("plugin.version must be semantic version x.y.z")
    if not _BUNDLE.fullmatch(plugin["bundle_id"]):
        raise ContractError("plugin.bundle_id contains unsupported characters")
    if not _CODE4.fullmatch(plugin["manufacturer_code"]):
        raise ContractError("plugin.manufacturer_code must be exactly four ASCII letters/digits")
    if not _CODE4.fullmatch(plugin["plugin_code"]):
        raise ContractError("plugin.plugin_code must be exactly four ASCII letters/digits")

    target = _require_object(data, "target")
    formats = set(_require_list(target, "formats"))
    if not formats or not formats.issubset(SUPPORTED_FORMATS):
        raise ContractError(f"target.formats must be a non-empty subset of {sorted(SUPPORTED_FORMATS)}")
    if target.get("os") != "windows_x64":
        raise ContractError("Phase 1 supports target.os=windows_x64 only")

    audio = _require_object(data, "audio")
    layouts = set(_require_list(audio, "layouts"))
    if not layouts or not layouts.issubset(SUPPORTED_LAYOUTS):
        raise ContractError(f"audio.layouts must be a non-empty subset of {sorted(SUPPORTED_LAYOUTS)}")

    parameters = _require_list(data, "parameters")
    if not parameters:
        raise ContractError("parameters must be non-empty")
    ids: set[str] = set()
    for index, parameter in enumerate(parameters):
        if not isinstance(parameter, dict):
            raise ContractError(f"parameters[{index}] must be an object")
        pid = parameter.get("id")
        if not isinstance(pid, str) or not _ID.fullmatch(pid):
            raise ContractError(f"parameters[{index}].id is invalid")
        if pid in ids:
            raise ContractError(f"duplicate parameter id: {pid}")
        ids.add(pid)
        if parameter.get("type") != "float":
            raise ContractError("Phase 1 generator supports float parameters only")
        for key in ("min", "max", "default"):
            if not isinstance(parameter.get(key), (int, float)) or isinstance(parameter.get(key), bool):
                raise ContractError(f"parameter {pid}.{key} must be numeric")
        lo, hi, default = float(parameter["min"]), float(parameter["max"]), float(parameter["default"])
        if not lo < hi:
            raise ContractError(f"parameter {pid}: min must be < max")
        if not lo <= default <= hi:
            raise ContractError(f"parameter {pid}: default must be within min/max")

    dsp = _require_object(data, "dsp")
    template = dsp.get("template")
    if not isinstance(template, str):
        raise ContractError("dsp.template must be a string")
    try:
        module_spec = require_build_eligible_module(
            template,
            contract_version=data["contract_version"],
        )
    except DspModuleRegistryError as exc:
        raise ContractError(f"unsupported dsp.template: {template}: {exc}") from exc

    required_parameter_ids = set(module_spec.required_parameter_ids)
    if ids != required_parameter_ids:
        raise ContractError(
            f"{template} requires exactly parameters {sorted(required_parameter_ids)}"
        )
    if not layouts.issubset(set(module_spec.supported_layouts)):
        raise ContractError(
            f"{template} does not support requested layouts {sorted(layouts)}"
        )
    if module_spec.source_revision_required:
        if not isinstance(dsp.get("source_revision"), str) or not dsp["source_revision"].strip():
            raise ContractError(
                f"{template}: dsp.source_revision must be a non-empty immutable identifier"
            )

    ui = _require_object(data, "ui")
    for key in ("width", "height"):
        value = ui.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 200 or value > 4000:
            raise ContractError(f"ui.{key} must be an integer in [200, 4000]")
    if not isinstance(ui.get("show_version"), bool):
        raise ContractError("ui.show_version must be boolean")

    validation = _require_object(data, "validation")
    required_validation_flags = (
        "pluginval", "state_restore", "automation", "silence", "nan_inf",
        "official_vst3_validator", "latency", "mono_stereo_layouts", "denormal", "bypass",
    )
    for key in required_validation_flags:
        if key in validation and not isinstance(validation.get(key), bool):
            raise ContractError(f"validation.{key} must be boolean")
    for key in ("pluginval", "state_restore", "automation", "silence", "nan_inf"):
        if not isinstance(validation.get(key), bool):
            raise ContractError(f"validation.{key} must be boolean")

    if validation["pluginval"] is not True:
        raise ContractError("validation.pluginval is a mandatory VST3 Factory gate and cannot be disabled")
    if validation["nan_inf"] is not True:
        raise ContractError("validation.nan_inf is a mandatory Factory safety gate and cannot be disabled")
    if validation.get("official_vst3_validator", True) is not True:
        raise ContractError(
            "validation.official_vst3_validator is a mandatory VST3 Factory gate and cannot be disabled"
        )

    sample_rates = validation.get("sample_rates", [44100, 48000, 88200, 96000])
    if not isinstance(sample_rates, list) or not sample_rates:
        raise ContractError("validation.sample_rates must be a non-empty array")
    if len(set(sample_rates)) != len(sample_rates):
        raise ContractError("validation.sample_rates must not contain duplicates")
    for rate in sample_rates:
        if not isinstance(rate, (int, float)) or isinstance(rate, bool) or not 8000 <= float(rate) <= 384000:
            raise ContractError("validation.sample_rates entries must be numeric values in [8000, 384000]")

    block_sizes = validation.get("block_sizes", [32, 64, 128, 257, 512, 1024])
    if not isinstance(block_sizes, list) or not block_sizes:
        raise ContractError("validation.block_sizes must be a non-empty array")
    if len(set(block_sizes)) != len(block_sizes):
        raise ContractError("validation.block_sizes must not contain duplicates")
    for size in block_sizes:
        if not isinstance(size, int) or isinstance(size, bool) or not 1 <= size <= 8192:
            raise ContractError("validation.block_sizes entries must be integers in [1, 8192]")
