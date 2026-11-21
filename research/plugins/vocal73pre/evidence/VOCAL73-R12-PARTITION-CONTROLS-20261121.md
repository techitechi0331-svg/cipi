# VOCAL73 R12 — Evidence / Decision / Job (2026-11-21 JST)

## Evidence
- Read CIPI main automation-status, VOCAL73 track and research-plan-v2, latest R11 commit and product DSP source (blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`). R11 already covers changing COLOR proxy; R12 adds unchanged-target negative control and settled-tail invariance.
- Product source: `colorSmoothed.reset(sampleRate, 0.03)`, `colorSmoothed.skip(buffer.getNumSamples())`, block-level `updateFilters` and `saturateSample`; no direct JUCE execution this run.
- Test: `research/plugins/vocal73pre/tests/test_color_partition_r12.py`, commit `fe7410b8c60c9ad9b6180671365bc130da20bbba`.
- Reproduce: `python research/plugins/vocal73pre/tests/test_color_partition_r12.py -v`; locally 4/4 tests PASS.
- Synthetic conditions: 48 kHz, 30ms = 1440 samples, 8192 samples, block sizes 32/256/2048; block-end piecewise-constant proxy, target 0→1; unchanged-target control 0.45→0.45.
- Numerical comparison: first-sample proxy COLOR 32=0.02222222, 2048=1.00000000, max pairwise absolute delta=0.97777778. Unchanged-target control: max pairwise delta=0. Settled tail samples [4096,8192): max pairwise delta=0. No audio output, THD, hardware or JUCE measurement.
- Provenance/rights: authorized connected GitHub source inspection; no manufacturer copyrighted schematic, licensed hardware audio or commercial-plugin measurements used.

## Decision
- DEC-VOCAL73-R12: accept proxy as a negative-control test of the *experimental harness*, not evidence of actual JUCE behavior or Neve fidelity. Block-size-dependent ramp schedule is falsifiable, but cannot be attributed to a DSP defect without actual JUCE build and output comparison.
- Do not change Vocal73Pre v0.2, CIPI Global DAG, Cross-Repo token/permissions or MELON contract.

## Job / re-entry
- JOB-VOCAL73-R13-JUCE-SMOOTHEDVALUE: READY for pinned JUCE9.0.2 source review of `SmoothedValue::skip` semantics and isolated C++ unit test; do not infer semantics from this proxy.
- JOB-VOCAL73-R12-JUCE-AUDIO: BLOCKED_EXTERNAL until JUCE9.0.2 compile/run fixture and captured 32/256/2048 audio output are available; then align absolute automation sample, compare max/RMS error and SHA256, repeat 3 times. Existing R6-R11 test infrastructure should be reused, not duplicated.
- External MELON track: FAILED / scheduler ineligible in reviewed health snapshot; do not blindly redispatch.
- Human Gate: calibrated original 1073 hardware A/B, listening, Cubase 14, final pluginval, product adoption/release. No sound-quality or match-percentage claim.
