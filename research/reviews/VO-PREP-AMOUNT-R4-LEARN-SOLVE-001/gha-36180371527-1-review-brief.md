# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-AMOUNT-R4-LEARN-SOLVE-001`
- Run: `gha-36180371527-1`
- Brief revision: **1**
- Triage: `VO-PREP-AMOUNT-R4-LEARN-SOLVE-001:gha-36180371527-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a one-time Threshold solved only from the explicit four-second Learn buffer make Vo.Prep Amount intensity transfer across fresh singers more robustly than the rejected R3 fixed relative-offset baseline, without adding continuous auto-threshold behavior or changing the frozen compressor core?

## Hypothesis

A Learn-time solver that chooses one locked Threshold so active Learn ActualGR mean is 5.5 dB will pass the original Amount safety gates on fresh VocalSet selection and holdout singers, materially improve target-intensity mapping relative to the R3 fixed-offset baseline, and preserve exact input-gain invariance while leaving normal-playback DSP unchanged.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- The compressor core remains frozen at Slow RMS 25 ms, instantaneous Fast peak, max(Slow, Fast-6 dB) fusion, 1.5:1 ratio, 18 dB knee, 8 ms attack and 70 ms release.
- Learn uses only the first four seconds of the selected excerpt; Learn activity is derived only from that four-second buffer and no post-Learn sample participates in Threshold calibration.
- Threshold is fixed after Learn; no continuous or hidden auto-threshold behavior is introduced.
- Selection uses exactly f5, f6, m5 and m6, with two qualifying VocalSet files per singer.
- Holdout uses exactly f7, f8, m7 and m8, with two qualifying VocalSet files per singer.
- No singer appears in both selection and holdout.
- Candidate selection passes the unchanged Amount safety gates, except that the selection ripple ceiling is tightened from 0.080 dB to 0.075 dB.
- Candidate selection Amount-mean mapping RMSE versus the predeclared 5.5 dB linear target is no more than 0.50 dB.
- Candidate selection cross-singer mean-GR standard deviation at Amount 50 is no more than 0.75 dB.
- Learn solver maximum residual is no more than 0.02 dB.
- Input-gain stress at -12, -6, 0, +6 and +12 dB has maximum Threshold-shift error no more than 0.005 dB and maximum post-lock mean-GR error no more than 0.005 dB.
- Complexity is justified only if the R3 baseline fails a selection gate or the candidate reduces selection mapping RMSE to no more than 70 percent of the baseline RMSE.
- Holdout is opened only after all selection and complexity gates pass.
- On holdout, Amount 0 produces exact zero gain reduction.
- On holdout, Amount 25 mean GR is between 0.75 and 2.25 dB and p95 GR is no more than 4.0 dB.
- On holdout, Amount 50 mean GR is between 2.5 and 3.75 dB, p95 GR is no more than 6.0 dB, and fraction above 10 dB is no more than 0.5 percent.
- On holdout, Amount 75 mean GR is between 3.75 and 5.5 dB and p99 GR is no more than 9.0 dB.
- On holdout, Amount 100 mean GR is between 5.0 and 7.0 dB, p99 GR is no more than 10.0 dB, and fraction above 10 dB is no more than 2 percent.
- Every nonzero holdout Amount has aggregate GR ripple no more than 0.080 dB.
- Holdout cross-singer mean-GR standard deviation at Amount 50 is no more than 1.0 dB.
- Holdout mean and p95 gain reduction remain monotonic with Amount.
- Holdout Amount-mean mapping RMSE versus the predeclared 5.5 dB linear target is no more than 0.65 dB.
- Holdout Learn solver maximum residual is no more than 0.02 dB.
- Raw VocalSet audio is not persisted in CIPI artifacts.
- A passing result authorizes a separate red-team only; it does not adopt the product mapping.

### Rejection criteria

- The candidate fails any selection gate.
- The Learn-time solver fails the declared residual or input-gain-invariance gates.
- The complexity-justification gate fails against the R3 simple baseline.
- The frozen candidate fails any holdout gate.
- Any required singer has fewer than two qualifying files.
- Any selection/holdout singer overlap occurs.
- Any post-Learn sample influences Learn-time Threshold calibration.
- Raw public audio is persisted into the evidence branch.
- Passing requires relaxing a predeclared gate.

## Bounded metric snapshot

- `acceptance_met`: False
- `baseline_selection_mapping_rmse_db`: 0.03139874270948164
- `decision`: REVISE
- `files_per_singer`: 2
- `gain_invariance_max_gr_error_db`: 2.0173601008366404e-05
- `gain_invariance_max_threshold_error_db`: 6.103515625e-05
- `holdout_mapping_rmse_db`: None
- `holdout_opened`: True
- `holdout_passes`: False
- `holdout_singers[0]`: f7
- `holdout_singers[1]`: f8
- `holdout_singers[2]`: m7
- `holdout_singers[3]`: m8
- `learn_target_actual_mean_gr_db`: 5.5
- `raw_audio_persisted`: False
- `selection_mapping_rmse_db`: 0.04436084731567598
- `selection_passes`: False
- `selection_relative_threshold_std_db`: 0.8468102804338035
- `selection_singers[0]`: f5
- `selection_singers[1]`: f6
- `selection_singers[2]`: m5
- `selection_singers[3]`: m6
- `selection_solver_max_residual_db`: 2.21645694198358e-05

## Knowledge candidate

A one-time Threshold solved from an explicit four-second Learn buffer can make a linear one-knob Amount control more corpus-robust than a fixed relative Threshold offset while leaving normal-playback compressor DSP unchanged.

## Reusable findings already retained

- none recorded

## Human-only gates

- Level-matched blind real-vocal listening before final Amount adoption.
- Cubase Pro 14 host validation before product release.

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
