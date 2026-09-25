#!/usr/bin/env python3
"""Vo.Prep detector-side 40 Hz HPF real-vocal validation.

Synthetic pilot already selected 40 Hz / 12 dB-oct as the lowest passing
candidate. This study compares only OFF versus that frozen candidate.

Raw VocalSet audio is streamed/decoded in runner memory only.
"""
from __future__ import annotations

import argparse, csv, importlib.util, json, math
from pathlib import Path
import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt, sosfilt_zi, lfilter

HERE=Path(__file__).resolve().parent
R4_PATH=HERE/"amount_mapping_r4_learn_solve.py"
spec=importlib.util.spec_from_file_location("r4_sc_hpf",R4_PATH)
r4=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r4)

VALIDATION_SINGERS=("f1","f2","m1","m2")
CONFIRM_SINGERS=("f3","f4","m3","m4")
FILES_PER_SINGER=2
HPF_HZ=40.0
TARGET_CLEAN_MEAN_GR=3.0
RUMBLE_HZ=30.0
RUMBLE_REL_DB=(-12.0,-6.0)
PLOSIVE_REL_DB=6.0

def detector_hpf(x):
    sos=butter(2,HPF_HZ/(r4.FS*.5),btype="highpass",output="sos")
    zi=sosfilt_zi(sos)*float(x[0])
    y,_=sosfilt(sos,x,zi=zi)
    return y

def effective_from_detector(det):
    slow=r4.slow_detector(det)
    slow_db=r4.db_amp(slow)
    fast_db=r4.db_amp(det)
    return np.maximum(slow_db,fast_db-6.0)

def actual_gr(det,threshold):
    eff=effective_from_detector(det)
    return r4.ballistics(r4.soft_knee_gr(eff,threshold))

def active_mask(x):
    slow_db=r4.db_amp(r4.slow_detector(x))
    m=r4.activity_mask(slow_db)
    if m is None or int(np.sum(m))<int(2.0*r4.FS):
        raise RuntimeError("insufficient active vocal")
    return m

def solve_clean_threshold(x,mask):
    lo,hi=-120.0,40.0
    def mean_at(th):
        g=actual_gr(x,th)
        return float(np.mean(g[mask]))
    mlo,mhi=mean_at(lo),mean_at(hi)
    if mlo<TARGET_CLEAN_MEAN_GR or mhi>TARGET_CLEAN_MEAN_GR:
        raise RuntimeError(f"threshold target not bracketed lo={mlo} hi={mhi}")
    for _ in range(22):
        mid=.5*(lo+hi)
        if mean_at(mid)>TARGET_CLEAN_MEAN_GR: lo=mid
        else: hi=mid
    th=.5*(lo+hi)
    achieved=mean_at(th)
    return th,abs(achieved-TARGET_CLEAN_MEAN_GR)

def gr_metrics(gr,mask):
    vals=gr[mask]
    trend=uniform_filter1d(gr,size=max(1,int(.04*r4.FS)),mode="nearest")
    return {
        "mean_gr":float(np.mean(vals)),
        "p95_gr":float(np.percentile(vals,95)),
        "p99_gr":float(np.percentile(vals,99)),
        "ripple":float(np.std((gr-trend)[mask])),
    }

def active_rms(x,mask):
    return float(np.sqrt(np.mean(np.square(x[mask]))+1e-18))

def add_rumble(x,mask,rel_db):
    t=np.arange(len(x),dtype=np.float64)/r4.FS
    target=active_rms(x,mask)*(10.0**(rel_db/20.0))
    amp=target*math.sqrt(2.0)
    return x+amp*np.sin(2*np.pi*RUMBLE_HZ*t+0.37)

def plosive_overlay(x,mask):
    y=x.copy()
    idx=np.flatnonzero(mask)
    if len(idx)==0:
        raise RuntimeError("no active samples")
    start=int(idx[min(len(idx)-1,int(.20*len(idx)))])
    n=int(.090*r4.FS)
    start=min(start,max(0,len(x)-n-1))
    t=np.arange(n,dtype=np.float64)/r4.FS
    env=np.exp(-t/.024)
    rng=np.random.default_rng(20260926)
    noise=rng.standard_normal(n)
    b,a=butter(2,180.0/(r4.FS*.5),btype="lowpass")
    noise=lfilter(b,a,noise)
    burst=(np.sin(2*np.pi*55.0*t)+0.35*noise)*env
    brms=float(np.sqrt(np.mean(burst*burst)+1e-18))
    target=active_rms(x,mask)*(10.0**(PLOSIVE_REL_DB/20.0))
    burst*=target/max(brms,1e-12)
    y[start:start+n]+=burst
    return y,start,n

def analyze_file(item):
    x=item["x"]
    mask=active_mask(x)
    th,resid=solve_clean_threshold(x,mask)

    off_clean=actual_gr(x,th)
    hp_clean=actual_gr(detector_hpf(x),th)
    mo=gr_metrics(off_clean,mask)
    mh=gr_metrics(hp_clean,mask)

    rumble_rows=[]
    for rel in RUMBLE_REL_DB:
        stressed=add_rumble(x,mask,rel)
        off=actual_gr(stressed,th)
        hp=actual_gr(detector_hpf(stressed),th)
        om=float(np.mean(off[mask]))
        hm=float(np.mean(hp[mask]))
        off_ex=max(0.0,om-mo["mean_gr"])
        hp_ex=max(0.0,hm-mh["mean_gr"])
        reduction=1.0-hp_ex/max(off_ex,1e-9)
        rumble_rows.append({
            "rel_db":rel,"off_excess_mean_gr":off_ex,
            "hpf_excess_mean_gr":hp_ex,"reduction":reduction,
        })

    stressed,start,n=plosive_overlay(x,mask)
    offp=actual_gr(stressed,th)
    hpp=actual_gr(detector_hpf(stressed),th)
    lo=max(0,start-int(.02*r4.FS))
    hi=min(len(x),start+n+int(.12*r4.FS))
    clean_off_peak=float(np.max(off_clean[lo:hi]))
    clean_hp_peak=float(np.max(hp_clean[lo:hi]))
    off_ex=max(0.0,float(np.max(offp[lo:hi]))-clean_off_peak)
    hp_ex=max(0.0,float(np.max(hpp[lo:hi]))-clean_hp_peak)
    plosive_reduction=1.0-hp_ex/max(off_ex,1e-9)

    return {
        "threshold_db":th,
        "solver_residual_db":resid,
        "clean_off":mo,
        "clean_hpf":mh,
        "clean_mean_delta_db":mh["mean_gr"]-mo["mean_gr"],
        "clean_p95_delta_db":mh["p95_gr"]-mo["p95_gr"],
        "clean_ripple_delta_db":mh["ripple"]-mo["ripple"],
        "rumble":rumble_rows,
        "plosive_off_excess_gr":off_ex,
        "plosive_hpf_excess_gr":hp_ex,
        "plosive_reduction":plosive_reduction,
    }

def cohort(singers,scan_limit):
    examples=r4.collect_examples(singers,scan_limit)
    rows=[]
    detail={}
    for name,ex in examples.items():
        a=analyze_file(ex)
        detail[name]={"singer":ex["singer"],**a}
        for rr in a["rumble"]:
            rows.append({
                "file":name,"singer":ex["singer"],"stress":f"rumble_{rr['rel_db']:g}",
                "clean_mean_delta_db":a["clean_mean_delta_db"],
                "clean_p95_delta_db":a["clean_p95_delta_db"],
                "clean_ripple_delta_db":a["clean_ripple_delta_db"],
                "stress_reduction":rr["reduction"],
                "solver_residual_db":a["solver_residual_db"],
            })
        rows.append({
            "file":name,"singer":ex["singer"],"stress":"plosive",
            "clean_mean_delta_db":a["clean_mean_delta_db"],
            "clean_p95_delta_db":a["clean_p95_delta_db"],
            "clean_ripple_delta_db":a["clean_ripple_delta_db"],
            "stress_reduction":a["plosive_reduction"],
            "solver_residual_db":a["solver_residual_db"],
        })

    vals=list(detail.values())
    rumble=[rr["reduction"] for v in vals for rr in v["rumble"]]
    plosive=[v["plosive_reduction"] for v in vals]
    male=[abs(v["clean_mean_delta_db"]) for v in vals if v["singer"].startswith("m")]
    agg={
        "file_count":len(vals),
        "clean_abs_mean_delta_db":float(np.mean([abs(v["clean_mean_delta_db"]) for v in vals])),
        "clean_abs_p95_delta_db":float(np.mean([abs(v["clean_p95_delta_db"]) for v in vals])),
        "clean_abs_ripple_delta_db":float(np.mean([abs(v["clean_ripple_delta_db"]) for v in vals])),
        "male_clean_abs_mean_delta_db":float(np.mean(male)) if male else 0.0,
        "rumble_reduction_mean":float(np.mean(rumble)),
        "rumble_positive_fraction":float(np.mean(np.asarray(rumble)>0.0)),
        "plosive_reduction_mean":float(np.mean(plosive)),
        "plosive_positive_fraction":float(np.mean(np.asarray(plosive)>0.0)),
        "solver_max_residual_db":float(max(v["solver_residual_db"] for v in vals)),
    }
    gates={
        "clean_mean_preservation":agg["clean_abs_mean_delta_db"]<=0.15,
        "clean_p95_preservation":agg["clean_abs_p95_delta_db"]<=0.25,
        "clean_ripple_preservation":agg["clean_abs_ripple_delta_db"]<=0.015,
        "male_body_preservation":agg["male_clean_abs_mean_delta_db"]<=0.20,
        "rumble_reduction_ge_50pct":agg["rumble_reduction_mean"]>=0.50,
        "rumble_consistency_ge_75pct":agg["rumble_positive_fraction"]>=0.75,
        "plosive_reduction_ge_15pct":agg["plosive_reduction_mean"]>=0.15,
        "plosive_consistency_ge_75pct":agg["plosive_positive_fraction"]>=0.75,
        "solver_residual":agg["solver_max_residual_db"]<=0.02,
    }
    return {"aggregate":agg,"gates":gates,"passes":all(gates.values()),"detail":detail},rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--scan-limit",type=int,default=14000)
    args=ap.parse_args()
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

    validation,rows=cohort(VALIDATION_SINGERS,args.scan_limit)
    confirmation=None
    if validation["passes"]:
        # Confirmation audio is not touched unless the first real-vocal cohort passes.
        confirmation,crows=cohort(CONFIRM_SINGERS,args.scan_limit)
        rows.extend(crows)

    acceptance=bool(validation["passes"] and confirmation and confirmation["passes"])
    decision="GO_TO_BLIND" if acceptance else "REVISE"
    result={
        "decision":decision,
        "candidate":{"hpf_hz":HPF_HZ,"order":2},
        "validation_singers":list(VALIDATION_SINGERS),
        "confirmation_singers":list(CONFIRM_SINGERS),
        "validation":validation,
        "confirmation":confirmation,
        "confirmation_accessed":confirmation is not None,
        "acceptance_met":acceptance,
        "raw_audio_persisted":False,
    }
    (out/"sidechain_hpf_real_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    fields=["file","singer","stress","clean_mean_delta_db","clean_p95_delta_db","clean_ripple_delta_db","stress_reduction","solver_residual_db"]
    with (out/"sidechain_hpf_real_metrics.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

    report=[
        "# Vo.Prep 40 Hz Sidechain HPF — Real Vocal Validation","",
        f"Decision: {decision}",
        f"Validation passes: {validation['passes']}",
        f"Validation rumble reduction: {validation['aggregate']['rumble_reduction_mean']*100:.2f}%",
        f"Validation plosive reduction: {validation['aggregate']['plosive_reduction_mean']*100:.2f}%",
        f"Validation clean mean |delta|: {validation['aggregate']['clean_abs_mean_delta_db']:.4f} dB",
        f"Confirmation accessed: {confirmation is not None}",
    ]
    if confirmation:
        report += [
            f"Confirmation passes: {confirmation['passes']}",
            f"Confirmation rumble reduction: {confirmation['aggregate']['rumble_reduction_mean']*100:.2f}%",
            f"Confirmation plosive reduction: {confirmation['aggregate']['plosive_reduction_mean']*100:.2f}%",
            f"Confirmation clean mean |delta|: {confirmation['aggregate']['clean_abs_mean_delta_db']:.4f} dB",
        ]
    (out/"sidechain_hpf_real_report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print((out/"sidechain_hpf_real_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
