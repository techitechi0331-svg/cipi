# Vo.Prep -> VoPriPro Actual VST3 Chain Validation v1

Status: **LOCKED BEFORE EXECUTION**

## Purpose

Validate the already-reviewed event-only compatibility hypothesis through the **actual built VST3 binaries**, not another source-code translation.

Frozen chain:

1. Vo.Prep
   - Input 0 dB
   - Plosive 50%
   - Macro Level 0%
   - Sibilance 50%
   - Subsonic OFF
   - Output 0 dB
2. VoPriPro
   - Amount 50%
   - Character 50% (Natural50)
   - Input 0 dB
   - Output 0 dB

Pinned product refs for the first run:

- Vo.Prep: `ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6`
- VoPriPro: `58049696815fcc24067870edd6a1b89c3cfd2163`
- JUCE: `9.0.2`

No product source is copied into CIPI. Private product repositories are checked out only inside the GitHub Actions workspace.

## Why this gate exists

The deterministic source-derived event-only screen already passed, but that does not prove that:

- JUCE/VST3 parameter normalisation matches the source model,
- the built wrapper exposes the expected parameter contract,
- bus configuration and processBlock behaviour are equivalent,
- reported latency is correct,
- the real Vo.Prep VST3 can feed the real VoPriPro VST3 without wrapper-specific interaction.

This gate is therefore intentionally binary-level.

## Test matrix

Run the same deterministic source-derived families used by the reviewed event-only integration work:

- neutral body,
- plosive positive control,
- sibilance positive control,
- phrase level steps.

Run each at:

- 44.1 kHz,
- 48 kHz,
- 88.2 kHz,
- 96 kHz.

Block size is fixed to 512 samples for v1.

Signals are synthesized in memory. No WAV or other audio artifact is persisted.

## Actual plugin paths

The workflow builds both pinned repositories in Release mode and passes the resulting VST3 bundle paths to a JUCE 9.0.2 headless host.

The host must discover each VST3 through JUCE's VST3 hosting format, instantiate the binary, enumerate parameters, set the frozen values by exact parameter name, prepare stereo processing, and process the matrix block-by-block.

A failure to discover, instantiate, configure, or process either VST3 is a hard failure.

## Latency

Vo.Prep is expected to report 0 samples.

VoPriPro is expected to report the current 1 ms safety-limiter lookahead, i.e. approximately `round(sampleRate * 0.001)` samples.

Measured output windows are aligned by each instantiated plugin's reported latency before RMS metrics are computed.

Latency disagreement is a rejection signal because an unreported or incorrect delay would break host compensation and invalidate direct waveform timing comparisons.

## Persisted metrics only

Persist:

- discovered plugin names,
- parameter-name presence gates,
- reported latency by sample rate,
- finite-output checks,
- neutral Vo.Prep-only RMS delta,
- neutral chain-vs-VoPriPro-only RMS delta,
- Plosive Vo.Prep-only event attenuation,
- Plosive chain-vs-VoPriPro-only event attenuation,
- Plosive post-event chain-vs-VoPriPro RMS delta,
- Sibilance Vo.Prep-only event attenuation,
- Sibilance chain-vs-VoPriPro-only event RMS delta,
- Sibilance post-event chain-vs-VoPriPro RMS delta,
- phrase-spread movement for Vo.Prep-only,
- phrase-spread movement for chain-vs-VoPriPro,
- cross-sample-rate spreads of the above compatibility metrics.

Do not persist rendered audio.

## Predeclared gates

### Binary / contract

- both VST3s discovered and instantiated at every sample rate;
- all required public parameters found exactly once;
- all output values finite;
- Vo.Prep latency = 0 samples;
- VoPriPro latency differs from `round(sr * 0.001)` by at most 1 sample.

### Neutrality

- absolute Vo.Prep-only neutral RMS delta <= 0.10 dB;
- absolute chain-vs-VoPriPro-only neutral RMS delta <= 0.10 dB.

### Plosive compatibility

- Vo.Prep-only event attenuation >= 0.25 dB;
- chain-vs-VoPriPro-only event attenuation >= 0.15 dB;
- absolute post-event chain-vs-VoPriPro RMS delta <= 0.15 dB.

### Sibilance compatibility

- Vo.Prep-only event attenuation >= 0.10 dB;
- absolute chain-vs-VoPriPro-only event RMS delta <= 0.15 dB;
- absolute post-event chain-vs-VoPriPro RMS delta <= 0.15 dB.

The chain delta is intentionally a bounded-neutrality gate rather than a required attenuation gate: the reviewed source-derived screen showed that Sibilance Guard attenuation and reduced downstream broadband compression can largely cancel in broadband RMS while still cleaning the event.

### Phrase compatibility

- absolute Vo.Prep-only phrase-spread movement <= 0.10 dB;
- absolute chain-vs-VoPriPro phrase-spread movement <= 0.10 dB.

### Cross-sample-rate consistency

For each primary compatibility metric above, max-min spread <= 0.15 dB.

## Decision

- **GO_TO_REAL_VOCAL_AB**: every gate passes.
- **REJECT_OR_REVISE**: any DSP/contract gate fails.
- **BLOCKED_EXTERNAL**: the required cross-repository credential or runner infrastructure is unavailable.

Passing does **not**:
- change product DSP,
- change the R2 threshold candidates,
- establish audible superiority,
- establish a default chain,
- close Cubase Pro 14,
- close human listening,
- authorize release.

Passing only confirms that the actual VST3 pair preserves the reviewed event-only compatibility envelope and may advance to real-vocal level-matched A/B.
