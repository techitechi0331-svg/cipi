# PeakBody Realtime Periodicity / Voicing Research 01

Status: **RESEARCH / BENCHMARK DESIGN**

## Problem

PeakBody's current successful synthetic guard uses an analysis-oriented periodicity proxy.

That proxy demonstrated an important mechanism, but it has not yet been justified as product DSP with respect to:

- realtime CPU;
- latency;
- noisy-vocal behavior;
- high-register harmonic protection;
- implementation simplicity.

The next task is not to replace it automatically. It is to compare established causal frame-wise periodicity families under the same PeakBody-specific discrimination problem.

## SOURCE_FACT

### PITCH-001 — YIN

YIN estimates F0 using an autocorrelation-related difference function with modifications intended to reduce pitch errors.

The original publication describes it as suitable for speech/music, relatively simple, efficient/low-latency, and without an intrinsic upper search-frequency limit.

### PITCH-002 — pYIN

pYIN extends frame-wise YIN with probabilistic threshold distributions and multiple pitch candidates, then uses temporal tracking.

For PeakBody, this supports the broader idea that **periodicity/voicing confidence** can be more useful than one hard pitch estimate.

Full pYIN/HMM tracking is not automatically appropriate for a low-latency compressor detector.

### PITCH-003 — McLeod Pitch Method

MPM uses a normalized square-difference / NSDF family and exposes a tonal **clarity** measure while being designed for realtime monophonic pitch estimation.

## Current baseline

PeakBody analysis baseline:

- causal trailing frame;
- 40 ms frame;
- 5 ms hop conceptually;
- normalized autocorrelation maximum;
- 80–1200 Hz lag range;
- periodicity confidence in [0,1].

## Candidates

### Candidate A — YIN CMND confidence

Use the cumulative-mean-normalized difference function.

Research confidence:

`confidence = clamp(1 - CMND_min, 0, 1)`

The F0 estimate is retained as a diagnostic but PeakBody primarily consumes confidence.

### Candidate B — MPM / NSDF clarity

Use maximum normalized square-difference function peak over the allowed lag range.

PeakBody consumes the clarity-like peak height.

## Research Question

Can YIN-CMND or MPM-clarity provide a realtime-bounded periodicity confidence that preserves clean/bright/noisy voiced material while rejecting noise-like sibilance/breath at least as safely as the current normalized-autocorrelation baseline?

## Simple baseline requirement

All candidates are compared to the existing normalized-autocorrelation confidence.

No candidate is adopted merely because it is published or because its pitch estimate is accurate.

## Synthetic cases locked before run

- low sine, 100 Hz;
- normal harmonic voice-like stack, 220 Hz;
- high harmonic stack, 700 Hz;
- bright high harmonic stack, 700 Hz;
- extreme bright harmonic stack, 1000 Hz;
- bright 700 Hz harmonic stack mixed with high-band noise at 6 dB SNR;
- sibilant-like high-band noise;
- breath-like colored noise;
- silence.

Analysis rate is fixed at 12 kHz for this algorithm-family benchmark. Host-rate/resampler validation is a separate future gate.

## Metrics

Per detector:

- minimum confidence across clean voiced cases;
- minimum confidence across bright-high cases;
- confidence for the noisy-voiced case;
- maximum confidence across noise-like cases;
- silence confidence;
- bright-vs-noise confidence margin;
- diagnostic F0 relative error on clean voiced cases;
- deterministic pair-operation proxy;
- operation ratio versus normalized-autocorrelation baseline;
- finite outputs.

## Candidate acceptance

A candidate qualifies for further implementation research only if all hold:

- clean voiced confidence minimum >= **0.75**;
- bright-high confidence minimum >= **0.75**;
- noisy-voiced confidence >= **0.55**;
- noise-like confidence maximum <= **0.35**;
- silence confidence <= **0.05**;
- bright-vs-noise confidence margin >= **0.45**;
- operation proxy ratio <= **2.5x** baseline;
- all outputs finite.

F0 error is recorded but is not a hard gate because PeakBody needs reliable voicing protection more than transcription-grade pitch.

## Selection rule

Automation may report which candidates satisfy the predeclared gates, but it must not select a product winner.

If multiple candidates qualify, later product research should compare:

- realtime C++ CPU;
- latency;
- automation/block-size behavior;
- private/public real-vocal false-protection behavior.

## Rejection rule

A candidate failing any hard confidence/safety gate remains negative evidence. Do not weaken thresholds after seeing the result.

## Scope limitation

Synthetic algorithm-family benchmark only.

A pass does not establish:

- real-vocal validity;
- product CPU;
- Cubase compatibility;
- universal optimality.
