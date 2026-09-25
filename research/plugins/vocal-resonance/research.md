# Vocal Resonance Suppressor Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/Vocal_resonance
- This formal track preserves the strongest available evidence without promoting undocumented product claims.

## Purpose
Falsification-first vocal resonance detection before any suppressor VST3 is allowed.

## Evidence carried forward

Candidate discovery has now passed its real-vocal budget gate for the current research scaffold.

Primary real-vocal gate:
- 20 identifiable VocalSet singers;
- 40 excerpts;
- four controlled injections per excerpt;
- 160 paired cases;
- Merge-20 recall: 87.50%;
- Merge-15 recall: 76.25%.

Independent confirmation cohort:
- different excerpt rows per singer;
- new injection seed;
- 20 singers / 40 excerpts / 160 paired cases;
- Merge-20 recall: 86.875%;
- Merge-15 recall: 78.125%;
- paired K20-K15 difference: +8.75 percentage points;
- bootstrap 95% interval: approximately +4.38 to +13.13 points;
- 14 improvements / 0 losses.

## Confirmed-for-scope knowledge

- Candidate budget **K=20** is locked for the current candidate-discovery scaffold.
- K=15 is rejected for this scope.
- Real-vocal controlled injection is practical and repeatable in CI without redistributing source audio.
- Observability-aware evaluation remains required; inserted EQ gain is not equivalent to measured spectral effect.

## Still provisional

The merged local + log/ERB proposal architecture is retained as a research scaffold, but its superiority over Local-20 is **not confirmed**.

On the independent confirmation cohort:
- Merge-20: 86.875%
- Local-20: 82.50%
- paired interval for the difference still crosses zero.

Do not convert this directional result into a universal architecture claim.

## Current unresolved problem

**Semantic ranking.**

Candidate discovery can propose useful locations, but the system has not yet proven that it can separate unwanted resonant emphasis from legitimate:
- harmonics;
- formants / singer's-formant structure;
- sibilance/fricatives;
- breath/noise;
- transient consonants;
- high-F0 sparse-harmonic cases.

## Reusable knowledge target

Observability-aware spectral candidate generation, hard sparse candidate budgets, high-F0/formant ambiguity handling, candidate-level semantic ranking, and adversarial real-vocal evaluation.

## Next formal gate

**MODULE 1 v0.4 — Semantic Ranker research and measurement.**

Start with interpretable deterministic / logistic-style candidate scoring. Require clean hard negatives and singer/excerpt-separated validation before any suppressor gain/filter design.

## Promotion rule

Do not mark the overall product track `CONFIRMED` until semantic ranking, suppression DSP, measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.

---

# Evidence reconciliation — 2026-09-25

The original independent-confirmation paragraph above is preserved as history. It describes the preliminary `skip_per_singer=2` confirmation run.

A later and stricter confirmation run explicitly excluded all 40 primary examples.

## Strict explicit-exclusion confirmation

Target Actions run: `36052307694`

- Merge-20: **85.00%**
- Merge-15: **74.375%**
- Local-20: **85.00%**
- paired Merge-20 minus Merge-15: **+10.625 points**
- bootstrap 95% interval: **+6.25 to +15.625 points**
- discordant wins/losses: **17 / 0**
- Merge-20 minus Local-20: **0 points**
- paired interval: **-5.625 to +5.625 points**

Decision:
- keep K=20 locked for the current candidate-discovery scaffold;
- keep K=15 rejected;
- do **not** claim Merge-20 is superior to Local-20;
- prefer the strict explicit-exclusion numbers in future summaries while retaining the earlier preliminary cohort.

## Semantic Ranker v0.4

Measured:
- Top-5: 34.375%
- strong-effect Top-5: 53.846%
- clean false trigger: 25.0%
- gate: NO_GO

## Semantic Ranker v0.4R.1 — pairwise case-relative

Measured:
- Top-5: 31.25%
- strong-effect Top-5: 46.154%
- clean false trigger: 37.5%

Decision: **REJECTED** for this scope.

## Semantic Ranker v0.4R.2 — causal safe-negative supervision

Measured:
- generator ceiling: 87.5%
- Top-5: 46.875%
- Top-5 given generator hit: 53.571%
- prominence baseline Top-5: 37.5%
- strong-effect Top-5: 46.154%
- clean false trigger: 37.5%
- gate: NO_GO

Interpretation:
- safer labels improved overall Top-5;
- strong-effect ranking and clean false-trigger behavior remain inadequate;
- model complexity should not be increased blindly;
- the next falsifiable question is whether F0/harmonic motion coherence adds useful protection/context.

## Next formal gate

**MODULE 1 v0.4R.3 — F0 / Harmonic Motion Coherence.**

Research must compare against:
1. v0.4R.2 safe-negative static ranker;
2. simple local-prominence baseline.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.3 Review — Motion Coherence

Autonomous run `VOCAL-RESONANCE-R3-MOTION-001 / gha-36069680311-1` completed under the CIPI free worker.

Measured locked-test result:
- static R2-style Top-5: 40.625%;
- motion R3 Top-5: 31.25%;
- static strong-effect Top-5: 60.0%;
- motion strong-effect Top-5: 53.33%;
- clean false-trigger: 25.0% for both;
- retention gate: **REJECTED**;
- product gate: **FAILED**.

The tested F0/harmonic-motion feature bundle is rejected for this scope.

Important caveat:
- the run contained zero test cases under the predeclared median-F0 >=500 Hz high-F0 definition, so high-F0 behavior remains unresolved.

## Next formal gate

**MODULE 1 v0.4R.4 — Adversarial Clean-Negative / Pitch-Coverage Audit.**

Do not add another model family until false-trigger subgroups and pitch coverage are measured on a broader disjoint clean cohort.


---

# MODULE 1 v0.4R.4 Clean-Negative Audit — assistant review

Run: `VOCAL-RESONANCE-R4-CLEAN-AUDIT-001 / gha-36070450907-1`

Measured:
- 32 clean excerpts / 4 test singers / 5 techniques;
- overall clean false-trigger: **31.25%**;
- belt 0%, breathy 25%, fast_forte 37.5%, fast_piano 62.5%, lip_trill 0%;
- singer range: 0% to 62.5%.

Review:
- subgroup concentration is retained as cohort-level evidence;
- the earlier lip-trill-specific clue is **REJECTED** because it did not reproduce;
- high-F0 coverage is **UNRESOLVED** because the legacy ACF proxy frequently saturates at its 1000 Hz search boundary;
- all Audit-001 excerpts were arpeggios, so exercise-family confounding remains.

Next:
**MODULE 1 v0.4R.4b — Independent Clean-Negative Re-audit.**

No new semantic model family is authorized before that replication.


---

# MODULE 1 v0.4R.4b Independent Clean-Negative Re-audit

Run: `VOCAL-RESONANCE-R4-CLEAN-REAUDIT-002 / gha-36072656461-2`

Measured:
- 40 clean excerpts / 4 singers / 9 techniques / 3 exercise families;
- zero basename overlap with Audit-001;
- overall clean false-trigger: 20.0%;
- fast_piano + fast_forte: 25.0%;
- other techniques: 18.75%;
- fast-minus-other: +6.25 points;
- YIN p90 >=400 Hz: 16 cases with 12.5% false-trigger.

Review:
- Audit-001 fast-technique concentration **did not replicate**;
- high pitch was not the dominant false-trigger subgroup;
- technique-specific and high-pitch-specific protection are not authorized;
- legacy ACF upper-quantile saturation remains unsuitable as high-pitch ground truth.

## Next formal gate

**MODULE 1 v0.4R.5 — Generic Temporal Morphology.**

Test technique-independent candidate run-length / fragmentation evidence against the unchanged static R2-style ranker and simple prominence baseline.


---

# MODULE 1 v0.4R.5 — Generic Temporal Morphology

Run: `VOCAL-RESONANCE-R5-TEMPORAL-MORPH-001 / gha-36078101620-1`

Measured:
- static R2 Top-5: 25.0%;
- morphology Top-5: 25.0%;
- static strong-effect Top-5: 33.33%;
- morphology strong-effect Top-5: 33.33%;
- static internal clean false-trigger: 37.5%;
- morphology internal clean false-trigger: 12.5%;
- static external-clean false-trigger: 17.5%;
- morphology external-clean false-trigger: 0.0% (n=40);
- morphology Top-3/MRR were slightly lower than static;
- retention gate passed; product gate failed.

Assistant review:
- **KEEP FOR FALSIFICATION / ITERATE**;
- morphology is currently an abstention/context candidate, not a demonstrated ranking improvement;
- the 0% external result is not promoted until source overlap, seed stability, same-C control and feature-family ablation are checked.

Next:
**MODULE 1 v0.4R.5b — Morphology Stability / Ablation / Leakage Audit.**


---

# MODULE 1 v0.4R.5b — Morphology Stability / Ablation Review

Run: `VOCAL-RESONANCE-R5B-MORPH-STABILITY-001 / gha-36080499046-1`

## MEASURED

Zero source overlap was verified for both tested seeds.

Seed 20261003:
- static Top-5: 25.0%
- full morphology Top-5: 25.0%
- static strong-effect Top-5: 33.33%
- full morphology strong-effect Top-5: 33.33%
- static external clean false-trigger: 17.5%
- full morphology: 0.0%
- same-C morphology: 2.5%

Seed 20261013:
- static Top-5: 34.375%
- full morphology Top-5: 31.25%
- static strong-effect Top-5: 28.57%
- full morphology strong-effect Top-5: 35.71%
- static external clean false-trigger: 25.0%
- full morphology: 20.0%
- same-C morphology: 20.0%

Ablation:
- run-only morphology reduced external clean false triggers in both seeds:
  - 17.5% -> 2.5%
  - 25.0% -> 17.5%
- but run-only Top-5 regressed on seed 20261013:
  - 34.375% -> 28.125%
- distribution-only morphology was unstable and is not retained.

## DECISION

**REJECT the full R5 Temporal Morphology bundle as a ranker feature family.**

Run-length morphology is **not accepted as a ranker feature**, but remains a bounded hypothesis for a separate post-ranker abstention/veto stage.

## Next formal gate

**MODULE 1 v0.4R.6 — Run-Length Veto / Abstention Gate.**

The veto must leave candidate scores/order unchanged and only decide whether a top-ranked candidate is safe enough to act on.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.6 — Run-Length Veto Review

Run: `VOCAL-RESONANCE-R6-RUN-VETO-001 / gha-36142911813-1`

## MEASURED

Seed 20261003:
- static external-clean false-trigger: 17.5%
- veto external-clean false-trigger: 15.0%
- improvement: 2.5 points
- predeclared minimum improvement: 5 points
- source overlap: 0
- ranking order unchanged: yes
- baseline target actions: 1
- veto target actions: 1
- baseline strong-effect actions: 0

Seed 20261013:
- static external-clean false-trigger: 25.0%
- veto external-clean false-trigger: 0.0%
- improvement: 25 points
- source overlap: 0
- ranking order unchanged: yes
- baseline target actions: 0
- baseline strong-effect actions: 0

## DECISION

**REJECT the tested run-length post-ranker veto as a validated research candidate.**

The predeclared two-seed gate failed because seed 20261003 improved external clean false-trigger by only 2.5 points.

## Measurement limitation discovered

The true-target retention test was not informative:
- seed 20261003 had only one baseline target action;
- seed 20261013 had zero baseline target actions;
- both seeds had zero strong-effect baseline target actions.

Therefore the reported 100% target/strong retention is largely vacuous and must not be promoted as protection evidence.

This is a major measurement warning:
the current static actuation threshold is too sparse for a useful veto-safety study.

## INFERRED

Further veto tuning is premature while semantic ranking and actuation remain weak.

The next research should answer a more fundamental question:
**does the current candidate representation contain enough information to identify the causal injected target when candidate discovery succeeds?**

## Next formal gate

**MODULE 1 v0.4R.7 — Identifiability / Causal Oracle Audit.**

Compare:
1. current single-view static inference features;
2. a research-only paired clean/injected delta oracle unavailable to the final plugin;
3. simple local-prominence baseline.

Required outputs:
- Top-1 / Top-3 / Top-5 conditional on generator hit;
- strong-effect conditional ranking;
- candidate alignment failure rate;
- oracle-vs-single-view gap;
- feature-family separability diagnostics.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.7 — Identifiability / Causal Oracle Review

Run: `VOCAL-RESONANCE-R7-IDENTIFIABILITY-001 / gha-36145023810-1`

## MEASURED

Seed 20261003:
- generator ceiling: 93.75%
- static conditional Top-5: 26.67%
- static strong-effect conditional Top-5: 36.36%
- oracle conditional Top-5: 100.0%
- oracle strong-effect conditional Top-5: 100.0%

Seed 20261013:
- generator ceiling: 84.375%
- static conditional Top-5: 40.74%
- static strong-effect conditional Top-5: 28.57%
- oracle conditional Top-5: 92.59%
- oracle strong-effect conditional Top-5: 100.0%

Causal-delta diagnostics:
- target median absolute local-score delta: 0.2197 / 0.2491
- safe-negative median absolute local-score delta: 0.0030 / 0.0024
- target new-candidate fraction: 33.33% / 29.63%
- safe-negative new-candidate fraction: 0% / 0%

## DECISION

Diagnostic route:
**SINGLE_VIEW_FEATURE_INFORMATION_GAP**

Candidate discovery is not the primary blocker for the covered cases. When a research-only paired clean reference is available, candidate ranking becomes near-ceiling conditional on generator hit.

The current production-feasible single-view feature set does not recover enough of that information.

## Important scope limit

The paired clean/injected oracle is research-only and cannot be deployed in the final plugin.

## Next formal gate

**MODULE 1 v0.4R.8 — Single-View Causal Proxy / Local Patch Context.**

Test bounded deployable feature families such as:
- local 2D spectro-temporal patch contrast;
- multi-scale spectral curvature;
- shoulder/asymmetry shape;
- candidate-vs-broad-envelope residual at several bandwidths;
- local temporal stationarity/covariance;
- within-excerpt contextual percentiles.

Requirements:
- no clean reference at inference;
- compare against frozen static R2 baseline;
- quantify gap to the R7 oracle ceiling;
- use both predeclared seeds;
- preserve external clean-negative evaluation;
- do not promote seed-specific gains.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.8 — Local Patch Proxy Review

Run: `VOCAL-RESONANCE-R8-LOCAL-PATCH-001 / gha-36155951333-1`

## MEASURED

Seed 20261003:
- static conditional Top-5: 26.67%
- local-patch conditional Top-5: 26.67%
- oracle conditional Top-5: 100.0%
- oracle-gap closure: 0%
- static strong-effect conditional Top-5: 36.36%
- local-patch strong-effect conditional Top-5: 45.45%
- external clean false-trigger: 17.5% -> 32.5%

Seed 20261013:
- static conditional Top-5: 40.74%
- local-patch conditional Top-5: 37.04%
- oracle conditional Top-5: 92.59%
- oracle-gap closure: -7.14%
- static strong-effect conditional Top-5: 28.57%
- local-patch strong-effect conditional Top-5: 28.57%
- external clean false-trigger: 25.0% -> 42.5%

## DECISION

**REJECT the tested single-view local patch / multi-scale curvature feature bundle.**

Reasons:
- no conditional Top-5 improvement on either seed;
- no meaningful R7 oracle-gap closure;
- one seed regressed ranking;
- independent clean-vocal false triggers materially worsened on both seeds.

## INFERRED

Static local narrowness/curvature/shoulder geometry is not enough to distinguish injected fixed resonance from legitimate narrow vocal structure and may actively overfit natural harmonics/formants.

The next proxy should use a different information axis rather than more local patch detail.

## Next formal gate

**MODULE 1 v0.4R.9 — Fixed-Hz Temporal Transfer Consistency.**

Research question:
Does a fixed resonance create a time-consistent relative-gain signature between a candidate frequency and its neighboring spectral context that natural moving vocal structure does not?

Candidate deployable features:
- center-vs-shoulder relative level over time;
- median relative gain and MAD;
- positive-support fraction;
- temporal sign consistency;
- center-vs-neighborhood regression residual bias;
- residual variance / robust SNR;
- correlation of candidate energy with broader local energy.

Requirements:
- no clean reference at inference;
- candidate ordering baseline remains frozen;
- two predeclared seeds;
- compare against static R2 baseline and R7 oracle ceiling;
- preserve external clean-negative evaluation;
- reject seed-specific gains.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.9 — Fixed-Hz Transfer Consistency Review

Run: `VOCAL-RESONANCE-R9-TRANSFER-CONSISTENCY-001 / gha-36172028692-1`

## MEASURED

Seed 20261003:
- static conditional Top-5: 26.67%
- transfer conditional Top-5: 33.33%
- oracle-gap closure: 9.09%
- static strong-effect conditional Top-5: 36.36%
- transfer strong-effect conditional Top-5: 18.18%
- external clean false-trigger: 17.5% -> 30.0%

Seed 20261013:
- static conditional Top-5: 40.74%
- transfer conditional Top-5: 48.15%
- oracle-gap closure: 14.29%
- static strong-effect conditional Top-5: 28.57%
- transfer strong-effect conditional Top-5: 42.86%
- external clean false-trigger: 25.0% -> 15.0%

## DECISION

**REJECT the tested fixed-Hz temporal transfer-consistency feature family.**

Reasons:
- neither seed reached the predeclared +0.08 conditional Top-5 improvement;
- neither seed reached 15% R7-oracle-gap closure;
- seed 20261003 materially regressed strong-effect ranking and clean false-trigger performance;
- behavior was not stable across seeds.

## INFERRED

The remaining information gap is unlikely to be solved by adding more within-excerpt local geometry or simple fixed-Hz stationarity alone.

A new information source is required.

## Next formal gate

**MODULE 1 v0.4R.10 — Singer-Disjoint Clean Normative Prior.**

Research question:
Can a lightweight prior learned only from clean training singers provide a deployable estimate of how unusual a candidate is relative to ordinary vocal spectral structure?

Constraints:
- final inference uses only current audio + a frozen trained prior;
- no paired clean reference;
- no deep model required;
- singer-disjoint training/validation/test;
- compare against frozen static R2;
- compare gap closure against R7 oracle;
- preserve independent clean-negative evaluation;
- reject seed-specific gains.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.10 — Clean Normative Prior Review

Run: `VOCAL-RESONANCE-R10-CLEAN-PRIOR-001 / gha-36177223221-1`

## MEASURED

### Seed 20261003
Frozen static:
- conditional Top-5: 26.67%
- strong-effect conditional Top-5: 36.36%
- external clean false-trigger: 17.5%

Static + clean normative prior:
- conditional Top-5: 26.67%
- strong-effect conditional Top-5: 36.36%
- external clean false-trigger: 22.5%
- R7 oracle-gap closure: 0%

Prior-only:
- conditional Top-5: 36.67%
- external clean false-trigger: 50.0%

### Seed 20261013
Frozen static:
- conditional Top-5: 40.74%
- strong-effect conditional Top-5: 28.57%
- external clean false-trigger: 25.0%

Static + clean normative prior:
- conditional Top-5: 44.44%
- strong-effect conditional Top-5: 42.86%
- external clean false-trigger: 32.5%
- R7 oracle-gap closure: 7.14%

Prior-only:
- conditional Top-5: 33.33%
- external clean false-trigger: 50.0%

The prior was correctly fit only on the predeclared training singers and each of the eight frequency bins had roughly 57–62 clean candidate rows.

## DECISION

**REJECT the tested singer-disjoint clean normative prior as a deployable feature family.**

Reason:
- conditional Top-5 improvement missed the predeclared +0.08 criterion on both seeds;
- oracle-gap closure missed 15% on both seeds;
- external clean false-trigger worsened on both seeds.

The result does not support a simple population-level notion of “unusual vocal resonance” for this task.

## Next formal gate

**MODULE 1 v0.4R.11 — Self-Counterfactual Spectral Inpainting Proxy.**

Instead of comparing to another singer or to raw local patch geometry, construct a pseudo-clean reference from the *same observation*:

1. remove a narrow candidate band from the STFT magnitude;
2. reconstruct that band from robust left/right spectral context;
3. recompute candidate evidence on the inpainted counterfactual;
4. use observed-minus-counterfactual deltas as deployable single-view proxy features.

This directly targets the type of difference that made the R7 paired clean/injected oracle strong, while requiring no real clean reference at inference.

Requirements:
- no paired clean reference in model features;
- compare against the frozen static R2 ranker;
- two predeclared seeds;
- report R7 oracle-gap closure;
- preserve independent clean-negative evaluation;
- include a simple shoulder/interpolation-only baseline;
- reject seed-specific gains.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.11 — Self-Counterfactual Inpainting Review

Run: `VOCAL-RESONANCE-R11-SELF-COUNTERFACTUAL-001 / gha-36179619006-1`

## MEASURED

### Seed 20261003
Frozen static:
- conditional Top-5: 26.67%
- strong-effect conditional Top-5: 36.36%
- external clean false-trigger: 17.5%

Static + self-counterfactual:
- conditional Top-5: 26.67%
- strong-effect conditional Top-5: 27.27%
- external clean false-trigger: 30.0%
- R7 oracle-gap closure: 0%

Simple inpaint delta:
- conditional Top-5: 23.33%
- strong-effect conditional Top-5: 18.18%
- external clean false-trigger: 20.0%

### Seed 20261013
Frozen static:
- conditional Top-5: 40.74%
- strong-effect conditional Top-5: 28.57%
- external clean false-trigger: 25.0%

Static + self-counterfactual:
- conditional Top-5: 37.04%
- strong-effect conditional Top-5: 28.57%
- external clean false-trigger: 37.5%
- R7 oracle-gap closure: -7.14%

Simple inpaint delta:
- conditional Top-5: 37.04%
- strong-effect conditional Top-5: 35.71%
- external clean false-trigger: 20.0%

### Proxy-vs-oracle diagnostics

Best observed correlations with absolute R7 true local-score delta were weak:
- cf_delta_local_s4: about 0.20
- cf_delta_local_s8: about 0.20–0.21
- raw-boost proxies: about -0.10 to +0.18
- log-delta proxies: about -0.08 to -0.09

## DECISION

**REJECT the tested same-observation spectral-inpainting feature family.**

It failed ranking, strong-effect, oracle-gap and clean-negative requirements.

The result is also diagnostic:
the hand-crafted counterfactual summary only weakly correlates with the R7 paired causal delta.

## Research route update

R8 through R11 have now tested four different hand-crafted deployable single-view information sources:
1. local 2D patch summaries;
2. fixed-Hz transfer consistency;
3. singer-disjoint population normality;
4. same-observation spectral inpainting.

None closed the R7 information gap robustly.

Before inventing another summary feature, test whether the *raw candidate-aligned local spectro-temporal field* contains separability that these summaries discard.

## Next formal gate

**MODULE 1 v0.4R.12 — Raw 2D Patch Sufficiency Audit.**

Use a fixed-size, candidate-centered, loudness-normalized local-residual patch available from the current observation only.

Compare:
- frozen static R2 baseline;
- raw-patch linear/logistic model;
- static + raw-patch linear model;
- tiny shallow nonlinear patch model as a diagnostic upper bound only.

Required:
- singer-disjoint split;
- both predeclared seeds;
- independent external-clean false-trigger;
- R7 oracle-gap closure;
- no raw patch persistence in GitHub artifacts;
- no deep/model-complexity product claim from a diagnostic pass.

No production suppressor or VST3 is authorized.
