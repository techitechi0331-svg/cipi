#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, math, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, sosfilt

POWER_FLOOR = 1.0e-12

def load_mono(path):
    sr, data = wavfile.read(path)
    arr = data.astype(np.float64)
    if np.issubdtype(data.dtype, np.integer):
        info = np.iinfo(data.dtype)
        arr /= max(abs(info.min), abs(info.max))
    if arr.ndim == 2:
        arr = arr.mean(axis=1)
    return int(sr), arr

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def biquad_hp_coeff(sr, cutoff):
    q = 1.0 / math.sqrt(2.0)
    w0 = 2.0 * math.pi * cutoff / sr
    c, s = math.cos(w0), math.sin(w0)
    alpha = s / (2.0*q)
    b0=(1+c)*0.5; b1=-(1+c); b2=(1+c)*0.5
    a0=1+alpha; a1=-2*c; a2=1-alpha
    return np.array([b0/a0,b1/a0,b2/a0]), np.array([1.0,a1/a0,a2/a0])

def smooth_power(x, alpha):
    return lfilter([1-alpha],[1,-alpha],x*x)

def crest_series(x,sr):
    alpha=math.exp(-1.0/(0.080*sr))
    rms2=smooth_power(x,alpha)
    peak2=np.empty_like(x)
    prev=0.0
    one=1-alpha
    for i,xx in enumerate(x*x):
        prev=max(xx, alpha*prev+one*xx)
        peak2[i]=prev
    c2=np.where(rms2>POWER_FLOOR,peak2/np.maximum(rms2,POWER_FLOOR),2.0)
    c2=np.clip(c2,1.0,1000.0)
    t=np.clip(np.log2(np.maximum(c2,2.0)/2.0)*0.5,0.0,1.0)
    return t

def spectral_guard_series(x,sr):
    b,a=biquad_hp_coeff(sr,5600.0)
    high=lfilter(b,a,x); high=lfilter(b,a,high)
    alpha=math.exp(-1.0/(0.020*sr))
    full=smooth_power(x,alpha); hp=smooth_power(high,alpha)
    ratio=10.0*np.log10(np.maximum(hp,POWER_FLOOR)/np.maximum(full,POWER_FLOOR))
    return np.clip((ratio+11.0)/6.0,0.0,1.0)

def low_ratio_series(x,sr):
    sos=butter(4,900.0/(sr*0.5),btype="low",output="sos")
    low=sosfilt(sos,x)
    alpha=math.exp(-1.0/(0.020*sr))
    full=smooth_power(x,alpha); lp=smooth_power(low,alpha)
    return np.clip(lp/np.maximum(full,POWER_FLOOR),0.0,10.0)

def periodicity_frames(x,sr,ends,window_samples):
    step=max(1,int(sr//12000))
    analysis_rate=sr/step
    minlag=max(1,int(analysis_rate/1200.0))
    maxlag=int(analysis_rate/80.0)
    result=np.zeros(len(ends),dtype=np.float64)
    batch_size=256
    n_down=(window_samples+step-1)//step
    nfft=1
    while nfft<2*n_down: nfft*=2
    for bs in range(0,len(ends),batch_size):
        be=min(len(ends),bs+batch_size)
        rows=[x[e-window_samples:e:step] for e in ends[bs:be]]
        L=min(map(len,rows))
        A=np.stack([r[-L:] for r in rows])
        A=A-A.mean(axis=1,keepdims=True)
        F=np.fft.rfft(A,n=nfft,axis=1)
        ac=np.fft.irfft(F*np.conj(F),n=nfft,axis=1)[:,:L]
        sq=A*A
        cs=np.concatenate([np.zeros((len(A),1)),np.cumsum(sq,axis=1)],axis=1)
        best=np.zeros(len(A))
        ml=min(maxlag,L//2)
        for lag in range(minlag,ml+1):
            le=cs[:,L]-cs[:,lag]
            re=cs[:,L-lag]
            den=np.sqrt(np.maximum(le*re,1e-18))
            best=np.maximum(best,ac[:,lag]/den)
        result[bs:be]=np.clip(best,0.0,1.0)
    return result

def retention(cand,base,mask):
    vals=cand[mask]/np.maximum(base[mask],1e-12)
    if not len(vals): return {"count":0}
    return {"count":int(len(vals)),"median":float(np.median(vals)),
            "p10":float(np.quantile(vals,0.1)),"p90":float(np.quantile(vals,0.9)),
            "min":float(np.min(vals))}

def analyze(pid,path):
    sr,x=load_mono(path)
    win=int(round(0.040*sr)); hop=max(1,int(round(0.005*sr)))
    ends=np.arange(win,len(x)+1,hop,dtype=int)
    overall=np.sqrt(np.mean(x*x))
    overall_db=20*np.log10(max(overall,POWER_FLOOR))
    active_thr_db=max(-60.0,overall_db-30.0)
    active_thr=10**(active_thr_db/20.0)
    cs=np.concatenate([[0.0],np.cumsum(x*x)])
    frame_rms=np.sqrt((cs[ends]-cs[ends-win])/win)
    active=frame_rms>active_thr

    base=crest_series(x,sr)[ends-1]
    spec=spectral_guard_series(x,sr)[ends-1]
    low=low_ratio_series(x,sr)[ends-1]
    per=periodicity_frames(x,sr,ends,win)
    cand=base*(1.0-0.75*spec*(1.0-per))

    noise=active&(base>=0.75)&(spec>=0.5)&(per<=0.35)
    bright=active&(base>=0.75)&(spec>=0.5)&(per>=0.80)
    body=active&(per>=0.80)&(base<=0.50)
    lowtran=active&(base>=0.75)&(low>=0.60)

    body_delta=np.abs(cand[body]-base[body])
    summary={
      "id":pid,"sha256":sha256(path),"sample_rate_hz":sr,
      "channels_input":int(wavfile.read(path,mmap=True)[1].shape[1] if wavfile.read(path,mmap=True)[1].ndim==2 else 1),
      "duration_seconds":float(len(x)/sr),"hop_ms_actual":float(hop/sr*1000.0),
      "active_threshold_dbfs":float(active_thr_db),
      "counts":{"analysis_frames":int(len(ends)),"active":int(active.sum()),
                "noise_like_highband":int(noise.sum()),"bright_voiced":int(bright.sum()),
                "periodic_body":int(body.sum()),"low_frequency_transient":int(lowtran.sum())},
      "noise_retention":retention(cand,base,noise),
      "bright_retention":retention(cand,base,bright),
      "low_frequency_transient_retention":retention(cand,base,lowtran),
      "body":{"count":int(body.sum()),
              "mean_abs_delta":float(body_delta.mean()) if len(body_delta) else None,
              "p90_abs_delta":float(np.quantile(body_delta,0.9)) if len(body_delta) else None},
      "periodicity_quantiles_active":{str(q):float(np.quantile(per[active],q)) for q in (0.1,0.25,0.5,0.75,0.9)},
      "finite":bool(np.isfinite(base).all() and np.isfinite(cand).all() and np.isfinite(spec).all() and np.isfinite(per).all())
    }
    return summary,{"active":active,"base":base,"cand":cand,"spec":spec,"per":per,"low":low}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("files",nargs="+",help="Private/local WAV paths; never written into output.")
    args=ap.parse_args()
    summaries=[]; arrays=[]
    for i,path in enumerate(args.files,1):
        s,a=analyze(f"PV{i}",path); summaries.append(s); arrays.append(a)

    def pooled_mask(kind,a):
        if kind=="noise": return a["active"]&(a["base"]>=0.75)&(a["spec"]>=0.5)&(a["per"]<=0.35)
        if kind=="bright": return a["active"]&(a["base"]>=0.75)&(a["spec"]>=0.5)&(a["per"]>=0.80)
        if kind=="low": return a["active"]&(a["base"]>=0.75)&(a["low"]>=0.60)
        raise ValueError(kind)

    pooled={}
    for kind in ("noise","bright","low"):
        vals=[]
        for a in arrays:
            m=pooled_mask(kind,a)
            vals.extend((a["cand"][m]/np.maximum(a["base"][m],1e-12)).tolist())
        vals=np.asarray(vals)
        pooled[kind]={"count":int(len(vals))}
        if len(vals):
            pooled[kind].update({"median":float(np.median(vals)),"p10":float(np.quantile(vals,0.1)),
                                 "p90":float(np.quantile(vals,0.9)),"min":float(vals.min())})
    bodyvals=[]
    for a in arrays:
        m=a["active"]&(a["per"]>=0.80)&(a["base"]<=0.50)
        bodyvals.extend(np.abs(a["cand"][m]-a["base"][m]).tolist())
    pooled["body"]={"count":len(bodyvals),"mean_abs_delta":float(np.mean(bodyvals)) if bodyvals else None}

    pairs=[]
    for i,j in itertools.combinations(range(len(arrays)),2):
        a,b=arrays[i],arrays[j]; common=a["active"]&b["active"]
        def corr(x,y):
            if len(x)<3 or np.std(x)<1e-12 or np.std(y)<1e-12: return None
            return float(np.corrcoef(x,y)[0,1])
        pairs.append({"pair":f"PV{i+1}-PV{j+1}","common_active":int(common.sum()),
                      "baseline_corr":corr(a["base"][common],b["base"][common]),
                      "candidate_corr":corr(a["cand"][common],b["cand"][common]),
                      "spectral_guard_corr":corr(a["spec"][common],b["spec"][common]),
                      "periodicity_corr":corr(a["per"][common],b["per"][common])})
    bc=[p["baseline_corr"] for p in pairs if p["baseline_corr"] is not None]
    cc=[p["candidate_corr"] for p in pairs if p["candidate_corr"] is not None]
    pooled["pairwise"]=pairs
    pooled["correlation_summary"]={
       "baseline_median":float(np.median(bc)),"candidate_median":float(np.median(cc)),
       "candidate_minus_baseline_median":float(np.median(cc)-np.median(bc))
    }

    enough = pooled["noise"]["count"]>=30 and pooled["bright"]["count"]>=30 and pooled["low"]["count"]>=30
    criteria={
      "all_finite":all(s["finite"] for s in summaries),
      "active_frames_each_ge_100":all(s["counts"]["active"]>=100 for s in summaries),
      "bright_count_ge_30":pooled["bright"]["count"]>=30,
      "noise_count_ge_30":pooled["noise"]["count"]>=30,
      "low_count_ge_30":pooled["low"]["count"]>=30,
      "bright_median_ge_0_95":pooled["bright"].get("median",0)>=0.95,
      "bright_p10_ge_0_85":pooled["bright"].get("p10",0)>=0.85,
      "low_median_ge_0_90":pooled["low"].get("median",0)>=0.90,
      "low_p10_ge_0_80":pooled["low"].get("p10",0)>=0.80,
      "noise_median_le_0_35":pooled["noise"].get("median",1)>0 and pooled["noise"].get("median",1)<=0.35,
      "body_mean_abs_delta_le_0_03":pooled["body"]["mean_abs_delta"] is not None and pooled["body"]["mean_abs_delta"]<=0.03,
      "candidate_corr_median_ge_0_80":pooled["correlation_summary"]["candidate_median"]>=0.80,
      "candidate_corr_drop_le_0_05":pooled["correlation_summary"]["candidate_minus_baseline_median"]>=-0.05,
    }
    if not enough:
        decision="INCONCLUSIVE"
    elif all(criteria.values()):
        decision="PASS"
    else:
        decision="REJECT"
    output={"schema":"peakbody-private-real-vocal-guard-01","decision":decision,
            "sources":summaries,"pooled":pooled,"criteria":criteria,
            "privacy":"aggregate non-reversible metrics only; no raw audio or frame timecodes"}
    print(json.dumps(output,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
