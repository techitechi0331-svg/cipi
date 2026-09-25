#!/usr/bin/env python3
"""Synthetic sidechain-HPF pilot for the frozen Vo.Prep transparent compressor.

Research only. No product DSP mutation and no raw audio.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfilt,lfilter

SRS=(44100,48000,96000)
CUTOFFS=(0,40,60,70,80,100)
THRESHOLD=-27.75
SLOW_MS=25.0
ATTACK_MS=8.0
RELEASE_MS=70.0
RATIO=1.5
KNEE_DB=18.0

def rms_db(x):
    return 20*math.log10(max(float(np.sqrt(np.mean(x*x)+1e-18)),1e-12))

def scale_rms(x,target_db):
    g=10**(target_db/20)/max(float(np.sqrt(np.mean(x*x)+1e-18)),1e-12)
    return x*g

def vowel(sr,f0,secs=1.2):
    t=np.arange(int(sr*secs))/sr
    x=np.zeros_like(t)
    for h,a in [(1,1.0),(2,.55),(3,.32),(4,.20),(5,.13),(6,.09)]:
        x += a*np.sin(2*np.pi*f0*h*t+0.13*h)
    return scale_rms(x,-18.0)

def make_cases(sr):
    n=int(1.5*sr); t=np.arange(n)/sr
    male=np.zeros(n); female=np.zeros(n)
    male[int(.2*sr):int(1.4*sr)]=vowel(sr,90,1.2)
    female[int(.2*sr):int(1.4*sr)]=vowel(sr,220,1.2)

    rumble=male.copy()
    rumble += (10**(-20/20))*np.sin(2*np.pi*30*t)

    prox=np.zeros(n)
    base=vowel(sr,120,1.2)
    tb=np.arange(len(base))/sr
    base += scale_rms(np.sin(2*np.pi*80*tb),-20.0)
    prox[int(.2*sr):int(1.4*sr)]=base

    plosive=male.copy()
    start=int(.18*sr); m=int(.09*sr)
    tp=np.arange(m)/sr
    burst=0.75*np.sin(2*np.pi*55*tp)*np.exp(-tp/.025)
    rng=np.random.default_rng(20260926)
    burst+=0.15*rng.standard_normal(m)*np.exp(-tp/.018)
    plosive[start:start+m]+=burst

    consonant=male.copy()
    m=int(.04*sr); start=int(.18*sr)
    rng=np.random.default_rng(1122)
    noise=rng.standard_normal(m)
    # high-pass-ish differentiator for consonant energy
    noise=np.concatenate([[noise[0]],np.diff(noise)])
    consonant[start:start+m]+=scale_rms(noise,-15.0)

    sibilant=male.copy()
    m=int(.08*sr); start=int(.18*sr); ts=np.arange(m)/sr
    rng=np.random.default_rng(3344)
    carrier=rng.standard_normal(m)*np.sin(2*np.pi*7000*ts)
    sibilant[start:start+m]+=scale_rms(carrier,-16.0)

    return {
      "male_low":male,"female":female,"rumble":rumble,
      "proximity":prox,"plosive":plosive,"consonant":consonant,"sibilant":sibilant
    }

def hpf(x,sr,fc):
    if fc<=0:return x.copy()
    sos=butter(2,fc/(sr*0.5),btype="highpass",output="sos")
    return sosfilt(sos,x)

def soft_gr(level):
    u=level-THRESHOLD
    half=KNEE_DB*.5
    frac=1.0-1.0/RATIO
    q=np.zeros_like(u)
    hi=u>half; mid=(u>=-half)&(~hi)
    q[hi]=frac*u[hi]
    z=u[mid]+half
    q[mid]=frac*(z*z)/(2*KNEE_DB)
    return np.maximum(q,0)

def compressor_gr(det,sr):
    a=math.exp(-1/(sr*SLOW_MS*1e-3))
    e=lfilter([1-a],[1,-a],det*det)
    slow=10*np.log10(np.maximum(e,1e-24))
    fast=20*np.log10(np.maximum(np.abs(det),1e-12))
    effective=np.maximum(slow,fast-6.0)
    desired=soft_gr(effective)
    aa=math.exp(-1/(sr*ATTACK_MS*1e-3))
    ar=math.exp(-1/(sr*RELEASE_MS*1e-3))
    out=np.empty_like(desired); s=0.0
    for i,v in enumerate(desired):
        k=aa if v>s else ar
        s=k*s+(1-k)*float(v); out[i]=s
    return out

def window(gr,sr,a,b):
    return gr[int(a*sr):int(b*sr)]

def case_metrics(gr,sr):
    return {
      "event_max":float(np.max(window(gr,sr,.16,.35))),
      "body_mean":float(np.mean(window(gr,sr,.55,1.25))),
      "whole_mean":float(np.mean(window(gr,sr,.20,1.30))),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out-dir",required=True)
    args=ap.parse_args();out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    per={}
    for sr in SRS:
      cases=make_cases(sr)
      for fc in CUTOFFS:
        key=f"{sr}:{fc}"; per[key]={}
        for name,x in cases.items():
          gr=compressor_gr(hpf(x,sr,fc),sr)
          m=case_metrics(gr,sr);per[key][name]=m
          rows.append({"sample_rate":sr,"cutoff_hz":fc,"case":name,**m})

    candidates=[]
    for fc in CUTOFFS:
      if fc==0:continue
      sr_results=[]
      for sr in SRS:
        base=per[f"{sr}:0"]; cur=per[f"{sr}:{fc}"]
        clean_male=base["male_low"]["body_mean"]
        rumble_extra=max(0.0,base["rumble"]["whole_mean"]-base["male_low"]["whole_mean"])
        rumble_cur=max(0.0,cur["rumble"]["whole_mean"]-cur["male_low"]["whole_mean"])
        rumble_reduction=1.0-(rumble_cur/max(rumble_extra,1e-9))

        plosive_excess=max(0.0,base["plosive"]["event_max"]-base["male_low"]["event_max"])
        plosive_cur=max(0.0,cur["plosive"]["event_max"]-cur["male_low"]["event_max"])
        plosive_reduction=1.0-(plosive_cur/max(plosive_excess,1e-9))

        consonant_ret=cur["consonant"]["event_max"]/max(base["consonant"]["event_max"],1e-9)
        sib_ret=cur["sibilant"]["event_max"]/max(base["sibilant"]["event_max"],1e-9)

        sr_results.append({
          "sr":sr,
          "rumble_reduction":rumble_reduction,
          "plosive_reduction":plosive_reduction,
          "male_body_delta_db":cur["male_low"]["body_mean"]-clean_male,
          "female_body_delta_db":cur["female"]["body_mean"]-base["female"]["body_mean"],
          "proximity_body_delta_db":cur["proximity"]["body_mean"]-base["proximity"]["body_mean"],
          "consonant_retention":consonant_ret,
          "sibilant_retention":sib_ret,
        })
      agg={k:float(np.mean([r[k] for r in sr_results])) for k in sr_results[0] if k!="sr"}
      spread={k:float(np.ptp([r[k] for r in sr_results])) for k in sr_results[0] if k not in ("sr",)}
      gates={
        "rumble_reduction_ge_50pct":agg["rumble_reduction"]>=.50,
        "plosive_reduction_ge_15pct":agg["plosive_reduction"]>=.15,
        "male_body_loss_le_0_30db":agg["male_body_delta_db"]>=-.30,
        "female_body_abs_delta_le_0_15db":abs(agg["female_body_delta_db"])<=.15,
        "consonant_retention_ge_90pct":agg["consonant_retention"]>=.90,
        "sibilant_retention_ge_90pct":agg["sibilant_retention"]>=.90,
        "sample_rate_body_delta_spread_le_0_10db":spread["male_body_delta_db"]<=.10,
      }
      candidates.append({"cutoff_hz":fc,"aggregate":agg,"spread":spread,"per_sr":sr_results,"gates":gates,"passes":all(gates.values())})

    passing=[c for c in candidates if c["passes"]]
    passing.sort(key=lambda c:c["cutoff_hz"])
    selected=passing[0] if passing else None
    decision="GO_TO_REAL_VOCAL" if selected else "REVISE"
    result={"decision":decision,"baseline_cutoff_hz":0,"candidates":candidates,"selected":selected,"raw_audio_persisted":False}
    (out/"sidechain_hpf_pilot.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    with (out/"matrix.csv").open("w",newline="",encoding="utf-8") as f:
      w=csv.DictWriter(f,fieldnames=["sample_rate","cutoff_hz","case","event_max","body_mean","whole_mean"])
      w.writeheader();w.writerows(rows)

    report=["# Vo.Prep Sidechain HPF Synthetic Pilot","",f"Decision: {decision}"]
    if selected:
      report += ["",f"Selected for real-vocal research: {selected['cutoff_hz']} Hz / 12 dB per octave","",json.dumps(selected["gates"],indent=2)]
    else:
      report += ["","No cutoff passed all predeclared preservation/rejection gates."]
    (out/"sidechain_hpf_pilot.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print((out/"sidechain_hpf_pilot.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
