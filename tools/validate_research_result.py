"""CIPI research-result integrity gate with legacy v1 and strict v2 envelopes.

v1 records remain readable for historical reproducibility. All new worker
results use v2 with complete SHA-256 coverage and canonical paths.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "schema_version", "job_id", "run_id", "source_commit", "worker_version",
    "started_at", "completed_at", "random_seed", "environment", "commands",
    "result", "acceptance_met", "rejection_triggered",
}
FORBIDDEN_EXT = {".wav", ".flac", ".mp3", ".aac", ".m4a", ".ogg", ".opus", ".pcm", ".raw"}
SECRET_PATTERNS = [
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def check_file_safety(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.exists():
        return errors
    for p in root.rglob("*"):
        if p.is_symlink():
            errors.append(f"{p}: symlinks forbidden in public research evidence")
            continue
        if not p.is_file():
            continue
        if p.suffix.lower() in FORBIDDEN_EXT:
            errors.append(f"{p}: raw/client audio-like extension is forbidden")
            continue
        if p.stat().st_size > 25 * 1024 * 1024:
            errors.append(f"{p}: file exceeds 25 MiB research evidence limit")
            continue
        payload = p.read_bytes()
        for pattern in SECRET_PATTERNS:
            if pattern.search(payload):
                errors.append(f"{p}: possible secret/private key detected")
                break
    return errors


def _canonical_member(value: str) -> bool:
    if not value or "\\" in value or value.startswith("/") or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and path.as_posix() == value and all(
        part not in {".", "..", ""} for part in value.split("/")
    )


def verify_checksums(run_dir: Path, name: str, *, strict: bool = False) -> list[str]:
    if name != "checksums.sha256":
        return [f"{run_dir}: checksums_file must name checksums.sha256"]
    path = run_dir / name
    if not path.is_file() or path.is_symlink():
        return [f"{run_dir}: missing or symlinked {name}"]
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not any(line.strip() for line in lines):
        errors.append(f"{path}: checksum manifest must not be empty")
    seen: set[str] = set()
    for line in lines:
        if not line.strip():
            errors.append(f"{path}: empty checksum line")
            continue
        try:
            digest, filename = line.split("  ", 1)
        except ValueError:
            errors.append(f"{path}: malformed checksum line")
            continue
        if not SHA256_RE.fullmatch(digest):
            errors.append(f"{path}: invalid SHA-256 digest")
            continue
        if not _canonical_member(filename) or filename == name:
            errors.append(f"{path}: unsafe checksum member path")
            continue
        if filename in seen:
            errors.append(f"{path}: duplicate checksum member {filename}")
            continue
        seen.add(filename)
        target = run_dir / filename
        if not target.is_file() or target.is_symlink():
            errors.append(f"{path}: missing or symlinked checksummed file {filename}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"{target}: SHA-256 mismatch")
    if strict:
        actual_files = {
            item.relative_to(run_dir).as_posix()
            for item in run_dir.rglob("*")
            if item.is_file() and item.name != name and not item.is_symlink()
        }
        missing = actual_files - seen
        extra = seen - actual_files
        if missing:
            errors.append(f"{path}: unchecksummed files: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"{path}: checksum references non-evidence files: {', '.join(sorted(extra))}")
        for item in run_dir.rglob("*"):
            if item.is_symlink():
                errors.append(f"{item}: symlink in evidence tree")
    return errors


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: JSON parse error: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: root must be object"]
    missing = sorted(REQUIRED - set(data))
    if missing:
        return [f"{path}: missing required keys: {', '.join(missing)}"]
    version = data["schema_version"]
    if version not in {"1.0", "2.0"}:
        errors.append(f"{path}: unsupported schema_version")
    if not re.fullmatch(r"[0-9a-f]{40}", str(data["source_commit"])):
        errors.append(f"{path}: source_commit must be a 40-char lowercase Git SHA")
    if data["result"] not in {"COMPLETED", "FAILED", "REJECTED"}:
        errors.append(f"{path}: invalid result")
    if not isinstance(data["acceptance_met"], bool) or not isinstance(data["rejection_triggered"], bool):
        errors.append(f"{path}: acceptance/rejection flags must be booleans")

    checks = data.get("checksums_file")
    if version == "2.0":
        if checks != "checksums.sha256":
            errors.append(f"{path}: v2 requires checksums_file=checksums.sha256")
        if str(data.get("job_id")) != path.parent.parent.name:
            errors.append(f"{path}: v2 job_id does not match parent evidence folder")
        if str(data.get("run_id")) != path.parent.name:
            errors.append(f"{path}: v2 run_id does not match evidence folder")
    if checks:
        errors += verify_checksums(path.parent, str(checks), strict=version == "2.0")
    return errors


def main() -> int:
    runs = ROOT / "research/runs"
    manifests = list(runs.rglob("manifest.json")) if runs.exists() else []
    errors = check_file_safety(runs)
    for path in manifests:
        errors += validate_manifest(path)
    if errors:
        print("CIPI research result gate: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print(f"CIPI research result gate: PASS ({len(manifests)} manifest(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
