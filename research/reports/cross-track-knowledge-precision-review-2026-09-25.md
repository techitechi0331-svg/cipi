# CIPI Cross-Track Knowledge Precision Review — 2026-09-25

## Purpose

Re-review the four `CROSS-TRACK-KNOWLEDGE-001` candidates for:
- evidence independence;
- same-source double counting;
- comparative-vs-invariance confusion;
- source fact vs product calibration confusion;
- scope inflation.

This pass does not overwrite the first synthesis. It creates a preferred precision-reviewed wording under:
`research/knowledge_candidates/CROSS-TRACK-KNOWLEDGE-REVIEW-002/`.

No DSP, schema, workflow, queue or knowledge-status value is changed.

## Overall result

| Candidate | First-pass issue | Precision result |
|---|---|---|
| CTK-01 Detection / decision / action | wording implied all adaptive processors have all three stages | **KEEP LIKELY**, conditional wording |
| CTK-02 Level-normalized features | wording implied cross-track superiority over absolute energy | **KEEP LIKELY**, remove superiority claim |
| CTK-03 Mechanism separation | mixed direct measurement with source/design support | **KEEP LIKELY**, state evidence asymmetry |
| CTK-04 Reuse mechanism not constants | could be read as applying to hardware/spec constants | **KEEP LIKELY**, limit rule to empirical product calibration |

No candidate is raised to PROVISIONAL or CONFIRMED.

---

## CTK-01 — Detection / decision / action separation

### Independent evidence check

Primary support path 1 — Vocal Resonance:
- candidate discovery and semantic ranking are distinct measured stages;
- high candidate recall did not guarantee strong semantic Top-K ranking.

Primary support path 2 — MicroDouble:
- earlier work conflated event detection/recall with processing/protection strength;
- later R3 explicitly separated detector activation from protection strength and preserved the negative lineage.

Secondary support — Vo.Prep:
- event confidence and bounded attenuation are architecturally separate;
- this supports the design pattern but is not counted as a fully independent falsification path.

### Precision finding

The principle is well supported, but the original wording used "semantic decision" too generally.

A compressor, gate or simple event controller may not contain a semantic ranking stage.

### Preferred wording

When a pipeline **actually contains** separable detection/candidate-generation, decision/ranking and action stages, measure them independently.

### Decision

**KEEP LIKELY.**

Reason:
- two materially different research tracks demonstrate different forms of upstream-success/downstream-failure;
- no exact detector topology or threshold is generalized.

---

## CTK-02 — Level-normalized character features

### Independent evidence check

Path 1 — Vo.Prep:
- level-normalized sibilance ratios reached a useful operating point;
- plosive ratio/context features outperformed an LF-energy-only rule on the declared stress cases.

Path 2 — PeakBody:
- the measured crest trajectory was numerically invariant under a -12 dB global gain change for the tested vocal.

### Precision problem

PeakBody does **not** provide a direct comparison showing that normalized features outperform absolute-energy features.

It provides invariance evidence.

Therefore the first-pass sentence:

> "a stronger reusable starting point than absolute energy alone"

was broader than the cross-track comparative evidence.

### Preferred wording

Level-normalized features can provide useful gain-invariant cues when absolute loudness is not the target, and should be tested alongside absolute features.

Whether they outperform absolute features remains task-specific.

### Decision

**KEEP LIKELY with narrowed claim.**

Why not HYPOTHESIS:
- gain invariance is independently supported outside Vo.Prep;
- Vo.Prep supplies direct event-specific comparative evidence.

Why not PROVISIONAL:
- no broad cross-language/cross-event benchmark establishes superiority.

---

## CTK-03 — Mechanism separation and complexity gate

### Evidence independence check

Direct measured support:
- VL2A nonlinear-model work exposed failure from an overly generic nonlinear approximation and benefited from separating line-amplifier/device/load/transformer concerns.

Source-backed/model-design support:
- LA-2A formal work separates optical control, tube amplifier and transformer contribution;
- 1176 formal work separates detector/control loop, FET law, amplifier and transformer behavior;
- Original Vocal Pre explicitly retains tube/feedback/transformer ablation rather than treating "analog color" as one block.

### Precision problem

The first-pass report could make the evidence look equally measured across all tracks.

It is not.

The strongest direct measured support is currently VL2A. The remaining tracks provide authoritative topology constraints and explicit validation designs.

### Preferred wording

Where source evidence identifies materially distinct mechanisms, keep them separable enough for ablation. Add extra nonlinearity/memory only when source or reproducible measurement justifies it over a simpler baseline.

### Decision

**KEEP LIKELY as a modeling/validation discipline.**

Do not reinterpret this as:
- simple models always sound better;
- every transformer needs a nonlinear model;
- VL2A findings prove the 610/1176/LA-2A implementations.

---

## CTK-04 — Transfer methods, not product calibration

### Evidence independence check

Multiple independent product tracks show calibration-specific values:
- MicroDouble detector activation;
- Vo.Prep Amount mapping;
- Vocal Resonance K candidate budget;
- VL2A Peak Reduction mapping/reference-level context.

All are intentionally scoped to their product/model/dataset context.

### Precision problem

The first-pass wording used "numeric calibrations" broadly enough that it could accidentally include:
- manufacturer-specified attack ranges;
- circuit component values;
- physical constants;
- standards-defined values.

Those are SOURCE_FACT or standards evidence, not empirical product tuning.

### Preferred wording

Do not transfer **empirically tuned product constants** by default.

Transfer:
- mechanisms;
- measurement methods;
- failure boundaries.

Source-defined physical/specification constants may transfer as SOURCE_FACT, but their mapping into a new digital product still needs explicit context.

### Decision

**KEEP LIKELY.**

This is a research-discipline principle, not a claim that numeric information is inherently non-transferable.

---

## Double-counting audit

The following are explicitly **not** treated as independent evidence:
- multiple candidates derived from the same Vo.Prep run;
- R1/R2/R3 iterations of the same MicroDouble transfer study as three independent products;
- repeated Vocal Resonance audits using the same underlying scaffold as independent confirmation of every broader claim;
- checksum or seed replications as new conceptual evidence.

They remain valuable for reproducibility and falsification, but not for inflating cross-track support counts.

---

## Promotion result

Preferred current cross-track candidates:

1. CTK-01 — **INFERRED / LIKELY**
2. CTK-02 — **INFERRED / LIKELY**, narrowed
3. CTK-03 — **INFERRED / LIKELY**, evidence asymmetry explicit
4. CTK-04 — **INFERRED / LIKELY**, product-calibration scope explicit

No:
- PROVISIONAL promotion;
- CONFIRMED promotion;
- product numeric constant promotion;
- human-listening closure;
- Cubase closure.

---

## Strongest next falsification tests

### CTK-01
Try a second adaptive processor where detection is intentionally excellent but action calibration is varied independently. Confirm whether detector metrics alone fail to predict product behavior.

### CTK-02
Run a matched absolute-feature vs normalized-feature comparison on a second product/dataset, including near-silence and large gain offsets.

### CTK-03
Perform the same mechanism-ablation discipline on Original Vocal Pre or another nonlinear product and quantify residual error versus model complexity.

### CTK-04
Take one successful product calibration and deliberately transfer the exact number into a second product, then compare against a locally re-tuned value. This is the cleanest direct falsification of the "do not transfer tuning constants" rule.

---

## Final precision check

- Independent support inflated by same-source reruns: **no**
- Comparative evidence confused with invariance evidence: **corrected**
- Product tuning confused with hardware/source fact: **corrected**
- Negative evidence removed: **no**
- Exact product constants generalized: **no**
- Cross-track claims exceed LIKELY: **no**
- Existing worker/chat compatibility affected: **no**

## Decision

The first cross-track synthesis was directionally sound but two claims were too broad.

The precision-reviewed wording in `CROSS-TRACK-KNOWLEDGE-REVIEW-002` is the preferred current interpretation.
