# Black76 Rev E — CIPI Sync 2026-09-25

Product repository: `techitechi0331-svg/76blackCompressor`

Product main reviewed at/after:
- Priority 1 working calibration completion
- Priority 2 P2-A threshold-order isolation
- Priority 2 control-path probe
- Priority 2 linear-detector ablation

This is an append-only sync note. Earlier imported evidence remains valid within its recorded scope.

## SOURCE_FACT

No new primary-source claim is promoted here beyond the existing CIPI 1176 import.

The existing source-backed constraints remain:
- ratio switching changes detector sensitivity and detector bias/threshold together;
- sidechain is sensed before the Output control;
- single-button nominal ratios are 4/8/12/20;
- published attack/release and 45 dB-class historical gain facts remain subject to their already-recorded scope and contradictions.

## MEASURED — Priority 1 retained working calibration

Product evidence records:
- normalized center Attack-OFF gain: about +0.002 dB;
- MAX/MAX small-signal gain: about +44.429 dB;
- 20 Hz–20 kHz response remained inside the published ±1 dB envelope in the accepted working calibration;
- Reference-vs-Production output difference remained about 0.001 dB maximum in the automated comparison;
- Windows VST3 build succeeded.

Working constants remain product calibrations, not component-level hardware facts:
- Line Amp macro multiplier 2.25;
- Output-control center-range correction 5.38359 dB;
- output-transformer HF leakage pole 80 kHz.

## MEASURED — P2-A threshold-order isolation

P2-A single-button detector-drive constants:
`{0.48, 0.55, 0.56, 0.65}`

Measured onset ordering became:
- 4: -42 dBFS
- 8: -40 dBFS
- 12: -38 dBFS
- 20: -37 dBFS

This corrected the previously reversed threshold order.

Deep-GR effective ratios remained far below the supplemental LN-era target, so detector-drive correction was insufficient.

## MEASURED — control-path probe

Product run 36070356399 directly measured Gate, Timing, actual GR and FET attenuation.

Across 4/8/12/20/ALL:
- Gate hard-clamp rows: 0;
- Timing node reached only about 6–8% of the 5 V hard clamp;
- FET attenuation remained continuous beyond 19 dB and reached roughly 20–22.5 dB in the sweep;
- at about 18 dB actual GR, gate remained around -2.73 V, far from the -0.02 V gate ceiling;
- no non-finite state was observed.

## REJECTED — hard-limit explanation

Rejected for the measured 1–18 dB GR operating region:

`deep static-ratio collapse is caused by Gate reaching -0.02 V or Timing reaching 5 V`

The measured control path did not approach either limit.

## MEASURED — linear detector ablation

A research-only diagnostic replaced the existing detector with:
`detected = abs(sidechain)`

Per-ratio detector gain and total bias were optimized against the committed supplemental LN-era onset/static-ratio target.

Best measured fits:

| mode | onset | 1–6 dB GR | 6–12 dB GR | 12–18 dB GR |
|---|---:|---:|---:|---:|
| 4 | -42 | 5.21 | 4.56 | 3.39 |
| 8 | -40 | 9.39 | 7.07 | 5.01 |
| 12 | -38 | 15.27 | 11.10 | 7.51 |
| 20 | -37 | 12.46 | 23.11 | 15.22 |

Committed supplemental target:

| mode | onset | 1–6 dB GR | 6–12 dB GR | 12–18 dB GR |
|---|---:|---:|---:|---:|
| 4 | -42 | 3.0854 | 4.6462 | 5.0337 |
| 8 | -40 | 4.9467 | 7.8239 | 8.2618 |
| 12 | -38 | 7.7485 | 11.8871 | 12.1317 |
| 20 | -37 | 13.7836 | 21.9264 | 22.8206 |

## REJECTED — simple linear detector as final solution

Rejected within the tested Black76 architecture:

`plain full-wave abs() detector + one gain and bias per ratio is sufficient to reproduce onset, knee/mid slope and deep-GR slope simultaneously`

Matching onset and one portion of the curve did not match the complete transfer curve.

## INFERRED

The dominant Priority-2 problem is a curvature/loop-shape problem rather than:
- simple threshold offset;
- FET attenuation exhaustion;
- Timing/Gate hard saturation.

Candidate mechanisms that remain open:
- nonlinear detector transfer shape;
- diode-bias operating-point interaction;
- ratio-dependent source/loading behavior;
- detector/control-amplifier loop gain;
- detector-to-FET control mapping interaction.

## HYPOTHESIS

The next productive experiment should compare a physically motivated nonlinear detector/control-amplifier candidate against:
1. the current detector baseline;
2. the rejected linear abs() baseline.

The candidate must be able to independently address low-level knee, mid-level nominal slope and high-level/deep-GR growth without an arbitrary post-hoc GR remap.

## Product / listening status

Earlier free-vocal continuity evidence remains valid as numerical-stability evidence only.

A newer actual-VST3 CC0 real-vocal AB pipeline was repaired on 2026-09-25 after a PowerShell `$Host` variable collision. A provenance-clean rerun is required before importing that newest AB artifact as final CIPI evidence.

Raw vocal audio must not be committed to CIPI.
