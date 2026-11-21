# VOCAL73 R11 — Evidence / Decision / Job (2026-11-21 JST)

## Evidence
- Source of truth: `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp`, blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c` (read this run); `colorSmoothed.reset(sampleRate, 0.03)`; `blockColor = colorSmoothed.skip(buffer.getNumSamples())`; one `updateFilters(blockColor,...)` and `saturateSample(...,blockColor,...)` value per process block.
- CIPI source plan and track reviewed; automation health shows VOCAL73 external job FAILED, scheduler ineligible; do not re-dispatch or infer an audio result.
- New executable synthetic proxy: `research/plugins/vocal73pre/tests/test_color_block_schedule_r11.py`, commit `c133c9510e13597e250ad9815de90e76983dc460`.
- Conditions: 48,000 samples/s, target COLOR 0→1 at sample zero, linear 30ms ramp (1,440 samples), 8,192 total samples, buffer sizes 32/256/2048. This is an **idealized block-end schedule**; it does not implement JUCE SmoothedValue or Vocal73DSP audio.
- First-block COLOR proxy: 32 = 0.0222222222, 256 = 0.1777777778, 2048 = 1.0; 2048-sample block = 42.6666667 ms. These are analytic proxy values, **not measured output**.
- Command: `python research/plugins/vocal73pre/tests/test_color_block_schedule_r11.py -v`. Locally executed: 3 tests PASS (first-block values, cross-buffer disagreement, bounded/finite schedule).
- Distinct from R9 absolute event index equality and R10 source-level risk: R11 asserts a reproducible counterexample for block-constant *parameter trajectories*, not merely event timing.
- Provenance/rights: product code inspected via authorized connected GitHub repository; original manufacturer documentation or licensed hardware audio **not** introduced.

## Decision
- `DEC-VOCAL73-R11`: accept synthetic proxy only as a falsifiable regression fixture; **do not** claim a confirmed JUCE bug, Neve 1073 fidelity, or an actual audio delta.
- Keep v0.2 untouched. Reject automatic product changes and commercial-plugin reference substitution.
- Model discrimination: a sample-accurate ramp and block-constant end-of-block ramp are different hypotheses; compare with exact JUCE output before attributing audible discontinuities.

## Job / re-entry
- `JOB-VOCAL73-R12-JUCE-COLOR-BLOCK` — `BLOCKED_EXTERNAL` for actual JUCE9.0.2 compile/run and captured outputs; independent static review remains READY.
- `external_wait.kind`: JUCE Windows/C++ build and output fixture; `ref`: product `Vocal73DSP.cpp` blob above; `resume_when`: compatible JUCE build environment and repeatable run output available; `resume_step`: compare 32/256/2048 audio sample sequences using aligned absolute automation timing, report max error, RMS, input/output SHA256 and 3-run repeatability.
- Additional READY: verify exact `juce::SmoothedValue::skip` semantics against pinned JUCE9.0.2 source and add a same-target/no-change negative control; avoid claiming exact ramp shape before this.
- Human Gate: original-unit calibrated A/B, listening, Cubase 14, pluginval final, adoption, release.
- Global DAG, MELON Bridge and Cross-Repo permissions unchanged; no external dispatch or product writes.
