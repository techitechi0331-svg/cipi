# VL2A GR meter scale decision — 2026-09-25

## Decision split

- **20 dB visible GR full scale: KEEP**
- **current display ballistics: OPEN / needs parity validation**

These are intentionally separate decisions.

## SOURCE_FACT — Waves CLA-2A

The official Waves CLA-2A User Guide shows the modeled VU meter with the gain
reduction scale extending from about -20 dB to 0 dB.

Source:
- https://assets.wavescdn.com/pdf/plugins/cla-2a-compressor-limiter-v16-update.pdf
- official guide UI figure / GR meter mode

The same guide states that the VU display can monitor Input, Gain Reduction and
Output.

## MEASURED — current VL2A UI

Current editor:
- visible range normalized to 0..20 dB GR;
- labels 0 / 5 / 10 / 15 / 20;
- DSP values above 20 dB are display-clamped;
- display-only rise time constant ~50 ms;
- display-only fall time constant ~320 ms.

Reference-parity artifact:
- run `36088776046`
- artifact `10844739826`
- digest:
  `sha256:757c94d102433c210fecd4fe7d901fc9eb2246f2a938a2bcdf52f242b79915df`

## MEASURED — ballistics consequence

At PR100 COMP, the current UI under-displays short bursts relative to DSP GR.

Examples:
- -18 dBFS / 50 ms:
  - DSP ~4.96 dB
  - UI ~3.17 dB
- -12 dBFS / 50 ms:
  - DSP ~8.53 dB
  - UI ~5.59 dB
- -6 dBFS / 50 ms:
  - DSP ~12.53 dB
  - UI ~8.40 dB

At 250..500 ms the UI converges much more closely to DSP GR.

## INFERRED

The 20 dB visible scale itself is reference-compatible and should not be
expanded to 40 dB merely because the compressor can generate up to roughly
40 dB gain limiting.

The separate question is whether the editor-only smoothing accurately reflects
the desired LA-2A meter experience.

## Decision

### KEEP
- 20 dB visible GR full-scale concept;
- bar/needle pegging at full scale when DSP GR exceeds the meter range.

### OPEN
- exact rise/fall ballistics;
- whether the digital numeric readout should show:
  - 20.0 when pegged;
  - 20+ when DSP GR is above visible scale;
  - or the raw DSP GR while the bar remains pegged.

No DSP compressor calibration change is authorized by the meter decision.

## REJECTED

- expanding the visible meter to 40 dB solely from maximum gain-limiting spec;
- increasing Peak Reduction sensitivity just to make the UI meter look busier;
- treating the current 20 dB clamp as proof that the audio DSP itself is
  limited to 20 dB.
