# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R13-ACTION-EQUIV-001`
- Run: `gha-44724301511-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R13-ACTION-EQUIV-001:gha-44724301511-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does exact injected-target Top-K materially overstate the candidate-frequency accuracy needed for a narrow resonance-suppression action?

## Hypothesis

Across both predeclared seeds, static Top-5 candidates will produce action-equivalent target attenuation substantially more often than they exactly contain the injected target: at Q=12 a fixed -2 dB candidate-centered cut will yield >=1 dB target attenuation in at least 70 percent of generator-hit cases, exceed exact Top-5 hit rate by at least 20 percentage points, preserve at least 70 percent action-equivalent coverage on strong-effect cases, and achieve at least 60 percent median attenuation relative to the nearest-candidate oracle. Q=8 and Q=20 must each retain at least a 10-point action-equivalence gain over exact hit rate.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- for each seed at static Top-5 Q=12: action-equivalent rate >= 0.70
- for each seed at static Top-5 Q=12: action-equivalent minus exact hit >= 0.20
- for each seed at static Top-5 Q=12: strong action-equivalent rate >= 0.70
- for each seed at static Top-5 Q=12: median oracle-relative attenuation >= 0.60
- for each seed at static Top-5 Q=8: action-equivalent minus exact hit >= 0.10
- for each seed at static Top-5 Q=20: action-equivalent minus exact hit >= 0.10

### Rejection criteria

- any seed fails any primary or Q-sensitivity criterion

## Bounded metric snapshot

- `action_equivalent_threshold_db`: 1.0
- `cut_db`: -2.0
- `diagnostic_gate.accepted`: False
- `diagnostic_gate.criteria.20261003.action_equivalent_rate_gte_0_70`: False
- `diagnostic_gate.criteria.20261003.action_minus_exact_gte_0_20`: False
- `diagnostic_gate.criteria.20261003.median_oracle_relative_attenuation_gte_0_60`: False
- `diagnostic_gate.criteria.20261003.q20_action_gain_gte_0_10`: False
- `diagnostic_gate.criteria.20261003.q8_action_gain_gte_0_10`: False
- `diagnostic_gate.criteria.20261003.strong_action_equivalent_rate_gte_0_70`: False
- `diagnostic_gate.criteria.20261013.action_equivalent_rate_gte_0_70`: False
- `diagnostic_gate.criteria.20261013.action_minus_exact_gte_0_20`: False
- `diagnostic_gate.criteria.20261013.median_oracle_relative_attenuation_gte_0_60`: False
- `diagnostic_gate.criteria.20261013.q20_action_gain_gte_0_10`: False
- `diagnostic_gate.criteria.20261013.q8_action_gain_gte_0_10`: False
- `diagnostic_gate.criteria.20261013.strong_action_equivalent_rate_gte_0_70`: False
- `diagnostic_gate.meaning`: Whether exact causal-target Top-K materially understates the frequency-placement utility of the selected candidate set. This does not authorize a suppressor implementation.
- `diagnostic_gate.route`: EXACT_RANKING_REMAINS_ACTION_RELEVANT
- `experiment`: VOCAL_RESONANCE_R13_ACTION_EQUIVALENCE
- `per_seed.20261003.prominence.1.12.action_equivalent_rate`: 0.0
- `per_seed.20261003.prominence.1.12.action_minus_exact`: -0.03333333333333333
- `per_seed.20261003.prominence.1.12.exact_hit_rate`: 0.03333333333333333
- `per_seed.20261003.prominence.1.12.median_action_attenuation_db`: 0.0006606452091465812
- `per_seed.20261003.prominence.1.12.median_oracle_relative_attenuation`: 0.0007764701962976182
- `per_seed.20261003.prominence.1.12.n_cases`: 30
- `per_seed.20261003.prominence.1.12.strong_action_equivalent_rate`: 0.0
- `per_seed.20261003.prominence.1.12.strong_n`: 11
- `per_seed.20261003.prominence.1.20.action_equivalent_rate`: 0.0
- `per_seed.20261003.prominence.1.20.action_minus_exact`: -0.03333333333333333
- `per_seed.20261003.prominence.1.20.exact_hit_rate`: 0.03333333333333333
- `per_seed.20261003.prominence.1.20.median_action_attenuation_db`: 0.0002378860125380062
- `per_seed.20261003.prominence.1.20.median_oracle_relative_attenuation`: 0.000362598329628784
- `per_seed.20261003.prominence.1.20.n_cases`: 30

## Knowledge candidate

Exact candidate-label Top-K may understate the practical frequency-placement utility of a resonance suppressor when nearby candidates produce equivalent narrow-band attenuation at the causal target.

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
