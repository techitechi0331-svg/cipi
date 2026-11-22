# Vocal73Pre R44 — executable JUCE measurement entrypoint (2026-11-22)

## Evidence (actual vs unverified)
- CIPI commit `17662c1a5fd3d8cc12e403b5a61a087d937c713b` adds `juce-headless-r42/run_headless.py`.
- The runner requires a local VocalPrepComp/Vocal73Pre checkout and a **local JUCE 9.0.2 source checkout**. It passes `FETCHCONTENT_SOURCE_DIR_JUCE` to CMake, avoiding network downloads of JUCE. It compiles the actual product `Vocal73DSP.cpp`, runs the 192-condition R42 harness, checks the measured CSV with the R43 acceptance gate, and emits a small `run_summary.json` plus logs and SHA-256 of successful measured CSV.
- Verified in this execution: the source-side JUCE tag `9.0.2` resolves on GitHub; the product `Vocal73DSP.h/.cpp` method signature matches the harness calls; CMake, C++ compiler and Python are present in the current Linux environment, but **JUCE source checkout and VocalPrepComp checkout are not locally present**, and network git access failed with DNS resolution error. The new runner was committed, but its full end-to-end execution has **not** been validated. **Measured JUCE audio rows: 0.** No sound-quality or original-1073 fidelity inference is justified.
- Previously observed MELON run `44714522345`: research and export succeeded, artifact upload failed with `Artifact storage quota has been hit`. No new successful artifact upload or quota reset verified this round.
- Example on a machine with source checkouts: `python research/plugins/vocal73pre/juce-headless-r42/run_headless.py --source C:/src/VocalPrepComp/Vocal73Pre --juce C:/src/JUCE --build C:/tmp/v73-build --out C:/tmp/v73-evidence`.
- The local execution is not a substitute for Windows VST3, pluginval, Cubase 14, or hardware A/B.

## Decision
- Priority P0: execute the real DSP measurement gate with local JUCE and product sources. **No synthetic CSV accepted as physical evidence.**
- Priority P0: resolve MELON artifact quota or avoid artifact uploads while preserving CIPI contract; do not retry identical failed upload blindly.
- **NOT_NEEDED**: additional COLOR boundary-value paper matrices or synthetic-only pass counts.
- **DEFERRED**: circuit-model selection and product modifications until actual baseline is captured and sources are provenance checked.
- Keep product v0.2 untouched. The runner is infrastructure only and cannot establish hardware accuracy.

## Job / resume
1. On a machine with JUCE 9.0.2 and VocalPrepComp sources, run the command above, inspect `run_summary.json`, retain raw `measured.csv`, and record the source and JUCE commit SHAs, compiler/CMake versions, numeric pass/fail and run times.
2. If build fails, fix the specific compiler error and rerun; no fabricated measurements.
3. If pass, compare the 192-condition CSV for unexpected behavior, then create a narrow experiment for HPF/EQ response and CPU/aliasing.
4. Keep quota-dependent MELON import **BLOCKED** only for the dependent branch; independent local validation remains READY.
5. Human Gate remains: identified original-1073 A/B, level-matched listening, Cubase 14, final pluginval, adoption/release.

## Status
Infrastructure entrypoint committed; actual JUCE DSP execution **BLOCKED by unavailable local source checkouts/network**, not by a demonstrated DSP failure. No new release claim.
