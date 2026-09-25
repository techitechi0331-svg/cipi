from __future__ import annotations

import ast
import inspect
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.worker import experiments


def registry_adapters() -> set[str]:
    path = ROOT / "automation" / "adapter_registry.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("adapters"), dict):
        raise AssertionError("adapter_registry.yaml must contain an adapters mapping")
    return set(data["adapters"])


def dispatched_adapters() -> set[str]:
    source = inspect.getsource(experiments.run_adapter)
    tree = ast.parse(source)
    found: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
            continue
        if not isinstance(node.left, ast.Name) or node.left.id != "name":
            continue
        if len(node.comparators) != 1:
            continue
        value = node.comparators[0]
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            found.add(value.value)

    return found


def main() -> int:
    registry = registry_adapters()
    allowlisted = set(experiments.ADAPTERS)
    dispatched = dispatched_adapters()

    problems: list[str] = []

    missing_worker = sorted(registry - allowlisted)
    extra_worker = sorted(allowlisted - registry)
    missing_dispatch = sorted(allowlisted - dispatched)
    extra_dispatch = sorted(dispatched - allowlisted)

    if missing_worker:
        problems.append(
            "registry adapter(s) missing from worker ADAPTERS: "
            + ", ".join(missing_worker)
        )
    if extra_worker:
        problems.append(
            "worker ADAPTERS missing from registry: "
            + ", ".join(extra_worker)
        )
    if missing_dispatch:
        problems.append(
            "allowlisted adapter(s) missing run_adapter dispatch: "
            + ", ".join(missing_dispatch)
        )
    if extra_dispatch:
        problems.append(
            "run_adapter dispatch not present in ADAPTERS: "
            + ", ".join(extra_dispatch)
        )

    if problems:
        print("CIPI adapter registry/worker sync: FAIL")
        for problem in problems:
            print("-", problem)
        return 1

    print(
        "CIPI adapter registry/worker sync: PASS "
        f"({len(registry)} adapter(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
