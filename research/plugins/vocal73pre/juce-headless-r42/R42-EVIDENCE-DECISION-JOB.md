# R42 — executable JUCE DSP harness, NOT YET EXECUTED
Date: 2026-11-22 JST. Product authority: VocalPrepComp/Vocal73Pre v0.2. CIPI research only.

## Evidence
- Read CIPI main: research/health/automation-status.md, track VOCAL73-1073-IDENTIFIABILITY-001.yaml, 1073-replication-research-plan-v2.md; last relevant CIPI commit R41 844834960161acb9a2f960144b810ce860900d86.
- Source examined: VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp SHA(blob) 691ceb53d773a8d23ed782a33c1c5ca47b29859c; DSP header SHA bb3026cd2065a1bba80ec80eea358d4ff40d1ddf; CMake uses JUCE 9.0.2.
- CIPI health: scheduler IDLE/NO_READY_WORK; 1073 external track FAILED due to latest external action failed. Prior MELON workflow 44714522345 uploaded 0 of 14 evidence files due to artifact quota; research steps had succeeded. This run did NOT delete artifacts or claim quota recovery.
- New CIPI-only executable harness: juce-headless-r42/CMakeLists.txt and main.cpp, calling the ACTUAL product Vocal73DSP::prepare/process (not a Python oracle), generating deterministic 0.12-peak sine signals and printing per-condition output RMS, peak, reported latency, and finite flag. Covers 48/96kHz x 32/256/2048 blocks x mono/stereo x ANALOG off/on x HPF off/80Hz x COLOR 0/50 x 80/1000Hz = **192 conditions**. Each condition is 0.25s, first 0.1s excluded from output metric to reduce transient bias. Exit nonzero on nonfinite output or negative latency. NOTE: this does not yet directly instrument EQ coefficient update count, DC gate, or oversampler invocation.
- Execution status: **NOT EXECUTED**. No JUCE source checkout/build or Windows runner was available in this tool session. Thus zero actual DSP sample measurements, zero pass/fail claims. CMake/harness compilation is unverified.

## Reproduction (Windows PowerShell, checkout CIPI and VocalPrepComp as sibling folders)
```powershell
cmake -S .\cipi\research\plugins\vocal73pre\juce-headless-r42 -B .\build-v73-r42 -G "Visual Studio 17 2022" -A x64 -DVOCAL73_SOURCE_DIR="$PWD\VocalPrepComp\Vocal73Pre"
cmake --build .\build-v73-r42 --config Release --target vocal73_headless
.\build-v73-r42\Release\vocal73_headless.exe > .\v73-r42.csv
```
First compile and run are mandatory before accepting results; record compiler/OS/JUCE revision, exit code, raw CSV and summary, latency consistency across ANALOG states, and compare HPF-off/on 80Hz response. If build fails, record exact diagnostic and patch harness only. Avoid uploading large artifacts while quota blocked; persist compact numeric summaries and hashes in CIPI within authority.

## Decision
- P0: real JUCE execution and measurable DSP behavior, not more synthetic COLOR boundary matrices.
- P0 infrastructure: unblock MELON artifact storage by reviewing retention/large artifacts and approved safe cleanup; do not delete unreviewed evidence or increase spend without authorization.
- P1: use actual measurement to select source-constrained transformer/Class A/inductor-EQ candidates, then separate research implementation; no hardware fidelity claim.
- NOT_NEEDED: additional synthetic-only COLOR gate recitations. DEFERRED: commercial plugin as fidelity oracle, nonessential DSP embellishments.
- Human Gate unchanged: licensed original 1073 measurements/A-B, level-matched blind listening, Cubase 14, final pluginval, product adoption and release.

## Next Job
1. Execute the 192-condition JUCE harness on the available Windows runner, save actual CSV + compile log + pass/fail to CIPI Evidence. Verify that source/header are the product SHA above or record changed SHA.
2. Add sample-exact parameter transition and harmonic/aliasing probes only after the baseline compiles; record THD/IMD methods and limitations. Avoid conflating test sine with hardware A/B.
3. Diagnose GitHub artifact quota usage and select safe retention / small evidence channel; retry only after quota recovers, with CIPI Cross-Repo/No-Wait budgets.
4. If only Human Gate work remains, stop generating low-value research jobs and report autonomous-work-converged awaiting human evidence.
