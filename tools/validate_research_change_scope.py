from __future__ import annotations

import argparse
import subprocess

ALLOWED_PREFIXES = (
    "research/jobs/",
    "research/runs/",
    "research/reports/",
    "research/knowledge_candidates/",
    "research/decisions/",
)

APPEND_ONLY_PREFIXES = (
    "research/runs/",
    "research/reports/",
    "research/knowledge_candidates/",
    "research/decisions/",
    "research/jobs/completed/",
    "research/jobs/rejected/",
)

QUEUE_PREFIX = "research/jobs/queued/"

def allowed(path: str) -> bool:
    return path.startswith(ALLOWED_PREFIXES)

def append_only(path: str) -> bool:
    return path.startswith(APPEND_ONLY_PREFIXES)

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--head", required=True)
    args = p.parse_args()

    output = subprocess.check_output(
        ["git", "diff", "--name-status", "--find-renames", args.base, args.head],
        text=True,
    )
    errors = []
    changes = []

    for raw in output.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        paths = parts[1:]
        if not paths:
            errors.append(f"malformed diff status line: {raw}")
            continue
        source = paths[0]
        target = paths[-1]
        changes.append((status, source, target))

        for path in {source, target}:
            if not allowed(path):
                errors.append(f"forbidden worker path: {path}")

        code = status[0]

        if code in {"M", "D", "C"}:
            affected = target if code != "D" else source
            if append_only(affected):
                errors.append(f"append-only evidence may not be {status}: {affected}")

        if code == "R":
            if append_only(source):
                errors.append(f"append-only evidence may not be renamed: {source} -> {target}")
            queue_move = source.startswith(QUEUE_PREFIX) and (
                target.startswith("research/jobs/completed/")
                or target.startswith("research/jobs/rejected/")
            )
            if not queue_move:
                errors.append(f"worker rename is not an allowed queue finalization: {source} -> {target}")

        if target.startswith(QUEUE_PREFIX) and code == "M":
            errors.append(f"queued jobs may be added or consumed, but not modified in place: {target}")

        if source.startswith(QUEUE_PREFIX) and code == "D":
            pass

        if append_only(target) and code not in {"A", "R"}:
            if not (code == "D" and source.startswith(QUEUE_PREFIX)):
                errors.append(f"append-only target requires a new file: {status} {target}")

    if errors:
        print("CIPI worker path/integrity scope: FAIL")
        for error in sorted(set(errors)):
            print("-", error)
        return 1

    print(f"CIPI worker path/integrity scope: PASS ({len(changes)} change(s))")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
