# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-AMOUNT-R5-SOFT-RANGE-001`
- Run: `gha-36201243756-1`
- Brief revision: **1**
- Triage: `VO-PREP-AMOUNT-R5-SOFT-RANGE-001:gha-36201243756-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a simple smooth post-ballistics GR Range repair the R4 high-Amount ripple failure without changing the frozen Vo.Prep detector, 1.5:1/18 dB curve, 8/70 ms ballistics, or explicit Learn-time Threshold solve?

## Hypothesis

At least one ceiling among 10, 9, or 8 dB with a 6 dB unity region will pass all original Amount gates and the 0.075 dB selection ripple ceiling on f7/f8/m7/m8, improve Amount-100 ripple by at least 15 percent versus the no-Range R4 baseline, preserve gain invariance, and then pass the unchanged 0.080 dB final ripple gate on fresh f9/m9/m10/m11 holdout singers.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- Selection uses only f7, f8, m7 and m8 with two qualifying files per singer.
- Fresh holdout uses only f9, m9, m10 and m11 with two qualifying files per singer.
- Holdout audio is not streamed or decoded until a candidate passes every selection, complexity and gain-invariance gate.
- Amount 0 is exact bypass.
- Amount 25 mean GR is 0.75 to 2.25 dB and p95 is no more than 4 dB.
- Amount 50 mean GR is 2.5 to 3.75 dB, p95 is no more than 6 dB and fraction above 10 dB is no more than 0.5 percent.
- Amount 75 mean GR is 3.75 to 5.5 dB and p99 is no more than 9 dB.
- Amount 100 mean GR is 5.0 to 7.0 dB, p99 is no more than 10 dB and fraction above 10 dB is no more than 2 percent.
- Selection aggregate ripple is no more than 0.075 dB at every nonzero Amount.
- Final holdout aggregate ripple is no more than 0.080 dB at every nonzero Amount.
- Cross-singer mean-GR standard deviation at Amount 50 is no more than 1.0 dB.
- Mean and p95 GR are monotonic with Amount.
- Selection mapping RMSE is no more than 0.50 dB.
- Final holdout mapping RMSE is no more than 0.65 dB.
- Learn-solver residual is no more than 0.02 dB.
- Selected candidate improves Amount-100 ripple by at least 15 percent versus R4 no-Range baseline.
- Gain-invariance Threshold and post-lock mean-GR errors are each no more than 0.005 dB across +/-12 dB.
- Among passing candidates choose the highest ceiling, preserving the least intrusive Range.
- Raw VocalSet audio is not persisted into CIPI artifacts.

### Rejection criteria

- No Range candidate passes every selection and complexity gate.
- Passing requires relaxing a predeclared gate.
- Fresh holdout fails any unchanged product gate.
- Holdout data is accessed before selection is frozen.
- Raw public audio is persisted.

## Bounded metric snapshot

- `acceptance_met`: False
- `baseline_amount100_ripple_db`: 0.08797198246318512
- `candidate_summary[0].amount100_ripple_db`: 0.08848596636123582
- `candidate_summary[0].ceiling_db`: 10.0
- `candidate_summary[0].id`: soft_range_start6_ceiling10
- `candidate_summary[0].mapping_rmse_db`: 0.5184546116982374
- `candidate_summary[0].passes_selection`: False
- `candidate_summary[0].ripple_improvement_ratio`: -0.005842586283261175
- `candidate_summary[1].amount100_ripple_db`: 0.08883704777112217
- `candidate_summary[1].ceiling_db`: 9.0
- `candidate_summary[1].id`: soft_range_start6_ceiling9
- `candidate_summary[1].mapping_rmse_db`: 0.5101827911389013
- `candidate_summary[1].passes_selection`: False
- `candidate_summary[1].ripple_improvement_ratio`: -0.009833418364751045
- `candidate_summary[2].amount100_ripple_db`: 0.08966973300731865
- `candidate_summary[2].ceiling_db`: 8.0
- `candidate_summary[2].id`: soft_range_start6_ceiling8
- `candidate_summary[2].mapping_rmse_db`: 0.4926789902935472
- `candidate_summary[2].passes_selection`: False
- `candidate_summary[2].ripple_improvement_ratio`: -0.01929876418147125
- `decision`: REVISE
- `holdout_accessed`: False
- `holdout_amount100_ripple_db`: None
- `holdout_passes`: False
- `holdout_singers[0]`: f9
- `holdout_singers[1]`: m9
- `holdout_singers[2]`: m10
- `holdout_singers[3]`: m11
- `range_start_db`: 6.0
- `raw_audio_persisted`: False
- `selected_candidate`: None
- `selected_ceiling_db`: None

## Knowledge candidate

A smooth high-GR Range may repair high-Amount time-domain ripple without reopening a validated compressor core.

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
