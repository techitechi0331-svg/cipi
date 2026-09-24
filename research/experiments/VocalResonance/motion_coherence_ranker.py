"""CIPI VOCAL-RESONANCE v0.4R.3 motion-coherence experiment.

Research only. No production DSP. No raw audio is persisted.

Question:
Can F0/harmonic motion coherence improve candidate ranking beyond the
v0.4R.2 causal-safe-negative static ranker while reducing clean false triggers?

The experiment streams VocalSet, decodes audio in runner memory, uses controlled
peaking-EQ injections, trains on positive + safe-negative labels, and compares:
- prominence-only baseline;
- v0.4R.2-style static safe-negative logistic ranker;
- v0.4R.3 static + motion-coherence ranker.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
from datasets import Audio, load_dataset
from scipy import ndimage, signal
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FS = 24000
DATASET = "Bill13579/vocalset-mirror"

TRAIN_SINGERS = {
    "f1","f2","f3","f4","f5","f6",
    "m1","m2","m3","m4","m5","m6",
}
VALID_SINGERS = {"f7","f8","m7","m8"}
TEST_SINGERS = {"f9","m9","m10","m11"}

STATIC_FEATURES = [
    "rel_local_score",
    "rel_log_score",
    "rel_persistence",
    "rel_q80",
    "rel_variability",
    "rel_norm_q",
    "rel_prom_x_persist",
    "rel_local_minus_log",
    "rel_cross_agreement",
    "harmonic_protection",
    "candidate_rank_score",
    "log_frequency",
]

MOTION_FEATURES = STATIC_FEATURES + [
    "ridge_harmonic_closeness",
    "ridge_motion_corr",
    "ridge_fixedness",
    "ridge_motion_ratio",
    "voiced_fraction",
    "pitch_span_norm",
]


def split_name(singer: str) -> str:
    if singer in TRAIN_SINGERS:
        return "train"
    if singer in VALID_SINGERS:
        return "valid"
    if singer in TEST_SINGERS:
        return "test"
    return "unused"


def to_mono_resampled(audio_bytes: bytes) -> np.ndarray:
    x, sr = sf.read(io.BytesIO(audio_bytes), always_2d=False, dtype="float64")
    if x.ndim > 1:
        x = np.mean(x, axis=1)
    if sr != FS:
        g = math.gcd(int(sr), FS)
        x = signal.resample_poly(x, FS // g, int(sr) // g)
    if not len(x):
        return np.asarray([], dtype=np.float64)
    peak = float(np.max(np.abs(x))) + 1e-12
    if peak > 1.0:
        x = x / peak
    return np.asarray(x, dtype=np.float64)


def best_energy_segment(x: np.ndarray, seconds: float = 7.0) -> np.ndarray:
    n = int(seconds * FS)
    if len(x) <= n:
        return x
    hop = FS
    best_start = 0
    best_rms = -1.0
    for start in range(0, len(x)-n+1, hop):
        seg = x[start:start+n]
        rms = float(np.sqrt(np.mean(seg*seg) + 1e-18))
        if rms > best_rms:
            best_rms = rms
            best_start = start
    return x[best_start:best_start+n]


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


def collect_examples(max_files: int, scan_limit: int, skip_per_singer: int):
    ds = load_dataset(DATASET, split="train", streaming=True)
    ds = ds.cast_column("audio", Audio(decode=False))

    selected = []
    per_label = defaultdict(int)
    per_singer = defaultdict(int)
    encountered = defaultdict(int)
    label_cap = 4
    singer_cap = 2

    for idx, row in enumerate(ds):
        if idx >= scan_limit or len(selected) >= max_files:
            break
        cell = row.get("audio")
        if not isinstance(cell, dict):
            continue
        path = str(cell.get("path") or "")
        singer = singer_id_from_path(path)
        if singer == "unknown":
            continue
        if encountered[singer] < skip_per_singer:
            encountered[singer] += 1
            continue
        encountered[singer] += 1

        label = str(row.get("label", "unknown"))
        if per_singer[singer] >= singer_cap or per_label[label] >= label_cap:
            continue
        data = cell.get("bytes")
        if data is None:
            continue
        try:
            x = to_mono_resampled(data)
        except Exception:
            continue
        if len(x) < FS:
            continue
        x = best_energy_segment(x)
        if float(np.sqrt(np.mean(x*x)+1e-18)) < 1e-4:
            continue
        selected.append({
            "index": idx,
            "label": label,
            "singer": singer,
            "source_basename": Path(path).name,
            "audio": x,
        })
        per_label[label] += 1
        per_singer[singer] += 1
    return selected


def rbj_peak(fc: float, q: float, gain_db: float):
    A = 10 ** (gain_db / 40.0)
    w0 = 2*np.pi*fc/FS
    alpha = np.sin(w0)/(2*q)
    c = np.cos(w0)
    b = np.array([1+alpha*A, -2*c, 1-alpha*A])
    a = np.array([1+alpha/A, -2*c, 1-alpha/A])
    return b/a[0], a/a[0]


def inject(x: np.ndarray, fc: float, q: float, gain_db: float):
    b, a = rbj_peak(fc, q, gain_db)
    zi = signal.lfilter_zi(b, a) * x[0]
    y, _ = signal.lfilter(b, a, x, zi=zi)
    return y


def stft_db(x: np.ndarray):
    f, t, z = signal.stft(
        x, fs=FS, window="hann", nperseg=768, noverlap=672,
        boundary=None, padded=False
    )
    keep = (f >= 150) & (f <= 10000)
    return f[keep], t, 20*np.log10(np.abs(z[keep]).T + 1e-8)


def robust_z(residual: np.ndarray):
    med = np.median(residual, axis=1, keepdims=True)
    mad = np.median(np.abs(residual-med), axis=1, keepdims=True) + 0.2
    return np.maximum((residual-med)/(1.4826*mad), 0)


def build_fields(f: np.ndarray, mag: np.ndarray):
    env = ndimage.gaussian_filter1d(mag, 4, axis=1, mode="nearest")
    local_z = robust_z(mag-env)
    local = np.quantile(local_z, 0.82, axis=0)

    centers = np.geomspace(180, 10000, 96)
    power = 10**(mag/10)
    weights = []
    for center in centers:
        bw = max(60, center/8)
        w = np.exp(-0.5*((f-center)/(bw/2.355))**2)
        w /= w.sum() + 1e-12
        weights.append(w)
    weights = np.stack(weights, axis=1)
    pooled = 10*np.log10(power @ weights + 1e-12)
    penv = ndimage.gaussian_filter1d(pooled, 2, axis=1, mode="nearest")
    log_z = robust_z(pooled-penv)
    log_field = np.quantile(log_z, 0.80, axis=0)
    return local, centers, log_field, local_z


def sparse_select(freq, score, k, peaks_only=False):
    if peaks_only:
        idx, _ = signal.find_peaks(score)
        order = idx[np.argsort(score[idx])[::-1]] if len(idx) else np.argsort(score)[::-1]
    else:
        order = np.argsort(score)[::-1]
    chosen = []
    for i in order:
        tol = max(55.0, 0.018*freq[i])
        if all(abs(freq[i]-freq[j]) >= max(tol, max(55.0,0.018*freq[j])) for j in chosen):
            chosen.append(int(i))
        if len(chosen) >= k:
            break
    return np.asarray(chosen, dtype=int)


def candidate_sets(f, local, centers, log_field):
    local_idx = sparse_select(f, local, 35, peaks_only=True)
    peak_idx = sparse_select(centers, log_field, 15, peaks_only=True)
    dense_idx = sparse_select(centers, log_field, 35, peaks_only=False)

    log_hybrid = list(centers[peak_idx[:10]])
    for fr in centers[dense_idx]:
        if all(abs(fr-old) >= max(55,0.018*max(fr,old)) for old in log_hybrid):
            log_hybrid.append(float(fr))
        if len(log_hybrid) >= 20:
            break

    objs = []
    for rank, fr in enumerate(f[local_idx], 1):
        objs.append({"freq":float(fr),"lr":rank,"gr":None,"sources":1})
    for rank, fr in enumerate(log_hybrid, 1):
        best = None
        best_d = 1e9
        for j, obj in enumerate(objs):
            tol = max(70.0, 0.018*max(fr,obj["freq"]))
            d = abs(fr-obj["freq"])
            if d < tol and d < best_d:
                best, best_d = j, d
        if best is None:
            objs.append({"freq":float(fr),"lr":None,"gr":rank,"sources":1})
        else:
            objs[best]["freq"] = 0.5*(objs[best]["freq"]+float(fr))
            objs[best]["gr"] = rank
            objs[best]["sources"] = 2

    for obj in objs:
        ranks = [1/r for r in [obj["lr"],obj["gr"]] if r is not None]
        obj["score"] = max(ranks) + 0.25*(obj["sources"]-1)

    chosen = []
    remaining = list(range(len(objs)))
    while remaining and len(chosen) < 20:
        best = None
        best_value = -1e9
        for j in remaining:
            base = objs[j]["score"]
            if chosen:
                dist = min(abs(np.log2(objs[j]["freq"]/objs[k]["freq"])) for k in chosen)
                value = 0.8*base + 0.2*min(dist,1.0)
            else:
                value = base
            if value > best_value:
                best_value, best = value, j
        chosen.append(best)
        remaining.remove(best)
    return np.asarray([objs[j]["freq"] for j in chosen])


def physical_effect(clean_mag, f, fc, q, gain_db):
    power = np.mean(10**(clean_mag/10), axis=0)
    b, a = rbj_peak(fc, q, gain_db)
    _, h = signal.freqz(b, a, worN=2*np.pi*f/FS)
    bw = max(fc/q, 30)
    mask = np.abs(f-fc) <= max(50, 0.8*bw)
    ratio = np.sum(power[mask]*np.abs(h[mask])**2)/(np.sum(power[mask])+1e-24)
    return float(10*np.log10(ratio+1e-24))


def estimate_f0_track(x: np.ndarray):
    frame = int(0.080*FS)
    hop = int(0.020*FS)
    min_lag = max(1, int(FS/1000.0))
    max_lag = min(frame-2, int(FS/70.0))
    window = np.hanning(frame)
    times, values, confidence = [], [], []
    for start in range(0, max(1, len(x)-frame+1), hop):
        seg = np.asarray(x[start:start+frame], dtype=float)
        if len(seg) < frame:
            break
        t = (start + frame/2) / FS
        seg = (seg-np.mean(seg))*window
        rms = float(np.sqrt(np.mean(seg*seg)+1e-18))
        if rms < 1e-4:
            times.append(t); values.append(np.nan); confidence.append(0.0); continue
        ac = signal.correlate(seg, seg, mode="full", method="fft")[frame-1:]
        zero = float(ac[0]) + 1e-18
        region = ac[min_lag:max_lag+1]
        if not len(region):
            times.append(t); values.append(np.nan); confidence.append(0.0); continue
        rel = region/zero
        idx = int(np.argmax(rel))
        lag = min_lag+idx
        conf = float(np.clip(rel[idx],0,1))
        times.append(t)
        values.append(np.nan if conf < 0.18 else FS/lag)
        confidence.append(conf)
    return np.asarray(times), np.asarray(values), np.asarray(confidence)


def nearest_agreement(freq, pool):
    if not len(pool):
        return 0.0
    dist = float(np.min(np.abs(pool-freq)))
    scale = max(70.0, 0.02*freq)
    return float(np.exp(-dist/scale))


def contiguous_width(freqs, score, idx):
    peak = float(score[idx])
    if peak <= 1e-9:
        return float(freqs[min(len(freqs)-1,idx+1)]-freqs[max(0,idx-1)])
    threshold = 0.5*peak
    lo=idx; hi=idx
    while lo>0 and score[lo-1]>=threshold and idx-lo<20: lo-=1
    while hi+1<len(score) and score[hi+1]>=threshold and hi-idx<20: hi+=1
    return float(max(1.0,freqs[hi]-freqs[lo]))


def motion_features(freq, f, t, local_frames, f0_t, f0, f0_conf):
    width = max(90.0, 0.03*freq)
    mask = np.abs(f-freq) <= width
    if int(np.sum(mask)) < 2:
        return dict(
            ridge_harmonic_closeness=0.0, ridge_motion_corr=0.0,
            ridge_fixedness=1.0, ridge_motion_ratio=0.0,
            voiced_fraction=0.0, pitch_span_norm=0.0
        )

    pool_f = f[mask]
    pool = local_frames[:,mask]
    ridge = pool_f[np.argmax(pool, axis=1)]

    valid_pitch = np.isfinite(f0)
    f0_safe = np.where(valid_pitch, f0, 0.0)
    interp_f0 = np.interp(t, f0_t, f0_safe, left=0.0, right=0.0)
    interp_conf = np.interp(t, f0_t, f0_conf, left=0.0, right=0.0)
    valid = (interp_f0 > 0.0) & (interp_conf >= 0.18)
    voiced_fraction = float(np.mean(valid)) if len(valid) else 0.0
    if np.sum(valid) < 8:
        return dict(
            ridge_harmonic_closeness=0.0, ridge_motion_corr=0.0,
            ridge_fixedness=float(np.exp(-np.std(ridge)/max(30.0,0.015*freq))),
            ridge_motion_ratio=0.0, voiced_fraction=voiced_fraction,
            pitch_span_norm=0.0
        )

    rv = ridge[valid]
    fv = interp_f0[valid]
    harmonic_index = np.maximum(1.0, np.round(rv/fv))
    harmonic_track = harmonic_index*fv
    norm_dist = np.clip(np.abs(rv-harmonic_track)/(0.5*fv+1e-9),0,1)
    closeness = 1.0-float(np.median(norm_dist))

    dr = np.diff(rv)
    dh = np.diff(harmonic_track)
    if len(dr) >= 4 and np.std(dr)>1e-6 and np.std(dh)>1e-6:
        corr = float(np.corrcoef(dr,dh)[0,1])
        if not np.isfinite(corr): corr=0.0
    else:
        corr=0.0

    fixedness = float(np.exp(-np.std(rv)/max(30.0,0.015*freq)))
    motion_ratio = float(np.std(rv)/(np.std(harmonic_track)+1e-9))
    pitch_span = float(np.std(fv)/(np.mean(fv)+1e-9))

    return dict(
        ridge_harmonic_closeness=closeness,
        ridge_motion_corr=float(np.clip(corr,-1,1)),
        ridge_fixedness=fixedness,
        ridge_motion_ratio=float(np.clip(motion_ratio,0,5)),
        voiced_fraction=voiced_fraction,
        pitch_span_norm=float(np.clip(pitch_span,0,2)),
    )


def extract_candidates(x, f0_t, f0, f0_conf):
    f,t,mag = stft_db(x)
    local,centers,log_field,local_frames = build_fields(f,mag)
    merged = candidate_sets(f,local,centers,log_field)
    local20 = f[sparse_select(f,local,20,peaks_only=True)]

    peak_idx=sparse_select(centers,log_field,15,peaks_only=True)
    dense_idx=sparse_select(centers,log_field,35,peaks_only=False)
    log_hybrid=list(centers[peak_idx[:10]])
    for fr in centers[dense_idx]:
        if all(abs(fr-old)>=max(55,0.018*max(fr,old)) for old in log_hybrid):
            log_hybrid.append(float(fr))
        if len(log_hybrid)>=20: break
    log_hybrid=np.asarray(log_hybrid[:20])

    rows=[]
    for rank,freq in enumerate(merged[:20],1):
        idx=int(np.argmin(np.abs(f-freq)))
        trajectory=local_frames[:,idx]
        width=contiguous_width(f,local,idx)
        la=nearest_agreement(freq,local20)
        ga=nearest_agreement(freq,log_hybrid)

        valid=np.isfinite(f0)&(f0_conf>=0.18)
        if np.any(valid):
            vals=f0[valid]
            h=np.maximum(1.0,np.round(freq/vals))
            nearest=h*vals
            norm=np.clip(np.abs(freq-nearest)/(0.5*vals+1e-9),0,1)
            harmonic_closeness=1.0-float(np.median(norm))
            f0c=float(np.mean(f0_conf[valid]))
            f0med=float(np.median(vals))
        else:
            harmonic_closeness=0.0; f0c=0.0; f0med=np.nan

        row={
            "candidate_rank":rank,
            "candidate_hz":float(freq),
            "local_score":float(local[idx]),
            "log_score":float(np.interp(freq,centers,log_field)),
            "local_persistence":float(np.mean(trajectory>1.0)),
            "local_q80":float(np.quantile(trajectory,0.80)),
            "local_variability":float(np.std(trajectory)),
            "local_width_hz":width,
            "local_agreement":la,
            "log_agreement":ga,
            "cross_agreement":la*ga,
            "harmonic_closeness":harmonic_closeness,
            "f0_confidence":f0c,
            "case_f0_median":f0med,
        }
        row.update(motion_features(float(freq),f,t,local_frames,f0_t,f0,f0_conf))
        rows.append(row)
    return rows,f,mag


def nearest_clean(row, clean_rows):
    if not clean_rows: return None,float("inf")
    d=np.asarray([abs(c["candidate_hz"]-row["candidate_hz"]) for c in clean_rows])
    i=int(np.argmin(d))
    return clean_rows[i],float(d[i])


def safe_negative(row,clean_rows,target_fc,target_tol):
    freq=float(row["candidate_hz"])
    if abs(freq-target_fc)<=max(2*target_tol,140.0,0.05*target_fc):
        return False
    clean,fd=nearest_clean(row,clean_rows)
    if clean is None or fd>max(70.0,0.025*freq):
        return False
    return (
        abs(row["local_score"]-clean["local_score"]) <= 0.18*max(1.0,abs(clean["local_score"]))+0.10
        and abs(row["log_score"]-clean["log_score"]) <= 0.18*max(1.0,abs(clean["log_score"]))+0.10
        and abs(row["local_persistence"]-clean["local_persistence"]) <= 0.08
        and abs(row["local_q80"]-clean["local_q80"]) <= 0.30
    )


def append_rows(out,candidates,*,split,singer,label,source,case_id,clean_rows,
                target_fc=None,target_q=None,target_gain=None,effect=None):
    nearest_i=None; tol=None
    if target_fc is not None:
        tol=max(70.0,0.7*target_fc/float(target_q))
        errs=np.asarray([abs(r["candidate_hz"]-target_fc) for r in candidates])
        if len(errs) and float(np.min(errs))<=tol:
            nearest_i=int(np.argmin(errs))
    for i,r in enumerate(candidates):
        is_target=int(nearest_i is not None and i==nearest_i)
        neg=0
        if target_fc is not None and not is_target:
            neg=int(safe_negative(r,clean_rows,target_fc,float(tol)))
        row=dict(r)
        row.update({
            "split":split,"singer":singer,"label_name":label,"source_name":source,
            "case_id":case_id,"is_clean":int(target_fc is None),
            "target_hz":np.nan if target_fc is None else target_fc,
            "target_q":np.nan if target_q is None else target_q,
            "target_gain_db":np.nan if target_gain is None else target_gain,
            "physical_effect_db":np.nan if effect is None else effect,
            "is_target":is_target,"safe_negative":neg,
            "generator_hit":int(nearest_i is not None),
        })
        out.append(row)


def build_dataset(seed,skip_per_singer):
    rng=np.random.default_rng(seed)
    examples=collect_examples(40,5000,skip_per_singer)
    if len(examples)<35:
        raise RuntimeError(f"Only {len(examples)} usable VocalSet examples")
    rows=[]
    gains=np.asarray([3.0,4.5,6.0,9.0])
    qs=np.asarray([4,8,16,30])
    for ex_i,ex in enumerate(examples):
        split=split_name(ex["singer"])
        if split=="unused": continue
        clean=ex["audio"]
        f0_t,f0,f0_conf=estimate_f0_track(clean)
        clean_candidates,f,clean_mag=extract_candidates(clean,f0_t,f0,f0_conf)
        append_rows(rows,clean_candidates,split=split,singer=ex["singer"],
                    label=ex["label"],source=ex["source_basename"],
                    case_id=f'{ex["singer"]}:{ex["source_basename"]}:clean',
                    clean_rows=clean_candidates)
        for inj in range(4):
            fc=float(np.exp(rng.uniform(np.log(250),np.log(9000))))
            gain=float(gains[(ex_i+inj)%len(gains)])
            q=int(qs[(2*ex_i+inj)%len(qs)])
            y=inject(clean,fc,q,gain)
            effect=physical_effect(clean_mag,f,fc,q,gain)
            cand,_,_=extract_candidates(y,f0_t,f0,f0_conf)
            append_rows(rows,cand,split=split,singer=ex["singer"],label=ex["label"],
                        source=ex["source_basename"],
                        case_id=f'{ex["singer"]}:{ex["source_basename"]}:inj{inj}',
                        clean_rows=clean_candidates,target_fc=fc,target_q=q,
                        target_gain=gain,effect=effect)
    return pd.DataFrame(rows)


def add_relative(frame):
    frame=frame.copy()
    frame["norm_q"]=frame["candidate_hz"]/frame["local_width_hz"].clip(lower=1.0)
    frame["prom_x_persist"]=frame["local_score"]*frame["local_persistence"]
    frame["local_minus_log"]=frame["local_score"]-frame["log_score"]
    frame["harmonic_protection"]=frame["harmonic_closeness"]*frame["f0_confidence"]
    frame["candidate_rank_score"]=1.0-(frame["candidate_rank"].astype(float)-1.0)/19.0
    frame["log_frequency"]=np.log2(frame["candidate_hz"].clip(lower=80.0)/1000.0)
    rel={
        "local_score":"rel_local_score","log_score":"rel_log_score",
        "local_persistence":"rel_persistence","local_q80":"rel_q80",
        "local_variability":"rel_variability","norm_q":"rel_norm_q",
        "prom_x_persist":"rel_prom_x_persist",
        "local_minus_log":"rel_local_minus_log",
        "cross_agreement":"rel_cross_agreement",
    }
    g=frame.groupby("case_id",sort=False)
    for src,dst in rel.items():
        mean=g[src].transform("mean")
        std=g[src].transform("std").fillna(0.0).where(lambda x:x>1e-6,1.0)
        frame[dst]=(frame[src]-mean)/std
    return frame


def labelled(frame):
    return frame[(frame.is_clean==0)&((frame.is_target==1)|(frame.safe_negative==1))].copy()


def rank_metrics(frame,score_col):
    inj=frame[frame.is_clean==0]
    groups=list(inj.groupby("case_id"))
    out={"n_cases":len(groups)}
    out["generator_ceiling"]=float(np.mean([int(g.generator_hit.max()>0) for _,g in groups])) if groups else 0.0
    for k in [1,3,5]:
        hits=[]; cond=[]
        for _,g in groups:
            h=int(g.sort_values(score_col,ascending=False).head(k).is_target.max()>0)
            hits.append(h)
            if g.generator_hit.max()>0: cond.append(h)
        out[f"top{k}"]=float(np.mean(hits)) if hits else 0.0
        out[f"top{k}_given_generator_hit"]=float(np.mean(cond)) if cond else 0.0
    rr=[]
    for _,g in groups:
        ranked=g.sort_values(score_col,ascending=False).reset_index(drop=True)
        pos=np.flatnonzero(ranked.is_target.to_numpy()==1)
        rr.append(0.0 if not len(pos) else 1.0/float(pos[0]+1))
    out["mrr"]=float(np.mean(rr)) if rr else 0.0

    strong=inj[inj.physical_effect_db>=3.0]
    sh=[]
    for _,g in strong.groupby("case_id"):
        sh.append(int(g.sort_values(score_col,ascending=False).head(5).is_target.max()>0))
    out["top5_effect_gte3"]=float(np.mean(sh)) if sh else None

    case_f0=inj.groupby("case_id").case_f0_median.median()
    high=set(case_f0[case_f0>=500.0].index)
    hh=[]
    for cid,g in groups:
        if cid in high:
            hh.append(int(g.sort_values(score_col,ascending=False).head(5).is_target.max()>0))
    out["top5_high_f0"]=float(np.mean(hh)) if hh else None
    out["n_high_f0_cases"]=len(hh)
    return out


def choose_threshold(frame,score_col):
    clean=frame[frame.is_clean==1]
    maxima=clean.groupby("case_id")[score_col].max().to_numpy()
    return float(np.quantile(maxima,0.95)) if len(maxima) else float("inf")


def clean_false(frame,score_col,threshold):
    clean=frame[frame.is_clean==1]
    maxima=clean.groupby("case_id")[score_col].max()
    return float(np.mean(maxima>threshold)) if len(maxima) else 0.0


def clean_false_by_label(frame,score_col,threshold):
    clean=frame[frame.is_clean==1].copy()
    rows=[]
    for cid,g in clean.groupby("case_id"):
        rows.append({
            "case_id":cid,"label_name":str(g.label_name.iloc[0]),
            "trigger":int(float(g[score_col].max())>threshold)
        })
    if not rows: return {}
    d=pd.DataFrame(rows)
    return {str(k):float(v) for k,v in d.groupby("label_name").trigger.mean().items()}


def fit_ranker(train,valid,features):
    tr=labelled(train)
    if tr.is_target.sum()<20 or tr.safe_negative.sum()<50:
        raise RuntimeError("insufficient certain labels")
    weights=np.ones(len(tr),dtype=float)
    pos=tr.is_target.to_numpy()==1
    eff=tr.physical_effect_db.fillna(0.0).to_numpy()
    weights[pos]=np.clip(eff[pos]/3.0,0.25,2.0)
    trials=[]
    for cval in [0.03,0.1,0.3,1.0,3.0]:
        pipe=Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(C=cval,class_weight="balanced",max_iter=3000,
                                        solver="lbfgs",random_state=20260929))
        ])
        pipe.fit(tr[features],tr.is_target,model__sample_weight=weights)
        vv=valid.copy()
        vv["score"]=pipe.predict_proba(vv[features])[:,1]
        m=rank_metrics(vv,"score")
        strong=-1.0 if m["top5_effect_gte3"] is None else m["top5_effect_gte3"]
        trials.append(((m["top5"],strong,m["mrr"],-cval),cval,pipe,m))
    trials.sort(key=lambda x:x[0],reverse=True)
    _,cval,pipe,m=trials[0]
    return pipe,cval,m,tr


def evaluate(frame,features,name):
    train=frame[frame.split=="train"].copy()
    valid=frame[frame.split=="valid"].copy()
    test=frame[frame.split=="test"].copy()
    pipe,cval,vm,tr=fit_ranker(train,valid,features)
    for part in (train,valid,test):
        part[name]=pipe.predict_proba(part[features])[:,1]
    th=choose_threshold(valid,name)
    tm=rank_metrics(test,name)
    tm["clean_false_trigger"]=clean_false(test,name,th)
    tm["threshold_from_valid_95pct"]=th
    tm["clean_false_by_label"]=clean_false_by_label(test,name,th)
    model=pipe.named_steps["model"]
    coef=pd.DataFrame({"feature":features,"coefficient":model.coef_[0]})
    return tm,vm,cval,coef,tr


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--seed",type=int,default=20260929)
    ap.add_argument("--skip-per-singer",type=int,default=2)
    args=ap.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)

    frame=add_relative(build_dataset(args.seed,args.skip_per_singer))
    test=frame[frame.split=="test"].copy()

    static_test,static_valid,static_c,static_coef,_=evaluate(
        frame,STATIC_FEATURES,"static_score"
    )
    motion_test,motion_valid,motion_c,motion_coef,_=evaluate(
        frame,MOTION_FEATURES,"motion_score"
    )

    test["prominence_score"]=test["local_score"]
    prom=rank_metrics(test,"prominence_score")
    prom_th=choose_threshold(frame[frame.split=="valid"],"local_score")
    prom["clean_false_trigger"]=clean_false(test,"local_score",prom_th)

    retention_accept=(
        motion_test["top5"] >= static_test["top5"] + 0.05
        and motion_test["clean_false_trigger"] <= static_test["clean_false_trigger"] - 0.05
        and (motion_test["top5_effect_gte3"] or 0.0) >= (static_test["top5_effect_gte3"] or 0.0)
        and (
            static_test["top5_high_f0"] is None
            or motion_test["top5_high_f0"] is None
            or motion_test["top5_high_f0"] >= static_test["top5_high_f0"] - 0.05
        )
    )

    product_gate=(
        motion_test["top5"]>=0.85
        and (motion_test["top5_effect_gte3"] or 0.0)>=0.92
        and motion_test["clean_false_trigger"]<=0.15
    )

    summary={
        "experiment":"VOCAL_RESONANCE_R3_MOTION_COHERENCE",
        "dataset":DATASET,
        "seed":args.seed,
        "skip_per_singer":args.skip_per_singer,
        "candidate_budget":20,
        "models":{
            "prominence":{"test":prom},
            "static_r2_style":{"C":static_c,"validation":static_valid,"test":static_test},
            "motion_r3":{"C":motion_c,"validation":motion_valid,"test":motion_test},
        },
        "retention_gate":{
            "accepted":bool(retention_accept),
            "meaning":"Whether motion features are worth retaining for further research; not a product promotion.",
            "criteria":{
                "top5_plus_0_05_vs_static":bool(motion_test["top5"]>=static_test["top5"]+0.05),
                "clean_false_minus_0_05_vs_static":bool(motion_test["clean_false_trigger"]<=static_test["clean_false_trigger"]-0.05),
                "strong_top5_not_worse":bool((motion_test["top5_effect_gte3"] or 0.0)>=(static_test["top5_effect_gte3"] or 0.0)),
                "high_f0_not_worse_by_0_05":bool(
                    static_test["top5_high_f0"] is None or motion_test["top5_high_f0"] is None
                    or motion_test["top5_high_f0"]>=static_test["top5_high_f0"]-0.05
                ),
            }
        },
        "product_gate":{
            "passed":bool(product_gate),
            "criteria":{"top5":0.85,"strong_top5":0.92,"clean_false_trigger_max":0.15}
        },
        "raw_audio_persisted":False,
    }

    comparison=[]
    for model,data in [
        ("prominence",prom),
        ("static_r2_style",static_test),
        ("motion_r3",motion_test),
    ]:
        row={"model":model}
        for k,v in data.items():
            if isinstance(v,(int,float,np.integer,np.floating)) or v is None:
                row[k]=v
        comparison.append(row)
    pd.DataFrame(comparison).to_csv(out/"comparison.csv",index=False)
    static_coef.assign(model="static_r2_style").to_csv(out/"static_coefficients.csv",index=False)
    motion_coef.assign(model="motion_r3").to_csv(out/"motion_coefficients.csv",index=False)

    subgroup=[]
    for model,data in [("static_r2_style",static_test),("motion_r3",motion_test)]:
        for label,rate in data["clean_false_by_label"].items():
            subgroup.append({"model":model,"label":label,"clean_false_trigger_rate":rate})
    pd.DataFrame(subgroup).to_csv(out/"clean_false_by_label.csv",index=False)

    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary))


if __name__=="__main__":
    main()
