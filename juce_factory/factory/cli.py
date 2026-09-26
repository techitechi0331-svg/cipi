from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from . import FACTORY_VERSION
from .contract import ContractError, load_contract
from .generator import generate_project
from .dsp_modules.registry import (
    list_module_ids,
    get_module_spec,
    registry_sha256,
)
from .result_bundle import (
    ResultBundleError,
    build_pass_bundle,
    build_quarantine_bundle,
    validate_result_bundle,
    write_result_bundle,
)


def _example_contract_path() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "golden_gain.contract.json"


def main() -> int:
    parser = argparse.ArgumentParser(prog="juce-factory")
    parser.add_argument("--version", action="version", version=FACTORY_VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a Plugin Contract")
    validate.add_argument("contract")

    generate = sub.add_parser("generate", help="generate a JUCE project from a Plugin Contract")
    generate.add_argument("contract")
    generate.add_argument("--output", required=True)

    sub.add_parser("self-test", help="validate and generate the Golden Plugin in a temporary directory")
    sub.add_parser("modules", help="list certified Factory DSP modules")

    validate_result = sub.add_parser("validate-result", help="validate a Factory Result Bundle")
    validate_result.add_argument("bundle")

    bundle_pass = sub.add_parser("bundle-pass", help="write a VALIDATION_PASS Factory Result Bundle")
    bundle_pass.add_argument("--manifest", required=True)
    bundle_pass.add_argument("--validation-report", required=True)
    bundle_pass.add_argument("--provenance", required=True)
    bundle_pass.add_argument("--sha256", required=True)
    bundle_pass.add_argument("--output", required=True)

    bundle_quarantine = sub.add_parser(
        "bundle-quarantine",
        help="write a QUARANTINED Factory Result Bundle",
    )
    bundle_quarantine.add_argument("--manifest", required=True)
    bundle_quarantine.add_argument("--failure", required=True)
    bundle_quarantine.add_argument("--output", required=True)

    args = parser.parse_args()
    try:
        if args.command == "validate":
            contract = load_contract(args.contract)
            print(json.dumps({"status": "CONTRACT_VALID", "plugin_id": contract["plugin"]["id"]}))
            return 0
        if args.command == "generate":
            contract = load_contract(args.contract)
            out = generate_project(contract, args.output)
            print(json.dumps({"status": "GENERATED", "output": str(out)}))
            return 0
        if args.command == "modules":
            modules = []
            for module_id in list_module_ids():
                spec = get_module_spec(module_id)
                modules.append({
                    "module_id": spec.module_id,
                    "implementation_id": spec.implementation_id,
                    "certification_status": spec.certification_status,
                    "factory_build_eligible": spec.factory_build_eligible,
                    "contract_versions": list(spec.contract_versions),
                    "required_parameter_ids": list(spec.required_parameter_ids),
                    "supported_layouts": list(spec.supported_layouts),
                    "validation_profile": spec.validation_profile,
                    "product_release_authority": spec.product_release_authority,
                })
            print(json.dumps({
                "status": "DSP_MODULE_REGISTRY_VALID",
                "registry_sha256": registry_sha256(),
                "modules": modules,
            }))
            return 0
        if args.command == "validate-result":
            bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8-sig"))
            if not isinstance(bundle, dict):
                raise ResultBundleError("Factory Result Bundle must be a JSON object")
            validate_result_bundle(bundle)
            print(json.dumps({"status": "FACTORY_RESULT_VALID", "bundle_hash": bundle["bundle_hash"]}))
            return 0
        if args.command == "bundle-pass":
            bundle = build_pass_bundle(
                args.manifest,
                args.validation_report,
                args.provenance,
                args.sha256,
            )
            write_result_bundle(args.output, bundle)
            print(json.dumps({"status": "FACTORY_RESULT_WRITTEN", "bundle_hash": bundle["bundle_hash"]}))
            return 0
        if args.command == "bundle-quarantine":
            bundle = build_quarantine_bundle(args.manifest, args.failure)
            write_result_bundle(args.output, bundle)
            print(json.dumps({"status": "FACTORY_RESULT_WRITTEN", "bundle_hash": bundle["bundle_hash"]}))
            return 0
        if args.command == "self-test":
            contract = load_contract(_example_contract_path())
            with tempfile.TemporaryDirectory(prefix="juce-factory-") as td:
                out = generate_project(contract, Path(td) / "GoldenGain")
                expected = {
                    out / "CMakeLists.txt",
                    out / "factory_manifest.json",
                    out / "plugin_contract.json",
                    out / "Source" / "PluginProcessor.cpp",
                    out / "Source" / "PluginProcessor.h",
                    out / "Source" / "PluginEditor.cpp",
                    out / "Source" / "PluginEditor.h",
                }
                missing = sorted(str(p) for p in expected if not p.exists())
                if missing:
                    raise RuntimeError(f"self-test generated files missing: {missing}")
            print(json.dumps({"status": "SELF_TEST_PASS", "factory_version": FACTORY_VERSION}))
            return 0
    except (ContractError, ResultBundleError, FileExistsError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "FACTORY_ERROR", "error": str(exc)}))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
