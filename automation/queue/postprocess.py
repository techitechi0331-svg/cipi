from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

def safe_template_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    allowed = (ROOT / "automation" / "job_templates").resolve()
    if allowed not in path.parents:
        raise ValueError(f"continuation template must stay under automation/job_templates: {value}")
    return path

def safe_cross_repo_template_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    allowed = (ROOT / "automation" / "cross_repo" / "action_templates").resolve()
    if allowed not in path.parents:
        raise ValueError(f"cross-repo continuation template must stay under automation/cross_repo/action_templates: {value}")
    return path

def write_immutable_yaml(path: Path, payload: dict) -> None:
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing != text:
            raise FileExistsError(f"immutable record already exists with different content: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_decision_record(job: dict, manifest: dict) -> dict:
    job_id = str(job["job_id"])
    run_id = str(manifest["run_id"])
    rejected = bool(manifest.get("rejection_triggered"))
    context = job.get("rejection_record") if isinstance(job.get("rejection_record"), dict) else {}
    lineage = job.get("lineage") if isinstance(job.get("lineage"), dict) else {}
    gaps = []

    if rejected:
        reason = str(context.get("reason", "Declared rejection criteria were triggered; detailed rationale requires review."))
        if not manifest.get("triggered_criteria"):
            gaps.append("triggered_criteria_need_adapter_or_review")
        retained = context.get("retained_findings")
        if not isinstance(retained, list) or not retained:
            retained = ["All run artifacts, measurements, parameters, environment data and checksums are retained as negative evidence."]
            gaps.append("retained_findings_need_domain_review")
        reusable = context.get("reusable_findings")
        if not isinstance(reusable, list):
            reusable = []
            gaps.append("reusable_findings_need_domain_review")
        revisit_if = context.get("revisit_if")
        if not isinstance(revisit_if, list) or not revisit_if:
            revisit_if = ["New evidence, a changed model, or a changed baseline materially affects the failed criteria."]
            gaps.append("revisit_conditions_need_domain_review")
        scope = str(context.get("scope", f"Automated rejection evidence for {job_id}; final rejection requires review."))
        decision = "REJECT"
        rationale = reason
    else:
        retained = ["The complete accepted run evidence is retained; passing an experiment gate does not itself promote shared knowledge."]
        reusable = []
        revisit_if = []
        scope = f"Automated acceptance evidence for {job_id}; promotion requires review."
        decision = "ITERATE"
        rationale = "The declared acceptance gate passed. Automation records evidence but does not promote knowledge or finalize product decisions."

    normalized_lineage = {
        "supersedes": list(lineage.get("supersedes", [])) if isinstance(lineage.get("supersedes", []), list) else [],
        "related_jobs": list(lineage.get("related_jobs", [])) if isinstance(lineage.get("related_jobs", []), list) else [],
        "related_decisions": list(lineage.get("related_decisions", [])) if isinstance(lineage.get("related_decisions", []), list) else [],
    }

    return {
        "schema_version": "1.0",
        "decision_id": f"{job_id}:{run_id}:auto",
        "job_id": job_id,
        "source_run": f"research/runs/{job_id}/{run_id}",
        "event_type": "AUTOMATED_PROPOSAL",
        "authority": "AUTOMATION",
        "decision": decision,
        "review_status": "PENDING",
        "rationale": rationale,
        "scope": scope,
        "declared_rejection_criteria": list(job.get("rejection", [])),
        "triggered_criteria": list(manifest.get("triggered_criteria", [])),
        "retained_findings": retained,
        "reusable_findings": reusable,
        "revisit_if": revisit_if,
        "review_gaps": gaps,
        "lineage": normalized_lineage,
        "created_at": str(manifest.get("completed_at", "")),
        "immutable": True,
    }

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

    decision = build_decision_record(job, manifest)
    write_immutable_yaml(Path("research/decisions") / job_id / f"{run_id}-auto.yaml", decision)

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
        write_immutable_yaml(out / f"{run_id}.yaml", payload)

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

    cross_repo = job.get("cross_repo_continuation")
    if isinstance(cross_repo, dict):
        key = "on_accept" if bool(manifest.get("acceptance_met")) else "on_reject"
        templates = cross_repo.get(key, [])
        if templates is None:
            templates = []
        if not isinstance(templates, list):
            raise ValueError(f"cross_repo_continuation.{key} must be a list")
        queue = Path("research/cross_repo/actions/queued")
        queue.mkdir(parents=True, exist_ok=True)
        for value in templates:
            src = safe_cross_repo_template_path(str(value))
            if not src.is_file():
                raise FileNotFoundError(src)
            data = yaml.safe_load(src.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError(f"cross-repo action template must be a mapping: {src}")
            data["state"] = "QUEUED"
            dst = queue / src.name
            if dst.exists():
                existing = yaml.safe_load(dst.read_text(encoding="utf-8"))
                if existing != data:
                    raise FileExistsError(f"queued cross-repo action already exists with different content: {dst}")
                continue
            dst.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
