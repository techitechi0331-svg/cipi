from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any,Callable
from .base import *
from .collect import *

def validate_snapshot(s:dict[str,Any],root:Path):
    e=[]; req={"schema_version","authority","project_id","generated_at","generation_id","freshness","cipi_ref","product_ref","phase","research","work","human_gates","blocked","ready","unresolved_questions","latest_decision_refs","rejected_refs","review_refs","resume_contract","source_manifest","source_state_digest"}
    miss=sorted(req-set(s))
    if miss:return ["missing keys: "+", ".join(miss)]
    if s.get("authority")!=AUTHORITY:e.append(f"authority must be {AUTHORITY}")
    if s.get("freshness") not in FRESHNESS:e.append(f"invalid freshness: {s.get('freshness')}")
    r=s.get("resume_contract")
    if not isinstance(r,dict):e.append("resume_contract must be an object")
    else:
        if r.get("resume_mode") not in RESUME_MODES:e.append(f"invalid resume_mode: {r.get('resume_mode')}")
        if r.get("can_autonomously_resume") and not s.get("ready"):e.append("autonomous resume requires at least one READY item")
        if s.get("freshness")!="FRESH" and r.get("can_autonomously_resume"):e.append("non-FRESH snapshot cannot autonomously resume")
    if s.get("freshness")=="FRESH":
        p=s.get("product_ref") or {}
        if p.get("verification")!="VERIFIED" or not p.get("commit_sha"):e.append("FRESH requires a verified product commit")
    m=s.get("source_manifest")
    if not isinstance(m,list):e.append("source_manifest must be a list")
    else:
        ok,errs=manifest_matches(root,m); e+=errs
        if ok and source_state_digest(m)!=s.get("source_state_digest"):e.append("source_state_digest mismatch")
    if scan_for_secrets(s):e.append("secret-like material detected in snapshot")
    ready={str(x.get("job_id") or x.get("track_id")) for x in s.get("ready",[]) if isinstance(x,dict)}
    blocked={str(x.get("job_id") or x.get("track_id")) for x in s.get("blocked",[]) if isinstance(x,dict)}
    overlap=sorted((ready&blocked)-{"None"})
    if overlap:e.append("READY/BLOCKED conflict: "+", ".join(overlap))
    return e

def render_handoff(s):
    def rows(items,key):
        if not items:return ["- none"]
        out=[]
        for x in items:
            if isinstance(x,dict):
                v=x.get(key) or x.get("path") or canonical_json(x); state=x.get("classification") or x.get("state")
                out.append(f"- {v}"+(f" — {state}" if state else ""))
            else:out.append(f"- {x}")
        return out
    p=s["product_ref"]; r=s["resume_contract"]
    out=[f"# {s['project_id']} Continuity","",f"- Authority: **{s['authority']}**",f"- Freshness: **{s['freshness']}**",f"- CIPI source commit: {s['cipi_ref']['commit_sha']}",f"- Source-state digest: {s['source_state_digest']}",f"- Product: {p['repository']}@{p['ref']}",f"- Product commit: {p.get('commit_sha') or 'UNVERIFIED'}","","## Current position",f"- Phase: **{s['phase']}**",f"- Resume mode: **{r['resume_mode']}**",f"- Can autonomously resume: **{str(r['can_autonomously_resume']).lower()}**",f"- Recommended action: {r['recommended_action']}","","## READY",*rows(s["ready"],"job_id"),"","## BLOCKED",*rows(s["blocked"],"job_id"),"","## Human gates"]
    out += [f"- {x.get('job_id') or x.get('track_id') or 'gate'}: {', '.join(x.get('gates') or [])}" for x in s["human_gates"]] or ["- none"]
    out += (["","## Must not repeat"]+[f"- {x}" for x in r.get("must_not_repeat",[])]) if r.get("must_not_repeat") else ["","## Must not repeat","- none"]
    out += (["","## Important decision refs"]+[f"- {x['path']}" for x in s["latest_decision_refs"][:8]]) if s["latest_decision_refs"] else ["","## Important decision refs","- none"]
    out += (["","## Unresolved questions"]+[f"- {x}" for x in s["unresolved_questions"][:8]]) if s["unresolved_questions"] else ["","## Unresolved questions","- none"]
    out += ["","## Re-entry rule","Validate schema, source-state digest, product ref, Human Gates, and READY/BLOCKED state before acting.","Do not infer PROMOTE, REJECT, product adoption, listening results, or release approval from this projection.",""]
    return "\n".join(out)

def build_project_snapshot(root:Path,spec:ProjectSpec,*,resolver:Callable|None=resolve_remote_head,token=None,cipi_sha=None,generated_at=None):
    c=SourceCollector(root)
    health=c.read_json("research/health/automation-status.json","AUTOMATION_HEALTH"); bridge=c.read_json("research/health/autonomous-bridge.json","AUTONOMOUS_BRIDGE_HEALTH"); c.read_yaml("automation/cross_repo/registry.yaml","CROSS_REPO_REGISTRY")
    for rel in ("research/jobs/queued","research/jobs/completed","research/decisions","research/reviews"):c.record_directory_index(rel)
    completed=completed_index(root); gate_decisions=human_gate_decisions(root,spec,c); jobs=queued_jobs(root,spec,c,completed,health_gate_map(health),gate_decisions)
    for jid,rel in completed.items():
        if matches_project(jid,spec.aliases):c.record_path(root/rel,"RESEARCH_JOB_COMPLETED")
    for job in jobs:
        for dep in job.get("depends_on_jobs",[]):
            if dep in completed:c.record_path(root/completed[dep],"RESEARCH_JOB_DEPENDENCY")
    drefs,rejected=decisions(root,spec,c); rrefs=reviews(root,spec,c); lifecycle,track_human,conflicts=track_state(bridge,spec)
    ready=[x for x in jobs if x["classification"]=="READY"]; blocked=[x for x in jobs if x["classification"] in {"BLOCKED_EXTERNAL","BLOCKED_DEPENDENCY"}]; human=list(track_human)
    for job in jobs:
        gates=job.get("unresolved_human_gates",[])
        if gates:human.append({"source":"RESEARCH_JOB","job_id":job["job_id"],"gates":gates,"blocking":job["classification"]=="HUMAN_GATE"})
    product_sha=resolver(spec.repository,spec.default_ref,token) if resolver else None
    manifest=c.manifest(); digest=source_state_digest(manifest); freshness="CONFLICT" if conflicts else ("FRESH" if product_sha else "STALE")
    if freshness=="CONFLICT":mode,recommended="CONFLICT","RECONSTRUCT_CONTEXT"
    elif freshness!="FRESH":mode,recommended="REFRESH_REQUIRED","REFRESH_PRODUCT_REF"
    elif ready:mode,recommended="AUTO_READY",ready[0]["job_id"]
    elif any(x.get("blocking") for x in human):mode,recommended="HUMAN_GATE","HUMAN_GATE"
    elif blocked:mode,recommended="BLOCKED","WAIT_OR_STEAL_OTHER_PROJECT"
    else:mode,recommended="IDLE","NO_READY_WORK"
    can_resume=freshness=="FRESH" and not conflicts; can_auto=can_resume and bool(ready)
    must=sorted({jid for jid in completed if matches_project(jid,spec.aliases)}|{str(x.get("job_id")) for x in rejected if x.get("job_id")})[:50]
    s={"schema_version":"1.0","authority":AUTHORITY,"project_id":spec.project_id,"generated_at":generated_at or git_head_time(root),"generation_id":"","freshness":freshness,"cipi_ref":{"branch":"main","commit_sha":cipi_sha or git_head_sha(root),"freshness_basis":"source_state_digest"},"product_ref":{"repository":spec.repository,"ref":spec.default_ref,"commit_sha":product_sha,"verification":"VERIFIED" if product_sha else "UNVERIFIED"},"phase":mode,"research":{"track_lifecycle":lifecycle,"decision_ref_count":len(drefs),"review_ref_count":len(rrefs)},"work":{"queued_job_count":len(jobs),"ready_count":len(ready),"blocked_count":len(blocked),"human_gate_count":len(human)},"human_gates":sorted(human,key=lambda x:str(x.get("job_id") or x.get("track_id") or "")),"blocked":blocked,"ready":ready,"unresolved_questions":[str(x["research_question"]) for x in jobs if x.get("research_question")][:20],"latest_decision_refs":drefs,"rejected_refs":rejected,"review_refs":rrefs,"resume_contract":{"can_resume":can_resume,"can_autonomously_resume":can_auto,"resume_mode":mode,"recommended_action":recommended,"blocked_dependencies":sorted({d for x in blocked for d in x.get("unresolved_dependencies",[])}),"human_gates":[x.get("job_id") or x.get("track_id") for x in human],"required_context":[x["path"] for x in drefs[:8]]+[x["path"] for x in rrefs[:8]],"must_not_repeat":must},"conflicts":sorted(set(conflicts)),"source_manifest":manifest,"source_state_digest":digest}
    s["generation_id"]=sha256_text("|".join([spec.project_id,digest,str(product_sha or "UNVERIFIED"),AUTHORITY]))[:24]
    errs=validate_snapshot(s,root)
    if errs:s["freshness"]="INVALID";s["resume_contract"].update({"can_resume":False,"can_autonomously_resume":False,"resume_mode":"CONFLICT","recommended_action":"REBUILD_INVALID_SNAPSHOT"});s["validation_errors"]=errs
    if scan_for_secrets(s):raise ContinuityError("secret-like material would be written to public continuity output")
    return s

def atomic_write(path:Path,text:str):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_name(path.name+".tmp");tmp.write_text(text,encoding="utf-8");os.replace(tmp,path)

def publish_project_snapshot(out:Path,s):
    d=out/"projects"/s["project_id"]; payload=json.dumps(s,indent=2,sort_keys=True,ensure_ascii=False)+"\n"; hand=render_handoff(s)
    if scan_for_secrets(payload) or scan_for_secrets(hand):raise ContinuityError("secret-like material detected during publish")
    atomic_write(d/"current.json",payload);atomic_write(d/"HANDOFF.md",hand)

def build_all(root:Path,*,output_root=None,project_id=None,resolver=resolve_remote_head,token=None,cipi_sha=None,generated_at=None,publish=True):
    specs=load_project_specs(root)
    if project_id:
        specs=[x for x in specs if x.project_id==project_id]
        if not specs:raise ContinuityError(f"unknown project: {project_id}")
    snaps={}
    for spec in specs:
        s=build_project_snapshot(root,spec,resolver=resolver,token=token,cipi_sha=cipi_sha,generated_at=generated_at);ok,errs=manifest_matches(root,s["source_manifest"])
        if not ok:raise ContinuityError("source changed during continuity build: "+"; ".join(errs))
        snaps[spec.project_id]=s
    if publish:
        out=output_root or root/"research/continuity"
        for s in snaps.values():publish_project_snapshot(out,s)
        index={"schema_version":"1.0","authority":AUTHORITY,"projects":[{"project_id":pid,"repository":s["product_ref"]["repository"],"snapshot":f"projects/{pid}/current.json","handoff":f"projects/{pid}/HANDOFF.md","freshness":s["freshness"],"generation_id":s["generation_id"]} for pid,s in sorted(snaps.items())]}
        global_state={"schema_version":"1.0","authority":AUTHORITY,"generated_at":generated_at or git_head_time(root),"project_count":len(snaps),"freshness_counts":{st:sum(1 for s in snaps.values() if s["freshness"]==st) for st in sorted(FRESHNESS)},"projects":[{"project_id":pid,"freshness":s["freshness"],"phase":s["phase"],"recommended_action":s["resume_contract"]["recommended_action"]} for pid,s in sorted(snaps.items())]}
        atomic_write(out/"index.json",json.dumps(index,indent=2,sort_keys=True)+"\n");atomic_write(out/"global/current.json",json.dumps(global_state,indent=2,sort_keys=True)+"\n")
    return snaps

def validate_published(root:Path,project_id=None):
    c=root/"research/continuity"; errors=[]; paths=[c/"projects"/project_id/"current.json"] if project_id else sorted((c/"projects").glob("*/current.json"))
    if not paths:return ["no continuity snapshots found"]
    for p in paths:
        if not p.exists():errors.append(f"missing snapshot: {p.relative_to(root)}");continue
        try:s=json.loads(p.read_text(encoding="utf-8"))
        except Exception as ex:errors.append(f"{p.relative_to(root)}: invalid JSON: {ex}");continue
        errors += [f"{p.relative_to(root)}: {x}" for x in validate_snapshot(s,root)]
        h=p.parent/"HANDOFF.md"
        if not h.exists():errors.append(f"{h.relative_to(root)}: missing")
        elif scan_for_secrets(h.read_text(encoding="utf-8")):errors.append(f"{h.relative_to(root)}: secret-like material detected")
    return errors
