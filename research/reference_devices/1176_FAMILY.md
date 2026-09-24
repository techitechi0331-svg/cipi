# 1176 Family — reference-device research 0.1

Status: **RESEARCHING**  
Maturity: **L2/L6**

This file separates documented circuit behaviour from later modeling hypotheses.

## Documented architecture

Universal Audio documentation describes the 1176LN as a FET gain-reduction compressor/limiter.

Important documented blocks:

`input attenuation -> transformer -> FET gain-reduction stage -> preamplifier/output path -> sidechain / GR control -> FET gate control`

The documentation identifies the unit as a **feedback-style compressor**, because the sidechain samples after gain reduction.

The gain-reduction control section uses phase-inverted paths feeding CR2/CR3 as a full-wave rectifier. The rectified control voltage is smoothed by C22. Attack and release controls alter the charge/discharge behaviour of that control network before driving the FET gate.

Reference:
- Universal Audio 1176LN documentation / technical section.
- https://help.uaudio.com/hc/en-us/articles/34530260482324-1176-Classic-FET-Compressor-Manual
- archived hardware manual pages/schematic used only where they match the UA-described topology.

## Documented timing ranges

UA documentation gives approximately:

- attack: 20 us to 800 us;
- release: 50 ms to 1100 ms;
- ratios: 4:1, 8:1, 12:1, 20:1.

These front-panel ranges do **not** imply a simple one-pole digital implementation.

UA also documents program-dependent release behaviour and ratio-dependent behaviour in its modeled 1176 family.

## Circuit research targets

The next pass must derive or measure:

1. FET variable-resistance operating region and control law.
2. Gain-reduction feedback-loop relationship.
3. Rectifier/control-voltage transfer.
4. RC attack/release trajectories across control positions.
5. Ratio-switch influence on threshold, loop gain and timing.
6. input/output amplifier nonlinear contribution.
7. transformer frequency/nonlinear contribution.
8. revision differences (A/B/C/D/E/F etc.).

## Modeling policy

Do not reduce "1176 sound" to:

`fast compressor + saturation`.

CIPI will separate at least:

- static compression curve;
- feedback topology;
- detector/rectifier;
- timing network;
- FET gain element;
- amplifier stages;
- transformer stages;
- level calibration.

Only after those are independently understood should a compact reusable FET-compressor design pattern be promoted.

## Current evidence

- FET as variable-resistance GR element: **E5 documented**.
- feedback sidechain topology: **E5 documented**.
- full-wave rectification and RC timing network: **E5 documented**.
- exact digital-equivalent FET law: **unconfirmed**.
- exact contribution of each nonlinear stage to perceived character: **unconfirmed / measurement required**.
