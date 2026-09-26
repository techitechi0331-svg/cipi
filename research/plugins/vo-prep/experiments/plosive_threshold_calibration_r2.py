#!/usr/bin/env python3
"""Vo.Prep Plosive Guard R2 bounded activation-threshold calibration.

Research only. Reuses the frozen v1 signal matrix and feature family.
No product DSP mutation and no raw audio.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import plosive_adversarial_v1 as v1

THRESHOLDS=(0.75,0.72,0.70)
RELEASE_THRESHOLD=0.55

class CalibratedDetector(v1.ContextDetector):
    activation_threshold=0.75
    def process(self,x:float):
        if not math.isfinite(x): x=0.0
        x=max(-64.0,min(64.0,x))
        sub=self.sub.process(x); mid=self.mid.process(x); broad=self.broad.process(x)
        self.sub_fast=self.follow(sub*sub,self.sub_fast,self.fast_c)
        self.mid_fast=self.follow(mid*mid,self.mid_fast,self.fast_c)
        self.broad_fast=self.follow(broad*broad,self.broad_fast,self.fast_c)
        self.sub_slow=self.follow(sub*sub,self.sub_slow,self.sub_slow_c)
        self.broad_slow=self.follow(broad*broad,self.broad_slow,self.broad_slow_c)
        self.divider+=1
        if self.divider>=8:
            self.divider=0
            sub_db=10.0*math.log10(max(self.sub_fast,1e-12))
            mid_db=10.0*math.log10(max(self.mid_fast,1e-12))
            broad_db=10.0*math.log10(max(self.broad_fast,1e-12))
            sub_slow_db=10.0*math.log10(max(self.sub_slow,1e-12))
            broad_slow_db=10.0*math.log10(max(self.broad_slow,1e-12))
            if broad_db < -90.0:
                self.probability=0.0
            else:
                c1=self.sigmoid(((sub_db-sub_slow_db)-7.0)/2.0)
                c2=self.sigmoid(((sub_db-mid_db)-12.0)/3.5)
                c3=self.sigmoid(((sub_db-broad_db)-2.5)/1.8)
                c4=self.sigmoid(((broad_db-broad_slow_db)-1.0)/3.0)
                self.probability=math.exp(
                    0.44*math.log(max(c1,1e-6))+
                    0.30*math.log(max(c2,1e-6))+
                    0.20*math.log(max(c3,1e-6))+
                    0.06*math.log(max(c4,1e-6))
                )
                self.probability=max(0.0,min(1.0,self.probability))
            if self.suppress:
                if self.probability < 0.45: self.suppress=False
            elif not self.active:
                if self.probability >= self.activation_threshold:
                    self.active=True; self.event_samples=0
            elif self.probability < RELEASE_THRESHOLD:
                self.active=False
        if self.active:
            self.event_samples+=1
            if self.event_samples > int(round(0.120*self.sr)):
                self.active=False; self.suppress=True
        return self.probability,self.active

def make_detector(threshold:float):
    class Detector(CalibratedDetector):
        activation_threshold=threshold
    return Detector

def summarize(rows,threshold):
    current=[r for r in rows if r["threshold"]==threshold]
    pos=[r for r in current if r["case"] in v1.POSITIVE_CASES]
    neg=[r for r in current if r["case"] in v1.NEGATIVE_CASES]
    positive_fraction=sum(bool(r["detected"]) for r in pos)/len(pos)
    soft_all=all(bool(r["detected"]) for r in pos if r["case"]=="plosive_soft")
    nominal_all=all(bool(r["detected"]) for r in pos if r["case"]=="plosive_nominal")
    strong_all=all(bool(r["detected"]) for r in pos if r["case"]=="plosive_strong")
    repeat_two=all(int(r["event_count"])>=2 for r in pos if r["case"]=="plosive_repeated")
    latency=[float(r["first_onset_latency_ms"]) for r in pos if r["first_onset_latency_ms"] is not None]
    neg_occ=[float(r["active_occupancy_pct"]) for r in neg]
    prob_spreads=[]
    for case in v1.POSITIVE_CASES+v1.NEGATIVE_CASES:
        vals=[float(r["max_probability"]) for r in current if r["case"]==case]
        prob_spreads.append(max(vals)-min(vals))
    max_duration=max(float(r["max_active_duration_ms"]) for r in current)
    # Scale-invariance replay uses the candidate threshold.
    sr=48000
    scales=(10**(-12/20),1.0,10**(12/20))
    scale_prob=0.0; scale_occ=0.0
    for case in ("plosive_nominal","low_vowel","growl"):
        vals=[v1.run_case(case,sr,make_detector(threshold),scale=s) for s in scales]
        pp=[float(x["max_probability"]) for x in vals]
        oo=[float(x["active_occupancy_pct"]) for x in vals]
        scale_prob=max(scale_prob,max(pp)-min(pp))
        scale_occ=max(scale_occ,max(oo)-min(oo))
    base_rows=[]
    for sr0 in v1.SAMPLE_RATES:
        for case in v1.NEGATIVE_CASES:
            base_rows.append(v1.run_case(case,sr0,v1.LfOnsetBaseline))
    base_mean=sum(float(x["active_occupancy_pct"]) for x in base_rows)/len(base_rows)
    neg_mean=sum(neg_occ)/len(neg_occ)
    ratio=neg_mean/base_mean if base_mean>1e-9 else None
    gates={
      "positive_detection_fraction_ge_0_90":positive_fraction>=0.90,
      "soft_detected_all_sr":soft_all,
      "nominal_detected_all_sr":nominal_all,
      "strong_detected_all_sr":strong_all,
      "repeated_two_events_all_sr":repeat_two,
      "positive_onset_latency_le_20ms":bool(latency) and max(latency)<=20.0,
      "negative_occupancy_mean_le_1pct":neg_mean<=1.0,
      "negative_occupancy_max_le_5pct":max(neg_occ)<=5.0,
      "false_occupancy_le_35pct_of_lf_only":ratio is not None and ratio<=0.35,
      "event_duration_le_125ms":max_duration<=125.0,
      "sample_rate_probability_spread_le_0_06":max(prob_spreads)<=0.06,
      "input_scale_probability_spread_le_0_05":scale_prob<=0.05,
      "input_scale_occupancy_spread_le_3pct":scale_occ<=3.0,
    }
    return {
      "threshold":threshold,
      "positive_detection_fraction":positive_fraction,
      "soft_detected_all_sr":soft_all,
      "nominal_detected_all_sr":nominal_all,
      "strong_detected_all_sr":strong_all,
      "repeated_two_events_all_sr":repeat_two,
      "max_positive_onset_latency_ms":max(latency) if latency else None,
      "negative_occupancy_mean_pct":neg_mean,
      "negative_occupancy_max_pct":max(neg_occ),
      "lf_only_negative_occupancy_mean_pct":base_mean,
      "false_occupancy_ratio":ratio,
      "max_probability_sample_rate_spread":max(prob_spreads),
      "max_active_duration_ms":max_duration,
      "max_input_scale_probability_spread":scale_prob,
      "max_input_scale_occupancy_spread_pct":scale_occ,
      "gates":gates,
      "passes":all(gates.values()),
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out-dir",required=True)
    args=ap.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for th in THRESHOLDS:
        cls=make_detector(th)
        for sr in v1.SAMPLE_RATES:
            for case in v1.POSITIVE_CASES+v1.NEGATIVE_CASES:
                m=v1.run_case(case,sr,cls)
                rows.append({"threshold":th,"sample_rate":sr,"case":case,**m})
    summaries=[summarize(rows,th) for th in THRESHOLDS]
    passing=[x for x in summaries if x["passes"]]
    passing.sort(key=lambda x:x["threshold"],reverse=True)
    selected=passing[0] if passing else None
    decision="GO_TO_REAL_VOCAL" if selected and selected["threshold"]<0.75 else "REVISE"
    result={
      "decision":decision,
      "baseline_threshold":0.75,
      "candidate_thresholds":[0.72,0.70],
      "release_threshold":RELEASE_THRESHOLD,
      "summaries":summaries,
      "selected":selected,
      "selection_rule":"highest passing activation threshold",
      "feature_family_changed":False,
      "raw_audio_persisted":False,
    }
    (out/"plosive_r2_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with (out/"plosive_r2_matrix.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["threshold","sample_rate","case","max_probability","active_occupancy_pct","event_count","max_active_duration_ms","first_onset_latency_ms","detected"]
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(rows)
    report=["# Vo.Prep Plosive Guard R2 threshold calibration","",f"Decision: {decision}","",
            "Frozen feature family; only activation threshold varies.","",
            json.dumps(summaries,indent=2)]
    (out/"plosive_r2_report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print((out/"plosive_r2_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
