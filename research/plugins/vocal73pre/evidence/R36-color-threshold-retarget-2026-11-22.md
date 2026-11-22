# R36 — COLOR threshold crossing and block-granularity falsification (2026-11-22)

## Provenance and scope
CIPI source of truth: `research/health/automation-status.md`, `research/autonomous_bridge/tracks/VOCAL73-1073-IDENTIFIABILITY-001.yaml`, `research/plugins/vocal73pre/1073-replication-research-plan-v2.md` (read 2026-11-22).
Product DSP `Vocal73Pre/Source/Vocal73DSP.cpp` blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c` (read only). R35 already established block-end `skip()` and premature whole-block switching; do not claim this is newly discovered.
Source lines: 39 (30 ms ramp), 43 (initial COLOR 0.45), 178-185 (set target and skip whole buffer), 195 (EQ update), 217/247 (threshold > 0.00001), 102 (EQ threshold > 0.0005). License: repository source read for internal analysis, no redistribution of JUCE or manufacturer material. No physical 1073 measurement.

## Novel R36 falsifiable test: subthreshold nonzero target vs zero target
Hypothesis: under `juce::SmoothedValue` linear ramp behavior, when the COLOR target is a *nonzero* value below the DSP gate (e.g. 0.000005), the nonlinear and DC stages eventually turn off even though the target is not zero; when target is slightly above gate (0.00002), they remain enabled. The EQ refresh threshold of 0.0005 is independent, so gate transitions can occur without a corresponding EQ coefficient refresh.

Controlled initial value 0.45; set target at buffer boundary; 30 ms ramp, fs=48k or 96k; evaluate buffer lengths 32/256/2048. For linear ramp, crossing index in samples (continuous approximation):
`n_cross = N * (0.45 - 0.00001) / (0.45 - target)` for target < 0.00001, N=0.03*fs.
The first fully disabled block starts at `floor((ceil(n_cross)-1)/B)*B` if threshold is reached by its end; exact boundary equality must be asserted with float32 JUCE values, not inferred from the approximation.

| fs | target | n_cross approximate | B=32 earliest whole-block OFF start | B=256 | B=2048 |
|---|---:|---:|---:|---:|---:|
| 48000 | 0 | 1439.968 | 1408 | 1280 | 0 |
| 48000 | 0.000005 | 1439.984 | 1408 | 1280 | 0 |
| 96000 | 0 | 2879.936 | 2848 | 2816 | 2048 |
| 96000 | 0.000005 | 2879.968 | 2848 | 2816 | 2048 |

At target=0.00002, the gate must stay ON after ramp completion; if it turns OFF, reject hypothesis. For target=0.000005, the first-block gating decision is expected to be OFF at 48k/B2048, despite samples early in that block having a hypothetical sample-accurate COLOR > threshold. The table is **calculated predictions**, not JUCE measurements. The exact JUCE `skip()` semantics and float rounding must be verified by executable fixture.

## Test specification and acceptance
1. Independent JUCE 9.0.2 fixture, float32: reset at 48/96k; setCurrentAndTargetValue(0.45); reset ramp to 0.03 seconds; target=0, 0.000005, 0.00001, 0.00002; B=32/256/2048.
2. Log block start/end, `getCurrentValue()` after `skip(B)`, gate predicate, EQ refresh predicate and actual coefficient hashes; compare sample-by-sample reference using `getNextValue()` on an *independent* smoother. Do not modify production v0.2.
3. Add mid-ramp retarget at 10 ms (to 0.25 and back to 0), documenting whether a new 30ms ramp begins from the current block-end value. Report first OFF block and count of samples for which block gate disagrees with per-sample reference.
4. Fail if predicted predicate differs from actual JUCE results, if mono/stereo differ for identical parameter trajectories, or if buffer-size invariance is falsely asserted. Record compiler, JUCE commit/version, fs, B, input seed, test source hash and output hash.
5. No manufacturer hardware fidelity inference; no product changes or automatic promotion.

## Decision
**KEEP AS UNVERIFIED HYPOTHESIS / READY INDEPENDENT FIXTURE.** Novelty is the subthreshold nonzero target and mid-ramp retarget falsification; prior R35 block-end prediction is baseline only. CIPI external track currently `FAILED` with reason `LATEST_EXTERNAL_ACTION_FAILED` (job `VOCAL73-1073-IDENTIFIABILITY-001-R1-798D396F`); do not dispatch/retry without examining failure and contract/budget. Product write prohibited. No claim of a successful JUCE test.

## Job and resume point
`JOB-VOCAL73-R36-JUCE-GATE-RETARGET-FIXTURE`: READY for independent fixture when an authorized JUCE environment is available; external workflow-dependent execution BLOCKED_EXTERNAL until prior failure is diagnosed. Resume by recording actual block traces and measured disagreement counts, then compare EQ coefficient updates and DC state against R31/R35. Human Gate: original hardware A/B, listening, Cubase 14, final pluginval, product adoption and release.
