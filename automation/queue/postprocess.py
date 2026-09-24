from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import yaml

ROOT = Path(__file__).resolve().parents[2]

def safe_template_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    allowed = (ROOT / "automation" / "job_templates").resolve()
    if allowed not in path.parents:
        raise ValueError(f"continuation template must stay under automation/job_templates: {value}")
    return path

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--job", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()

    job_path = Path(args.job)
    run_dir = Path(args.run_dir)
    job = yaml.safe_load(job_path.read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    job_id = str(job["job_id"])
    run_id = str(manifest["run_id"])

    candidate = job.get("knowledge_candidate")
    if isinstance(candidate, dict):
        out = Path("research/knowledge_candidates") / job_id
        out.mkdir(parents=True, exist_ok=True)
        payload = {
            "claim": str(candidate["claim"]),
            "evidence_type": str(candidate["evidence_type"]),
            "scope": str(candidate["scope"]),
            "source_run": f"research/runs/{job_id}/{run_id}",
            "promotion_requested": str(candidate.get("promotion_requested", "HYPOTHESIS")),
        }
        (out / f"{run_id}.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    continuation = job.get("continuation")
    if isinstance(continuation, dict):
        key = "on_accept" if bool(manifest.get("acceptance_met")) else "on_reject"
        templates = continuation.get(key, [])
        if templates is None:
            templates = []
        if not isinstance(templates, list):
            raise ValueError(f"continuation.{key} must be a list")
        queue = Path("research/jobs/queued")
        queue.mkdir(parents=True, exist_ok=True)
        for value in templates:
            src = safe_template_path(str(value))
            if not src.is_file():
                raise FileNotFoundError(src)
            data = yaml.safe_load(src.read_text(encoding="utf-8"))
            data["state"] = "QUEUED"
            dst = queue / src.name
            if dst.exists():
                existing = yaml.safe_load(dst.read_text(encoding="utf-8"))
                if existing != data:
                    raise FileExistsError(f"queued continuation already exists with different content: {dst}")
                continue
            dst.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
