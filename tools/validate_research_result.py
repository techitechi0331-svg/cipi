from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={
 "schema_version","job_id","run_id","source_commit","worker_version","started_at",
 "completed_at","random_seed","environment","commands","result","acceptance_met","rejection_triggered"
}
FORBIDDEN_EXT={".wav",".flac",".mp3",".aac",".m4a",".ogg",".opus",".pcm",".raw"}
SECRET_PATTERNS=[
 re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
 re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
 re.compile(rb"AKIA[0-9A-Z]{16}"),
 re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

def check_file_safety(root: Path) -> list[str]:
    errors=[]
    if not root.exists(): return errors
    for p in root.rglob("*"):
        if not p.is_file(): continue
        if p.suffix.lower() in FORBIDDEN_EXT:
            errors.append(f"{p}: raw/client audio-like extension is forbidden")
            continue
        if p.stat().st_size > 25*1024*1024:
            errors.append(f"{p}: file exceeds 25 MiB research evidence limit")
            continue
        payload=p.read_bytes()
        for pat in SECRET_PATTERNS:
            if pat.search(payload):
                errors.append(f"{p}: possible secret/private key detected")
                break
    return errors

def verify_checksums(run_dir: Path, name: str) -> list[str]:
    path=run_dir/name
    if not path.exists(): return [f"{run_dir}: missing {name}"]
    errors=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try:
            digest, filename=line.split("  ",1)
        except ValueError:
            errors.append(f"{path}: malformed checksum line")
            continue
        target=run_dir/filename
        if not target.exists():
            errors.append(f"{path}: missing checksummed file {filename}")
            continue
        actual=hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"{target}: SHA-256 mismatch")
    return errors

def validate_manual_sync_manifest(path: Path, data: dict) -> list[str]:
    errors=[]
    required={
        "schema_version","kind","track","source_repo","source_snapshot_sha",
        "measured_product_sha","source_ci_run","source_artifact_digest",
        "raw_audio_in_cipi","imported_files","note",
    }
    missing=sorted(required-set(data))
    if missing:
        return [f"{path}: manual sync missing required keys: {', '.join(missing)}"]
    if data.get("schema_version")!="1.0":
        errors.append(f"{path}: schema_version must be 1.0")
    if data.get("kind")!="manual_repository_evidence_sync":
        errors.append(f"{path}: invalid manual sync kind")
    for key in ("source_snapshot_sha","measured_product_sha"):
        if not re.fullmatch(r"[0-9a-f]{40}",str(data.get(key,""))):
            errors.append(f"{path}: {key} must be a 40-char lowercase Git SHA")
    if not isinstance(data.get("source_ci_run"),int) or data["source_ci_run"] < 1:
        errors.append(f"{path}: source_ci_run must be a positive integer")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}",str(data.get("source_artifact_digest",""))):
        errors.append(f"{path}: source_artifact_digest must be sha256:<64 lowercase hex>")
    if data.get("raw_audio_in_cipi") is not False:
        errors.append(f"{path}: manual sync may not declare raw audio in CIPI")
    imported=data.get("imported_files")
    if not isinstance(imported,list) or not imported or not all(isinstance(x,str) and x.strip() for x in imported):
        errors.append(f"{path}: imported_files must be a non-empty string list")
    if len(str(data.get("track","")).strip()) < 3:
        errors.append(f"{path}: track is too short")
    if len(str(data.get("source_repo","")).strip()) < 3:
        errors.append(f"{path}: source_repo is too short")
    if len(str(data.get("note","")).strip()) < 10:
        errors.append(f"{path}: note is too short")
    return errors


def validate_manifest(path: Path) -> list[str]:
    errors=[]
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: return [f"{path}: JSON parse error: {exc}"]
    if not isinstance(data,dict): return [f"{path}: root must be object"]
    if data.get("kind") == "manual_repository_evidence_sync":
        return validate_manual_sync_manifest(path, data)
    missing=sorted(REQUIRED-set(data))
    if missing: return [f"{path}: missing required keys: {', '.join(missing)}"]
    if data["schema_version"]!="1.0": errors.append(f"{path}: schema_version must be 1.0")
    if not re.fullmatch(r"[0-9a-f]{40}",str(data["source_commit"])):
        errors.append(f"{path}: source_commit must be a 40-char lowercase Git SHA")
    if data["result"] not in {"COMPLETED","FAILED","REJECTED"}:
        errors.append(f"{path}: invalid result")
    if not isinstance(data["acceptance_met"],bool) or not isinstance(data["rejection_triggered"],bool):
        errors.append(f"{path}: acceptance/rejection flags must be booleans")
    checks=data.get("checksums_file")
    if checks:
        errors += verify_checksums(path.parent,str(checks))
    return errors

def main() -> int:
    runs=ROOT/"research/runs"
    manifests=list(runs.rglob("manifest.json")) if runs.exists() else []
    errors=check_file_safety(runs)
    for path in manifests: errors += validate_manifest(path)
    if errors:
        print("CIPI research result gate: FAIL")
        for e in errors: print("-",e)
        return 1
    print(f"CIPI research result gate: PASS ({len(manifests)} manifest(s))")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
