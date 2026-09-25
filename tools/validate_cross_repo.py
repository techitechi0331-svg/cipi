from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "cross_repo"))

from core import load_registry, load_yaml, validate_action  # noqa: E402


def main() -> int:
    errors: list[str] = []
    try:
        registry = load_registry(ROOT / "automation" / "cross_repo" / "registry.yaml")
    except Exception as exc:
        print(f"CIPI cross-repo gate: FAIL\n- registry: {exc}")
        return 1

    base = ROOT / "research" / "cross_repo" / "actions"
    states = {"queued": "QUEUED", "dispatched": "DISPATCHED", "completed": "COMPLETED", "failed": "FAILED", "quarantined": "QUARANTINED"}
    count = 0
    for folder, expected in states.items():
        root = base / folder
        if not root.exists():
            continue
        for path in sorted(root.glob("*.yaml")):
            count += 1
            try:
                action = load_yaml(path)
            except Exception as exc:
                errors.append(f"{path}: {exc}")
                continue
            if action.get("state") != expected:
                errors.append(f"{path}: expected state {expected}, got {action.get('state')!r}")
            for error in validate_action(action, registry):
                errors.append(f"{path}: {error}")

    if errors:
        print("CIPI cross-repo gate: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print(f"CIPI cross-repo gate: PASS ({count} action file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
