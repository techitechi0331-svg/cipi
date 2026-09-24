# Vocal Resonance MODULE 1 v0.4R.4 Clean-Negative Audit Review

Date: 2026-09-25

Source run:
`research/runs/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/gha-36070450907-1/`

## Review verdict

**ITERATE.**

The diagnostic cohort is sufficient to show substantial clean false-trigger subgroup variation, but it is not sufficient to authorize a new ranker feature family or to accept the high-F0 coverage claim.

## MEASURED

- 32 clean excerpts
- 4 held-out singers
- 5 resolved techniques
- overall clean false-trigger: **31.25%**

Technique:
- belt: **0/5 = 0%**
- breathy: **2/8 = 25%**
- fast_forte: **3/8 = 37.5%**
- fast_piano: **5/8 = 62.5%**
- lip_trill: **0/3 = 0%**

Singer:
- f9: **4/8 = 50%**
- m10: **5/8 = 62.5%**
- m11: **0/8 = 0%**
- m9: **1/8 = 12.5%**

Technique false-trigger spread: **62.5 percentage points**.

## REJECTED

The earlier small-subset clue that **lip_trill is the dominant clean false-trigger condition** did not reproduce. Audit-001 measured 0/3 lip-trill false triggers.

Do not build lip-trill-specific protection from that earlier clue.

## High-pitch measurement caveat

Audit-001 used the R3 framewise ACF proxy with a search ceiling of 1000 Hz.

In the 32 excerpts:
- 7/32 have old ACF p90 exactly 1000 Hz;
- 8/32 have old ACF p90 >=900 Hz;
- 23/32 have old ACF p95 exactly 1000 Hz.

This boundary saturation makes octave/harmonic errors a material alternative explanation. Therefore the existing p90>=400 group is preserved as measured output but **not accepted as validated high-F0 ground truth**.

The predeclared high-pitch hypothesis also did not pass: 37.5% for the p90>=400 group was not at least overall 31.25% + 15 points.

## Additional confound

All selected Audit-001 basenames are arpeggio excerpts. Technique effects are therefore not separated from exercise-family effects.

## INFERRED

Clean false triggers are not uniformly distributed in this cohort. Both technique and singer show large variation, so a technique-specific causal explanation remains premature.

## Next gate

Run an independent re-audit that:
1. excludes every Audit-001 basename;
2. spans more than one exercise family;
3. freezes the exact Audit-001 static reference ranker and threshold;
4. reports a conservative YIN-style pitch proxy alongside the legacy ACF proxy;
5. treats ACF/YIN disagreement as uncertainty.

Only if the subgroup concentration replicates should event-context feature research begin.
