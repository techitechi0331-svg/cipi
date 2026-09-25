# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R11-SELF-COUNTERFACTUAL-001`
- Run: `gha-36179619006-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R11-SELF-COUNTERFACTUAL-001:gha-36179619006-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a deployable same-observation spectral-inpainting counterfactual approximate the R7 paired causal delta and materially improve semantic candidate ranking without increasing independent clean-vocal false triggers?

## Hypothesis

Across both predeclared seeds, observed-minus-inpainted counterfactual features will improve conditional Top-5 by at least 0.08, close at least 15 percent of the R7 oracle gap, preserve strong-effect conditional Top-5 within 0.05, and not worsen external clean false-trigger by more than 0.025.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- for each seed: source overlap count == 0
- for each seed: conditional Top-5 >= static + 0.08
- for each seed: R7 oracle gap closure >= 0.15
- for each seed: strong-effect conditional Top-5 >= static - 0.05
- for each seed: external clean false-trigger <= static + 0.025
- for each seed: generator ceiling >= 0.80

### Rejection criteria

- any seed has source overlap
- any seed conditional Top-5 improvement < 0.08
- any seed oracle gap closure < 0.15
- any seed strong-effect conditional Top-5 regresses by more than 0.05
- any seed external clean false-trigger worsens by more than 0.025

## Bounded metric snapshot

- `candidate_budget`: 20
- `counterfactual_feature_family[0]`: cf_delta_local_s2
- `counterfactual_feature_family[1]`: cf_delta_local_s4
- `counterfactual_feature_family[2]`: cf_delta_local_s8
- `counterfactual_feature_family[3]`: cf_delta_local_s12
- `counterfactual_feature_family[4]`: cf_delta_q80_s4
- `counterfactual_feature_family[5]`: cf_delta_q80_s8
- `counterfactual_feature_family[6]`: cf_delta_persistence_s4
- `counterfactual_feature_family[7]`: cf_delta_persistence_s8
- `counterfactual_feature_family[8]`: cf_raw_boost_q80_s4
- `counterfactual_feature_family[9]`: cf_raw_boost_q80_s8
- `counterfactual_feature_family[10]`: cf_raw_boost_gt1_s4
- `counterfactual_feature_family[11]`: cf_raw_boost_gt1_s8
- `counterfactual_feature_family[12]`: cf_log_delta_s4
- `counterfactual_feature_family[13]`: cf_log_delta_s8
- `counterfactual_feature_family[14]`: cf_scale_consistency
- `counterfactual_feature_family[15]`: cf_relative_suppression
- `experiment`: VOCAL_RESONANCE_R11_SELF_COUNTERFACTUAL_INPAINTING
- `per_seed.20261003.conditional_top5_gap_closure`: 0.0
- `per_seed.20261003.counterfactual_C`: 0.1
- `per_seed.20261003.counterfactual_test.generator_ceiling`: 0.9375
- `per_seed.20261003.counterfactual_test.mrr`: 0.1718504279625603
- `per_seed.20261003.counterfactual_test.n_cases`: 32
- `per_seed.20261003.counterfactual_test.n_high_f0_cases`: 0
- `per_seed.20261003.counterfactual_test.strong_hit_cases`: 11
- `per_seed.20261003.counterfactual_test.strong_top5_given_generator_hit`: 0.2727272727272727
- `per_seed.20261003.counterfactual_test.top1`: 0.03125
- `per_seed.20261003.counterfactual_test.top1_given_generator_hit`: 0.03333333333333333
- `per_seed.20261003.counterfactual_test.top3`: 0.125
- `per_seed.20261003.counterfactual_test.top3_given_generator_hit`: 0.13333333333333333
- `per_seed.20261003.counterfactual_test.top5`: 0.25
- `per_seed.20261003.counterfactual_test.top5_effect_gte3`: 0.25

## Knowledge candidate

Same-observation spectral inpainting may provide a deployable self-counterfactual proxy for the causal resonance delta revealed by a paired clean/injected oracle.

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
