# VL2A Phase03D longer optical mean tracking — REJECTED

Date: 2026-09-25

## Classification

- SOURCE_FACT: none added in this phase
- MEASURED: all numeric results below
- INFERRED: longer optical mean tracking improves the isolated low-band A/B deviation
- HYPOTHESIS: a still-longer tau may cross the strict <=0.75 dB gate without harming the active-GR harmonic target
- REJECTED: 4.5 / 5.0 / 6.0 ms as final values

## Trigger

Phase03C showed that shortening the optical mean-tracking tau below 4.0 ms
worsened the isolated forte 20..80 Hz color-isolation difference.

Phase03D therefore tested the opposite direction:
- 4.5 ms
- 5.0 ms
- 6.0 ms

## Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Branch:
- `integration/vl2a-v060-rc2`

Measured source SHA:
- `2f8e7a3ca27ae461ac4ee2c7246bff1ad6a4d358`

Workflow:
- run `36173645172`
- conclusion: FAILURE only because strict selector found no passing candidate

Artifact:
- id `10882090233`
- digest:
  `sha256:50471ec2a26aa9361aa1cfff79f72b5ce3868d5d089c34d24b002b479f501031`

## MEASURED real-vocal A/B results

Maximum absolute band-energy shift:

- 4.0 ms current baseline: ~0.789805 dB
- 4.5 ms: ~0.782919 dB
- 5.0 ms: ~0.777979 dB
- 6.0 ms: ~0.772116 dB

The controlling miss remained the forte 20..80 Hz band.

Detailed forte 20..80 Hz:
- 4.5 ms: +0.782919 dB
- 5.0 ms: +0.777979 dB
- 6.0 ms: +0.772116 dB

Breathy and straight remained comfortably inside the 0.75 dB gate.

## MEASURED harmonic results

Active-GR 1 kHz:

- 4.5 ms: THD ~0.782900%, H3 ~-42.2222 dBc
- 5.0 ms: THD ~0.782790%, H3 ~-42.2234 dBc
- 6.0 ms: THD ~0.782622%, H3 ~-42.2253 dBc

63 Hz active-GR THD:

- 4.5 ms: ~1.35540%
- 5.0 ms: ~1.34513%
- 6.0 ms: ~1.32680%

All remain inside the conservative hardware-informed range used by the project.

## Control-path result

The detector/control path remained unchanged:
- actual matched GR stayed ~6.12 dB in the reference measurements;
- no non-finite result was observed;
- PR0 clean control remained valid;
- H3 dominance remained valid.

## Decision

- 4.5 ms: REJECTED as final value
- 5.0 ms: REJECTED as final value
- 6.0 ms: REJECTED as final value

Reason:
- each still misses the strict <=0.75 dB real-vocal max-band-shift gate.

The direction itself is **not rejected** because the metric improves
monotonically as tau is increased.

## Next experiment

Phase03E:
- 8.0 ms
- 12.0 ms
- 16.0 ms

Additional gate:
- 63 Hz active-GR THD must remain 0.9..1.6%.

If no Phase03E candidate passes, do not loosen the A/B gate automatically.
Return to model structure and test a dedicated low-frequency residual-shaping
mechanism or reopen the metric only with new evidence.
