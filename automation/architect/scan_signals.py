from __future__ import annotations
import argparse, hashlib, re
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]

def normalize(text:str)->str:
    return re.sub(r"\s+"," ",text.strip())

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--output-root",default=str(ROOT))
    p.add_argument("--max-signals",type=int,default=12)
    p.add_argument("--github-output")
    a=p.parse_args()
    root=Path(a.output_root)
    outdir=root/"research/architect/signals"
    outdir.mkdir(parents=True,exist_ok=True)
    candidates=[]
    for status in sorted((ROOT/"research").rglob("status.yaml")):
        if "_template" in status.parts:
            continue
        try:
            data=yaml.safe_load(status.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data,dict):
            continue
        for kind in ("unresolved","blockers"):
            vals=data.get(kind) or []
            if not isinstance(vals,list):
                continue
            for item in vals:
                text=normalize(str(item))
                if len(text)<18:
                    continue
                digest=hashlib.sha256((str(status.relative_to(ROOT))+"\n"+kind+"\n"+text).encode()).hexdigest()[:16]
                signal_id=f"SIG-{digest.upper()}"
                path=outdir/f"{signal_id}.yaml"
                if path.exists():
                    continue
                candidates.append((signal_id,status,kind,text,path))
    created=[]
    for signal_id,status,kind,text,path in candidates[:max(0,a.max_signals)]:
        doc={
            "schema_version":"1.0",
            "signal_id":signal_id,
            "source_path":str(status.relative_to(ROOT)),
            "kind":kind.upper(),
            "text_hash":signal_id[4:].lower(),
            "text":text,
            "state":"UNCLASSIFIED",
            "note":"Deterministic gap signal only. It is not yet a Research Proposal and cannot execute code."
        }
        path.write_text(yaml.safe_dump(doc,sort_keys=False,allow_unicode=True),encoding="utf-8")
        created.append(str(path.relative_to(ROOT)))
    print(f"architect signals: {len(created)} created")
    for item in created:
        print("-",item)
    if a.github_output:
        with Path(a.github_output).open("a",encoding="utf-8") as h:
            h.write(f"signal_count={len(created)}\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
