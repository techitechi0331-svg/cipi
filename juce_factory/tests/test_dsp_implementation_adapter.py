from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from juce_factory.factory.contract import load_contract
from juce_factory.factory.dsp_modules.implementation_adapter import (
    DspImplementationAdapterError,
    get_implementation_adapter,
    implementation_adapter_sha256,
    list_implementation_ids,
    require_implementation_adapter,
)
from juce_factory.factory.dsp_modules.registry import get_module_spec
from juce_factory.factory.generator import generate_project


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "golden_gain.contract.json"


class DspImplementationAdapterTests(unittest.TestCase):
    def test_golden_adapter_is_only_implemented_adapter(self):
        self.assertEqual(
            list_implementation_ids(),
            ("builtin.golden_gain_v1",),
        )
        adapter = get_implementation_adapter("builtin.golden_gain_v1")
        self.assertEqual(adapter.module_id, "golden_gain_v1")
        self.assertEqual(adapter.renderer_id, "renderer.golden_gain_v1")
        self.assertEqual(adapter.renderer_version, "1.0")
        self.assertEqual(adapter.validation_profile, "golden_gain_v1")
        self.assertFalse(adapter.product_release_authority)

    def test_unknown_implementation_is_rejected(self):
        with self.assertRaises(DspImplementationAdapterError):
            get_implementation_adapter("builtin.unknown_v1")

    def test_module_mismatch_is_rejected(self):
        spec = get_module_spec("golden_gain_v1")
        mismatched = replace(spec, module_id="other_module_v1")
        with self.assertRaises(DspImplementationAdapterError):
            require_implementation_adapter(mismatched)

    def test_validation_profile_mismatch_is_rejected(self):
        spec = get_module_spec("golden_gain_v1")
        mismatched = replace(spec, validation_profile="other_profile_v1")
        with self.assertRaises(DspImplementationAdapterError):
            require_implementation_adapter(mismatched)

    def test_adapter_hash_is_stable_sha256(self):
        first = implementation_adapter_sha256("builtin.golden_gain_v1")
        second = implementation_adapter_sha256("builtin.golden_gain_v1")
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")

    def test_generated_manifest_pins_renderer_and_adapter_hash(self):
        contract = load_contract(EXAMPLE)
        with tempfile.TemporaryDirectory() as td:
            out = generate_project(contract, Path(td) / "plugin")
            manifest = json.loads(
                (out / "factory_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["dsp_renderer_id"],
                "renderer.golden_gain_v1",
            )
            self.assertEqual(manifest["dsp_renderer_version"], "1.0")
            self.assertEqual(
                manifest["dsp_implementation_adapter_sha256"],
                implementation_adapter_sha256("builtin.golden_gain_v1"),
            )


if __name__ == "__main__":
    unittest.main()
