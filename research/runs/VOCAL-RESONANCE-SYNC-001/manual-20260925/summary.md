# Vocal Resonance evidence reconciliation

This manual import reconciles the CIPI track with the latest target-repository evidence and the decisions made in the development chat.

## Important contradiction retained and resolved by scope

Two confirmation cohorts exist:

1. a preliminary per-singer `skip=2` cohort:
   - Merge-20 = 86.875%
   - Merge-15 = 78.125%
2. a later stricter cohort that explicitly excluded the 40 primary examples:
   - Merge-20 = 85.0%
   - Merge-15 = 74.375%
   - Local-20 = 85.0%

Both are retained. The stricter explicit-exclusion cohort is preferred for future reporting of the independent confirmation number.

The K=20 over K=15 conclusion survives the stricter cohort:
- paired difference = +10.625 percentage points;
- bootstrap 95% interval = +6.25 to +15.625 points;
- 17 improvements / 0 losses.

Merge-20 superiority over Local-20 is not supported in the stricter cohort:
- both = 85.0%;
- paired bootstrap interval for the difference = -5.625 to +5.625 points.

## Semantic-ranker history

- v0.4 logistic ranker: NO-GO.
- v0.4R.1 pairwise case-relative ranker: REJECTED because it worsened Top-5, strong-effect Top-5, and clean false triggers.
- v0.4R.2 causal safe-negative ranker: improved Top-5 to 46.875% versus a 37.5% prominence baseline, but remains NO-GO because strong-effect ranking did not improve and clean false triggers remained 37.5%.

## Product state

No suppressor DSP, VST3, or Cubase release candidate exists. This is intentional; MODULE 1 semantic ranking remains a blocker.
