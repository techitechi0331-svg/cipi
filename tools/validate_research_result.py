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

def validate_manifest(path: Path) -> list[str]:
    errors=[]
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: return [f"{path}: JSON parse error: {exc}"]
    if not isinstance(data,dict): return [f"{path}: root must be object"]
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
