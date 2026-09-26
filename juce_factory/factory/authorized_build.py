from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from automation.incubator.factory_build_authorization import (
    FactoryBuildAuthorizationError,
    validate_authorization,
    verify_authorization_sources,
)
from juce_factory.factory.contract import (
    ContractError,
    contract_sha256,
    validate_contract,
)
from juce_factory.factory.generator import generate_project
from juce_factory.factory.result_bundle import validate_result_bundle

_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
EXPECTED_FILES = {
    "plugin_contract.json",
    "factory_build_authorization.json",
}
_BINDING_VERSION = "1.0"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class AuthorizedBuildIntakeError(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuthorizedBuildIntakeError(f"{path} must contain a JSON object")
    return value


def _safe_request_dir(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    repo_root = root.resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise AuthorizedBuildIntakeError("request directory escapes repository root") from exc
    if path.is_symlink():
        raise AuthorizedBuildIntakeError(f"request directory must not be a symlink: {path}")
    if not path.is_dir():
        raise AuthorizedBuildIntakeError(f"request directory does not exist: {path}")
    if not _REQUEST_ID.fullmatch(path.name):
        raise AuthorizedBuildIntakeError(f"invalid request directory name: {path.name}")
    return resolved


def load_authorized_request(
    request_dir: str | Path,
    *,
    root: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    repo_root = Path(root).resolve()
    request = Path(request_dir)
    resolved = _safe_request_dir(request, repo_root)

    contract_path = resolved / "plugin_contract.json"
    authorization_path = resolved / "factory_build_authorization.json"
    for path in (contract_path, authorization_path):
        if path.is_symlink():
            raise AuthorizedBuildIntakeError(f"request file must not be a symlink: {path}")
        if not path.is_file():
            raise AuthorizedBuildIntakeError(f"authorized request is missing {path.name}")

    unexpected = sorted(
        entry.name
        for entry in resolved.iterdir()
        if entry.is_file() and entry.name not in EXPECTED_FILES
    )
    if unexpected:
        raise AuthorizedBuildIntakeError(
            f"authorized request contains unexpected files: {unexpected}"
        )

    contract = _load_json(contract_path)
    authorization = _load_json(authorization_path)
    validate_contract(contract)
    validate_authorization(authorization)
    verify_authorization_sources(authorization, root=repo_root)

    semantic_hash = contract_sha256(contract)
    if semantic_hash != authorization["contract_sha256"]:
        raise AuthorizedBuildIntakeError(
            "request Plugin Contract does not match Factory Build Authorization"
        )
    if authorization["factory_build_authorized"] is not True:
        raise AuthorizedBuildIntakeError("Factory Build Authorization is not active")
    if authorization["product_release_authority"] is not False:
        raise AuthorizedBuildIntakeError(
            "authorized build request must not carry product release authority"
        )
    if authorization["cubase_confirmed"] is not False:
        raise AuthorizedBuildIntakeError(
            "authorized build request must not claim Cubase confirmation"
        )
    if authorization["listening_confirmed"] is not False:
        raise AuthorizedBuildIntakeError(
            "authorized build request must not claim listening confirmation"
        )

    return contract, authorization


def discover_authorized_requests(
    *,
    root: str | Path,
    requests_root: str | Path = "research/incubator/factory_build_requests",
) -> list[dict[str, Any]]:
    repo_root = Path(root).resolve()
    base = (repo_root / requests_root).resolve()
    try:
        base.relative_to(repo_root)
    except ValueError as exc:
        raise AuthorizedBuildIntakeError("requests root escapes repository root") from exc

    if not base.exists():
        return []
    if base.is_symlink() or not base.is_dir():
        raise AuthorizedBuildIntakeError("requests root must be a real directory")

    records: list[dict[str, Any]] = []
    seen_plugin_ids: set[str] = set()
    seen_bundle_ids: set[str] = set()
    seen_codes: set[tuple[str, str]] = set()

    for request_dir in sorted(
        (entry for entry in base.iterdir() if entry.is_dir()),
        key=lambda value: value.name,
    ):
        contract, authorization = load_authorized_request(request_dir, root=repo_root)
        plugin = contract["plugin"]
        plugin_id = plugin["id"]
        bundle_id = plugin["bundle_id"]
        code_key = (plugin["manufacturer_code"], plugin["plugin_code"])

        if plugin_id in seen_plugin_ids:
            raise AuthorizedBuildIntakeError(
                f"duplicate plugin.id across authorized requests: {plugin_id}"
            )
        if bundle_id in seen_bundle_ids:
            raise AuthorizedBuildIntakeError(
                f"duplicate plugin.bundle_id across authorized requests: {bundle_id}"
            )
        if code_key in seen_codes:
            raise AuthorizedBuildIntakeError(
                "duplicate manufacturer/plugin code across authorized requests: "
                f"{code_key[0]}/{code_key[1]}"
            )

        seen_plugin_ids.add(plugin_id)
        seen_bundle_ids.add(bundle_id)
        seen_codes.add(code_key)
        records.append(
            {
                "request_id": request_dir.name,
                "request_path": request_dir.relative_to(repo_root).as_posix(),
                "plugin_id": plugin_id,
                "plugin_name": plugin["name"],
                "plugin_version": plugin["version"],
                "bundle_id": bundle_id,
                "contract_sha256": authorization["contract_sha256"],
                "authorization_hash": authorization["authorization_hash"],
            }
        )

    return records



def _canonical_json(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _binding_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("binding_hash", None)
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def validate_result_binding(binding: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "binding_kind",
        "request_id",
        "plugin_id",
        "plugin_version",
        "contract_sha256",
        "authorization_hash",
        "authorization_authority",
        "factory_result_bundle_hash",
        "factory_status",
        "automatic_final_decision",
        "factory_build_authorized",
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
        "binding_hash",
    }
    missing = sorted(required - set(binding))
    unknown = sorted(set(binding) - required)
    if missing:
        raise AuthorizedBuildIntakeError(f"result binding missing fields: {missing}")
    if unknown:
        raise AuthorizedBuildIntakeError(f"result binding contains unknown fields: {unknown}")
    if binding["schema_version"] != _BINDING_VERSION:
        raise AuthorizedBuildIntakeError("unsupported result binding schema_version")
    if binding["binding_kind"] != "AUTHORIZED_FACTORY_BUILD_RESULT":
        raise AuthorizedBuildIntakeError("unexpected result binding kind")
    if not isinstance(binding["request_id"], str) or not _REQUEST_ID.fullmatch(binding["request_id"]):
        raise AuthorizedBuildIntakeError("invalid result binding request_id")
    for key in ("plugin_id", "plugin_version"):
        if not isinstance(binding[key], str) or not binding[key].strip():
            raise AuthorizedBuildIntakeError(f"{key} must be non-empty")
    for key in (
        "contract_sha256",
        "authorization_hash",
        "factory_result_bundle_hash",
        "binding_hash",
    ):
        if not isinstance(binding[key], str) or not _SHA256.fullmatch(binding[key]):
            raise AuthorizedBuildIntakeError(f"{key} must be a lowercase SHA-256 digest")
    if binding["authorization_authority"] not in {"HUMAN", "ASSISTANT_REVIEW"}:
        raise AuthorizedBuildIntakeError("authorization_authority cannot be AUTOMATION")
    if binding["factory_status"] not in {"VALIDATION_PASS", "QUARANTINED"}:
        raise AuthorizedBuildIntakeError("invalid factory_status in result binding")
    if binding["automatic_final_decision"] is not False:
        raise AuthorizedBuildIntakeError("automatic_final_decision must be false")
    if binding["factory_build_authorized"] is not True:
        raise AuthorizedBuildIntakeError("factory_build_authorized must be true")
    for key in (
        "product_release_authority",
        "cubase_confirmed",
        "listening_confirmed",
    ):
        if binding[key] is not False:
            raise AuthorizedBuildIntakeError(f"{key} must be false")
    if binding["binding_hash"] != _binding_hash(binding):
        raise AuthorizedBuildIntakeError("result binding hash mismatch")


def bind_factory_result(
    request_dir: str | Path,
    factory_result_bundle_path: str | Path,
    *,
    root: str | Path,
) -> dict[str, Any]:
    request = Path(request_dir)
    contract, authorization = load_authorized_request(request, root=root)
    bundle = _load_json(Path(factory_result_bundle_path))
    validate_result_bundle(bundle)

    semantic_hash = contract_sha256(contract)
    if bundle["contract_sha256"] != semantic_hash:
        raise AuthorizedBuildIntakeError(
            "Factory Result Bundle Contract does not match authorized request"
        )
    if bundle["plugin_id"] != contract["plugin"]["id"]:
        raise AuthorizedBuildIntakeError(
            "Factory Result Bundle plugin_id does not match authorized request"
        )
    if bundle["plugin_version"] != contract["plugin"]["version"]:
        raise AuthorizedBuildIntakeError(
            "Factory Result Bundle plugin_version does not match authorized request"
        )

    binding: dict[str, Any] = {
        "schema_version": _BINDING_VERSION,
        "binding_kind": "AUTHORIZED_FACTORY_BUILD_RESULT",
        "request_id": request.name,
        "plugin_id": contract["plugin"]["id"],
        "plugin_version": contract["plugin"]["version"],
        "contract_sha256": semantic_hash,
        "authorization_hash": authorization["authorization_hash"],
        "authorization_authority": authorization["authority"],
        "factory_result_bundle_hash": bundle["bundle_hash"],
        "factory_status": bundle["factory_status"],
        "automatic_final_decision": False,
        "factory_build_authorized": True,
        "product_release_authority": False,
        "cubase_confirmed": False,
        "listening_confirmed": False,
    }
    binding["binding_hash"] = _binding_hash(binding)
    validate_result_binding(binding)
    return binding


def write_result_binding(path: str | Path, binding: dict[str, Any]) -> None:
    validate_result_binding(binding)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(binding, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

def generate_authorized_project(
    request_dir: str | Path,
    output_dir: str | Path,
    *,
    root: str | Path,
) -> Path:
    contract, authorization = load_authorized_request(request_dir, root=root)
    if contract_sha256(contract) != authorization["contract_sha256"]:
        raise AuthorizedBuildIntakeError("authorized Contract changed before generation")
    return generate_project(contract, output_dir)


def main() -> int:
    parser = argparse.ArgumentParser(prog="juce-factory-authorized-build")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate one authorized Factory build request")
    validate.add_argument("--request", required=True)
    validate.add_argument("--root", default=".")

    discover = sub.add_parser("discover", help="discover all authorized Factory build requests")
    discover.add_argument("--root", default=".")
    discover.add_argument(
        "--requests-root",
        default="research/incubator/factory_build_requests",
    )
    discover.add_argument("--matrix", action="store_true")

    generate = sub.add_parser("generate", help="generate JUCE project from an authorized request")
    generate.add_argument("--request", required=True)
    generate.add_argument("--root", default=".")
    generate.add_argument("--output", required=True)

    bind = sub.add_parser("bind-result", help="bind a Factory Result Bundle to its build authorization")
    bind.add_argument("--request", required=True)
    bind.add_argument("--bundle", required=True)
    bind.add_argument("--root", default=".")
    bind.add_argument("--output", required=True)

    args = parser.parse_args()
    try:
        if args.command == "validate":
            contract, authorization = load_authorized_request(
                args.request,
                root=args.root,
            )
            print(json.dumps({
                "status": "AUTHORIZED_BUILD_REQUEST_VALID",
                "plugin_id": contract["plugin"]["id"],
                "contract_sha256": authorization["contract_sha256"],
                "factory_build_authorized": True,
                "product_release_authority": False,
            }))
            return 0

        if args.command == "discover":
            records = discover_authorized_requests(
                root=args.root,
                requests_root=args.requests_root,
            )
            if args.matrix:
                print(json.dumps({"include": records}, separators=(",", ":")))
            else:
                print(json.dumps({
                    "status": "AUTHORIZED_BUILD_REQUEST_DISCOVERY_PASS",
                    "count": len(records),
                    "requests": records,
                }))
            return 0

        if args.command == "generate":
            out = generate_authorized_project(
                args.request,
                args.output,
                root=args.root,
            )
            print(json.dumps({
                "status": "AUTHORIZED_FACTORY_PROJECT_GENERATED",
                "output": str(out),
            }))
            return 0

        if args.command == "bind-result":
            binding = bind_factory_result(
                args.request,
                args.bundle,
                root=args.root,
            )
            write_result_binding(args.output, binding)
            print(json.dumps({
                "status": "AUTHORIZED_FACTORY_RESULT_BOUND",
                "binding_hash": binding["binding_hash"],
                "factory_status": binding["factory_status"],
                "product_release_authority": False,
            }))
            return 0
    except (
        AuthorizedBuildIntakeError,
        FactoryBuildAuthorizationError,
        ContractError,
        FileExistsError,
        ValueError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        print(json.dumps({
            "status": "AUTHORIZED_BUILD_INTAKE_ERROR",
            "error": str(exc),
        }))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
