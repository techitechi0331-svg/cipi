# PeakBody Private Real-Vocal Guard Validation 01

Status: **PROTOCOL LOCKED BEFORE DETAILED MEASUREMENT**  
Evidence target: **MEASURED (private-source, derived metrics only)**

## Research Question

Does the PeakBody periodicity-protected spectral guard remain stable and musically plausible on a real sung-vocal performance after realistic dereverb/clarity/compression-style processing changes, without committing raw audio to GitHub?

## Scope

This is **not** a multi-singer corpus.

All four sources are processing variants of the same approximately 68.36 s vocal performance. They are used as a **processing-invariance / confounder robustness test** only.

No claim from this study may be generalized to all singers, languages, registers, microphones, or performance styles.

## Private source binding

Raw audio remains outside GitHub.

Only source identifiers, metadata, SHA-256 hashes, and aggregate non-reversible measurements may be stored.

| ID | Private source | SR | Channels | Duration | SHA-256 |
|---|---|---:|---:|---:|---|
| PV1 | clear_enhanced_audio.wav | 44100 | 2 | 68.3595 s | 6df64e2aba1b6c00582f2ac4eaf17ba169d6cdd239550863d2c8773d79d7e234 |
| PV2 | dereverb_clear_audio.wav | 44100 | 1 | 68.3595 s | 5798e68e732725f345a032a48da658aed6ac93b3db2d769b0d183bb0c8d75ad5 |
| PV3 | natural_dereverb_audio.wav | 44100 | 1 | 68.3595 s | c40c1454f09c3047b07daacb77b04097cc177d517b1556a847e00e3a5b70cf04 |
| PV4 | studio_recording_style.wav | 44100 | 1 | 68.3595 s | 14890fbce0e891f9c3267b2c42cd3e454399e7367af88b0a054394f77ffdc750 |

PV4 has prior light compression and is treated as a stress/processed variant, not as a raw-vocal reference.

## Baseline

**PeakBody Revision 02 broadband crest only**

- crest integration: 80 ms;
- transient factor:
  `t = clamp(log2(max(C2, 2) / 2) / 2, 0, 1)`;
- no spectral/periodicity guard.

## Candidate

**PeakBody periodicity-protected spectral guard**

Reuse the synthetic Stage-2 structure:

- normalized high-band / broadband energy guard;
- high-band cutoff baseline: 5.6 kHz;
- ratio envelope: 20 ms;
- spectral guard threshold: -11 dB;
- spectral transition width: 6 dB;
- maximum guard strength: 0.75;
- periodicity protection multiplies the spectral guard by `(1 - periodicityConfidence)`.

For this private real-vocal study, periodicity is made **streaming/causal enough for research** rather than computed once over a complete event:

- trailing analysis window: 40 ms;
- update hop: 5 ms;
- lag search: 80–1200 Hz equivalent;
- normalized autocorrelation;
- no future samples;
- analysis-only implementation, not yet product DSP.

## Hypothesis

Compared with broadband crest alone, the candidate will:

1. strongly reduce peak-preservation behavior on high-band-dominant / weakly periodic frames;
2. preserve peak-preservation on high-band-dominant / strongly periodic frames;
3. leave steady voiced/body behavior almost unchanged;
4. behave consistently across the four processing variants of the same performance.

## Counter Hypotheses

- Dereverb/clarity/compression changes make the guard decision unstable.
- Bright periodic singing is still suppressed because the streaming periodicity estimate is weaker than the synthetic whole-event proxy.
- Plosive/low-frequency transients are incorrectly suppressed.
- The guard changes ordinary sustained-body behavior too much.
- There are too few naturally occurring proxy events to support a conclusion.

## Frame and activity definition

Analysis hop: **5 ms**.

Active frame:

- trailing 40 ms RMS is above both:
  - -60 dBFS, and
  - 30 dB below that file's overall RMS.

The stereo PV1 source is downmixed to mono by arithmetic channel mean for detector research only.

## Proxy event classes

These are **feature-defined proxies**, not human semantic labels.

### Noise-like high-band crest proxy

A frame must satisfy:

- baseline transient factor >= 0.75;
- spectral guard activation >= 0.5;
- periodicity confidence <= 0.35;
- active frame.

Used only to test whether the candidate actually suppresses the kind of low-periodicity/high-band crest event it was designed to reject.

### Bright voiced crest proxy

A frame must satisfy:

- baseline transient factor >= 0.75;
- spectral guard activation >= 0.5;
- periodicity confidence >= 0.80;
- active frame.

Used to test whether periodicity protection prevents the synthetic bright-high-F0 failure.

### Strong periodic voiced/body proxy

A frame must satisfy:

- periodicity confidence >= 0.80;
- baseline transient factor <= 0.50;
- active frame.

Used to test steady/body invariance.

### Low-frequency transient proxy

A frame must satisfy:

- baseline transient factor >= 0.75;
- low-band (<900 Hz) power ratio >= 0.60;
- active frame.

Used as a real-audio proxy for plosive/low-frequency transient preservation.

## Metrics

Per private source and pooled:

- active frame count;
- each proxy-class frame count;
- candidate/baseline transient-factor retention ratio;
- median and p10 retention for bright voiced crest frames;
- median and p10 retention for low-frequency transient frames;
- median candidate suppression ratio for noise-like high-band crest frames;
- mean absolute candidate-vs-baseline transient-factor change for strong periodic body frames;
- pairwise cross-variant correlation of baseline transient factor;
- pairwise cross-variant correlation of candidate transient factor;
- pairwise cross-variant correlation of spectral-guard strength;
- periodicity-confidence quantiles;
- finite-value / boundary checks.

No raw frames or timecodes are committed.

## Acceptance Criteria

The private-source study passes its **limited processing-invariance scope** only if:

1. all derived values are finite;
2. each of the four files has at least 100 active analysis frames;
3. pooled bright voiced crest proxy count >= 30;
4. pooled noise-like high-band crest proxy count >= 30;
5. pooled low-frequency transient proxy count >= 30;
6. bright voiced crest:
   - median retention >= 0.95;
   - p10 retention >= 0.85;
7. low-frequency transient:
   - median retention >= 0.90;
   - p10 retention >= 0.80;
8. noise-like high-band crest:
   - median candidate/baseline transient-factor ratio <= 0.35;
9. strong periodic voiced/body:
   - mean absolute candidate-vs-baseline transient-factor delta <= 0.03;
10. median pairwise cross-variant candidate transient-factor correlation >= 0.80;
11. candidate correlation is not more than 0.05 lower than the baseline correlation median.

## Rejection / Inconclusive Criteria

**REJECT** the current guard for this private-source scope if any preservation or invariance criterion fails with adequate proxy counts.

**INCONCLUSIVE** rather than reject if:

- any required proxy class has fewer than 30 pooled frames;
- timing alignment between source variants is materially inconsistent;
- source preprocessing makes the proxy definitions unusable.

## Reproducibility / Privacy

- random seed: not applicable; deterministic analysis;
- timeout target: < 10 minutes local CPU;
- no network required;
- raw audio must not be committed;
- no per-frame timecodes committed;
- no spectrogram/image derived from private audio committed;
- only aggregate CSV/JSON/Markdown and hashes may enter CIPI.

## Simple Baseline Requirement

The candidate is always compared against Revision 02 broadband crest with no guard.

No success claim may be made from candidate-only metrics.

## Next Decision

- PASS -> keep periodicity-protected guard as the leading detector hypothesis and advance to broader/multi-singer or product-realtime periodicity testing.
- REJECT -> preserve the negative result and return to guard research.
- INCONCLUSIVE -> acquire or unlock a better private vocal corpus before changing the detector.
