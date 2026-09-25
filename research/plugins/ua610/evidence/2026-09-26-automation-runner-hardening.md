# Original Vocal Pre — automation and runner hardening

Date: 2026-09-26

## SOURCE_FACT

Research OS:
- `techitechi0331-svg/cipi`
- knowledge track: `UA610_ORIGINAL_VOCAL_PRE`

Product repo:
- `techitechi0331-svg/610`
- product branch: `original-vocal-pre-v0.1`
- vocal AB branch: `original-vocal-ab-experiment`

Runner failure evidence:
- Original research Run `36177831783` / job `108212661021` failed before configure.
- Root log error: Windows PowerShell refused the generated temporary `.ps1` because script execution was disabled.
- Checkout itself completed successfully.
- The failure was therefore runner shell policy, not DSP, CMake configure, compiler, analyzer, or VST3 failure.
- The overload artifact upload also failed because no gate output existed after the earlier shell failure; this was a secondary failure, not the root cause.

Runner hardening:
- PowerShell workflow steps now explicitly use `-ExecutionPolicy Bypass -File {0}`.
- Main branch hardening commit: `40f618e8009fe2a2c55a5e6455dbad53cb525f93`.
- AB branch hardening commit: `6edb27af40ab0f53311851b9ea0a15f3628dd6da`.
- A later AB run (`36178036758`) completed Checkout, Resolve local CMake, and Prepare persistent JUCE cache successfully before entering Configure. This is direct evidence that the ExecutionPolicy repair cleared the previous shell-policy failure point.

Build/cache hardening:
- Self-hosted workflows now create a persistent per-user JUCE 9.0.2 FetchContent base directory.
- When `juce-src/CMakeLists.txt` is already present, configure requests `FETCHCONTENT_FULLY_DISCONNECTED=ON`.
- Goal: eliminate repeated JUCE downloads on subsequent self-hosted runs while keeping first-use bootstrap available.

## INFERRED

Static review found an automation-safety asymmetry in the Original model:
- Tone coefficient changes already use 2 ms Biquad coefficient smoothing.
- Tube feedback target changes already use approximately 1.5 ms smoothing.
- Output gain already uses 20 ms smoothing.
- Input gain was previously read directly from `controls.inputDb` inside the oversampled analog sample path.
- Character pre-drive was previously applied directly from `currentPreDriveDb`.
- Therefore stepped host automation of Input or Character could introduce a block-boundary gain discontinuity even though the other control-dependent paths were smoothed.

The host-facing processor already reports the oversampling latency through `setLatencySamples()`, and APVTS state/parameter IDs remain stable in the current implementation.

## HYPOTHESIS

Per-channel 2 ms smoothing for Input gain and Character pre-drive should:
- remove the block-boundary discontinuity;
- preserve settled static gain and existing steady-state tone/distortion measurements;
- preserve stereo matching;
- avoid changing Plugin ID, Parameter IDs, state format, UI, or historical 610 research behavior.

Candidate product-only implementation:
- `a7e752a6a9b5a79ec185cbd7476ff780ef48087d`: add per-channel gain smoothers.
- `9bebdcf010d306720aa315a298933005e73927bc`: apply 2 ms smoothing to Input and Character pre-drive.

A dedicated regression analyzer was added:
- `76cfda259a86b8d8b96dfb77553596768b37c395`: automation step analyzer.
- `109063da6e55eed0787cfee13b5c97de209cb593`: CMake target.
- `1f0ad46c9603c9437892e4304b19d29c8676c038`: workflow gate.

The analyzer linearizes the Original signal path to isolate control-gain transitions, then checks:
- first-sample jump as a fraction of the final gain step;
- settled analytical gain error;
- finite output;
- stereo channel matching.

## SIMPLE BASELINE

CPU measurement now includes an oversampling-only baseline:
- same JUCE FIR oversampling topology;
- no Original nonlinear/circuit processing.

This allows the measured cost of oversampling filters to be separated from the nonlinear/tube/transformer model cost.

Implementation:
- `d8ddc5b1cb262e5902b2c7b41ede3ab0656ae4ea`.

The timed benchmark region was also tightened so test-signal synthesis and finite-output validation are outside the timer:
- `c330c303f171472bdc920c1b5f56db78faf7a9f3`.

## AB FAIRNESS HARDENING

Static review found that the first AB renderer delayed the bypass to the maximum latency but did not explicitly add the missing delay to a processed path if 610 and Original native latencies differed.

The renderer now:
- measures native 610 and Original latencies independently;
- chooses one common maximum latency;
- applies explicit extra alignment delay to any lower-latency processed render;
- records native latency, common aligned latency and added alignment delay in `ab_metrics.csv`.

Implementation:
- main: `d3a0b96037bd2923b12dfabd52f1aa023983192a`;
- AB branch sync: `6bd49e9ab62f8d15eaa19487dc202e762ab18caa`.

## REJECTED

- Treating Run 50 as a DSP/build failure.
- Continuing to depend on `lukka/get-cmake` for the self-hosted runner.
- Treating a queued or configuring workflow as a reason to stop all work.
- Selecting a final Original profile before automation regression, CPU/latency evidence and level-matched real-vocal AB.
- Assuming common oversampling settings automatically guarantee identical rendered alignment without recording native latency.

## STATUS

- Runner shell-policy root cause: identified and patched.
- Persistent JUCE cache: implemented; full end-to-end reuse still awaiting a completed subsequent run.
- Input/Character automation smoothing: implemented, **PROVISIONAL pending regression measurement**.
- Automation regression analyzer: implemented, **pending Windows execution**.
- CPU simple-baseline measurement: implemented, **pending Windows execution**.
- Real-vocal AB alignment hardening: implemented, **pending renderer build and rendered evidence**.
- Cubase Pro 14 host validation remains open and must not be auto-closed.
