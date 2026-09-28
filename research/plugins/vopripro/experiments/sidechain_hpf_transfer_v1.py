#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, json, math, random
from pathlib import Path

SAMPLE_RATES=(44100,48000,96000,192000)
CUTOFFS=(80.0,60.0,40.0)
RATIO=2.7
KNEE_DB=12.0
CAL_GR_DB=3.0
MAX_GR_DB=6.0
ATTACK_S=0.020
RELEASE_S=0.110
RMS_TAU_S=0.025
PEAK_WEIGHT=0.35
HPF_Q=0.70710678
SEED=20260926

def db_to_gain(db): return 10.0**(db/20.0)
def gain_to_db(g): return 20.0*math.log10(max(abs(g),1e-12))
def onepole(tau,sr): return math.exp(-1.0/(tau*sr))

class HPF:
    def __init__(self,sr,fc):
        w0=2*math.pi*fc/sr
        c=math.cos(w0); s=math.sin(w0)
        alpha=s/(2*HPF_Q); a0=1+alpha
        self.b0=((1+c)*.5)/a0
        self.b1=(-(1+c))/a0
        self.b2=((1+c)*.5)/a0
        self.a1=(-2*c)/a0
        self.a2=(1-alpha)/a0
        self.z1=0.0; self.z2=0.0
    def process(self,x):
        y=self.b0*x+self.z1
        self.z1=self.b1*x-self.a1*y+self.z2
        self.z2=self.b2*x-self.a2*y
        return y

class Detector:
    def __init__(self,sr,fc):
        self.hpf=HPF(sr,fc)
        self.rmsc=onepole(RMS_TAU_S,sr)
        self.p=0.0
    def db(self,x):
        sc=self.hpf.process(x)
        peak=abs(sc)
        self.p=self.rmsc*self.p+(1-self.rmsc)*sc*sc
        rms=math.sqrt(max(self.p,0.0))
        return gain_to_db(PEAK_WEIGHT*peak+(1-PEAK_WEIGHT)*rms)

def soft_gr(level,th):
    k=1.0-1.0/RATIO
    d=level-th
    half=KNEE_DB*.5
    if d<=-half:return 0.0
    if d>=half:return min(MAX_GR_DB,max(0.0,k*d))
    u=d+half
    return min(MAX_GR_DB,max(0.0,k*u*u/(2*KNEE_DB)))

def render_gr(samples,sr,fc,th):
    det=Detector(sr,fc)
    aa=onepole(ATTACK_S,sr); ar=onepole(RELEASE_S,sr)
    state=0.0; out=[]
    for x in samples:
        desired=soft_gr(det.db(x),th)
        a=aa if desired>state else ar
        state=a*state+(1-a)*desired
        out.append(state)
    return out

def harmonic_vowel(sr,f0,seconds=1.2,rms_db=-18.0):
    n=int(round(seconds*sr))
    x=[]
    weights=(1.0,.55,.34,.23,.16,.11,.08,.06)
    for i in range(n):
        t=i/sr
        y=0.0
        for h,w in enumerate(weights,1):
            y += w*math.sin(2*math.pi*f0*h*t+0.17*h)
        x.append(y)
    rms=math.sqrt(sum(v*v for v in x)/max(1,len(x)))
    g=db_to_gain(rms_db)/max(rms,1e-12)
    return [v*g for v in x]

def active_mean(gr,sr,start=.40,end=1.15):
    lo=int(start*sr); hi=min(len(gr),int(end*sr))
    vals=gr[lo:hi]
    return sum(vals)/max(1,len(vals))

def peak(gr): return max(gr) if gr else 0.0

def solve_threshold(sr,fc):
    ref=harmonic_vowel(sr,220.0)
    lo,hi=-80.0,10.0
    for _ in range(36):
        mid=.5*(lo+hi)
        m=active_mean(render_gr(ref,sr,fc,mid),sr)
        if m>CAL_GR_DB: lo=mid
        else: hi=mid
    th=.5*(lo+hi)
    resid=abs(active_mean(render_gr(ref,sr,fc,th),sr)-CAL_GR_DB)
    return th,resid

def add_rumble(x,sr,hz=30.0,rel_db=-9.0):
    rms=math.sqrt(sum(v*v for v in x)/max(1,len(x)))
    amp=rms*db_to_gain(rel_db)*math.sqrt(2)
    return [v+amp*math.sin(2*math.pi*hz*i/sr+0.37) for i,v in enumerate(x)]

def add_plosive(x,sr,hz=55.0,rel_db=6.0):
    y=list(x)
    n=int(.090*sr); start=int(.25*sr)
    rms=math.sqrt(sum(v*v for v in x)/max(1,len(x)))
    t=[i/sr for i in range(n)]
    burst=[math.sin(2*math.pi*hz*tt)*math.exp(-tt/.024) for tt in t]
    brms=math.sqrt(sum(v*v for v in burst)/max(1,n))
    scale=rms*db_to_gain(rel_db)/max(brms,1e-12)
    for i,v in enumerate(burst):
        if start+i<len(y): y[start+i]+=v*scale
    return y,start,n

def make_transient(sr):
    pre=[0.0]*int(.20*sr)
    n=int(.020*sr)
    burst=[]
    for i in range(n):
        t=i/sr
        env=math.sin(math.pi*(i+.5)/max(1,n))
        burst.append(db_to_gain(-7.0)*env*math.sin(2*math.pi*2400*t))
    return pre+burst+[0.0]*int(.40*sr)

def make_sibilant(sr):
    rng=random.Random(SEED+sr)
    pre=[0.0]*int(.20*sr); n=int(.120*sr)
    prev=0.0; sig=[]
    for i in range(n):
        white=rng.uniform(-1,1)
        high=white-.92*prev; prev=white
        env=math.sin(math.pi*(i+.5)/max(1,n))
        sig.append(db_to_gain(-10.0)*env*high)
    return pre+sig+[0.0]*int(.40*sr)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out-dir",required=True)
    args=ap.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    rows=[]; refs=[]
    for sr in SAMPLE_RATES:
        thresholds={}
        for fc in CUTOFFS:
            th,resid=solve_threshold(sr,fc)
            thresholds[fc]=th
            refs.append({"sample_rate":sr,"cutoff_hz":fc,"threshold_db":th,"calibration_residual_db":resid})

        for f0 in (80.0,90.0,110.0,150.0,220.0):
            src=harmonic_vowel(sr,f0)
            for fc in CUTOFFS:
                gr=render_gr(src,sr,fc,thresholds[fc])
                rows.append({"sample_rate":sr,"cutoff_hz":fc,"case":"vowel","f0_hz":f0,
                             "mean_gr_db":active_mean(gr,sr),"peak_gr_db":peak(gr)})

        base=harmonic_vowel(sr,110.0)
        for name,samples in (("rumble",add_rumble(base,sr)),("plosive",add_plosive(base,sr)[0]),
                             ("transient",make_transient(sr)),("sibilant",make_sibilant(sr))):
            for fc in CUTOFFS:
                gr=render_gr(samples,sr,fc,thresholds[fc])
                rows.append({"sample_rate":sr,"cutoff_hz":fc,"case":name,"f0_hz":0.0,
                             "mean_gr_db":active_mean(gr,sr,0.20,min(len(gr)/sr,.95)),
                             "peak_gr_db":peak(gr)})

    candidates=[]
    for fc in (60.0,40.0):
        per_sr=[]
        for sr in SAMPLE_RATES:
            def get(cut,case,f0=None):
                rr=[r for r in rows if r["sample_rate"]==sr and r["cutoff_hz"]==cut and r["case"]==case]
                if f0 is not None: rr=[r for r in rr if r["f0_hz"]==f0]
                return rr[0]

            base_v=[get(80.0,"vowel",f) for f in (80.0,90.0,110.0,150.0,220.0)]
            cand_v=[get(fc,"vowel",f) for f in (80.0,90.0,110.0,150.0,220.0)]
            base_vals=[x["mean_gr_db"] for x in base_v]
            cand_vals=[x["mean_gr_db"] for x in cand_v]
            base_bias=max(base_vals)-min(base_vals)
            cand_bias=max(cand_vals)-min(cand_vals)
            pitch_bias_reduction=1.0-cand_bias/max(base_bias,1e-9)

            rb=get(80.0,"rumble"); rc=get(fc,"rumble")
            pb=get(80.0,"plosive"); pc=get(fc,"plosive")
            tb=get(80.0,"transient"); tc=get(fc,"transient")
            sb=get(80.0,"sibilant"); sc=get(fc,"sibilant")

            per_sr.append({
                "sample_rate":sr,
                "pitch_bias_reduction":pitch_bias_reduction,
                "pitch_bias_baseline_db":base_bias,
                "pitch_bias_candidate_db":cand_bias,
                "rumble_extra_peak_gr_db":rc["peak_gr_db"]-rb["peak_gr_db"],
                "plosive_extra_peak_gr_db":pc["peak_gr_db"]-pb["peak_gr_db"],
                "transient_abs_peak_delta_db":abs(tc["peak_gr_db"]-tb["peak_gr_db"]),
                "sibilant_abs_peak_delta_db":abs(sc["peak_gr_db"]-sb["peak_gr_db"]),
                "low80_mean_delta_db":cand_v[0]["mean_gr_db"]-base_v[0]["mean_gr_db"],
            })

        agg={k:sum(x[k] for x in per_sr)/len(per_sr) for k in per_sr[0] if k!="sample_rate"}
        spread=max(x["pitch_bias_candidate_db"] for x in per_sr)-min(x["pitch_bias_candidate_db"] for x in per_sr)
        gates={
            "pitch_bias_reduction_ge_25pct":agg["pitch_bias_reduction"]>=.25,
            "rumble_extra_peak_le_0_20db":agg["rumble_extra_peak_gr_db"]<=.20,
            "plosive_extra_peak_le_0_25db":agg["plosive_extra_peak_gr_db"]<=.25,
            "transient_abs_peak_delta_le_0_10db":agg["transient_abs_peak_delta_db"]<=.10,
            "sibilant_abs_peak_delta_le_0_10db":agg["sibilant_abs_peak_delta_db"]<=.10,
            "pitch_bias_sr_spread_le_0_10db":spread<=.10,
            "low80_not_less_compressed":agg["low80_mean_delta_db"]>=-.05,
        }
        candidates.append({"cutoff_hz":fc,"aggregate":agg,"sample_rate_spread_db":spread,
                           "per_sr":per_sr,"gates":gates,"passes":all(gates.values())})

    passing=[c for c in candidates if c["passes"]]
    passing.sort(key=lambda x:(-x["aggregate"]["pitch_bias_reduction"], x["cutoff_hz"]))
    selected=passing[0] if passing else None
    decision="GO_TO_REAL_VOCAL" if selected else "KEEP_80HZ_BASELINE"

    result={
      "experiment":"VOPRIPRO_SIDECHAIN_HPF_TRANSFER_V1",
      "baseline_cutoff_hz":80.0,
      "candidates":candidates,
      "selected":selected,
      "decision":decision,
      "reference_calibration":refs,
      "acceptance_met":selected is not None,
      "interpretation":"Synthetic eligibility only. Passing does not authorize product integration."
    }
    (out/"summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    with (out/"rows.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    report=["# VoPriPro Sidechain HPF Transfer v1","",f"Decision: **{decision}**","",
            "Baseline: current 80 Hz / 12 dB-oct detector HPF.",
            "Candidates: 60 Hz and 40 Hz with current Natural50 detector, curve and 20/110 ms ballistics held fixed.",""]
    for c in candidates:
        report += [f"## {c['cutoff_hz']:.0f} Hz",f"- passes: {c['passes']}",f"- metrics: {json.dumps(c['aggregate'],sort_keys=True)}",f"- gates: {json.dumps(c['gates'],sort_keys=True)}",""]
    (out/"report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print((out/"report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
