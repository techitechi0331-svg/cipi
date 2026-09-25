from __future__ import annotations

import argparse
from pathlib import Path
import re
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

def slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")

def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--root", default=str(REPO_ROOT))
    p.add_argument("--max-candidates", type=int, default=1)
    p.add_argument("--github-output")
    args=p.parse_args()
    root=Path(args.root)
    proposals=root/"research"/"architect"/"proposals"
    outdir=root/"research"/"architect"/"adapter_candidates"
    outdir.mkdir(parents=True, exist_ok=True)

    created=[]
    if proposals.exists():
        for path in sorted(proposals.glob("*.yaml")):
            if len(created) >= max(1,args.max_candidates):
                break
            data=load(path)
            if not isinstance(data,dict) or data.get("state")!="NEEDS_ADAPTER":
                continue
            aid=f"AC-{slug(str(data['proposal_id']))}"
            target=outdir/f"{aid}.yaml"
            if target.exists():
                continue

            q=str(data.get("research_question",""))
            text=(q+" "+str(data.get("hypothesis",""))).lower()
            public_data_hint=any(token in text for token in ("singer","vocal","mix","language","breath"))
            candidate={
                "schema_version":"1.0",
                "adapter_candidate_id":aid,
                "source_research_proposal":str(path.relative_to(root)),
                "state":"DRAFT_REVIEW",
                "executable":False,
                "proposed_adapter_name":slug(str(data["proposal_id"])).lower().replace("-","_")+"_pilot_v1",
                "track":data.get("track"),
                "research_question":data.get("research_question"),
                "baseline":list(data.get("baseline") or []),
                "variants":list(data.get("variants") or []),
                "metrics":list(data.get("metrics") or []),
                "acceptance":list(data.get("acceptance") or []),
                "rejection":list(data.get("rejection") or []),
                "required_operations":[
                    "read_committed_research_evidence",
                    "generate_deterministic_synthetic_inputs",
                    "calculate_declared_metrics",
                    "write_derived_json_csv_markdown_sha256"
                ],
                "network_required":False,
                "public_dataset_review_recommended":public_data_hint,
                "timeout_minutes":5,
                "dependency_policy":"standard-library or explicitly pinned existing CIPI dependency only",
                "allowed_output_prefixes":[
                    "research/runs/ARCHITECT-",
                    "research/knowledge_candidates/ARCHITECT-",
                    "research/decisions/ARCHITECT-"
                ],
                "forbidden_operations":[
                    "arbitrary_shell_from_yaml",
                    "production_plugin_mutation",
                    "adapter_registry_self_registration",
                    "raw_client_audio_persistence",
                    "secret_access",
                    "automatic_promote_or_confirm",
                    "official_repo_or_release_creation"
                ],
                "review_requirements":[
                    "Confirm the metric really tests the research question.",
                    "Confirm baseline and counter-hypotheses remain competitive.",
                    "Confirm dependencies, network access and timeout are bounded.",
                    "Implement the adapter separately and pass Architect/Auto Research gates before registry consideration."
                ],
                "implementation_status":"NOT_IMPLEMENTED",
                "automatic_registry_promotion_allowed":False,
            }
            target.write_text(yaml.safe_dump(candidate,sort_keys=False,allow_unicode=True),encoding="utf-8")
            created.append((aid,str(target.relative_to(root))))

    print(f"adapter candidate bridge: {len(created)} candidate(s) created")
    for aid,path in created:
        print("-",aid,path)
    if args.github_output:
        with Path(args.github_output).open("a",encoding="utf-8") as handle:
            handle.write(f"created_count={len(created)}\n")
            handle.write(f"adapter_candidate_id={(created[0][0] if created else '')}\n")
            handle.write(f"adapter_candidate_path={(created[0][1] if created else '')}\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
