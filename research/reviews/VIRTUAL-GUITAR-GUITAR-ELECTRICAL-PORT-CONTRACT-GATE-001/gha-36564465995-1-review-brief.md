# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VIRTUAL-GUITAR-GUITAR-ELECTRICAL-PORT-CONTRACT-GATE-001`
- Run: `gha-36564465995-1`
- Brief revision: **1**
- Triage: `VIRTUAL-GUITAR-GUITAR-ELECTRICAL-PORT-CONTRACT-GATE-001:gha-36564465995-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is the Guitar Electrical Port a validated versioned electrical boundary rather than a design-only contract or finished-WAV interface?

## Hypothesis

Integration requires a validated source/network representation with explicit state and compatibility semantics before Reference DI or Amp loading can be trusted.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- required electrical-port capabilities are explicit
- interface contract has measured validation status
- missing fields cannot silently default

### Rejection criteria

- contract remains design-only
- source impedance or network representation is missing
- finished WAV is used as proof of loading behavior

## Bounded metric snapshot

- `acceptance_met`: False
- `checks.baseline_completed`: True
- `checks.contract_values_frozen`: False
- `checks.foundation_status`: SOURCE_EVIDENCE_FOUNDATION
- `checks.interface_contract_validated`: False
- `checks.pickup_di_research_job_completed`: True
- `checks.port_track_research_ready`: True
- `checks.product_repository_write`: False
- `checks.required_capabilities_covered`: True
- `checks.same_midi_identity_collapse_count`: 2
- `gate`: port
- `missing_evidence_or_work[0]`: validate Guitar Electrical Port contract with measured network evidence

## Knowledge candidate

none

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
