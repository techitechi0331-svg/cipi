# VL2A Phase 03 active-GR nonlinearity selection — 2026-09-25

## Status

**MEASURED / v4 selected as follow-up candidate only**

The candidate matrix completed successfully. This record does **not** approve
v4 for production because the physical mechanism remains unresolved.

## Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Research branch:
- `research/vl2a-phase03-t4-active-nonlinearity`

Measured source SHA:
- `8baa663589e6fbf0e2e6a8ca8b814523568df346`

Workflow:
- run `36108289078`
- conclusion: SUCCESS

Artifact:
- id `10852169556`
- name `VL2A-Phase03-Active-GR-Candidates`
- digest:
  `sha256:88d6bc1388424608e81a3fb032c4c62fd340474fc5a90cddc56d9b6a97877a3a`

## Candidate result at -18 dBFS / ~6 dB GR / 1 kHz

| Variant | Hard gate | Fidelity gate | THD | H3 | Max fixed-GR drift |
|---|---|---|---:|---:|---:|
| v0 baseline | PASS | n/a | 0.0357% | -69.13 dBc | 0.0000 dB |
| v1 | FAIL | FAIL | 0.5998% | -44.58 dBc | 0.2576 dB |
| v2 | FAIL | PASS | 0.9410% | -40.66 dBc | 0.3950 dB |
| v4 | PASS | PASS | 0.9408% | -40.67 dBc | 0.0000 dB |
| v3 | FAIL | PASS | 1.3657% | -37.43 dBc | 0.5639 dB |

Strict selector result:
- **SELECTED = v4**

## Why v4 won numerically

v4 reproduced the conservative low end of the measured hardware active-GR THD
range while preserving the validated control path:

- THD: ~0.9408%
- H3 dominant
- fixed-control GR drift: 0.0000 dB
- 60 ms release-retention drift: 0
- sample-rate GR drift versus baseline: 0
- PR0 THD unchanged: ~0.01157%
- stress remained finite

v2/v3 reached suitable harmonic ranges but altered the feedback/control law
beyond the predeclared regression limits.

## Mechanism boundary

v4 is a detector-preserving, GR-dependent reduced-order coloration proxy.

It answers:
- can the missing active-compression harmonic envelope be added without
  disturbing the validated control trajectory?

Answer:
- **yes, numerically**.

It does not prove:
- that a memoryless audio-node waveshaper is the physical T4 mechanism;
- that the T4 alone causes all measured hardware THD;
- that v4 will sound more natural on vocals.

The existing CIPI contradiction record remains controlling:
`2026-09-25-active-gr-distortion-contradiction.md`.

## Decision

- v4: **PROMOTE TO FOLLOW-UP RESEARCH CANDIDATE**
- v1/v2/v3: **REJECT for product integration in current form**
- baseline v0: retain as production reference until the mechanism/listening
  follow-up closes.

## Required follow-up

Before v4 or a successor can enter product DSP:

1. test a stateful / optical-modulation reduced model grounded in
   light-source/photoresistor dynamics;
2. compare steady-state harmonic envelope with v4;
3. compare attack/release harmonic behavior, not only steady-state THD;
4. real-vocal level-matched A/B;
5. confirm no interaction with the new Peak Reduction calibration;
6. final sample-rate/alias/stress review.

No production change is authorized by this evidence record alone.
