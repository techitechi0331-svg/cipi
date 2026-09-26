from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from juce_factory.factory.contract import load_contract
from juce_factory.factory.generator import generate_project
from juce_factory.factory.reproducibility import (
    ReproducibilityComparisonError,
    _report_hash,
    compare_pass_bundles,
    validate_comparison_report,
)
from juce_factory.factory.result_bundle import _hash_payload, build_pass_bundle


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "golden_gain.contract.json"


class FactoryReproducibilityTests(unittest.TestCase):
    def _bundle(
        self,
        root: Path,
        artifact_digest: str,
        *,
        contract: dict | None = None,
        juce_version: str | None = None,
    ) -> dict:
        contract = contract or load_contract(EXAMPLE)
        out = generate_project(contract, root / "plugin")
        manifest_path = out / "factory_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if juce_version is not None:
            manifest["juce_version"] = juce_version
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        report = {
            "factory_status": "VALIDATION_PASS",
            "factory_owned_validation": "PASS",
            "pluginval": "PASS",
            "steinberg_validator": "PASS",
            "release_authority": False,
        }
        provenance = {
            "factory_status": "VALIDATION_PASS",
            "source_revision": "1" * 40,
            "validation_revision": "2" * 40,
            "validation_base_revision": "3" * 40,
            "juce_version": manifest["juce_version"],
            "platform": manifest["target_os"],
            "contract_semantic_sha256": manifest["contract_sha256"],
            "release_authority": False,
        }
        report_path = out / "validation_report.json"
        provenance_path = out / "provenance.json"
        hashes_path = out / "sha256.txt"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
        hashes_path.write_text(
            artifact_digest
            + "  passed/GoldenGain.vst3/Contents/x86_64-win/GoldenGain.vst3\n",
            encoding="ascii",
        )
        return build_pass_bundle(
            manifest_path,
            report_path,
            provenance_path,
            hashes_path,
        )


    def _downgrade_to_v1_0(self, bundle: dict) -> dict:
        legacy = copy.deepcopy(bundle)
        legacy["schema_version"] = "1.0"
        for key in (
            "dsp_module_id",
            "dsp_implementation_id",
            "dsp_certification_status",
            "dsp_validation_profile",
            "dsp_module_spec_sha256",
            "dsp_module_registry_sha256",
        ):
            legacy.pop(key, None)
        legacy["bundle_hash"] = _hash_payload(legacy)
        return legacy

    def test_identical_recorded_inputs_and_hashes_match(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "a" * 64)
            report = compare_pass_bundles(first, second)
            validate_comparison_report(report)
            self.assertEqual(report["classification"], "ARTIFACT_HASH_MATCH")
            self.assertTrue(report["same_contract"])
            self.assertTrue(report["same_generated_source"])
            self.assertTrue(report["artifact_hash_match"])
            self.assertFalse(report["automatic_gate_decision"])
            self.assertFalse(report["bit_reproducibility_confirmed"])

    def test_same_source_with_different_binary_hash_is_measured_not_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "b" * 64)
            report = compare_pass_bundles(first, second)
            self.assertEqual(report["classification"], "ARTIFACT_HASH_DIFF")
            self.assertTrue(report["same_generated_source"])
            self.assertFalse(report["artifact_hash_match"])
            self.assertFalse(report["automatic_gate_decision"])

    def test_different_generated_source_is_not_comparable(self):
        contract = load_contract(EXAMPLE)
        changed = copy.deepcopy(contract)
        changed["plugin"]["version"] = "0.1.1"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64, contract=contract)
            second = self._bundle(root / "b", "a" * 64, contract=changed)
            report = compare_pass_bundles(first, second)
            self.assertEqual(report["classification"], "NOT_COMPARABLE_SOURCE_DIFF")
            self.assertFalse(report["same_contract"])
            self.assertFalse(report["same_generated_source"])

    def test_recorded_context_difference_is_not_binary_repro_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "a" * 64, juce_version="9.0.3")
            report = compare_pass_bundles(first, second)
            self.assertEqual(
                report["classification"],
                "NOT_COMPARABLE_RECORDED_CONTEXT_DIFF",
            )
            self.assertTrue(report["same_generated_source"])
            self.assertFalse(report["same_recorded_factory_context"])




    def test_v1_0_and_v1_1_are_not_same_recorded_context(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            current = self._bundle(root / "a", "a" * 64)
            legacy = self._downgrade_to_v1_0(
                self._bundle(root / "b", "a" * 64)
            )
            report = compare_pass_bundles(current, legacy)
            self.assertEqual(
                report["classification"],
                "NOT_COMPARABLE_RECORDED_CONTEXT_DIFF",
            )
            self.assertTrue(report["same_contract"])
            self.assertTrue(report["same_generated_source"])
            self.assertFalse(report["same_recorded_factory_context"])

    def test_registry_hash_difference_is_recorded_context_difference(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "a" * 64)
            second["dsp_module_registry_sha256"] = "f" * 64
            second["bundle_hash"] = _hash_payload(second)

            report = compare_pass_bundles(first, second)
            self.assertEqual(
                report["classification"],
                "NOT_COMPARABLE_RECORDED_CONTEXT_DIFF",
            )
            self.assertFalse(report["same_recorded_factory_context"])

    def test_module_spec_hash_difference_is_recorded_context_difference(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "a" * 64)
            second["dsp_module_spec_sha256"] = "e" * 64
            second["bundle_hash"] = _hash_payload(second)

            report = compare_pass_bundles(first, second)
            self.assertEqual(
                report["classification"],
                "NOT_COMPARABLE_RECORDED_CONTEXT_DIFF",
            )
            self.assertFalse(report["same_recorded_factory_context"])

    def test_report_schema_required_fields_match_runtime_report(self):
        schema = json.loads(
            (ROOT / "schemas" / "factory_reproducibility_report.schema.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "a" * 64)
            report = compare_pass_bundles(first, second)
            self.assertEqual(set(schema["required"]), set(report))
            self.assertFalse(schema["properties"]["automatic_gate_decision"]["const"])
            self.assertFalse(schema["properties"]["bit_reproducibility_confirmed"]["const"])

    def test_semantically_inconsistent_report_is_rejected_even_with_fresh_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "a" * 64)
            report = compare_pass_bundles(first, second)
            report["artifact_hash_match"] = False
            report["report_hash"] = _report_hash(report)
            with self.assertRaises(ReproducibilityComparisonError):
                validate_comparison_report(report)

    def test_report_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._bundle(root / "a", "a" * 64)
            second = self._bundle(root / "b", "a" * 64)
            report = compare_pass_bundles(first, second)
            report["bit_reproducibility_confirmed"] = True
            with self.assertRaises(ReproducibilityComparisonError):
                validate_comparison_report(report)


if __name__ == "__main__":
    unittest.main()
