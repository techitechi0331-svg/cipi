# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-AMOUNT-R3-VOCALSET-001`
- Run: `gha-36176939027-1`
- Brief revision: **1**
- Triage: `VO-PREP-AMOUNT-R3-VOCALSET-001:gha-36176939027-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a predeclared DesiredGR-scaling Amount mapping with a selection-side ripple safety margin pass the unchanged Vo.Prep real-vocal gates on a completely different VocalSet singer corpus after Amount R2 narrowly failed HUST holdout ripple?

## Hypothesis

At least one target100 value among 5.0, 5.2, 5.3, 5.4, and 5.5 dB will pass all original Amount safety gates plus a 0.075 dB selection ripple margin on four VocalSet selection singers, and the frozen selected candidate will then pass the unchanged 0.080 dB ripple gate and all other original gates on four different VocalSet holdout singers.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- Candidate target values and offsets are fixed before VocalSet evaluation.
- Selection uses exactly f1, f2, m1, and m2 with two qualifying files per singer.
- Final holdout uses exactly f3, f4, m3, and m4 with two qualifying files per singer.
- No singer appears in both selection and final holdout.
- Selection candidate must pass every original Amount gate with GR ripple tightened to no more than 0.075 dB.
- Among selection-margin passers, choose the highest target100 value before opening final holdout.
- Amount 0 final holdout produces exact zero gain reduction.
- Amount 25 final-holdout mean GR is between 0.75 and 2.25 dB and p95 GR is no more than 4.0 dB.
- Amount 50 final-holdout mean GR is between 2.5 and 3.75 dB, p95 GR is no more than 6.0 dB, and fraction above 10 dB is no more than 0.5 percent.
- Amount 75 final-holdout mean GR is between 3.75 and 5.5 dB and p99 GR is no more than 9.0 dB.
- Amount 100 final-holdout mean GR is between 5.0 and 7.0 dB, p99 GR is no more than 10.0 dB, and fraction above 10 dB is no more than 2 percent.
- Every nonzero final-holdout Amount has aggregate GR ripple no more than 0.080 dB.
- Final-holdout cross-singer mean-GR standard deviation at Amount 50 is no more than 1.0 dB.
- Final-holdout mean and p95 gain reduction remain monotonic with Amount.
- Raw VocalSet audio is not persisted into CIPI artifacts.

### Rejection criteria

- No candidate passes all selection-margin gates.
- The frozen selected candidate fails any unchanged original gate on the untouched final holdout singers.
- Any required singer has fewer than two qualifying files.
- Any selection/final-holdout singer overlap occurs.
- Raw public audio is persisted into the evidence branch.

## Bounded metric snapshot

- `acceptance_met`: False
- `decision`: REVISE
- `files_per_singer`: 2
- `final_ripple_gate_db`: 0.08
- `holdout_passes`: False
- `holdout_singer_count`: 4
- `holdout_singers[0]`: f3
- `holdout_singers[1]`: f4
- `holdout_singers[2]`: m3
- `holdout_singers[3]`: m4
- `raw_audio_persisted`: False
- `selected_candidate`: None
- `selected_target100_db`: None
- `selection_ripple_margin_db`: 0.075
- `selection_singer_count`: 4
- `selection_singers[0]`: f1
- `selection_singers[1]`: f2
- `selection_singers[2]`: m1
- `selection_singers[3]`: m2

## Knowledge candidate

A speaker-disjoint selection safety margin can make a mathematically linear DesiredGR-scaling Amount control generalize across a second independent public singing corpus without relaxing the frozen Vo.Prep ripple gate.

## Reusable findings already retained

- none recorded

## Human-only gates

- Level-matched blind real-vocal listening before final Amount adoption.

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
