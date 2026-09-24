# 1176 / FET Feedback Compressor — Formal Research Track

## Research target
Build a source-traceable, measurable model of the 1176 family that separates feedback topology, detector/rectifier, timing, FET gain control, ratio behavior, amplifier stages, and transformer contribution.

Legacy summary: `../1176_FAMILY.md`  
Evidence ledger: `../../SOURCE_LEDGER.md`

## SOURCE_FACT
From the existing CIPI source-backed family summary:

- The 1176LN is a FET gain-reduction compressor/limiter.
- The documented topology is feedback-style.
- The gain-reduction control section uses phase-inverted paths into a full-wave rectifier network, followed by a timing/control network that drives the FET.
- Documented control ranges are approximately:
  - attack: 20 us to 800 us;
  - release: 50 ms to 1100 ms.
- Documented ratios include 4:1, 8:1, 12:1, and 20:1.

These ranges do not uniquely define a correct digital-equivalent envelope model.

## MEASURED
No CIPI-owned measurement set for a specifically identified hardware 1176 revision is registered in this formal track yet.

No stage-ablation result separating FET, amplifier, and transformer contribution is registered yet.

## INFERRED
- A generic feed-forward peak compressor plus saturation is not an adequate research proxy for the documented feedback topology.
- Static curve, rectifier/detector, timing, FET law, amplifier stages, transformer stages, and calibration should remain separable during validation.
- Revision-specific differences must be scoped rather than silently averaged together.
- Agreement between circuit-derived and measurement-identified gray-box models would materially increase confidence.

## HYPOTHESIS
A compact reusable FET-compressor pattern may eventually use:
- feedback-aware control;
- rectifier/detector behavior matched to burst/step tests;
- nonlinear FET control mapping;
- ratio-dependent loop/gain behavior;
- optional calibrated amplifier/transformer color stages.

## Candidate numerical anchors
- Attack range: ~20–800 us.
- Release range: ~50–1100 ms.
- Ratios: 4:1 / 8:1 / 12:1 / 20:1.

No exact FET law, digital detector coefficient, threshold, knee, or nonlinear transfer constant is locked yet.

## Measurement / AB plan
Required tests include:
- static transfer at every ratio;
- attack/release across control positions and GR depths;
- repeated-burst and level-dependent recovery;
- tests that distinguish feedback behavior from a generic feed-forward baseline;
- fitted FET attenuation law with residual error;
- THD/IMD vs drive and GR;
- ablation of control path, FET law, amplifier stages, and transformer stage;
- level-matched vocal AB using sharp consonants, sustained vowels, repeated transients, dense choruses, and loud phrase changes.

## Current location
Review / contradiction resolution.

## Next stage
Parameter lock after review convergence.

## Final precision status
- Evidence classes separated: yes.
- Revision scope limitation explicit: yes.
- FET/control law locked: no.
- Timing/ratio behavior measured or fitted: no.
- CIPI measurements registered: no.
- Level-matched vocal AB registered: no.
- Cubase Pro 14 VST3 validation registered: no.
- Final review complete: no.
