from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from juce_factory.factory.contract import canonical_json, contract_sha256, validate_contract

HANDOFF_VERSION = "1.0"
NON_AUTOMATION_AUTHORITIES = {"HUMAN", "ASSISTANT_REVIEW"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
PASS_GATES = {
    "baseline_improvement_pass",
    "holdout_pass",
    "regression_pass",
    "cpu_pass",
    "latency_pass",
    "overlap_advantage_pass",
    "negative_knowledge_reviewed",
}


class FactoryHandoffError(ValueError):
    pass


def _load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FactoryHandoffError(f"{path} must contain a YAML mapping")
    return value



def _require_safe_rel(value: Any, label: str, prefix: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FactoryHandoffError(f"{label} must be non-empty")
    normalized = value.replace("\\", "/")
    if normalized != value:
        raise FactoryHandoffError(f"{label} must use canonical forward-slash separators")
    parts = normalized.split("/")
    if normalized.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise FactoryHandoffError(f"{label} must be a safe repository-relative path")
    if not normalized.startswith(prefix):
        raise FactoryHandoffError(f"{label} must be under {prefix}")
    return normalized

def _canonical_rel(path: str | Path, root: Path) -> str:
    resolved = Path(path).resolve()
    root_resolved = root.resolve()
    try:
        rel = resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise FactoryHandoffError(f"path is outside repository root: {path}") from exc
    return rel.as_posix()


def _file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _receipt_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("receipt_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_review(review: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "plugin_proposal_id",
        "source_incubate_decision",
        "source_product_evidence",
        "review",
        "contract",
    }
    missing = sorted(required - set(review))
    unknown = sorted(set(review) - required)
    if missing:
        raise FactoryHandoffError(f"Manufacturing Review missing fields: {missing}")
    if unknown:
        raise FactoryHandoffError(f"Manufacturing Review contains unknown fields: {unknown}")
    if review["schema_version"] != HANDOFF_VERSION:
        raise FactoryHandoffError("unsupported Manufacturing Review schema_version")
    if not isinstance(review["plugin_proposal_id"], str) or not review["plugin_proposal_id"].strip():
        raise FactoryHandoffError("plugin_proposal_id must be non-empty")
    _require_safe_rel(
        review["source_incubate_decision"],
        "source_incubate_decision",
        "research/incubator/decisions/",
    )
    _require_safe_rel(
        review["source_product_evidence"],
        "source_product_evidence",
        "research/incubator/evidence/",
    )

    gate = review["review"]
    if not isinstance(gate, dict):
        raise FactoryHandoffError("review must be an object")
    gate_required = {
        "authority",
        "approved_for_factory_contract_candidate",
        "automatic_approval",
        "final_product_decision",
        "factory_build_authorized",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
    }
    missing_gate = sorted(gate_required - set(gate))
    unknown_gate = sorted(set(gate) - gate_required)
    if missing_gate:
        raise FactoryHandoffError(f"review missing fields: {missing_gate}")
    if unknown_gate:
        raise FactoryHandoffError(f"review contains unknown fields: {unknown_gate}")
    if gate["authority"] not in NON_AUTOMATION_AUTHORITIES:
        raise FactoryHandoffError("Manufacturing Review authority must be HUMAN or ASSISTANT_REVIEW")
    if gate["approved_for_factory_contract_candidate"] is not True:
        raise FactoryHandoffError("Manufacturing Review must explicitly approve a Factory Contract candidate")
    for key in (
        "automatic_approval",
        "final_product_decision",
        "factory_build_authorized",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
    ):
        if gate[key] is not False:
            raise FactoryHandoffError(f"review.{key} must be false")

    contract = review["contract"]
    if not isinstance(contract, dict):
        raise FactoryHandoffError("contract must be a Plugin Contract object")
    validate_contract(contract)


def build_contract_candidate(
    proposal_path: str | Path,
    decision_path: str | Path,
    evidence_path: str | Path,
    review_path: str | Path,
    *,
    root: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    repo_root = Path(root).resolve()
    proposal = _load_yaml(proposal_path)
    decision = _load_yaml(decision_path)
    evidence = _load_yaml(evidence_path)
    review = _load_yaml(review_path)
    validate_review(review)

    pid = review["plugin_proposal_id"]
    if proposal.get("plugin_proposal_id") != pid:
        raise FactoryHandoffError("proposal does not match Manufacturing Review")
    if proposal.get("automatic_production_allowed") is not False:
        raise FactoryHandoffError("proposal automatic_production_allowed must remain false")

    if decision.get("plugin_proposal_id") != pid:
        raise FactoryHandoffError("INCUBATE decision does not match proposal")
    if decision.get("decision") != "INCUBATE":
        raise FactoryHandoffError("Factory handoff requires an INCUBATE decision")
    if decision.get("final") is not False:
        raise FactoryHandoffError("INCUBATE decision must remain non-final")
    if decision.get("authority") != "AUTOMATION":
        raise FactoryHandoffError("current Incubator handoff expects the bounded automation INCUBATE decision")

    if evidence.get("plugin_proposal_id") != pid:
        raise FactoryHandoffError("product evidence does not match proposal")
    if evidence.get("raw_audio_persisted") is not False:
        raise FactoryHandoffError("product evidence must not persist raw audio")
    if not all(evidence.get(key) is True for key in PASS_GATES):
        raise FactoryHandoffError("all Incubator product-discrimination gates must pass")

    decision_rel = _canonical_rel(decision_path, repo_root)
    evidence_rel = _canonical_rel(evidence_path, repo_root)
    if decision.get("source_evidence") != evidence_rel:
        raise FactoryHandoffError("INCUBATE decision source_evidence does not match supplied evidence")
    if review["source_incubate_decision"] != decision_rel:
        raise FactoryHandoffError("Manufacturing Review decision provenance does not match")
    if review["source_product_evidence"] != evidence_rel:
        raise FactoryHandoffError("Manufacturing Review evidence provenance does not match")

    contract = review["contract"]
    validate_contract(contract)

    receipt: dict[str, Any] = {
        "schema_version": HANDOFF_VERSION,
        "handoff_kind": "INCUBATOR_TO_FACTORY_CONTRACT_CANDIDATE",
        "plugin_proposal_id": pid,
        "source_proposal": _canonical_rel(proposal_path, repo_root),
        "source_proposal_sha256": _file_sha256(proposal_path),
        "source_incubate_decision": decision_rel,
        "source_incubate_decision_sha256": _file_sha256(decision_path),
        "source_product_evidence": evidence_rel,
        "source_product_evidence_sha256": _file_sha256(evidence_path),
        "source_manufacturing_review": _canonical_rel(review_path, repo_root),
        "source_manufacturing_review_sha256": _file_sha256(review_path),
        "review_authority": review["review"]["authority"],
        "contract_sha256": contract_sha256(contract),
        "status": "CONTRACT_CANDIDATE",
        "automatic_final_decision": False,
        "factory_build_authorized": False,
        "product_release_authority": False,
        "cubase_confirmed": False,
        "listening_confirmed": False,
    }
    receipt["receipt_hash"] = _receipt_hash(receipt)
    validate_receipt(receipt)
    return contract, receipt


def validate_receipt(receipt: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "handoff_kind",
        "plugin_proposal_id",
        "source_proposal",
        "source_proposal_sha256",
        "source_incubate_decision",
        "source_incubate_decision_sha256",
        "source_product_evidence",
        "source_product_evidence_sha256",
        "source_manufacturing_review",
        "source_manufacturing_review_sha256",
        "review_authority",
        "contract_sha256",
        "status",
        "automatic_final_decision",
        "factory_build_authorized",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
        "receipt_hash",
    }
    missing = sorted(required - set(receipt))
    unknown = sorted(set(receipt) - required)
    if missing:
        raise FactoryHandoffError(f"handoff receipt missing fields: {missing}")
    if unknown:
        raise FactoryHandoffError(f"handoff receipt contains unknown fields: {unknown}")
    if receipt["schema_version"] != HANDOFF_VERSION:
        raise FactoryHandoffError("unsupported handoff receipt schema_version")
    if receipt["handoff_kind"] != "INCUBATOR_TO_FACTORY_CONTRACT_CANDIDATE":
        raise FactoryHandoffError("unexpected handoff kind")
    if receipt["status"] != "CONTRACT_CANDIDATE":
        raise FactoryHandoffError("handoff status must remain CONTRACT_CANDIDATE")
    if receipt["review_authority"] not in NON_AUTOMATION_AUTHORITIES:
        raise FactoryHandoffError("handoff review authority cannot be AUTOMATION")
    for key in (
        "automatic_final_decision",
        "factory_build_authorized",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
    ):
        if receipt[key] is not False:
            raise FactoryHandoffError(f"{key} must be false")
    for key in (
        "contract_sha256",
        "source_proposal_sha256",
        "source_incubate_decision_sha256",
        "source_product_evidence_sha256",
        "source_manufacturing_review_sha256",
        "receipt_hash",
    ):
        if not isinstance(receipt[key], str) or not _SHA256.fullmatch(receipt[key]):
            raise FactoryHandoffError(f"{key} must be a lowercase SHA-256 digest")
    if not isinstance(receipt["plugin_proposal_id"], str) or not receipt["plugin_proposal_id"].strip():
        raise FactoryHandoffError("plugin_proposal_id must be non-empty")
    _require_safe_rel(receipt["source_proposal"], "source_proposal", "research/incubator/proposals/")
    _require_safe_rel(
        receipt["source_incubate_decision"],
        "source_incubate_decision",
        "research/incubator/decisions/",
    )
    _require_safe_rel(
        receipt["source_product_evidence"],
        "source_product_evidence",
        "research/incubator/evidence/",
    )
    _require_safe_rel(
        receipt["source_manufacturing_review"],
        "source_manufacturing_review",
        "research/incubator/manufacturing_reviews/",
    )
    if receipt["receipt_hash"] != _receipt_hash(receipt):
        raise FactoryHandoffError("handoff receipt hash mismatch")


def verify_receipt_sources(receipt: dict[str, Any], *, root: str | Path) -> None:
    validate_receipt(receipt)
    repo_root = Path(root).resolve()
    pairs = (
        ("source_proposal", "source_proposal_sha256"),
        ("source_incubate_decision", "source_incubate_decision_sha256"),
        ("source_product_evidence", "source_product_evidence_sha256"),
        ("source_manufacturing_review", "source_manufacturing_review_sha256"),
    )
    for path_key, hash_key in pairs:
        rel = receipt[path_key]
        path = (repo_root / rel).resolve()
        try:
            path.relative_to(repo_root)
        except ValueError as exc:
            raise FactoryHandoffError(f"{path_key} escapes repository root") from exc
        if not path.is_file():
            raise FactoryHandoffError(f"{path_key} source file is missing: {rel}")
        actual = _file_sha256(path)
        if actual != receipt[hash_key]:
            raise FactoryHandoffError(f"{path_key} source hash mismatch: {rel}")


def write_candidate(
    contract: dict[str, Any],
    receipt: dict[str, Any],
    output_dir: str | Path,
) -> Path:
    validate_contract(contract)
    validate_receipt(receipt)
    if contract_sha256(contract) != receipt["contract_sha256"]:
        raise FactoryHandoffError("contract does not match handoff receipt")

    out = Path(output_dir)
    if out.exists() and any(out.iterdir()):
        raise FactoryHandoffError(f"refusing to overwrite non-empty handoff output: {out}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "plugin_contract_candidate.json").write_text(
        json.dumps(contract, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "handoff_receipt.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(prog="cipi-incubator-factory-handoff")
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        contract, receipt = build_contract_candidate(
            args.proposal,
            args.decision,
            args.evidence,
            args.review,
            root=args.root,
        )
        out = write_candidate(contract, receipt, args.output)
        print(json.dumps({
            "status": "FACTORY_CONTRACT_CANDIDATE_WRITTEN",
            "path": str(out),
            "contract_sha256": receipt["contract_sha256"],
            "factory_build_authorized": False,
        }))
        return 0
    except (FactoryHandoffError, ValueError, OSError, yaml.YAMLError) as exc:
        print(json.dumps({"status": "FACTORY_HANDOFF_ERROR", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
