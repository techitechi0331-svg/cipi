from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from . import FACTORY_VERSION
from .contract import contract_sha256, validate_contract
from .dsp_modules.registry import (
    module_spec_sha256,
    registry_sha256,
    require_build_eligible_module,
)
from .dsp_modules.implementation_adapter import (
    implementation_adapter_sha256,
    require_implementation_adapter,
)
from .dsp_modules.golden_gain_renderer import render_golden_gain


def _cpp_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _content_tree_sha256(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(files[path].encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _target_name(plugin_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]", "", plugin_id)
    if not safe:
        raise ValueError("plugin id cannot produce an empty CMake target")
    if safe[0].isdigit():
        safe = "P" + safe
    return "JF" + safe


def _refuse_nonempty(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


def generate_project(contract: dict[str, Any], output_dir: str | Path) -> Path:
    validate_contract(contract)
    out = Path(output_dir)
    _refuse_nonempty(out)
    source = out / "Source"
    source.mkdir(parents=True, exist_ok=True)
    tests = out / "Tests"
    tests.mkdir(parents=True, exist_ok=True)

    plugin = contract["plugin"]
    validation = contract["validation"]
    module_spec = require_build_eligible_module(
        contract["dsp"]["template"],
        contract_version=contract["contract_version"],
    )
    implementation = require_implementation_adapter(module_spec)
    if implementation.renderer_id != "renderer.golden_gain_v1":
        raise ValueError(
            f"Factory generator has no renderer for {implementation.renderer_id}"
        )
    sample_rates = validation.get("sample_rates", [44100, 48000, 88200, 96000])
    block_sizes = validation.get("block_sizes", [32, 64, 128, 257, 512, 1024])
    target = _target_name(plugin["id"])

    cmake = f'''cmake_minimum_required(VERSION 3.24)
project({target} VERSION {plugin["version"]} LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(DEFINED JUCE_SOURCE_DIR AND EXISTS "${{JUCE_SOURCE_DIR}}/CMakeLists.txt")
    add_subdirectory("${{JUCE_SOURCE_DIR}}" JUCE)
elseif(EXISTS "${{CMAKE_SOURCE_DIR}}/JUCE/CMakeLists.txt")
    add_subdirectory(JUCE)
else()
    include(FetchContent)
    FetchContent_Declare(
        JUCE
        GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
        GIT_TAG 9.0.2
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(JUCE)
endif()

juce_add_plugin({target}
    COMPANY_NAME "{_cpp_string(plugin["vendor"])}"
    BUNDLE_ID "{plugin["bundle_id"]}"
    PLUGIN_MANUFACTURER_CODE {plugin["manufacturer_code"]}
    PLUGIN_CODE {plugin["plugin_code"]}
    FORMATS VST3
    PRODUCT_NAME "{_cpp_string(plugin["name"])}"
    COPY_PLUGIN_AFTER_BUILD FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
)

juce_generate_juce_header({target})

target_sources({target}
    PRIVATE
        Source/PluginProcessor.cpp
        Source/PluginProcessor.h
        Source/PluginEditor.cpp
        Source/PluginEditor.h
)

target_compile_definitions({target}
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries({target}
    PRIVATE
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
)
'''
    rendered = render_golden_gain(contract)
    processor_h = rendered.processor_h
    processor_cpp = rendered.processor_cpp
    editor_h = rendered.editor_h
    editor_cpp = rendered.editor_cpp
    validation_cpp = rendered.validation_cpp

    cmake += f'''

juce_add_console_app({target}FactoryValidation
    PRODUCT_NAME "{_cpp_string(plugin["name"])} Factory Validation"
)

juce_generate_juce_header({target}FactoryValidation)

target_sources({target}FactoryValidation
    PRIVATE
        Tests/FactoryValidation.cpp
        Source/PluginProcessor.cpp
        Source/PluginProcessor.h
)

target_compile_definitions({target}FactoryValidation
    PUBLIC
        JUCE_FACTORY_HEADLESS_TEST=1
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries({target}FactoryValidation
    PRIVATE
        juce::juce_audio_processors
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
)
'''

    generated_sources = {
        "CMakeLists.txt": cmake,
        "Source/PluginProcessor.h": processor_h,
        "Source/PluginProcessor.cpp": processor_cpp,
        "Source/PluginEditor.h": editor_h,
        "Source/PluginEditor.cpp": editor_cpp,
        "Tests/FactoryValidation.cpp": validation_cpp,
    }
    generated_source_sha256 = _content_tree_sha256(generated_sources)

    manifest = {
        "factory_version": FACTORY_VERSION,
        "contract_version": contract["contract_version"],
        "contract_sha256": contract_sha256(contract),
        "plugin_id": plugin["id"],
        "plugin_version": plugin["version"],
        "dsp_template": contract["dsp"]["template"],
        "dsp_implementation_id": module_spec.implementation_id,
        "dsp_renderer_id": implementation.renderer_id,
        "dsp_renderer_version": implementation.renderer_version,
        "dsp_implementation_adapter_sha256": implementation_adapter_sha256(
            implementation.implementation_id
        ),
        "dsp_certification_status": module_spec.certification_status,
        "dsp_validation_profile": module_spec.validation_profile,
        "dsp_module_spec_sha256": module_spec_sha256(module_spec.module_id),
        "dsp_module_registry_sha256": registry_sha256(),
        "dsp_source_revision": contract["dsp"]["source_revision"],
        "generated_source_sha256": generated_source_sha256,
        "juce_version": "9.0.2",
        "target_os": contract["target"]["os"],
        "formats": contract["target"]["formats"],
        "status": "GENERATED",
        "release_authority": False,
        "validation_matrix": {
            "sample_rates": sample_rates,
            "block_sizes": block_sizes,
            "state_restore": validation.get("state_restore", True),
            "automation": validation.get("automation", True),
            "silence": validation.get("silence", True),
            "nan_inf": validation.get("nan_inf", True),
            "official_vst3_validator": validation.get("official_vst3_validator", True),
            "latency": validation.get("latency", True),
            "mono_stereo_layouts": validation.get("mono_stereo_layouts", True),
            "denormal": validation.get("denormal", True),
            "bypass": validation.get("bypass", True),
        },
    }

    (out / "CMakeLists.txt").write_text(cmake, encoding="utf-8")
    (source / "PluginProcessor.h").write_text(processor_h, encoding="utf-8")
    (source / "PluginProcessor.cpp").write_text(processor_cpp, encoding="utf-8")
    (source / "PluginEditor.h").write_text(editor_h, encoding="utf-8")
    (source / "PluginEditor.cpp").write_text(editor_cpp, encoding="utf-8")
    (tests / "FactoryValidation.cpp").write_text(validation_cpp, encoding="utf-8")
    (out / "plugin_contract.json").write_text(
        json.dumps(contract, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "factory_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out
