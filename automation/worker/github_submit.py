from __future__ import annotations

import argparse
import os
import re
import subprocess

BRANCH_RE = re.compile(r"^research-bot/[A-Z0-9][A-Z0-9._-]{2,95}/[A-Za-z0-9._-]+$")

def run(*args: str) -> None:
    subprocess.run(args, check=True)

def main() -> int:
    parser = argparse.ArgumentParser(description="Submit an already-generated research run as a PR.")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", default="Automated research evidence submission. No knowledge promotion requested.")
    args = parser.parse_args()

    if not BRANCH_RE.fullmatch(args.branch):
        raise SystemExit("branch must match research-bot/<JOB-ID>/<run-id>")
    if not os.getenv("GH_TOKEN"):
        raise SystemExit("GH_TOKEN is required; use a least-privilege token or GitHub App token")

    run("git", "checkout", "-b", args.branch)
    run("git", "add", "research/jobs", "research/runs", "research/reports", "research/knowledge_candidates")
    run("git", "commit", "-m", f"submit autonomous research evidence: {args.branch}")
    run("git", "push", "--set-upstream", "origin", args.branch)
    run("gh", "pr", "create", "--base", "main", "--head", args.branch, "--title", args.title, "--body", args.body)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
