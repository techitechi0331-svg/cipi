# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VIRTUAL-GUITAR-PICKUP-DI-IMPLEMENTATION-RESEARCH-001`
- Run: `gha-36520787383-1`
- Brief revision: **1**
- Triage: `VIRTUAL-GUITAR-PICKUP-DI-IMPLEMENTATION-RESEARCH-001:gha-36520787383-1:triage-v1`
- Route: **CONTINUE_RESEARCH**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

What minimum physical/electrical Pickup/DI architecture can explain the baseline string/fret identity and pickup-stage gaps while preserving explicit uncertainty?

## Hypothesis

Separating string-state observation, magnetic pickup behavior, passive R/L/C network, controls, cable load, output impedance and guitar jack will provide a falsifiable PICKUP_DI candidate without disguising RAW-string model error.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- reuse existing CIPI pickup/electrical/cable/output-port evidence before new research
- produce an explicit RAW_PHYSICAL_STRING to PICKUP_DI stage contract
- no RAW-to-DI fake substitution
- no static EQ-only adoption without falsification against electrical alternatives
- no product repository write
- prepare matched Reference DI validation as a downstream gate

### Rejection criteria

- candidate collapses string/fret identity to MIDI pitch only
- candidate uses RAW output relabelled as PICKUP_DI
- candidate requires Amp/Cab/Mic coloration to hide upstream defects
- candidate introduces unsupported electrical constants without evidence classification
- candidate performs product repository writes or automatic product adoption

## Bounded metric snapshot

- `candidate_model_counts.amp_input`: 3
- `candidate_model_counts.cable`: 3
- `candidate_model_counts.magnetic_transduction`: 2
- `candidate_model_counts.pickup_electrical`: 3
- `candidate_model_counts.pickup_observation`: 2
- `classification_counts.HYPOTHESIS`: 3
- `classification_counts.INFERRED`: 3
- `classification_counts.MEASURED`: 1
- `classification_counts.REJECTED`: 7
- `classification_counts.SOURCE_FACT`: 4
- `evidence_gates.all_model_boundaries_present`: True
- `evidence_gates.automatic_knowledge_promotion_off`: True
- `evidence_gates.automatic_product_decision_off`: True
- `evidence_gates.higher_order_counter_hypothesis_present`: True
- `evidence_gates.higher_order_model_not_predeclared_required`: True
- `evidence_gates.low_order_model_not_predeclared_final`: True
- `evidence_gates.manufacturer_hss_source_present`: True
- `evidence_gates.manufacturer_sss_source_present`: True
- `evidence_gates.minimum_tier1_sources`: True
- `evidence_gates.minimum_tier2_sources`: True
- `evidence_gates.peer_reviewed_cable_loading_source_present`: True
- `evidence_gates.peer_reviewed_pickup_model_source_present`: True
- `evidence_gates.product_repository_write_off`: True
- `evidence_gates.reference_di_is_rejected_as_upstream_prerequisite`: True
- `evidence_gates.shortcut_rejections_complete`: True
- `foundation_ready_for_measurement_design`: True
- `model_adopted`: False
- `pickup_fidelity_claim`: False
- `product_repository_write`: False
- `reference_di_converged`: False
- `source_count`: 5
- `tier1_source_count`: 2

## Knowledge candidate

none

## Reusable findings already retained

- none recorded

## Human-only gates

- none

## Allowed review actions

ITERATE, ARCHIVE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
