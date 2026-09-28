from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json, os, re, subprocess
from pathlib import Path
from typing import Any
import urllib.error, urllib.request
import yaml

AUTHORITY="CONTEXT_RECONSTRUCTION_ONLY"
FRESHNESS={"FRESH","STALE","CONFLICT","INVALID"}
RESUME_MODES={"AUTO_READY","BLOCKED","HUMAN_GATE","IDLE","REFRESH_REQUIRED","CONFLICT"}
SECRET_PATTERNS=(
 re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
 re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
 re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
 re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
 re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
 re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\s*[:=]\s*[\"']?[A-Za-z0-9_\-./+=]{16,}"),
)

@dataclass(frozen=True)
class ProjectSpec:
    project_id:str
    repository:str
    default_ref:str
    aliases:tuple[str,...]

class ContinuityError(RuntimeError): pass

def sha256_text(v:str)->str: return hashlib.sha256(v.encode()).hexdigest()
def canonical_json(v:Any)->str: return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def normalize_token(v:str)->str: return re.sub(r"[^A-Z0-9]+","",v.upper())

class SourceCollector:
    def __init__(self,root:Path): self.root=root; self.refs={}
    def _record(self,path:Path,text:str,source_type:str):
        rel=path.relative_to(self.root).as_posix()
        self.refs[rel]={"source_type":source_type,"repository":"techitechi0331-svg/cipi","path":rel,"sha256":sha256_text(text)}
    def read_text(self,rel:str,source_type="CIPI_FILE"):
        p=self.root/rel; t=p.read_text(encoding="utf-8"); self._record(p,t,source_type); return t
    def read_json(self,rel:str,source_type="CIPI_JSON"): return json.loads(self.read_text(rel,source_type))
    def read_yaml(self,rel:str,source_type="CIPI_YAML"): return yaml.safe_load(self.read_text(rel,source_type))
    def record_path(self,path:Path,source_type="CIPI_FILE"): self._record(path,path.read_text(encoding="utf-8"),source_type)
    def record_directory_index(self,rel:str):
        p=self.root/rel
        entries=sorted(x.relative_to(p).as_posix() for x in p.rglob("*") if x.is_file()) if p.exists() else []
        self.refs[rel]={"source_type":"CIPI_DIRECTORY_INDEX","repository":"techitechi0331-svg/cipi","path":rel,"sha256":sha256_text(canonical_json(entries)),"kind":"directory_index"}
    def manifest(self): return [self.refs[k] for k in sorted(self.refs)]

def source_state_digest(manifest):
    items=[{"path":x["path"],"sha256":x["sha256"]} for x in manifest if x.get("path") and x.get("sha256")]
    return sha256_text(canonical_json(sorted(items,key=lambda x:x["path"])))

def git_head_sha(root:Path):
    try: return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return os.environ.get("GITHUB_SHA") or "UNKNOWN"

def git_head_time(root:Path):
    try: return subprocess.check_output(["git","-C",str(root),"show","-s","--format=%cI","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

def aliases_for(repo_key:str,repository:str):
    name=repository.rsplit("/",1)[-1]
    raw={repo_key,repo_key.replace("_","-"),repo_key.replace("-","_"),name,name.replace("_","-"),name.replace("-","_")}
    if repo_key=="pre610": raw.add("UA610")
    if repo_key=="surface": raw|={"VOCAL_SURFACE","VOCALSURFACE"}
    if repo_key=="doubler": raw|={"MICRODOUBLE","VOCAL_ONE_KNOB_DOUBLER"}
    if repo_key=="vo_prep": raw|={"VOPREP","VO_PREP"}
    return tuple(sorted({normalize_token(x) for x in raw if x}))

def load_project_specs(root:Path,collector:SourceCollector|None=None):
    rel="automation/cross_repo/registry.yaml"
    data=collector.read_yaml(rel,"CROSS_REPO_REGISTRY") if collector else yaml.safe_load((root/rel).read_text(encoding="utf-8"))
    out=[]
    for key,cfg in sorted((data.get("repositories",{}) if isinstance(data,dict) else {}).items()):
        if isinstance(cfg,dict) and cfg.get("repository"):
            out.append(ProjectSpec(str(key),str(cfg["repository"]),str(cfg.get("default_ref","main")),aliases_for(str(key),str(cfg["repository"]))))
    return out

def matches_project(value:Any,aliases):
    if value is None:return False
    text=canonical_json(value) if isinstance(value,(dict,list,tuple)) else str(value)
    n=normalize_token(text)
    return any(a and a in n for a in aliases)

def resolve_remote_head(repository:str,ref:str,token:str|None=None,timeout:float=8.0):
    req=urllib.request.Request(f"https://api.github.com/repos/{repository}/commits/{ref}",headers={"Accept":"application/vnd.github+json","User-Agent":"cipi-continuity/1.0",**({"Authorization":f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r: data=json.loads(r.read().decode())
        return str(data["sha"]) if data.get("sha") else None
    except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError,ValueError): return None

def scan_for_secrets(value):
    text=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)
    return [p.pattern for p in SECRET_PATTERNS if p.search(text)]

def manifest_matches(root:Path,manifest):
    errors=[]
    for item in manifest:
        rel=item.get("path"); expected=item.get("sha256")
        if not rel or not expected: continue
        p=root/str(rel)
        if item.get("kind")=="directory_index":
            if not p.is_dir(): errors.append(f"missing source directory: {rel}"); continue
            entries=sorted(x.relative_to(p).as_posix() for x in p.rglob("*") if x.is_file())
            actual=sha256_text(canonical_json(entries))
        else:
            if not p.is_file(): errors.append(f"missing source: {rel}"); continue
            actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=expected: errors.append(f"source hash changed: {rel}")
    return not errors,errors
