from __future__ import annotations
import argparse, hashlib, re
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]

def norm(text:str)->str:
    return re.sub(r"\s+"," ",text.strip())

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",default=str(ROOT))
    p.add_argument("--max-signals",type=int,default=8)
    p.add_argument("--github-output")
    a=p.parse_args()
    root=Path(a.root)
    outdir=root/"research/architect/signals"
    outdir.mkdir(parents=True,exist_ok=True)
    pending=[]
    for path in sorted((ROOT/"research").rglob("status.yaml")):
        if "_template" in path.parts: continue
        try:data=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:continue
        if not isinstance(data,dict):continue
        for kind in ("unresolved","blockers"):
            values=data.get(kind) or []
            if not isinstance(values,list):continue
            for raw in values:
                text=norm(str(raw))
                if len(text)<18:continue
                key=f"{path.relative_to(ROOT)}\n{kind}\n{text}"
                digest=hashlib.sha256(key.encode()).hexdigest()[:16].upper()
                sid=f"SIG-{digest}"
                target=outdir/f"{sid}.yaml"
                if target.exists():continue
                pending.append((sid,path,kind,text,target))
    created=[]
    for sid,path,kind,text,target in pending[:max(0,a.max_signals)]:
        doc={
            "schema_version":"1.0",
            "signal_id":sid,
            "source_path":str(path.relative_to(ROOT)),
            "kind":kind.upper(),
            "text_hash":sid[4:].lower(),
            "text":text,
            "state":"UNCLASSIFIED",
            "executable":False,
            "note":"Gap signal only. It may seed a future reviewed topic/proposal but cannot execute code."
        }
        target.write_text(yaml.safe_dump(doc,sort_keys=False,allow_unicode=True),encoding="utf-8")
        created.append(str(target.relative_to(root)))
    print(f"architect signal scan: {len(created)} new signal(s)")
    for item in created:print("-",item)
    if a.github_output:
        with Path(a.github_output).open("a",encoding="utf-8") as h:
            h.write(f"signal_count={len(created)}\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
