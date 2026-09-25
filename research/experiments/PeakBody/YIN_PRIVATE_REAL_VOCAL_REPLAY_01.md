# PeakBody YIN Private Real-Vocal Replay 01

Status: **PROTOCOL LOCKED BEFORE MEASUREMENT**  
Evidence target: **MEASURED / private aggregate only**

## Research Question

On the same four private processing variants used in PeakBody Private Real-Vocal Guard Validation 01, does replacing normalized-autocorrelation periodicity confidence with YIN-CMND confidence preserve the known low-frequency/body/processing-invariance behavior **without increasing false protection on the previously observed noise-like high-band frames**?

## Why this test now

The synthetic periodicity-family benchmark qualified both YIN-CMND and MPM-NSDF.

YIN is the first challenger because:

- operation proxy was 0.7172x normalized-autocorrelation baseline;
- clean F0 diagnostic error was much lower;
- bright/noisy voiced synthetic confidence passed.

However, YIN noise-like confidence was **higher** than the current autocorrelation baseline, creating a plausible risk that it will protect sibilance/breath too strongly in real vocal material.

## Private source scope

Use the same four SHA-256-bound private processing variants from:

`PEAKBODY-PRIVATE-VOCAL-GUARD-001/private-local-01`

They represent one performance under four processing variants, not four independent singers.

No raw audio may enter GitHub.

## Fixed signal analysis

- mono analysis;
- analysis hop: 5 ms;
- trailing frame: 40 ms;
- analysis rate for YIN: 12 kHz equivalent;
- YIN lag range: 80–1200 Hz;
- YIN confidence: `clamp(1 - CMND_min, 0, 1)`;
- spectral guard unchanged from prior study;
- guard strength unchanged: 0.75;
- Revision 02 crest/transient-factor law unchanged.

## Baseline

Previous/current analysis-periodicity guard:

`candidate_auto = t * (1 - 0.75 * spectral_guard * (1 - autocorr_confidence))`

## Challenger

YIN-CMND guard:

`candidate_yin = t * (1 - 0.75 * spectral_guard * (1 - yin_confidence))`

No threshold tuning is permitted in this replay.

## Event masks

To prevent candidate-dependent event selection, event masks are defined from **baseline features only**.

### Noise-like high-band reference mask

Reuse the prior baseline definition:

- active;
- baseline transient factor >= 0.75;
- spectral guard >= 0.5;
- normalized-autocorrelation confidence <= 0.35.

The prior run contained 246 pooled frames.

### Strong periodic body reference mask

- active;
- normalized-autocorrelation confidence >= 0.80;
- baseline transient factor <= 0.50.

### Low-frequency transient reference mask

- active;
- baseline transient factor >= 0.75;
- low-band (<900 Hz) power ratio >= 0.60.

### Bright voiced reference mask

- active;
- baseline transient factor >= 0.75;
- spectral guard >= 0.5;
- normalized-autocorrelation confidence >= 0.80.

The prior run had zero such frames; this remains a coverage gap rather than a reason to tune thresholds.

## Metrics

Per source and pooled:

- exact baseline-mask counts;
- autocorr-guard retention ratio;
- YIN-guard retention ratio;
- YIN minus autocorr retention on noise-like mask;
- low-frequency transient median/p10 retention;
- periodic-body mean absolute delta;
- processing-variant pairwise correlation;
- active-frame YIN/autocorr confidence correlation;
- YIN confidence quantiles on baseline noise-like mask;
- finite values.

## Acceptance for YIN as next product-research challenger

This replay qualifies YIN for later C++/broader-corpus testing only if:

1. all values finite;
2. each source has >=100 active frames;
3. pooled baseline noise-like mask count >=30;
4. pooled low-frequency transient count >=30;
5. pooled periodic-body count >=30;
6. YIN noise-like median retention <= **0.50**;
7. YIN noise-like median retention is no more than **0.02 absolute** above autocorr-guard median retention;
8. YIN low-frequency transient median retention >= **0.90**;
9. YIN low-frequency transient p10 retention >= **0.80**;
10. YIN periodic-body mean absolute delta from Revision-02 baseline <= **0.03**;
11. median pairwise YIN-guard transient-factor correlation >= **0.80**;
12. YIN-guard correlation median is not more than **0.05** below the autocorr-guard correlation median.

The original target of noise-like retention <=0.35 remains the desired mature-detector target; this replay does **not** lower that final target. The 0.50 gate is only a non-regression qualification against the already-measured private baseline.

## Rejection

Reject YIN as the immediate PeakBody challenger for this private scope if adequate mask counts exist and any preservation/non-regression gate fails.

## Inconclusive

Return INCONCLUSIVE if a required baseline-defined mask has fewer than 30 pooled frames.

The known absence of bright-voiced frames means this replay cannot validate high-register safety; that remains a separate open corpus gap even if all non-regression gates pass.

## Privacy

Commit only:

- aggregate metrics;
- source hashes already stored in the prior run;
- protocol;
- reproducible analysis code;
- immutable decision/provenance.

Do not commit raw audio, timecodes, per-frame arrays, or spectral images.
