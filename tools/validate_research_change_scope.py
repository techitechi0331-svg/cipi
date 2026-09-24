from __future__ import annotations

import argparse
import subprocess
import sys

ALLOWED=(
 "research/jobs/",
 "research/runs/",
 "research/reports/",
 "research/knowledge_candidates/",
)

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--base",required=True)
    p.add_argument("--head",required=True)
    args=p.parse_args()
    output=subprocess.check_output(["git","diff","--name-only",args.base,args.head],text=True)
    paths=[x.strip() for x in output.splitlines() if x.strip()]
    bad=[x for x in paths if not x.startswith(ALLOWED)]
    if bad:
        print("CIPI worker path scope: FAIL")
        for path in bad: print("-",path)
        return 1
    print(f"CIPI worker path scope: PASS ({len(paths)} changed path(s))")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
