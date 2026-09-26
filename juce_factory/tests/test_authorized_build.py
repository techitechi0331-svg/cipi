from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from automation.incubator.factory_build_authorization import (
    build_authorization,
    write_authorized_build_request,
)
from automation.incubator.factory_handoff import (
    build_contract_candidate,
    write_candidate,
)
from juce_factory.factory.authorized_build import (
    AuthorizedBuildIntakeError,
    _binding_hash,
    bind_factory_result,
    discover_authorized_requests,
    generate_authorized_project,
    load_authorized_request,
    validate_result_binding,
)
from juce_factory.factory.contract import load_contract
from juce_factory.factory.result_bundle import (
    build_pass_bundle,
    build_quarantine_bundle,
    write_result_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "examples" / "golden_gain.contract.json"


class AuthorizedBuildIntakeTests(unittest.TestCase):
    def _request(
        self,
        root: Path,
        *,
        pid: str,
        request_id: str,
        plugin_id: str = "GoldenGain",
        bundle_id: str = "audio.cipi.factory.goldengain",
        manufacturer_code: str = "Cipi",
        plugin_code: str = "JFG1",
    ) -> Path:
        proposal_rel = Path("research/incubator/proposals") / f"{pid}.yaml"
        evidence_rel = Path("research/incubator/evidence") / pid / "evidence-001.yaml"
        decision_rel = Path("research/incubator/decisions") / f"{pid}-incubate.yaml"
        manufacturing_review_rel = (
            Path("research/incubator/manufacturing_reviews") / f"{pid}.yaml"
        )
        contract_dir_rel = Path("research/incubator/factory_contracts") / pid
        auth_review_rel = (
            Path("research/incubator/factory_build_authorizations") / f"{pid}.yaml"
        )
        request_rel = Path("research/incubator/factory_build_requests") / request_id

        contract = load_contract(GOLDEN)
        contract["plugin"]["id"] = plugin_id
        contract["plugin"]["name"] = f"{plugin_id} Test"
        contract["plugin"]["bundle_id"] = bundle_id
        contract["plugin"]["manufacturer_code"] = manufacturer_code
        contract["plugin"]["plugin_code"] = plugin_code

        proposal = {
            "schema_version": "1.0",
            "plugin_proposal_id": pid,
            "state": "RESEARCH_MORE",
            "automatic_production_allowed": False,
        }
        evidence = {
            "schema_version": "1.0",
            "plugin_proposal_id": pid,
            "source_measurement_run": "research/runs/TEST/run-001",
            "baseline_improvement_pass": True,
            "holdout_pass": True,
            "regression_pass": True,
            "cpu_pass": True,
            "latency_pass": True,
            "overlap_advantage_pass": True,
            "negative_knowledge_reviewed": True,
            "raw_audio_persisted": False,
            "scope": "synthetic unit fixture",
        }
        decision = {
            "schema_version": "1.0",
            "plugin_proposal_id": pid,
            "decision": "INCUBATE",
            "authority": "AUTOMATION",
            "final": False,
            "source_evidence": evidence_rel.as_posix(),
        }
        manufacturing_review = {
            "schema_version": "1.0",
            "plugin_proposal_id": pid,
            "source_incubate_decision": decision_rel.as_posix(),
            "source_product_evidence": evidence_rel.as_posix(),
            "review": {
                "authority": "ASSISTANT_REVIEW",
                "approved_for_factory_contract_candidate": True,
                "automatic_approval": False,
                "final_product_decision": False,
                "factory_build_authorized": False,
                "product_release_authority": False,
                "cubase_confirmed": False,
                "listening_confirmed": False,
            },
            "contract": contract,
        }

        for rel, value in (
            (proposal_rel, proposal),
            (evidence_rel, evidence),
            (decision_rel, decision),
            (manufacturing_review_rel, manufacturing_review),
        ):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

        candidate, receipt = build_contract_candidate(
            root / proposal_rel,
            root / decision_rel,
            root / evidence_rel,
            root / manufacturing_review_rel,
            root=root,
        )
        contract_dir = root / contract_dir_rel
        write_candidate(candidate, receipt, contract_dir)

        contract_rel = contract_dir_rel / "plugin_contract_candidate.json"
        receipt_rel = contract_dir_rel / "handoff_receipt.json"
        auth_review = {
            "schema_version": "1.0",
            "plugin_proposal_id": pid,
            "source_contract_candidate": contract_rel.as_posix(),
            "source_handoff_receipt": receipt_rel.as_posix(),
            "authorization": {
                "authority": "ASSISTANT_REVIEW",
                "approved_for_factory_build": True,
                "automatic_approval": False,
                "final_product_decision": False,
                "product_release_authority": False,
                "cubase_confirmed": False,
                "listening_confirmed": False,
            },
        }
        auth_review_path = root / auth_review_rel
        auth_review_path.parent.mkdir(parents=True, exist_ok=True)
        auth_review_path.write_text(
            yaml.safe_dump(auth_review, sort_keys=False),
            encoding="utf-8",
        )

        authorized_contract, authorization = build_authorization(
            root / contract_rel,
            root / receipt_rel,
            auth_review_path,
            root=root,
        )

        request_dir = root / request_rel
        write_authorized_build_request(
            authorized_contract,
            authorization,
            request_dir,
        )
        return request_dir


    def _pass_bundle(self, root: Path, request: Path, *, suffix: str) -> Path:
        generated = generate_authorized_project(
            request,
            root / f"generated-{suffix}",
            root=root,
        )
        manifest = json.loads(
            (generated / "factory_manifest.json").read_text(encoding="utf-8")
        )
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
        report_path = generated / "validation_report.json"
        provenance_path = generated / "provenance.json"
        hashes_path = generated / "sha256.txt"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
        hashes_path.write_text(
            ("a" * 64)
            + "  passed/Candidate.vst3/Contents/x86_64-win/Candidate.vst3\n",
            encoding="ascii",
        )
        bundle = build_pass_bundle(
            generated / "factory_manifest.json",
            report_path,
            provenance_path,
            hashes_path,
        )
        bundle_path = generated / "factory_result_bundle.json"
        write_result_bundle(bundle_path, bundle)
        return bundle_path

    def _quarantine_bundle(self, root: Path, request: Path, *, suffix: str) -> Path:
        generated = generate_authorized_project(
            request,
            root / f"quarantine-generated-{suffix}",
            root=root,
        )
        failure = {
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
        failure_path = generated / "failure.json"
        failure_path.write_text(json.dumps(failure), encoding="utf-8")
        bundle = build_quarantine_bundle(
            generated / "factory_manifest.json",
            failure_path,
        )
        bundle_path = generated / "factory_result_bundle.json"
        write_result_bundle(bundle_path, bundle)
        return bundle_path

    def test_valid_request_loads_and_discovers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-001",
                request_id="authorized-001",
            )
            contract, authorization = load_authorized_request(request, root=root)
            self.assertEqual(contract["plugin"]["id"], "GoldenGain")
            self.assertTrue(authorization["factory_build_authorized"])
            self.assertFalse(authorization["product_release_authority"])

            records = discover_authorized_requests(root=root)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["request_id"], "authorized-001")
            self.assertEqual(
                records[0]["authorization_hash"],
                authorization["authorization_hash"],
            )

    def test_authorized_request_generates_factory_project(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-002",
                request_id="authorized-002",
            )
            out = generate_authorized_project(
                request,
                root / "generated",
                root=root,
            )
            self.assertTrue((out / "CMakeLists.txt").exists())
            manifest = json.loads(
                (out / "factory_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["plugin_id"], "GoldenGain")

    def test_request_contract_substitution_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-003",
                request_id="authorized-003",
            )
            contract_path = request / "plugin_contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["plugin"]["version"] = "0.1.1"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")

            with self.assertRaises(AuthorizedBuildIntakeError):
                load_authorized_request(request, root=root)

    def test_authorization_source_mutation_is_rejected_at_intake(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-004",
                request_id="authorized-004",
            )
            authorization = json.loads(
                (request / "factory_build_authorization.json").read_text(
                    encoding="utf-8"
                )
            )
            review_path = root / authorization["source_authorization_review"]
            review = yaml.safe_load(review_path.read_text(encoding="utf-8"))
            review["authorization"]["listening_confirmed"] = True
            review_path.write_text(yaml.safe_dump(review), encoding="utf-8")

            with self.assertRaises(Exception):
                load_authorized_request(request, root=root)

    def test_unexpected_request_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-005",
                request_id="authorized-005",
            )
            (request / "release_me.txt").write_text("no", encoding="utf-8")

            with self.assertRaises(AuthorizedBuildIntakeError):
                load_authorized_request(request, root=root)

    def test_partial_request_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = (
                root
                / "research/incubator/factory_build_requests"
                / "partial-request"
            )
            request.mkdir(parents=True)
            (request / "plugin_contract.json").write_text("{}", encoding="utf-8")

            with self.assertRaises(AuthorizedBuildIntakeError):
                discover_authorized_requests(root=root)

    def test_duplicate_plugin_id_across_requests_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-006A",
                request_id="authorized-006a",
                plugin_id="DuplicatePlugin",
                bundle_id="audio.cipi.factory.duplicate.a",
                plugin_code="DP01",
            )
            self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-006B",
                request_id="authorized-006b",
                plugin_id="DuplicatePlugin",
                bundle_id="audio.cipi.factory.duplicate.b",
                plugin_code="DP02",
            )

            with self.assertRaises(AuthorizedBuildIntakeError):
                discover_authorized_requests(root=root)

    def test_duplicate_bundle_id_across_requests_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-007A",
                request_id="authorized-007a",
                plugin_id="BundlePluginA",
                bundle_id="audio.cipi.factory.samebundle",
                plugin_code="BA01",
            )
            self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-007B",
                request_id="authorized-007b",
                plugin_id="BundlePluginB",
                bundle_id="audio.cipi.factory.samebundle",
                plugin_code="BB01",
            )

            with self.assertRaises(AuthorizedBuildIntakeError):
                discover_authorized_requests(root=root)

    def test_duplicate_vst3_code_pair_across_requests_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-008A",
                request_id="authorized-008a",
                plugin_id="CodePluginA",
                bundle_id="audio.cipi.factory.code.a",
                manufacturer_code="Cipi",
                plugin_code="ZZ01",
            )
            self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-008B",
                request_id="authorized-008b",
                plugin_id="CodePluginB",
                bundle_id="audio.cipi.factory.code.b",
                manufacturer_code="Cipi",
                plugin_code="ZZ01",
            )

            with self.assertRaises(AuthorizedBuildIntakeError):
                discover_authorized_requests(root=root)


    def test_pass_result_binds_to_exact_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-009",
                request_id="authorized-009",
            )
            bundle_path = self._pass_bundle(root, request, suffix="009")
            binding = bind_factory_result(request, bundle_path, root=root)
            self.assertEqual(binding["factory_status"], "VALIDATION_PASS")
            self.assertTrue(binding["factory_build_authorized"])
            self.assertFalse(binding["product_release_authority"])
            self.assertFalse(binding["cubase_confirmed"])
            self.assertFalse(binding["listening_confirmed"])

            authorization = json.loads(
                (request / "factory_build_authorization.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                binding["authorization_hash"],
                authorization["authorization_hash"],
            )

    def test_quarantine_result_still_binds_without_release_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-010",
                request_id="authorized-010",
            )
            bundle_path = self._quarantine_bundle(root, request, suffix="010")
            binding = bind_factory_result(request, bundle_path, root=root)
            self.assertEqual(binding["factory_status"], "QUARANTINED")
            self.assertTrue(binding["factory_build_authorized"])
            self.assertFalse(binding["product_release_authority"])

    def test_result_from_different_contract_cannot_be_bound(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request_a = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-011A",
                request_id="authorized-011a",
                plugin_id="BindingPluginA",
                bundle_id="audio.cipi.binding.a",
                plugin_code="BD01",
            )
            request_b = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-011B",
                request_id="authorized-011b",
                plugin_id="BindingPluginB",
                bundle_id="audio.cipi.binding.b",
                plugin_code="BD02",
            )
            bundle_b = self._pass_bundle(root, request_b, suffix="011b")
            with self.assertRaises(AuthorizedBuildIntakeError):
                bind_factory_result(request_a, bundle_b, root=root)

    def test_result_binding_semantic_tamper_is_rejected_with_fresh_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-012",
                request_id="authorized-012",
            )
            bundle_path = self._pass_bundle(root, request, suffix="012")
            binding = bind_factory_result(request, bundle_path, root=root)
            binding["product_release_authority"] = True
            binding["binding_hash"] = _binding_hash(binding)
            with self.assertRaises(AuthorizedBuildIntakeError):
                validate_result_binding(binding)

    def test_result_binding_schema_matches_runtime_fields(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request = self._request(
                root,
                pid="PLUGIN-RP-AUTHORIZED-013",
                request_id="authorized-013",
            )
            bundle_path = self._pass_bundle(root, request, suffix="013")
            binding = bind_factory_result(request, bundle_path, root=root)
            schema = json.loads(
                (
                    ROOT
                    / "schemas"
                    / "authorized_build_result_binding.schema.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(set(schema["required"]), set(binding))
            self.assertFalse(
                schema["properties"]["product_release_authority"]["const"]
            )

    def test_empty_request_root_is_valid_and_discovers_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(discover_authorized_requests(root=root), [])


if __name__ == "__main__":
    unittest.main()
