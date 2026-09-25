# PeakBody MPM Private Real-Vocal Replay 01

Status: **PROTOCOL LOCKED BEFORE MEASUREMENT**

## Research Question

Does MPM/NSDF clarity preserve the current autocorrelation guard's real-vocal noise rejection, transient preservation, body invariance and processing-variant stability when used as the direct periodicity-protection term?

## Motivation

MPM qualified in the synthetic realtime-periodicity benchmark and had confidence behavior almost identical to the normalized-autocorrelation baseline.

Because YIN failed the private noise-like non-regression replay, MPM is now tested as the remaining qualified synthetic challenger/control.

## Private source scope

Use the same four SHA-256-bound private processing variants and the same baseline-defined event masks used by the prior private studies.

No raw audio may enter GitHub.

## Baseline

Current autocorrelation guard:

`candidate_auto = t * (1 - 0.75 * spectral_guard * (1 - autocorr_confidence))`

## Challenger

MPM/NSDF guard:

`candidate_mpm = t * (1 - 0.75 * spectral_guard * (1 - mpm_clarity))`

MPM analysis:

- causal trailing 40 ms frame;
- 12 kHz analysis rate;
- 80–1200 Hz lag range;
- clarity = maximum positive NSDF peak within the allowed lag range;
- no threshold tuning after measurement.

## Event masks

Masks are defined from the existing baseline autocorrelation features only:

- noise-like high-band reference mask: prior definition;
- strong periodic body reference mask: prior definition;
- low-frequency transient reference mask: prior definition;
- bright voiced reference mask: prior definition.

Candidate MPM output is not allowed to select its own evaluation frames.

## Metrics

Same as YIN private replay:

- baseline-mask counts;
- autocorr-guard and MPM-guard retention ratios;
- MPM minus autocorr noise-like retention;
- low-frequency transient median/p10 retention;
- periodic-body mean absolute delta;
- processing-variant pairwise correlation;
- MPM/autocorr active-frame confidence correlation;
- finite values.

## Acceptance for MPM as next product-research challenger

With adequate pooled reference counts:

1. all values finite;
2. each source >=100 active frames;
3. noise-like mask >=30;
4. low-frequency transient mask >=30;
5. periodic-body mask >=30;
6. MPM noise-like median retention <= **0.50**;
7. MPM noise-like median retention <= autocorr median + **0.02**;
8. MPM low-frequency median retention >= **0.90**;
9. MPM low-frequency p10 retention >= **0.80**;
10. MPM periodic-body mean absolute delta <= **0.03**;
11. MPM guard pairwise correlation median >= **0.80**;
12. MPM guard correlation median >= autocorr guard correlation median - **0.05**.

The mature-detector target of <=0.35 noise-like retention remains unchanged.

## Rejection

Reject MPM as the immediate challenger if an adequate-count non-regression gate fails.

## High-register limitation

The known bright-voiced private reference count is zero. Passing this replay cannot close the separate multi-singer/high-register corpus gap.
