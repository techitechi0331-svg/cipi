# HA-100X Input Transformer — source baseline v2

Date: 2026-09-26
Status: source/topology refinement
Product integration authority: NONE

## New SOURCE_FACT — UTC terminal arrangements

Primary-document scan:
https://www.barryrudolph.com/recall/manuals/utc_transformer_pinouts.pdf

The UTC terminal-arrangement sheet explicitly maps HA-100X to:
- primary arrangement 6;
- secondary arrangement 31;
- schematic F.

For primary arrangement 6:
- 500/600 ohm service: connect to terminals 1 and 6;
- join terminals 3 and 4.

For secondary arrangement 31 in single-grid service:
- terminal 7 to grid/signal;
- terminal 10 return;
- join terminals 8 and 9.

This is stronger evidence than forum recollection and upgrades the HA-100X winding connection topology to SOURCE_FACT.

## SOURCE_FACT — manufacturer/catalog electrical envelope

UTC catalog:
- primary includes 500/600 ohm tap;
- secondary 60,000 ohms overall, split;
- 30 Hz to 20 kHz within +/-1 dB;
- maximum level +16 dBm.

The impedance labels imply a nominal overall ratio magnitude near 10:1 by sqrt(Zs/Zp), but this remains INFERRED rather than a winding-count measurement.

## SOURCE_FACT — LA-2A application

Universal Audio LA-2A manual:
https://media.uaudio.com/assetlibrary/l/a/la-2a_manual.pdf

- LA-2A input impedance: 600 ohms balanced.
- maximum input level: +16 dBm.
- overall response: +/-0.1 dB from 30 Hz to 15 kHz.
- input transformer supplies isolation and impedance matching.
- transformer output feeds both the gain-reduction/audio path and side-chain path.
- Figure 5 identifies HA-100X and the immediately associated R5/R6/R7/Gain network.

Original Teletronix schematic scan:
https://www.steampoweredradio.com/pdf/teletronix/Teletronix%20LA-2A%20Leveling%20Amplifier%20Circa%201966.pdf

The scan identifies T1 as UTC HA100X and documents the 600/250 input terminal options and the surrounding input/gain-reduction network.

## MEASURED — lower-tier hardware observations, retained as non-authoritative priors

GroupDIY HA-100X measurements:
https://groupdiy.com/threads/utc-ha-100x.35743/page-2

Reported dark-grey HA-100X examples:
- full 600-ohm-primary-path DCR around 64.7 ohms with 3/4 strapped;
- secondary halves around 1485 and 1551 ohms on one reported unit;
- another pair around 1.58/1.61 kohm.

Reported reissue-type unit:
- primary around 64.45 ohms;
- secondary halves around 1625/1638 ohms.

Reported LCR measurements with secondary 8/9 strapped:
- dark-grey HA-100X: 2128 H at 120 Hz, Q=1.7;
- reissue-type HA-100X: 2154 H at 120 Hz, Q=1.37.

These remain lower-tier MEASURED observations, not universal HA-100X constants.

## INFERRED — referred magnetizing-inductance prior

If:
- the overall nominal impedance-derived ratio magnitude is treated as 10;
- the reported 2128–2154 H is interpreted as the overall secondary inductance;

then its primary-referred inductance is approximately 21.28–21.54 H by Lp = Ls / n^2.

This is an INFERRED sensitivity prior built on lower-tier measurement and a nominal ratio. It must not be promoted to SOURCE_FACT.

## New contradiction / fidelity pressure

Current VL2A input TransformerModel at low level measures roughly:
- 30 Hz relative to 1 kHz: about -0.643 dB;
- 20 kHz relative to 1 kHz: approximately flat.

The 30 Hz result is almost exactly what a first-order 12 Hz high-pass predicts.

The official LA-2A system specification is +/-0.1 dB from 30 Hz to 15 kHz.

CIPI Phase01H line-amplifier evidence is itself only around -0.044 dB at 30 Hz relative to 1 kHz and does not supply a compensating LF boost.

Therefore:

INFERRED:
The current 12 Hz input-transformer high-pass is a significant risk to whole-system LF fidelity. A compiled whole-engine PR0 response test is now required and has been added to the research branch.

This is not yet promoted to MEASURED product mismatch until the compiled engine result is ingested.

## Source impedance warning

"LA-2A input impedance = 600 ohms" is NOT the same statement as:
"every source driving the LA-2A has 600-ohm source resistance."

All physical-reference sweeps must therefore cover a source-resistance family, e.g.:
- 50 ohms;
- 150 ohms;
- 250 ohms;
- 600 ohms.

No single source resistance may be silently baked in as hardware truth.

## Revised uncertainty map

| Quantity | Classification | Current status |
|---|---|---|
| 500/600 primary connection 1-6, join 3-4 | SOURCE_FACT | established by UTC terminal sheet |
| secondary overall connection 7-10, join 8-9 | SOURCE_FACT | established by UTC terminal sheet |
| nominal 500/600 -> 60k relationship | SOURCE_FACT | UTC catalog |
| nominal ratio ~=10 | INFERRED | impedance-derived |
| 30-20k +/-1 dB transformer envelope | SOURCE_FACT | UTC catalog |
| +16 dBm transformer rating | SOURCE_FACT | UTC catalog |
| LA-2A 30-15k +/-0.1 dB system response | SOURCE_FACT | UA manual |
| primary DCR ~60-65 ohms | MEASURED low-tier | multiple reported units |
| secondary total DCR ~3.0-3.3 kohm | MEASURED low-tier | multiple reported units |
| secondary inductance ~2.13 kH @120Hz | MEASURED low-tier | reported units |
| primary-referred Lm ~21.3 H | INFERRED low-tier | ratio-referred |
| leakage inductance | unknown | no adoption value |
| parasitic capacitance | unknown | no adoption value |
| core-loss R | unknown | no adoption value |
| hysteresis constants | unknown | prohibited for adoption |
| exact winding turns ratio | unknown | no direct manufacturer value located |
