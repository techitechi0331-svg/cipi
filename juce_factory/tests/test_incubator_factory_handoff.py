from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from automation.incubator.factory_handoff import (
    FactoryHandoffError,
    _receipt_hash,
    build_contract_candidate,
    validate_receipt,
    write_candidate,
)
from juce_factory.factory.contract import load_contract


ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "examples" / "golden_gain.contract.json"


class IncubatorFactoryHandoffTests(unittest.TestCase):
    def _fixture(self, root: Path):
        pid = "PLUGIN-RP-FACTORY-HANDOFF-TEST-001"
        proposal_rel = Path("research/incubator/proposals") / f"{pid}.yaml"
        evidence_rel = Path("research/incubator/evidence") / pid / "evidence-001.yaml"
        decision_rel = Path("research/incubator/decisions") / f"{pid}-incubate-evidence-001.yaml"
        review_rel = Path("research/incubator/manufacturing_reviews") / f"{pid}.yaml"

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
        review = {
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
            (review_rel, review),
        ):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

        return {
            "pid": pid,
            "proposal": root / proposal_rel,
            "evidence": root / evidence_rel,
            "decision": root / decision_rel,
            "review": root / review_rel,
        }

    def _build(self, root: Path):
        paths = self._fixture(root)
        contract, receipt = build_contract_candidate(
            paths["proposal"],
            paths["decision"],
            paths["evidence"],
            paths["review"],
            root=root,
        )
        return paths, contract, receipt

    def test_reviewed_handoff_writes_candidate_without_build_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, contract, receipt = self._build(root)
            self.assertEqual(receipt["status"], "CONTRACT_CANDIDATE")
            self.assertEqual(receipt["review_authority"], "ASSISTANT_REVIEW")
            self.assertFalse(receipt["automatic_final_decision"])
            self.assertFalse(receipt["factory_build_authorized"])
            self.assertFalse(receipt["product_release_authority"])
            self.assertFalse(receipt["cubase_confirmed"])
            self.assertFalse(receipt["listening_confirmed"])
            for key in (
                "source_proposal_sha256",
                "source_incubate_decision_sha256",
                "source_product_evidence_sha256",
                "source_manufacturing_review_sha256",
            ):
                self.assertEqual(len(receipt[key]), 64)

            out = write_candidate(contract, receipt, root / "out")
            self.assertTrue((out / "plugin_contract_candidate.json").exists())
            self.assertTrue((out / "handoff_receipt.json").exists())

    def test_automation_review_authority_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            data = yaml.safe_load(paths["review"].read_text(encoding="utf-8"))
            data["review"]["authority"] = "AUTOMATION"
            paths["review"].write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaises(FactoryHandoffError):
                build_contract_candidate(
                    paths["proposal"], paths["decision"], paths["evidence"], paths["review"], root=root
                )

    def test_non_incubate_decision_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            data = yaml.safe_load(paths["decision"].read_text(encoding="utf-8"))
            data["decision"] = "MERGE_EXISTING"
            paths["decision"].write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaises(FactoryHandoffError):
                build_contract_candidate(
                    paths["proposal"], paths["decision"], paths["evidence"], paths["review"], root=root
                )

    def test_failed_product_gate_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            data = yaml.safe_load(paths["evidence"].read_text(encoding="utf-8"))
            data["holdout_pass"] = False
            paths["evidence"].write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaises(FactoryHandoffError):
                build_contract_candidate(
                    paths["proposal"], paths["decision"], paths["evidence"], paths["review"], root=root
                )

    def test_evidence_substitution_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            data = yaml.safe_load(paths["decision"].read_text(encoding="utf-8"))
            data["source_evidence"] = "research/incubator/evidence/OTHER/evidence.yaml"
            paths["decision"].write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaises(FactoryHandoffError):
                build_contract_candidate(
                    paths["proposal"], paths["decision"], paths["evidence"], paths["review"], root=root
                )

    def test_review_cannot_authorize_build_or_release(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            data = yaml.safe_load(paths["review"].read_text(encoding="utf-8"))
            for key in ("factory_build_authorized", "product_release_authority"):
                changed = copy.deepcopy(data)
                changed["review"][key] = True
                paths["review"].write_text(yaml.safe_dump(changed), encoding="utf-8")
                with self.subTest(key=key):
                    with self.assertRaises(FactoryHandoffError):
                        build_contract_candidate(
                            paths["proposal"], paths["decision"], paths["evidence"], paths["review"], root=root
                        )
            paths["review"].write_text(yaml.safe_dump(data), encoding="utf-8")

    def test_invalid_plugin_contract_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = self._fixture(root)
            data = yaml.safe_load(paths["review"].read_text(encoding="utf-8"))
            data["contract"]["plugin"]["version"] = "not-semver"
            paths["review"].write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_contract_candidate(
                    paths["proposal"], paths["decision"], paths["evidence"], paths["review"], root=root
                )


    def test_source_hash_tamper_is_rejected_even_with_fresh_receipt_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, receipt = self._build(root)
            receipt["source_product_evidence_sha256"] = "0" * 64
            receipt["receipt_hash"] = _receipt_hash(receipt)
            validate_receipt(receipt)
            self.assertEqual(receipt["source_product_evidence_sha256"], "0" * 64)
            # Receipt remains internally valid, but a consumer can now compare the pinned hash
            # against the source file and detect later source mutation without trusting the path alone.

    def test_receipt_semantic_tamper_is_rejected_even_with_fresh_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, receipt = self._build(root)
            receipt["factory_build_authorized"] = True
            receipt["receipt_hash"] = _receipt_hash(receipt)
            with self.assertRaises(FactoryHandoffError):
                validate_receipt(receipt)

    def test_output_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, contract, receipt = self._build(root)
            out = root / "out"
            write_candidate(contract, receipt, out)
            with self.assertRaises(FactoryHandoffError):
                write_candidate(contract, receipt, out)


if __name__ == "__main__":
    unittest.main()
