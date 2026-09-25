# PeakBody Contextual Noise Guard Research 01

Status: **PROTOCOL LOCKED BEFORE MEASUREMENT**

## Research Question

After YIN-CMND and MPM-NSDF both failed private real-vocal noise-like non-regression when used directly as periodicity protection, can PeakBody improve noise-like crest rejection by changing **how periodicity is used** and, only if necessary, adding contextual sibilance evidence?

## Reused CIPI / product evidence

### Current PeakBody evidence

Current guard:

`guardStrength = 0.75 * spectralGuard * (1 - periodicityConfidence)`

Synthetic periodicity protection solved the catastrophic bright-high-F0 failure of spectral-only guarding.

Private same-performance real-vocal evidence then showed:

- current autocorr guard noise-like median retention: ~0.493;
- low-frequency transient median/p10 retention: 1.0/1.0;
- body delta: 0.0;
- processing-variant correlation median: ~0.904;
- bright-voiced private reference count: 0.

YIN and MPM direct-confidence replacements were rejected because both increased false protection on the same 246 baseline-defined noise-like frames.

### Vo.Prep Sibilance Guard v2.3 evidence

Repository-verified detector:

- high: 4–12 kHz;
- mid reference: 1–4 kHz;
- broad reference: 250 Hz–12 kHz;
- upper-high: 7–12 kHz;
- fast power envelope: 8 ms;
- high local reference: 120 ms;
- feature geometric weights:
  - HF/Broad 0.45
  - HF/Mid 0.30
  - high onset 0.10
  - upper/high 0.15
- activation 0.65 / release 0.45 in the product event detector.

The continuous probability is:

`P_sib = exp(0.45 ln(c1) + 0.30 ln(c2) + 0.10 ln(c3) + 0.15 ln(c4))`

with product sigmoid mappings retained from the verified Vo.Prep implementation.

Measured Vo.Prep corpus evidence reported ~64% recall against a conservative FFT-derived high-confidence reference and ~0.02% false-trigger rate against clearly low-confidence frames.

This is reusable evidence, not proof that the same probability is optimal for PeakBody.

## Design hypothesis

The current private failure may be caused less by the periodicity estimator family than by using **weak periodicity continuously as proportional protection**.

Low periodicity values such as 0.2–0.4 still reduce guard action under `(1-p)`, even though they may not be strong evidence of voiced harmonic structure.

PeakBody should test periodicity as a **strong-voicing veto** rather than a continuously proportional discount.

## Baseline

Current guard:

`G0 = 0.75 * S * (1 - P)`

where:

- `S` = existing PeakBody normalized high-band spectral guard;
- `P` = current normalized-autocorrelation periodicity confidence.

Candidate transient factor:

`T0 = T * (1 - G0)`

## Simple Candidate A — Strong-Periodicity Veto

No new detector family.

Define:

`u = clamp((P - 0.55) / 0.25, 0, 1)`

`V = u*u*(3 - 2*u)`

Then:

`GA = 0.75 * S * (1 - V)`

`TA = T * (1 - GA)`

Interpretation:

- P <= 0.55: no voiced protection;
- 0.55 < P < 0.80: smooth transition;
- P >= 0.80: full voiced protection.

This is the mandatory Simple Baseline challenger.

## Context Candidate B — Vo.Prep Context + Strong-Periodicity Veto

Reuse the verified continuous Vo.Prep v2.3 contextual sibilance probability `P_sib`.

Define contextual noise evidence:

`N = max(S, P_sib)`

Then:

`GB = 0.75 * N * (1 - V)`

`TB = T * (1 - GB)`

No Vo.Prep event hysteresis or attenuation topology is imported at this stage. Only the **detector probability** is tested as evidence.

## Why max() first

The complex candidate must not become weaker than the existing spectral evidence solely because the Vo.Prep detector intentionally under-detects breath-like material.

`max(S, P_sib)` makes contextual probability an additional noise-evidence source, not a replacement.

## Synthetic matrix

Use the established PeakBody confounder cases:

- voiced low;
- voiced high;
- bright high-F0 harmonic transient;
- sibilant;
- breath-like noise;
- steady vowel;
- low-frequency plosive-like transient.

Add:

- noisy bright voiced harmonic at 6 dB SNR;
- long S-like event;
- startup bright vowel after silence.

Sample rates:

- 44.1 / 48 / 96 / 192 kHz where the analysis model supports them.

## Private real-vocal replay

Use the same four private processing variants and the same **candidate-independent baseline masks** already used for YIN/MPM replay:

- noise-like high-band: 246 pooled reference frames in prior run;
- low-frequency transient: 11,969;
- periodic body: 10,612;
- bright voiced: 0 (open coverage gap).

No candidate may choose its own favorable mask.

## Metrics

For Baseline / A / B:

- noise-like retention median/p10/p90;
- low-frequency transient median/p10 retention;
- periodic-body mean absolute delta;
- processing-variant pairwise correlation median;
- synthetic bright-high retention minimum;
- synthetic noisy-voiced retention;
- synthetic sibilant/breath false-preservation maximum;
- synthetic plosive retention minimum;
- finite values.

For B additionally:

- contextual probability distribution by synthetic class;
- contextual probability on private baseline-defined noise-like mask;
- incremental improvement of B over A.

## Acceptance — Simple Candidate A

A qualifies for next product research only if:

- private noise-like median retention <= **0.35**;
- private low-frequency median >= **0.90**;
- private low-frequency p10 >= **0.80**;
- private body mean absolute delta <= **0.03**;
- private pairwise correlation median >= **0.80**;
- correlation drop vs current baseline <= **0.05**;
- synthetic bright-high retention >= **0.95**;
- synthetic noisy-voiced retention >= **0.90**;
- synthetic plosive retention >= **0.85**;
- synthetic sibilant/breath false-preservation <= **0.25**;
- all values finite.

## Acceptance — Context Candidate B

B must satisfy every A safety gate.

Complexity is justified only if at least one holds **without worsening another hard gate**:

- private noise-like median retention improves by >= **0.03 absolute** versus A;
- synthetic noise-like false-preservation improves by >= **0.03 absolute** versus A;
- B preserves a class that A fails while B passes all hard gates.

If A passes and B does not clear the complexity-improvement rule, prefer A.

## Rejection rules

- If A harms bright/noisy voiced or plosive preservation, reject the veto mapping.
- If B causes additional false suppression or fails to improve meaningfully over passing A, reject contextual complexity for this revision.
- Preserve every Negative Result.

## Known limitation

The private corpus still contains zero bright-voiced reference frames. Synthetic bright-high preservation remains mandatory, but broader annotated multi-singer/high-register validation remains an open gate before product promotion.

## No-tuning rule

The 0.55/0.80 veto transition, 0.75 guard ceiling, Vo.Prep probability formula and all acceptance thresholds are locked before measurement.

Do not change them after seeing this experiment.
