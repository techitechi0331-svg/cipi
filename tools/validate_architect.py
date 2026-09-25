from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
GAP_REQUIRED = {
    "schema_version","gap_id","topic_id","title","state","score","support_path_count",
    "minimum_support_paths","support_paths","why_gap","question","human_only","plugin_opportunity"
}
PROPOSAL_REQUIRED = {
    "schema_version","proposal_id","source_gap","state","track","research_question","hypothesis",
    "counter_hypotheses","baseline","variants","metrics","acceptance","rejection","pilot_job_id",
    "plugin_opportunity","overlap_hints","external_validity","budget"
}
PROPOSAL_STATES = {"PILOT_READY","NEEDS_ADAPTER","RESEARCH_MORE","ARCHIVED"}
SIGNAL_REQUIRED = {"schema_version","signal_id","source_path","kind","text_hash","text","state","executable"}
ADAPTER_REQUIRED = {
    "schema_version","adapter_candidate_id","source_research_proposal","state","executable",
    "proposed_adapter_name","track","research_question","baseline","variants","metrics",
    "acceptance","rejection","required_operations","network_required","timeout_minutes",
    "dependency_policy","allowed_output_prefixes","forbidden_operations","review_requirements",
    "implementation_status","automatic_registry_promotion_allowed"
}

def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def validate_root(root: Path) -> list[str]:
    errors=[]
    base=root/"research"/"architect"
    for path in sorted((base/"signals").glob("*.yaml")) if (base/"signals").exists() else []:
        try: data=load(path)
        except Exception as exc:
            errors.append(f"{path}: YAML parse error: {exc}"); continue
        if not isinstance(data,dict):
            errors.append(f"{path}: root must be mapping"); continue
        missing=sorted(SIGNAL_REQUIRED-set(data))
        if missing: errors.append(f"{path}: missing {', '.join(missing)}")
        if data.get("state") not in {"UNCLASSIFIED","CLASSIFIED","ARCHIVED"}:
            errors.append(f"{path}: invalid signal state")
        if data.get("executable") is not False:
            errors.append(f"{path}: research-gap signal must be non-executable")

    for path in sorted((base/"gaps").glob("*.yaml")) if (base/"gaps").exists() else []:
        try: data=load(path)
        except Exception as exc:
            errors.append(f"{path}: YAML parse error: {exc}"); continue
        if not isinstance(data,dict):
            errors.append(f"{path}: root must be mapping"); continue
        missing=sorted(GAP_REQUIRED-set(data))
        if missing: errors.append(f"{path}: missing {', '.join(missing)}")
        if data.get("schema_version")!="1.0": errors.append(f"{path}: schema_version must be 1.0")
        if data.get("state") not in {"OPEN","PILOTED","CLOSED","ARCHIVED"}:
            errors.append(f"{path}: invalid gap state")
        if not isinstance(data.get("support_paths"),list): errors.append(f"{path}: support_paths must be list")
        if not isinstance(data.get("score"),int): errors.append(f"{path}: score must be integer")
    for path in sorted((base/"proposals").glob("*.yaml")) if (base/"proposals").exists() else []:
        try: data=load(path)
        except Exception as exc:
            errors.append(f"{path}: YAML parse error: {exc}"); continue
        if not isinstance(data,dict):
            errors.append(f"{path}: root must be mapping"); continue
        missing=sorted(PROPOSAL_REQUIRED-set(data))
        if missing: errors.append(f"{path}: missing {', '.join(missing)}")
        if data.get("state") not in PROPOSAL_STATES: errors.append(f"{path}: invalid proposal state")
        for key in ("counter_hypotheses","baseline","variants","metrics","acceptance","rejection","overlap_hints","external_validity"):
            if not isinstance(data.get(key),list) or (key not in {"overlap_hints"} and not data.get(key)):
                errors.append(f"{path}: {key} must be a non-empty list" if key!="overlap_hints" else f"{path}: overlap_hints must be list")
        source=root/str(data.get("source_gap",""))
        if not source.exists(): errors.append(f"{path}: source_gap does not exist: {data.get('source_gap')}")
        budget=data.get("budget")
        if not isinstance(budget,dict): errors.append(f"{path}: budget must be mapping")

    for path in sorted((base/"adapter_candidates").glob("*.yaml")) if (base/"adapter_candidates").exists() else []:
        try: data=load(path)
        except Exception as exc:
            errors.append(f"{path}: YAML parse error: {exc}"); continue
        if not isinstance(data,dict):
            errors.append(f"{path}: root must be mapping"); continue
        missing=sorted(ADAPTER_REQUIRED-set(data))
        if missing: errors.append(f"{path}: missing {', '.join(missing)}")
        if data.get("state") not in {"DRAFT_REVIEW","APPROVED_FOR_IMPLEMENTATION","REJECTED"}:
            errors.append(f"{path}: invalid adapter candidate state")
        if data.get("executable") is not False:
            errors.append(f"{path}: adapter candidate artifact must be non-executable")
        if data.get("automatic_registry_promotion_allowed") is not False:
            errors.append(f"{path}: automatic registry promotion must be false")
        source=root/str(data.get("source_research_proposal",""))
        if not source.exists():
            errors.append(f"{path}: source_research_proposal does not exist")
        else:
            proposal=load(source)
            if proposal.get("state") != "NEEDS_ADAPTER":
                errors.append(f"{path}: source proposal must remain NEEDS_ADAPTER until reviewed implementation exists")
        for key in ("baseline","variants","metrics","acceptance","rejection","required_operations","allowed_output_prefixes","forbidden_operations","review_requirements"):
            if not isinstance(data.get(key),list) or not data.get(key):
                errors.append(f"{path}: {key} must be a non-empty list")
    return errors

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=str(REPO_ROOT))
    args=p.parse_args()
    errors=validate_root(Path(args.root))
    if errors:
        print("CIPI architect gate: FAIL")
        for e in errors: print("-",e)
        return 1
    print("CIPI architect gate: PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
