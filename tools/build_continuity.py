from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.continuity.core import ContinuityError, build_all, validate_snapshot

def main() -> int:
    parser = argparse.ArgumentParser(description="Build CIPI continuity projections.")
    parser.add_argument("--project", help="Build one project id from the cross-repo registry.")
    parser.add_argument("--check-only", action="store_true", help="Build and validate in memory without publishing generated files.")
    parser.add_argument("--offline", action="store_true", help="Do not resolve product repository heads. Snapshots will be STALE.")
    args = parser.parse_args()
    token = os.environ.get("CIPI_CROSS_REPO_TOKEN") or os.environ.get("GH_TOKEN")
    resolver = None if args.offline else __import__("automation.continuity.core", fromlist=["resolve_remote_head"]).resolve_remote_head
    try:
        snapshots = build_all(ROOT, project_id=args.project, resolver=resolver, token=token, publish=not args.check_only)
    except ContinuityError as exc:
        print(f"CIPI continuity build: FAIL\n- {exc}")
        return 1
    failures=[]
    for project_id,snapshot in sorted(snapshots.items()):
        failures.extend(f"{project_id}: {error}" for error in validate_snapshot(snapshot,ROOT))
    if failures:
        print("CIPI continuity build: FAIL")
        for failure in failures: print(f"- {failure}")
        return 1
    counts={k:sum(1 for s in snapshots.values() if s["freshness"]==k) for k in ("FRESH","STALE","CONFLICT","INVALID")}
    mode="checked" if args.check_only else "published"
    print(f"CIPI continuity build: PASS ({mode}; projects={len(snapshots)} fresh={counts['FRESH']} stale={counts['STALE']} conflict={counts['CONFLICT']} invalid={counts['INVALID']})")
    return 0

if __name__=="__main__": sys.exit(main())
