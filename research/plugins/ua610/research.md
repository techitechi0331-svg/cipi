# 610 Research -> Original Vocal Preamp Formal Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/610
- Research origin: Universal Audio 610-B / 2-610 and related 610-family hardware. Current UA 2-610 specifications list one 12AX7A and one 12AT7 per channel; UA service documentation also records 6072/12AT7 use across specific 610-family units/eras. Treat these as hardware-specific tube-complement facts rather than one universal 610 tube identity. Transformer coupling, negative feedback and class-A tube behavior remain reference mechanisms, not proof of clone identity.
- The historical 610 gray-box work is preserved as evidence and baseline material.

## Purpose

This track is no longer gated on proving a hardware-identical 610 clone.

The current goal is a **reference-informed original vocal preamp**:
- extract reusable tube / transformer / feedback knowledge from the 610 research;
- redesign the behavior for singing-vocal usefulness;
- validate the result numerically and with level-matched real-vocal listening;
- keep claims evidence-aware and do not imply hardware identity.

## Direction change

Previous:
610 research -> public circuit/spec evidence -> gray-box model -> hardware Golden Dataset -> clone-fidelity closure.

Current:
610 research -> reusable nonlinear/feedback/transformer knowledge -> original vocal-specific DSP -> measurement -> real-vocal A/B -> revision -> Windows/Cubase validation -> final review.

A reference-hardware Golden Dataset remains useful for historical 610-fidelity research, but it is **not a completion blocker** for the original product.

## Evidence carried forward

- Repository separates confirmed, supported, assumed and unknown evidence.
- Stable Koren-form tube modeling exists for two nonlinear stages.
- Negative feedback is explicitly controllable and measurable.
- Input/output transformer-inspired stateful nonlinear stages exist.
- 8x FIR oversampling and alias validation exist.
- Deterministic regression covers sample rates, block sizes, NaN/Inf, automation, stereo behavior and latency.
- A known-good 610 research branch remains available as a baseline/reference model.

## Reusable CIPI knowledge

From 610:
- tube nonlinear transfer modeling;
- feedback vs gain/distortion interaction;
- transformer state / LF saturation behavior;
- harmonic and alias measurement.

From VoPriPro:
- input calibration;
- bounded processing;
- level management;
- regression-first product calibration.

From Vo.Prep:
- plosive, sibilance and slow macro-level context as future vocal-aware detector inputs.

From Vocal Surface:
- harshness/low-mid awareness;
- do not confuse legitimate vocal harmonics/formants with defects.

From Density:
- nonlinear density must be judged with alias, latency and loudness-matched listening.

## Original-product hypotheses under test

- a bounded continuous Character/Drive macro is preferable to exposing the 610 stepped gain structure;
- paired pre/de-emphasis around nonlinear stages may reduce low-end mud and HF/sibilance overdrive while approximately restoring linear spectral balance;
- Stage 1 can prioritize density/transient shape while Stage 2 prioritizes body/smoothing;
- feedback modulation can be used as a product-design dimension rather than a clone constraint;
- transformer behavior should survive ablation before it is retained.

These are **HYPOTHESES**, not confirmed product truths.

## Current implementation branch

original-vocal-pre-v0.1

The existing 610 baseline is intentionally preserved separately so Bypass / 610 baseline / Original comparisons remain possible.

## Current formal gate

**measurement**

The first original prototype must be characterized for:
- THD and H2-H10 vs Character and input level;
- frequency/phase behavior;
- LF saturation;
- alias energy;
- sample-rate consistency;
- stability;
- block ablation.

Numerical results are used to revise the prototype before product parameter lock.

## Required later gates

1. level-matched real-vocal A/B: Bypass vs 610 baseline vs Original;
2. revision based on measured/listening evidence;
3. Windows VST3 release-candidate build;
4. Cubase Pro 14 scan/load/automation/state-recall validation;
5. final precision review.

## Unresolved

- final Character mapping is not locked;
- final Tone mapping is not locked;
- final transformer contribution is not yet ablation-proven;
- vocal-aware dynamic protection is not yet justified;
- real-vocal A/B is not yet complete;
- final CPU/latency tradeoff is not yet locked.

Historical 610-fidelity unknowns such as exact transformer magnetics remain documented, but they are no longer blockers for the original-product track.

## Reusable knowledge target

Vocal-aware analog coloration:
- bounded tube density;
- feedback shaping;
- frequency-dependent nonlinear drive;
- transformer contribution;
- harmonic balance;
- anti-aliasing;
- level compensation;
- evidence-driven minimal UI.

## Promotion rule

Do not mark this track CONFIRMED until numerical measurement, level-matched real-vocal A/B, Windows VST3/Cubase Pro 14 validation, state recall/automation checks and final precision review are complete for the original-product scope.

## 2026-09-25 source-fact spot check

Authoritative UA references checked during the non-destructive content audit:

- UA 2-610 support specifications: modern 2-610 tube complement is one 12AX7A and one 12AT7 per channel.
- UA tube-replacement guidance: some 610-family units/eras use 6072 or 12AT7 in the second tube position; UA notes they are interchangeable in those units but can differ subtly in gain/distortion depending on the power circuit.
- UA 610-B plug-in documentation: the modern 610-B model is based on the 2-610 hardware, while the vintage 610-A is a separate historical target.

Implication:
- CIPI must not silently merge vintage 610-A, modern 610-B/2-610 and every 610-family tube complement into one exact hardware topology.
- The current product remains a reference-informed original vocal preamp, so these distinctions constrain historical claims without creating a new clone blocker.

References:
- https://help.uaudio.com/hc/en-us/articles/206356253-2-610-Dual-Channel-Tube-Preamplifier
- https://help.uaudio.com/hc/en-us/articles/215479643-Replacing-Tubes-in-Your-UA-Analog-Hardware
- https://help.uaudio.com/hc/en-us/articles/17475989779860-UA-610-Tube-Preamp-EQ-Collection-Manual

