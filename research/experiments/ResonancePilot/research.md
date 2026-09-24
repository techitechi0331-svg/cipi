# CIPI ResonancePilot 0.1 Research Track

## Research target

Develop a singing-specific dynamic resonance controller that reduces genuinely excessive narrow/persistent spectral structures without flattening intentional harmonics, vowels, formants, or singer-formant/ring energy.

## SOURCE_FACT

VOX-001 establishes that vocal-tract resonances strongly shape the spectral envelope and contribute to timbre, loudness, efficiency, and phonemic information. A spectral peak is not automatically equivalent to a physical vocal-tract resonance.

VOX-002 shows that conventional formant estimation can be biased in high-pitched singing because sparse, strong pitch harmonics dominate the spectral structure. This is directly relevant to any detector that naively labels local spectral maxima as "resonances."

VOX-003 documents legitimate trained-singing energy concentrations in approximately the 2–4 kHz region and, in some groups/conditions, around 8–9 kHz. A vocal-only suppressor must therefore avoid treating those regions as intrinsically undesirable.

RES-001 demonstrates an implementable automatic resonance-attenuation family: FFT analysis, psychoacoustically motivated band partitioning, estimation of a general spectral shape, peak/threshold comparison, and time-varying IIR peak attenuation.

RES-002 demonstrates automated peak identification and high-Q parametric suppression in a room-resonance context. It is useful methodologically but room modes are not equivalent to vocal resonances.

## INFERRED

For singing, spectral **prominence alone is insufficient**. A safer detector should consider at least:

- prominence above a local spectral envelope;
- estimated bandwidth / Q;
- persistence across frames;
- relationship to estimated F0 and its harmonics;
- broad spectral/formant context;
- level-normalized behavior.

A narrow peak locked exactly to a harmonic should receive more protection than an equally prominent non-harmonic narrow peak, especially at high F0 where harmonic spacing is sparse.

## HYPOTHESIS

Candidate detection score:

`score(k,t) = prominence(k,t) * narrowness(k,t) * persistence(k,t) * harmonicRiskWeight(k,t)`

where `harmonicRiskWeight` reduces suppression confidence near plausible F0 harmonics rather than increasing it.

A separate broad-envelope protection term may be needed around legitimate formant/singer-formant structures.

## Candidate architecture — not locked

`input -> STFT/analysis -> local spectral envelope -> peak prominence -> peak width -> temporal tracker -> F0/harmonic guard -> suppression targets -> bounded realtime gain/EQ stage -> output`

Two implementation families remain open:

1. **Spectral gain field**
   - high selectivity;
   - potentially more latency and phase/time-frequency artifacts.

2. **Tracked dynamic IIR peak filters**
   - lower processing latency;
   - finite number of resonances;
   - requires stable peak tracking / coefficient motion.

## Critical failure modes

- suppressing ordinary harmonics in high-pitched vocals;
- flattening vowel/formant identity;
- suppressing desirable singer-formant/ring energy;
- filter chatter as peaks move between bins;
- musical "lisp"/dullness caused by confusing sibilance with resonance;
- overreaction to breath/noise;
- excessive latency for tracking/live monitoring;
- time-frequency smearing if spectral processing is chosen.

## Research measurements required

Before implementation promotion:

- synthetic harmonic stack with known formant envelope;
- same stack with injected narrow non-harmonic resonances;
- F0 sweep through low/high singing ranges;
- prominence and false-positive rate versus F0;
- persistence discrimination;
- injected-Q discrimination;
- singer-formant protection test;
- labelled real-vocal corpus;
- latency/CPU estimate for spectral versus tracked-IIR implementation.

## Current location

Research.

## Next stage

Compare spectral-envelope estimators, F0/harmonic guards, and realtime suppression topologies. No production DSP constants are locked yet.
