from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from automation.factory.intake import (
    FactoryEvidenceIntakeError,
    build_evidence_record,
    validate_evidence_record,
    write_evidence_record,
)
from juce_factory.factory.contract import load_contract
from juce_factory.factory.generator import generate_project
from juce_factory.factory.result_bundle import (
    ResultBundleError,
    _hash_payload,
    build_pass_bundle,
    build_quarantine_bundle,
    validate_result_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "golden_gain.contract.json"


class FactoryResultBundleTests(unittest.TestCase):
    def _generated(self, root: Path) -> tuple[Path, dict]:
        contract = load_contract(EXAMPLE)
        out = generate_project(contract, root)
        manifest = json.loads((out / "factory_manifest.json").read_text(encoding="utf-8"))
        return out, manifest

    def _pass_inputs(self, out: Path, manifest: dict) -> tuple[Path, Path, Path]:
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
        sha_path = out / "sha256.txt"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
        sha_path.write_text(
            ("a" * 64) + "  passed/GoldenGain.vst3/Contents/x86_64-win/GoldenGain.vst3\n",
            encoding="ascii",
        )
        return report_path, provenance_path, sha_path

    def test_generated_source_hash_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, first = self._generated(root / "one")
            _, second = self._generated(root / "two")
            self.assertEqual(
                first["generated_source_sha256"],
                second["generated_source_sha256"],
            )

    def test_generated_source_hash_changes_with_generated_product_version(self):
        contract = load_contract(EXAMPLE)
        changed = copy.deepcopy(contract)
        changed["plugin"]["version"] = "0.1.1"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first_out = generate_project(contract, root / "one")
            second_out = generate_project(changed, root / "two")
            first = json.loads((first_out / "factory_manifest.json").read_text(encoding="utf-8"))
            second = json.loads((second_out / "factory_manifest.json").read_text(encoding="utf-8"))
            self.assertNotEqual(
                first["generated_source_sha256"],
                second["generated_source_sha256"],
            )

    def test_pass_bundle_and_cipi_intake_are_bounded_and_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            validate_result_bundle(bundle)
            self.assertEqual(bundle["schema_version"], "1.1")
            self.assertEqual(bundle["factory_status"], "VALIDATION_PASS")
            self.assertEqual(bundle["dsp_module_id"], manifest["dsp_template"])
            self.assertEqual(
                bundle["dsp_implementation_id"],
                manifest["dsp_implementation_id"],
            )
            self.assertEqual(
                bundle["dsp_certification_status"],
                "FACTORY_CERTIFIED",
            )
            self.assertEqual(
                bundle["dsp_validation_profile"],
                manifest["dsp_validation_profile"],
            )
            self.assertEqual(
                bundle["dsp_module_spec_sha256"],
                manifest["dsp_module_spec_sha256"],
            )
            self.assertEqual(
                bundle["dsp_module_registry_sha256"],
                manifest["dsp_module_registry_sha256"],
            )
            self.assertFalse(bundle["promotion_authority"])
            self.assertFalse(bundle["product_release_authority"])
            self.assertFalse(bundle["cubase_confirmed"])
            self.assertFalse(bundle["listening_confirmed"])
            self.assertFalse(bundle["raw_audio_persisted"])
            self.assertEqual(bundle["source_revision"], "1" * 40)
            self.assertEqual(bundle["validation_revision"], "2" * 40)
            self.assertEqual(bundle["validation_base_revision"], "3" * 40)

            record = build_evidence_record(bundle)
            validate_evidence_record(record)
            self.assertEqual(record["schema_version"], "1.1")
            self.assertEqual(record["evidence_type"], "MEASURED")
            self.assertEqual(record["scope"], "manufacturing_and_host_safety_only")
            for key in (
                "dsp_module_id",
                "dsp_implementation_id",
                "dsp_certification_status",
                "dsp_validation_profile",
                "dsp_module_spec_sha256",
                "dsp_module_registry_sha256",
            ):
                self.assertEqual(record[key], bundle[key])
            self.assertFalse(record["promotion_requested"])
            self.assertEqual(record["source_revision"], "1" * 40)
            self.assertEqual(record["validation_revision"], "2" * 40)
            self.assertEqual(record["validation_base_revision"], "3" * 40)

            evidence_root = root / "evidence"
            first = write_evidence_record(bundle, evidence_root)
            second = write_evidence_record(bundle, evidence_root)
            self.assertEqual(first, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())



    def test_legacy_manifest_emits_v1_0_bundle_and_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            for key in (
                "dsp_implementation_id",
                "dsp_certification_status",
                "dsp_validation_profile",
                "dsp_module_spec_sha256",
                "dsp_module_registry_sha256",
            ):
                manifest.pop(key)
            (out / "factory_manifest.json").write_text(
                json.dumps(manifest, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            self.assertEqual(bundle["schema_version"], "1.0")
            for key in (
                "dsp_module_id",
                "dsp_implementation_id",
                "dsp_certification_status",
                "dsp_validation_profile",
                "dsp_module_spec_sha256",
                "dsp_module_registry_sha256",
            ):
                self.assertNotIn(key, bundle)

            record = build_evidence_record(bundle)
            self.assertEqual(record["schema_version"], "1.0")
            self.assertNotIn("dsp_module_id", record)
            validate_evidence_record(record)

    def test_partial_manifest_module_provenance_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            manifest.pop("dsp_module_registry_sha256")
            (out / "factory_manifest.json").write_text(
                json.dumps(manifest, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            report, provenance, hashes = self._pass_inputs(out, manifest)
            with self.assertRaises(ResultBundleError):
                build_pass_bundle(
                    out / "factory_manifest.json",
                    report,
                    provenance,
                    hashes,
                )

    def test_v1_1_module_hash_tamper_is_rejected_even_with_fresh_bundle_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            bundle["dsp_module_spec_sha256"] = "not-a-sha"
            bundle["bundle_hash"] = _hash_payload(bundle)
            with self.assertRaises(ResultBundleError):
                validate_result_bundle(bundle)

    def test_v1_0_bundle_rejects_v1_1_module_field_injection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            for key in (
                "dsp_implementation_id",
                "dsp_certification_status",
                "dsp_validation_profile",
                "dsp_module_spec_sha256",
                "dsp_module_registry_sha256",
            ):
                manifest.pop(key)
            (out / "factory_manifest.json").write_text(
                json.dumps(manifest, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            self.assertEqual(bundle["schema_version"], "1.0")
            bundle["dsp_module_id"] = "golden_gain_v1"
            bundle["bundle_hash"] = _hash_payload(bundle)
            with self.assertRaises(ResultBundleError):
                validate_result_bundle(bundle)

    def test_v1_1_evidence_module_hash_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            record = build_evidence_record(bundle)
            record["dsp_module_registry_sha256"] = "bad"
            with self.assertRaises(FactoryEvidenceIntakeError):
                validate_evidence_record(record)

    def test_pass_bundle_requires_explicit_validation_revisions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            data = json.loads(provenance.read_text(encoding="utf-8"))
            del data["validation_base_revision"]
            provenance.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ResultBundleError):
                build_pass_bundle(
                    out / "factory_manifest.json",
                    report,
                    provenance,
                    hashes,
                )

    def test_pass_bundle_rejects_platform_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            data = json.loads(provenance.read_text(encoding="utf-8"))
            data["platform"] = "windows-x64"
            provenance.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ResultBundleError):
                build_pass_bundle(
                    out / "factory_manifest.json",
                    report,
                    provenance,
                    hashes,
                )

    def test_artifact_hash_manifest_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            hashes.write_text(("a" * 64) + "  ../escape.vst3\\n", encoding="ascii")
            with self.assertRaises(ResultBundleError):
                build_pass_bundle(
                    out / "factory_manifest.json",
                    report,
                    provenance,
                    hashes,
                )

    def test_bundle_authority_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            tampered = copy.deepcopy(bundle)
            tampered["product_release_authority"] = True
            with self.assertRaises(ResultBundleError):
                validate_result_bundle(tampered)

    def test_quarantine_stays_measured_failure_not_product_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, _ = self._generated(root / "plugin")
            failure_path = out / "failure.json"
            failure_path.write_text(
                json.dumps(
                    {
                        "factory_status": "QUARANTINED",
                        "failure_class": "PLUGINVAL_ERROR",
                        "source_revision": "4" * 40,
                        "validation_revision": "5" * 40,
                        "validation_base_revision": "6" * 40,
                        "validators": {
                            "factory_owned_validation": "PASS",
                            "pluginval": "FAIL",
                            "steinberg_validator": "NOT_RUN",
                        },
                        "release_authority": False,
                    }
                ),
                encoding="utf-8",
            )
            bundle = build_quarantine_bundle(
                out / "factory_manifest.json",
                failure_path,
            )
            self.assertEqual(bundle["schema_version"], "1.1")
            self.assertEqual(bundle["dsp_module_id"], "golden_gain_v1")
            self.assertEqual(bundle["dsp_certification_status"], "FACTORY_CERTIFIED")
            self.assertEqual(bundle["validators"]["factory_owned_validation"], "PASS")
            self.assertEqual(bundle["validators"]["pluginval"], "FAIL")
            self.assertEqual(bundle["validators"]["steinberg_validator"], "NOT_RUN")
            record = build_evidence_record(bundle)
            self.assertEqual(record["factory_status"], "QUARANTINED")
            self.assertEqual(record["evidence_type"], "MEASURED")
            self.assertEqual(record["validation_revision"], "5" * 40)
            self.assertEqual(record["validation_base_revision"], "6" * 40)
            self.assertIn("PLUGINVAL_ERROR", record["claim"])
            self.assertFalse(record["automatic_final_decision"])
            self.assertFalse(record["promotion_authority"])



    def test_bundle_rejects_incomplete_validation_matrix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            malformed = copy.deepcopy(bundle)
            del malformed["validation_matrix"]["block_sizes"]
            with self.assertRaises(ResultBundleError):
                validate_result_bundle(malformed)

    def test_bundle_rejects_disabled_mandatory_matrix_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            malformed = copy.deepcopy(bundle)
            malformed["validation_matrix"]["official_vst3_validator"] = False
            with self.assertRaises(ResultBundleError):
                validate_result_bundle(malformed)

    def test_bundle_rejects_non_string_format_entries(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            malformed = copy.deepcopy(bundle)
            malformed["formats"] = [{"name": "VST3"}]
            with self.assertRaises(ResultBundleError):
                validate_result_bundle(malformed)

    def test_evidence_revision_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            record = build_evidence_record(bundle)
            record["validation_revision"] = "not-a-git-sha"
            with self.assertRaises(FactoryEvidenceIntakeError):
                validate_evidence_record(record)

    def test_evidence_record_hash_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out, manifest = self._generated(root / "plugin")
            report, provenance, hashes = self._pass_inputs(out, manifest)
            bundle = build_pass_bundle(
                out / "factory_manifest.json",
                report,
                provenance,
                hashes,
            )
            record = build_evidence_record(bundle)
            record["claim"] += " tampered"
            with self.assertRaises(FactoryEvidenceIntakeError):
                validate_evidence_record(record)


if __name__ == "__main__":
    unittest.main()
