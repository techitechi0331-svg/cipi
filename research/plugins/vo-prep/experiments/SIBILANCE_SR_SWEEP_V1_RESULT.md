# Vo.Prep Sibilance SR Sweep v1 — Result

## Classification

**MEASURED**

Actual built VST3 binaries were used.

- Vo.Prep: `ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6`
- VoPriPro: `58049696815fcc24067870edd6a1b89c3cfd2163`
- JUCE: `9.0.2`
- Workflow run: `36753394948`
- Artifact: `VoPrep-Sibilance-SR-Sweep-v1`
- Artifact SHA-256: `86f1530f3dbc48be2a3e6188ea52fa9922852e6067f02b7518824039f3153fc2`

No product DSP was mutated by this sweep.

## Decision

**DEPTH_SCALING_SUFFICIENT**

48 kHz / Sibilance 50% reference Vo.Prep-only event attenuation:

- **0.32648 dB**

High-rate rows satisfying the predeclared diagnostic envelope:

| SR | Sibilance | Vo.Prep event attenuation | chain vs VoPriPro event delta | post-event delta |
|---:|---:|---:|---:|---:|
| 88.2 kHz | 35% | 0.29345 dB | -0.13337 dB | +0.00001 dB |
| 96 kHz | 35% | 0.29996 dB | -0.13923 dB | -0.01755 dB |

Both:
- stay within +/-0.05 dB of the 48 kHz / 50% Vo.Prep-only reference;
- satisfy absolute chain event delta <= 0.15 dB;
- satisfy absolute post-event delta <= 0.15 dB;
- remain above the 0.10 dB useful-event attenuation floor.

At 40%:
- 88.2 kHz chain delta = -0.15115 dB;
- 96 kHz chain delta = -0.15778 dB.

So the useful boundary lies between the 35% and 40% rows at high sample rates.

## Interpretation

The actual-binary evidence supports a **depth-normalization revision before a detector/topology rewrite**.

This does not prove that the detector filters are perfectly sample-rate invariant. It only shows that the observed chain rejection can be recovered by controlling reduction depth while leaving detector classification and processing topology unchanged.

## Next experiment

Predeclare and test a minimal sample-rate depth normalization in Vo.Prep. Preserve:
- detector bands and probability blend;
- activation/release thresholds;
- attack/hold/release;
- 33% wide / 67% high topology;
- public Sibilance parameter mapping;
- zero latency.

Then rerun product regression tests and an actual VST3 chain gate against the candidate binary.
