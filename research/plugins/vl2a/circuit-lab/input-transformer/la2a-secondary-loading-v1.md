# LA-2A / HA-100X secondary loading network v1

Date: 2026-09-26
Status: topology reconstruction / offline-reference input
Product integration authority: NONE

## SOURCE_FACT — schematic topology

The Universal Audio LA-2A Figure 5 and the historical Teletronix schematic show the HA-100X secondary feeding a network built around:

- R5 = 68k;
- R6 = 68k;
- R7 = 2.7k in the referenced manual drawing;
- Gain R1 = 100k;
- T4 photoconductive cell;
- a side-chain/attenuator-drive takeoff.

The manual explicitly explains that the T4 photo-cell is the lower leg of a voltage divider: lower photo-cell resistance creates more attenuation.

The simplified redraw at:
https://tangible-technology.com/dynamics/art_o_dynamics.html

makes the network connectivity especially readable and is consistent with the official Figure 5.

## Reconstructed low-frequency resistive network

Research abstraction:

secondary signal node S
- direct termination branch: R5 -> ground;
- audio/control branch: R6 -> node A;
- node A -> sidechain input load Zsc;
- node A -> R7 -> node B;
- node B -> Gain pot total resistance R1 -> ground;
- node B -> T4 photo-cell Rphoto -> ground.

Ignoring the very high tube-grid input impedance for the first load calculation:

Zb = R1 || Rphoto
Za = Zsc || (R7 + Zb)
Zsecondary = R5 || (R6 + Za)

This is a topology model, not yet a complete AC model.

## INFERRED — load movement

With:
- R5 = 68k;
- R6 = 68k;
- R7 = 2.7k;
- R1 = 100k;

and leaving Zsc open, the simplified effective load is approximately:
- Rphoto = 20 Mohm -> 48.59 kohm;
- Rphoto = 4.7 Mohm -> 48.46 kohm;
- Rphoto = 100 kohm -> 43.50 kohm;
- Rphoto = 10 kohm -> 36.71 kohm;
- Rphoto = 1 kohm -> 34.90 kohm.

If a 100k sidechain loading branch is included:
- dark load is approximately 43.2 kohm;
- bright ~1k photo-cell load is approximately 34.87 kohm.

These values are circuit calculations from a reduced loading abstraction, not hardware measurements.

## Important implication

The HA-100X is not necessarily operating into one fixed 60k load.

Its effective secondary loading can depend on:
- T4 photo-cell state;
- sidechain input loading;
- Gain network loading;
- COMP/LIMIT topology around R7.

Therefore a physically stronger offline model should allow:

T4 state -> secondary load -> HA-100X transfer -> audio/detector drive

rather than only:

input sample -> fixed transformer coloration -> T4.

This creates a physically meaningful program-dependent interaction that the current VL2A TransformerModel cannot represent.

## Stability / realtime warning

Do not introduce a realtime algebraic loop merely to model this interaction.

Offline reference:
- solve the coupled network directly/implicitly if needed.

Realtime reduced candidates:
- use previous-sample optical state or a bounded state estimate if the load interaction proves audibly/measurably relevant;
- or collapse it into a stable parameterized transfer if the full interaction produces negligible improvement.

## HYPOTHESIS

Because R5 provides a strong ~68k termination and the load range remains on the order of tens of kohms, the load-dependent transformer response may be measurable but modest.

It should be tested before adding runtime complexity.

## REJECTED

- treating 60k catalog secondary impedance as a fixed resistor that is always present in the LA-2A circuit;
- assuming the transformer can never interact with T4 state;
- adding a feedback/algebraic loop before offline measurement shows the interaction is material.
