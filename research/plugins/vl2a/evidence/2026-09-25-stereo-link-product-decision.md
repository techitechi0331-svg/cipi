# VL2A stereo-link product decision — 2026-09-25

## Decision

**KEEP current shared, phase-safe stereo detector as an intentional modern
product design.**

Current implementation:
`detector = 0.5 * (abs(L) + abs(R))`

This decision does **not** claim that the equation is an exact reconstruction of
the 1966 stereo-link electrical network.

## SOURCE_FACT — 1966 Teletronix

The original stereo system links the gain-reduction control voltage between two
units. A control voltage generated in either amplifier causes equal gain
reduction in both units after stereo-balance calibration.

The manual does not publish a digital-equivalent sample-by-sample detector law
for:
- one-sided signals;
- phase-shifted stereo signals;
- whether a linked pair behaves as max, sum, average, RMS, or another law when
  translated to one plug-in instance.

Therefore a direct max(L,R) replacement is not source-supported.

## SOURCE_FACT — Waves CLA-2A

Official Waves documentation describes the stereo component as:
- two channel paths;
- one detector shared by both paths.

This supports the VL2A requirement that both channels receive one common GR
trajectory, but it does not disclose the exact L/R combine law.

## MEASURED current VL2A

Reference-parity run:
- `36088776046`
- artifact `10844739826`

The current detector is:
- perfectly L/R symmetric;
- centered identical stereo == mono GR;
- one shared GR trajectory for both channels;
- phase-safe because magnitude is combined after per-channel absolute value.

One-sided signals yield less GR than centered equal-level stereo.

Example COMP / -12 dBFS / PR100:
- centered: ~10.28 dB GR
- one-sided: ~6.20 dB GR

This behavior is quantitatively known.

## PRODUCT REASONING

VL2A is a modern vocal-oriented product, not a literal two-chassis electrical
stereo-link clone.

The current law has useful modern properties:
- no stereo-image shift from separate L/R compressors;
- no cancellation when L/R are out of phase;
- deterministic symmetry;
- centered mono-compatible material preserves the mono calibration exactly;
- no unsupported detector change is required.

Changing to max detection would materially increase one-sided compression and
would be a new product choice, not a proven fidelity repair.

## Classification

- shared detector concept: **KEEP**
- current average-of-magnitudes law: **KEEP AS INTENTIONAL PRODUCT DEVIATION**
- claim of exact 1966 one-sided sensitivity: **REJECTED**
- max detector as historical truth: **REJECTED / unsupported**

## Reopen condition

Reopen only if a controlled test captures one-sided versus centered GR under
documented levels/settings from:
- a calibrated linked hardware pair;
- or a commercial reference whose stereo detector law is measured rather than
  inferred.

Stereo behavior is no longer a release blocker as long as VL2A documentation
states that its link law is a modern phase-safe shared-detector implementation.
