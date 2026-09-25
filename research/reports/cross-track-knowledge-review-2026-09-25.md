# CIPI Cross-Track Knowledge Review — 2026-09-25

## Purpose

Turn accumulated product research into reusable CIPI knowledge **without universalising product-specific numbers**.

This review does not change schemas, workers, adapters, queue semantics, product DSP, parameter defaults, confidence values or knowledge-status values. It adds a bounded synthesis layer on top of the existing evidence.

Source snapshot:
- CIPI main: `711610a4c615c62013fde6166571fed58b171f42`
- existing Knowledge Candidate records reviewed: **32**
- new cross-track candidates created: **4**
- exact numeric product constants promoted across tracks: **0**
- CONFIRMED promotions: **0**

## Promotion discipline used in this review

A broad reusable candidate is allowed only when at least one of these is true:

1. **Independent cross-track convergence**
   - the same principle is supported by at least two materially different product/research tracks;
   - support is not merely the same code or dataset rerun.

2. **Source-backed mechanism + measured implementation evidence**
   - authoritative/reference evidence establishes the mechanism;
   - at least one measured implementation constrains how it may be modeled;
   - no known contradictory evidence invalidates the generalized wording.

The following do **not** count as independent confirmation:
- rerunning the same model with another seed alone;
- reformatting or checksum-normalizing the same artifact;
- selection and holdout from one product when the proposed claim is broader than that product;
- two candidates derived from the same source code and same corpus;
- subjective preference without level matching.

## What may transfer across products

Prefer transferring:
- architectural separation;
- measurement methods;
- failure boundaries;
- detector invariance properties;
- negative results;
- validation discipline.

Do not transfer by default:
- exact thresholds;
- exact knob positions;
- exact candidate counts;
- exact attack/release values;
- exact saturation coefficients;
- exact reference-level mappings;
- exact default Amount/Color/Width values.

Those remain product calibration until independently reproduced in the new context.

---

# Cross-track candidates accepted for further promotion review

These are **not CONFIRMED**. They are newly synthesized as `INFERRED / LIKELY` because the support crosses track boundaries.

## CTK-01 — Separate detection, decision and action strength

Candidate:
`research/knowledge_candidates/CROSS-TRACK-KNOWLEDGE-001/detection-decision-action-separation.yaml`

Supporting evidence:
- Vocal Resonance: candidate discovery can retain useful recall while semantic Top-K ranking remains poor.
- MicroDouble R1/R2/R3: event recall and protection strength were initially conflated; separating them exposed the failure and enabled a bounded threshold study.
- Vo.Prep: detector confidence and applied attenuation are explicitly bounded as separate concerns.

Reusable conclusion:
- measure detector/candidate recall separately from semantic decision quality and separately again from action/attenuation strength.

Boundary:
- this does not prescribe one detector, classifier, threshold or action law.

Promotion recommendation:
- **LIKELY shared principle**.

## CTK-02 — Prefer level-normalized character features when loudness is not the target

Candidate:
`research/knowledge_candidates/CROSS-TRACK-KNOWLEDGE-001/level-normalized-character-features.yaml`

Supporting evidence:
- Vo.Prep Sibilance Guard: high-to-broad/high-to-mid ratios reached a precision-biased operating point on the current corpus.
- PeakBody: the crest trajectory reproduced to numerical precision after a -12 dB gain change in the tested vocal.
- Vo.Prep Plosive Guard: adding ratio/context information separated tested plosive cases better than an LF-energy-only rule.

Reusable conclusion:
- when the research target is spectral/transient **character**, normalized ratios are a stronger default research primitive than absolute level alone.

Boundary:
- near-silence behavior, language/singer variation and event-specific context remain separate validation problems.

Promotion recommendation:
- **LIKELY shared principle**.

## CTK-03 — Separate analog mechanisms and gate complexity by evidence

Candidate:
`research/knowledge_candidates/CROSS-TRACK-KNOWLEDGE-001/mechanism-separation-complexity-gate.yaml`

Supporting evidence:
- VL2A: generic composite tube/nonlinear approximations exposed low-level behavior defects; load-aware tube-output and transformer structure were evaluated separately.
- VL2A A-24 work: unsupported magnetic saturation/hysteresis constants were explicitly rejected as historical truth.
- Original Vocal Pre: tube, feedback and transformer contributions remain ablation targets instead of being collapsed into one "analog" block.
- LA-2A/1176 formal tracks: detector/control path, gain-control element, amplifier and transformer behavior remain separate validation concerns.

Reusable conclusion:
- reference-informed analog DSP should start with separable mechanisms and should earn extra nonlinear/memory complexity with source or measurement evidence.

Boundary:
- this is a modeling discipline, not evidence that a simpler model is always sonically preferable.

Promotion recommendation:
- **LIKELY shared principle**.

## CTK-04 — Reuse mechanisms, not calibration constants

Candidate:
`research/knowledge_candidates/CROSS-TRACK-KNOWLEDGE-001/reuse-mechanism-not-calibration-constant.yaml`

Supporting examples:
- MicroDouble activation `0.62` is a product/corpus calibration.
- Vo.Prep Amount mapping is explicitly tied to the frozen core and its validation corpus.
- Vocal Resonance `K=20` is scoped to the current candidate-discovery scaffold.
- VL2A Peak Reduction calibration was reopened when reference-level contexts were compared more strictly.
- multiple track documents already state that nominal midpoint/default mappings are product calibration rather than universal compressor constants.

Reusable conclusion:
- cross-product knowledge transfer should move the **reasoning, mechanism, metric and failure boundary** first; numeric constants must be revalidated.

Promotion recommendation:
- **LIKELY shared principle**.

---

# Existing candidates that remain product-scoped

These are useful and should remain available, but this review does not broaden them into shared constants.

## Strong measured product evidence

- `MICRODOUBLE-SIBILANCE-R3-GATE-001`
  - strong selection/holdout evidence;
  - activation `0.62` stays MicroDouble-specific.

- `MICRODOUBLE-V03-PRODUCT-GATE-001`
  - midpoint remap result stays tied to the committed product snapshot.

- `OVP-TUNING-FRONTIER-001`
  - 4 dB / 6 dB profile findings stay inside the tested Original Vocal Pre grid.

- `PEAKBODY-REV02-POLICY-001`
  - split-direction crest timing is promising but the exact timing range remains PeakBody-specific.

- `VL2A-PHASE01H-SNAPSHOT-GATE-001`
  - block-isolation method is reusable;
  - Phase 01-H transfer and its measured response remain VL2A-specific.

- Vo.Prep Macro Level / Plosive / Sibilance candidates
  - useful measured evidence;
  - exact detector thresholds, event caps and attenuation topology remain product/corpus-scoped.

- Vocal Resonance measured candidates
  - Audit-001 subgroup rates, R5 cohort results, K=20 and safe-negative ranking remain tied to the stated scaffold/cohorts.

## Why these are not broadened

A measured result can be strong **inside its declared scope** without being ready for cross-product reuse. Product maturity and knowledge generality are separate dimensions.

---

# Existing candidates that remain hypotheses / replication targets

## MicroDouble sibilance reuse precursor

`MICRODOUBLE-SIBILANCE-REUSE-001` correctly authorized a direct test rather than adoption. Later R3 evidence is stronger. Preserve the precursor as lineage; do not reinterpret it as a final detector claim.

## Vo.Prep Amount mapping

`VO-PREP-AMOUNT-MAP-001` proves useful deterministic properties in the level-domain model, but real-vocal safety/generalization and listening remain separate. Exact mapping stays product-specific.

## Vocal Resonance temporal/motion hypotheses

- R3 motion-coherence direction did not earn product promotion.
- R5 temporal morphology produced an encouraging measured cohort result but causal attribution/generalization is still under R5b falsification.
- high-F0/technique subgroup interpretations remain bounded by the follow-up audits.

No broad semantic-resonance rule is promoted in this review.

---

# Negative knowledge retained

Negative evidence is part of the reusable knowledge base.

## 1176 / Black76

Detector-drive correction alone was insufficient to recover steep high-ratio slopes against the committed supplemental target. This narrows the search but does not identify the missing hardware mechanism.

## Original Vocal Pre

The v0.1 output-transformer configuration produced an excessive LF-THD penalty under the fixed product gates. Checksum correction did not make the acoustic failure disappear.

## PeakBody

The historical crest-to-fast model is reproducible, but reproducibility does not revive a rejected product direction.

## Vocal Resonance

The earlier lip-trill-dominance hypothesis did not reproduce in Audit-001. Later motion-coherence candidates also failed to solve the semantic-ranking problem. These failures should constrain future feature design.

---

# Candidates deliberately NOT promoted broadly yet

## Bounded event duration

Existing candidate:
`VO-PREP-SYNC-001/manual-20260925-event-caps.yaml`

Reason:
- two event caps exist inside the same product family;
- no independent second product has yet demonstrated the same safeguard under comparable false-trigger conditions.

Decision:
- retain as a useful **single-track inference**;
- do not treat 120 ms, 350 ms, or "event caps are always best" as shared truth.

## Zero-crossing slope continuity / low-level THD

Existing candidate:
`VL2A-CHAT-RECOVERY-001/slope-discontinuity-low-level-thd.yaml`

Reason:
- the failure is well measured and mathematically plausible;
- current CIPI evidence is still concentrated in the historical VL2A waveshaper case.

Decision:
- retain as a strong screening hypothesis/principle;
- seek replication in another nonlinear product such as Original Vocal Pre or Density before broad promotion.

## Sibilance topology

Vo.Prep's hybrid wide/high topology is promising for compressor-prep use, but MicroDouble is now testing detector transfer rather than proving the same action topology. Detection reuse must not be mistaken for proof that the same attenuation topology transfers.

---

# Cross-track contradiction result

No destructive contradiction requiring evidence deletion was found.

The important distinctions are:

- **LA-2A and 1176 can both have program-dependent timing while using different mechanisms.**
- **A product may intentionally use fixed timing without that becoming reference-device truth.**
- **A detector can be technically strong while the downstream semantic/action layer still fails.**
- **A product-specific optimum can coexist with a different optimum in another product.**
- **Negative results narrow scope; they do not erase every reusable sub-finding.**

---

# External-validity boundary

The shared candidates above are methodological/architectural, not perceptual product claims.

They do not close:
- Japanese/Korean singing generalization;
- microphone/interface diversity;
- heavy tuning/editing chains;
- Cubase Pro 14 host validation;
- blinded level-matched preference;
- broad singer/genre coverage.

Any shared candidate that later becomes a product default must re-enter the relevant product's own measurement/listening/host gates.

---

# Recommended next evidence to strengthen shared knowledge

Priority 1:
- replicate event-duration safeguards in a second event-sensitive product.

Priority 2:
- run zero-crossing slope / low-level THD screening on another nonlinear processor.

Priority 3:
- reuse the block-isolation invariant-method from VL2A in another dynamics/reference track.

Priority 4:
- broaden normalized detector testing to Japanese/Korean singing and breathy/high-register material.

These are **research gaps**, not reasons to weaken the four current LIKELY cross-track principles.

---

# Final decision

CIPI now has enough evidence to distinguish:

1. **cross-track reusable principles**;
2. **strong but product-scoped measured findings**;
3. **hypotheses awaiting independent replication**;
4. **negative knowledge that must remain preserved**.

The four new cross-track candidates are intentionally limited to `LIKELY`.

No numerical product calibration was promoted, no existing evidence was deleted, and no human/Cubase gate was closed.
