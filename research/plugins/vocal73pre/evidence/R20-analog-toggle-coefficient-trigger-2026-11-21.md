# R20 — Vocal73Pre coefficient-update trigger separation (2026-11-21)

## Evidence
- Source inspected live: `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp`; baseline `Vocal73Pre v0.2`. Prior R19: CIPI commit 6882d0aa5333da5d7be59e14c165066a9163b43d. Source inspection only, not an audio benchmark.
- CIPI health: `VOCAL73-1073-IDENTIFIABILITY-001` FAILED / `LATEST_EXTERNAL_ACTION_FAILED`, scheduler ineligible. Research Gate on R19 commit succeeded (Actions run 44887606920); this does not validate DSP runtime.
- Rights: repository source inspected for analysis; no proprietary schematic, hardware capture or licensed original 1073 measurement used.

## New falsifiable observation
R19 identified redundant shelf factory calls with ANALOG OFF. The v0.2 source additionally uses a **single** `toneChanged` predicate for both the color-dependent shelf coefficients and the ANALOG enable transition:
`abs(color-lastFilterColor)>0.0005 || analogEnabled!=lastAnalogEnabled`.
Thus a flag-only ANALOG OFF→ON event at fixed COLOR necessarily requests both shelf coefficient factories once; a subsequent ON→OFF event requests them again with unity gains. These two events are distinct from COLOR automation. This follows the control flow, but the exact JUCE allocation behavior remains unknown.

## Isolated regression specification (not executed)
At 48 kHz, stereo, 256 frames/block, 0 dB input/output, HPF OFF, COLOR held at 50%, run:
A. Warm up with ANALOG OFF, then remain OFF for 10 blocks.
B. Toggle OFF→ON at block boundary, then hold ON for 10 blocks.
C. Toggle ON→OFF, then hold OFF for 10 blocks.
D. With ANALOG OFF, automate COLOR 50→100% and hold.
E. Repeat B/C with COLOR=0%, so coefficient construction is distinguished from audible nonlinear effects.

Instrument per-block `hpfFactoryCalls`, `shelfFactoryCalls`, allocation count and bytes on callback thread, wall-clock microseconds, output SHA256 (outside callback), plus `lastFilterColor` and `lastAnalogEnabled` snapshots. Warm-up counts must be reported separately. Predicted **source-level** B and C: 0 HPF factories and 2 shelf factories each, assuming no HPF change and exactly one process call per event. A steady-state block: 0 shelf factories after initialization. D: at least one shelf refresh is possible, count depends on COLOR smoothing/threshold. E: toggles still request coefficient factories despite zero COLOR. Do not present predictions as measurements.

## Decision and job
- DECISION: Keep v0.2 product unchanged; classify source-level unnecessary recomputation candidate only. Do not claim real-time allocation, glitch, hardware fidelity, or fixed percent similarity.
- READY: inspect exact JUCE 9.0.2 `IIR::Coefficients::makeLowShelf/makeHighShelf` and `ProcessorDuplicator`/filter state ownership, preserving upstream commit and line references; prepare nonallocating test counters.
- BLOCKED_EXTERNAL: instrumented Windows JUCE/VST3 execution, pluginval and Cubase until authorized environment available. Failed MELON track is not retried automatically; no scheduler, budget, DAG or product write.
- HUMAN_GATE: licensed original 1073 unit A/B, level-matched blind listening, Cubase 14 confirmation, product adoption, release.
- Resume with actual per-event factory counts, audio-thread allocations, timing distributions and sample hashes; only then decide whether isolated precomputation is worth prototyping.
