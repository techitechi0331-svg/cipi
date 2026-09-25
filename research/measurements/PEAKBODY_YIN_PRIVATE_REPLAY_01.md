# PeakBody YIN Private Real-Vocal Replay 01 — Result

Classification: **MEASURED / REJECTED as immediate challenger**  
Raw audio committed: **NO**

## Decision

**REJECT YIN-CMND as the immediate PeakBody periodicity challenger for this private scope.**

This does not reject YIN as a pitch estimator or as a reusable DSP method. It rejects the tested use of raw YIN-CMND confidence as the direct periodicity-protection term in the current PeakBody guard.

## Locked non-regression gates

The replay reused baseline-defined event masks from the prior private study. Candidate output was not allowed to choose its own favorable frames.

Adequate pooled reference counts existed:

- noise-like high-band: **246**
- low-frequency transient: **11,969**
- strong periodic body: **10,612**

The bright-voiced mask remained **0**, so high-register real-vocal safety remains an independent open corpus gap.

## MEASURED

### Noise-like high-band false protection

Median candidate/baseline transient-factor retention:

- current autocorr guard: **0.492622**
- YIN guard: **0.667187**
- YIN minus autocorr: **+0.174565**

Locked YIN qualification gates:

- YIN median <= 0.50: **FAIL**
- YIN no more than +0.02 above autocorr median: **FAIL**

On the same baseline noise-like frames, median confidence was:

- autocorr: **0.228648**
- YIN: **0.406017**

This directly explains the weaker suppression: YIN treated these real vocal frames as substantially more periodic and therefore protected them more strongly.

### Low-frequency transient preservation

- median retention: **1.0**
- p10 retention: **1.0**

PASS.

### Periodic body invariance

Mean absolute YIN-guard versus Revision-02 baseline transient-factor delta:

- **0.0**

PASS.

### Processing-variant stability

Median pairwise guard-output correlation:

- autocorr guard: **0.904205**
- YIN guard: **0.908642**
- difference: **+0.004437**

PASS.

## INFERRED

The synthetic YIN result did not generalize to the real-vocal noise-like proxy in the way PeakBody needs.

YIN's lower operation proxy and accurate diagnostic F0 are real benefits, but they do not compensate for the measured increase in false protection of the current private noise-like event set.

For PeakBody, **accurate pitch estimation is not equivalent to safe voicing confidence**.

## REJECTED

Do not replace the current periodicity guard with raw YIN-CMND confidence using the tested mapping without new evidence or a redesigned confidence calibration.

## Still unresolved

- bright/high-register real-vocal coverage remains absent;
- multi-singer validation remains blocked by corpus access;
- production C++ CPU/block-size behavior remains unmeasured;
- MPM remains a qualified synthetic control and should receive the same private non-regression replay.
