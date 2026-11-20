from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
from typing import Any
import zipfile
import yaml

TEXT_SUFFIXES = {".json", ".csv", ".md", ".txt", ".log", ".yaml", ".yml", ".xml"}
EVIDENCE_NAME_RE = re.compile(
    r"(measurement|metric|result|report|log|summary|baseline|validation|validator|reference|analysis|evidence|test|research)",
    re.IGNORECASE,
)
MAX_ARCHIVE_BYTES = 50 * 1024 * 1024
MAX_MEMBER_BYTES = 2 * 1024 * 1024
MAX_TOTAL_TEXT_BYTES = 10 * 1024 * 1024


def should_download_text_artifact(name: str) -> bool:
    return bool(EVIDENCE_NAME_RE.search(name))


def safe_member(name: str) -> PurePosixPath | None:
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts:
        return None
    if p.suffix.lower() not in TEXT_SUFFIXES:
        return None
    return p


def extract_text_evidence(data: bytes) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    records: list[dict[str, Any]] = []
    extracted: dict[str, bytes] = {}
    total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            member = safe_member(info.filename)
            if member is None:
                continue
            if info.file_size > MAX_MEMBER_BYTES:
                records.append({
                    "path": info.filename,
                    "status": "skipped_too_large",
                    "size": info.file_size,
                })
                continue
            if total + info.file_size > MAX_TOTAL_TEXT_BYTES:
                records.append({
                    "path": info.filename,
                    "status": "skipped_total_budget",
                    "size": info.file_size,
                })
                continue
            payload = zf.read(info)
            total += len(payload)
            digest = hashlib.sha256(payload).hexdigest()
            key = member.as_posix()
            extracted[key] = payload
            records.append({
                "path": key,
                "status": "ingested",
                "size": len(payload),
                "sha256": digest,
            })
    return records, extracted



# A public CIPI must never mirror arbitrary text from private VST3 repos.
# Only a narrowly typed scientific summary from MELON is allowed across this
# boundary; the full source bundle stays private.
PUBLIC_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
PUBLIC_ENUM = re.compile(r"^[A-Z][A-Z0-9_]{0,79}$")
PUBLIC_TIME = re.compile(r"^[0-9TZ:+.-]{10,48}$")


def _public_id(value: Any, field: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not PUBLIC_ID.fullmatch(value):
        raise ValueError(f"invalid public identifier for {field}")
    return value


def _public_enum(value: Any, field: str) -> str:
    if not isinstance(value, str) or not PUBLIC_ENUM.fullmatch(value):
        raise ValueError(f"invalid public enum for {field}")
    return value


def _public_number(value: Any, field: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"invalid public finite number for {field}")
    return value


def project_public_melon_macro(source: bytes) -> bytes:
    """Return a minimal, nonverbatim summary, never private raw text.

    Untrusted descriptive strings, candidate inputs and arbitrary result
    objects are excluded. Public summaries cannot authorize an automatic
    continuation or a human promotion. Source hash ties a public summary to
    the private bundle for separately authorized inspection.
    """
    if len(source) > MAX_MEMBER_BYTES:
        raise ValueError("private macro result exceeds per-file limit")
    data = json.loads(source.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("private macro result must be an object")
    if data.get("schema_version") != "1.0" or data.get("result_type") != "MELON_MACRO_RESEARCH_RESULT":
        raise ValueError("unexpected macro schema/result type")
    if data.get("evidence_class") != "MEASURED":
        raise ValueError("unsupported evidence class")
    if any(data.get(field) is not False for field in (
        "automatic_final_decision", "cipi_promotion_authority", "product_release_authority"
    )):
        raise ValueError("private source attempted automated authority escalation")

    identifiers = (
        "track_id", "run_id", "job_id", "root_research_id", "research_id",
        "hypothesis_id", "experiment_id",
    )
    result: dict[str, Any] = {
        "schema_version": "1.0",
        "result_type": "MELON_MACRO_RESEARCH_RESULT",
        "evidence_class": "MEASURED",
        "automatic_final_decision": False,
        "cipi_promotion_authority": False,
        "product_release_authority": False,
        "parent_run_id": _public_id(data.get("parent_run_id"), "parent_run_id", nullable=True),
        "parent_job_id": _public_id(data.get("parent_job_id"), "parent_job_id", nullable=True),
        "public_projection": "BOUNDED_REDACTED_PRIVATE_EVIDENCE",
        "private_source_sha256": hashlib.sha256(source).hexdigest(),
        "reason": "Private evidence requires authorized source review; this is a public metrics-only summary.",
        "unresolved_questions": [],
        "continuation_candidates": [],
        "source_commit": data.get("source_commit"),
    }
    for field in identifiers:
        result[field] = _public_id(data.get(field), field)
    if not isinstance(result["source_commit"], str) or not re.fullmatch(r"[0-9a-f]{40}", result["source_commit"]):
        raise ValueError("source_commit is not a 40-character lowercase SHA")
    if not isinstance(data.get("timestamp"), str) or not PUBLIC_TIME.fullmatch(data["timestamp"]):
        raise ValueError("invalid public timestamp")
    result["timestamp"] = data["timestamp"]
    depth = data.get("loop_depth")
    if type(depth) is not int or depth < 1:
        raise ValueError("invalid loop_depth")
    result["loop_depth"] = depth
    route = _public_enum(data.get("route"), "route")
    if route not in {"CONTINUE", "HUMAN_GATE", "STOP"}:
        raise ValueError("invalid route")
    # The private candidate inputs have not been approved for publication.
    # Never silently synthesize runnable continuation candidates.
    result["route"] = "HUMAN_GATE" if route == "CONTINUE" else route
    result["source_route"] = route
    result["regression_status"] = _public_enum(data.get("regression_status"), "regression_status")
    result["stop_reason"] = _public_enum(data.get("stop_reason"), "stop_reason")
    for field in ("confidence", "novelty", "elapsed_seconds", "measured_candidates"):
        result[field] = _public_number(data.get(field), field)
    raw_cost = data.get("experiment_cost")
    raw_result = data.get("result")
    if not isinstance(raw_cost, dict) or not isinstance(raw_result, dict):
        raise ValueError("invalid public experiment cost/result")
    result["experiment_cost"] = {
        field: _public_number(raw_cost.get(field), field)
        for field in ("candidates", "deep_validation_count", "runtime_seconds", "stage2_measurement_runs")
    }
    result["result"] = {
        "improvement_signal": _public_number(raw_result.get("improvement_signal"), "improvement_signal"),
        "deep_validation_count": _public_number(raw_result.get("deep_validation_count"), "deep_validation_count"),
        "precision_review_passed": raw_result.get("precision_review_passed") is True,
    }
    unhashed = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    result["bundle_hash"] = hashlib.sha256(unhashed.encode("utf-8")).hexdigest()
    return (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def extract_public_melon_evidence(data: bytes) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    """Only macro_result.json may cross the private -> public boundary."""
    records: list[dict[str, Any]] = []
    extracted: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        candidates = [
            info for info in zf.infolist()
            if not info.is_dir() and PurePosixPath(info.filename).name == "macro_result.json"
            and safe_member(info.filename) is not None
            and (info.external_attr >> 16 & 0o170000) != 0o120000
        ]
        if len(candidates) != 1:
            raise ValueError("expected exactly one safe private macro_result.json")
        info = candidates[0]
        if info.file_size > MAX_MEMBER_BYTES:
            raise ValueError("private macro_result.json exceeds budget")
        original = zf.read(info)
        projected = project_public_melon_macro(original)
        relative = PurePosixPath(info.filename).as_posix()
        extracted[relative] = projected
        records.append({
            "path": relative,
            "status": "sanitized_public_projection",
            "sha256": hashlib.sha256(projected).hexdigest(),
            "source_sha256": hashlib.sha256(original).hexdigest(),
            "size": len(projected),
        })
    return records, extracted

def ingest_artifact(
    root: Path,
    *,
    repo_key: str,
    repo: str,
    run_id: int,
    run_attempt: int,
    artifact: dict[str, Any],
    archive_bytes: bytes | None,
) -> bool:
    artifact_id = artifact.get("id")
    if artifact_id is None:
        return False
    base = root / "research" / "cross_repo" / "artifacts" / repo_key / str(run_id) / str(artifact_id)
    manifest_path = base / "manifest.yaml"
    if manifest_path.exists():
        return False

    name = str(artifact.get("name") or "")
    private_source = repo_key != "cipi"
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "repository": repo,
        "repo_key": repo_key,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "artifact_id": artifact_id,
        "artifact_name": "PRIVATE_ARTIFACT_REDACTED" if private_source else name,
        "artifact_name_sha256": hashlib.sha256(name.encode("utf-8")).hexdigest() if private_source else None,
        "privacy_boundary": "PRIVATE_SOURCE_METADATA_ONLY" if private_source else "CIPI_OWN_REPOSITORY",
        "expired": bool(artifact.get("expired")),
        "size_in_bytes": artifact.get("size_in_bytes"),
        "created_at": artifact.get("created_at"),
        "expires_at": artifact.get("expires_at"),
        "authority": "EXTERNAL_ARTIFACT_EVIDENCE_ONLY",
        "automatic_knowledge_promotion": False,
        "automatic_product_decision": False,
        "files": [],
    }

    if archive_bytes is None or (private_source and repo_key != "melon"):
        manifest["ingest_status"] = "private_metadata_only" if private_source else "metadata_only"
    elif len(archive_bytes) > MAX_ARCHIVE_BYTES:
        manifest["ingest_status"] = "archive_over_budget"
    else:
        manifest["archive_sha256"] = hashlib.sha256(archive_bytes).hexdigest()
        try:
            if repo_key == "melon":
                records, extracted = extract_public_melon_evidence(archive_bytes)
                manifest["ingest_status"] = "private_redacted_public_metrics_only"
            else:
                records, extracted = extract_text_evidence(archive_bytes)
                manifest["ingest_status"] = "text_evidence_ingested"
        except (ValueError, UnicodeError, json.JSONDecodeError, zipfile.BadZipFile, RuntimeError):
            records, extracted = [], {}
            manifest["ingest_status"] = "private_evidence_quarantined"
        manifest["files"] = records
        for relative, payload in extracted.items():
            target = base / "files" / Path(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

    base.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return True
