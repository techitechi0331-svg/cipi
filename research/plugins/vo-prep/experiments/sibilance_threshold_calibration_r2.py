#!/usr/bin/env python3
"""Vo.Prep Sibilance Guard R2 bounded activation-threshold calibration.

Research only. Reuses the frozen v1 signal matrix and feature family.
No product DSP mutation and no raw audio.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import sibilance_adversarial_v1 as v1

THRESHOLDS=(0.65,0.62,0.60,0.58)
RELEASE_THRESHOLD=0.45

class CalibratedDetector(v1.ContextDetector):
    activation_threshold=0.65
    def process(self,x:float):
        if not math.isfinite(x): x=0.0
        x=max(-64.0,min(64.0,x))
        high=self.high.process(x); mid=self.mid.process(x); broad=self.broad.process(x); upper=self.upper.process(x)
        hp=high*high; mp=mid*mid; bp=broad*broad; up=upper*upper
        self.high_fast+=self.fast_c*(hp-self.high_fast)
        self.mid_fast+=self.fast_c*(mp-self.mid_fast)
        self.broad_fast+=self.fast_c*(bp-self.broad_fast)
        self.upper_fast+=self.fast_c*(up-self.upper_fast)
        self.high_slow+=self.slow_c*(hp-self.high_slow)
        broad_db=10.0*math.log10(max(self.broad_fast,1e-12))
        if broad_db < -90.0:
            self.active=False; self.suppress=False; self.startup_inhibit=int(round(0.005*self.sr))
        elif self.startup_inhibit>0:
            self.startup_inhibit-=1
        self.divider+=1
        if self.divider>=8:
            self.divider=0
            high_db=10.0*math.log10(max(self.high_fast,1e-12))
            mid_db=10.0*math.log10(max(self.mid_fast,1e-12))
            upper_db=10.0*math.log10(max(self.upper_fast,1e-12))
            high_slow_db=10.0*math.log10(max(self.high_slow,1e-12))
            if broad_db < -90.0:
                self.probability=0.0
            else:
                c1=self.sigmoid(((high_db-broad_db)+4.5)/1.4)
                c2=self.sigmoid(((high_db-mid_db)-2.0)/2.4)
                c3=self.sigmoid(((high_db-high_slow_db)-1.0)/3.0)
                c4=self.sigmoid(((upper_db-high_db)+10.0)/2.5)
                self.probability=math.exp(
                    0.45*math.log(max(c1,1e-6))+
                    0.30*math.log(max(c2,1e-6))+
                    0.10*math.log(max(c3,1e-6))+
                    0.15*math.log(max(c4,1e-6))
                )
                self.probability=max(0.0,min(1.0,self.probability))
            if self.startup_inhibit>0:
                self.active=False
            elif self.suppress:
                if self.probability < 0.35: self.suppress=False
            elif not self.active:
                if self.probability >= self.activation_threshold:
                    self.active=True; self.event_samples=0
            elif self.probability < RELEASE_THRESHOLD:
                self.active=False
        if self.active:
            self.event_samples+=1
            if self.event_samples > int(round(0.350*self.sr)):
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
    all_positive=all(bool(r["detected"]) for r in pos)
    s_sh_all=all(bool(r["detected"]) for r in pos if r["case"] in ("s","sh"))
    latency=[float(r["first_onset_latency_ms"]) for r in pos if r["first_onset_latency_ms"] is not None]
    neg_occ=[float(r["active_occupancy_pct"]) for r in neg]
    prob_spreads=[]
    for case in v1.POSITIVE_CASES+v1.NEGATIVE_CASES:
        vals=[float(r["max_probability"]) for r in current if r["case"]==case]
        prob_spreads.append(max(vals)-min(vals))
    max_duration=max(float(r["max_active_duration_ms"]) for r in current)
    sr=48000; scales=(10**(-12/20),1.0,10**(12/20))
    scale_prob=0.0; scale_occ=0.0
    for case in ("s","bright_vowel","breath"):
        vals=[v1.run_case(case,sr,make_detector(threshold),scale=s) for s in scales]
        pp=[float(x["max_probability"]) for x in vals]; oo=[float(x["active_occupancy_pct"]) for x in vals]
        scale_prob=max(scale_prob,max(pp)-min(pp)); scale_occ=max(scale_occ,max(oo)-min(oo))
    neg_mean=sum(neg_occ)/len(neg_occ)
    gates={
      "positive_detection_fraction_ge_0_99":positive_fraction>=0.99,
      "all_positive_cases_detected_all_sr":all_positive,
      "s_sh_detected_all_sr":s_sh_all,
      "positive_onset_latency_le_30ms":bool(latency) and max(latency)<=30.0,
      "negative_occupancy_mean_le_0_5pct":neg_mean<=0.5,
      "negative_occupancy_max_le_2pct":max(neg_occ)<=2.0,
      "event_duration_le_355ms":max_duration<=355.0,
      "sample_rate_probability_spread_le_0_08":max(prob_spreads)<=0.08,
      "input_scale_probability_spread_le_0_05":scale_prob<=0.05,
      "input_scale_occupancy_spread_le_5pct":scale_occ<=5.0,
    }
    return {
      "threshold":threshold,
      "positive_detection_fraction":positive_fraction,
      "all_positive_cases_detected_all_sr":all_positive,
      "s_sh_detected_all_sr":s_sh_all,
      "max_positive_onset_latency_ms":max(latency) if latency else None,
      "negative_occupancy_mean_pct":neg_mean,
      "negative_occupancy_max_pct":max(neg_occ),
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
    decision="GO_TO_REAL_VOCAL" if selected and selected["threshold"]<0.65 else "REVISE"
    result={
      "decision":decision,
      "baseline_threshold":0.65,
      "candidate_thresholds":[0.62,0.60,0.58],
      "release_threshold":RELEASE_THRESHOLD,
      "summaries":summaries,
      "selected":selected,
      "selection_rule":"highest passing activation threshold",
      "relative_false_occupancy_ratio_removed":True,
      "reason_relative_ratio_removed":"v1 baseline negative occupancy was zero, making the ratio undefined; R2 predeclares absolute occupancy gates instead",
      "feature_family_changed":False,
      "raw_audio_persisted":False,
    }
    (out/"sibilance_r2_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with (out/"sibilance_r2_matrix.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["threshold","sample_rate","case","max_probability","active_occupancy_pct","event_count","max_active_duration_ms","first_onset_latency_ms","detected"]
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(rows)
    report=["# Vo.Prep Sibilance Guard R2 threshold calibration","",f"Decision: {decision}","",
            "Frozen feature family; only activation threshold varies.","",
            "V1 relative false-occupancy ratio is not reused because its denominator was zero. R2 uses absolute negative-occupancy gates predeclared before execution.","",
            json.dumps(summaries,indent=2)]
    (out/"sibilance_r2_report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print((out/"sibilance_r2_report.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
