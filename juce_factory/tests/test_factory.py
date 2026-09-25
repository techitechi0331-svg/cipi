from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from juce_factory.factory.adapters.melon import MelonAdapterError, validate_result_bundle
from juce_factory.factory.contract import ContractError, contract_sha256, load_contract, validate_contract
from juce_factory.factory.generator import generate_project


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "golden_gain.contract.json"


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_is_valid(self):
        validate_contract(self.contract)

    def test_duplicate_parameter_is_rejected(self):
        bad = copy.deepcopy(self.contract)
        bad["parameters"].append(copy.deepcopy(bad["parameters"][0]))
        with self.assertRaises(ContractError):
            validate_contract(bad)

    def test_out_of_range_default_is_rejected(self):
        bad = copy.deepcopy(self.contract)
        bad["parameters"][0]["default"] = 1000.0
        with self.assertRaises(ContractError):
            validate_contract(bad)

    def test_optional_validation_gate_must_be_boolean(self):
        bad = copy.deepcopy(self.contract)
        bad["validation"]["official_vst3_validator"] = "yes"
        with self.assertRaises(ContractError):
            validate_contract(bad)

    def test_contract_hash_is_stable(self):
        a = contract_sha256(self.contract)
        b = contract_sha256(json.loads(json.dumps(self.contract, sort_keys=True)))
        self.assertEqual(a, b)

    def test_generate_refuses_overwrite(self):
        contract = load_contract(EXAMPLE)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "plugin"
            generate_project(contract, out)
            with self.assertRaises(FileExistsError):
                generate_project(contract, out)

    def test_golden_project_files_exist(self):
        contract = load_contract(EXAMPLE)
        with tempfile.TemporaryDirectory() as td:
            out = generate_project(contract, Path(td) / "plugin")
            self.assertTrue((out / "CMakeLists.txt").exists())
            self.assertTrue((out / "factory_manifest.json").exists())
            self.assertTrue((out / "Source" / "PluginProcessor.cpp").exists())
            self.assertTrue((out / "Source" / "GoldenGainDSP.h").exists())
            self.assertTrue((out / "Tests" / "DspTests.cpp").exists())
            cmake = (out / "CMakeLists.txt").read_text(encoding="utf-8")
            self.assertIn("FactoryTests", cmake)
            self.assertIn("add_test", cmake)
            processor = (out / "Source" / "PluginProcessor.cpp").read_text(encoding="utf-8")
            self.assertIn("NormalisableRange<float>(-24.0f, 24.0f, 0.01f)", processor)
            self.assertIn("\n        0.0f,\n", processor)
            manifest = json.loads((out / "factory_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["juce_version"], "9.0.2")
            self.assertFalse(manifest["release_authority"])


class MelonBoundaryTests(unittest.TestCase):
    def test_release_authority_is_rejected_before_hash(self):
        bundle = {
            "schema_version": "1.0",
            "bridge_version": "melon-cipi-bridge/0.1",
            "source_system": "MELON",
            "target_system": "CIPI",
            "contract_id": "TEST",
            "candidate": {},
            "measurement": {},
            "knowledge_candidate": {},
            "negative_evidence_retained": True,
            "automatic_final_decision": False,
            "promotion_authority": False,
            "product_release_authority": True,
            "bundle_hash": "invalid"
        }
        with self.assertRaises(MelonAdapterError):
            validate_result_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
