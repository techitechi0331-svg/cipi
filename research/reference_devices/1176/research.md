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


## Imported Black76 Rev E product evidence

Product-specific measurements and rejected hypotheses are recorded in:
`BLACK76_REV_E_IMPORT.md`

Key imported evidence now available to this formal track:

- a working product Gain Structure calibration with explicit hardware-honesty limits;
- supplemental LN-era control-taper measurements and interpolation-method comparison;
- corrected ratio-threshold ordering from a detector-drive isolation test;
- negative evidence that detector drive alone does not repair deep-ratio collapse;
- bounded optimizer evidence that detector gain plus detector bias alone is insufficient for the target high-ratio slopes;
- real-vocal numerical continuity checks without storing raw vocal audio in CIPI.

These imports improve the evidence base but do not resolve the blocker of missing directly identified vintage Rev-E hardware transfer measurements.

### Scope boundary for Black76 P2-A evidence — 2026-09-25 content audit

The imported P2-A result is a **product-specific falsification result against the committed supplemental LN-era target**, not a direct hardware-identification result for a vintage Rev-E unit.

What the evidence supports:
- detector-drive correction can repair the tested threshold ordering in the Black76 model;
- detector drive alone did not recover the required deep high-ratio slopes against that supplemental target;
- detector-gain plus detector-bias-only optimization was also insufficient in that bounded model study.

What it does **not** support:
- that the supplemental target is a complete or uniquely correct Rev-E hardware truth;
- that one particular missing FET/control-loop mechanism has already been identified;
- that the measured Black76 static curve can be generalized to all 1176 revisions.

The formal 1176 track therefore remains in contradiction-resolution/review until directly identified revision measurements or stronger independent evidence constrain the FET law, rectifier/control loop, ratio network and revision-specific amplifier behavior.

## 2026-09-25 timing/revision source-fact spot check

Current UA documentation reinforces two scope constraints that are easy to lose in a simplified digital model:

- nominal control ranges remain approximately 20..800 us attack and 50..1100 ms release for the standard 1176LN family;
- UA explicitly describes release as materially program dependent, with fast-release, slow-release and transition-time behavior, and notes revision/model differences in the slow-release/transition behavior;
- ratio selection and multi-button modes change more than a single ideal static-ratio number; UA documents altered bias/timing behavior in All-Button operation.

Implication:
- a fixed one-pole release should remain a simple baseline, not be promoted as the final 1176 reference model;
- ratio/revision validation must include timing/control-loop behavior rather than only static I/O slope.

References:
- https://help.uaudio.com/hc/en-us/articles/4419447352980-UA-1176-Classic-Limiter-Collection-Manual
- https://media.uaudio.com/assetlibrary/1/1/1176ln_manual.pdf

