from __future__ import annotations

import argparse
from pathlib import Path
import yaml

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--job", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--result", required=True, choices=["COMPLETED", "FAILED", "REJECTED"])
    args = p.parse_args()
    src = Path(args.job)
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    data["state"] = args.result
    data["latest_run"] = args.run_id
    folder = "completed" if args.result == "COMPLETED" else "rejected"
    dst = Path("research/jobs") / folder / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    src.unlink()
    print(dst)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
