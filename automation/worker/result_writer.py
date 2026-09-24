from __future__ import annotations

from pathlib import Path
import hashlib
import json

def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def write_checksums(directory: Path, names: list[str]) -> None:
    lines = []
    for name in sorted(names):
        payload = (directory / name).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        lines.append(f"{digest}  {name}")
    (directory / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
