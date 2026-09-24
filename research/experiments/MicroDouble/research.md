# CIPI MicroDouble 0.1 Research Track

## Research target

Create a singing-oriented artificial doubler that adds believable width/thickness while keeping the lead center stable and constraining mono collapse/comb filtering.

## SOURCE_FACT

SPAT-001 demonstrates time-varying all-pass filtering as a method for reducing interchannel correlation while attempting to minimise degradation of stereo perception.

SPAT-002 describes realtime decorrelation and emphasizes a quality/decorrelation trade-off, including frequency-dependent perceptual constraints.

SPAT-003 provides implementation background for modulation- and delay-based audio effects.

## Mathematical risk of simple Haas doubling

For an equal-amplitude direct signal and delayed copy summed to mono:

`H(f) = 1 + exp(-j 2 pi f tau)`

and therefore:

`|H(f)| = 2 |cos(pi f tau)|`

with cancellation zeros at:

`f_zero = (2k + 1) / (2 tau)`.

This makes a fixed equal-level delay attractive in stereo but structurally vulnerable to comb filtering in mono.

## INFERRED

A safer vocal architecture should avoid making the generated side signal as structurally important as the center lead.

Candidate strategy:

`center dry + left generated double + right generated double`

with:

- center dry preserved;
- side voices lower in level than the lead;
- independent bounded micro-time variation;
- independent bounded micro-pitch variation;
- frequency-dependent decorrelation;
- reduced side generation at low frequencies;
- slow/random modulation rather than coherent periodic LFO where naturalness matters.

## HYPOTHESIS

Time-varying all-pass decorrelation can complement, rather than replace, micro-pitch/time variation. All-pass processing preserves per-channel magnitude but can reduce interchannel coherence through phase change. It does not guarantee mono transparency, so mono-sum measurements remain mandatory.

## Candidate architectures to compare

### A. Delay + micro-pitch

Closest to classic artificial double tracking.

Pros:
- intuitive;
- can sound take-like.

Risks:
- chorus/flange signature;
- interpolation artifacts;
- mono combing.

### B. Time-varying all-pass side decorrelation

Pros:
- flat magnitude per processed channel;
- low delay possible;
- controllable coherence.

Risks:
- mono phase coloration;
- synthetic spatial quality if overused.

### C. Hybrid protected-center design

Dry center remains dominant. Two low-level side voices receive independent delay/pitch variation plus mild all-pass decorrelation.

This is the current leading research hypothesis.

## Required measurements

- L/R correlation over time;
- mono-sum frequency-response variance;
- center-channel energy retention;
- latency;
- pitch/modulation sidebands;
- interpolation aliasing;
- low-frequency stereo width;
- level-matched vocal naturalness;
- comparison against fixed Haas baseline.

## Current location

Research.

## Next stage

Review modulation ranges, interpolation methods, and mono-compatibility metrics before locking any DSP constants.
