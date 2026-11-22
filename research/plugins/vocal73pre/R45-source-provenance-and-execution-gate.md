# Vocal73Pre — source provenance gate, 2026-11-22 (R45)

## Evidence: verified this run
- CIPI latest main inspected: health `research/health/automation-status.md`, active foundation track `VOCAL73-1073-IDENTIFIABILITY-001.yaml`, research plan v2, R44 job and current headless harness.
- Source `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp` inspected directly: 2x oversampling, color-smoothing, tanh shaping, HPF choice 2 = 80 Hz, fixed-shelf EQ and conditional DC blocker. No original hardware measurement is implied.
- R44 runner previously accepted arbitrary local JUCE checkout and did not record either git SHA in the output. A test performed with the wrong JUCE version could have been incorrectly labeled a 9.0.2 result.
- CIPI commit `c810e3774bb9b332e0497b8be6e6ebdc7e559349` now requires JUCE source HEAD to match its local `9.0.2` tag commit and requires verifiable product source git HEAD; both SHAs are added to `run_summary.json` on attempted measurement. This is a provenance/measurement integrity fix, **not** a successful JUCE build or a measured audio improvement.
- Git source access from the current isolated execution environment was attempted: `git ls-remote https://github.com/juce-framework/JUCE.git refs/tags/9.0.2` returned `Could not resolve host: github.com`. No local JUCE or VocalPrepComp checkout was present. Actual JUCE audio measurements **0 / 192**. No new CPU/THD/IMD figures.
- Previous MELON workflow `techitechi0331-svg/melon/actions/runs/44714522345`: export succeeded but upload failed on artifact storage quota; no evidence of recovery or new successful export in this run.

## Decision and priority
- **P0 BLOCKED (environment-dependent)**: run the existing 192-condition actual-DSP harness on a machine with pinned JUCE 9.0.2 checkout and product git checkout. Do not replace with Python proxy or synthetic CSV.
- **P0 BLOCKED (quota-dependent)**: resolve GitHub artifact storage limit or use a contract-compliant upload-free evidence route; avoid blind retries and avoid paid quota expansion.
- **FIXED (research infrastructure)**: refuse unknown JUCE source versions and record product/JUCE commit provenance. This does not validate the C++ build or numerical accuracy.
- **NOT_NEEDED**: further paper-only COLOR boundary tables; repeated synthetic pass reports.
- **DEFERRED**: WDF/state-space/SPICE selection and product DSP edits until real baseline and licensed primary-reference constraints are available.
- **Human Gate**: identified 1970s unit A/B, listening, Cubase 14, final pluginval, product adoption and release.

## Next independent action
Use the already-committed `juce-headless-r42/run_headless.py` with `--source`, `--juce`, `--build`, `--out` on the Windows runner or any provisioned machine. Save `run_summary.json`, compiler/CMake versions, `measured.csv` hash, 192-row acceptance, failing logs and minimal evidence in CIPI. If JUCE 9.0.2 source tag is absent, obtain/verify it through authorized runner setup before attempting measurements. Product v0.2 unchanged. No analog-fidelity completion claim.
