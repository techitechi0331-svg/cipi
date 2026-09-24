# PeakBody 0.1 — Revision Measurement 02

Date: 2026-09-24  
Classification: **MEASURED + HYPOTHESIS**

## Why Revision 02 exists

Revision 01 established the correct vocal-specific **direction**:

- high crest -> slower attack + faster release;
- low crest -> faster attack + slower release.

Its first selected values were:

- 40 ms crest integration;
- 6–35 ms attack;
- 120–400 ms release.

A second targeted sweep tested whether the crest-memory window and maximum attack could improve transient preservation without sacrificing sustained-body control.

## Candidates compared

The sweep compared 40 / 60 / 80 ms crest integration, with multiple attack/release bounds, against:

- fixed 40 / 400 ms compression;
- the rejected crest->fast prototype;
- real singing onset events;
- synthetic 10–100 ms bursts;
- sustained synthetic sine/body;
- 100 ms RMS dynamic-range reduction on real singing.

## Selected Revision 02

Current leading prototype:

- crest integration: **80 ms**
- attack: **6–40 ms**
- release: **120–400 ms**

Transient factor:

`t = clamp(log2(max(C2, 2) / 2) / 2, 0, 1)`

Timing:

`attack = 6 + 34*t` ms

`release = 400 - 280*t` ms

## Synthetic transient comparison

At the standard Amount-50 measurement setting, Revision 02 versus fixed 40/400 ms:

| Burst length | Revision 02 max GR | Fixed 40/400 max GR | Extra GR |
|---:|---:|---:|---:|
| 10 ms | ~1.21 dB | ~1.22 dB | ~-0.00 dB |
| 20 ms | ~2.24 dB | ~2.26 dB | ~-0.02 dB |
| 30 ms | ~3.01 dB | ~3.01 dB | **~+0.01 dB** |
| 50 ms | ~4.61 dB | ~4.25 dB | ~+0.36 dB |
| 100 ms | ~6.96 dB | ~5.92 dB | ~+1.04 dB |

Interpretation:

- 10–30 ms transient/consonant-scale events are effectively preserved like a fixed 40 ms attack;
- by 50–100 ms the processor increasingly treats the event as body rather than a transient and begins controlling it more strongly.

This is the intended vocal behavior.

## Sustained-body convergence

For the synthetic sustained-sine test:

- steady GR: ~3.12 dB;
- time to approximately 90% of steady GR: **~147 ms**.

Revision 01 reached body faster (~100 ms) but grabbed 30–50 ms material more aggressively.

Revision 02 was selected because ~147 ms remained within the provisional 150 ms body-control target while materially improving transient preservation.

## Real singing — phrase-start behavior

On the available less-compressed singing variants, Revision 02 remained slightly **more preserving** than the fixed 40/400 ms baseline at detected low-pre-GR phrase starts.

Across the tested variants:

- 20 ms phrase-start extra GR:
  - median roughly -0.09 dB;
  - worst p90 roughly **-0.01 dB**.
- 50 ms phrase-start extra GR:
  - median roughly -0.11 dB;
  - worst p90 roughly **-0.02 dB**.

Negative values indicate slightly less early attenuation than the fixed baseline.

## Real singing — body stabilisation

For `natural_dereverb_audio.wav`, 100 ms RMS dynamic spread:

| Model | 90th–10th percentile RMS spread |
|---|---:|
| input | ~14.87 dB |
| fixed 40/400 | ~12.84 dB |
| Revision 02 | **~12.82 dB** |
| rejected softened crest->fast | ~12.53 dB |

Revision 02 therefore retains essentially the same broad level-stabilisation effect as the fixed baseline while preserving short transients more deliberately.

The stronger reduction of the rejected crest->fast model is not automatically an advantage because it partly came from greater transient flattening.

## Current acceptance criteria encoded for CI

Revision 02 adds deterministic behavioral gates:

1. **30 ms burst preservation**
   - adaptive max GR may not exceed fixed 40 ms attack by more than **0.15 dB**.

2. **sustained-body convergence**
   - at 150 ms after onset, GR must have reached at least **88%** of the final sustained-body GR.

These gates protect the intended balance during future optimization/refactoring.

## Remaining limitations

Revision 02 is still not a release lock.

Pending:

- full Macro-Level raw vocal corpus;
- multiple singer/register conditions;
- sibilant/breath-heavy phrases;
- CPU benchmark at 44.1 / 96 / 192 kHz;
- level-matched real-audio AB;
- full main pluginval + Steinberg validator;
- Cubase Pro 14 host validation;
- final review.

## Decision

**Revision 02 supersedes Revision 01** as the current PeakBody implementation target.

Proceed to implementation regression CI, then full VST3 gates.
