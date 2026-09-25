from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from . import FACTORY_VERSION
from .contract import ContractError, load_contract
from .generator import generate_project


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
        if args.command == "self-test":
            contract = load_contract(_example_contract_path())
            with tempfile.TemporaryDirectory(prefix="juce-factory-") as td:
                out = generate_project(contract, Path(td) / "GoldenGain")
                expected = {
                    out / "CMakeLists.txt",
                    out / "factory_manifest.json",
                    out / "plugin_contract.json",
                    out / "Source" / "GoldenGainDSP.h",
                    out / "Tests" / "DspTests.cpp",
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
    except (ContractError, FileExistsError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "FACTORY_ERROR", "error": str(exc)}))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
