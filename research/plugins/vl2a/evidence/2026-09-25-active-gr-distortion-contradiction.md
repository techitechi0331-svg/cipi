# VL2A active-GR distortion source contradiction — 2026-09-25

## Status

**OPEN CONTRADICTION / blocks direct mechanism promotion**

This record prevents a numerically convenient distortion proxy from being
treated as a proven physical T4 model.

## Evidence A — peer-reviewed hardware measurements

Moore (JAES, 2026) measured six hardware LA-2A compressors during active gain
reduction and reported:
- about 0.9% to 4.2% THD at 1 kHz across units;
- third harmonic generally dominant;
- the author identifies the T4 electro-optical attenuator as the most plausible
  primary source of elevated harmonic content during gain reduction, while also
  noting transformer and active-stage interaction.

The mechanism is described as time-varying and related to:
- lamp brightness versus photocell resistance;
- tungsten-filament dynamics;
- CdS behavior;
- attack/release transitions.

Evidence level: **E5 / peer-reviewed measured hardware**.

Source:
- Austin Moore, JAES 74(1/2), 2026,
  https://doi.org/10.17743/jaes.2022.0240
- open manuscript:
  https://pure.hud.ac.uk/ws/portalfiles/portal/140787498/AAM.pdf

## Evidence B — official Waves modeling documentation

Waves CLA-2A User Guide states that the electro-luminescent circuitry does not
add distortion when it modulates the sound and separately states that tube
distortion was modeled.

Evidence level: **E4 / official product manual**.

Source:
- https://assets.wavescdn.com/pdf/plugins/cla-2a-compressor-limiter-v16-update.pdf

## Reconciliation boundary

These statements are not treated as equivalent claims:

- Moore reports complete-hardware behavior and offers a reasoned mechanism
  interpretation from measured THD.
- Waves describes its modeling/design interpretation and may be simplifying the
  electro-optical element for product explanation.

The peer-reviewed hardware evidence has higher evidentiary weight for the fact
that active-compression THD exists.

However, it does **not** prove that a memoryless static waveshaper inserted at
the audio-side optical node is the correct physical mechanism.

## Consequence for Phase 03

Phase 03 static GR-dependent odd-color candidates may be used to answer:
- can the missing harmonic envelope be reproduced without breaking control
  behavior?

They may **not** establish:
- physical T4 mechanism fidelity;
- production approval.

Even if a candidate passes:
- 0.8..1.6% THD;
- H3 dominance;
- GR/release/sample-rate regression gates;

its status is only **candidate-for-follow-up**.

## Required follow-up before production

At least one of the following must support the mechanism:

1. a stateful optical model grounded in lamp/CdS behavior reproduces the same
   harmonic result naturally;
2. measured hardware data across steady-state and attack/release conditions
   show that the chosen reduced-order proxy tracks the dynamic harmonic
   behavior;
3. a gray-box comparison demonstrates that a simpler proxy is perceptually and
   objectively equivalent enough for the vocal product goal.

Real-vocal A/B remains required.

## REJECTED

- adding 1% static saturation globally;
- enabling the distortion at PR0;
- asserting that the T4 is definitively the sole distortion source;
- asserting that Waves disproves measured hardware THD;
- promoting a Phase 03 numeric winner directly into production.
