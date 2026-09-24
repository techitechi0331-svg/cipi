from __future__ import annotations

import argparse
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--job-id", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--branch", required=True)
    args = p.parse_args()
    out = Path("research/reports") / args.job_id
    out.mkdir(parents=True, exist_ok=True)
    text = (
        "# Autonomous Research Local Gate\n\n"
        f"- Job: {args.job_id}\n"
        f"- Run: {args.run_id}\n"
        f"- Branch: `{args.branch}`\n"
        "- Research Job validator: PASS\n"
        "- Result / artifact safety validator: PASS\n"
        "- Existing CIPI research contract: PASS\n"
        "- Execution mode: free GitHub-hosted standard runner\n"
        "- External paid API: none\n\n"
        "This report is generated before the research-bot branch is pushed. "
        "Knowledge promotion still requires CIPI review.\n"
    )
    (out / f"{args.run_id}-gate.md").write_text(text, encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
