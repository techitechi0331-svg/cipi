from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from juce_factory.factory.contract import (
    ContractError,
    SUPPORTED_DSP_TEMPLATES,
    load_contract,
    validate_contract,
)
from juce_factory.factory.dsp_modules.registry import (
    DspModuleRegistryError,
    DspModuleSpec,
    _parse_spec,
    get_module_spec,
    list_module_ids,
    module_spec_sha256,
    registry_sha256,
    require_build_eligible_module,
)
from juce_factory.factory.generator import generate_project


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "golden_gain.contract.json"
REGISTRY = ROOT / "factory" / "dsp_modules" / "registry.json"


class DspModuleRegistryTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract(EXAMPLE)

    def test_registry_has_one_certified_golden_module(self):
        self.assertEqual(list_module_ids(), ("golden_gain_v1",))
        spec = get_module_spec("golden_gain_v1")
        self.assertEqual(spec.implementation_id, "builtin.golden_gain_v1")
        self.assertEqual(spec.certification_status, "FACTORY_CERTIFIED")
        self.assertTrue(spec.factory_build_eligible)
        self.assertEqual(spec.required_parameter_ids, ("gain_db",))
        self.assertEqual(spec.supported_layouts, ("mono", "stereo"))
        self.assertFalse(spec.product_release_authority)

    def test_contract_supported_templates_are_registry_driven(self):
        self.assertEqual(SUPPORTED_DSP_TEMPLATES, set(list_module_ids()))

    def test_plugin_contract_schema_template_enum_matches_registry(self):
        schema = json.loads(
            (ROOT / "schemas" / "plugin_contract.schema.json").read_text(
                encoding="utf-8"
            )
        )
        enum = schema["properties"]["dsp"]["properties"]["template"]["enum"]
        self.assertEqual(set(enum), set(list_module_ids()))

    def test_registry_schema_module_fields_match_canonical_registry(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        schema = json.loads(
            (ROOT / "schemas" / "dsp_module_registry.schema.json").read_text(
                encoding="utf-8"
            )
        )
        required = set(schema["properties"]["modules"]["items"]["required"])
        self.assertEqual(required, set(registry["modules"][0]))

    def test_registry_and_module_hashes_are_stable_sha256(self):
        self.assertRegex(registry_sha256(), r"^[0-9a-f]{64}$")
        self.assertRegex(module_spec_sha256("golden_gain_v1"), r"^[0-9a-f]{64}$")
        self.assertEqual(registry_sha256(), registry_sha256())
        self.assertEqual(
            module_spec_sha256("golden_gain_v1"),
            module_spec_sha256("golden_gain_v1"),
        )

    def test_unregistered_module_is_rejected_by_contract(self):
        bad = copy.deepcopy(self.contract)
        bad["dsp"]["template"] = "mystery_module_v1"
        with self.assertRaises(ContractError):
            validate_contract(bad)

    def test_registered_module_requires_exact_parameter_ids(self):
        bad = copy.deepcopy(self.contract)
        bad["parameters"][0]["id"] = "wrong_gain"
        with self.assertRaises(ContractError):
            validate_contract(bad)

    def test_registered_module_requires_source_revision(self):
        bad = copy.deepcopy(self.contract)
        bad["dsp"]["source_revision"] = ""
        with self.assertRaises(ContractError):
            validate_contract(bad)

    def test_registry_entry_cannot_grant_release_authority(self):
        raw = {
            "module_id": "unsafe_v1",
            "implementation_id": "builtin.unsafe_v1",
            "certification_status": "FACTORY_CERTIFIED",
            "factory_build_eligible": True,
            "contract_versions": [1],
            "required_parameter_ids": ["gain_db"],
            "supported_layouts": ["mono", "stereo"],
            "validation_profile": "unsafe_v1",
            "source_revision_required": True,
            "product_release_authority": True,
        }
        with self.assertRaises(DspModuleRegistryError):
            _parse_spec(raw)

    def test_build_eligible_gate_rejects_registered_but_disabled_module(self):
        fake = DspModuleSpec(
            module_id="disabled_v1",
            implementation_id="builtin.disabled_v1",
            certification_status="FACTORY_CERTIFIED",
            factory_build_eligible=False,
            contract_versions=(1,),
            required_parameter_ids=("gain_db",),
            supported_layouts=("mono", "stereo"),
            validation_profile="disabled_v1",
            source_revision_required=True,
            product_release_authority=False,
        )
        with patch(
            "juce_factory.factory.dsp_modules.registry.get_module_spec",
            return_value=fake,
        ):
            with self.assertRaises(DspModuleRegistryError):
                require_build_eligible_module("disabled_v1", contract_version=1)

    def test_generator_refuses_registered_module_without_implementation(self):
        fake = SimpleNamespace(
            module_id="golden_gain_v1",
            implementation_id="builtin.not_implemented_v1",
            certification_status="FACTORY_CERTIFIED",
            validation_profile="golden_gain_v1",
        )
        with tempfile.TemporaryDirectory() as td, patch(
            "juce_factory.factory.generator.require_build_eligible_module",
            return_value=fake,
        ):
            with self.assertRaises(ValueError):
                generate_project(self.contract, Path(td) / "plugin")

    def test_generated_manifest_pins_module_registry_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            out = generate_project(self.contract, Path(td) / "plugin")
            manifest = json.loads(
                (out / "factory_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["dsp_implementation_id"],
                "builtin.golden_gain_v1",
            )
            self.assertEqual(
                manifest["dsp_certification_status"],
                "FACTORY_CERTIFIED",
            )
            self.assertEqual(
                manifest["dsp_validation_profile"],
                "golden_gain_v1",
            )
            self.assertEqual(
                manifest["dsp_module_registry_sha256"],
                registry_sha256(),
            )
            self.assertEqual(
                manifest["dsp_module_spec_sha256"],
                module_spec_sha256("golden_gain_v1"),
            )


if __name__ == "__main__":
    unittest.main()
