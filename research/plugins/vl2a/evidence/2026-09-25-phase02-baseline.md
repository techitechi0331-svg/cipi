# VL2A Phase 02 baseline evidence — 2026-09-25

## Status

**MEASURED / hard correctness gate PASS**

This is the exact v0.5.0 optical/sidechain baseline. No production DSP constant
was promoted or modified by this phase.

## Provenance

- Product repo: `techitechi0331-svg/VocalPrepComp`
- Research branch: `research/vl2a-phase02-t4-sidechain-baseline`
- Measured source SHA:
  `76d84dbccc9339348c7fd2a2b0e456e49f7285e9`
- Workflow run: `36084297057`
- Artifact: `VL2A-Phase02-T4-Sidechain-Baseline`
- Artifact id: `10842459304`
- Artifact digest:
  `sha256:2f7698d1353dcf131afd4be06c5778036be558c9f9a2ce1a552e6503300733e8`

## SOURCE_FACT context

Universal Audio documentation describes the LA-2A as a feedback compressor:
the signal driving the sidechain is affected by the gain-reduced signal, passes
through Peak Reduction, a 12AX7 sidechain amplifier, pre-emphasis network, and
a 6AQ5 driver for the electro-luminescent panel. For musical use the emphasis
network is normally set flat.

Primary official source:
- https://media.uaudio.com/assetlibrary/l/a/la-2a_manual.pdf

The 1966 Teletronix schematic documents:
- R2 Peak Reduction = 100 kOhm;
- R37 Limit Response = 1 MOhm;
- V3 = 12AX7A;
- V4 = 6AQ5A;
- T4A optical element.

1966 source:
- https://www.steampoweredradio.com/pdf/teletronix/Teletronix%20LA-2A%20Leveling%20Amplifier%20Circa%201966.pdf

## MEASURED — Peak Reduction map

Representative COMP values:

| Input peak | PR50 | PR75 | PR80 | PR100 |
|---|---:|---:|---:|---:|
| -30 dBFS | 0.027 dB | 0.285 dB | 0.379 dB | 1.140 dB |
| -24 dBFS | 0.203 dB | 0.838 dB | 1.100 dB | 3.008 dB |
| -18 dBFS | 0.614 dB | 2.313 dB | 2.922 dB | 6.217 dB |
| -12 dBFS | 1.743 dB | 5.161 dB | 6.086 dB | 10.283 dB |
| -6 dBFS | 4.180 dB | 9.008 dB | 10.112 dB | 14.767 dB |
| 0 dBFS | 7.742 dB | 13.351 dB | 14.538 dB | 19.427 dB |

PR0 measured 0 dB GR throughout the matrix.

Interpretation:
- the earlier Cubase observation of about 3 dB GR around PR80 is reproduced by
  the exact current engine for a signal peaking around -18 dBFS;
- therefore that observation alone is **not evidence of a sensitivity bug**.

## MEASURED — COMP / LIMIT

At fixed high-drive conditions LIMIT becomes progressively stronger than COMP.

Examples:
- -12 dBFS / PR100:
  - COMP = 10.283 dB GR
  - LIMIT = 10.926 dB GR
- -6 dBFS / PR100:
  - COMP = 14.767 dB
  - LIMIT = 16.158 dB
- 0 dBFS / PR100:
  - COMP = 19.427 dB
  - LIMIT = 22.156 dB

Static local I/O slope diagnostic at PR100:
- COMP rises toward ~4.48:1 at the strongest measured step.
- LIMIT reaches ~7.81:1 before the final step becomes effectively horizontal
  under the analyzer's high-ratio clamp.

This is not interpreted as a constant hardware ratio claim.

## MEASURED — Release / program memory

GR retained after 60 ms:

- 0.1 s prior exposure: 47.47%
- 1 s: 50.94%
- 5 s: 53.02%
- 15 s: 53.49%

The longer prior exposure also leaves progressively larger long tails.

Interpretation:
- the present model reproduces the characteristic rapid first recovery region
  plus program-dependent memory well enough to remain the baseline;
- no release retune is justified before matched-metric hardware comparison.

## MEASURED — Attack probe

For -12 dBFS / PR75 COMP relative to the 1 s reference state:

- 1 ms: 2.17%
- 5 ms: 13.45%
- 10 ms: 31.61%
- 20 ms: 59.63%
- 50 ms: 83.21%
- 100 ms: 87.68%

This probe is not directly compared to Moore 2026 stabilization times because
the measurement definitions differ.

## MEASURED — sidechain frequency behavior

At -12 dBFS / PR75 COMP:

- 100 Hz: 5.112 dB GR
- 1 kHz: 5.161 dB
- 5 kHz: 5.162 dB
- 10 kHz: 5.162 dB
- 15 kHz: 5.161 dB

This confirms the current emphasis behavior is effectively factory-flat.

## MEASURED — sample-rate invariance

Representative GR:

- 44.1 kHz host: 5.16265 dB
- 48 kHz: 5.16136 dB
- 96 kHz: 5.15724 dB
- 192 kHz: 5.17116 dB

Spread: about 0.014 dB.

## MEASURED — complete-engine active-compression THD

1 kHz examples:

- -18 dBFS / PR0:
  - THD = 0.01157%
- -18 dBFS / PR75:
  - GR = 2.33 dB
  - THD = 0.01765%
- -18 dBFS / PR100:
  - GR = 6.26 dB
  - THD = 0.03648%

At -18 dBFS, Moore 2026 calibrated the hardware test to +4 dBu and adjusted
for about 6 dB gain reduction. The six measured hardware units produced much
higher 1 kHz THD, with the table spanning approximately 0.94% to 4.22% for the
original Teletronix subset.

Peer-reviewed source:
- Austin Moore, JAES 74(1/2), 2026,
  https://doi.org/10.17743/jaes.2022.0240

## INFERRED

The present VL2A does not need an arbitrary Peak Reduction boost to explain the
Cubase PR80 observation.

The stronger evidence gap is that active gain reduction adds very little
nonlinear coloration relative to measured hardware under a closely matched
reference condition.

## HYPOTHESIS

A bounded GR-dependent optical-path nonlinearity may recover part of this
hardware behavior without damaging the already-good T4 timing or feedback
curves.

This hypothesis moves to Phase 03 and is not yet a production fact.

## REJECTED

- global static saturation active at PR0;
- increasing Peak Reduction sensitivity solely to make the meter move more;
- changing release timing merely to raise THD;
- targeting the 4.22% hardware outlier as a universal 'correct' sound;
- assuming one vintage specimen represents all 1966 units.
