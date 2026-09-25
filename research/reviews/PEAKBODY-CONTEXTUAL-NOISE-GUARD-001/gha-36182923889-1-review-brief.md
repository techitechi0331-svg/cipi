# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `PEAKBODY-CONTEXTUAL-NOISE-GUARD-001`
- Run: `gha-36182923889-1`
- Brief revision: **1**
- Triage: `PEAKBODY-CONTEXTUAL-NOISE-GUARD-001:gha-36182923889-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can replacing proportional periodicity discount with a strong-periodicity veto improve PeakBody noise-like rejection without harming bright/noisy voiced or plosive preservation, and does adding Vo.Prep contextual sibilance probability justify its extra complexity?

## Hypothesis

The simple strong-periodicity veto will satisfy the locked synthetic safety gates; contextual sibilance evidence will only be retained if it adds at least a meaningful extra improvement without harming another hard gate.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- at least one candidate satisfies every locked synthetic hard gate
- standard voiced retention minimum is at least 0.90
- bright/startup voiced retention minimum is at least 0.95
- 6 dB SNR noisy-voiced retention minimum is at least 0.90
- sibilant/breath/long-S false-preservation maximum is no more than 0.25
- plosive retention minimum is at least 0.85
- steady-vowel mean transient-factor delta is no more than 0.03
- all outputs are finite

### Rejection criteria

- neither simple_veto nor context_veto satisfies every locked synthetic hard gate

## Bounded metric snapshot

- `context_incremental_noise_improvement`: 0.000944822373393802
- `context_veto.acceptance_met`: False
- `context_veto.all_finite`: True
- `context_veto.bright_high_retention_min`: 1.0
- `context_veto.context_probability_bright_max`: 0.9334715682989068
- `context_veto.context_probability_noise_max`: 0.9492583155957172
- `context_veto.noise_false_preserve_ratio_max`: 0.0
- `context_veto.noisy_voiced_retention_min`: 1.0
- `context_veto.plosive_retention_min`: 0.04541666666666667
- `context_veto.standard_voiced_retention_min`: 1.0
- `context_veto.steady_mean_t_delta_max`: 0.0
- `context_veto.triggered_criteria[0]`: plosive retention below 0.85
- `simple_veto.acceptance_met`: False
- `simple_veto.all_finite`: True
- `simple_veto.bright_high_retention_min`: 1.0
- `simple_veto.context_probability_bright_max`: 0.9334715682989068
- `simple_veto.context_probability_noise_max`: 0.9492583155957172
- `simple_veto.noise_false_preserve_ratio_max`: 0.000944822373393802
- `simple_veto.noisy_voiced_retention_min`: 1.0
- `simple_veto.plosive_retention_min`: 0.05458333333333333
- `simple_veto.standard_voiced_retention_min`: 1.0
- `simple_veto.steady_mean_t_delta_max`: 0.0
- `simple_veto.triggered_criteria[0]`: plosive retention below 0.85

## Knowledge candidate

A strong-periodicity veto may be safer than proportional weak-periodicity protection for PeakBody; contextual sibilance evidence must beat the simple veto enough to justify complexity.

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
