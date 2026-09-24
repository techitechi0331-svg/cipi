# Vocal Resonance Suppressor Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/Vocal_resonance
- This formal track preserves the strongest available evidence without promoting undocumented product claims.

## Purpose
Falsification-first vocal resonance detection before any suppressor VST3 is allowed.

## Evidence carried forward

Candidate discovery has now passed its real-vocal budget gate for the current research scaffold.

Primary real-vocal gate:
- 20 identifiable VocalSet singers;
- 40 excerpts;
- four controlled injections per excerpt;
- 160 paired cases;
- Merge-20 recall: 87.50%;
- Merge-15 recall: 76.25%.

Independent confirmation cohort:
- different excerpt rows per singer;
- new injection seed;
- 20 singers / 40 excerpts / 160 paired cases;
- Merge-20 recall: 86.875%;
- Merge-15 recall: 78.125%;
- paired K20-K15 difference: +8.75 percentage points;
- bootstrap 95% interval: approximately +4.38 to +13.13 points;
- 14 improvements / 0 losses.

## Confirmed-for-scope knowledge

- Candidate budget **K=20** is locked for the current candidate-discovery scaffold.
- K=15 is rejected for this scope.
- Real-vocal controlled injection is practical and repeatable in CI without redistributing source audio.
- Observability-aware evaluation remains required; inserted EQ gain is not equivalent to measured spectral effect.

## Still provisional

The merged local + log/ERB proposal architecture is retained as a research scaffold, but its superiority over Local-20 is **not confirmed**.

On the independent confirmation cohort:
- Merge-20: 86.875%
- Local-20: 82.50%
- paired interval for the difference still crosses zero.

Do not convert this directional result into a universal architecture claim.

## Current unresolved problem

**Semantic ranking.**

Candidate discovery can propose useful locations, but the system has not yet proven that it can separate unwanted resonant emphasis from legitimate:
- harmonics;
- formants / singer's-formant structure;
- sibilance/fricatives;
- breath/noise;
- transient consonants;
- high-F0 sparse-harmonic cases.

## Reusable knowledge target

Observability-aware spectral candidate generation, hard sparse candidate budgets, high-F0/formant ambiguity handling, candidate-level semantic ranking, and adversarial real-vocal evaluation.

## Next formal gate

**MODULE 1 v0.4 — Semantic Ranker research and measurement.**

Start with interpretable deterministic / logistic-style candidate scoring. Require clean hard negatives and singer/excerpt-separated validation before any suppressor gain/filter design.

## Promotion rule

Do not mark the overall product track `CONFIRMED` until semantic ranking, suppression DSP, measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
