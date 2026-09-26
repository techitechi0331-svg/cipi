from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from automation.incubator.factory_build_authorization import (
    FactoryBuildAuthorizationError,
    _hash_payload,
    build_authorization,
    validate_authorization,
    verify_authorization_sources,
    write_authorized_build_request,
)
from automation.incubator.factory_handoff import (
    build_contract_candidate,
    write_candidate,
)
from juce_factory.factory.contract import load_contract


ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "examples" / "golden_gain.contract.json"


class FactoryBuildAuthorizationTests(unittest.TestCase):
    def _fixture(self, root: Path):
        pid = "PLUGIN-RP-FACTORY-BUILD-AUTH-TEST-001"

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
            "contract": load_contract(GOLDEN),
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

        contract, receipt = build_contract_candidate(
            root / proposal_rel,
            root / decision_rel,
            root / evidence_rel,
            root / manufacturing_review_rel,
            root=root,
        )
        contract_dir = root / contract_dir_rel
        write_candidate(contract, receipt, contract_dir)

        contract_candidate_rel = contract_dir_rel / "plugin_contract_candidate.json"
        handoff_receipt_rel = contract_dir_rel / "handoff_receipt.json"
        auth_review = {
            "schema_version": "1.0",
            "plugin_proposal_id": pid,
            "source_contract_candidate": contract_candidate_rel.as_posix(),
            "source_handoff_receipt": handoff_receipt_rel.as_posix(),
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
            yaml.safe_dump(auth_review, sort_keys=False), encoding="utf-8"
        )

        return {
            "pid": pid,
            "contract": root / contract_candidate_rel,
            "receipt": root / handoff_receipt_rel,
            "review": auth_review_path,
            "contract_dir": contract_dir,
        }

    def _authorize(self, root: Path):
        paths = self._fixture(root)
        contract, authorization = build_authorization(
            paths["contract"],
            paths["receipt"],
            paths["review"],
            root=root,
        )
        return paths, contract, authorization

    def test_separate_review_authorizes_build_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, contract, authorization = self._authorize(root)

            self.assertEqual(
                authorization["status"], "FACTORY_BUILD_AUTHORIZED"
            )
            self.assertEqual(authorization["authority"], "ASSISTANT_REVIEW")
            self.assertTrue(authorization["factory_build_authorized"])
            self.assertFalse(authorization["automatic_final_decision"])
            self.assertFalse(authorization["product_release_authority"])
            self.assertFalse(authorization["cubase_confirmed"])
            self.assertFalse(authorization["listening_confirmed"])

            out = write_authorized_build_request(
                contract, authorization, root / "authorized-request"
            )
            self.assertTrue((out / "plugin_contract.json").exists())
            self.assertTrue((out / "factory_build_authorization.json").exists())

    def test_automation_cannot_authorize_factory_build(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            review = yaml.safe_load(paths["review"].read_text(encoding="utf-8"))
            review["authorization"]["authority"] = "AUTOMATION"
            paths["review"].write_text(yaml.safe_dump(review), encoding="utf-8")

            with self.assertRaises(FactoryBuildAuthorizationError):
                build_authorization(
                    paths["contract"], paths["receipt"], paths["review"], root=root
                )

    def test_review_cannot_smuggle_release_or_final_decision(self):
        for key in ("final_product_decision", "product_release_authority"):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                paths = self._fixture(root)
                review = yaml.safe_load(paths["review"].read_text(encoding="utf-8"))
                review["authorization"][key] = True
                paths["review"].write_text(yaml.safe_dump(review), encoding="utf-8")

                with self.assertRaises(FactoryBuildAuthorizationError):
                    build_authorization(
                        paths["contract"], paths["receipt"], paths["review"], root=root
                    )

    def test_review_requires_explicit_build_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            review = yaml.safe_load(paths["review"].read_text(encoding="utf-8"))
            review["authorization"]["approved_for_factory_build"] = False
            paths["review"].write_text(yaml.safe_dump(review), encoding="utf-8")

            with self.assertRaises(FactoryBuildAuthorizationError):
                build_authorization(
                    paths["contract"], paths["receipt"], paths["review"], root=root
                )

    def test_contract_mutation_after_authorization_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths, _, authorization = self._authorize(root)
            verify_authorization_sources(authorization, root=root)

            contract = json.loads(paths["contract"].read_text(encoding="utf-8"))
            contract["plugin"]["version"] = "0.1.1"
            paths["contract"].write_text(json.dumps(contract), encoding="utf-8")

            with self.assertRaises(FactoryBuildAuthorizationError):
                verify_authorization_sources(authorization, root=root)

    def test_handoff_receipt_mutation_after_authorization_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths, _, authorization = self._authorize(root)
            receipt = json.loads(paths["receipt"].read_text(encoding="utf-8"))
            receipt["plugin_proposal_id"] += "-MUTATED"
            paths["receipt"].write_text(json.dumps(receipt), encoding="utf-8")

            with self.assertRaises(FactoryBuildAuthorizationError):
                verify_authorization_sources(authorization, root=root)

    def test_authorization_review_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths, _, authorization = self._authorize(root)
            review = yaml.safe_load(paths["review"].read_text(encoding="utf-8"))
            review["authorization"]["listening_confirmed"] = True
            paths["review"].write_text(yaml.safe_dump(review), encoding="utf-8")

            with self.assertRaises(FactoryBuildAuthorizationError):
                verify_authorization_sources(authorization, root=root)

    def test_authorization_semantic_tamper_rejected_even_with_fresh_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, authorization = self._authorize(root)
            tampered = copy.deepcopy(authorization)
            tampered["product_release_authority"] = True
            tampered["authorization_hash"] = _hash_payload(
                tampered, "authorization_hash"
            )

            with self.assertRaises(FactoryBuildAuthorizationError):
                validate_authorization(tampered)

    def test_authorization_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, authorization = self._authorize(root)
            tampered = copy.deepcopy(authorization)
            tampered["source_contract_candidate"] = "../../escape.json"
            tampered["authorization_hash"] = _hash_payload(
                tampered, "authorization_hash"
            )

            with self.assertRaises(FactoryBuildAuthorizationError):
                validate_authorization(tampered)

    def test_authorized_request_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, contract, authorization = self._authorize(root)
            out = root / "authorized-request"
            write_authorized_build_request(contract, authorization, out)

            with self.assertRaises(FactoryBuildAuthorizationError):
                write_authorized_build_request(contract, authorization, out)


if __name__ == "__main__":
    unittest.main()
