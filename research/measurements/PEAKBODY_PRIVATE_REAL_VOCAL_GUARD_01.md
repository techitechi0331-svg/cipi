# PeakBody Private Real-Vocal Guard Validation 01 — Result

Classification: **MEASURED / INCONCLUSIVE**  
Raw audio committed: **NO**

## Decision

**INCONCLUSIVE**

The locked protocol requires adequate proxy counts before interpreting the candidate as PASS or REJECT.

The private same-performance corpus contained:

- **246** noise-like high-band crest proxy frames;
- **11,969** low-frequency transient proxy frames;
- **10,612** strong periodic voiced/body proxy frames;
- **0** bright voiced crest proxy frames.

Because the required bright voiced proxy count was at least 30, the study cannot validate the most important synthetic success: protection of bright high-F0 periodic material.

The detector is therefore **not promoted and not rejected** from this private study.

## MEASURED findings

### Processing-variant stability

Four processing variants of the same approximately 68.36 s vocal performance were analysed.

Median pairwise transient-factor correlation:

- broadband baseline: **0.91121**
- periodicity-protected candidate: **0.90420**
- change: **-0.00700**

Protocol gates:

- candidate correlation median >= 0.80: **PASS**
- candidate correlation not more than 0.05 below baseline: **PASS**

This supports stability across the tested dereverb/clarity/compression-style processing changes.

### Low-frequency transient preservation

Pooled proxy count: **11,969**

Retention relative to broadband-crest baseline:

- median: **1.000**
- p10: **1.000**
- minimum observed aggregate frame ratio: **0.481**

Protocol median/p10 preservation gates both **PASS**.

### Strong periodic body invariance

Pooled proxy count: **10,612**

Mean absolute candidate-vs-baseline transient-factor delta:

- **0.000**

Gate <= 0.03: **PASS**.

### Noise-like high-band behavior

Pooled proxy count: **246**

Candidate/baseline transient-factor retention:

- median: **0.49262**
- p10: **0.38918**
- p90: **0.68649**
- minimum: **0.35326**

Protocol target median <= 0.35: **NOT MET**.

This does not by itself produce a REJECT decision because the same locked protocol is inconclusive when any required proxy class lacks the minimum sample count.

It does show that the private real-vocal material is materially less separable than the synthetic sibilance/breath cases.

### Bright voiced high-band protection

Pooled proxy count: **0**

The study cannot evaluate the bright high-F0 protection criterion.

This is the dominant data-coverage gap.

## Source privacy / identity

Four private processing variants were bound by SHA-256 before analysis.

Only aggregate, non-reversible metrics are stored in CIPI.

No:

- raw audio;
- frame timecodes;
- spectral images;
- per-frame feature arrays

are committed.

The four variants represent the **same vocal performance** and must not be interpreted as four independent singers.

## INFERRED

The periodicity-protected guard is more stable than the rejected spectral-only hypothesis, but the synthetic noise-rejection strength does not transfer directly to this private processed vocal.

The largest current uncertainty is not low-frequency transient preservation or processing invariance. It is **coverage of genuinely bright periodic high-band singing and realistic noise-like consonant/breath events across different singers/registers**.

## HYPOTHESIS

A production detector may need one or more of:

- a stronger realtime voicing confidence feature;
- context-aware hysteresis;
- a continuous rather than hard spectral/periodicity interaction;
- singer/register-aware harmonic protection.

No such change is justified by this single-performance study alone.

## Next research gate

Acquire or access a broader public/private singing corpus with:

- multiple singers;
- high-register material;
- sibilance/breath/noisy consonants;
- note/F0 annotation where possible.

Keep the current Revision 02 + periodicity-protected guard as the **leading hypothesis**, but do not alter its thresholds based on this incomplete private study.
