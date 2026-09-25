# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R8-LOCAL-PATCH-001`
- Run: `gha-36155951333-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R8-LOCAL-PATCH-001:gha-36155951333-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can deployable single-view local spectro-temporal patch/context features recover a material fraction of the R7 causal-oracle ranking gap without increasing independent clean-vocal false triggers?

## Hypothesis

Across both predeclared seeds, local multi-scale curvature/shoulder/coherence features will improve conditional Top-5 by at least 0.08 over the frozen static ranker, close at least 15 percent of the R7 oracle gap, preserve strong-effect conditional Top-5 within 0.05, and not worsen external clean false-trigger by more than 0.05.

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
- `experiment`: VOCAL_RESONANCE_R8_SINGLE_VIEW_LOCAL_PATCH
- `feature_family[0]`: ms_resid_s2_q80
- `feature_family[1]`: ms_resid_s4_q80
- `feature_family[2]`: ms_resid_s8_q80
- `feature_family[3]`: ms_resid_s12_q80
- `feature_family[4]`: narrow_minus_broad
- `feature_family[5]`: shoulder_drop_2_q80
- `feature_family[6]`: shoulder_drop_4_q80
- `feature_family[7]`: shoulder_drop_8_q80
- `feature_family[8]`: shoulder_asym_4_median
- `feature_family[9]`: center_neighbor_corr_4
- `feature_family[10]`: center_neighbor_corr_8
- `feature_family[11]`: patch_stationarity_4
- `per_seed.20261003.conditional_top5_gap_closure`: 0.0
- `per_seed.20261003.external_clean_n`: 40
- `per_seed.20261003.external_clean_patch_fpr`: 0.325
- `per_seed.20261003.external_clean_static_fpr`: 0.175
- `per_seed.20261003.oracle_conditional_top5`: 1.0
- `per_seed.20261003.oracle_strong_conditional_top5`: 1.0
- `per_seed.20261003.patch_C`: 0.03
- `per_seed.20261003.patch_test.generator_ceiling`: 0.9375
- `per_seed.20261003.patch_test.mrr`: 0.1826531509157767
- `per_seed.20261003.patch_test.n_cases`: 32
- `per_seed.20261003.patch_test.n_high_f0_cases`: 0
- `per_seed.20261003.patch_test.strong_hit_cases`: 11
- `per_seed.20261003.patch_test.strong_top5_given_generator_hit`: 0.45454545454545453
- `per_seed.20261003.patch_test.top1`: 0.0625
- `per_seed.20261003.patch_test.top1_given_generator_hit`: 0.06666666666666667
- `per_seed.20261003.patch_test.top3`: 0.09375
- `per_seed.20261003.patch_test.top3_given_generator_hit`: 0.1
- `per_seed.20261003.patch_test.top5`: 0.25

## Knowledge candidate

Single-view multi-scale local spectro-temporal patch shape may recover part of the causal resonance information revealed by the paired R7 oracle.

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
