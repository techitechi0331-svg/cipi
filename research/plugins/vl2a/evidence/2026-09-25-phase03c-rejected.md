# VL2A Phase03C low-band optical refinement — REJECTED

Date: 2026-09-25

## Trigger

Final real-vocal color-isolation A/B with the RC2 / Phase03B optical-v3 model
found one strict-gate miss:
- forte
- 20..80 Hz band
- +0.789805 dB after level matching
- gate: <= 0.75 dB

All higher bands were substantially smaller.

## Hypothesis tested

Shorten the optical mean-tracking time from the current 4.0 ms, while keeping:
- optical coloration amount 0.055
- fast residual tau 0.10 ms
- Peak v8
- T4 control law
- line amplifier
- COMP/LIMIT
- R37
- stereo detector

Candidates:
- 3.5 ms
- 3.0 ms
- 2.5 ms

## Provenance

Product branch:
- `integration/vl2a-v060-rc2`

Workflow:
- run `36170244690`
- conclusion: FAILURE only because strict selector found no passing candidate

Artifact:
- id `10880946038`
- digest `sha256:b5fab4161c1b4d4c41b9bed29309baf438fe1499452ac39ed371c981f7a5346a`

## MEASURED results

Maximum real-vocal band shift:
- current 4.0 ms: ~0.789805 dB
- 3.5 ms: ~0.799981 dB
- 3.0 ms: ~0.813955 dB
- 2.5 ms: ~0.836254 dB

The miss remained isolated to forte / 20..80 Hz.

At 1 kHz active GR:
- 3.5 ms THD ~0.783197%, H3 ~-42.219 dBc
- 3.0 ms THD ~0.783407%, H3 ~-42.217 dBc
- 2.5 ms THD ~0.783680%, H3 ~-42.214 dBc

PR0 clean THD remained ~0.01157%.
Stress remained finite.

## Decision

- shortening optical mean tracking: **REJECTED**
- Phase03B coloration amount 0.055: not rejected
- Peak v8: unaffected / remains accepted
- T4 control path: unaffected
- next direction: test longer optical mean tracking above 4.0 ms

## Next experiment

Phase03D:
- 4.5 ms
- 5.0 ms
- 6.0 ms

Selection rule:
- choose the smallest tau above 4.0 ms that passes all strict A/B and THD gates.
