# Vocal73 R4 — COLOR coefficient-rebuild cadence, source-equation evidence (2026-11-21 JST)

Track: `VOCAL73-1073-IDENTIFIABILITY-001`
Evidence: `EVID-VOCAL73-R4-COEFF-CADENCE-20261121`
Decision: `DEC-VOCAL73-R4-REALTIME-FIXTURE-20261121`
Job: `JOB-VOCAL73-R4-JUCE-ALLOC-001`
Authority: CIPI research only. Product v0.2 unchanged. No hardware fidelity claim.

## Source and distinction from prior tests

Current product: `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp`, baseline blob SHA `691ceb53d773a8d23ed782a33c1c5ca47b29859c`. `prepare()` configures COLOR as a 30 ms JUCE linear `SmoothedValue`. `process()` uses `skip(buffer.getNumSamples())` once per block, then `updateFilters(blockColor,...)`. When `abs(color-lastFilterColor)>0.0005`, two JUCE coefficient factory calls run for low and high shelves and states are assigned. This R4 probe adds a **coefficient factory invocation count / realtime CPU risk** dimension to previous COLOR block-partition tests, not a second test of audio smoothing or actual JUCE execution.

## Reproducible experiment

Code: `research/plugins/vocal73pre/tests/test_filter_update_cadence.py`, commit `dc442aa33e68a0e756fcd8e015e1b66e621861e0`.
Run: `python research/plugins/vocal73pre/tests/test_filter_update_cadence.py -v`
Result in isolated Python 3 environment: **3 tests passed** (0.002 seconds).
Test conditions: 48,000 Hz; COLOR target 0->1 at sample zero; linear ramp length 1,440 samples (30 ms); `lastFilterColor=-1`; threshold strictly >0.0005; total 0.12 s; block size fixed; one source-equation `updateFilters` invocation per block. Predicted coefficient **rebuild events**, each creating *two* shelf coefficient objects:

| Buffer samples | Predicted events | Predicted coefficient-factory calls |
|---:|---:|---:|
| 1 | 1,440 | 2,880 |
| 32 | 45 | 90 |
| 256 | 6 | 12 |
| 2,048 | 1 | 2 |

The last block size crosses the 30 ms ramp within one process block. All above are **model-derived counts**, not measured C++ allocations, CPU timings or audible artifacts. The ramp is assumed to start at zero for controlled comparison; the actual v0.2 initial COLOR state is 0.45 and must be explicitly settled before a real test. Initial coefficient change on first block is included.

## Falsifiable realtime and host test

- Build an isolated JUCE 9.0.2 source-accurate fixture (not a production write); run actual `Vocal73DSP::process` for blocks 1, 32, 256, 2048 with a fixed absolute sample-time automation event and a pre-settled COLOR=0 state. Instrument the coefficient factory call sites and global `operator new` / allocation events during audio-thread processing; report per-block count, worst-case duration, and process input/output hashes. Run ANALOG on/off separately, since `updateFilters` may rebuild both shelves even when ANALOG is off.
- Check whether JUCE coefficient factories allocate on the real-time thread and whether the observed event counts match the source-equation predictions. If not, inspect JUCE smoothing, threshold, reset and parameter automation semantics before changing the model.
- Do not call this a confirmed real-time allocation violation until the fixture is executed. Investigate preallocation/immutable coefficient tables or off-audio-thread updates only after the measured result and review; never blindly change v0.2 preset behavior.

## Lifecycle and gates

Latest CIPI `research/health/automation-status.json`: track `FAILED` / `LATEST_EXTERNAL_ACTION_FAILED` with `scheduler_eligible=false`; Global DAG has no ready external dispatch, 0 dispatched, 29 failed. Earlier MELON job 44714522345 computed and exported its macro result but artifact upload failed with GitHub storage quota, and no accepted artifact was ingested. This external path stays **BLOCKED**; no repeat dispatch or score promotion.
Independent `JOB-VOCAL73-R4-JUCE-ALLOC-001` remains **READY as a research proposal**, not registered as a runnable Global DAG node and not an executed JUCE fixture.
Human Gate: identified/licensed original 1073 measurements, real-vocal blind listening, Cubase 14, pluginval final approval, product integration and release.
Next: compile actual JUCE fixture and execute allocation/CPU instrumentation; after evidence review compare coefficient update design alternatives. Preserve 1970s original vs modern AMS Neve provenance separation.
