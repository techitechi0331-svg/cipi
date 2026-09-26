from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from automation.incubator.factory_handoff import (
    FactoryHandoffError,
    NON_AUTOMATION_AUTHORITIES,
    validate_receipt,
    verify_receipt_sources,
)
from juce_factory.factory.contract import canonical_json, contract_sha256, validate_contract

AUTHORIZATION_VERSION = "1.0"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class FactoryBuildAuthorizationError(ValueError):
    pass


def _load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FactoryBuildAuthorizationError(f"{path} must contain a JSON object")
    return value


def _load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FactoryBuildAuthorizationError(f"{path} must contain a YAML mapping")
    return value


def _file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _hash_payload(data: dict[str, Any], hash_field: str) -> str:
    payload = dict(data)
    payload.pop(hash_field, None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _safe_repo_rel(value: Any, label: str, prefix: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FactoryBuildAuthorizationError(f"{label} must be non-empty")
    if "\\" in value:
        raise FactoryBuildAuthorizationError(f"{label} must use forward-slash separators")
    parts = value.split("/")
    if value.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise FactoryBuildAuthorizationError(f"{label} must be a safe repository-relative path")
    if not value.startswith(prefix):
        raise FactoryBuildAuthorizationError(f"{label} must be under {prefix}")
    return value


def _repo_rel(path: str | Path, root: Path) -> str:
    resolved = Path(path).resolve()
    repo_root = root.resolve()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise FactoryBuildAuthorizationError(f"path is outside repository root: {path}") from exc


def validate_authorization_review(review: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "plugin_proposal_id",
        "source_contract_candidate",
        "source_handoff_receipt",
        "authorization",
    }
    missing = sorted(required - set(review))
    unknown = sorted(set(review) - required)
    if missing:
        raise FactoryBuildAuthorizationError(f"Build Authorization Review missing fields: {missing}")
    if unknown:
        raise FactoryBuildAuthorizationError(f"Build Authorization Review contains unknown fields: {unknown}")
    if review["schema_version"] != AUTHORIZATION_VERSION:
        raise FactoryBuildAuthorizationError("unsupported Build Authorization Review schema_version")
    if not isinstance(review["plugin_proposal_id"], str) or not review["plugin_proposal_id"].strip():
        raise FactoryBuildAuthorizationError("plugin_proposal_id must be non-empty")
    _safe_repo_rel(
        review["source_contract_candidate"],
        "source_contract_candidate",
        "research/incubator/factory_contracts/",
    )
    _safe_repo_rel(
        review["source_handoff_receipt"],
        "source_handoff_receipt",
        "research/incubator/factory_contracts/",
    )

    auth = review["authorization"]
    if not isinstance(auth, dict):
        raise FactoryBuildAuthorizationError("authorization must be an object")
    required_auth = {
        "authority",
        "approved_for_factory_build",
        "automatic_approval",
        "final_product_decision",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
    }
    missing_auth = sorted(required_auth - set(auth))
    unknown_auth = sorted(set(auth) - required_auth)
    if missing_auth:
        raise FactoryBuildAuthorizationError(f"authorization missing fields: {missing_auth}")
    if unknown_auth:
        raise FactoryBuildAuthorizationError(f"authorization contains unknown fields: {unknown_auth}")
    if auth["authority"] not in NON_AUTOMATION_AUTHORITIES:
        raise FactoryBuildAuthorizationError(
            "Factory Build Authorization authority must be HUMAN or ASSISTANT_REVIEW"
        )
    if auth["approved_for_factory_build"] is not True:
        raise FactoryBuildAuthorizationError("approved_for_factory_build must be true")
    for key in (
        "automatic_approval",
        "final_product_decision",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
    ):
        if auth[key] is not False:
            raise FactoryBuildAuthorizationError(f"authorization.{key} must be false")


def build_authorization(
    contract_candidate_path: str | Path,
    handoff_receipt_path: str | Path,
    authorization_review_path: str | Path,
    *,
    root: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    repo_root = Path(root).resolve()
    contract = _load_json(contract_candidate_path)
    receipt = _load_json(handoff_receipt_path)
    review = _load_yaml(authorization_review_path)

    validate_contract(contract)
    validate_receipt(receipt)
    verify_receipt_sources(receipt, root=repo_root)
    validate_authorization_review(review)

    if receipt["status"] != "CONTRACT_CANDIDATE":
        raise FactoryBuildAuthorizationError("handoff receipt must be a CONTRACT_CANDIDATE")
    if receipt["factory_build_authorized"] is not False:
        raise FactoryBuildAuthorizationError("handoff receipt must not already authorize a Factory build")
    if contract_sha256(contract) != receipt["contract_sha256"]:
        raise FactoryBuildAuthorizationError("contract candidate does not match handoff receipt")

    pid = receipt["plugin_proposal_id"]
    if review["plugin_proposal_id"] != pid:
        raise FactoryBuildAuthorizationError("Build Authorization Review does not match handoff receipt")

    contract_rel = _repo_rel(contract_candidate_path, repo_root)
    receipt_rel = _repo_rel(handoff_receipt_path, repo_root)
    if review["source_contract_candidate"] != contract_rel:
        raise FactoryBuildAuthorizationError("Build Authorization Review contract provenance mismatch")
    if review["source_handoff_receipt"] != receipt_rel:
        raise FactoryBuildAuthorizationError("Build Authorization Review receipt provenance mismatch")

    authorization: dict[str, Any] = {
        "schema_version": AUTHORIZATION_VERSION,
        "authorization_kind": "FACTORY_BUILD_AUTHORIZATION",
        "plugin_proposal_id": pid,
        "source_contract_candidate": contract_rel,
        "source_contract_candidate_sha256": _file_sha256(contract_candidate_path),
        "source_handoff_receipt": receipt_rel,
        "source_handoff_receipt_sha256": _file_sha256(handoff_receipt_path),
        "source_handoff_receipt_hash": receipt["receipt_hash"],
        "source_authorization_review": _repo_rel(authorization_review_path, repo_root),
        "source_authorization_review_sha256": _file_sha256(authorization_review_path),
        "contract_sha256": contract_sha256(contract),
        "authority": review["authorization"]["authority"],
        "status": "FACTORY_BUILD_AUTHORIZED",
        "automatic_final_decision": False,
        "factory_build_authorized": True,
        "product_release_authority": False,
        "cubase_confirmed": False,
        "listening_confirmed": False,
    }
    authorization["authorization_hash"] = _hash_payload(authorization, "authorization_hash")
    validate_authorization(authorization)
    return contract, authorization


def validate_authorization(authorization: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "authorization_kind",
        "plugin_proposal_id",
        "source_contract_candidate",
        "source_contract_candidate_sha256",
        "source_handoff_receipt",
        "source_handoff_receipt_sha256",
        "source_handoff_receipt_hash",
        "source_authorization_review",
        "source_authorization_review_sha256",
        "contract_sha256",
        "authority",
        "status",
        "automatic_final_decision",
        "factory_build_authorized",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
        "authorization_hash",
    }
    missing = sorted(required - set(authorization))
    unknown = sorted(set(authorization) - required)
    if missing:
        raise FactoryBuildAuthorizationError(f"Factory Build Authorization missing fields: {missing}")
    if unknown:
        raise FactoryBuildAuthorizationError(f"Factory Build Authorization contains unknown fields: {unknown}")
    if authorization["schema_version"] != AUTHORIZATION_VERSION:
        raise FactoryBuildAuthorizationError("unsupported Factory Build Authorization schema_version")
    if authorization["authorization_kind"] != "FACTORY_BUILD_AUTHORIZATION":
        raise FactoryBuildAuthorizationError("unexpected authorization_kind")
    if authorization["status"] != "FACTORY_BUILD_AUTHORIZED":
        raise FactoryBuildAuthorizationError("status must be FACTORY_BUILD_AUTHORIZED")
    if authorization["authority"] not in NON_AUTOMATION_AUTHORITIES:
        raise FactoryBuildAuthorizationError("authorization authority cannot be AUTOMATION")
    if authorization["automatic_final_decision"] is not False:
        raise FactoryBuildAuthorizationError("automatic_final_decision must be false")
    if authorization["factory_build_authorized"] is not True:
        raise FactoryBuildAuthorizationError("factory_build_authorized must be true")
    for key in (
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
    ):
        if authorization[key] is not False:
            raise FactoryBuildAuthorizationError(f"{key} must be false")

    _safe_repo_rel(
        authorization["source_contract_candidate"],
        "source_contract_candidate",
        "research/incubator/factory_contracts/",
    )
    _safe_repo_rel(
        authorization["source_handoff_receipt"],
        "source_handoff_receipt",
        "research/incubator/factory_contracts/",
    )
    _safe_repo_rel(
        authorization["source_authorization_review"],
        "source_authorization_review",
        "research/incubator/factory_build_authorizations/",
    )

    for key in (
        "source_contract_candidate_sha256",
        "source_handoff_receipt_sha256",
        "source_handoff_receipt_hash",
        "source_authorization_review_sha256",
        "contract_sha256",
        "authorization_hash",
    ):
        if not isinstance(authorization[key], str) or not _SHA256.fullmatch(authorization[key]):
            raise FactoryBuildAuthorizationError(f"{key} must be a lowercase SHA-256 digest")

    if not isinstance(authorization["plugin_proposal_id"], str) or not authorization["plugin_proposal_id"].strip():
        raise FactoryBuildAuthorizationError("plugin_proposal_id must be non-empty")
    if authorization["authorization_hash"] != _hash_payload(
        authorization, "authorization_hash"
    ):
        raise FactoryBuildAuthorizationError("authorization_hash mismatch")


def verify_authorization_sources(
    authorization: dict[str, Any],
    *,
    root: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_authorization(authorization)
    repo_root = Path(root).resolve()
    sources = (
        ("source_contract_candidate", "source_contract_candidate_sha256"),
        ("source_handoff_receipt", "source_handoff_receipt_sha256"),
        ("source_authorization_review", "source_authorization_review_sha256"),
    )
    for path_key, hash_key in sources:
        path = (repo_root / authorization[path_key]).resolve()
        try:
            path.relative_to(repo_root)
        except ValueError as exc:
            raise FactoryBuildAuthorizationError(f"{path_key} escapes repository root") from exc
        if not path.is_file():
            raise FactoryBuildAuthorizationError(f"{path_key} source is missing")
        if _file_sha256(path) != authorization[hash_key]:
            raise FactoryBuildAuthorizationError(f"{path_key} source hash mismatch")

    contract = _load_json(repo_root / authorization["source_contract_candidate"])
    receipt = _load_json(repo_root / authorization["source_handoff_receipt"])
    validate_contract(contract)
    validate_receipt(receipt)
    verify_receipt_sources(receipt, root=repo_root)
    if contract_sha256(contract) != authorization["contract_sha256"]:
        raise FactoryBuildAuthorizationError("authorized contract hash mismatch")
    if receipt["receipt_hash"] != authorization["source_handoff_receipt_hash"]:
        raise FactoryBuildAuthorizationError("authorized handoff receipt hash mismatch")
    if receipt["contract_sha256"] != authorization["contract_sha256"]:
        raise FactoryBuildAuthorizationError("handoff receipt contract does not match authorization")
    return contract, receipt


def write_authorized_build_request(
    contract: dict[str, Any],
    authorization: dict[str, Any],
    output_dir: str | Path,
) -> Path:
    validate_contract(contract)
    validate_authorization(authorization)
    if contract_sha256(contract) != authorization["contract_sha256"]:
        raise FactoryBuildAuthorizationError("contract does not match Factory Build Authorization")

    out = Path(output_dir)
    if out.exists() and any(out.iterdir()):
        raise FactoryBuildAuthorizationError(
            f"refusing to overwrite non-empty authorized build request: {out}"
        )
    out.mkdir(parents=True, exist_ok=True)
    (out / "plugin_contract.json").write_text(
        json.dumps(contract, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "factory_build_authorization.json").write_text(
        json.dumps(authorization, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(prog="cipi-factory-build-authorization")
    parser.add_argument("--contract-candidate", required=True)
    parser.add_argument("--handoff-receipt", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        contract, authorization = build_authorization(
            args.contract_candidate,
            args.handoff_receipt,
            args.review,
            root=args.root,
        )
        out = write_authorized_build_request(contract, authorization, args.output)
        print(json.dumps({
            "status": "FACTORY_BUILD_AUTHORIZED_REQUEST_WRITTEN",
            "path": str(out),
            "factory_build_authorized": True,
            "product_release_authority": False,
        }))
        return 0
    except (
        FactoryBuildAuthorizationError,
        FactoryHandoffError,
        ValueError,
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as exc:
        print(json.dumps({"status": "FACTORY_BUILD_AUTHORIZATION_ERROR", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
