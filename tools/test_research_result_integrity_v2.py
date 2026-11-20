from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from validate_research_result import validate_manifest, verify_checksums


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def create_v2(root: Path) -> Path:
    run = root / "JOB-001" / "RUN-001"
    run.mkdir(parents=True)
    files = {
        "metrics.json": '{"safety": true}\n',
        "environment.json": '{"python": "3.12"}\n',
        "parameters.json": '{}\n',
        "summary.md": '# Negative evidence must be retained\n',
    }
    manifest = {
        "schema_version": "2.0",
        "job_id": "JOB-001", "run_id": "RUN-001",
        "source_commit": "a" * 40, "worker_version": "test-v2",
        "started_at": "2026-11-20T00:00:00Z",
        "completed_at": "2026-11-20T00:00:01Z",
        "random_seed": 1, "environment": {}, "commands": [],
        "result": "REJECTED", "acceptance_met": False,
        "rejection_triggered": True,
        "checksums_file": "checksums.sha256",
    }
    files["manifest.json"] = json.dumps(manifest) + "\n"
    for name, value in files.items():
        (run / name).write_text(value, encoding="utf-8")
    (run / "checksums.sha256").write_text(
        "".join(f"{digest(value.encode('utf-8'))}  {name}\n" for name, value in sorted(files.items())),
        encoding="utf-8",
    )
    return run


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run = create_v2(root)
        assert validate_manifest(run / "manifest.json") == []
        original = (run / "checksums.sha256").read_text(encoding="utf-8")

        (run / "checksums.sha256").write_text("", encoding="utf-8")
        assert validate_manifest(run / "manifest.json"), "empty hash list wrongly accepted"
        (run / "checksums.sha256").write_text(original, encoding="utf-8")

        (run / "summary.md").write_text("modified", encoding="utf-8")
        assert any("mismatch" in e.lower() for e in validate_manifest(run / "manifest.json"))
        (run / "summary.md").write_text("# Negative evidence must be retained\n", encoding="utf-8")

        (run / "extra.log").write_text("unhashed extra evidence\n", encoding="utf-8")
        assert any("unchecksummed" in e for e in validate_manifest(run / "manifest.json"))
        (run / "extra.log").unlink()

        checksum_path = run / "checksums.sha256"
        checksum_path.write_text(original + f"{'f'*64}  ../escape.txt\n", encoding="utf-8")
        assert any("unsafe" in e.lower() for e in validate_manifest(run / "manifest.json"))
        checksum_path.write_text(original, encoding="utf-8")

        checksum_path.write_text(original + original.splitlines()[0] + "\n", encoding="utf-8")
        assert any("duplicate" in e.lower() for e in validate_manifest(run / "manifest.json"))
        checksum_path.write_text(original, encoding="utf-8")

        manifest_path = run / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["job_id"] = "WRONG-JOB"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        assert any("job_id" in e for e in validate_manifest(manifest_path))

        # Legacy v1 is still readable where the writer never included a hash.
        manifest["schema_version"] = "1.0"
        manifest["job_id"] = "JOB-001"
        manifest.pop("checksums_file")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        assert validate_manifest(manifest_path) == []
        assert verify_checksums(run, "checksums.sha256", strict=True), "changed legacy manifest must now mismatch"

    print("CIPI evidence v2 strict checksums: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
