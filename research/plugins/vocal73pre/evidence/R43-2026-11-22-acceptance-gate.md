# Vocal73Pre R43 — executable CSV acceptance gate (2026-11-22)

## Baseline and authority
- Product: `techitechi0331-svg/VocalPrepComp/Vocal73Pre` v0.2; no product changes.
- CIPI main R42 headless JUCE harness at `research/plugins/vocal73pre/juce-headless-r42/` (192 conditions).
- This round adds `check_csv.py`, a post-run acceptance check. It is **not** DSP audio measurement, JUCE build evidence, or Neve 1073 hardware fidelity evidence.
- CIPI health at inspection: VOCAL73-1073-IDENTIFIABILITY-001 `FAILED`, reason `LATEST_EXTERNAL_ACTION_FAILED`; next scheduler action `IDLE`, no local READY jobs.

## Executed and observable
- Inspected current CIPI health, track, plan, latest R42 commits and product `Vocal73DSP.h/.cpp`.
- Verified product DSP entry points: `prepare(sr, block, channels)`, `process(buffer, inputDb, colorPercent, outputDb, hpfChoice, analogEnabled)`, `getLatencySamples()`. R42 harness matches these signatures.
- Added deterministic post-run CSV gate: exactly 192 unique tuples, finite/nonzero RMS and peak, nonnegative latency, ANALOG-off COLOR invariance, HPF 80 Hz attenuation, buffer-independent reported latency.
- Local Python 3 execution against a **synthetic CSV fixture** generated with the 192 prescribed tuples returned `PASS: 192 ...; 96 invariance/HPF checks; stable reported latency`. The fixture is **synthetic**, not JUCE output; therefore 0 real-DSP conditions have been measured in this round. Missing-path negative control returned nonzero exit and `FAIL` as expected.
- No artifacts uploaded, no paid storage usage, no external runner invoked. GitHub file commit: `237a7fb29e3d5b0b760a2d0f6c91af27465a10df`.

## Decision
- **READY**: run the existing R42 JUCE 9.0.2 harness in an environment with JUCE source, VocalPrepComp checkout, and a C++ toolchain, pipe CSV to `check_csv.py`; collect raw rows and failing conditions as compact GitHub text evidence.
- **BLOCKED (dependent only)**: the MELON R1 external track remains FAILED because upload-artifact storage quota prevented evidence upload; do not blindly retry the identical upload.
- **BLOCKED (local environment)**: container has cmake/g++ but cannot resolve github.com, and JUCE 9.0.2 source is not locally available; no honest JUCE build or audio measurement can be claimed.
- **DEFERRED**: WDF/SPICE/model replacement until the current real-DSP baseline is measured and original-hardware provenance is sufficient.
- **NOT_NEEDED**: more COLOR threshold paper tests, or additional R numbers without runnable test improvement.
- **Human Gate**: licensed original-unit measurements, level-matched blind listening, Cubase 14, final pluginval, product adoption and release.

## Reproduction / next resume
1. With authorized checkouts, run `cmake -S research/plugins/vocal73pre/juce-headless-r42 -B build/vocal73 -DVOCAL73_SOURCE_DIR=/path/to/VocalPrepComp/Vocal73Pre` (requires JUCE 9.0.2 FetchContent access).
2. Run `cmake --build build/vocal73 --config Release`; execute `vocal73_headless` and redirect stdout to `r42-measured.csv`.
3. Run `python3 research/plugins/vocal73pre/juce-headless-r42/check_csv.py r42-measured.csv`. Preserve exact commands, compiler/JUCE version, CSV summary and failures in CIPI Evidence. Do not upload a GitHub Actions artifact until quota is restored; use small commit or job log if permitted.
4. Investigate failures before changing v0.2, and preserve Human Gates.
