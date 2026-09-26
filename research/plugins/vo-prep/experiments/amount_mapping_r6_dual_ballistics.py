#!/usr/bin/env python3
"""Vo.Prep Amount R6: current 8/70 shared ballistics vs dual Peak Assist.

Research only. The detector/static curve remain frozen.
Simple baseline:
  Effective=max(Slow, Fast-6 dB) -> curve -> shared 8/70.
Candidate reuses the previously validated Peak Assist principle but updates the
Body path to the current 8/70 core:
  BodyDesired=curve(Slow)
  TotalDesired=curve(max(Slow, Fast-6.5 dB))
  PeakExtra=max(TotalDesired-BodyDesired, 0)
  BodyActual=8/70
  PeakExtraActual=3/20
  ActualGR=BodyActual+PeakExtraActual
One audio gain cell is implied by summed GR.

Selection singers f7/f8/m7/m8 are already exposed in earlier Amount work.
Fresh holdout f9/m9/m10/m11 is not accessed unless selection passes all gates.
"""
from __future__ import annotations

import argparse, csv, importlib.util, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.ndimage import uniform_filter1d

HERE=Path(__file__).resolve().parent
R4_PATH=HERE/"amount_mapping_r4_learn_solve.py"
spec=importlib.util.spec_from_file_location("r4_r6",R4_PATH)
r4=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r4)

SELECTION_SINGERS=("f7","f8","m7","m8")
HOLDOUT_SINGERS=("f9","m9","m10","m11")
FILES_PER_SINGER=2
AMOUNTS=r4.AMOUNTS
TARGET_MEAN_GR=5.5
BASE_CREST_DB=6.0
PEAK_CREST_DB=6.5
BODY_ATTACK_MS=8.0
BODY_RELEASE_MS=70.0
PEAK_ATTACK_MS=3.0
PEAK_RELEASE_MS=20.0
SELECTION_RIPPLE_LIMIT=0.075
FINAL_RIPPLE_LIMIT=0.080
SELECTION_MAPPING_RMSE_MAX=0.50
HOLDOUT_MAPPING_RMSE_MAX=0.65
SOLVER_RESIDUAL_MAX=0.02
GAIN_INVARIANCE_MAX=0.005
MIN_RIPPLE_IMPROVEMENT=0.15
MIN_EVENT_CONTRAST_GAIN_DB=0.15
MAX_NONEVENT_P95_DELTA_DB=0.25

EXPECTED={25.0:1.375,50.0:2.75,75.0:4.125,100.0:5.5}

def coeff(ms):
    return math.exp(-1.0/(r4.FS*ms*1e-3))

def ballistic(desired,attack_ms,release_ms):
    aa=coeff(attack_ms); ar=coeff(release_ms)
    out=np.empty_like(desired,dtype=np.float64)
    state=0.0
    for i,v in enumerate(desired):
        fv=float(v)
        a=aa if fv>state else ar
        state=a*state+(1-a)*fv
        out[i]=state
    return out

def level_fields(x):
    slow=r4.slow_detector(x)
    slow_db=r4.db_amp(slow)
    fast_db=r4.db_amp(x)
    return slow_db,fast_db

def baseline_actual_from_fields(slow_db,fast_db,threshold):
    eff=np.maximum(slow_db,fast_db-BASE_CREST_DB)
    desired=r4.soft_knee_gr(eff,threshold)
    return ballistic(desired,BODY_ATTACK_MS,BODY_RELEASE_MS)

def dual_actual_from_fields(slow_db,fast_db,threshold):
    body_desired=r4.soft_knee_gr(slow_db,threshold)
    total_eff=np.maximum(slow_db,fast_db-PEAK_CREST_DB)
    total_desired=r4.soft_knee_gr(total_eff,threshold)
    peak_desired=np.maximum(total_desired-body_desired,0.0)
    body=ballistic(body_desired,BODY_ATTACK_MS,BODY_RELEASE_MS)
    peak=ballistic(peak_desired,PEAK_ATTACK_MS,PEAK_RELEASE_MS)
    return body+peak,body,peak

def prepare(ex):
    item=r4.prepare_item(ex)
    learn_x=ex["x"][:int(round(r4.LEARN_SECONDS*r4.FS))]
    eval_x=ex["x"][int(round(r4.LEARN_SECONDS*r4.FS)):]
    ls,lf=level_fields(learn_x)
    es,ef=level_fields(eval_x)
    return {
        **item,
        "learn_slow_db":ls,"learn_fast_db":lf,
        "eval_slow_db":es,"eval_fast_db":ef,
    }

def mean_for_threshold(item,arch,threshold):
    if arch=="shared_8_70":
        a=baseline_actual_from_fields(item["learn_slow_db"],item["learn_fast_db"],threshold)
    elif arch=="dual_8_70_plus_3_20":
        a,_,_=dual_actual_from_fields(item["learn_slow_db"],item["learn_fast_db"],threshold)
    else: raise ValueError(arch)
    return float(np.mean(a[item["learn_active"]]))

def solve(item,arch,target=TARGET_MEAN_GR):
    lo,hi=-120.0,40.0
    mlo=mean_for_threshold(item,arch,lo)
    mhi=mean_for_threshold(item,arch,hi)
    if mlo<target or mhi>target:
        raise RuntimeError(f"{item['source_basename']}: target not bracketed {arch}: {mlo}, {mhi}")
    for _ in range(22):
        mid=.5*(lo+hi)
        m=mean_for_threshold(item,arch,mid)
        if m>target: lo=mid
        else: hi=mid
    th=.5*(lo+hi)
    achieved=mean_for_threshold(item,arch,th)
    return {"threshold":th,"residual":abs(achieved-target),"achieved":achieved}

def full_eval(item,arch,threshold):
    if arch=="shared_8_70":
        total=baseline_actual_from_fields(item["eval_slow_db"],item["eval_fast_db"],threshold)
        return total,np.zeros_like(total)
    total,body,peak=dual_actual_from_fields(item["eval_slow_db"],item["eval_fast_db"],threshold)
    return total,peak

def metric(item,actual):
    vals=actual[item["eval_active"]]
    trend=uniform_filter1d(actual,size=max(1,int(.04*r4.FS)),mode="nearest")
    return {
        "mean_gr":float(np.mean(vals)),
        "p95_gr":float(np.percentile(vals,95)),
        "p99_gr":float(np.percentile(vals,99)),
        "max_gr":float(np.max(vals)),
        "frac_gt10":float(np.mean(vals>10.0)),
        "gr_ripple":float(np.std((actual-trend)[item["eval_active"]])),
    }

def aggregate(rows):
    keys=("mean_gr","p95_gr","p99_gr","max_gr","frac_gt10","gr_ripple")
    out={k:float(np.mean([r[k] for r in rows])) for k in keys}
    by=defaultdict(list)
    for r in rows: by[r["singer"]].append(r["mean_gr"])
    out["cross_source_mean_gr_std"]=float(np.std([np.mean(v) for v in by.values()]))
    return out

def summarize(items,arch):
    sols={}
    full={}
    peak={}
    for name,item in items.items():
        sol=solve(item,arch)
        sols[name]=sol
        full[name],peak[name]=full_eval(item,arch,sol["threshold"])
    by={}
    for amount in AMOUNTS:
        rows=[]
        for name,item in items.items():
            actual=np.zeros_like(full[name]) if amount<=0 else full[name]*(amount/100.0)
            m=metric(item,actual);m.update({"file":name,"singer":item["singer"]})
            rows.append(m)
        by[str(amount)]={"aggregate":aggregate(rows),"files":rows}
    solver={
        "max_residual_db":max(v["residual"] for v in sols.values()),
        "mean_threshold_db":float(np.mean([v["threshold"] for v in sols.values()])),
        "std_threshold_db":float(np.std([v["threshold"] for v in sols.values()])),
    }
    return by,solver,sols,full,peak

def gates(by,ripple_limit):
    A=lambda a:by[str(a)]["aggregate"]
    means=np.array([A(a)["mean_gr"] for a in AMOUNTS])
    p95=np.array([A(a)["p95_gr"] for a in AMOUNTS])
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
        "monotonic":bool(np.all(np.diff(means)>=-1e-6) and np.all(np.diff(p95)>=-1e-6)),
    }

def mapping_rmse(by):
    return float(np.sqrt(np.mean([
        (by[str(a)]["aggregate"]["mean_gr"]-target)**2 for a,target in EXPECTED.items()
    ])))

def event_metrics(items,base_full,cand_full,cand_peak):
    rows=[]
    for name,item in items.items():
        active=item["eval_active"]
        crest=item["eval_fast_db"]-item["eval_slow_db"]
        event=active & (crest>=8.0)
        nonevent=active & (crest<=5.0)
        if int(np.sum(event))<100: continue
        b=base_full[name]; c=cand_full[name]; p=cand_peak[name]
        base_event=float(np.mean(b[event]))
        base_non=float(np.mean(b[nonevent])) if np.any(nonevent) else 0.0
        cand_event=float(np.mean(c[event]))
        cand_non=float(np.mean(c[nonevent])) if np.any(nonevent) else 0.0
        rows.append({
            "file":name,
            "event_contrast_gain_db":(cand_event-cand_non)-(base_event-base_non),
            "event_extra_gr_db":cand_event-base_event,
            "peakextra_event_mean_db":float(np.mean(p[event])),
            "nonevent_abs_delta_p95_db":float(np.percentile(np.abs(c[nonevent]-b[nonevent]),95)) if np.any(nonevent) else 0.0,
        })
    if not rows:
        raise RuntimeError("no qualifying crest events")
    agg={
        "file_count":len(rows),
        "event_contrast_gain_db":float(np.mean([x["event_contrast_gain_db"] for x in rows])),
        "event_extra_gr_db":float(np.mean([x["event_extra_gr_db"] for x in rows])),
        "peakextra_event_mean_db":float(np.mean([x["peakextra_event_mean_db"] for x in rows])),
        "nonevent_abs_delta_p95_db":float(np.mean([x["nonevent_abs_delta_p95_db"] for x in rows])),
        "positive_event_extra_fraction":float(np.mean([x["event_extra_gr_db"]>0 for x in rows])),
    }
    return {"aggregate":agg,"rows":rows}

def gain_invariance(item,arch):
    base=solve(item,arch)
    base_total,_=full_eval(item,arch,base["threshold"])
    base_mean=float(np.mean(base_total[item["eval_active"]]))
    te=[]; ge=[]
    for gain in (-12.,-6.,0.,6.,12.):
        q=dict(item)
        q["learn_slow_db"]=item["learn_slow_db"]+gain
        q["learn_fast_db"]=item["learn_fast_db"]+gain
        q["eval_slow_db"]=item["eval_slow_db"]+gain
        q["eval_fast_db"]=item["eval_fast_db"]+gain
        s=solve(q,arch)
        total,_=full_eval(q,arch,s["threshold"])
        mean=float(np.mean(total[q["eval_active"]]))
        te.append(abs((s["threshold"]-base["threshold"])-gain))
        ge.append(abs(mean-base_mean))
    return {"max_threshold_shift_error_db":max(te),"max_eval_mean_gr_error_db":max(ge)}

def evaluate_cohort(items,ripple_limit,is_selection):
    bb,bs,bsol,bfull,bpeak=summarize(items,"shared_8_70")
    cb,cs,csol,cfull,cpeak=summarize(items,"dual_8_70_plus_3_20")
    bg=gates(bb,ripple_limit); cg=gates(cb,ripple_limit)
    br=mapping_rmse(bb); cr=mapping_rmse(cb)
    ev=event_metrics(items,bfull,cfull,cpeak)
    base_rip=bb["100.0"]["aggregate"]["gr_ripple"]
    cand_rip=cb["100.0"]["aggregate"]["gr_ripple"]
    improvement=1.0-cand_rip/max(base_rip,1e-12)
    extra={
        "mapping_rmse":cr<=(SELECTION_MAPPING_RMSE_MAX if is_selection else HOLDOUT_MAPPING_RMSE_MAX),
        "solver_residual":cs["max_residual_db"]<=SOLVER_RESIDUAL_MAX,
        "ripple_improvement_ge_15pct":improvement>=MIN_RIPPLE_IMPROVEMENT,
        "event_contrast_gain_ge_0_15db":ev["aggregate"]["event_contrast_gain_db"]>=MIN_EVENT_CONTRAST_GAIN_DB,
        "nonevent_p95_delta_le_0_25db":ev["aggregate"]["nonevent_abs_delta_p95_db"]<=MAX_NONEVENT_P95_DELTA_DB,
        "positive_event_extra_fraction_ge_0_60":ev["aggregate"]["positive_event_extra_fraction"]>=.60,
    }
    return {
        "baseline":{"response":bb,"solver":bs,"gates":bg,"mapping_rmse_db":br},
        "candidate":{"response":cb,"solver":cs,"gates":cg,"mapping_rmse_db":cr},
        "event_metrics":ev,
        "ripple_improvement_ratio":improvement,
        "extra_gates":extra,
        "passes":all(cg.values()) and all(extra.values()),
        "_baseline_full":bfull,"_candidate_full":cfull,"_candidate_peak":cpeak,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--scan-limit",type=int,default=15000)
    args=ap.parse_args()
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

    sel_ex=r4.collect_examples(SELECTION_SINGERS,args.scan_limit)
    selection={k:prepare(v) for k,v in sel_ex.items()}
    s=evaluate_cohort(selection,SELECTION_RIPPLE_LIMIT,True)
    probe=selection[sorted(selection)[0]]
    gi=gain_invariance(probe,"dual_8_70_plus_3_20")
    gain_pass=gi["max_threshold_shift_error_db"]<=GAIN_INVARIANCE_MAX and gi["max_eval_mean_gr_error_db"]<=GAIN_INVARIANCE_MAX
    selection_pass=s["passes"] and gain_pass

    # strip large private arrays before JSON
    for k in ("_baseline_full","_candidate_full","_candidate_peak"): s.pop(k,None)

    holdout=None
    if selection_pass:
        h_ex=r4.collect_examples(HOLDOUT_SINGERS,args.scan_limit)
        h={k:prepare(v) for k,v in h_ex.items()}
        holdout=evaluate_cohort(h,FINAL_RIPPLE_LIMIT,False)
        for k in ("_baseline_full","_candidate_full","_candidate_peak"): holdout.pop(k,None)

    acceptance=bool(selection_pass and holdout and holdout["passes"])
    decision="GO_TO_REDTEAM" if acceptance else "REVISE"
    result={
        "decision":decision,
        "selection_singers":list(SELECTION_SINGERS),
        "holdout_singers":list(HOLDOUT_SINGERS),
        "files_per_singer":FILES_PER_SINGER,
        "baseline_architecture":"shared_8_70_crest6",
        "candidate_architecture":"body8_70_plus_peak3_20_crest6_5",
        "selection":s,
        "gain_invariance_probe":gi,
        "selection_passes":selection_pass,
        "holdout":holdout,
        "holdout_accessed":holdout is not None,
        "acceptance_met":acceptance,
        "raw_audio_persisted":False,
    }
    (out/"amount_r6_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    rows=[]
    for split,obj in [("selection",s),("holdout",holdout)]:
        if obj is None: continue
        for archkey in ("baseline","candidate"):
            by=obj[archkey]["response"]
            for amount in AMOUNTS:
                rows.append({"split":split,"architecture":archkey,"amount":amount,**by[str(amount)]["aggregate"]})
    fields=["split","architecture","amount","mean_gr","p95_gr","p99_gr","max_gr","frac_gt10","gr_ripple","cross_source_mean_gr_std"]
    with (out/"amount_r6_metrics.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

    report=[
        "# Vo.Prep Amount R6 — Current 8/70 vs Dual Peak Assist","",
        f"Decision: {decision}",
        f"Selection passes: {selection_pass}",
        f"Baseline Amount100 ripple: {s['baseline']['response']['100.0']['aggregate']['gr_ripple']:.6f} dB",
        f"Candidate Amount100 ripple: {s['candidate']['response']['100.0']['aggregate']['gr_ripple']:.6f} dB",
        f"Ripple improvement: {s['ripple_improvement_ratio']*100:.2f}%",
        f"Event contrast gain: {s['event_metrics']['aggregate']['event_contrast_gain_db']:.4f} dB",
        f"Non-event p95 delta: {s['event_metrics']['aggregate']['nonevent_abs_delta_p95_db']:.4f} dB",
        f"Fresh holdout accessed: {holdout is not None}",
    ]
    if holdout:
        report += [
            f"Holdout passes: {holdout['passes']}",
            f"Holdout candidate Amount100 ripple: {holdout['candidate']['response']['100.0']['aggregate']['gr_ripple']:.6f} dB",
        ]
    (out/"amount_r6_report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print((out/"amount_r6_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
