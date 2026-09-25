from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import yaml

REPO_ROOT=Path(__file__).resolve().parents[1]
PROPOSAL_REQUIRED={
 "schema_version","plugin_proposal_id","source_research_proposal","state","working_name",
 "problem","target_user","target_signal","supporting_research","supporting_negative_knowledge",
 "existing_plugin_overlap","why_not_merge_existing","dsp_hypothesis","simple_baseline",
 "metrics","failure_criteria","expected_cpu","expected_latency","automatic_production_allowed"
}
DECISIONS={"REJECT","ITERATE","MERGE_EXISTING","INCUBATE","ARCHIVE"}
STATES={"OVERLAP_REVIEW","RESEARCH_MORE","INCUBATE","REJECTED","ARCHIVED"}

def validate_root(root:Path)->list[str]:
    errors=[]
    base=root/"research"/"incubator"
    proposals={}
    pdir=base/"proposals"
    if pdir.exists():
        for path in sorted(pdir.glob("*.yaml")):
            try:data=yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:errors.append(f"{path}: YAML parse error: {exc}");continue
            if not isinstance(data,dict):errors.append(f"{path}: root must be mapping");continue
            missing=sorted(PROPOSAL_REQUIRED-set(data))
            if missing:errors.append(f"{path}: missing {', '.join(missing)}")
            if data.get("state") not in STATES:errors.append(f"{path}: invalid state")
            if data.get("automatic_production_allowed") is not False:
                errors.append(f"{path}: automatic production must be false")
            proposals[data.get("plugin_proposal_id")]=path
    ddir=base/"decisions"
    if ddir.exists():
        for path in sorted(ddir.glob("*.yaml")):
            try:data=yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:errors.append(f"{path}: YAML parse error: {exc}");continue
            if data.get("decision") not in DECISIONS:errors.append(f"{path}: invalid decision")
            if data.get("final") is not False:errors.append(f"{path}: automation decision must not be final")
            if data.get("plugin_proposal_id") not in proposals:
                errors.append(f"{path}: matching proposal not found")
    cdir=base/"candidates"
    if cdir.exists():
        for path in sorted(cdir.glob("*.yaml")):
            try:data=yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:errors.append(f"{path}: YAML parse error: {exc}");continue
            if not isinstance(data,dict):errors.append(f"{path}: root must be mapping");continue
            if data.get("state")!="INCUBATE":errors.append(f"{path}: candidate state must be INCUBATE")
            if data.get("automatic_production_allowed") is not False:
                errors.append(f"{path}: candidate automatic production must be false")
            if not str(data.get("source_run","")).startswith("research/runs/"):
                errors.append(f"{path}: candidate source_run must point under research/runs/")
            if not str(data.get("source_incubator_decision","")).startswith("research/incubator/decisions/"):
                errors.append(f"{path}: candidate source decision missing")
    proto=base/"prototypes"
    if proto.exists():
        for path in proto.rglob("metrics.json"):
            try:json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:errors.append(f"{path}: JSON parse error: {exc}")
    return errors

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--root",default=str(REPO_ROOT));args=p.parse_args()
    errors=validate_root(Path(args.root))
    if errors:
        print("CIPI incubator gate: FAIL")
        for e in errors:print("-",e)
        return 1
    print("CIPI incubator gate: PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
