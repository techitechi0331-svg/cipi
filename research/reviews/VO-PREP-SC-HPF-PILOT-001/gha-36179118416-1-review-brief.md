# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-SC-HPF-PILOT-001`
- Run: `gha-36179118416-1`
- Brief revision: **1**
- Triage: `VO-PREP-SC-HPF-PILOT-001:gha-36179118416-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a simple detector-only 12 dB/oct high-pass reduce low-frequency rumble/plosive-driven gain reduction without materially under-compressing low male vowels or weakening consonant/sibilant event capture in the frozen Vo.Prep transparent compressor?

## Hypothesis

At least one cutoff among 40, 60, 70, 80, or 100 Hz will reduce synthetic rumble-driven excess GR by at least 50 percent and plosive excess GR by at least 15 percent while preserving low-male body GR within 0.30 dB, female body GR within 0.15 dB, and consonant/sibilant event GR to at least 90 percent of the OFF baseline.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Synthetic matrix is evaluated at 44.1, 48, and 96 kHz.
- Mean rumble-driven excess-GR reduction is at least 50 percent versus OFF.
- Mean plosive excess-GR reduction is at least 15 percent versus OFF.
- Mean low-male body-GR loss is no more than 0.30 dB versus OFF.
- Mean female body-GR absolute change is no more than 0.15 dB versus OFF.
- Consonant event-GR retention is at least 90 percent of OFF.
- Sibilant event-GR retention is at least 90 percent of OFF.
- Low-male body-GR delta sample-rate spread is no more than 0.10 dB.
- The selected cutoff is the lowest cutoff that passes every gate.

### Rejection criteria

- No cutoff passes every preservation and false-trigger reduction gate.
- Any candidate is non-finite or unstable across the declared sample rates.
- Passing requires relaxing a predeclared preservation gate.

## Bounded metric snapshot

- `candidate_count`: 5
- `decision`: GO_TO_REAL_VOCAL
- `raw_audio_persisted`: False
- `selected_aggregate.consonant_retention`: 0.9920443963571205
- `selected_aggregate.female_body_delta_db`: 0.00544445236416428
- `selected_aggregate.male_body_delta_db`: 0.0457614202540683
- `selected_aggregate.plosive_reduction`: 0.22150306428323516
- `selected_aggregate.proximity_body_delta_db`: -0.004121146621899996
- `selected_aggregate.rumble_reduction`: 0.7179301600637237
- `selected_aggregate.sibilant_retention`: 0.9947121399655207
- `selected_cutoff_hz`: 40
- `selected_gates.consonant_retention_ge_90pct`: True
- `selected_gates.female_body_abs_delta_le_0_15db`: True
- `selected_gates.male_body_loss_le_0_30db`: True
- `selected_gates.plosive_reduction_ge_15pct`: True
- `selected_gates.rumble_reduction_ge_50pct`: True
- `selected_gates.sample_rate_body_delta_spread_le_0_10db`: True
- `selected_gates.sibilant_retention_ge_90pct`: True

## Knowledge candidate

A low-order detector-only high-pass can reduce low-frequency false compressor drive while preserving useful vocal-body and short-event behavior in the frozen Vo.Prep compressor.

## Reusable findings already retained

- none recorded

## Human-only gates

- Public/real-vocal validation before any product HPF adoption.
- Level-matched listening before subjective naturalness claims.

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
