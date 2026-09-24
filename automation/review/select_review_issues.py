from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TITLE_RE = re.compile(r"^Autonomous research ready:\s*(\S+)\s*$")
BRANCH_RE = re.compile(r"(research-bot/[A-Z0-9._-]+/[^\s]+)")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--issues-json", required=True)
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--github-output", required=True)
    args = p.parse_args()

    issues = json.loads(Path(args.issues_json).read_text(encoding="utf-8"))
    matrix = []
    for item in issues:
        title = str(item.get("title", ""))
        m = TITLE_RE.match(title)
        if not m:
            continue
        labels = {str(x.get("name", "")) for x in item.get("labels", []) if isinstance(x, dict)}
        if "cipi-triaged" in labels:
            continue
        body = str(item.get("body", "") or "")
        branch_match = BRANCH_RE.search(body)
        matrix.append({
            "issue_number": int(item["number"]),
            "job_id": m.group(1),
            "branch": branch_match.group(1).rstrip(".,)") if branch_match else "",
        })
        if len(matrix) >= max(1, args.limit):
            break

    with Path(args.github_output).open("a", encoding="utf-8") as fh:
        fh.write("has_items=" + ("true" if matrix else "false") + "\n")
        fh.write("matrix=" + json.dumps(matrix, separators=(",", ":")) + "\n")
    print(json.dumps(matrix, indent=2))

if __name__ == "__main__":
    raise SystemExit(main())
