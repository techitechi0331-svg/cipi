# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-SC-HPF-REAL-001`
- Run: `gha-36201657171-1`
- Brief revision: **1**
- Triage: `VO-PREP-SC-HPF-REAL-001:gha-36201657171-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the synthetic-pilot winner, a detector-only 40 Hz second-order high-pass, reduce low-frequency false compressor drive on real singing vocals without materially changing clean-vocal compression?

## Hypothesis

On real VocalSet vocals, 40 Hz HPF will preserve clean mean/p95/ripple behavior within tight bounds, reduce added 30 Hz rumble-driven excess GR by at least 50 percent and added low-frequency plosive excess GR by at least 15 percent, first on f1/f2/m1/m2 and then on untouched confirmation f3/f4/m3/m4.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Candidate remains fixed at 40 Hz / second order; no cutoff reselection occurs on real vocals.
- Validation uses f1, f2, m1 and m2 with two qualifying files per singer.
- Confirmation uses f3, f4, m3 and m4 with two qualifying files per singer.
- Confirmation audio is not streamed or decoded until every validation gate passes.
- Per-file clean OFF threshold is calibrated to 3.0 dB mean GR before comparing OFF versus HPF, isolating detector behavior from unresolved Amount mapping.
- Mean absolute clean-vocal mean-GR delta is no more than 0.15 dB.
- Mean absolute clean-vocal p95-GR delta is no more than 0.25 dB.
- Mean absolute clean-vocal GR-ripple delta is no more than 0.015 dB.
- Male clean-vocal mean-GR absolute delta is no more than 0.20 dB.
- Mean controlled-rumble excess-GR reduction is at least 50 percent.
- At least 75 percent of controlled-rumble cases show positive excess-GR reduction.
- Mean controlled-plosive excess-GR reduction is at least 15 percent.
- At least 75 percent of controlled-plosive cases show positive excess-GR reduction.
- Clean-threshold calibration residual is no more than 0.02 dB.
- The confirmation cohort passes the same unchanged gates.
- Raw public audio is not persisted into CIPI artifacts.

### Rejection criteria

- Validation fails any clean-preservation or LF-stress benefit gate.
- Confirmation fails any unchanged gate.
- Confirmation audio is accessed before validation passes.
- Passing requires changing the candidate cutoff or relaxing a criterion.
- Raw public audio is persisted.

## Bounded metric snapshot

- `acceptance_met`: True
- `candidate_hpf_hz`: 40.0
- `confirmation_accessed`: True
- `confirmation_aggregate.clean_abs_mean_delta_db`: 0.0041768211447698045
- `confirmation_aggregate.clean_abs_p95_delta_db`: 0.0025319484806010095
- `confirmation_aggregate.clean_abs_ripple_delta_db`: 0.00013960896953969847
- `confirmation_aggregate.file_count`: 8
- `confirmation_aggregate.male_clean_abs_mean_delta_db`: 0.0035907352824853245
- `confirmation_aggregate.plosive_positive_fraction`: 1.0
- `confirmation_aggregate.plosive_reduction_mean`: 0.20211374555654038
- `confirmation_aggregate.rumble_positive_fraction`: 1.0
- `confirmation_aggregate.rumble_reduction_mean`: 0.737451385518135
- `confirmation_aggregate.solver_max_residual_db`: 5.58192105293287e-06
- `confirmation_passes`: True
- `confirmation_singers[0]`: f3
- `confirmation_singers[1]`: f4
- `confirmation_singers[2]`: m3
- `confirmation_singers[3]`: m4
- `decision`: GO_TO_BLIND
- `raw_audio_persisted`: False
- `validation_aggregate.clean_abs_mean_delta_db`: 0.005159873647465674
- `validation_aggregate.clean_abs_p95_delta_db`: 0.005970168204070481
- `validation_aggregate.clean_abs_ripple_delta_db`: 7.031695051045242e-05
- `validation_aggregate.file_count`: 8
- `validation_aggregate.male_clean_abs_mean_delta_db`: 0.006825389634820822
- `validation_aggregate.plosive_positive_fraction`: 1.0
- `validation_aggregate.plosive_reduction_mean`: 0.17034021959672924
- `validation_aggregate.rumble_positive_fraction`: 1.0
- `validation_aggregate.rumble_reduction_mean`: 0.7351043887229355
- `validation_aggregate.solver_max_residual_db`: 4.367938575722263e-06
- `validation_passes`: True
- `validation_singers[0]`: f1

## Knowledge candidate

The 40 Hz detector-only HPF selected synthetically may reduce LF false drive on real vocals while preserving clean-vocal compression.

## Reusable findings already retained

- none recorded

## Human-only gates

- Level-matched real-vocal listening before product adoption.

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
