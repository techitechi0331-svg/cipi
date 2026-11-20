# Vocal73 R1 — reproducible block-held COLOR control-path counterexample (2026-11-20)

Track: `VOCAL73-1073-IDENTIFIABILITY-001` | Decision: `DEC-VOCAL73-R1-CONTROL-PATH-20261120`
Evidence class: **source-derived analytic fixture**, not compiled JUCE, not measured audio, not Neve hardware.

## New falsifiable finding
The current immutable v0.2 `Vocal73DSP::process` advances `colorSmoothed` with `skip(buffer.getNumSamples())`, then applies **one** `blockColor` to the entire block, including its nonlinear tanh stage and both COLOR-linked shelves. `colorSmoothed.reset(sampleRate, 0.03)` specifies 30 ms. Therefore control behavior depends on the audio callback partition, even when sample rate and control automation target are the same.

Assuming JUCE `LinearSmoothedValue` ramp length rounds 48,000 * 0.03 to 1,440 samples, and a 0→1 target jump at the first block boundary, the **first-block** held COLOR values are:

| callback length | duration (ms) | COLOR held during first callback | small-signal tanh-stage gain from 1+0.2*COLOR (dB), shelves excluded |
| ---: | ---: | ---: | ---: |
| 32 | 0.6667 | 0.0222222 | +0.0385 |
| 256 | 5.3333 | 0.1777778 | +0.3035 |
| 2048 | 42.6667 | 1.0000000 | +1.5836 |

These values are **analytical control-path predictions** and intentionally exclude oversampler, filters, host automation scheduling and parameter default state. Exact JUCE 9.0.2 behavior and sound must be verified with a compiled source-accurate harness. Crucially, an entire 2048-sample block receives the final COLOR value rather than a 30-ms within-block ramp. The 32-sample block holds only its end-of-block value. This establishes a source-level buffer partition dependence, not a measured click.

## Reproducible research-only test
File: `research/plugins/vocal73pre/tests/test_v02_block_smoothing_analytic.py`. Command:
`python3 -m unittest research/plugins/vocal73pre/tests/test_v02_block_smoothing_analytic.py -v`
or direct Python invocation. Python stdlib only; 3 test methods. No source modification to `VocalPrepComp`.

## Independent corroboration still required
1. Compile v0.2 JUCE 9.0.2 DSP into a headless harness and compare equal-length renders partitioned into 32/256/2048 samples with identical sample-accurate parameter target events.
2. Record source blob SHA `691ceb53d773a8d23ed782a33c1c5ca47b29859c`, JUCE version, compiler, exact command, input/output SHA256, RMS/peak of render difference, control traces and host timing semantics.
3. Add counterexample to CI: for a fixed automation timeline, require future reference DSP to produce output invariant (within numerical tolerance) to callback segmentation. Do **not** silently change v0.2's existing presets or sound.
4. Check independent HPF state-reset/crossfade, ANALOG bypass discontinuity, real-time coefficient allocation under instrumented Windows build. None is an observed defect until rendered and measured.

## Decision / Job / gates
- **DECISION:** Preserve v0.2; approve research-only fixture and partition-invariance acceptance criterion, not product integration.
- **READY:** `JOB-VOCAL73-1073-R1-BASELINE-001` compile the source-accurate harness and execute actual partition tests.
- **READY:** `JOB-VOCAL73-1073-R1-SCHEMA-002` continue original-vintage versus modern reissue source-and-rights ledger; unknown magnetic constants remain unknown.
- **BLOCKED_EXTERNAL:** MELON `44714522345` evidence upload failed because GitHub artifact storage quota was hit; CIPI track lifecycle is `FAILED`/`LATEST_EXTERNAL_ACTION_FAILED`. Do not count unarchived results, repeat blindly, or bypass CIPI DAG.
- **HUMAN_GATE:** licensed calibrated original hardware A/B, listening, Cubase 14, pluginval final acceptance, product adoption and release.
- **Next:** run source-accurate JUCE harness with deterministic WAVs/hashes once runner and evidence intake are available; keep unrelated READY work active.
