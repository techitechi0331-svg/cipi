from __future__ import annotations

import hashlib
import io
from pathlib import Path, PurePosixPath
import re
from typing import Any
import zipfile
import yaml

TEXT_SUFFIXES = {".json", ".csv", ".md", ".txt", ".log", ".yaml", ".yml", ".xml"}
EVIDENCE_NAME_RE = re.compile(
    r"(measurement|metric|result|report|log|summary|validation|validator|reference|analysis|evidence|test|research)",
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
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "repository": repo,
        "repo_key": repo_key,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "artifact_id": artifact_id,
        "artifact_name": name,
        "expired": bool(artifact.get("expired")),
        "size_in_bytes": artifact.get("size_in_bytes"),
        "created_at": artifact.get("created_at"),
        "expires_at": artifact.get("expires_at"),
        "authority": "EXTERNAL_ARTIFACT_EVIDENCE_ONLY",
        "automatic_knowledge_promotion": False,
        "automatic_product_decision": False,
        "files": [],
    }

    if archive_bytes is None:
        manifest["ingest_status"] = "metadata_only"
    else:
        if len(archive_bytes) > MAX_ARCHIVE_BYTES:
            manifest["ingest_status"] = "archive_over_budget"
        else:
            manifest["archive_sha256"] = hashlib.sha256(archive_bytes).hexdigest()
            records, extracted = extract_text_evidence(archive_bytes)
            manifest["files"] = records
            manifest["ingest_status"] = "text_evidence_ingested"
            for relative, payload in extracted.items():
                target = base / "files" / Path(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)

    base.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return True
