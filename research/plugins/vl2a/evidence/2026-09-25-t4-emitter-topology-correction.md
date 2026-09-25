# VL2A T4 emitter topology correction — 2026-09-25

## Status

**SOURCE CORRECTION / mechanism interpretation revised**

This record preserves the measured Moore 2026 hardware data while correcting a
physical-description mismatch in the paper's T4 discussion.

## E5/E4 source facts for original LA-2A T4 topology

Teletronix / Universal Audio LA-2A documentation describes the T4 as an
electro-optical attenuator using:
- an electro-luminescent (EL) panel;
- a photo-electric / CdS cell.

The sidechain driver supplies the high voltage needed to drive the EL panel.

Sources:
- original/archived Teletronix LA-2A documentation and schematic;
- Universal Audio LA-2A user manual / gain-reduction-circuit description.

Representative official/manual wording:
- T4 is composed of an electro-luminescent panel and photo-electric cell;
- greater sidechain voltage increases EL brightness;
- the photo-cell resistance decreases with light and forms the attenuating
  voltage divider.

## Conflict in Moore 2026 mechanism narrative

Moore 2026 correctly measures complete hardware LA-2A units and reports
meaningful active-compression THD. Those empirical measurements remain valid
evidence.

However, the paper's conceptual T4 description refers to:
- a tungsten lamp / tungsten filament;
- thermal inertia of that filament.

That emitter description does not match the EL-panel topology documented for
the LA-2A T4.

## Evidence separation

### KEEP as E5 MEASURED
- six-unit THD measurements;
- third-harmonic-dominant results;
- unit-to-unit variation;
- tone-burst measurement results;
- ABX results.

### DOWNGRADE to INFERRED / mechanism hypothesis
- attribution of the elevated THD primarily to a T4 mechanism described through
  tungsten-filament thermal behavior.

The paper itself already uses cautious language such as "likely" / "most
plausible" for the source attribution. The emitter-topology mismatch further
prevents promotion of that mechanism explanation to SOURCE_FACT.

## Consequence for VL2A Phase 03

A memoryless GR-dependent odd waveshaper at the optical audio node is **not
physically validated** by Moore 2026.

Phase 03 may still be used diagnostically to answer:
- how much nonlinear coloration would be needed to match measured hardware THD;
- whether that amount can coexist with validated control behavior.

But such a candidate cannot be promoted as a T4 model solely from the Moore
measurements.

## Higher-priority mechanism research

After Peak Reduction calibration is corrected, investigate the complete
closed-loop sources of active-compression harmonics separately:

1. EL drive / CdS resistance transfer nonlinearity and finite response;
2. sidechain 12AX7 / 6AQ5 driver behavior;
3. time-varying attenuation interacting with a periodic signal;
4. input/output transformer level dependence;
5. main amplifier operating-level changes under feedback.

The selected reduced-order implementation should emerge from these interactions
where possible rather than from a globally inserted saturation block.

## REJECTED

- "tungsten lamp thermal inertia" as a SOURCE_FACT for a 1966 LA-2A T4;
- production promotion of a static optical-node waveshaper from THD match alone;
- discarding Moore's measured THD table because the conceptual emitter
  description is inaccurate.
