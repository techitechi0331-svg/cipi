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

---

# Evidence reconciliation — 2026-09-25

The original independent-confirmation paragraph above is preserved as history. It describes the preliminary `skip_per_singer=2` confirmation run.

A later and stricter confirmation run explicitly excluded all 40 primary examples.

## Strict explicit-exclusion confirmation

Target Actions run: `36052307694`

- Merge-20: **85.00%**
- Merge-15: **74.375%**
- Local-20: **85.00%**
- paired Merge-20 minus Merge-15: **+10.625 points**
- bootstrap 95% interval: **+6.25 to +15.625 points**
- discordant wins/losses: **17 / 0**
- Merge-20 minus Local-20: **0 points**
- paired interval: **-5.625 to +5.625 points**

Decision:
- keep K=20 locked for the current candidate-discovery scaffold;
- keep K=15 rejected;
- do **not** claim Merge-20 is superior to Local-20;
- prefer the strict explicit-exclusion numbers in future summaries while retaining the earlier preliminary cohort.

## Semantic Ranker v0.4

Measured:
- Top-5: 34.375%
- strong-effect Top-5: 53.846%
- clean false trigger: 25.0%
- gate: NO_GO

## Semantic Ranker v0.4R.1 — pairwise case-relative

Measured:
- Top-5: 31.25%
- strong-effect Top-5: 46.154%
- clean false trigger: 37.5%

Decision: **REJECTED** for this scope.

## Semantic Ranker v0.4R.2 — causal safe-negative supervision

Measured:
- generator ceiling: 87.5%
- Top-5: 46.875%
- Top-5 given generator hit: 53.571%
- prominence baseline Top-5: 37.5%
- strong-effect Top-5: 46.154%
- clean false trigger: 37.5%
- gate: NO_GO

Interpretation:
- safer labels improved overall Top-5;
- strong-effect ranking and clean false-trigger behavior remain inadequate;
- model complexity should not be increased blindly;
- the next falsifiable question is whether F0/harmonic motion coherence adds useful protection/context.

## Next formal gate

**MODULE 1 v0.4R.3 — F0 / Harmonic Motion Coherence.**

Research must compare against:
1. v0.4R.2 safe-negative static ranker;
2. simple local-prominence baseline.

No production suppressor or VST3 is authorized.


---

# MODULE 1 v0.4R.3 Review — Motion Coherence

Autonomous run `VOCAL-RESONANCE-R3-MOTION-001 / gha-36069680311-1` completed under the CIPI free worker.

Measured locked-test result:
- static R2-style Top-5: 40.625%;
- motion R3 Top-5: 31.25%;
- static strong-effect Top-5: 60.0%;
- motion strong-effect Top-5: 53.33%;
- clean false-trigger: 25.0% for both;
- retention gate: **REJECTED**;
- product gate: **FAILED**.

The tested F0/harmonic-motion feature bundle is rejected for this scope.

Important caveat:
- the run contained zero test cases under the predeclared median-F0 >=500 Hz high-F0 definition, so high-F0 behavior remains unresolved.

## Next formal gate

**MODULE 1 v0.4R.4 — Adversarial Clean-Negative / Pitch-Coverage Audit.**

Do not add another model family until false-trigger subgroups and pitch coverage are measured on a broader disjoint clean cohort.


---

# MODULE 1 v0.4R.4 Clean-Negative Audit — assistant review

Run: `VOCAL-RESONANCE-R4-CLEAN-AUDIT-001 / gha-36070450907-1`

Measured:
- 32 clean excerpts / 4 test singers / 5 techniques;
- overall clean false-trigger: **31.25%**;
- belt 0%, breathy 25%, fast_forte 37.5%, fast_piano 62.5%, lip_trill 0%;
- singer range: 0% to 62.5%.

Review:
- subgroup concentration is retained as cohort-level evidence;
- the earlier lip-trill-specific clue is **REJECTED** because it did not reproduce;
- high-F0 coverage is **UNRESOLVED** because the legacy ACF proxy frequently saturates at its 1000 Hz search boundary;
- all Audit-001 excerpts were arpeggios, so exercise-family confounding remains.

Next:
**MODULE 1 v0.4R.4b — Independent Clean-Negative Re-audit.**

No new semantic model family is authorized before that replication.
