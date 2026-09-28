from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from automation.continuity.core import validate_published

def main()->int:
    parser=argparse.ArgumentParser(description="Validate published CIPI continuity projections.")
    parser.add_argument("--project",help="Validate one project id.")
    args=parser.parse_args()
    errors=validate_published(ROOT,args.project)
    if errors:
        print("CIPI continuity validation: FAIL")
        for error in errors:print(f"- {error}")
        return 1
    print("CIPI continuity validation: PASS");return 0
if __name__=="__main__":sys.exit(main())
