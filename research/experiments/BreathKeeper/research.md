# CIPI BreathKeeper 0.1 Research Track

## Research target

Control excessive recorded breath events in a lead vocal while preserving intentional expressive breathing and breathy phonation.

## Critical distinction

CIPI separates two acoustically different phenomena:

1. **breath event**
   - inhalation/exhalation noise between or around sung phrases;
   - often largely unvoiced / noise-like;
   - may occur near pause boundaries.

2. **breathy phonation**
   - still a voiced sung sound;
   - periodic vocal-fold excitation remains present;
   - breathiness is part of timbre/phonation and should not be treated as removable noise by default.

A processor that merges these two cases risks destroying expressive singing.

## SOURCE_FACT — singing breath events

BREATH-001 analysed unaccompanied singing from 18 singers, totaling about 128 minutes and 1488 labelled breath events.

Reported properties include:

- breath spectral envelopes were relatively similar within the same song/singer;
- long-term average spectra showed a notable region around approximately 1.6 kHz for male singers and 1.7 kHz for female singers;
- an HMM using MFCC, delta-MFCC, and delta-power features achieved high recall but materially lower precision, showing that false positives remain an important design problem.

BREATH-002 reports that short silence-like edge regions before/after breathing sounds can help reduce false alarms in realistic speech.

BREATH-003 describes inhalation noise as having weak formant-like structure with noise energy extending into roughly the 4–5 kHz region and discusses the singing breath findings above.

## SOURCE_FACT — breathy phonation

PHON-001 reports that breathy phonation tends toward lower CPP and higher H1-H2 relative to typical phonation in the studied tasks.

PHON-002 also supports CPP as an acoustic correlate of perceived breathiness, while spectral slope adds information.

These are phonation-quality results, not direct breath-event detectors.

## INFERRED

A useful singing breath-event detector should combine multiple weak cues rather than use one high-frequency threshold.

Candidate feature groups:

- **periodicity / voicing**
  - CPP-like periodicity confidence;
  - harmonicity/HNR;
  - F0 confidence.

- **spectral shape**
  - MFCC-like compact envelope representation;
  - spectral centroid / flatness;
  - broad-band energy distribution;
  - similarity to an adaptive per-singer breath template.

- **temporal context**
  - phrase-edge / pause context;
  - attack/decay envelope;
  - short silence-like edges around the event where present;
  - duration.

- **rejection features**
  - sibilance confidence;
  - plosive/low-frequency transient confidence;
  - strong voiced harmonic confidence.

## Leading hypothesis

First realtime prototype should be conservative and use a feature score, not a hard classifier trained on unknown external data:

`breathScore = noiseLike * pauseContext * spectralMatch * temporalShape * (1 - voicedConfidence) * rejectProtection`

where `rejectProtection` suppresses action when sibilance/plosive/voiced-breathy evidence is strong.

The processor should prefer **under-detection over damaging voiced expression**.

## Candidate processing actions

### A. Event-level gain envelope

Apply bounded attenuation only while breath confidence is high.

Pros:
- low latency;
- transparent when detector is correct.

Risk:
- obvious pumping if event boundaries are wrong.

### B. Spectral breath shaping

Reduce only the most breath-dominant spectral regions.

Pros:
- may preserve expression better than full-band attenuation.

Risk:
- can sound like de-essing or dull the phrase transition.

### C. Hybrid

Moderate full-band attenuation plus gentle spectral shaping.

Current leading hypothesis, but not numerically locked.

## Required research measurements

- labelled breath-event recall/precision;
- separate false-positive rates for sibilants, fricatives, plosives, whispered/breathy phonation, and room noise;
- timing/boundary error;
- singer-to-singer transfer;
- Japanese/Korean/English material where available;
- isolated vocal versus bleed/accompaniment contamination;
- level-matched listening for expressive-naturalness loss.

## Current location

Research.

## Next stage

Review lightweight feature implementations and define a labelled corpus protocol before any realtime DSP constants are locked.
