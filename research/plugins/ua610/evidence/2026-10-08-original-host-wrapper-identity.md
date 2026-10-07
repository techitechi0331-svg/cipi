# Original Vocal Pre — dedicated host identity correction and AB acquisition blocker

Date reviewed: 2026-10-08 (JST)
CIPI track: `UA610_ORIGINAL_VOCAL_PRE`
Status: additive research evidence; no confidence/current_stage change; no CONFIRMED promotion.

## SOURCE_FACT

- Product repository `techitechi0331-svg/610`, branch `original-vocal-pre-v0.1`, reviewed HEAD `1bb4277c3886e3c5b135af73ad451a7a7247bc88`.
- The user reported a severe practical fault when selecting Mic 2k / Mic 500 in what was presented as the Original product. Subsequent source inspection established an **artifact/host-wrapper identity mismatch**: an earlier artifact named `Original-Vocal-Pre-Windows-VST3` had built the preserved `UA610Model` wrapper rather than a dedicated Original processor. The +30 dB Mic behavior alone was not the full root cause.
- The current `CMakeLists.txt` has separate JUCE targets `UA610Model` and `OriginalVocalPre`. The latter compiles `Source/OriginalPluginProcessor.cpp` and `Source/OriginalPluginEditor.cpp`.
- The current Original processor uses `vocalpre::OriginalPreampModel` and exposes exactly four parameters: `input`, `character`, `tone`, `output`. It has no Line / Mic 2k / Mic 500 selector. The 610 wrapper still exposes the Mic modes and remains a separate research target.
- The Original Windows workflow explicitly builds `UA610Model_VST3` and `OriginalVocalPre_VST3` and uploads them from different target-specific VST3 paths to `610-Research-Windows-VST3` and `Original-Vocal-Pre-Windows-VST3`, respectively.
- Source-level default Original tuning remains **provisional** balanced: Drive 6 dB, output flux x8, saturation/hysteresis x0.125, clean Character compensation enabled. This is not a listening winner or parameter lock.
- Earlier CIPI note `research/plugins/ua610/evidence/2026-09-25-mic-input-daw-safety.md` remains historically valid for the intermediate DAW-safe 610-wrapper investigation, but must **not** be used as proof that the dedicated Original VST3 should retain Mic modes. This note is an additive architectural correction, not a deletion of historical evidence.

## MEASURED / WORKFLOW-OBSERVED

- Windows `Original Vocal Pre Research` Run 59, `36179835447`, source SHA `1bb4277c3886e3c5b135af73ad451a7a7247bc88`, completed SUCCESS on 2026-09-25.
- The run reports PASS for preserved 610 baseline regression, Original automation regression, build of extended analyzers and both VST3 targets, Original shortlist/compensation/performance steps, and distinct VST3 artifact upload steps. The run lists artifacts `Original-Vocal-Pre-Windows-VST3` and `610-Research-Windows-VST3` as separate nonexpired archives.
- This evidence is **build/workflow evidence**, not yet a claim of Cubase Pro 14 host validation, Steinberg validator or pinned pluginval completion.
- Separate `original-vocal-ab-experiment` branch at `c2950da842454f10faff7f1f4b3362f0878f1e87` diverges from the product branch: 17 commits ahead and 15 behind as of this review. AB renders from this branch must not be represented as tests of the latest product HEAD until code provenance is reconciled.
- Real-vocal AB Run 17, `36179723464`, attempt 1 failed at the approved Wikimedia source download step on 2026-09-25 with HTTP 429. CMake/build and hosted performance reference succeeded; the vocal render, source hashes and blind artifacts did not run. This is an acquisition failure, not a DSP rejection.
- A retry of the failed AB job was requested on 2026-10-08; its result is pending at the time of this evidence note.

## INFERRED

- The dedicated four-control host architecture is the appropriate correction to the user's Original-product Mic-mode bug; merely attenuating Mic gain in a 610 wrapper is insufficient to establish product identity.
- An AB corpus fetch retry or an approved alternative acquisition path is needed; do not weaken acoustic gates or choose a listening winner in response to HTTP 429.
- The AB experiment's code divergence is a reproducibility/provenance concern independent of source acquisition. Reconcile with the latest product source before accepting an AB decision for the release candidate.

## HYPOTHESIS

- Once approved vocal material is available and the AB renderer is aligned to the product implementation, level-matched blind comparisons may distinguish conservative, balanced and color-contrast settings and reveal whether spectral protection is perceptually useful.

## REJECTED

- Treating a renamed `UA610Model` artifact as an Original VST3 product.
- Exposing Line/Mic 2k/Mic 500 in the dedicated four-control Original product.
- Declaring the Original Mic bug resolved solely by `dawSafeMicInput` while host-wrapper identity remains wrong.
- Inferring a product winner from numerical measurements, or treating HTTP 429 as a DSP failure.

## Outstanding gates

1. Confirm AB retry outcome and preserve failed acquisition logs.
2. Resolve public-vocal acquisition through approved, reproducible, license-documented sources, without committing raw audio.
3. Reconcile AB code provenance with latest product branch before interpreting renders.
4. Level-matched blind real-vocal AB and listening review.
5. Final numerical/IMD/alias/CPU/latency/state/automation checks; Steinberg validator and pinned pluginval; Cubase Pro 14 user-side host/listening verification.
6. Keep CIPI track PROVISIONAL. No main push, confidence/current_stage mutation, CONFIRMED auto-promotion or product release by automated worker.

Evidence URLs:
- https://github.com/techitechi0331-svg/610/actions/runs/36179835447
- https://github.com/techitechi0331-svg/610/actions/runs/36179723464
- https://github.com/techitechi0331-svg/610/blob/original-vocal-pre-v0.1/CMakeLists.txt
- https://github.com/techitechi0331-svg/610/blob/original-vocal-pre-v0.1/.github/workflows/original-vocal-pre.yml
- https://github.com/techitechi0331-svg/610/blob/original-vocal-pre-v0.1/Source/OriginalPluginProcessor.cpp
