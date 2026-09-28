from __future__ import annotations
from pathlib import Path
from typing import Any
import re, yaml
from .base import ProjectSpec,SourceCollector,matches_project

def yaml_files(path:Path):
    if not path.exists(): return []
    return sorted([p for p in path.rglob("*.yaml") if p.is_file()]+[p for p in path.rglob("*.yml") if p.is_file()],key=lambda p:p.as_posix())

def safe_yaml(path:Path):
    try:
        x=yaml.safe_load(path.read_text(encoding="utf-8")); return x if isinstance(x,dict) else {}
    except Exception:return {}

def job_id(path:Path):
    x=safe_yaml(path)
    return str(x["job_id"]) if x.get("job_id") else re.sub(r"^\d+-","",path.stem)

def completed_index(root:Path):
    return {job_id(p):p.relative_to(root).as_posix() for p in yaml_files(root/"research/jobs/completed")}

def health_gate_map(health):
    return {str(x["job_id"]):[str(g) for g in x.get("gates",[])] for x in health.get("human_gates",[]) or [] if isinstance(x,dict) and x.get("job_id")}


def human_gate_decisions(root:Path,spec:ProjectSpec,c:SourceCollector):
    base=root/"research/human_gates/decisions"
    latest={}
    if not base.exists():return latest
    c.record_directory_index("research/human_gates/decisions")
    for p in yaml_files(base):
        x=safe_yaml(p)
        if str(x.get("project_id") or "")!=spec.project_id:continue
        target_type=str(x.get("target_type") or "")
        target_id=str(x.get("target_id") or "")
        gate=str(x.get("gate") or "")
        if not target_type or not target_id or not gate:continue
        c.record_path(p,"HUMAN_GATE_DECISION")
        key=(target_type,target_id,gate)
        rank=(str(x.get("created_at") or ""),p.as_posix())
        if key not in latest or rank>latest[key][0]:
            latest[key]=(rank,x)
    return {k:v[1] for k,v in latest.items()}

def gate_completed(decisions,target_type,target_id,gate):
    item=decisions.get((target_type,target_id,gate))
    return bool(item and str(item.get("outcome") or "").upper()=="COMPLETE" and str(item.get("operational_effect") or "")=="RESOLVE_RESEARCH_JOB_GATE")

def queued_jobs(root:Path,spec:ProjectSpec,c:SourceCollector,completed,gate_map,gate_decisions):
    out=[]
    for p in yaml_files(root/"research/jobs/queued"):
        x=safe_yaml(p)
        if not matches_project({"job_id":x.get("job_id"),"track":x.get("track"),"research_question":x.get("research_question")},spec.aliases):continue
        c.record_path(p,"RESEARCH_JOB")
        jid=str(x.get("job_id") or p.stem); deps=[str(v) for v in x.get("depends_on_jobs",[]) or []]; missing=[d for d in deps if d not in completed]
        policy=x.get("review_policy") if isinstance(x.get("review_policy"),dict) else {}
        declared=[str(v) for v in policy.get("required_human_gates",[]) or []]; current=list(gate_map.get(jid,[])); state=str(x.get("state","QUEUED"))
        all_gates=sorted(set(declared+current))
        resolved=sorted(g for g in all_gates if gate_completed(gate_decisions,"RESEARCH_JOB",jid,g))
        unresolved=sorted(g for g in all_gates if g not in resolved)
        if state=="BLOCKED_EXTERNAL": cls="BLOCKED_EXTERNAL"
        elif state=="BLOCKED_DEPENDENCY" or missing: cls="BLOCKED_DEPENDENCY"
        elif unresolved: cls="HUMAN_GATE"
        elif state=="QUEUED": cls="READY"
        else: cls=state
        out.append({"job_id":jid,"path":p.relative_to(root).as_posix(),"state":state,"classification":cls,"priority":x.get("priority"),"depends_on_jobs":deps,"unresolved_dependencies":missing,"research_question":x.get("research_question"),"declared_human_gates":sorted(set(declared)),"current_human_gates":sorted(set(current)),"resolved_human_gates":resolved,"unresolved_human_gates":unresolved})
    return sorted(out,key=lambda x:(-int(x.get("priority") or 0),x["job_id"]))

def decisions(root:Path,spec:ProjectSpec,c:SourceCollector):
    refs=[]; rejected=[]
    for p in yaml_files(root/"research/decisions"):
        x=safe_yaml(p)
        if not matches_project({"job_id":x.get("job_id"),"decision_id":x.get("decision_id"),"scope":x.get("scope")},spec.aliases):continue
        c.record_path(p,"DECISION")
        item={"path":p.relative_to(root).as_posix(),"decision_id":x.get("decision_id"),"job_id":x.get("job_id"),"decision":x.get("decision"),"authority":x.get("authority"),"review_status":x.get("review_status"),"event_type":x.get("event_type"),"created_at":x.get("created_at")}
        refs.append(item)
        authority=str(x.get("authority") or "").upper(); event=str(x.get("event_type") or "").upper(); review=str(x.get("review_status") or "").upper()
        if str(x.get("decision") or "").upper()=="REJECT" and authority not in {"AUTOMATION","WORKER"} and event!="AUTOMATED_PROPOSAL" and review not in {"","PENDING"}: rejected.append(item)
    key=lambda x:(str(x.get("created_at") or ""),x["path"])
    return sorted(refs,key=key,reverse=True)[:20],sorted(rejected,key=key,reverse=True)[:20]

def reviews(root:Path,spec:ProjectSpec,c:SourceCollector):
    out=[]
    for p in yaml_files(root/"research/reviews"):
        x=safe_yaml(p)
        if not matches_project({"job_id":x.get("job_id"),"triage_id":x.get("triage_id"),"source_decision_id":x.get("source_decision_id")},spec.aliases):continue
        c.record_path(p,"REVIEW")
        out.append({"path":p.relative_to(root).as_posix(),"job_id":x.get("job_id"),"triage_id":x.get("triage_id"),"route":x.get("route"),"final_decision_made":x.get("final_decision_made"),"created_at":x.get("created_at")})
    return sorted(out,key=lambda x:(str(x.get("created_at") or ""),x["path"]),reverse=True)[:20]

def track_state(bridge,spec):
    matched={}; human=[]; conflicts=[]
    for tid,state in sorted((bridge.get("track_lifecycle",{}) if isinstance(bridge,dict) else {}).items()):
        if not matches_project(tid,spec.aliases):continue
        matched[tid]=state
        if isinstance(state,dict) and str(state.get("state") or "")=="HUMAN_GATE":
            human.append({"source":"AUTONOMOUS_TRACK","track_id":tid,"gates":["HUMAN_GATE"],"blocking":True})
            if state.get("scheduler_eligible"): conflicts.append(f"track {tid} is HUMAN_GATE but scheduler_eligible=true")
    return matched,human,conflicts
