# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `MICRODOUBLE-SIBILANCE-R3-GATE-001`
- Run: `gha-36089834243-1`
- Brief revision: **1**
- Triage: `MICRODOUBLE-SIBILANCE-R3-GATE-001:gha-36089834243-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **PROMOTION_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the predeclared MicroDouble sibilance R3 study preserve its R1/R2 negative results, deterministically select activation 0.62 as the highest passing candidate, and reproduce every gate on a disjoint holdout set strongly enough to authorize development integration?

## Hypothesis

The exact source transfer and R2 remain rejected, but activation 0.62 is the highest passing predeclared candidate and independently passes the frozen holdout criteria, justifying implementation on a development branch.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Committed metrics snapshot SHA256 must match.
- R1 and R2 must remain failed evidence and the 0.64 R3 candidate must remain failed.
- Both 0.62 and 0.60 must pass selection so the highest-passing rule deterministically freezes 0.62.
- Frozen activation must equal 0.62.
- Holdout clean candidate occupancy must be at most 5 percent.
- Holdout candidate detection recall must be at least 75 percent.
- Holdout recall gap versus baseline must be at most 5 percentage points.
- Holdout candidate non-event occupancy must be at most 6 percent and at least 2 percentage points below baseline.
- Holdout event strength mean must be at least 0.10 and p90 at least 0.20.
- Holdout maximum onset latency must be at most 25 ms.

### Rejection criteria

- Any declared acceptance condition fails.
- Negative results are missing or rewritten.
- The frozen threshold differs from the predeclared highest-passing rule.

## Bounded metric snapshot

- `holdout_baseline_non_event_pct`: 10.08347
- `holdout_baseline_recall_pct`: 97.464097
- `holdout_candidate_clean_pct`: 0.0
- `holdout_candidate_non_event_pct`: 0.364273
- `holdout_candidate_recall_pct`: 94.744268
- `holdout_gate_ok`: True
- `holdout_max_onset_ms`: 23.310658
- `holdout_pass`: 1.0
- `holdout_recall_gap_pp`: 2.719829
- `holdout_strength_mean`: 0.381149
- `holdout_strength_p90`: 0.443423
- `r1_r2_and_064_negative_evidence_preserved`: True
- `r2_recall_gap_pp`: 5.728143
- `r3_060_pass`: 1.0
- `r3_062_pass`: 1.0
- `r3_064_pass`: 0.0
- `r3_selected_activation`: 0.62
- `selection_rule_ok`: True
- `snapshot_checksum_ok`: True

## Knowledge candidate

In the controlled MicroDouble transfer study, separating detection from protection strength and calibrating only the hybrid detector activation threshold to 0.62 produced a candidate that passed predeclared selection and disjoint holdout gates while preserving prior negative results.

## Reusable findings already retained

- none recorded

## Human-only gates

- Review R1/R2 negative-result preservation before development integration.
- Product regressions and listening after integration.

## Allowed review actions

ITERATE, ARCHIVE_AFTER_REVIEW

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
