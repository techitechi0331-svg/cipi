#!/usr/bin/env python3
"""Leak-free Vo.Prep Amount Revision 3 on VocalSet.

Raw public audio is streamed and decoded in runner memory only.
No raw audio is written to the repository or output directory.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
from datasets import Audio, load_dataset
from scipy.ndimage import uniform_filter1d
from scipy.signal import lfilter, resample_poly

DATASET = "Bill13579/vocalset-mirror"
FS = 24000

SLOW_MS = 25.0
ATTACK_MS = 8.0
RELEASE_MS = 70.0
RATIO = 1.5
KNEE_DB = 18.0
LEARN_SECONDS = 4.0
AMOUNTS = (0.0,12.5,25.0,37.5,50.0,62.5,75.0,87.5,100.0)

SELECTION_SINGERS = ("f1","f2","m1","m2")
HOLDOUT_SINGERS = ("f3","f4","m3","m4")
FILES_PER_SINGER = 2
SELECTION_RIPPLE_MARGIN_DB = 0.075
FINAL_RIPPLE_GATE_DB = 0.080

TARGET100_OFFSETS = {
    5.0: -14.864720702171326,
    5.2: -15.492585062980652,
    5.3: -15.806517243385315,
    5.4: -16.120449423789978,
    5.5: -16.43438160419464,
}
TARGETS = tuple(sorted(TARGET100_OFFSETS))

def singer_id_from_path(source_path: str) -> str:
    name = Path(source_path).name.lower()
    m = re.match(r"([fm]\d+)_", name)
    if m:
        return m.group(1)
    for part in Path(source_path).parts:
        p = part.lower()
        m = re.match(r"(female|male)(\d+)$", p)
        if m:
            return ("f" if m.group(1) == "female" else "m") + m.group(2)
    return "unknown"

def to_mono_resampled(data: bytes) -> np.ndarray:
    x, sr = sf.read(io.BytesIO(data), always_2d=True, dtype="float64")
    x = np.mean(x, axis=1)
    if not np.all(np.isfinite(x)):
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    if int(sr) != FS:
        g = math.gcd(int(sr), FS)
        x = resample_poly(x, FS // g, int(sr) // g)
    peak = float(np.max(np.abs(x))) if len(x) else 0.0
    if peak > 1.0:
        x = x / peak
    return np.asarray(x, dtype=np.float64)

def best_energy_segment(x: np.ndarray, seconds: float = 10.0) -> np.ndarray:
    n = int(seconds * FS)
    if len(x) <= n:
        return x
    hop = FS
    best_start = 0
    best_rms = -1.0
    for start in range(0, len(x)-n+1, hop):
        seg = x[start:start+n]
        rms = float(np.sqrt(np.mean(seg*seg)+1e-18))
        if rms > best_rms:
            best_rms = rms
            best_start = start
    return x[best_start:best_start+n]

def collect_examples(scan_limit: int = 10000):
    wanted = set(SELECTION_SINGERS + HOLDOUT_SINGERS)
    ds = load_dataset(DATASET, split="train", streaming=True)
    ds = ds.cast_column("audio", Audio(decode=False))

    per_singer = defaultdict(int)
    per_singer_label = defaultdict(int)
    selected = {}

    for idx, row in enumerate(ds):
        if idx >= scan_limit:
            break
        cell = row.get("audio")
        if not isinstance(cell, dict):
            continue
        source_path = str(cell.get("path") or "")
        singer = singer_id_from_path(source_path)
        if singer not in wanted or per_singer[singer] >= FILES_PER_SINGER:
            continue

        label = str(row.get("label", "unknown"))
        if per_singer_label[(singer,label)] >= 1:
            continue

        data = cell.get("bytes")
        if data is None:
            continue
        try:
            x = best_energy_segment(to_mono_resampled(data))
        except Exception:
            continue
        if len(x) < int((LEARN_SECONDS + 1.0) * FS):
            continue
        if float(np.sqrt(np.mean(x*x)+1e-18)) < 1e-4:
            continue

        # "Qualifying file" means it can actually supply the declared 4 s
        # active Learn window plus at least 1 s of active post-lock evaluation.
        # This is an eligibility check only; no Amount candidate is evaluated.
        qslow = slow_detector(x)
        qslow_db = db_amp(qslow)
        qfinite = np.isfinite(qslow_db) & (qslow_db > -180.0)
        qpeak = float(np.max(qslow_db[qfinite])) if np.any(qfinite) else -180.0
        qactive = qfinite & (qslow_db >= qpeak - 30.0)
        if int(np.sum(qactive)) < int((LEARN_SECONDS + 1.0) * FS):
            continue

        key = f"{singer}:{Path(source_path).name}"
        selected[key] = {
            "singer": singer,
            "label": label,
            "source_basename": Path(source_path).name,
            "x": x,
        }
        per_singer[singer] += 1
        per_singer_label[(singer,label)] += 1

        if all(per_singer[s] >= FILES_PER_SINGER for s in wanted):
            break

    missing = {s: FILES_PER_SINGER-per_singer[s] for s in wanted if per_singer[s] < FILES_PER_SINGER}
    if missing:
        raise RuntimeError(f"Insufficient VocalSet examples: {missing}")
    return selected

def db_amp(x):
    return 20.0*np.log10(np.maximum(np.abs(x),1e-12))

def slow_detector(x):
    a = math.exp(-1.0/(FS*SLOW_MS*1e-3))
    e = lfilter([1.0-a],[1.0,-a],x*x)
    return np.sqrt(np.maximum(e,1e-24))

def soft_knee_gr(level,threshold):
    u = np.asarray(level,dtype=np.float64)-threshold
    half = KNEE_DB*0.5
    frac = 1.0-1.0/RATIO
    q = np.zeros_like(u)
    hi = u > half
    mid = (u >= -half) & (~hi)
    q[hi] = frac*u[hi]
    z = u[mid] + half
    q[mid] = frac*(z*z)/(2.0*KNEE_DB)
    return np.maximum(q,0.0)

def ballistics(desired):
    aa = math.exp(-1.0/(FS*ATTACK_MS*1e-3))
    ar = math.exp(-1.0/(FS*RELEASE_MS*1e-3))
    out = np.empty_like(desired)
    state = 0.0
    for i,v in enumerate(desired):
        fv=float(v)
        a=aa if fv>state else ar
        state=a*state+(1.0-a)*fv
        out[i]=state
    return out

def prepare_item(ex):
    x = ex["x"]
    slow = slow_detector(x)
    slow_db = db_amp(slow)
    fast_db = db_amp(x)
    effective = np.maximum(slow_db, fast_db-6.0)

    finite = np.isfinite(slow_db) & (slow_db > -180.0)
    peak = float(np.max(slow_db[finite])) if np.any(finite) else -180.0
    active = finite & (slow_db >= peak-30.0)
    idx = np.flatnonzero(active)
    need = int(round(LEARN_SECONDS*FS))
    if len(idx) < need:
        raise RuntimeError(f"{ex['source_basename']}: fewer than 4 s active samples")
    learn_idx = idx[:need]
    ref = float(np.median(slow_db[learn_idx]))
    lock = int(learn_idx[-1])
    mask = active.copy()
    mask[:lock+1] = False
    if np.sum(mask) < FS:
        raise RuntimeError(f"{ex['source_basename']}: less than 1 s eval after Learn")
    return {**ex, "effective":effective, "ref":ref, "mask":mask}

def full_amount_actual(item,target100):
    threshold = item["ref"] + TARGET100_OFFSETS[target100]
    desired100 = soft_knee_gr(item["effective"],threshold)
    return ballistics(desired100)

def scaled_actual_from_full(actual100,amount):
    if amount <= 0.0:
        return np.zeros_like(actual100)
    return actual100*(amount/100.0)

def metrics(item,actual):
    vals = actual[item["mask"]]
    trend = uniform_filter1d(actual,size=max(1,int(.04*FS)),mode="nearest")
    return {
        "mean_gr":float(np.mean(vals)),
        "p95_gr":float(np.percentile(vals,95)),
        "p99_gr":float(np.percentile(vals,99)),
        "max_gr":float(np.max(vals)),
        "frac_gt10":float(np.mean(vals>10.0)),
        "gr_ripple":float(np.std((actual-trend)[item["mask"]])),
    }

def summarize(items,target100):
    # Exact positive-scaling homogeneity of the frozen attack/release state:
    # B(c*d) = c*B(d). Branch selection is preserved because both DesiredGR
    # and the previous state scale by the same positive c.
    full={name:full_amount_actual(item,target100) for name,item in items.items()}

    first_name=next(iter(items))
    first_item=items[first_name]
    threshold=first_item["ref"]+TARGET100_OFFSETS[target100]
    direct50=ballistics(0.5*soft_knee_gr(first_item["effective"],threshold))
    homogeneity_error=float(np.max(np.abs(direct50-0.5*full[first_name])))
    if homogeneity_error>1.0e-10:
        raise RuntimeError(f"Ballistics homogeneity assertion failed: {homogeneity_error}")

    by={}
    for amount in AMOUNTS:
        rows=[]
        for name,item in items.items():
            m=metrics(item,scaled_actual_from_full(full[name],amount))
            m["file"]=name
            m["singer"]=item["singer"]
            rows.append(m)
        agg={}
        for k in ("mean_gr","p95_gr","p99_gr","max_gr","frac_gt10","gr_ripple"):
            agg[k]=float(np.mean([r[k] for r in rows]))
        singer_means=defaultdict(list)
        for r in rows:
            singer_means[r["singer"]].append(r["mean_gr"])
        per_singer=[float(np.mean(v)) for v in singer_means.values()]
        agg["cross_source_mean_gr_std"]=float(np.std(per_singer))
        agg["ballistics_homogeneity_max_error"]=homogeneity_error
        by[str(amount)]={"aggregate":agg,"files":rows}

    means=np.asarray([by[str(a)]["aggregate"]["mean_gr"] for a in AMOUNTS])
    p95=np.asarray([by[str(a)]["aggregate"]["p95_gr"] for a in AMOUNTS])
    monotonic=bool(np.all(np.diff(means)>=-1e-4) and np.all(np.diff(p95)>=-0.05))
    return by,monotonic

def gates(by,monotonic,ripple_limit):
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
        "ripple_all":max(x["gr_ripple"] for x in nonzero)<=ripple_limit,
        "cross_source_50":A(50.0)["cross_source_mean_gr_std"]<=1.0,
        "monotonic":monotonic,
    }

def flatten(candidate,split,by):
    rows=[]
    for amount in AMOUNTS:
        rows.append({
            "candidate":candidate,
            "split":split,
            "amount":amount,
            **by[str(amount)]["aggregate"],
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--scan-limit",type=int,default=10000)
    args=ap.parse_args()
    out=Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)

    examples=collect_examples(args.scan_limit)
    prepared={k:prepare_item(v) for k,v in examples.items()}
    selection={k:v for k,v in prepared.items() if v["singer"] in SELECTION_SINGERS}
    holdout={k:v for k,v in prepared.items() if v["singer"] in HOLDOUT_SINGERS}

    selection_results=[]
    selection_rows=[]
    for target in TARGETS:
        by,mono=summarize(selection,target)
        original_gates=gates(by,mono,FINAL_RIPPLE_GATE_DB)
        margin_gates=gates(by,mono,SELECTION_RIPPLE_MARGIN_DB)
        passes=all(margin_gates.values())
        row={
            "id":f"desired_gr_scale_target100_{target:.1f}",
            "target100":target,
            "response":by,
            "original_gates":original_gates,
            "selection_margin_gates":margin_gates,
            "passes_selection_margin":passes,
        }
        selection_results.append(row)
        selection_rows.extend(flatten(row["id"],"selection",by))

    passing=[x for x in selection_results if x["passes_selection_margin"]]
    passing.sort(key=lambda x:x["target100"],reverse=True)
    selected=passing[0] if passing else None

    if selected is None:
        decision="REVISE"
        final=None
        holdout_rows=[]
        acceptance=False
    else:
        hby,hmono=summarize(holdout,selected["target100"])
        hgs=gates(hby,hmono,FINAL_RIPPLE_GATE_DB)
        final={
            "id":selected["id"],
            "target100":selected["target100"],
            "response":hby,
            "gates":hgs,
            "passes":all(hgs.values()),
        }
        holdout_rows=flatten(selected["id"],"holdout",hby)
        acceptance=bool(final["passes"])
        decision="GO_FOR_BLIND" if acceptance else "REVISE"

    result={
        "decision":decision,
        "dataset":DATASET,
        "selection_singers":list(SELECTION_SINGERS),
        "holdout_singers":list(HOLDOUT_SINGERS),
        "files_per_singer":FILES_PER_SINGER,
        "selection_ripple_margin_db":SELECTION_RIPPLE_MARGIN_DB,
        "final_ripple_gate_db":FINAL_RIPPLE_GATE_DB,
        "candidate_targets":list(TARGETS),
        "candidate_offsets":TARGET100_OFFSETS,
        "selection_candidates":selection_results,
        "selected_before_holdout":None if selected is None else {
            "id":selected["id"],"target100":selected["target100"]
        },
        "final_holdout":final,
        "acceptance_met":acceptance,
        "raw_audio_persisted":False,
    }
    (out/"amount_r3_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    fields=["candidate","split","amount","mean_gr","p95_gr","p99_gr","max_gr","frac_gt10","gr_ripple","cross_source_mean_gr_std"]
    for name,rows in (("selection.csv",selection_rows),("holdout.csv",holdout_rows)):
        with (out/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields)
            w.writeheader();w.writerows(rows)

    lines=[
        "# Vo.Prep Amount Mapping Revision 3 — VocalSet",
        "",
        f"Decision: {decision}",
        f"Selection singers: {', '.join(SELECTION_SINGERS)}",
        f"Final holdout singers: {', '.join(HOLDOUT_SINGERS)}",
        f"Selection ripple margin: {SELECTION_RIPPLE_MARGIN_DB:.6f} dB",
        f"Final ripple gate: {FINAL_RIPPLE_GATE_DB:.6f} dB",
        "",
        "The final 0.08 dB gate is unchanged from R1/R2.",
    ]
    if selected is not None:
        lines += [
            "",
            f"Selected before holdout: {selected['id']}",
            f"Final holdout passes: {final['passes']}",
            "",
            "Final holdout gates:",
            json.dumps(final["gates"],indent=2),
        ]
    (out/"amount_r3_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print((out/"amount_r3_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
