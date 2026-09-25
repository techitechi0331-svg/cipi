from __future__ import annotations

import argparse
from pathlib import Path
import re
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

def slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--proposal", required=True)
    p.add_argument("--catalog", default=str(REPO_ROOT / "automation/incubator/product_catalog.yaml"))
    p.add_argument("--output-root", default=str(REPO_ROOT))
    p.add_argument("--github-output")
    args = p.parse_args()

    source = yaml.safe_load(Path(args.proposal).read_text(encoding="utf-8"))
    if not source.get("plugin_opportunity"):
        print("incubator: research proposal is not product-oriented")
        return 0

    catalog = yaml.safe_load(Path(args.catalog).read_text(encoding="utf-8"))
    names = {item["name"].lower(): item for item in catalog.get("products") or []}
    overlap_hints = list(source.get("overlap_hints") or [])
    matched = [hint for hint in overlap_hints if hint.lower() in names]

    pid = f"PLUGIN-{slug(source['proposal_id'])}"
    decision = "MERGE_EXISTING" if matched else "ITERATE"
    state = "OVERLAP_REVIEW" if matched else "RESEARCH_MORE"
    reason = (
        "Existing products already cover adjacent user problems; a new product is not justified "
        "until an independent advantage over merge/feature-extension alternatives is measured."
        if matched else
        "No direct catalog overlap was declared, but research evidence is not yet sufficient for INCUBATE."
    )

    proposal = {
        "schema_version": "1.0",
        "plugin_proposal_id": pid,
        "source_research_proposal": str(Path(args.proposal)),
        "state": state,
        "working_name": source["proposal_id"].replace("RP-", "").replace("-", " ").title(),
        "problem": source["research_question"],
        "target_user": "vocal / singing mix engineer",
        "target_signal": "singing vocal",
        "supporting_research": [source["source_gap"]],
        "supporting_negative_knowledge": list(source.get("counter_hypotheses") or []),
        "existing_plugin_overlap": matched,
        "why_not_merge_existing": (
            "Not yet demonstrated; overlap review must be resolved before an independent product is incubated."
            if matched else
            "No explicit overlap was declared, but product value still requires measured evidence."
        ),
        "dsp_hypothesis": source["hypothesis"],
        "simple_baseline": list(source.get("baseline") or []),
        "metrics": list(source.get("metrics") or []),
        "failure_criteria": list(source.get("rejection") or []),
        "expected_cpu": "bounded pilot required",
        "expected_latency": "must be measured",
        "prototype_adapter": source.get("prototype_adapter"),
        "automatic_production_allowed": False,
    }
    dec = {
        "schema_version": "1.0",
        "plugin_proposal_id": pid,
        "decision": decision,
        "authority": "AUTOMATION",
        "final": False,
        "reason": reason,
        "matched_existing_products": matched,
        "next_action": (
            "Route the mechanism to the relevant existing product review before any standalone prototype."
            if decision == "MERGE_EXISTING"
            else "Obtain measured research evidence and a reviewed prototype adapter before INCUBATE."
        ),
    }

    root = Path(args.output_root)
    proposal_rel = Path("research/incubator/proposals") / f"{pid}.yaml"
    decision_rel = Path("research/incubator/decisions") / f"{pid}-auto.yaml"
    for rel, data in ((proposal_rel, proposal), (decision_rel, dec)):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            print(f"incubator: existing {rel}; no overwrite")
            continue
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"incubator: {pid} -> {decision}")
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"plugin_proposal_id={pid}\n")
            handle.write(f"incubator_decision={decision}\n")
            handle.write(f"plugin_proposal_path={proposal_rel}\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
