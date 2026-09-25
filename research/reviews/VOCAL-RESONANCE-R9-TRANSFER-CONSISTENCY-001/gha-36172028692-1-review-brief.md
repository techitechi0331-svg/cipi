# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R9-TRANSFER-CONSISTENCY-001`
- Run: `gha-36172028692-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R9-TRANSFER-CONSISTENCY-001:gha-36172028692-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can deployable single-view fixed-Hz temporal transfer-consistency features recover a material fraction of the R7 causal-oracle ranking gap without increasing independent clean-vocal false triggers?

## Hypothesis

Across both predeclared seeds, time-consistent center-vs-neighborhood relative-gain features will improve conditional Top-5 by at least 0.08 over the frozen static ranker, close at least 15 percent of the R7 oracle gap, preserve strong-effect conditional Top-5 within 0.05, and not worsen external clean false-trigger by more than 0.05.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- for each seed: conditional Top-5 >= static + 0.08
- for each seed: R7 oracle gap closure >= 0.15
- for each seed: strong-effect conditional Top-5 >= static - 0.05
- for each seed: external clean false-trigger <= static + 0.05
- for each seed: generator ceiling >= 0.80

### Rejection criteria

- any seed conditional Top-5 improvement < 0.08
- any seed oracle gap closure < 0.15
- any seed strong-effect conditional Top-5 regresses by more than 0.05
- any seed external clean false-trigger worsens by more than 0.05

## Bounded metric snapshot

- `candidate_budget`: 20
- `experiment`: VOCAL_RESONANCE_R9_TRANSFER_CONSISTENCY
- `feature_family[0]`: rel_gain_near_median
- `feature_family[1]`: rel_gain_near_mad
- `feature_family[2]`: rel_gain_near_q80
- `feature_family[3]`: rel_gain_near_pos_frac
- `feature_family[4]`: rel_gain_near_gt1_frac
- `feature_family[5]`: rel_gain_near_robust_snr
- `feature_family[6]`: rel_gain_near_diff_mad
- `feature_family[7]`: rel_gain_near_lag1_corr
- `feature_family[8]`: rel_gain_far_median
- `feature_family[9]`: rel_gain_far_mad
- `feature_family[10]`: near_far_consistency
- `feature_family[11]`: center_reference_corr
- `feature_family[12]`: regression_intercept
- `feature_family[13]`: regression_slope
- `feature_family[14]`: regression_resid_mad
- `per_seed.20261003.conditional_top5_gap_closure`: 0.09090909090909088
- `per_seed.20261003.external_clean_n`: 40
- `per_seed.20261003.external_clean_static_fpr`: 0.175
- `per_seed.20261003.external_clean_transfer_fpr`: 0.3
- `per_seed.20261003.oracle_conditional_top5`: 1.0
- `per_seed.20261003.oracle_strong_conditional_top5`: 1.0
- `per_seed.20261003.seed`: 20261003
- `per_seed.20261003.static_C`: 0.03
- `per_seed.20261003.static_test.generator_ceiling`: 0.9375
- `per_seed.20261003.static_test.mrr`: 0.17148762051287206
- `per_seed.20261003.static_test.n_cases`: 32
- `per_seed.20261003.static_test.n_high_f0_cases`: 0
- `per_seed.20261003.static_test.strong_hit_cases`: 11
- `per_seed.20261003.static_test.strong_top5_given_generator_hit`: 0.36363636363636365
- `per_seed.20261003.static_test.top1`: 0.03125

## Knowledge candidate

A fixed unwanted resonance may be distinguishable from natural vocal structure by the time-consistency of its relative gain at one absolute frequency versus neighboring spectral context.

## Reusable findings already retained

- none recorded

## Human-only gates

- none

## Allowed review actions

REJECT, ITERATE, ARCHIVE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
