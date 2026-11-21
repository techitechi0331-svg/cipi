# Vocal73 R32 — COLOR gate boundary audit (2026-11-22)

## Evidence (source-derived, not hardware/JUCE runtime)
- Product authority: `techitechi0331-svg/VocalPrepComp`, `Vocal73Pre/Source/Vocal73DSP.cpp` on main, read-only. Relevant lines: 39 (`colorSmoothed.reset(sampleRate,0.03)`), 179 (`setTargetValue(color)`), 185 (`blockColor = colorSmoothed.skip(buffer.getNumSamples())`), 195 (`updateFilters(blockColor,...)`), 217 (nonlinearity gate), 247–248 (DC blocker gate).
- The same strict predicate `analogEnabled && blockColor > 0.00001f` controls saturation and DC processing, while `updateFilters` receives the **block-end smoothed COLOR**. This creates a potentially testable distinction between requested COLOR, smoothed COLOR, and whether the DC state is advanced.
- Prior R31 defined sample-exact JUCE DC oracle; this R32 adds a **separate boundary and gating control oracle** to prevent false interpretation of R31 data.

## Numerical truth table (pure predicate; no audio inference)
COLOR values below are *normalized values passed to the predicate*, not UI percentages:
| analogEnabled | blockColor | saturator enabled | DC stage enabled |
|---|---:|---|---|
| false | 1.0 | no | no |
| true | 0 | no | no |
| true | 0.000009 | no | no |
| true | 0.000010 | no | no (strict greater-than) |
| true | 0.000011 | yes | yes |
| true | 0.45 | yes | yes |

Threshold in normalized COLOR units: 0.00001 = 0.001% of full-scale COLOR range (assuming 0–1 maps to 0–100%). The exact first enabled **block** depends on JUCE smoothing and block segmentation, not solely on the UI target. No measured first-block index is claimed.

## Falsifiable isolated test (READY independent of external 1073 runner)
1. In a standalone fixture, record each block's requested COLOR, `blockColor`, ANALOG flag, `nSamples`, and both gate predicates. Use rates 48/96 kHz and lengths 32/256/2048; include target changes 0 -> 0.000009 -> 0.000010 -> 0.000011 -> 0.45 -> 0.
2. Verify that the two gate flags are equal at every block; if not, this source-derived oracle is falsified. At a strict equality boundary the expected flag is false. Log float32 bit pattern, because literal decimal values can round.
3. Record exact block where `blockColor` crosses threshold and where DC state begins/stops advancing. Re-run with the same sample-absolute target changes but different block partitions; classify any discrepancy as smoothing/block scheduling, **not** hardware fidelity.
4. Cross-check the actual product's pre-DC capture from R31 against these gate flags; do not infer reset semantics from output differences alone.

## Decision
- ACCEPT as a **test-control refinement**, not a DSP change. Do not substitute a synthetic `blockColor` or assume sample-accurate parameter changes.
- REJECT claims of JUCE execution, original 1073 equivalence, or improved sound. v0.2 product unchanged.
- R31 DC-state oracle remains the primary executable next step; R32 gate logging is a prerequisite for interpreting its results.

## Job / continuation
- READY (CIPI research-only): add block-level gate trace and threshold assertions to an isolated JUCE 9.0.2 fixture; save compiler/JUCE SHA, input SHA256, block partition, target timeline, float32 blockColor, gate flags, and failing indices.
- BLOCKED dependent work: external VOCAL73 track marked FAILED / LATEST_EXTERNAL_ACTION_FAILED in `research/health/automation-status.md`; do not dispatch/retry outside Global DAG / budget and authority checks.
- HUMAN GATE: original 1073 hardware A/B, licensed reference audio, blind listening, Cubase 14, final pluginval, product adoption/release.
