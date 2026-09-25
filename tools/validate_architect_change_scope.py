from __future__ import annotations

import argparse
import subprocess

ALLOWED_PREFIXES=(
 "research/architect/",
 "research/incubator/",
 "research/runs/ARCHITECT-",
 "research/knowledge_candidates/ARCHITECT-",
 "research/decisions/ARCHITECT-",
)

def allowed(path:str)->bool:
    return path.startswith(ALLOWED_PREFIXES)

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--base",required=True);p.add_argument("--head",required=True);args=p.parse_args()
    output=subprocess.check_output(["git","diff","--name-status","--find-renames",args.base,args.head],text=True)
    errors=[];count=0
    for raw in output.splitlines():
        if not raw.strip():continue
        parts=raw.split("\t");status=parts[0];paths=parts[1:];count+=1
        if not paths:
            errors.append(f"malformed diff line: {raw}");continue
        for path in paths:
            if not allowed(path):errors.append(f"forbidden architect-bot path: {path}")
        if status[0] != "A":
            errors.append(f"architect evidence is append-only; expected A, got {status}: {' -> '.join(paths)}")
    if errors:
        print("CIPI architect-bot scope: FAIL")
        for e in sorted(set(errors)):print("-",e)
        return 1
    print(f"CIPI architect-bot scope: PASS ({count} change(s))")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
