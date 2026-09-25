# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R6-RUN-VETO-001`
- Run: `gha-36142911813-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R6-RUN-VETO-001:gha-36142911813-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can run-length-only temporal morphology work as a separate post-ranker veto/abstention gate that reduces clean-vocal false triggers without reordering candidates or vetoing true injected resonances?

## Hypothesis

Across both predeclared injection seeds, a validation-selected run-length veto will reduce independent clean false-trigger rate by at least 5 percentage points while retaining at least 95 percent of baseline target actions and strong-effect target actions.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- for each seed: source overlap count == 0
- for each seed: ranking order is unchanged
- for each seed: veto external clean false-trigger <= baseline - 0.05
- for each seed: paired external-clean bootstrap upper bound <= 0
- for each seed: target action keep >= 0.95
- for each seed: strong-effect target action keep >= 0.95
- for each seed: veto creates zero new external clean false triggers

### Rejection criteria

- any seed fails the 5 percentage point clean false-trigger reduction
- any seed target action keep < 0.95
- any seed strong-effect action keep < 0.95
- candidate ranking is changed
- source overlap is detected

## Bounded metric snapshot

- `candidate_budget`: 20
- `experiment`: VOCAL_RESONANCE_R6_RUN_LENGTH_VETO
- `per_seed.20261003.external_clean.baseline_fpr`: 0.175
- `per_seed.20261003.external_clean.bootstrap_hi`: 0.0
- `per_seed.20261003.external_clean.bootstrap_lo`: -0.075
- `per_seed.20261003.external_clean.improvements`: 1
- `per_seed.20261003.external_clean.n`: 40
- `per_seed.20261003.external_clean.regressions`: 0
- `per_seed.20261003.external_clean.veto_fpr`: 0.15
- `per_seed.20261003.external_clean.veto_minus_baseline`: -0.025
- `per_seed.20261003.internal_clean.baseline_fpr`: 0.375
- `per_seed.20261003.internal_clean.bootstrap_hi`: 0.0
- `per_seed.20261003.internal_clean.bootstrap_lo`: 0.0
- `per_seed.20261003.internal_clean.improvements`: 0
- `per_seed.20261003.internal_clean.n`: 8
- `per_seed.20261003.internal_clean.regressions`: 0
- `per_seed.20261003.internal_clean.veto_fpr`: 0.375
- `per_seed.20261003.internal_clean.veto_minus_baseline`: 0.0
- `per_seed.20261003.ranking_order_unchanged`: True
- `per_seed.20261003.seed`: 20261003
- `per_seed.20261003.source_overlap_count`: 0
- `per_seed.20261003.static_C`: 0.03
- `per_seed.20261003.static_ranking.clean_false_trigger`: 0.375
- `per_seed.20261003.static_ranking.generator_ceiling`: 0.9375
- `per_seed.20261003.static_ranking.mrr`: 0.17148762051287206
- `per_seed.20261003.static_ranking.n_cases`: 32
- `per_seed.20261003.static_ranking.n_high_f0_cases`: 0
- `per_seed.20261003.static_ranking.threshold_from_valid_95pct`: 0.7941223642156119
- `per_seed.20261003.static_ranking.top1`: 0.03125
- `per_seed.20261003.static_ranking.top1_given_generator_hit`: 0.03333333333333333
- `per_seed.20261003.static_ranking.top3`: 0.125
- `per_seed.20261003.static_ranking.top3_given_generator_hit`: 0.13333333333333333

## Knowledge candidate

Run-length morphology may be useful as a separate post-ranker abstention/veto signal even when it is not stable enough to modify semantic ranking scores.

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
