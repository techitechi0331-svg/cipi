#!/usr/bin/env python3
"""Vo.Prep Amount Revision 5: Learn-solved Threshold + post-ballistics Soft Range.

Research only. Frozen detector/curve/ballistics stay unchanged.
R4 Learn-solve without Range is the simple baseline.

Selection singers are the already-exposed R4 cohort f7/f8/m7/m8.
Fresh final holdout singers f9/m9/m10/m11 are not streamed/decoded unless
selection passes.
"""
from __future__ import annotations

import argparse, csv, importlib.util, json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.ndimage import uniform_filter1d

HERE=Path(__file__).resolve().parent
R4_PATH=HERE/"amount_mapping_r4_learn_solve.py"
spec=importlib.util.spec_from_file_location("r4_amount",R4_PATH)
r4=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(r4)

SELECTION_SINGERS=("f7","f8","m7","m8")
HOLDOUT_SINGERS=("f9","m9","m10","m11")
FILES_PER_SINGER=2
AMOUNTS=r4.AMOUNTS
TARGET_MEAN=5.5
RANGE_START_DB=6.0
CEILINGS=(10.0,9.0,8.0)
SELECTION_RIPPLE_LIMIT=0.075
FINAL_RIPPLE_LIMIT=0.080
SELECTION_MAPPING_RMSE_MAX=0.50
HOLDOUT_MAPPING_RMSE_MAX=0.65
SOLVER_RESIDUAL_MAX=0.02
GAIN_INVARIANCE_MAX=0.005
MIN_RIPPLE_IMPROVEMENT=0.15

EXPECTED={25.0:1.375,50.0:2.75,75.0:4.125,100.0:5.5}

def soft_range(x,start,ceiling):
    a=np.asarray(x,dtype=np.float64)
    if ceiling<=start:
        raise ValueError("ceiling must exceed start")
    span=ceiling-start
    excess=np.maximum(a-start,0.0)
    ranged=start+span*np.tanh(excess/span)
    return np.where(a<=start,a,ranged)

def learn_mean(item,threshold,ceiling=None):
    desired=r4.soft_knee_gr(item["learn_effective"],threshold)
    actual=r4.ballistics(desired)
    if ceiling is not None:
        actual=soft_range(actual,RANGE_START_DB,ceiling)
    return float(np.mean(actual[item["learn_active"]]))

def solve(item,ceiling=None,target=TARGET_MEAN):
    lo,hi=-120.0,40.0
    mlo=learn_mean(item,lo,ceiling)
    mhi=learn_mean(item,hi,ceiling)
    if mlo<target or mhi>target:
        raise RuntimeError(
            f"{item['source_basename']}: target not bracketed "
            f"lo={mlo:.4f} hi={mhi:.4f} target={target:.4f}"
        )
    for _ in range(22):
        mid=.5*(lo+hi)
        m=learn_mean(item,mid,ceiling)
        if m>target: lo=mid
        else: hi=mid
    threshold=.5*(lo+hi)
    achieved=learn_mean(item,threshold,ceiling)
    return {
        "threshold":threshold,
        "achieved":achieved,
        "residual":abs(achieved-target),
        "relative_to_ref":threshold-item["ref"],
    }

def full_raw(item,threshold):
    return r4.ballistics(r4.soft_knee_gr(item["eval_effective"],threshold))

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
    sm=defaultdict(list)
    for row in rows: sm[row["singer"]].append(row["mean_gr"])
    out["cross_source_mean_gr_std"]=float(np.std([np.mean(v) for v in sm.values()]))
    return out

def summarize(items,ceiling=None):
    solved={}
    raw={}
    for name,item in items.items():
        s=solve(item,ceiling)
        solved[name]=s
        raw[name]=full_raw(item,s["threshold"])

    by={}
    for amount in AMOUNTS:
        rows=[]
        for name,item in items.items():
            if amount<=0:
                final=np.zeros_like(raw[name])
            else:
                scaled=raw[name]*(amount/100.0)
                final=scaled if ceiling is None else soft_range(scaled,RANGE_START_DB,ceiling)
            m=metric(item,final)
            m.update({"file":name,"singer":item["singer"]})
            rows.append(m)
        by[str(amount)]={"aggregate":aggregate(rows),"files":rows}

    solver={
        "max_residual_db":max(v["residual"] for v in solved.values()),
        "mean_relative_threshold_db":float(np.mean([v["relative_to_ref"] for v in solved.values()])),
        "std_relative_threshold_db":float(np.std([v["relative_to_ref"] for v in solved.values()])),
    }
    return by,solver,solved

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
        (by[str(a)]["aggregate"]["mean_gr"]-target)**2
        for a,target in EXPECTED.items()
    ])))

def gain_invariance(item,ceiling):
    base=solve(item,ceiling)
    base_raw=full_raw(item,base["threshold"])
    base_final=soft_range(base_raw,RANGE_START_DB,ceiling)
    base_mean=float(np.mean(base_final[item["eval_active"]]))
    terr=[];gerr=[];rows=[]
    for gain in (-12.,-6.,0.,6.,12.):
        q=dict(item)
        q["learn_effective"]=item["learn_effective"]+gain
        q["eval_effective"]=item["eval_effective"]+gain
        q["ref"]=item["ref"]+gain
        s=solve(q,ceiling)
        act=soft_range(full_raw(q,s["threshold"]),RANGE_START_DB,ceiling)
        mean=float(np.mean(act[q["eval_active"]]))
        te=abs((s["threshold"]-base["threshold"])-gain)
        ge=abs(mean-base_mean)
        terr.append(te);gerr.append(ge)
        rows.append({"gain_db":gain,"threshold_shift_error_db":te,"eval_mean_gr_error_db":ge})
    return {
        "max_threshold_shift_error_db":max(terr),
        "max_eval_mean_gr_error_db":max(gerr),
        "rows":rows,
    }

def pack_candidate(items,ceiling,baseline_ripple100):
    by,solver,solved=summarize(items,ceiling)
    gs=gates(by,SELECTION_RIPPLE_LIMIT)
    rmse=mapping_rmse(by)
    ripple100=by["100.0"]["aggregate"]["gr_ripple"]
    improvement=1.0-ripple100/max(baseline_ripple100,1e-12)
    extra={
        "mapping_rmse":rmse<=SELECTION_MAPPING_RMSE_MAX,
        "solver_residual":solver["max_residual_db"]<=SOLVER_RESIDUAL_MAX,
        "ripple_improvement_ge_15pct":improvement>=MIN_RIPPLE_IMPROVEMENT,
    }
    return {
        "id":f"soft_range_start6_ceiling{ceiling:g}",
        "ceiling_db":ceiling,
        "response":by,
        "solver":solver,
        "thresholds":solved,
        "gates":gs,
        "extra_gates":extra,
        "mapping_rmse_db":rmse,
        "ripple_improvement_ratio":improvement,
        "passes_selection":all(gs.values()) and all(extra.values()),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--scan-limit",type=int,default=15000)
    args=ap.parse_args()
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

    # Selection only. Fresh holdout is not touched here.
    sel_ex=r4.collect_examples(SELECTION_SINGERS,args.scan_limit)
    selection={k:r4.prepare_item(v) for k,v in sel_ex.items()}

    base_by,base_solver,_=summarize(selection,None)
    base_g=gates(base_by,SELECTION_RIPPLE_LIMIT)
    base_rmse=mapping_rmse(base_by)
    base_ripple100=base_by["100.0"]["aggregate"]["gr_ripple"]

    candidates=[pack_candidate(selection,c,base_ripple100) for c in CEILINGS]
    passing=[x for x in candidates if x["passes_selection"]]
    passing.sort(key=lambda x:x["ceiling_db"],reverse=True)
    selected=passing[0] if passing else None

    gain_probe=None
    holdout=None
    acceptance=False
    if selected is not None:
        probe=selection[sorted(selection)[0]]
        gain_probe=gain_invariance(probe,selected["ceiling_db"])
        if gain_probe["max_threshold_shift_error_db"]>GAIN_INVARIANCE_MAX or gain_probe["max_eval_mean_gr_error_db"]>GAIN_INVARIANCE_MAX:
            selected=None

    if selected is not None:
        # Fresh holdout access is structurally delayed until every selection gate,
        # complexity gate and gain-invariance gate has passed.
        h_ex=r4.collect_examples(HOLDOUT_SINGERS,args.scan_limit)
        h={k:r4.prepare_item(v) for k,v in h_ex.items()}
        h_by,h_solver,h_thresholds=summarize(h,selected["ceiling_db"])
        h_g=gates(h_by,FINAL_RIPPLE_LIMIT)
        h_rmse=mapping_rmse(h_by)
        h_extra={
            "mapping_rmse":h_rmse<=HOLDOUT_MAPPING_RMSE_MAX,
            "solver_residual":h_solver["max_residual_db"]<=SOLVER_RESIDUAL_MAX,
        }
        h_pass=all(h_g.values()) and all(h_extra.values())
        holdout={
            "response":h_by,"solver":h_solver,"thresholds":h_thresholds,
            "gates":h_g,"extra_gates":h_extra,
            "mapping_rmse_db":h_rmse,"passes":h_pass,
        }
        acceptance=h_pass
        decision="GO_TO_REDTEAM" if h_pass else "REVISE"
    else:
        decision="REVISE"

    result={
        "decision":decision,
        "dataset":r4.DATASET,
        "selection_singers":list(SELECTION_SINGERS),
        "holdout_singers":list(HOLDOUT_SINGERS),
        "files_per_singer":FILES_PER_SINGER,
        "range_start_db":RANGE_START_DB,
        "candidate_ceilings_db":list(CEILINGS),
        "learn_target_actual_mean_gr_db":TARGET_MEAN,
        "baseline":{
            "id":"r4_learn_solve_no_range","response":base_by,
            "solver":base_solver,"gates":base_g,
            "mapping_rmse_db":base_rmse,
        },
        "candidates":candidates,
        "selected_before_holdout":None if selected is None else {
            "id":selected["id"],"ceiling_db":selected["ceiling_db"]
        },
        "gain_invariance_probe":gain_probe,
        "holdout":holdout,
        "holdout_accessed":holdout is not None,
        "acceptance_met":acceptance,
        "raw_audio_persisted":False,
    }
    (out/"amount_r5_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    rows=[]
    for label,obj in [("baseline",result["baseline"])]+[(c["id"],c) for c in candidates]:
        for amount in AMOUNTS:
            rows.append({"candidate":label,"split":"selection","amount":amount,**obj["response"][str(amount)]["aggregate"]})
    if holdout is not None:
        for amount in AMOUNTS:
            rows.append({"candidate":selected["id"],"split":"holdout","amount":amount,**holdout["response"][str(amount)]["aggregate"]})
    fields=["candidate","split","amount","mean_gr","p95_gr","p99_gr","max_gr","frac_gt10","gr_ripple","cross_source_mean_gr_std"]
    with (out/"amount_r5_metrics.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

    lines=[
        "# Vo.Prep Amount Revision 5 — Soft Range",
        "",
        f"Decision: {decision}",
        f"Selection singers: {', '.join(SELECTION_SINGERS)}",
        f"Fresh holdout singers: {', '.join(HOLDOUT_SINGERS)}",
        f"R4 baseline Amount-100 ripple: {base_ripple100:.6f} dB",
    ]
    if selected:
        lines += [
            f"Selected before holdout: {selected['id']}",
            f"Selection Amount-100 ripple: {selected['response']['100.0']['aggregate']['gr_ripple']:.6f} dB",
            f"Selection ripple improvement: {selected['ripple_improvement_ratio']*100:.2f}%",
            f"Holdout pass: {holdout['passes'] if holdout else False}",
        ]
    (out/"amount_r5_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print((out/"amount_r5_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
