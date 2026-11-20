# Vocal73 R4 — source-linked JUCE headless fixture handoff (2026-11-21 JST)

Track: VOCAL73-1073-IDENTIFIABILITY-001
Decision: DEC-VOCAL73-R4-FIXTURE-20261121
Job: JOB-VOCAL73-R4-JUCE-FIXTURE-001
Status: SOURCE_ADDED / NOT_COMPILED / NOT_EXECUTED
Authority: CIPI research evidence only; no automatic product modification or fidelity claim.

## Evidence and exact changes
- Current CIPI main checked before changes: 8d593417d544c8798828b2e17cff1a9318533b25.
- Health source: research/health/automation-status.md and .json. VOCAL73 lifecycle FAILED (LATEST_EXTERNAL_ACTION_FAILED), external R1 job VOCAL73-1073-IDENTIFIABILITY-001-R1-798D396F. This is the MELON artifact-quota dependent path; no accepted R1 result.
- Track and research plan reviewed: research/autonomous_bridge/tracks/VOCAL73-1073-IDENTIFIABILITY-001.yaml and research/plugins/vocal73pre/1073-replication-research-plan-v2.md.
- Product source and header read directly: VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp blob 691ceb53d773a8d23ed782a33c1c5ca47b29859c; header bb3026cd2065a1bba80ec80eea358d4ff40d1ddf. v0.2 unchanged.
- Existing earlier source-equation, DC blocker, HPF state and coefficient-cadence probes were not rerun or duplicated.
- NEW source-linked fixture: research/plugins/vocal73pre/fixtures/juce_headless_v02_probe.cpp (commit 8ec70644813d937f0eda5d9a648192d32fe11eb4).
- NEW JUCE CMake wiring: research/plugins/vocal73pre/fixtures/CMakeLists.txt (commit 107ab9be7c716ae15526fe12a7c062e7f3accd69).

## Executable design and limits
The fixture directly compiles the **actual unmodified** Vocal73DSP.cpp and calls its public prepare/process interface. It renders 48kHz mono deterministic 997Hz sine at 0.1 peak plus 0.04 DC; 16,384 samples, switch at sample 8,192, buffer sizes 32/256/2048. Three independently varied controls: HPF 0->80Hz, ANALOG OFF->ON, COLOR 45->100%. For each it reports latency, finite outputs, post-switch max/RMS difference versus a fixed-control reference and peak magnitude in the 8-sample-before/64-after window. It does NOT measure transient clicks in isolation; steady-state transfer changes also contribute to differences, so a separate level-matched local discontinuity test is needed before calling a click a bug. The ANALOG comparison deliberately uses a constant-ON reference and must not be interpreted as pure switch transient.
No test has yet run; no numerical output or build PASS is claimed. CMake may require extra JUCE modules/platform linkage; first compile is the next falsification gate. The fixture does not yet output input/output hashes, so outputs are **exploratory only** and cannot satisfy the R1 baseline acceptance contract or be promoted to measured evidence until SHA256 capture, binary/source/fixture provenance, calibration and full logs are added.

## Reproduction commands (unexecuted)
With JUCE 9.0.2 checkout and VocalPrepComp checkout, from the CIPI fixture directory:

```sh
cmake -S . -B build -DJUCE_DIR=/absolute/path/to/JUCE -DVOCAL73_SOURCE_DIR=/absolute/path/to/VocalPrepComp/Vocal73Pre/Source -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target vocal73_probe
./build/vocal73_probe
```

Windows executable path depends on CMake generator (e.g. build/Release/vocal73_probe.exe). Verify compiler, JUCE revision, product DSP blob SHA, source checkout, CMake and executable hash before any measurement. Do not build in or modify product checkout.

## Decision, blocker, next jobs
- DECISION: accept source-level fixture **as uncompiled research implementation only**. Keep original v0.2 unchanged. Do not promote source-level expectations to real 1073 fidelity.
- READY: JOB-VOCAL73-R4-JUCE-FIXTURE-001: compile with JUCE 9.0.2, fix fixture-only build errors, run deterministic 3x3 switching matrix, capture source/fixture/binary/input/output SHA256, exact toolchain, numerical CSV, and controlled switch-click discriminator (local discontinuity against no-switch, with matched steady-state response). Run with process CPU/allocation instrumentation after baseline correctness.
- READY: independent primary-source provenance ledger with rights and original-vs-modern revision tags.
- BLOCKED_EXTERNAL: MELON artifact quota and R1 macro result intake; no automatic rerun until quota and retry budget verified. R4 physical fidelity BLOCKED_REFERENCE until licensed calibrated original unit data.
- HUMAN_GATE: physical A/B, subjective listening, Cubase Pro 14, pluginval final, adoption and release.
- No new MELON dispatch, no Cross-Repo Token or Global DAG mutation, no product write.
