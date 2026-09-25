from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

REPO_ROOT=Path(__file__).resolve().parents[2]
ALLOWED_PROTOTYPES={"dual_timescale_phrase_level_v1"}

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--proposal",required=True)
    p.add_argument("--evidence-manifest")
    p.add_argument("--output-root",default=str(REPO_ROOT))
    p.add_argument("--github-output")
    args=p.parse_args()

    proposal=yaml.safe_load(Path(args.proposal).read_text(encoding="utf-8"))
    pid=proposal["plugin_proposal_id"]
    overlaps=list(proposal.get("existing_plugin_overlap") or [])
    adapter=proposal.get("prototype_adapter")
    evidence_ok=False
    source_run=None
    if args.evidence_manifest:
        manifest_path=Path(args.evidence_manifest)
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        evidence_ok=bool(manifest.get("acceptance_met")) and not bool(manifest.get("rejection_triggered"))
        try:
            source_run=str(manifest_path.parent.relative_to(REPO_ROOT))
        except ValueError:
            source_run=str(manifest_path.parent)

    if overlaps:
        decision="MERGE_EXISTING"
        state="OVERLAP_REVIEW"
        reason="Direct/declared overlap remains unresolved; standalone incubation is not authorized."
    elif not evidence_ok:
        decision="ITERATE"
        state="RESEARCH_MORE"
        reason="No accepted bounded research evidence was supplied for standalone incubation."
    elif adapter not in ALLOWED_PROTOTYPES:
        decision="ITERATE"
        state="RESEARCH_MORE"
        reason="Research passed, but there is no reviewed allowlisted prototype adapter."
    else:
        decision="INCUBATE"
        state="INCUBATE"
        reason="Bounded research evidence passed, no direct product overlap is declared, and the prototype adapter is allowlisted."

    root=Path(args.output_root)
    drel=Path("research/incubator/decisions")/f"{pid}-evaluation.yaml"
    dpath=root/drel
    dpath.parent.mkdir(parents=True,exist_ok=True)
    if dpath.exists():
        raise SystemExit(f"refusing to overwrite incubator evaluation: {dpath}")
    decision_doc={
        "schema_version":"1.0",
        "plugin_proposal_id":pid,
        "decision":decision,
        "authority":"AUTOMATION",
        "final":False,
        "reason":reason,
        "matched_existing_products":overlaps,
        "source_run":source_run,
        "next_action":(
            "Create an isolated allowlisted DSP prototype and measure it against the declared baseline."
            if decision=="INCUBATE" else
            "Continue research or resolve product overlap before an isolated standalone prototype."
        )
    }
    dpath.write_text(yaml.safe_dump(decision_doc,sort_keys=False,allow_unicode=True),encoding="utf-8")

    candidate_path=""
    if decision=="INCUBATE":
        crel=Path("research/incubator/candidates")/f"{pid}.yaml"
        cpath=root/crel
        cpath.parent.mkdir(parents=True,exist_ok=True)
        if cpath.exists():
            raise SystemExit(f"refusing to overwrite incubator candidate: {cpath}")
        candidate=dict(proposal)
        candidate["state"]="INCUBATE"
        candidate["source_incubator_decision"]=str(drel)
        candidate["source_run"]=source_run
        cpath.write_text(yaml.safe_dump(candidate,sort_keys=False,allow_unicode=True),encoding="utf-8")
        candidate_path=str(crel)

    print(f"incubator evaluation: {pid} -> {decision}")
    if args.github_output:
        with Path(args.github_output).open("a",encoding="utf-8") as h:
            h.write(f"incubator_evaluation={decision}\n")
            h.write(f"incubator_candidate_path={candidate_path}\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
