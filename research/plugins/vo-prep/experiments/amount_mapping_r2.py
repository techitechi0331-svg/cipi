#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import tempfile
import urllib.request
import zipfile

import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d
from scipy.signal import lfilter

SLOW_MS=25.0
ATTACK_MS=8.0
RELEASE_MS=70.0
RATIO=1.5
KNEE_DB=18.0
LEARN_SECONDS=4.0
AMOUNTS=(0.0,12.5,25.0,37.5,50.0,62.5,75.0,87.5,100.0)

ANCHOR_OFFSETS={
    25.0: 0.32994329929351807,
    50.0: -6.475958228111267,
    75.0: -11.65919840335846,
}
TARGET100_OFFSETS={
    5.0: -14.864720702171326,
    5.2: -15.492585062980652,
    5.4: -16.120449423789978,
    5.5: -16.43438160419464,
}

SELECTION_STEMS=(
    "man1_butterfly",
    "man2_schoolbell",
    "woman1_twinkle",
    "woman2_butterfly",
)
HOLDOUT_STEMS=(
    "man3_twinkle",
    "man4_butterfly",
    "woman3_schoolbell",
    "man5_twinkle",
)

HUST_MEDIA_URL="https://media.githubusercontent.com/media/itec-hust/HUST_Solfege/master/wav/HUST_Solfege.zip"
HUST_LFS_OID="0891bb9bf18209575b285a556c9c47ad295900a4c5ee9611e83ae3cdcca2bb34"
HUST_LFS_SIZE=273333879

def download_hust_zip(path: Path) -> None:
    req=urllib.request.Request(HUST_MEDIA_URL,headers={"User-Agent":"CIPI-Research/1.0"})
    with urllib.request.urlopen(req,timeout=180) as src, path.open("wb") as dst:
        while True:
            chunk=src.read(1024*1024)
            if not chunk:
                break
            dst.write(chunk)
    raw_head=path.read_bytes()[:128]
    if path.stat().st_size < 1000 or raw_head.startswith(b"version https://git-lfs.github.com/spec"):
        raise RuntimeError("HUST media URL returned an LFS pointer instead of the pinned object")
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != HUST_LFS_OID:
        raise RuntimeError(f"HUST LFS SHA256 mismatch: {digest}")
    if path.stat().st_size != HUST_LFS_SIZE:
        raise RuntimeError(f"HUST LFS size mismatch: {path.stat().st_size}")

def extract_selected(zip_path: Path, out_dir: Path) -> dict[str,Path]:
    wanted=set(SELECTION_STEMS+HOLDOUT_STEMS)
    found={}
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            p=Path(info.filename)
            if p.suffix.lower() != ".wav":
                continue
            stem=p.stem
            if stem in wanted:
                target=out_dir/f"{stem}.wav"
                with z.open(info) as src, target.open("wb") as dst:
                    while True:
                        chunk=src.read(1024*1024)
                        if not chunk:
                            break
                        dst.write(chunk)
                found[stem]=target
    missing=sorted(wanted-set(found))
    if missing:
        raise RuntimeError("Missing HUST WAV stems: "+", ".join(missing))
    return found

def read_mono(path: Path) -> tuple[np.ndarray,int]:
    x,sr=sf.read(path,always_2d=True,dtype="float64")
    x=np.mean(x,axis=1)
    if not np.all(np.isfinite(x)):
        x=np.nan_to_num(x,nan=0.0,posinf=0.0,neginf=0.0)
    peak=float(np.max(np.abs(x))) if len(x) else 0.0
    if peak>1.0:
        x=x/peak
    return x,int(sr)

def db_amp(x):
    return 20.0*np.log10(np.maximum(np.abs(x),1e-12))

def slow_detector(x,sr):
    a=math.exp(-1.0/(sr*SLOW_MS*1e-3))
    e=lfilter([1.0-a],[1.0,-a],x*x)
    return np.sqrt(np.maximum(e,1e-24))

def soft_knee_gr(level,threshold):
    u=np.asarray(level,dtype=np.float64)-threshold
    half=KNEE_DB*0.5
    frac=1.0-1.0/RATIO
    q=np.zeros_like(u)
    hi=u>half
    mid=(u>=-half)&(~hi)
    q[hi]=frac*u[hi]
    z=u[mid]+half
    q[mid]=frac*(z*z)/(2.0*KNEE_DB)
    return np.maximum(q,0.0)

def ballistics(desired,sr):
    aa=math.exp(-1.0/(sr*ATTACK_MS*1e-3))
    ar=math.exp(-1.0/(sr*RELEASE_MS*1e-3))
    out=np.empty_like(desired,dtype=np.float64)
    state=0.0
    for i in range(desired.size):
        v=float(desired[i])
        a=aa if v>state else ar
        state=a*state+(1.0-a)*v
        out[i]=state
    return out

def prepare_item(path):
    x,sr=read_mono(path)
    slow=slow_detector(x,sr)
    slow_db=db_amp(slow)
    fast_db=db_amp(x)
    effective=np.maximum(slow_db,fast_db-6.0)
    finite=np.isfinite(slow_db)&(slow_db>-180.0)
    peak=float(np.max(slow_db[finite])) if np.any(finite) else -180.0
    active=finite&(slow_db>=peak-30.0)
    idx=np.flatnonzero(active)
    need=max(1,int(round(LEARN_SECONDS*sr)))
    if len(idx)<need:
        raise RuntimeError(f"{path.name}: fewer than 4 s active samples")
    learn_idx=idx[:need]
    ref=float(np.median(slow_db[learn_idx]))
    lock=int(learn_idx[-1])
    eval_mask=active.copy()
    eval_mask[:lock+1]=False
    if np.sum(eval_mask)<sr:
        raise RuntimeError(f"{path.name}: less than 1 s evaluation after learn")
    return {"x":x,"sr":sr,"effective":effective,"ref":ref,"mask":eval_mask}

def anchor_offset(amount,target100):
    if amount<=0:
        return None
    offsets={**ANCHOR_OFFSETS,100.0:TARGET100_OFFSETS[target100]}
    anchors=(0.0,25.0,50.0,75.0,100.0)
    for a0,a1 in zip(anchors[:-1],anchors[1:]):
        if a0<=amount<=a1:
            if a0==0.0:
                o25=offsets[25.0]
                o50=offsets[50.0]
                slope=(o50-o25)/25.0
                return o25+slope*(amount-25.0)
            t=(amount-a0)/(a1-a0)
            return offsets[a0]+t*(offsets[a1]-offsets[a0])
    return offsets[100.0]

def process(item,kind,target100,amount):
    if amount<=0.0:
        return np.zeros_like(item["effective"])
    base=item["ref"]+TARGET100_OFFSETS[target100]
    if kind=="anchor_threshold":
        threshold=item["ref"]+anchor_offset(amount,target100)
        desired=soft_knee_gr(item["effective"],threshold)
    elif kind=="desired_gr_scale":
        desired=soft_knee_gr(item["effective"],base)*(amount/100.0)
    else:
        raise ValueError(kind)
    return ballistics(desired,item["sr"])

def metrics(item,actual):
    vals=actual[item["mask"]]
    trend=uniform_filter1d(actual,size=max(1,int(.04*item["sr"])),mode="nearest")
    ripple=float(np.std((actual-trend)[item["mask"]]))
    return {
        "mean_gr":float(np.mean(vals)),
        "p95_gr":float(np.percentile(vals,95)),
        "p99_gr":float(np.percentile(vals,99)),
        "max_gr":float(np.max(vals)),
        "frac_gt10":float(np.mean(vals>10.0)),
        "gr_ripple":ripple,
    }

def summarize(items,kind,target100):
    by={}
    for amount in AMOUNTS:
        rows=[]
        for name,item in items.items():
            m=metrics(item,process(item,kind,target100,amount))
            m["file"]=name
            rows.append(m)
        agg={}
        for k in ("mean_gr","p95_gr","p99_gr","max_gr","frac_gt10","gr_ripple"):
            agg[k]=float(np.mean([r[k] for r in rows]))
        agg["cross_source_mean_gr_std"]=float(np.std([r["mean_gr"] for r in rows]))
        by[str(amount)]={"aggregate":agg,"files":rows}
    means=np.array([by[str(a)]["aggregate"]["mean_gr"] for a in AMOUNTS])
    p95=np.array([by[str(a)]["aggregate"]["p95_gr"] for a in AMOUNTS])
    monotonic=bool(np.all(np.diff(means)>=-1e-4) and np.all(np.diff(p95)>=-0.05))
    return by,monotonic

def gates(by,monotonic):
    A=lambda amount:by[str(amount)]["aggregate"]
    nonzero=[A(a) for a in AMOUNTS if a>0]
    return {
        "amount0_exact_bypass":A(0.0)["max_gr"]<=1e-12,
        "amount25_mean":.75<=A(25.0)["mean_gr"]<=2.25,
        "amount25_p95":A(25.0)["p95_gr"]<=4.0,
        "amount50_mean":2.5<=A(50.0)["mean_gr"]<=3.75,
        "amount50_p95":A(50.0)["p95_gr"]<=6.0,
        "amount50_gt10":A(50.0)["frac_gt10"]<=.005,
        "amount75_mean":3.75<=A(75.0)["mean_gr"]<=5.5,
        "amount75_p99":A(75.0)["p99_gr"]<=9.0,
        "amount100_mean":5.0<=A(100.0)["mean_gr"]<=7.0,
        "amount100_p99":A(100.0)["p99_gr"]<=10.0,
        "amount100_gt10":A(100.0)["frac_gt10"]<=.02,
        "ripple_all":max(x["gr_ripple"] for x in nonzero)<=.08,
        "cross_source_50":A(50.0)["cross_source_mean_gr_std"]<=1.0,
        "monotonic":monotonic,
    }

def flatten_csv(candidate_id,split,by):
    rows=[]
    for amount in AMOUNTS:
        agg=by[str(amount)]["aggregate"]
        rows.append({"candidate":candidate_id,"split":split,"amount":amount,**agg})
    return rows

def choose(selection):
    passing=[x for x in selection if x["passes"]]
    if not passing:
        return None
    top_target=max(x["target100"] for x in passing)
    pool=[x for x in passing if x["target100"]==top_target]
    pool.sort(key=lambda x:(
        x["response"]["100.0"]["aggregate"]["gr_ripple"],
        x["response"]["50.0"]["aggregate"]["cross_source_mean_gr_std"],
        0 if x["kind"]=="desired_gr_scale" else 1,
    ))
    if len(pool)>=2:
        a,b=pool[0],pool[1]
        aa=a["response"]["100.0"]["aggregate"]
        bb=b["response"]["100.0"]["aggregate"]
        safety_equiv=(
            abs(aa["gr_ripple"]-bb["gr_ripple"])<=.002
            and abs(
                a["response"]["50.0"]["aggregate"]["cross_source_mean_gr_std"]
                -b["response"]["50.0"]["aggregate"]["cross_source_mean_gr_std"]
            )<=.05
            and abs(aa["p99_gr"]-bb["p99_gr"])<=.10
        )
        if safety_equiv:
            simple=[x for x in pool[:2] if x["kind"]=="desired_gr_scale"]
            if simple:
                return simple[0]
    return pool[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()
    out=Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cipi-hust-solfege-") as tmp:
        td=Path(tmp)
        z=td/"HUST_Solfege.zip"
        download_hust_zip(z)
        files=extract_selected(z,td)
        selection={s:prepare_item(files[s]) for s in SELECTION_STEMS}
        holdout={s:prepare_item(files[s]) for s in HOLDOUT_STEMS}

        candidates=[]
        for target100 in (5.0,5.2,5.4,5.5):
            for kind in ("anchor_threshold","desired_gr_scale"):
                cid=f"{kind}_target100_{target100:.1f}"
                by,mono=summarize(selection,kind,target100)
                gs=gates(by,mono)
                candidates.append({
                    "id":cid,
                    "kind":kind,
                    "target100":target100,
                    "response":by,
                    "gates":gs,
                    "passes":all(gs.values()),
                })

        selected=choose(candidates)
        selection_rows=[]
        for candidate in candidates:
            selection_rows.extend(
                flatten_csv(candidate["id"],"selection",candidate["response"])
            )

        if selected is None:
            decision="REVISE"
            holdout_result=None
            holdout_rows=[]
            acceptance=False
        else:
            hby,hmono=summarize(holdout,selected["kind"],selected["target100"])
            hgs=gates(hby,hmono)
            holdout_result={
                "id":selected["id"],
                "kind":selected["kind"],
                "target100":selected["target100"],
                "response":hby,
                "gates":hgs,
                "passes":all(hgs.values()),
            }
            holdout_rows=flatten_csv(selected["id"],"holdout",hby)
            acceptance=bool(holdout_result["passes"])
            decision="GO_FOR_BLIND" if acceptance else "REVISE"

        result={
            "decision":decision,
            "selection_speakers":list(SELECTION_STEMS),
            "holdout_speakers":list(HOLDOUT_STEMS),
            "candidate_definitions":{
                "anchor_25_target":1.0,
                "anchor_50_target":2.5,
                "anchor_75_target":4.0,
                "target100_candidates":[5.0,5.2,5.4,5.5],
                "target100_offsets":TARGET100_OFFSETS,
                "amounts":list(AMOUNTS),
                "learn_seconds":LEARN_SECONDS,
            },
            "selection_candidates":candidates,
            "selected_before_holdout":None if selected is None else {
                "id":selected["id"],
                "kind":selected["kind"],
                "target100":selected["target100"],
            },
            "final_holdout":holdout_result,
            "acceptance_met":acceptance,
        }
        (out/"amount_r2_results.json").write_text(
            json.dumps(result,indent=2),encoding="utf-8"
        )

        fields=[
            "candidate","split","amount","mean_gr","p95_gr","p99_gr","max_gr",
            "frac_gt10","gr_ripple","cross_source_mean_gr_std"
        ]
        for name,rows in (("selection.csv",selection_rows),("holdout.csv",holdout_rows)):
            with (out/name).open("w",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

        lines=[
            "# Vo.Prep Amount Mapping Revision 2",
            "",
            f"Decision: {decision}",
            f"Selection speakers: {', '.join(SELECTION_STEMS)}",
            f"Final holdout speakers: {', '.join(HOLDOUT_STEMS)}",
            "",
            "Original 0.08 dB ripple gate was retained unchanged.",
        ]
        if selected is not None:
            lines.extend([
                "",
                f"Selected before holdout: {selected['id']}",
                f"Selection passes: {selected['passes']}",
                f"Final holdout passes: {holdout_result['passes']}",
                "",
                "Final holdout gates:",
                json.dumps(holdout_result["gates"],indent=2),
            ])
        (out/"amount_r2_report.md").write_text(
            "\n".join(lines)+"\n",encoding="utf-8"
        )
        print((out/"amount_r2_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
