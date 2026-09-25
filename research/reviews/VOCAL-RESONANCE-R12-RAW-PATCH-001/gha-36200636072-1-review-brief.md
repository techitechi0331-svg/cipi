# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R12-RAW-PATCH-001`
- Run: `gha-36200636072-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R12-RAW-PATCH-001:gha-36200636072-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Do candidate-centered normalized raw 2D local-residual patches contain deployable single-view resonance information that the hand-crafted R8-R11 summaries discarded?

## Hypothesis

Across both predeclared seeds, at least one raw-patch model will improve conditional Top-5 by at least 0.08, close at least 15 percent of the R7 oracle gap, preserve strong-effect conditional Top-5 within 0.05, and not worsen external clean false-trigger by more than 0.05.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- on both seeds, at least one predeclared raw-patch model satisfies all model criteria
- model criteria: source overlap count == 0
- model criteria: generator ceiling >= 0.80
- model criteria: conditional Top-5 >= static + 0.08
- model criteria: R7 oracle gap closure >= 0.15
- model criteria: strong-effect conditional Top-5 >= static - 0.05
- model criteria: external clean false-trigger <= static + 0.05

### Rejection criteria

- no raw-patch model satisfies all criteria on both seeds

## Bounded metric snapshot

- `candidate_budget`: 20
- `diagnostic_gate.accepted`: False
- `diagnostic_gate.criteria.combined_linear.20261003.conditional_top5_improves_by_0_08`: False
- `diagnostic_gate.criteria.combined_linear.20261003.external_clean_fpr_not_worse_by_0_05`: True
- `diagnostic_gate.criteria.combined_linear.20261003.generator_ceiling_gte_0_80`: True
- `diagnostic_gate.criteria.combined_linear.20261003.oracle_gap_closure_gte_0_15`: False
- `diagnostic_gate.criteria.combined_linear.20261003.strong_conditional_top5_not_worse_by_0_05`: False
- `diagnostic_gate.criteria.combined_linear.20261003.zero_source_overlap`: True
- `diagnostic_gate.criteria.combined_linear.20261013.conditional_top5_improves_by_0_08`: False
- `diagnostic_gate.criteria.combined_linear.20261013.external_clean_fpr_not_worse_by_0_05`: True
- `diagnostic_gate.criteria.combined_linear.20261013.generator_ceiling_gte_0_80`: True
- `diagnostic_gate.criteria.combined_linear.20261013.oracle_gap_closure_gte_0_15`: False
- `diagnostic_gate.criteria.combined_linear.20261013.strong_conditional_top5_not_worse_by_0_05`: True
- `diagnostic_gate.criteria.combined_linear.20261013.zero_source_overlap`: True
- `diagnostic_gate.criteria.patch_linear.20261003.conditional_top5_improves_by_0_08`: False
- `diagnostic_gate.criteria.patch_linear.20261003.external_clean_fpr_not_worse_by_0_05`: True
- `diagnostic_gate.criteria.patch_linear.20261003.generator_ceiling_gte_0_80`: True
- `diagnostic_gate.criteria.patch_linear.20261003.oracle_gap_closure_gte_0_15`: False
- `diagnostic_gate.criteria.patch_linear.20261003.strong_conditional_top5_not_worse_by_0_05`: False
- `diagnostic_gate.criteria.patch_linear.20261003.zero_source_overlap`: True
- `diagnostic_gate.criteria.patch_linear.20261013.conditional_top5_improves_by_0_08`: False
- `diagnostic_gate.criteria.patch_linear.20261013.external_clean_fpr_not_worse_by_0_05`: True
- `diagnostic_gate.criteria.patch_linear.20261013.generator_ceiling_gte_0_80`: True
- `diagnostic_gate.criteria.patch_linear.20261013.oracle_gap_closure_gte_0_15`: False
- `diagnostic_gate.criteria.patch_linear.20261013.strong_conditional_top5_not_worse_by_0_05`: True
- `diagnostic_gate.criteria.patch_linear.20261013.zero_source_overlap`: True
- `diagnostic_gate.criteria.tiny_mlp.20261003.conditional_top5_improves_by_0_08`: False
- `diagnostic_gate.criteria.tiny_mlp.20261003.external_clean_fpr_not_worse_by_0_05`: True
- `diagnostic_gate.criteria.tiny_mlp.20261003.generator_ceiling_gte_0_80`: True
- `diagnostic_gate.criteria.tiny_mlp.20261003.oracle_gap_closure_gte_0_15`: False
- `diagnostic_gate.criteria.tiny_mlp.20261003.strong_conditional_top5_not_worse_by_0_05`: False
- `diagnostic_gate.criteria.tiny_mlp.20261003.zero_source_overlap`: True

## Knowledge candidate

Candidate-centered raw local-residual spectro-temporal patches may retain deployable single-view resonance information that compact hand-crafted summaries discard.

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
