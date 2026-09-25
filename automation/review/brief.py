from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

MAX_METRIC_LEAVES = 32

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def write_immutable(path: Path, content: str) -> None:
    if path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise FileExistsError(f"immutable review brief already differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def find_job(root: Path, job_id: str):
    base = root / "research" / "jobs"
    candidates = list(base.rglob("*.yaml")) + list(base.rglob("*.yml")) if base.exists() else []
    examples = root / "automation" / "examples"
    if examples.exists():
        candidates += list(examples.glob("*.yaml")) + list(examples.glob("*.yml"))
    for path in sorted(candidates):
        data = load_yaml(path)
        if isinstance(data, dict) and str(data.get("job_id")) == job_id:
            return path, data
    raise FileNotFoundError(f"research job not found for {job_id}")

def find_candidate(root: Path, job_id: str, source_run: str):
    base = root / "research" / "knowledge_candidates" / job_id
    if not base.exists():
        return None, None
    for path in sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml"))):
        data = load_yaml(path)
        if isinstance(data, dict) and str(data.get("source_run", "")) == source_run:
            return path, data
    return None, None

def find_decision_by_id(root: Path, job_id: str, decision_id: str | None):
    if not decision_id:
        return None, None
    base = root / "research" / "decisions" / job_id
    if not base.exists():
        return None, None
    for path in sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml"))):
        data = load_yaml(path)
        if isinstance(data, dict) and str(data.get("decision_id", "")) == decision_id:
            return path, data
    return None, None

def metric_leaves(value, prefix=""):
    leaves = []
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            leaves.extend(metric_leaves(value[key], child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{prefix}[{index}]"
            leaves.extend(metric_leaves(item, child))
    elif isinstance(value, (str, int, float, bool)) or value is None:
        leaves.append({"path": prefix or "$", "value": value})
    return leaves

def output_github(path_value: str | None, values: dict[str, str]) -> None:
    if not path_value:
        return
    with Path(path_value).open("a", encoding="utf-8") as fh:
        for key, value in values.items():
            fh.write(f"{key}={value}\n")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--review-root")
    p.add_argument("--job-id", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--triage-path")
    p.add_argument("--github-output")
    args = p.parse_args()

    root = Path(args.root).resolve()
    review_root = Path(args.review_root).resolve() if args.review_root else root
    source_run = f"research/runs/{args.job_id}/{args.run_id}"
    run_dir = root / source_run
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))

    triage_path = Path(args.triage_path) if args.triage_path else root / "research" / "reviews" / args.job_id / f"{args.run_id}-triage.yaml"
    if not triage_path.is_absolute():
        triage_path = root / triage_path
    triage = load_yaml(triage_path)
    if not isinstance(triage, dict):
        raise ValueError("triage record must be a mapping")

    job_path, job = find_job(root, args.job_id)
    candidate_path, candidate = find_candidate(root, args.job_id, source_run)

    review_id = triage.get("existing_review_decision_id")
    review_path, confirmed = find_decision_by_id(review_root, args.job_id, str(review_id) if review_id else None)
    if confirmed is None and review_root != root:
        review_path, confirmed = find_decision_by_id(root, args.job_id, str(review_id) if review_id else None)

    route = str(triage["route"])
    if route == "REJECTION_REVIEW":
        actions = ["REJECT", "ITERATE", "ARCHIVE"]
    elif route == "PROMOTION_REVIEW":
        actions = ["PROMOTE", "ITERATE", "ARCHIVE"]
    elif route == "HUMAN_GATE_REVIEW":
        actions = ["ITERATE", "ARCHIVE_AFTER_REVIEW"]
    elif route == "CONTINUE_RESEARCH":
        actions = ["ITERATE", "ARCHIVE"]
    else:
        actions = [str(confirmed.get("decision"))] if isinstance(confirmed, dict) and confirmed.get("decision") else ["NO_ACTION"]

    source_decision_path = root / str(triage["source_decision_path"])
    source_decision = load_yaml(source_decision_path)

    metric_snapshot = metric_leaves(metrics)[:MAX_METRIC_LEAVES]
    candidate_summary = None
    if isinstance(candidate, dict):
        candidate_summary = {
            "claim": candidate.get("claim"),
            "evidence_type": candidate.get("evidence_type"),
            "scope": candidate.get("scope"),
            "promotion_requested": candidate.get("promotion_requested"),
        }

    confirmed_summary = None
    if isinstance(confirmed, dict):
        confirmed_summary = {
            "decision_id": confirmed.get("decision_id"),
            "decision": confirmed.get("decision"),
            "scope": confirmed.get("scope"),
            "rationale": confirmed.get("rationale"),
            "path": review_path.relative_to(review_root).as_posix() if review_path else None,
        }

    required_checks = [
        "Evidence integrity and source-run provenance are intact.",
        "Acceptance/rejection criteria were declared before interpreting the result.",
        "Negative or contradictory evidence has not been omitted.",
        "The proposed decision stays inside the measured scope.",
        "Reusable findings are separated from product-specific calibration.",
        "Human-only listening/Cubase/host gates remain open unless explicitly completed.",
        "No product release claim is inferred from a research knowledge decision.",
    ]

    payload = {
        "schema_version": "1.0",
        "brief_version": "1.0",
        "brief_id": f"{args.job_id}:{args.run_id}:review-brief-v1",
        "job_id": args.job_id,
        "run_id": args.run_id,
        "source_run": source_run,
        "route": route,
        "candidate_class": triage.get("candidate_class"),
        "triage_path": triage_path.relative_to(root).as_posix(),
        "job_path": job_path.relative_to(root).as_posix(),
        "research_question": job.get("research_question"),
        "hypothesis": job.get("hypothesis"),
        "counter_hypotheses": list(job.get("counter_hypotheses", [])),
        "acceptance_criteria": list(job.get("acceptance", [])),
        "rejection_criteria": list(job.get("rejection", [])),
        "manifest_summary": {
            "result": manifest.get("result"),
            "acceptance_met": bool(manifest.get("acceptance_met")),
            "rejection_triggered": bool(manifest.get("rejection_triggered")),
            "triggered_criteria": list(manifest.get("triggered_criteria", [])),
            "source_commit": manifest.get("source_commit"),
            "worker_version": manifest.get("worker_version"),
        },
        "metric_snapshot": metric_snapshot,
        "knowledge_candidate": candidate_summary,
        "source_proposal": {
            "decision_id": source_decision.get("decision_id"),
            "decision": source_decision.get("decision"),
            "rationale": source_decision.get("rationale"),
            "review_gaps": list(source_decision.get("review_gaps", [])),
            "retained_findings": list(source_decision.get("retained_findings", [])),
            "reusable_findings": list(source_decision.get("reusable_findings", [])),
            "revisit_if": list(source_decision.get("revisit_if", [])),
        },
        "confirmed_review": confirmed_summary,
        "required_human_gates": list(triage.get("required_human_gates", [])),
        "downstream_gate_signals": list(triage.get("downstream_gate_signals", [])),
        "allowed_review_actions": actions,
        "required_precision_checks": required_checks,
        "automatic_final_decision": False,
        "immutable": True,
    }

    out_dir = root / "research" / "reviews" / args.job_id
    yaml_path = out_dir / f"{args.run_id}-review-brief.yaml"
    md_path = out_dir / f"{args.run_id}-review-brief.md"

    yaml_text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)

    metric_lines = "\n".join(f"- `{m['path']}`: {m['value']}" for m in metric_snapshot) or "- no scalar metrics"
    accept_lines = "\n".join(f"- {x}" for x in payload["acceptance_criteria"]) or "- none"
    reject_lines = "\n".join(f"- {x}" for x in payload["rejection_criteria"]) or "- none"
    checks = "\n".join(f"- [ ] {x}" for x in required_checks)
    human = "\n".join(f"- {x}" for x in payload["required_human_gates"]) or "- none"
    reusable = "\n".join(f"- {x}" for x in payload["source_proposal"]["reusable_findings"]) or "- none recorded"
    candidate_claim = candidate_summary["claim"] if candidate_summary else "none"
    confirmed_line = (
        f"**{confirmed_summary['decision']}** — {confirmed_summary['decision_id']}"
        if confirmed_summary else "none"
    )

    md_text = f"""# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `{args.job_id}`
- Run: `{args.run_id}`
- Route: **{route}**
- Candidate class: **{triage.get('candidate_class')}**
- Existing confirmed review: {confirmed_line}
- Automatic final decision: **false**

## Research question

{job.get('research_question')}

## Hypothesis

{job.get('hypothesis')}

## Gate result

- Acceptance met: **{str(bool(manifest.get('acceptance_met'))).lower()}**
- Rejection triggered: **{str(bool(manifest.get('rejection_triggered'))).lower()}**

### Acceptance criteria

{accept_lines}

### Rejection criteria

{reject_lines}

## Bounded metric snapshot

{metric_lines}

## Knowledge candidate

{candidate_claim}

## Reusable findings already retained

{reusable}

## Human-only gates

{human}

## Allowed review actions

{', '.join(actions)}

## Final precision checklist

{checks}

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
"""

    write_immutable(yaml_path, yaml_text)
    write_immutable(md_path, md_text)
    output_github(args.github_output, {
        "brief_yaml_path": yaml_path.relative_to(root).as_posix(),
        "brief_markdown_path": md_path.relative_to(root).as_posix(),
    })
    print(md_path.relative_to(root).as_posix())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
