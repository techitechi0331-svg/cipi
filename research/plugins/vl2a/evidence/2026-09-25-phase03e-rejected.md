# VL2A Phase03E extended optical mean tracking — REJECTED

Date: 2026-09-25

## Classification

- MEASURED: candidate A/B, harmonic, release, sample-rate and control results
- INFERRED: tau-only tuning reaches a local optimum near 8 ms
- HYPOTHESIS: residual-path frequency shaping can solve the remaining low-band miss
- REJECTED: 8 / 12 / 16 ms as final values
- REJECTED direction: optical-mean tau-only tuning as the sole final fix

## Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Branch:
- `integration/vl2a-v060-rc2`

Measured source SHA:
- `38937e7dd41c4382dcf76b69dc7ef47161a38aae`

Workflow:
- run `36178543570`
- conclusion: FAILURE because no candidate passed the strict color gate

Artifact:
- id `10883033656`
- digest:
  `sha256:d0c33819a5e826b37eb2216bcf0906c25459cec792ebf9fe39f547832d972c9b`

## MEASURED real-vocal color-isolation

Maximum absolute band-energy shift:

- 8 ms: **0.768085 dB**
- 12 ms: **0.768993 dB**
- 16 ms: **0.771614 dB**

Strict gate:
- <=0.75 dB

The controlling row remained:
- forte
- 20..80 Hz

This establishes a local minimum near 8 ms; extending tau farther begins to
worsen the metric again.

## MEASURED harmonic behavior

### 8 ms
- 63 Hz THD: ~1.298999%
- 1 kHz THD: ~0.782401%
- 1 kHz H3: ~-42.2277 dBc

### 12 ms
- 63 Hz THD: ~1.265903%
- 1 kHz THD: ~0.782169%
- 1 kHz H3: ~-42.2304 dBc

### 16 ms
- 63 Hz THD: ~1.247469%
- 1 kHz THD: ~0.782044%
- 1 kHz H3: ~-42.2318 dBc

All candidates remain inside:
- 1 kHz THD gate 0.75..1.60%
- 63 Hz THD guard 0.90..1.60%
- H3-dominant requirement

## MEASURED control/safety

For all candidates:
- release trajectory identical:
  - start GR ~15.7198 dB
  - 60 ms GR ~8.8900 dB
  - retained fraction ~0.56553
- sample-rate GR rows identical and finite
- sample-rate spread ~0.0450 dB
- PR0 THD ~0.01157%
- stress finite

Thus the failure is isolated to the real-vocal low-band coloration gate, not
the compressor control law.

## Validation-process finding

The Phase03E workflow protocol specified a 63 Hz THD guard, but the automated
selector inherited from Phase03D did not enforce that guard.

Manual final-precision inspection of the artifact confirmed that all three
candidates satisfy the 63 Hz guard.

Because every candidate already failed the independent <=0.75 dB color gate,
this selector omission does **not** change the REJECT outcome.

The omission is retained as a validation-process Negative Result.

## Decision

- 8 / 12 / 16 ms: REJECTED as final values
- tau-only optical-mean tuning: EXHAUSTED / REJECTED as sole fix
- 8 ms retained only as the Simple Baseline for the next structural comparison

## Next

Phase03F:
- 8 ms baseline / no residual HP
- 8 ms + 25 Hz residual-modulation HP
- 8 ms + 50 Hz residual-modulation HP
- 8 ms + 75 Hz residual-modulation HP

The new filter affects only the small optical-ripple audio-coloration path and
must not alter the T4 detector/control path.
