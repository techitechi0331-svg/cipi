# VL2A v0.6.0 RC2 final evidence — draft

Date: 2026-09-25
Status: FINAL VALIDATION IN PROGRESS

## Product candidate

Repository:
- `techitechi0331-svg/VocalPrepComp`

Integration branch:
- `integration/vl2a-v060-rc2`

RC2 gate run:
- run `36147549961`
- conclusion: SUCCESS
- source SHA: `f59e15479dc436bcb9f7f85ff597caf3aaf5c080`

## Peak Reduction midpoint requirement

Final product requirement:
- real vocal peak-normalized to approximately -18 dBFS;
- COMP;
- Peak Reduction = 50;
- maximum GR target = approximately 5..7 dB.

Pinned VocalSet real-vocal measurements:

- breathy: 5.30939 dB max GR
- straight: 5.55217 dB
- forte: 6.40301 dB
- median: 5.55217 dB

Selected Peak curve:

`e(n) = 2 * (1 - (1-n)^2.70)`
`drive = 0.18 * 10^e(n)`

where `n = Peak Reduction / 100`.

This is monotonic, retains PR0, and retains the same 40 dB full-scale
sidechain-drive endpoint.

## Active-GR coloration

Phase 03B stateful optical-ripple v3 remains integrated.

At -18 dBFS / approximately 6 dB GR / 1 kHz:
- THD: ~0.7830%
- H3: ~-42.22 dBc
- H3 dominant
- PR0 THD: ~0.01157%

RC2 re-measurement retained the same active-GR harmonic result.

## Control-path behavior

RC2:
- COMP / -18 dBFS / PR75: ~11.79 dB GR
- COMP / -18 dBFS / PR100: ~12.51 dB
- LIMIT / -18 dBFS / PR75: ~12.65 dB
- LIMIT / -18 dBFS / PR100: ~13.47 dB

Sample-rate representative GR:
- 44.1 kHz: ~16.414 dB
- 48 kHz: ~16.406 dB
- 96 kHz: ~16.407 dB
- 192 kHz: ~16.369 dB

Spread remains well below 0.20 dB.

Important:
fixed-PR release comparisons are not used to judge T4 timing after the Peak
recalibration, because fixed PR now produces a different GR depth.
The final validation run therefore performs a matched-GR release check.

## Meter

The central numeric GR display is upgraded to use an audio-thread block-peak
hold exposed through an atomic value and consumed at the editor refresh.

Purpose:
- avoid losing short GR events between 60 Hz UI refreshes;
- keep the smooth 0..20 dB segmented bar as a separate visual presentation.

The audio DSP path is unchanged by the meter patch.

## Stereo / R37

- stereo shared detector: intentional modern, phase-safe VL2A product design;
- no claim of exact 1966 one-sided sensitivity;
- R37 / Limit Response: factory-flat musical default retained;
- no front-panel R37 control.

## Main line amplifier

Phase 01-H line amplifier remains unchanged:
- 12AX7 reduced physical reference;
- load-aware 12BH7 proxy;
- A-24 load/network proxy;
- previously validated sample-rate/stress behavior retained.

## Gain

Gain:
- -18..+18 dB;
- 0 dB center;
- intentional modern-DAW product deviation;
- not claimed as a literal 1966 +40 dB Gain control reproduction.

## Remaining final gates

The following must be appended before release closure:

1. matched-GR T4 release result;
2. level-matched real-vocal A/B result;
3. pluginval strictness 10;
4. final VST3 artifact id/digest;
5. final source-state audit;
6. CIPI contradiction review;
7. Cubase Pro 14 real-host confirmation remains the only user-side gate.

No final release claim is authorized until items 1..6 pass.
