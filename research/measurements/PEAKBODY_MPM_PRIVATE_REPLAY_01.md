# PeakBody MPM Private Real-Vocal Replay 01 — Result

Classification: **MEASURED / REJECTED as immediate challenger**  
Raw audio committed: **NO**

## Decision

**REJECT MPM/NSDF clarity as the immediate PeakBody periodicity challenger for this private scope.**

The tested direct use of MPM clarity as the periodicity-protection term regressed noise-like rejection relative to the current autocorrelation guard.

## Locked reference counts

Candidate-independent baseline masks:

- noise-like high-band: **246**
- low-frequency transient: **11,969**
- strong periodic body: **10,612**
- bright voiced: **0**

The known absence of bright-voiced frames remains a separate high-register corpus gap.

## MEASURED

### Noise-like high-band false protection

Median candidate/baseline transient-factor retention:

- current autocorr guard: **0.492622**
- MPM guard: **0.625372**
- MPM minus autocorr: **+0.132749**

Locked qualification gates:

- MPM median <= 0.50: **FAIL**
- MPM no more than +0.02 above autocorr median: **FAIL**

Median confidence on the same noise-like reference frames:

- autocorr: **0.228648**
- MPM: **0.331997**

MPM therefore protected these frames more strongly than the current autocorrelation guard.

### Low-frequency transient preservation

- median retention: **1.0**
- p10 retention: **1.0**

PASS.

### Periodic body invariance

Mean absolute MPM-guard versus Revision-02 baseline transient-factor delta:

- **0.0**

PASS.

### Processing-variant stability

Median pairwise guard-output correlation:

- autocorr guard: **0.904205**
- MPM guard: **0.908387**
- difference: **+0.004182**

PASS.

## INFERRED

MPM's synthetic confidence separation was not sufficient evidence for direct replacement of the existing autocorrelation periodicity term.

Like YIN, MPM's real-vocal failure mode is not transient/body destruction. It is **excessive protection of frames that the current baseline classifies as noise-like high-band events**.

## REJECTED

Do not replace the current PeakBody periodicity term with raw MPM/NSDF clarity under the tested direct mapping.

## Next design implication

Both qualified synthetic challengers failed the same real-vocal non-regression axis.

The next research direction should therefore stop treating the periodicity estimator itself as the main missing component and instead investigate a **contextual noise-evidence score** where periodicity acts as one protection/veto feature among several.

CIPI's Vo.Prep Sibilance Guard and BreathKeeper research are the strongest existing reusable sources for that next architecture.
