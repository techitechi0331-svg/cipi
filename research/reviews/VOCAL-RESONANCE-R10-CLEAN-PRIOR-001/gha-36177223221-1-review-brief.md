# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R10-CLEAN-PRIOR-001`
- Run: `gha-36177223221-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R10-CLEAN-PRIOR-001:gha-36177223221-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a lightweight normative prior learned only from clean training singers provide deployable single-view information that materially closes the R7 causal-oracle ranking gap without increasing independent clean-vocal false triggers?

## Hypothesis

Across both predeclared seeds, adding clean-trained frequency-conditioned robust rarity features to the frozen static candidate representation will improve conditional Top-5 by at least 0.08, close at least 15 percent of the R7 oracle gap, preserve strong-effect conditional Top-5 within 0.05, and not worsen external clean false-trigger by more than 0.025.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- for each seed: prior is fit only on predeclared training singers
- for each seed: conditional Top-5 >= static + 0.08
- for each seed: R7 oracle gap closure >= 0.15
- for each seed: strong-effect conditional Top-5 >= static - 0.05
- for each seed: external clean false-trigger <= static + 0.025
- for each seed: generator ceiling >= 0.80

### Rejection criteria

- any seed has prior singer leakage
- any seed conditional Top-5 improvement < 0.08
- any seed oracle gap closure < 0.15
- any seed strong-effect conditional Top-5 regresses by more than 0.05
- any seed external clean false-trigger worsens by more than 0.025

## Bounded metric snapshot

- `candidate_budget`: 20
- `experiment`: VOCAL_RESONANCE_R10_CLEAN_NORMATIVE_PRIOR
- `per_seed.20261003.combined_C`: 0.03
- `per_seed.20261003.combined_test.generator_ceiling`: 0.9375
- `per_seed.20261003.combined_test.mrr`: 0.17700546934897748
- `per_seed.20261003.combined_test.n_cases`: 32
- `per_seed.20261003.combined_test.n_high_f0_cases`: 0
- `per_seed.20261003.combined_test.strong_hit_cases`: 11
- `per_seed.20261003.combined_test.strong_top5_given_generator_hit`: 0.36363636363636365
- `per_seed.20261003.combined_test.top1`: 0.03125
- `per_seed.20261003.combined_test.top1_given_generator_hit`: 0.03333333333333333
- `per_seed.20261003.combined_test.top3`: 0.15625
- `per_seed.20261003.combined_test.top3_given_generator_hit`: 0.16666666666666666
- `per_seed.20261003.combined_test.top5`: 0.25
- `per_seed.20261003.combined_test.top5_effect_gte3`: 0.3333333333333333
- `per_seed.20261003.combined_test.top5_given_generator_hit`: 0.26666666666666666
- `per_seed.20261003.combined_test.top5_high_f0`: None
- `per_seed.20261003.combined_validation.generator_ceiling`: 0.84375
- `per_seed.20261003.combined_validation.mrr`: 0.2652990206710214
- `per_seed.20261003.combined_validation.n_cases`: 32
- `per_seed.20261003.combined_validation.n_high_f0_cases`: 0
- `per_seed.20261003.combined_validation.top1`: 0.125
- `per_seed.20261003.combined_validation.top1_given_generator_hit`: 0.14814814814814814
- `per_seed.20261003.combined_validation.top3`: 0.28125
- `per_seed.20261003.combined_validation.top3_given_generator_hit`: 0.3333333333333333
- `per_seed.20261003.combined_validation.top5`: 0.4375
- `per_seed.20261003.combined_validation.top5_effect_gte3`: 0.5625
- `per_seed.20261003.combined_validation.top5_given_generator_hit`: 0.5185185185185185
- `per_seed.20261003.combined_validation.top5_high_f0`: None
- `per_seed.20261003.conditional_top5_gap_closure`: 0.0
- `per_seed.20261003.external_clean_combined_fpr`: 0.225
- `per_seed.20261003.external_clean_n`: 40

## Knowledge candidate

Singer-disjoint clean-vocal normative priors may provide deployable context for distinguishing unusual candidate resonances from ordinary vocal spectral structure without a paired clean reference.

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
