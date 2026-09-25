from __future__ import annotations
import argparse
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
REQUIRED_GATES=(
 "baseline_improvement_pass","holdout_pass","regression_pass","cpu_pass",
 "latency_pass","overlap_advantage_pass","negative_knowledge_reviewed"
)

def load(path:Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=str(ROOT))
    p.add_argument("--max-candidates",type=int,default=1)
    p.add_argument("--github-output")
    a=p.parse_args()
    root=Path(a.root)
    pdir=root/"research/incubator/proposals"
    edir=root/"research/incubator/evidence"
    ddir=root/"research/incubator/decisions"
    ddir.mkdir(parents=True,exist_ok=True)
    emitted=[]
    if pdir.exists() and edir.exists():
        for pp in sorted(pdir.glob("*.yaml")):
            if len(emitted)>=max(1,a.max_candidates):break
            proposal=load(pp)
            if not isinstance(proposal,dict):continue
            pid=str(proposal.get("plugin_proposal_id",""))
            if proposal.get("state") not in {"OVERLAP_REVIEW","RESEARCH_MORE"}:continue
            group=edir/pid
            if not group.exists():continue
            for ep in sorted(group.glob("*.yaml"),reverse=True):
                evidence=load(ep)
                if not isinstance(evidence,dict):continue
                if evidence.get("plugin_proposal_id")!=pid:continue
                if evidence.get("raw_audio_persisted") is not False:continue
                if not all(evidence.get(k) is True for k in REQUIRED_GATES):continue
                if not proposal.get("prototype_adapter"):continue
                evidence_id=ep.stem
                decision_path=ddir/f"{pid}-incubate-{evidence_id}.yaml"
                if decision_path.exists():break
                decision={
                    "schema_version":"1.0",
                    "plugin_proposal_id":pid,
                    "decision":"INCUBATE",
                    "authority":"AUTOMATION",
                    "final":False,
                    "reason":"All declared product-discrimination gates passed; authorize an isolated experimental DSP prototype only.",
                    "matched_existing_products":list(proposal.get("existing_plugin_overlap") or []),
                    "source_evidence":str(ep.relative_to(root)),
                    "next_action":"Run the allowlisted isolated prototype. Product release, official repo creation, subjective listening and Cubase remain review gates."
                }
                decision_path.write_text(yaml.safe_dump(decision,sort_keys=False,allow_unicode=True),encoding="utf-8")
                emitted.append((pid,str(pp.relative_to(root)),str(decision_path.relative_to(root))))
                break
    print(f"incubator evaluator: {len(emitted)} INCUBATE proposal(s)")
    for item in emitted:print("-",item[0],item[2])
    if a.github_output:
        first=emitted[0] if emitted else ("","","")
        with Path(a.github_output).open("a",encoding="utf-8") as h:
            h.write(f"incubate_count={len(emitted)}\n")
            h.write(f"plugin_proposal_path={first[1]}\n")
            h.write(f"incubate_decision_path={first[2]}\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
