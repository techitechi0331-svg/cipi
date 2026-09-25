from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

ROUTES = {"REJECTION_REVIEW", "PROMOTION_REVIEW", "CONTINUE_RESEARCH", "HUMAN_GATE_REVIEW", "DONE"}
CANDIDATES = {"REJECT_CANDIDATE", "PROMOTION_CANDIDATE", "RESEARCH_MORE", "ALREADY_REVIEWED"}
PROMOTION_LEVELS = {"LIKELY", "PROVISIONAL"}

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def find_job(root: Path, job_id: str):
    candidates = []
    base = root / "research" / "jobs"
    if base.exists():
        candidates.extend(list(base.rglob("*.yaml")) + list(base.rglob("*.yml")))
    examples = root / "automation" / "examples"
    if examples.exists():
        candidates.extend(list(examples.glob("*.yaml")) + list(examples.glob("*.yml")))
    for path in sorted(candidates):
        data = load_yaml(path)
        if isinstance(data, dict) and str(data.get("job_id")) == job_id:
            return path, data
    raise FileNotFoundError(f"research job not found for {job_id}")

def find_latest_run(root: Path, job_id: str, run_id: str | None):
    base = root / "research" / "runs" / job_id
    if run_id:
        manifest_path = base / run_id / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return run_id, manifest_path, manifest
    found = []
    if base.exists():
        for manifest_path in base.glob("*/manifest.json"):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            found.append((str(manifest.get("completed_at", "")), str(manifest.get("run_id", manifest_path.parent.name)), manifest_path, manifest))
    if not found:
        raise FileNotFoundError(f"research run not found for {job_id}")
    found.sort()
    _, resolved, manifest_path, manifest = found[-1]
    return resolved, manifest_path, manifest

def find_auto_decision(root: Path, job_id: str, run_id: str | None):
    base = root / "research" / "decisions" / job_id
    found = []
    if base.exists():
        for path in sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml"))):
            data = load_yaml(path)
            if not isinstance(data, dict) or data.get("event_type") != "AUTOMATED_PROPOSAL":
                continue
            source_run = str(data.get("source_run", ""))
            if run_id and not source_run.endswith("/" + run_id):
                continue
            found.append((str(data.get("created_at", "")), str(data.get("decision_id", "")), path, data))
    if not found:
        raise FileNotFoundError(f"automated decision proposal not found for {job_id} run={run_id or '*'}")
    found.sort()
    _, _, path, data = found[-1]
    return path, data

def backfill_auto_decision(root: Path, job: dict, manifest: dict):
    job_id = str(job["job_id"])
    run_id = str(manifest["run_id"])
    rejected = bool(manifest.get("rejection_triggered"))
    triggered = list(manifest.get("triggered_criteria", [])) if isinstance(manifest.get("triggered_criteria", []), list) else []
    gaps = []
    if rejected and not triggered:
        gaps.append("legacy_triggered_criteria_not_recorded")
    if rejected:
        decision = "REJECT"
        retained = ["The complete legacy run evidence is retained; this backfill reconstructs only the pending automated proposal."]
        reusable = []
        revisit = ["Revisit if new evidence, a changed model, or a changed baseline materially affects the declared rejection criteria."]
        rationale = "Legacy manifest indicates a rejection condition triggered. This deterministic backfill does not finalize rejection."
        scope = f"Legacy automated-proposal backfill for {job_id}; final rejection requires review."
    else:
        decision = "ITERATE"
        retained = ["The complete legacy run evidence is retained; this backfill reconstructs only the pending automated proposal."]
        reusable = []
        revisit = []
        rationale = "Legacy manifest passed its declared experiment gate. This deterministic backfill does not promote knowledge."
        scope = f"Legacy automated-proposal backfill for {job_id}; promotion requires review."

    payload = {
        "schema_version": "1.0",
        "decision_id": f"{job_id}:{run_id}:auto-backfill",
        "job_id": job_id,
        "source_run": f"research/runs/{job_id}/{run_id}",
        "event_type": "AUTOMATED_PROPOSAL",
        "authority": "AUTOMATION",
        "decision": decision,
        "review_status": "PENDING",
        "rationale": rationale,
        "scope": scope,
        "declared_rejection_criteria": list(job.get("rejection", [])),
        "triggered_criteria": triggered,
        "retained_findings": retained,
        "reusable_findings": reusable,
        "revisit_if": revisit,
        "review_gaps": gaps,
        "lineage": {"supersedes": [], "related_jobs": [], "related_decisions": []},
        "created_at": str(manifest.get("completed_at", "")),
        "immutable": True,
    }
    path = root / "research" / "decisions" / job_id / f"{run_id}-auto-backfill.yaml"
    content = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    write_immutable(path, content)
    return path, payload

def find_confirmed_review(root: Path, job_id: str, parent_decision_id: str, source_run: str | None = None):
    base = root / "research" / "decisions" / job_id
    exact = []
    lineage = []
    if base.exists():
        for path in sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml"))):
            data = load_yaml(path)
            if not isinstance(data, dict):
                continue
            if data.get("event_type") != "REVIEW" or data.get("review_status") != "CONFIRMED":
                continue
            item = (str(data.get("created_at", "")), str(data.get("decision_id", "")), path, data)
            if str(data.get("parent_decision_id", "")) == parent_decision_id:
                exact.append(item)
                continue
            if source_run and str(data.get("source_run", "")) == source_run:
                lineage.append(item)
    found = exact if exact else lineage
    if not found:
        return None
    found.sort()
    return found[-1]

def find_candidate(root: Path, job_id: str, source_run: str):
    base = root / "research" / "knowledge_candidates" / job_id
    if not base.exists():
        return None, None
    for path in sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml"))):
        data = load_yaml(path)
        if isinstance(data, dict) and str(data.get("source_run", "")) == source_run:
            return path, data
    return None, None

def collect_downstream_signals(root: Path, job: dict):
    track = job.get("track", {})
    if not isinstance(track, dict):
        return []
    status_path = root / str(track.get("path", "")) / "status.yaml"
    if not status_path.is_file():
        return []
    data = load_yaml(status_path)
    if not isinstance(data, dict):
        return []
    texts = []
    for key in ("unresolved", "blockers"):
        values = data.get(key, [])
        if isinstance(values, list):
            texts.extend(str(v) for v in values)
    needles = (
        "cubase", "human", "listening", "subjective", "audio_ab", "audio ab",
        "level-matched", "real-vocal", "real vocal", "host validation", "vst3 validation",
    )
    return [text for text in texts if any(n in text.lower() for n in needles)]

def write_immutable(path: Path, content: str):
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing != content:
            raise FileExistsError(f"immutable triage artifact already differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def output_github(path_value: str | None, values: dict[str, str]):
    if not path_value:
        return
    path = Path(path_value)
    with path.open("a", encoding="utf-8") as fh:
        for key, value in values.items():
            fh.write(f"{key}={value}\n")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--job-id", required=True)
    p.add_argument("--run-id")
    p.add_argument("--github-output")
    p.add_argument("--review-root", help="Optional authoritative main-tree root for confirmed REVIEW decisions.")
    args = p.parse_args()

    root = Path(args.root).resolve()
    job_path, job = find_job(root, args.job_id)
    run_id, manifest_path, manifest = find_latest_run(root, args.job_id, args.run_id)
    try:
        decision_path, decision = find_auto_decision(root, args.job_id, run_id)
    except FileNotFoundError:
        decision_path, decision = backfill_auto_decision(root, job, manifest)
    source_run = str(decision["source_run"])
    run_dir = root / source_run

    confirmed = find_confirmed_review(root, args.job_id, str(decision["decision_id"]), source_run)
    review_root = Path(args.review_root).resolve() if args.review_root else None
    if review_root is not None and review_root != root:
        main_confirmed = find_confirmed_review(review_root, args.job_id, str(decision["decision_id"]), source_run)
        if main_confirmed is not None:
            confirmed = main_confirmed
    candidate_path, candidate = find_candidate(root, args.job_id, source_run)
    review_gaps = list(decision.get("review_gaps", [])) if isinstance(decision.get("review_gaps", []), list) else []
    policy = job.get("review_policy", {}) if isinstance(job.get("review_policy"), dict) else {}
    required_human_gates = list(policy.get("required_human_gates", [])) if isinstance(policy.get("required_human_gates", []), list) else []
    downstream_signals = collect_downstream_signals(root, job)

    promotion_requested = None
    if isinstance(candidate, dict):
        promotion_requested = str(candidate.get("promotion_requested", "HYPOTHESIS"))

    reasons = []
    if confirmed:
        candidate_class = "ALREADY_REVIEWED"
        route = "DONE"
        reasons.append("A confirmed REVIEW decision already exists for the automated proposal.")
    elif decision.get("decision") == "REJECT":
        candidate_class = "REJECT_CANDIDATE"
        route = "REJECTION_REVIEW"
        reasons.append("The automated proposal is REJECT; final rejection still requires review authority.")
    elif review_gaps or required_human_gates:
        candidate_class = "RESEARCH_MORE" if promotion_requested not in PROMOTION_LEVELS else "PROMOTION_CANDIDATE"
        route = "HUMAN_GATE_REVIEW"
        if review_gaps:
            reasons.append("The automated proposal contains unresolved review_gaps.")
        if required_human_gates:
            reasons.append("The research job explicitly requires human gates before further promotion.")
    elif decision.get("decision") == "ITERATE" and promotion_requested in PROMOTION_LEVELS:
        candidate_class = "PROMOTION_CANDIDATE"
        route = "PROMOTION_REVIEW"
        reasons.append(f"The declared experiment gate passed and the bounded knowledge candidate requests {promotion_requested} review.")
    else:
        candidate_class = "RESEARCH_MORE"
        route = "CONTINUE_RESEARCH"
        reasons.append("The run passed as evidence, but it does not yet request a bounded LIKELY/PROVISIONAL promotion review.")

    if route not in ROUTES or candidate_class not in CANDIDATES:
        raise RuntimeError("internal triage classification error")

    if route == "REJECTION_REVIEW":
        recommended = "Review the triggered rejection criteria, retained findings, reusable findings and revisit conditions; confirm or supersede with a new REVIEW decision."
    elif route == "PROMOTION_REVIEW":
        recommended = "Review the bounded knowledge claim and evidence scope for PROMOTE/ITERATE/ARCHIVE; do not treat this as product release approval."
    elif route == "HUMAN_GATE_REVIEW":
        recommended = "Resolve the listed review gaps or required human gates before a final knowledge decision."
    elif route == "CONTINUE_RESEARCH":
        recommended = "Continue the declared research path or use a predeclared continuation; no promotion decision is warranted yet."
    else:
        recommended = "No review handoff remains for this proposal; preserve the issue as historical context and close it."

    payload = {
        "schema_version": "1.0",
        "triage_id": f"{args.job_id}:{run_id}:triage-v1",
        "job_id": args.job_id,
        "run_id": run_id,
        "source_run": source_run,
        "source_decision_id": str(decision["decision_id"]),
        "source_decision_path": decision_path.relative_to(root).as_posix(),
        "job_path": job_path.relative_to(root).as_posix(),
        "knowledge_candidate_path": candidate_path.relative_to(root).as_posix() if candidate_path else None,
        "candidate_class": candidate_class,
        "route": route,
        "final_decision_made": bool(confirmed),
        "existing_review_decision_id": str(confirmed[3].get("decision_id")) if confirmed else None,
        "existing_review_source_run_match": bool(confirmed and str(confirmed[3].get("source_run", "")) == source_run),
        "acceptance_met": bool(manifest.get("acceptance_met")),
        "rejection_triggered": bool(manifest.get("rejection_triggered")),
        "promotion_requested": promotion_requested,
        "review_gaps": review_gaps,
        "required_human_gates": required_human_gates,
        "downstream_gate_signals": downstream_signals,
        "reasons": reasons,
        "recommended_action": recommended,
        "created_at": str(decision.get("created_at", manifest.get("completed_at", ""))),
        "triage_version": "1.0",
        "immutable": True,
    }

    out_dir = root / "research" / "reviews" / args.job_id
    yaml_path = out_dir / f"{run_id}-triage.yaml"
    md_path = out_dir / f"{run_id}-triage.md"
    yaml_text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)

    human_lines = "\n".join(f"- {x}" for x in required_human_gates) or "- none explicitly declared by the job"
    signal_lines = "\n".join(f"- {x}" for x in downstream_signals) or "- none detected in the track status"
    reason_lines = "\n".join(f"- {x}" for x in reasons)
    gap_lines = "\n".join(f"- {x}" for x in review_gaps) or "- none"
    md_text = f"""# CIPI Automated Review Triage

<!-- cipi-review-triage:v1 -->

- Job: `{args.job_id}`
- Run: `{run_id}`
- Candidate class: **{candidate_class}**
- Routing: **{route}**
- Final decision made: **{str(bool(confirmed)).lower()}**
- Promotion requested: **{promotion_requested or 'none'}**
- Acceptance met: **{str(bool(manifest.get('acceptance_met'))).lower()}**
- Rejection triggered: **{str(bool(manifest.get('rejection_triggered'))).lower()}**

## Why this route

{reason_lines}

## Review gaps

{gap_lines}

## Explicit human gates

{human_lines}

## Downstream track signals

{signal_lines}

## Recommended next action

{recommended}

This is deterministic triage only. It does not PROMOTE, ARCHIVE or finally REJECT research, and it does not approve a product release.
"""

    write_immutable(yaml_path, yaml_text)
    write_immutable(md_path, md_text)

    output_github(args.github_output, {
        "route": route,
        "candidate_class": candidate_class,
        "yaml_path": yaml_path.relative_to(root).as_posix(),
        "markdown_path": md_path.relative_to(root).as_posix(),
        "reviewed": "true" if confirmed else "false",
    })
    print(f"{candidate_class} -> {route}: {md_path.relative_to(root).as_posix()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
