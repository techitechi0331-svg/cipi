from __future__ import annotations

import argparse
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

_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
EXPECTED_FILES = {
    "plugin_contract.json",
    "factory_build_authorization.json",
}


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
