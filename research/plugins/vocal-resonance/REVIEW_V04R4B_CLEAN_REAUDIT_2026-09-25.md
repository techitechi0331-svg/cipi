# Vocal Resonance MODULE 1 v0.4R.4b Independent Clean-Negative Re-audit Review

Date: 2026-09-25

Source:
`research/runs/VOCAL-RESONANCE-R4-CLEAN-REAUDIT-002/gha-36072656461-2/`

## Verdict

**ITERATE — diagnostic evidence accepted; technique-specific hypothesis not replicated.**

## MEASURED

Independent cohort:
- 40 clean excerpts
- 4 held-out singers
- 9 resolved techniques
- 3 exercise families
- 0 basename overlap with Audit-001
- overall clean false-trigger: **20.0%**

Technique:
- belt: 25.0%
- breathy: 12.5%
- fast_forte: 50.0%
- fast_piano: 0%
- forte: 50.0%
- inhaled: 100% (n=1; insufficient for a technique claim)
- spoken: 0%
- straight: 0%
- vibrato: 0%

Grouped:
- fast_piano + fast_forte: **25.0%**
- other techniques: **18.75%**
- difference: **+6.25 percentage points**

Therefore the Audit-001 fast-technique concentration did **not** replicate under the broader independent cohort.

Exercise family:
- arpeggio: 18.75%
- other: 18.75%
- scale: 25.0%

No single exercise family dominated.

## Pitch re-audit

A conservative YIN-style proxy was added alongside the legacy ACF proxy.

- YIN p90 >= 400 Hz: 16 cases
- false-trigger in that group: **12.5%**
- overall false-trigger: 20.0%
- YIN unresolved: 2 cases

The available high-pitch subset is sufficient for diagnostic coverage, but high pitch was **not** a higher-false-trigger subgroup in this cohort.

Legacy ACF upper-quantile saturation remains visible:
- old ACF p90 >= 900 Hz: 6 cases
- old ACF p95 >= 900 Hz: 22 cases

Do not use those upper ACF quantiles as high-pitch ground truth.

## REJECTED

For the current evidence:
- lip-trill-specific protection: rejected;
- fast-piano/fast-forte-specific protection: not supported / do not implement;
- high-pitch-specific false-trigger protection: not supported / do not implement.

## INFERRED

The remaining clean false-trigger problem is more likely a general candidate-context / calibration problem than a single vocal-technique or pitch-regime failure.

## Next research question

Test a **generic temporal-morphology feature family** that does not depend on technique labels or F0:
- longest continuous candidate-active run;
- active-run count / fragmentation;
- median active-run duration;
- temporal occupancy;
- temporal entropy / concentration.

Compare it against the unchanged static R2-style safe-negative ranker and simple prominence baseline.

The feature family should be retained only if it improves ranking while materially reducing clean false triggers on disjoint singers/excerpts.

No production suppressor or VST3 is authorized.
