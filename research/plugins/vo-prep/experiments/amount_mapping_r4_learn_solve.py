#!/usr/bin/env python3
"""Vo.Prep Amount Revision 4: explicit-Learn threshold solve.

Research only. The frozen compressor core is unchanged.
Raw VocalSet audio is streamed and decoded in runner memory only.

R4 tests one new architecture against the rejected R3 simple baseline:
- baseline: Learn Slow-P50 + fixed R3 relative offset;
- candidate: use only the explicit 4 s Learn buffer to solve one locked
  Threshold whose frozen-core ActualGR mean is 5.5 dB on active Learn audio.

After Learn, Threshold is fixed. There is no continuous auto-threshold.
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

SELECTION_SINGERS = ("f5","f6","m5","m6")
HOLDOUT_SINGERS = ("f7","f8","m7","m8")
FILES_PER_SINGER = 2

# R3 strongest fixed-offset baseline.
R3_FIXED_OFFSET_DB = -16.43438160419464

# Product-intensity target: center of the unchanged Amount-100 mean-GR gate.
LEARN_TARGET_ACTUAL_MEAN_GR_DB = 5.5
SELECTION_RIPPLE_MARGIN_DB = 0.075
FINAL_RIPPLE_GATE_DB = 0.080
SELECTION_MAPPING_RMSE_MAX_DB = 0.50
HOLDOUT_MAPPING_RMSE_MAX_DB = 0.65
SELECTION_CROSS_SOURCE_50_MAX_DB = 0.75
SOLVER_RESIDUAL_MAX_DB = 0.02
GAIN_INVARIANCE_MAX_ERROR_DB = 0.005
COMPLEXITY_IMPROVEMENT_RATIO = 0.70

EXPECTED_MEAN_GR = {
    25.0: LEARN_TARGET_ACTUAL_MEAN_GR_DB * 0.25,
    50.0: LEARN_TARGET_ACTUAL_MEAN_GR_DB * 0.50,
    75.0: LEARN_TARGET_ACTUAL_MEAN_GR_DB * 0.75,
    100.0: LEARN_TARGET_ACTUAL_MEAN_GR_DB,
}

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

def db_amp(x):
    return 20.0*np.log10(np.maximum(np.abs(x),1e-12))

def slow_detector(x):
    a = math.exp(-1.0/(FS*SLOW_MS*1e-3))
    e = lfilter([1.0-a],[1.0,-a],x*x)
    return np.sqrt(np.maximum(e,1e-24))

def soft_knee_gr(level, threshold):
    u = np.asarray(level,dtype=np.float64)-threshold
    half = KNEE_DB*0.5
    frac = 1.0-1.0/RATIO
    q = np.zeros_like(u)
    hi = u > half
    mid = (u >= -half) & (~hi)
    q[hi] = frac*u[hi]
    z = u[mid]+half
    q[mid] = frac*(z*z)/(2.0*KNEE_DB)
    return np.maximum(q,0.0)

def ballistics(desired):
    aa = math.exp(-1.0/(FS*ATTACK_MS*1e-3))
    ar = math.exp(-1.0/(FS*RELEASE_MS*1e-3))
    out = np.empty_like(desired,dtype=np.float64)
    state = 0.0
    for i,v in enumerate(desired):
        fv=float(v)
        a=aa if fv>state else ar
        state=a*state+(1.0-a)*fv
        out[i]=state
    return out

def activity_mask(level_db: np.ndarray, minimum_fraction: float = 0.0):
    finite = np.isfinite(level_db) & (level_db > -180.0)
    peak = float(np.max(level_db[finite])) if np.any(finite) else -180.0
    active = finite & (level_db >= peak-30.0)
    if minimum_fraction > 0.0 and float(np.mean(active)) < minimum_fraction:
        return None
    return active

def collect_examples(singers, scan_limit: int):
    wanted=set(singers)
    ds=load_dataset(DATASET,split="train",streaming=True)
    ds=ds.cast_column("audio",Audio(decode=False))

    selected={}
    per_singer=defaultdict(int)
    per_singer_label=defaultdict(int)

    for idx,row in enumerate(ds):
        if idx>=scan_limit:
            break
        cell=row.get("audio")
        if not isinstance(cell,dict):
            continue
        source_path=str(cell.get("path") or "")
        singer=singer_id_from_path(source_path)
        if singer not in wanted or per_singer[singer]>=FILES_PER_SINGER:
            continue
        label=str(row.get("label","unknown"))
        if per_singer_label[(singer,label)]>=1:
            continue
        data=cell.get("bytes")
        if data is None:
            continue
        try:
            x=best_energy_segment(to_mono_resampled(data))
        except Exception:
            continue
        if len(x)<int((LEARN_SECONDS+2.0)*FS):
            continue
        if float(np.sqrt(np.mean(x*x)+1e-18))<1e-4:
            continue

        slow=slow_detector(x)
        slow_db=db_amp(slow)
        learn_n=int(round(LEARN_SECONDS*FS))
        learn_mask=activity_mask(slow_db[:learn_n],minimum_fraction=0.60)
        eval_mask=activity_mask(slow_db[learn_n:])
        if learn_mask is None or eval_mask is None:
            continue
        if int(np.sum(eval_mask))<int(1.5*FS):
            continue

        key=f"{singer}:{Path(source_path).name}"
        selected[key]={
            "singer":singer,
            "label":label,
            "source_basename":Path(source_path).name,
            "x":x,
        }
        per_singer[singer]+=1
        per_singer_label[(singer,label)]+=1

        if all(per_singer[s]>=FILES_PER_SINGER for s in wanted):
            break

    missing={s:FILES_PER_SINGER-per_singer[s] for s in wanted if per_singer[s]<FILES_PER_SINGER}
    if missing:
        raise RuntimeError(f"Insufficient R4 VocalSet examples: {missing}")
    return selected

def prepare_item(ex):
    x=ex["x"]
    slow=slow_detector(x)
    slow_db=db_amp(slow)
    fast_db=db_amp(x)
    effective=np.maximum(slow_db,fast_db-6.0)

    learn_n=int(round(LEARN_SECONDS*FS))
    learn_slow=slow_db[:learn_n]
    learn_active=activity_mask(learn_slow,minimum_fraction=0.60)
    if learn_active is None:
        raise RuntimeError(f"{ex['source_basename']}: insufficient Learn activity")

    eval_slow=slow_db[learn_n:]
    eval_active=activity_mask(eval_slow)
    if eval_active is None or int(np.sum(eval_active))<int(1.5*FS):
        raise RuntimeError(f"{ex['source_basename']}: insufficient evaluation activity")

    ref=float(np.median(learn_slow[learn_active]))
    return {
        **ex,
        "learn_effective":effective[:learn_n],
        "learn_active":learn_active,
        "eval_effective":effective[learn_n:],
        "eval_active":eval_active,
        "ref":ref,
        "learn_active_fraction":float(np.mean(learn_active)),
    }

def actual_mean_for_threshold(learn_effective, learn_active, threshold):
    desired=soft_knee_gr(learn_effective,threshold)
    actual=ballistics(desired)
    return float(np.mean(actual[learn_active]))

def solve_threshold(item, target=LEARN_TARGET_ACTUAL_MEAN_GR_DB):
    lo=-120.0
    hi=40.0
    m_lo=actual_mean_for_threshold(item["learn_effective"],item["learn_active"],lo)
    m_hi=actual_mean_for_threshold(item["learn_effective"],item["learn_active"],hi)
    if m_lo<target or m_hi>target:
        raise RuntimeError(
            f"{item['source_basename']}: target not bracketed "
            f"(lo={m_lo:.4f}, hi={m_hi:.4f}, target={target:.4f})"
        )

    for _ in range(20):
        mid=0.5*(lo+hi)
        m=actual_mean_for_threshold(item["learn_effective"],item["learn_active"],mid)
        if m>target:
            lo=mid
        else:
            hi=mid

    threshold=0.5*(lo+hi)
    achieved=actual_mean_for_threshold(item["learn_effective"],item["learn_active"],threshold)
    return {
        "threshold":threshold,
        "achieved":achieved,
        "residual":abs(achieved-target),
        "relative_to_ref":threshold-item["ref"],
        "iterations":20,
    }

def actual100_for_threshold(item, threshold):
    desired100=soft_knee_gr(item["eval_effective"],threshold)
    return ballistics(desired100)

def metrics(item,actual):
    vals=actual[item["eval_active"]]
    trend=uniform_filter1d(actual,size=max(1,int(.04*FS)),mode="nearest")
    return {
        "mean_gr":float(np.mean(vals)),
        "p95_gr":float(np.percentile(vals,95)),
        "p99_gr":float(np.percentile(vals,99)),
        "max_gr":float(np.max(vals)),
        "frac_gt10":float(np.mean(vals>10.0)),
        "gr_ripple":float(np.std((actual-trend)[item["eval_active"]])),
    }

def aggregate_rows(rows):
    agg={}
    for k in ("mean_gr","p95_gr","p99_gr","max_gr","frac_gt10","gr_ripple"):
        agg[k]=float(np.mean([r[k] for r in rows]))
    singer_means=defaultdict(list)
    for r in rows:
        singer_means[r["singer"]].append(r["mean_gr"])
    per_singer=[float(np.mean(v)) for v in singer_means.values()]
    agg["cross_source_mean_gr_std"]=float(np.std(per_singer))
    return agg

def summarize(items, architecture):
    full={}
    solve_meta={}
    for name,item in items.items():
        if architecture=="r3_fixed_offset":
            threshold=item["ref"]+R3_FIXED_OFFSET_DB
            solve_meta[name]={
                "threshold":threshold,
                "achieved":None,
                "residual":None,
                "relative_to_ref":R3_FIXED_OFFSET_DB,
                "iterations":0,
            }
        elif architecture=="learn_actual_mean_solve":
            solve_meta[name]=solve_threshold(item)
            threshold=solve_meta[name]["threshold"]
        else:
            raise ValueError(architecture)
        full[name]=actual100_for_threshold(item,threshold)

    first=next(iter(items))
    if architecture=="learn_actual_mean_solve":
        threshold=solve_meta[first]["threshold"]
    else:
        threshold=items[first]["ref"]+R3_FIXED_OFFSET_DB
    direct50=ballistics(0.5*soft_knee_gr(items[first]["eval_effective"],threshold))
    homogeneity_error=float(np.max(np.abs(direct50-0.5*full[first])))
    if homogeneity_error>1e-10:
        raise RuntimeError(f"Ballistics homogeneity failed: {homogeneity_error}")

    by={}
    flat=[]
    for amount in AMOUNTS:
        rows=[]
        for name,item in items.items():
            actual=np.zeros_like(full[name]) if amount<=0 else full[name]*(amount/100.0)
            m=metrics(item,actual)
            m.update({"file":name,"singer":item["singer"]})
            rows.append(m)
        agg=aggregate_rows(rows)
        agg["ballistics_homogeneity_max_error"]=homogeneity_error
        by[str(amount)]={"aggregate":agg,"files":rows}
        flat.extend([{"architecture":architecture,"amount":amount,**r} for r in rows])

    solver_residuals=[x["residual"] for x in solve_meta.values() if x["residual"] is not None]
    relative_offsets=[x["relative_to_ref"] for x in solve_meta.values()]
    solver={
        "max_residual_db":max(solver_residuals) if solver_residuals else 0.0,
        "mean_relative_threshold_db":float(np.mean(relative_offsets)),
        "std_relative_threshold_db":float(np.std(relative_offsets)),
        "min_relative_threshold_db":float(np.min(relative_offsets)),
        "max_relative_threshold_db":float(np.max(relative_offsets)),
        "mean_learn_active_fraction":float(np.mean([x["learn_active_fraction"] for x in items.values()])),
    }

    means=np.asarray([by[str(a)]["aggregate"]["mean_gr"] for a in AMOUNTS])
    p95=np.asarray([by[str(a)]["aggregate"]["p95_gr"] for a in AMOUNTS])
    monotonic=bool(np.all(np.diff(means)>=-1e-6) and np.all(np.diff(p95)>=-1e-6))
    return by,solver,monotonic,flat,solve_meta

def original_gates(by, monotonic, ripple_limit):
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

def mapping_rmse(by):
    err=[]
    for amount,target in EXPECTED_MEAN_GR.items():
        err.append(by[str(amount)]["aggregate"]["mean_gr"]-target)
    return float(np.sqrt(np.mean(np.square(err))))

def gain_invariance_probe(item):
    base=solve_threshold(item)
    base_actual=actual100_for_threshold(item,base["threshold"])
    base_mean=float(np.mean(base_actual[item["eval_active"]]))
    threshold_errors=[]
    gr_errors=[]
    rows=[]
    for gain_db in (-12.0,-6.0,0.0,6.0,12.0):
        shifted=dict(item)
        shifted["learn_effective"]=item["learn_effective"]+gain_db
        shifted["eval_effective"]=item["eval_effective"]+gain_db
        shifted["ref"]=item["ref"]+gain_db
        sol=solve_threshold(shifted)
        act=actual100_for_threshold(shifted,sol["threshold"])
        mean=float(np.mean(act[shifted["eval_active"]]))
        threshold_error=abs((sol["threshold"]-base["threshold"])-gain_db)
        gr_error=abs(mean-base_mean)
        threshold_errors.append(threshold_error)
        gr_errors.append(gr_error)
        rows.append({
            "gain_db":gain_db,
            "threshold_db":sol["threshold"],
            "threshold_shift_error_db":threshold_error,
            "eval_mean_gr_error_db":gr_error,
        })
    return {
        "max_threshold_shift_error_db":max(threshold_errors),
        "max_eval_mean_gr_error_db":max(gr_errors),
        "rows":rows,
    }

def csv_rows(architecture,split,by):
    rows=[]
    for amount in AMOUNTS:
        a=by[str(amount)]["aggregate"]
        rows.append({
            "architecture":architecture,
            "split":split,
            "amount":amount,
            **a,
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--scan-limit",type=int,default=12000)
    args=ap.parse_args()
    out=Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)

    selection_examples=collect_examples(SELECTION_SINGERS,args.scan_limit)
    selection={k:prepare_item(v) for k,v in selection_examples.items()}

    base_by,base_solver,base_mono,_,base_meta=summarize(selection,"r3_fixed_offset")
    cand_by,cand_solver,cand_mono,_,cand_meta=summarize(selection,"learn_actual_mean_solve")

    base_gates=original_gates(base_by,base_mono,SELECTION_RIPPLE_MARGIN_DB)
    cand_gates=original_gates(cand_by,cand_mono,SELECTION_RIPPLE_MARGIN_DB)
    base_rmse=mapping_rmse(base_by)
    cand_rmse=mapping_rmse(cand_by)

    probe_item=selection[sorted(selection)[0]]
    gain_probe=gain_invariance_probe(probe_item)

    complexity_justified=(
        (not all(base_gates.values()))
        or cand_rmse <= base_rmse*COMPLEXITY_IMPROVEMENT_RATIO
    )

    selection_extra={
        "mapping_rmse":cand_rmse<=SELECTION_MAPPING_RMSE_MAX_DB,
        "cross_source_50_margin":cand_by["50.0"]["aggregate"]["cross_source_mean_gr_std"]<=SELECTION_CROSS_SOURCE_50_MAX_DB,
        "solver_residual":cand_solver["max_residual_db"]<=SOLVER_RESIDUAL_MAX_DB,
        "gain_invariance_threshold":gain_probe["max_threshold_shift_error_db"]<=GAIN_INVARIANCE_MAX_ERROR_DB,
        "gain_invariance_gr":gain_probe["max_eval_mean_gr_error_db"]<=GAIN_INVARIANCE_MAX_ERROR_DB,
        "complexity_justified":complexity_justified,
    }
    selection_pass=all(cand_gates.values()) and all(selection_extra.values())

    holdout_result=None
    if selection_pass:
        # Holdout audio is not even streamed/decoded until selection has passed.
        # This enforces the declared data-separation gate at access time.
        holdout_examples=collect_examples(HOLDOUT_SINGERS,args.scan_limit)
        holdout={k:prepare_item(v) for k,v in holdout_examples.items()}
        h_base_by,h_base_solver,h_base_mono,_,_=summarize(holdout,"r3_fixed_offset")
        h_cand_by,h_cand_solver,h_cand_mono,_,h_cand_meta=summarize(holdout,"learn_actual_mean_solve")
        h_gates=original_gates(h_cand_by,h_cand_mono,FINAL_RIPPLE_GATE_DB)
        h_rmse=mapping_rmse(h_cand_by)
        h_extra={
            "mapping_rmse":h_rmse<=HOLDOUT_MAPPING_RMSE_MAX_DB,
            "solver_residual":h_cand_solver["max_residual_db"]<=SOLVER_RESIDUAL_MAX_DB,
        }
        holdout_pass=all(h_gates.values()) and all(h_extra.values())
        holdout_result={
            "candidate_response":h_cand_by,
            "candidate_solver":h_cand_solver,
            "candidate_gates":h_gates,
            "candidate_extra_gates":h_extra,
            "candidate_mapping_rmse_db":h_rmse,
            "baseline_response":h_base_by,
            "baseline_solver":h_base_solver,
            "baseline_mapping_rmse_db":mapping_rmse(h_base_by),
            "passes":holdout_pass,
            "thresholds":{
                name:{
                    "threshold_db":meta["threshold"],
                    "relative_to_ref_db":meta["relative_to_ref"],
                    "solver_residual_db":meta["residual"],
                } for name,meta in h_cand_meta.items()
            },
        }
        decision="GO_TO_REDTEAM" if holdout_pass else "REVISE"
        acceptance=holdout_pass
    else:
        decision="REVISE"
        acceptance=False

    result={
        "decision":decision,
        "dataset":DATASET,
        "selection_singers":list(SELECTION_SINGERS),
        "holdout_singers":list(HOLDOUT_SINGERS),
        "files_per_singer":FILES_PER_SINGER,
        "learn_seconds":LEARN_SECONDS,
        "learn_target_actual_mean_gr_db":LEARN_TARGET_ACTUAL_MEAN_GR_DB,
        "baseline":{
            "id":"r3_fixed_offset",
            "fixed_offset_db":R3_FIXED_OFFSET_DB,
            "response":base_by,
            "solver":base_solver,
            "gates":base_gates,
            "mapping_rmse_db":base_rmse,
        },
        "candidate":{
            "id":"learn_actual_mean_solve",
            "response":cand_by,
            "solver":cand_solver,
            "gates":cand_gates,
            "extra_gates":selection_extra,
            "mapping_rmse_db":cand_rmse,
            "gain_invariance_probe":gain_probe,
            "thresholds":{
                name:{
                    "threshold_db":meta["threshold"],
                    "relative_to_ref_db":meta["relative_to_ref"],
                    "solver_residual_db":meta["residual"],
                } for name,meta in cand_meta.items()
            },
            "passes_selection":selection_pass,
        },
        "holdout":holdout_result,
        "holdout_accessed":holdout_result is not None,
        "acceptance_met":acceptance,
        "raw_audio_persisted":False,
    }

    (out/"amount_r4_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    rows=[]
    rows+=csv_rows("r3_fixed_offset","selection",base_by)
    rows+=csv_rows("learn_actual_mean_solve","selection",cand_by)
    if holdout_result is not None:
        rows+=csv_rows("r3_fixed_offset","holdout",holdout_result["baseline_response"])
        rows+=csv_rows("learn_actual_mean_solve","holdout",holdout_result["candidate_response"])
    fields=[
        "architecture","split","amount","mean_gr","p95_gr","p99_gr","max_gr",
        "frac_gt10","gr_ripple","cross_source_mean_gr_std","ballistics_homogeneity_max_error"
    ]
    with (out/"amount_r4_metrics.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader();w.writerows(rows)

    with (out/"gain_invariance.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["gain_db","threshold_db","threshold_shift_error_db","eval_mean_gr_error_db"])
        w.writeheader();w.writerows(gain_probe["rows"])

    lines=[
        "# Vo.Prep Amount Revision 4 — Learn-time Threshold Solve",
        "",
        f"Decision: {decision}",
        f"Selection singers: {', '.join(SELECTION_SINGERS)}",
        f"Holdout singers: {', '.join(HOLDOUT_SINGERS)}",
        f"Learn target ActualGR mean: {LEARN_TARGET_ACTUAL_MEAN_GR_DB:.3f} dB",
        "",
        f"Baseline selection mapping RMSE: {base_rmse:.6f} dB",
        f"Candidate selection mapping RMSE: {cand_rmse:.6f} dB",
        f"Candidate selection passes: {selection_pass}",
        f"Candidate solver max residual: {cand_solver['max_residual_db']:.6f} dB",
        f"Gain-invariance max GR error: {gain_probe['max_eval_mean_gr_error_db']:.9f} dB",
    ]
    if holdout_result is not None:
        lines += [
            "",
            f"Holdout mapping RMSE: {holdout_result['candidate_mapping_rmse_db']:.6f} dB",
            f"Holdout passes: {holdout_result['passes']}",
        ]
    (out/"amount_r4_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print((out/"amount_r4_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
