# Moore 2026 LA-2A hardware evidence for VL2A

Source:
Austin Moore, **Objective Analysis and Perceptual Evaluation of LA-2A Compressors and Vocal Recordings**, Journal of the Audio Engineering Society 74(1/2), 2026, pp. 61–72.
DOI: 10.17743/jaes.2022.0240

Evidence level: **SOURCE_FACT / E5 peer-reviewed AES**

## Scope

The study measured six hardware LA-2A compressors:
- three vintage Teletronix units;
- three Universal Audio reissues.

The work included frequency response, THD, tone-burst attack/release analysis,
and an ABX experiment with 17 trained listeners.

This source is used as multi-unit empirical context. It is **not** treated as a
single canonical target curve for VL2A.

## Measured hardware variation

### Tone-burst stabilization

The paper defines attack/release stabilization from a peak-hold envelope and a
derivative threshold rather than the manufacturer-style 10 ms attack / 60 ms
half-release descriptors.

Reported attack-to-stabilization times across the six units:
- 51 ms
- 70 ms
- 33 ms
- 81 ms
- 40 ms
- 42 ms

Range: **33–81 ms**
Mean: **52.83 ms**

Reported release-to-stabilization:
- 1670 ms
- 1121 ms
- 740 ms
- 1030 ms
- 449 ms
- 491 ms

Range: **449–1670 ms**
Mean: **916.5 ms**

Interpretation for VL2A:
- do not equate a single internal state constant with one universal hardware
  attack/release time;
- measurement definitions matter;
- a current VL2A trajectory should be judged with the same metric used for the
  comparison source;
- considerable unit variation is normal and must not be 'corrected' toward one
  arbitrary specimen.

### THD under gain reduction

At 1 kHz, the six units showed approximately **0.9%–4.2% THD** in the study's
active-compression measurements.

The paper explicitly distinguishes these values from manufacturer nominal THD
specifications measured under baseline/non-compressing conditions.

The authors argue that the T4 electro-optical attenuator is a plausible major
source of the increased, time-varying distortion during active compression,
while transformers and other active stages may also contribute.

Interpretation for VL2A:
- the very low THD of the isolated Phase 01-H line amplifier is not evidence
  that the complete VL2A should remain equivalently clean during gain
  reduction;
- active-compression distortion should therefore be measured separately before
  deciding whether the current T4/control path is sufficiently faithful;
- do **not** inject 0.9–4.2% static saturation merely to match the table. The
  hardware result is condition-, unit-, frequency-, and dynamic-state
  dependent.

## Frequency-response context

The six units showed unit-to-unit response variation, with the study observing
the most prominent coloration differences mainly below 30 Hz or above 14 kHz.
The paper did not find a simple vintage-versus-reissue performance grouping.

Interpretation:
- small extreme-band differences in the Phase 01-H A/B are not by themselves a
  reason to force a correction;
- unit-level variation is stronger evidence than simplistic
  'vintage = one curve / reissue = another curve' assumptions.

## ABX context

The trained-listener ABX results mixed statistically significant and
non-significant outcomes depending on music context.

Interpretation:
- objective differences do not automatically imply robust perceptual
  discrimination in a mix;
- level-matched listening remains appropriate when a candidate introduces
  measurable but small changes.

## Research consequences

Add to Phase 02/next-stage validation:
1. a standardized current-engine tone-burst stabilization measurement;
2. a complete-VL2A active-compression THD/harmonic measurement;
3. static/no-GR THD as the control condition;
4. avoid universal single-unit timing or THD targets;
5. retain the current source separation between measured hardware facts and
   product hypotheses.

No production DSP change is authorized by this source import alone.
