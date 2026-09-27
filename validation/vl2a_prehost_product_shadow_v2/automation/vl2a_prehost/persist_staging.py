from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

FILES = (
    "vl2a_lineamp_v01/Source/LA2AEngine.cpp",
    "vl2a_lineamp_v01/Source/LA2AEngine.h",
    "vl2a_lineamp_v01/Source/HA100XPreHostModel.h",
    "Research/17_PreHostHA100X/prehost_probe.cpp",
    "Research/17_PreHostHA100X/CMakeLists.txt",
    "Research/17_PreHostHA100X/candidate_manifest.json",
)

def safe_branch(candidate_id: str, run_id: str) -> str:
    if not re.fullmatch(r"HA100X-[A-Za-z0-9._-]{6,80}", candidate_id):
        raise ValueError("unsafe candidate_id")
    if not re.fullmatch(r"[0-9]{1,30}", run_id):
        raise ValueError("unsafe run_id")
    slug = re.sub(r"[^a-z0-9._-]+", "-", candidate_id.lower()).strip("-")
    return f"research/prehost/{slug}-{run_id}"

class GitHub:
    def __init__(self, repo: str, token: str):
        if not token:
            raise ValueError("GITHUB_TOKEN is required")
        self.repo = repo
        self.token = token

    def request(self, method: str, path: str, payload: dict | None = None):
        url = f"https://api.github.com/repos/{self.repo}/{path.lstrip('/')}"
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "vl2a-prehost-staging/1.0",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {detail}") from exc
        return json.loads(raw.decode("utf-8")) if raw else None

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--candidate-id", required=True)
    p.add_argument("--run-id", required=True)
    args = p.parse_args()

    root = Path(args.root).resolve()
    branch = safe_branch(args.candidate_id, args.run_id)
    gh = GitHub(args.repo, os.environ.get("GITHUB_TOKEN", ""))

    encoded_ref = urllib.parse.quote(args.source_ref, safe="")
    branch_info = gh.request("GET", f"branches/{encoded_ref}")
    source_sha = str(branch_info["commit"]["sha"])
    commit = gh.request("GET", f"git/commits/{source_sha}")
    base_tree = str(commit["tree"]["sha"])

    entries = []
    for relative in FILES:
        path = root / relative
        if not path.exists():
            raise FileNotFoundError(f"staging file missing: {relative}")
        blob = gh.request("POST", "git/blobs", {
            "content": path.read_text(encoding="utf-8"),
            "encoding": "utf-8",
        })
        entries.append({
            "path": relative,
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })

    tree = gh.request("POST", "git/trees", {
        "base_tree": base_tree,
        "tree": entries,
    })
    staged_commit = gh.request("POST", "git/commits", {
        "message": f"stage {args.candidate_id} for pre-host validation",
        "tree": tree["sha"],
        "parents": [source_sha],
    })
    gh.request("POST", "git/refs", {
        "ref": f"refs/heads/{branch}",
        "sha": staged_commit["sha"],
    })

    print(json.dumps({
        "branch": branch,
        "source_sha": source_sha,
        "staging_sha": staged_commit["sha"],
        "files": list(FILES),
    }, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
