# Black76 Rev E — Imported Product Evidence

## Scope

Product repository: `techitechi0331-svg/76blackCompressor`

This document imports reusable evidence from the Black76 Revision E implementation into the CIPI 1176/FET feedback-compressor truth track.

It does **not** promote the product implementation to hardware truth. Product-specific working calibrations, supplemental UA proxy measurements, and vintage Rev-E facts remain separated.

## SOURCE_FACT

Imported source-backed constraints already tracked by the product repository:

- 1176LN Blackface D/E-family attack range: approximately 20 us to 800 us.
- release range: approximately 50 ms to 1.1 s.
- ratios: 4:1 / 8:1 / 12:1 / 20:1.
- the ratio network changes detector sensitivity and detector bias/threshold together.
- the sidechain is taken before the Output control.
- historical/UA manual material supports a 45 dB ±1 dB vintage working maximum-gain specification, while current UA support material lists 50 dB. Both are retained as a contradiction rather than averaged.
- the Rev D/E-family output stage is a Class-A amplifier/transformer feedback system.

Source provenance remains in the product repo `docs/REV_E_SOURCE_LEDGER.md`.

## MEASURED — Priority 1 Gain Structure

Latest accepted working calibration in the product repository:

- normalized center, Attack OFF: +0.0022368 dB.
- MAX/MAX small-signal gain: +44.429 dB.
- 20 Hz relative to 1 kHz: about -0.887 dB.
- 20 kHz relative to 1 kHz: about -0.634 dB.
- Reference vs Production max output error: about 0.001 dB.
- Reference vs Production max GR error: about 0.000 dB.
- latest reported Production-vs-Reference core speedup: about 1.86x.
- Windows VST3 build succeeded for the Priority-1 working calibration.

Accepted product working constants:

- Line Amp nominal macro multiplier: 2.25.
- Output-control center-range correction: 5.38359 dB.
- provisional output-transformer HF leakage pole: 80 kHz.

These are **product working calibration values**, not asserted original Rev-E component values.

## MEASURED — Supplemental UA control/taper study

Installed measured model:
`UA 1176 Classic FET Compressor v1.0.3`

It is **not** the exact UAD 1176LN Rev E model.

Measured facts within that supplemental model:

- 162-condition small-signal gain matrix was stable between -70 and -60 dBFS; max gain difference was about 0.0003 dB.
- normalized Input and Output control effects were separable to approximately micro-dB residual in the tested regime.
- normalized MAX/MAX gain was about +44.20 dB.
- a 17-point piecewise-linear dB LUT reproduced the measured 65-point Input/Output curves far better than a simple power law or 9-point interpolation.
- normalized 0.5 did **not** establish hardware panel marking 24 and that earlier mapping was rejected.

Reusable implication:
For measured compressor control tapers with deliberate slope changes, a compact piecewise-linear dB LUT can outperform smoother generic curve fits while remaining simple and deterministic.

## MEASURED — Priority 2 baseline after Priority 1

Black76 baseline before detector-drive isolation:

| Mode | 0.5 dB GR onset | 1–6 dB GR ratio | 6–12 dB GR ratio | 12–18 dB GR ratio |
|---|---:|---:|---:|---:|
| 4 | -45 dBFS | 2.9277 | 2.6344 | 2.1770 |
| 8 | -50 dBFS | 3.5692 | 2.9622 | 2.1208 |
| 12 | -52 dBFS | 4.1118 | 3.2887 | 1.8749 |
| 20 | -54 dBFS | 4.5805 | 3.3160 | 1.5645 |

Two faults were visible:

1. higher ratios entered compression earlier, opposite the documented family behavior;
2. deep-GR slopes collapsed toward 1:1 rather than approaching nominal ratios.

## MEASURED — P2-A detector-drive isolation

P2-A changed only the single-button detector-drive constants to:

`{0.48, 0.55, 0.56, 0.65}`

while preserving bias, threshold trim, source resistance, timing, FET and Gain Structure.

Measured result:

| Mode | 0.5 dB GR onset | 1–6 dB GR ratio | 6–12 dB GR ratio | 12–18 dB GR ratio |
|---|---:|---:|---:|---:|
| 4 | -42 dBFS | 2.9750 | 2.6379 | 2.1777 |
| 8 | -40 dBFS | 3.5884 | 3.0036 | 2.1319 |
| 12 | -38 dBFS | 4.1318 | 3.3138 | 1.8997 |
| 20 | -37 dBFS | 4.6023 | 3.3454 | 1.6158 |

Result:

- threshold ordering was corrected and matched the supplemental LN-era onset ordering closely;
- deep static ratios were **not** materially fixed;
- detector-drive change alone is therefore insufficient.

## MEASURED — Detector gain + bias optimizer

A bounded optimizer adjusted detector gain and total bias while solving each mode's onset target.

Best candidates matched the onset targets but still produced only approximately:

- 4: 3.42 / 2.90 / 2.15
- 8: 3.56 / 3.00 / 2.18
- 12: 3.66 / 3.06 / 2.15
- 20: 3.69 / 3.09 / 2.15

for the 1–6 / 6–12 / 12–18 dB GR regions.

The supplemental LN-era proxy target in the same regions is much steeper at high ratios.

This is strong negative evidence that detector gain and detector bias alone cannot reproduce the desired ratio slopes in the current Black76 architecture.

## MEASURED — Real vocal continuity

A free/redistributable vocal test run completed successfully after Priority 1 / during Priority 2 development.

Across 4, 20 and ALL modes and input peaks -18 / -12 / -6 dBFS:

- all tested outputs remained finite;
- Reference vs Production RMS differences were small;
- no numerical discontinuity or digital-clipping failure was identified by the automated test.

This validates numerical continuity, **not** Rev-E ratio fidelity or subjective preference.

Raw vocal audio is not stored in CIPI.

## REJECTED

- `normalized 0.5 == hardware panel 24`: rejected.
- hidden global output trim as a Gain Structure fix: rejected.
- changing transformer turns ratio merely to fill the gain deficit: rejected.
- large detector-drive multipliers as the sole method to create higher ratios: rejected for the current Black76 architecture.
- detector gain + detector bias alone as a sufficient solution for nominal 8/12/20 ratio slopes: rejected by the bounded optimizer for the tested architecture.

## INFERRED

- Ratio-network calibration should separate threshold/onset calibration from deep-GR slope generation.
- Once threshold ordering is corrected, remaining high-ratio failure must be sought in the detector-to-FET control span, FET attenuation law/useful operating range, ratio-dependent loop behavior, or another missing interaction rather than simply restoring large detector drive.
- Working Gain Structure should remain frozen while Priority 2 is investigated, otherwise sidechain calibration becomes ambiguous.

## HYPOTHESIS

The next productive Priority-2 experiment should preserve P2-A threshold ordering while changing one of:

1. detector/control-voltage span into the FET,
2. ratio-dependent FET control mapping / loop law,
3. explicit reconstruction of the switched detector/bias network interaction,

and compare each against a simple detector-drive/bias baseline.

## Current product location

Priority 1 Gain Structure: working calibration complete.

Priority 2 Static Ratio / Threshold: research + isolation measurements in progress.

Exact vintage Rev-E transfer curves remain unavailable, so supplemental UA measurements remain supporting evidence only.
