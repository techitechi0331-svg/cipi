# Vo.Prep Sibilance Sample-Rate Sweep v1

Status: **LOCKED BEFORE EXECUTION**

## Purpose
Diagnose the actual-VST3 chain rejection without changing product DSP or relaxing the locked chain gate.

Observed trigger for this diagnostic:
- actual Vo.Prep -> VoPriPro VST3 chain reached binary processing successfully;
- every locked gate passed except `sibilance_chain_abs_delta_le_0_15db`;
- absolute Sibilance chain delta increased with sample rate and exceeded 0.15 dB at high rates.

## Frozen binaries
- Vo.Prep: `ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6`
- VoPriPro: `58049696815fcc24067870edd6a1b89c3cfd2163`
- JUCE: `9.0.2`

## Diagnostic matrix
Sample rates:
- 44.1 kHz
- 48 kHz
- 88.2 kHz
- 96 kHz

Sibilance normalized Amount values:
- 0.00
- 0.25
- 0.30
- 0.35
- 0.40
- 0.45
- 0.50

Vo.Prep diagnostic configuration:
- Input 0 dB
- Plosive 0% (isolates Sibilance Guard)
- Macro Level 0%
- Sibilance = sweep value
- Subsonic OFF
- Output 0 dB

VoPriPro:
- Amount 50%
- Character 50% / Natural
- Input 0 dB
- Output 0 dB

Use the same deterministic sibilance-on-vowel family as the locked actual-VST3 chain probe.

## Persisted metrics
For every sample-rate / Sibilance-amount pair:
- finite-output state
- Vo.Prep-only event attenuation
- chain-vs-VoPriPro-only event RMS delta
- post-event chain-vs-VoPriPro RMS delta

No rendered audio is persisted.

## Interpretation
This is a diagnostic sweep, not a product-selection gate.

Classify:
- **DEPTH_SCALING_SUFFICIENT** if lower Sibilance amounts at high sample rates can recover the 48 kHz / 50% compatibility envelope while post-event behaviour remains bounded.
- **DETECTOR_OR_TOPOLOGY_REVIEW** if reducing Amount cannot recover the envelope consistently, or the required amount relationship is materially irregular.
- **BLOCKED_EXTERNAL** only for repository/runner infrastructure failure.

Do not:
- relax the locked v1 chain gate;
- mutate Vo.Prep or VoPriPro DSP;
- promote a new default Amount from this sweep alone;
- claim perceptual superiority.

The result is evidence for selecting the next experiment only.
