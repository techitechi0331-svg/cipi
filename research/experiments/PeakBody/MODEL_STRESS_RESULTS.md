# PeakBody 0.1 — Model Stress Results

Classification: **MODEL_MEASUREMENT**, not VST3 measurement.

Reproduction script: `model_stress.py`

Model:

- sample rate: 48 kHz
- crest integration: 200 ms
- literature core: `2 / C2`
- CIPI response exponent: 0.35
- CIPI timing floor: 0.25
- attack maximum: 40 ms
- release maximum: 400 ms

## Results

| Signal | Mean C2, final 0.5 s | Mean scale, final 0.5 s | 5th % scale | Mean attack | Mean release |
|---|---:|---:|---:|---:|---:|
| steady sine 0.8 | 1.9970 | 1.0000 | 1.0000 | 40.00 ms | 400.00 ms |
| steady sine 0.08 | 1.9970 | 1.0000 | 1.0000 | 40.00 ms | 400.00 ms |
| white noise 0.2 | 12.94 | 0.522 | 0.489 | 20.87 ms | 208.71 ms |
| square 0.3 | 1.0002 | 1.0000 | 1.0000 | 40.00 ms | 400.00 ms |
| sine + impulse every 100 ms | 493.03 | 0.250 | 0.250 | 10.00 ms | 100.00 ms |
| sine + 5 ms burst every 500 ms | 33.53 | 0.392 | 0.310 | 15.66 ms | 156.64 ms |

## Findings

### MEASURED

The detector remains level-invariant for the two steady sine amplitudes to the shown precision.

The softened mapping no longer drives broadband noise to the former ~0.16 average scale. It stays around 0.52 in this deterministic model.

Repeated strong short peaks still request the fastest allowed timing, but the new safety floor limits that state to 10 ms attack / 100 ms release instead of 4 ms / 40 ms.

### INFERRED

The revised mapping is materially safer for a vocal prototype because noise-like sections are no longer forced close to the absolute fastest timing.

### UNRESOLVED

This model does not prove that 0.35 / 0.25 are perceptually optimal. Sibilants, breaths, plosives, vowel onsets, and real singing dynamics must still be tested.

The VST3 implementation must separately pass the deterministic C++ gate, pluginval, Steinberg validator, measurements, and level-matched vocal AB.
