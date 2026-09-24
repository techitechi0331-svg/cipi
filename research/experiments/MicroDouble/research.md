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


## Leading architecture after mono-model review

The initial fixed-delay model confirmed that lowering generated-side level reduces static mono coloration, but even protected-center delay copies still alter the mono frequency response because the delayed content remains present in the sum.

A stronger topology is now preferred:

`Lout = Lin + g*S`

`Rout = Rin - g*S`

where `S` is a generated artificial-double side signal.

For a standard mono downmix:

`Mout = (Lout + Rout) / 2`

therefore:

`Mout = (Lin + Rin) / 2`

The generated side cancels algebraically. This means the width effect can disappear in mono without imposing the fixed comb-filter response of conventional equal-polarity Haas doubling.

### Candidate side construction

`M = (Lin + Rin) / 2`

`dA = variableDelayA(M)`

`dB = variableDelayB(M)`

`Sraw = HPF((dA - dB) / 2)`

`S = sideGuard(Sraw, M)`

The two virtual takes should use different bounded delay trajectories. Modulated delay naturally creates small time/pitch variation; explicit pitch shifting is therefore optional in the first prototype.

### Stereo-correlation guard

If dry Mid `M` and generated Side `S` are approximately uncorrelated, the L/R correlation is approximately:

`rho = (sigma_M^2 - g^2 sigma_S^2) / (sigma_M^2 + g^2 sigma_S^2)`

Define the side-to-mid RMS ratio:

`r = g sigma_S / sigma_M`

then:

`rho = (1 - r^2) / (1 + r^2)`

This gives a useful safety relation before implementation. For example, keeping generated Side RMS well below Mid RMS helps retain positive stereo correlation.

## INFERRED

For a lead vocal, exact mono preservation of the original track is a stronger design objective than preserving the generated double in mono.

The current leading topology is therefore **original signal untouched + artificial double encoded only into Side**.

## HYPOTHESIS

The first prototype should use:

- two independently modulated short delays driven from Mid;
- Side formed from their difference;
- low-frequency removal from generated Side;
- bounded Side/Mid RMS ratio;
- no explicit pitch shifter initially;
- fractional-delay interpolation suitable for slowly moving delays.

This must be compared against a conventional positive-polarity ADT/Haas baseline in stereo naturalness, correlation, and mono behavior.


## Review note — perceptual group-delay budget

SPAT-004 is directly useful for the decorrelation half of MicroDouble.

Its main design lesson is that decorrelation should not be treated as a single broadband "random phase" target. The amount of group delay that can be used effectively without objectionable smearing is frequency dependent, and perceptually informed ERB-scale constraints can outperform naive random-phase approaches.

CIPI implication:

- define a frequency-dependent decorrelation budget rather than one global delay amount;
- protect low frequencies strongly;
- allow more phase/time diversity only where the perceptual cost is acceptable;
- measure both objective coherence and audible smearing;
- do not assume lower correlation automatically means better vocal sound.

This makes a future ERB-aware side generator more attractive than an arbitrary cascade of identical all-pass sections.

## Review note — fractional-delay interpolation

SPAT-003 confirms that time-varying delay/pitch effects require fractional-delay interpolation.

DELAY-001, although studied in a different audio-DSP context, provides a useful interpolation comparison:

- linear interpolation is simple and has linear phase but increasing high-frequency magnitude error;
- first-order all-pass interpolation preserves magnitude but has increasing high-frequency phase error;
- cubic Lagrange interpolation can materially improve fractional-delay accuracy.

For MicroDouble, cubic Lagrange is therefore a strong baseline candidate for time-varying side delays.

This is **INFERRED**, not yet a proven best choice for vocal doubling. The eventual implementation must compare:

- interpolation error;
- modulation sidebands;
- CPU;
- subjective chorus/zipper artifacts.

## Updated leading architecture

Current leading hypothesis:

`dry center + two lower-level generated sides`

Each side:

`fractional delay -> slow stochastic delay modulation -> bounded micro-pitch behavior -> mild ERB-aware decorrelation -> low-frequency side reduction`

The two sides should not use identical modulation trajectories.

The center lead remains unprocessed by the widening stage so mono collapse cannot remove the primary vocal anchor.
