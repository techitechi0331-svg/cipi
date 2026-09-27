# SM57 Reference Evidence Inventory — 2026-09-28

## Purpose

This inventory starts the first real-reference Mic Simulator track after `MIC-SIM-FOUNDATION-001`.
It records only source-supported SM57 facts and explicitly separates unresolved transfer-function dimensions.

## SOURCE_FACT

Primary manufacturer sources:
- https://www.shure.com/en-US/docs/guide/SM57
- https://pubs.shure.com/view/guide/SM57/en-US.pdf
- https://content-files.shure.com/publications/specSheet/ja/sm57-lce.pdf

Registered facts:
- Manufacturer/model: Shure SM57.
- Transducer type: dynamic / moving coil.
- Frequency response: 40 Hz to 15 kHz.
- Polar pattern: cardioid.
- Sensitivity at 1 kHz: -56.0 dBV/Pa (1.6 mV).
- Output impedance: 310 ohm actual; some manufacturer material also states 150 ohm rated.
- Positive acoustic pressure on the diaphragm produces positive voltage on pin 2 relative to pin 3.
- Manufacturer publishes a typical frequency-response curve.
- Manufacturer publishes polar plots at selected frequencies.
- Manufacturer documents proximity effect and states that at about 6 mm distance the bass response can rise by about 6 to 10 dB below 100 Hz.

## MEASURED

No controlled unit-level SM57 transfer-function measurement has been admitted into CIPI by this registration.

Foundation measurements remain synthetic and must not be reclassified as SM57 hardware evidence.

## INFERRED

- The published frequency and polar material is enough to define measurement targets and falsifiable model dimensions.
- It is not enough to establish phase parity, transient parity, complete off-axis parity, distance interpolation, or nonlinear level dependence.

## HYPOTHESIS

A reusable SM57 model will require separate dimensions for:
- frequency response,
- phase/group delay,
- transient response,
- polar/off-axis behavior,
- proximity/distance behavior,
- static electrical behavior,
- level-dependent/nonlinear behavior.

A frequency-response-only match is insufficient.

## UNRESOLVED

- quantified phase response / group delay,
- impulse / step / transient response,
- dense angle-by-frequency polar behavior,
- continuous distance/proximity transfer behavior,
- quantified level-dependent distortion or transfer behavior,
- controlled source/cab/room isolation for real reference capture,
- unit-to-unit variation,
- sample-rate-independent implementation validation.

## REJECTED

- treating the published frequency curve as full microphone parity,
- fabricating phase or transient data from magnitude response alone,
- treating manufacturer marketing language as quantitative nonlinear evidence,
- auto-promoting source facts into product-adoption evidence,
- coupling the Mic Simulator implementation directly to Virtual Guitar internals.

## Human-gated evidence required later

- controlled real-reference audio/measurement acquisition,
- listening judgment,
- Cubase/host confirmation,
- final product adoption,
- release decision.
