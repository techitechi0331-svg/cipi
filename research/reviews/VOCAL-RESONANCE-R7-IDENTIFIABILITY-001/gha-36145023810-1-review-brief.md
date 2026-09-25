# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R7-IDENTIFIABILITY-001`
- Run: `gha-36145023810-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R7-IDENTIFIABILITY-001:gha-36145023810-1:triage-v1`
- Route: **CONTINUE_RESEARCH**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

When candidate discovery hits the injected resonance, does a research-only paired clean/injected causal oracle rank that target near the top, and how large is the gap versus single-view inference features?

## Hypothesis

If single-view feature information is the main blocker, the causal oracle will achieve conditional Top-5 >= 0.80 and strong-effect conditional Top-5 >= 0.85 on both seeds, with at least a 0.20 conditional Top-5 gain over the frozen static ranker.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- for each seed: generator ceiling >= 0.80
- for each seed: at least 24 locked test cases
- for each seed: at least 20 target candidate rows

### Rejection criteria

- audit coverage is insufficient on either seed

## Bounded metric snapshot

- `candidate_budget`: 20
- `diagnostic_gate.accepted`: True
- `diagnostic_gate.criteria.20261003.coverage_sufficient`: True
- `diagnostic_gate.criteria.20261003.oracle_gap_vs_static_gte_0_20`: True
- `diagnostic_gate.criteria.20261003.oracle_strong_given_hit_gte_0_85`: True
- `diagnostic_gate.criteria.20261003.oracle_top5_given_hit_gte_0_80`: True
- `diagnostic_gate.criteria.20261013.coverage_sufficient`: True
- `diagnostic_gate.criteria.20261013.oracle_gap_vs_static_gte_0_20`: True
- `diagnostic_gate.criteria.20261013.oracle_strong_given_hit_gte_0_85`: True
- `diagnostic_gate.criteria.20261013.oracle_top5_given_hit_gte_0_80`: True
- `diagnostic_gate.meaning`: Acceptance means the audit has enough coverage to diagnose the next research direction. It is not product or knowledge promotion.
- `diagnostic_gate.route`: SINGLE_VIEW_FEATURE_INFORMATION_GAP
- `experiment`: VOCAL_RESONANCE_R7_IDENTIFIABILITY_ORACLE
- `oracle_is_research_only`: True
- `per_seed.20261003.diagnostics.injected_candidate_rows`: 640
- `per_seed.20261003.diagnostics.safe_abs_delta_local_median`: 0.0030180987453819474
- `per_seed.20261003.diagnostics.safe_negative_new_candidate_fraction`: 0.0
- `per_seed.20261003.diagnostics.safe_negative_rows`: 537
- `per_seed.20261003.diagnostics.target_abs_delta_local_median`: 0.2196879492563002
- `per_seed.20261003.diagnostics.target_new_candidate_fraction`: 0.3333333333333333
- `per_seed.20261003.diagnostics.target_rows`: 30
- `per_seed.20261003.oracle.generator_ceiling`: 0.9375
- `per_seed.20261003.oracle.mrr`: 0.5546875
- `per_seed.20261003.oracle.n_cases`: 32
- `per_seed.20261003.oracle.n_high_f0_cases`: 0
- `per_seed.20261003.oracle.strong_hit_cases`: 11
- `per_seed.20261003.oracle.strong_top5_given_generator_hit`: 1.0
- `per_seed.20261003.oracle.top1`: 0.28125
- `per_seed.20261003.oracle.top1_given_generator_hit`: 0.3
- `per_seed.20261003.oracle.top3`: 0.90625
- `per_seed.20261003.oracle.top3_given_generator_hit`: 0.9666666666666667
- `per_seed.20261003.oracle.top5`: 0.9375

## Knowledge candidate

A paired clean/injected causal oracle can diagnose whether poor vocal-resonance semantic ranking is caused primarily by missing single-view information versus candidate/label alignment.

## Reusable findings already retained

- none recorded

## Human-only gates

- none

## Allowed review actions

ITERATE, ARCHIVE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
