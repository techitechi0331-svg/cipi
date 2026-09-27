# VoPriPro AMOUNT Real-Vocal Sweep v1 Protocol

Date: 2026-09-27
Status: LOCKED BEFORE EXECUTION
Product mutation: none
Protected DSP baseline: `techitechi0331-svg/VocalPrepComp@cc796d30d7e1885e0ca66caaf7f1b02d0bffeb33`

## Question

How does the current protected VoPriPro AMOUNT map behave across its published anchors on the same real-vocal material, before any alternative mapping is proposed?

This study quantifies control travel. It does not attempt to prove perceptual optimality.

## Corpus

Reuse the already accepted VoPriPro HUST_Solfege validation snapshot:

- man1_twinkle.wav
- man4_twinkle.wav
- woman1_twinkle.wav
- woman3_twinkle.wav

No new singer/generalisation claim is permitted from this four-recording snapshot.

## Frozen settings

For the AMOUNT sweep:

- Character: 50% Natural
- Input: 0 dB
- Output: 0 dB
- AMOUNT: 0%, 10%, 25%, 40%, 50%, 60%, 75%, 90%, 100%
- existing DC block, detector, knee, sidechain HPF and limiter remain unchanged
- process block size follows the existing real-vocal validator

Existing Amount50 Smooth/Punch and Drive+6 cases may remain in the validator for regression continuity, but they are not part of the AMOUNT-sweep decision.

## Required derived metrics

Per file and AMOUNT:

- input and output peak / RMS / crest;
- input and output 100 ms active-window P90-P10 dynamics;
- compressor block-max GR p50;
- compressor block-max GR p95;
- compressor block-max GR maximum;
- limiter p95 and maximum;
- finite-output / sample-peak safety status.

No new listening claim may be inferred from these metrics.

## Predeclared hard gates

### Safety

For every AMOUNT/file row:

- output must remain finite;
- output must remain inside the existing -1.0 dBFS sample-peak safety ceiling using the validator's existing numerical tolerance.

Any violation is **REJECT_OR_REVISE** for the tested baseline/validator path and must be investigated before control-travel interpretation.

### Monotonic compression ordering

For each file independently, across Natural AMOUNT anchors in ascending order:

- GR p50 must not decrease by more than 0.05 dB between adjacent anchors;
- GR p95 must not decrease by more than 0.05 dB between adjacent anchors;
- GR max must not decrease by more than 0.05 dB between adjacent anchors.

A larger reversal is a **REVIEW_MAPPING_OR_MEASUREMENT** signal.

These gates test ordered control behavior only. They do not require equal-sized steps.

## Diagnostic-only analyses

The following are measured but deliberately not assigned product-adoption thresholds in v1:

- adjacent GR step size;
- 90% -> 100% incremental GR;
- dynamic P90-P10 reduction by AMOUNT;
- crest-factor change by AMOUNT;
- limiter engagement by AMOUNT;
- between-singer spread of each AMOUNT effect.

Reason: setting a perceptual-uniformity threshold before real listening evidence would be arbitrary.

## Decisions

- **KEEP_BASELINE_FOR_LISTENING**: all hard safety and monotonic-ordering gates pass.
- **REVIEW_MAPPING_OR_MEASUREMENT**: an ordering gate fails.
- **REJECT_OR_REVISE**: a hard safety gate fails.
- **BLOCKED_EXTERNAL**: the established corpus/runner path cannot execute.

A KEEP result only allows the protected map to advance to level-matched AMOUNT listening. It does not establish that 50% is universally optimal or that knob travel is perceptually uniform.

## Holdout discipline

No alternative AMOUNT mapping is designed or tuned from this v1 result.

If v1 exposes a meaningful control-travel hypothesis, a separate candidate must be declared and evaluated without retuning against the final listening holdout.

## Precision boundary

This is real-vocal engineering evidence on four HUST_Solfege adult recordings. It is not:

- a universal singer result;
- a genre result;
- a microphone result;
- a human naturalness result;
- a Cubase result;
- an authorization to mutate product DSP.
