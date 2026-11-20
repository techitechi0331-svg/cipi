# Vocal73 R5 — headless transition control correction (2026-11-21 JST)

Track: VOCAL73-1073-IDENTIFIABILITY-001
Evidence: EVID-VOCAL73-R5-CONTROL-MATCH-20261121
Decision: DEC-VOCAL73-R5-CONTROL-MATCH-20261121
Job: JOB-VOCAL73-R5-JUCE-EXECUTE-001
Status: SOURCE_REVIEWED / NOT_COMPILED / NOT_MEASURED

## Source and changes
- CIPI fixture: `research/plugins/vocal73pre/fixtures/juce_headless_v02_probe.cpp`.
- Product source authority unchanged: `techitechi0331-svg/VocalPrepComp/Vocal73Pre` v0.2; DSP blob SHA recorded by track `691ceb53d773a8d23ed782a33c1c5ca47b29859c` (reconfirm on build).
- CIPI commits: `62c00b4d04798390f0753f9c4cdf1ca7acfadb21` (correct ANALOG baseline) and `64c8b0b53f391c5e55c3f61db612b26c01387be6` (pre-switch control and excess-jump outputs).
- Previous fixture incorrectly compared an ANALOG OFF->ON transition to a baseline that was ANALOG ON from sample zero, so pre-switch history differed and post-switch residual conflated history with the actual transition. New `initialAnalog` flag explicitly holds the reference in OFF and the changed run OFF until sample 8192; the changed run switches ON at sample 8192. Other test cases keep their original baseline.
- Added `pre_switch_max_difference` and `excess_jump_at_switch` columns. Pre-switch mismatch >1e-6 logs `INVALID_CONTROL` (currently stderr diagnostic, **not** process failure). `excess_jump_at_switch` is changed sample-to-sample jump minus matched baseline jump; this is a digital discontinuity proxy, **not** a listening result or real hardware click measurement.
- Design fixture: 48 kHz, mono, 16,384 samples, 997 Hz sine amplitude 0.1 + DC 0.04, switch at sample 8192, blocks 32/256/2048; 8192 divisible by each. Deterministic, but **no compiled render hashes or numeric audio outputs yet**.

## Counterfactual test and acceptance
| Case | pre-switch state changed | pre-switch state baseline | post-switch changed | post-switch baseline | pre-switch null expectation |
|---|---|---|---|---|---|
| HPF OFF->80 | HPF OFF | HPF OFF | HPF 80 | HPF OFF | <=1e-6 |
| ANALOG OFF->ON | ANALOG OFF | ANALOG OFF | ANALOG ON | ANALOG OFF | <=1e-6 |
| COLOR 45->100 | COLOR 45 | COLOR 45 | COLOR 100 | COLOR 45 | <=1e-6 |

No numeric signal delta is claimed. A matched pre-switch null is necessary but not sufficient to identify the physical cause of a transient. The test input contains DC and can provoke filter history behavior; a second zero-DC test and a sine-only test are required to separate DC from ordinary switching response. Record actual input/output SHA256, compile versions, run commands and outputs.

## Decision / blockers
- ACCEPT source-level test design correction only. Do not accept a DSP fault, hardware-fidelity metric or product patch without a compiled and executed fixture.
- READY independent: compile and run with pinned JUCE 9.0.2 and exact product source in isolated build directory; make pre-switch mismatch a failing exit status, check finite samples, record reproducible logs and output hashes. Then repeat without DC, with no switch, and at different block sizes.
- BLOCKED dependent MELON path: CIPI health still reports `LATEST_EXTERNAL_ACTION_FAILED` for external R1 job `VOCAL73-1073-IDENTIFIABILITY-001-R1-798D396F`; prior run 44714522345 failed artifact upload due to storage quota. No blind retry and no fabricated results.
- Human Gate: identified original-1970s 1073 reference, calibrated A/B, blind listening, Cubase 14, final adoption/release. WDF/state-space/SPICE/black-box architecture not selected.
- CIPI-only fixture changes; product v0.2 untouched; no budget increase, Cross-Repo Token use or MELON promotion.

Next re-entry: run isolated JUCE fixture and store complete executable evidence; if no verified build environment, continue source-licence ledger without claiming measurements.
