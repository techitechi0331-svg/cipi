# Vocal Resonance MODULE 1 v0.4R.5 Temporal Morphology Review

Date: 2026-09-25

Source:
`research/runs/VOCAL-RESONANCE-R5-TEMPORAL-MORPH-001/gha-36078101620-1/`

## Verdict

**KEEP FOR FALSIFICATION / ITERATE.**

R5 materially improved measured clean-vocal abstention, but it did **not** improve semantic target ranking and is not ready for numeric lock or product implementation.

## MEASURED

Locked test:
- static R2 Top-5: **25.0%**
- temporal morphology Top-5: **25.0%**
- static strong-effect Top-5: **33.33%**
- temporal morphology strong-effect Top-5: **33.33%**
- static Top-3: **12.5%**
- morphology Top-3: **9.375%**
- static MRR: **0.17149**
- morphology MRR: **0.16214**
- static internal-clean false trigger: **37.5%**
- morphology internal-clean false trigger: **12.5%**

External clean cohort reported by R5:
- static false trigger: **17.5%**
- morphology false trigger: **0.0%**
- n = **40**

The predeclared R5 retention gate passed.
The product gate failed.

## INFERRED

Generic temporal morphology may contain useful **abstention/context** information. The current evidence does not demonstrate improved resonance ranking.

## HYPOTHESIS

The clean-false reduction is caused by temporal morphology itself rather than:
- a different selected regularization C;
- validation-threshold/calibration interaction;
- accidental source overlap between the ranker corpus and external-clean cohort;
- one injection random seed;
- one specific morphology subfamily.

## REJECTED / NOT SUPPORTED

- “R5 improves semantic ranking” — not supported; Top-5 was unchanged and Top-3/MRR were slightly worse.
- “R5 passes the product semantic-ranker gate” — rejected.
- “0% external-clean false trigger is already production-safe” — rejected; independence and stability are not yet closed.

## Mandatory next gate

**MODULE 1 v0.4R.5b — Morphology Stability / Ablation / Leakage Audit**

Required:
1. zero source-basename overlap between ranker sources and the external-clean cohort;
2. two controlled injection seeds;
3. static / run-length-only / distribution-only / full morphology ablation;
4. full morphology trained with the exact C selected by the static model;
5. paired external-clean false-trigger comparison with bootstrap interval;
6. no Top-5 or strong-effect regression on either seed.

No production suppressor, numeric lock, VST3, confidence promotion, or current-stage promotion is authorized.
