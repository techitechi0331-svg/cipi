# Vocal73 R6 — zero-DC counterfactual and fail-closed headless fixture (2026-11-21 JST)

Track: VOCAL73-1073-IDENTIFIABILITY-001
Evidence: EVID-VOCAL73-R6-TRANSITION-MATRIX-20261121
Decision: DEC-VOCAL73-R6-FAIL-CLOSED-20261121
Job: JOB-VOCAL73-R6-JUCE-RUN-001
State: SOURCE_ONLY / NOT_COMPILED / NOT_MEASURED

## Provenance and delta
- Read current CIPI main, automation-status.md, track YAML, v2 research plan and R5 fixture evidence before changing code.
- Product authority remains `techitechi0331-svg/VocalPrepComp/Vocal73Pre` v0.2; track-pinned DSP blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c` must be reverified at build. No product writes.
- Research fixture updated at `research/plugins/vocal73pre/fixtures/juce_headless_v02_probe.cpp`; commit `06546183275ecefed4e292d76a25ff4ab93cfce2`.
- R5 logged pre-switch mismatch but still exited zero. R6 changes the exit contract to code 2 on nonfinite render, unequal latency, or pre-switch difference > 1e-6. Both changed and baseline outputs are checked for finiteness.
- R6 adds zero-DC paired control to the existing 0.04-DC experiment. Input: 0.1 peak, 997 Hz sine, 48 kHz, 16,384 samples; transition at sample 8192; blocks 32, 256, 2048; unchanged pre-switch states and matched baselines.
- CSV case labels include `_WITH_DC` or `_ZERO_DC`. Cases: HPF OFF->80, ANALOG OFF->ON, COLOR 45->100, each for both DC offsets and each block size.

## Deterministic design matrix (test counts, not audio measurements)
| Variable | Values | Count |
|---|---|---:|
| Block size | 32, 256, 2048 | 3 |
| DC offset | 0.04, 0 | 2 |
| Transition | HPF, ANALOG, COLOR | 3 |
| **Comparison rows** | 3 × 2 × 3 | **18** |

At 48 kHz the 8192-sample pre-switch period is 170.667 ms; the full render is 341.333 ms. Transition time is block aligned for all three sizes. A paired `_WITH_DC` vs `_ZERO_DC` difference can suggest DC-state involvement but is not sufficient to attribute a physical mechanism, distinguish signal history from coefficient switching, or establish audible clicking. `excess_jump_at_switch` is a sample discontinuity proxy, not dBFS click measurement. The 997 Hz input is not a measured original-1073 reference.

## Acceptance and missing evidence
- **Source-level**: added a deterministic falsifiable comparison and fail-closed control invariant. This is the only accepted result.
- **Not executed**: no verified JUCE 9.0.2 toolchain or product-source checkout in this run; therefore no C++ compile, rendered audio, SHA256 outputs, pluginval, CPU measurements, or hardware fidelity values. The code has not been proven to compile.
- Next job READY (independent): verify JUCE 9.0.2 and DSP source SHA, configure and build fixture, run the 18-case matrix, capture stdout/stderr/exit status, binary SHA256, compiler/JUCE versions and input/output hashes. Add no-switch reference and explicit per-sample sample history before any root-cause assertion. Validate no real-time allocation separately.
- External MELON job `VOCAL73-1073-IDENTIFIABILITY-001-R1-798D396F` still `FAILED` in current CIPI health; prior run 44714522345 artifact upload failed due to GitHub Actions quota. Do not retry blindly or treat missing artifacts as completed research. Only this dependent path is BLOCKED.
- Human Gates remain identified original 1970s Neve unit/calibrated A/B, blind listening, Cubase Pro 14, product adoption and release. No WDF/state-space/SPICE/black-box architecture selected and no fidelity percentage claimed.

Decision: preserve v0.2; continue only independent READY fixture verification and provenance research under CIPI No-Wait, unchanged budgets and Global DAG.
