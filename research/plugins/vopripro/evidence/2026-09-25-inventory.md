# VoPriPro evidence inventory — 2026-09-25

## Provenance

- CIPI source baseline: `main@4a4c150daaa6d740d9a63812c387778167bf2f5d`.
- Product repository: `techitechi0331-svg/VocalPrepComp`.
- Product evidence baseline: `main@cc796d30d7e1885e0ca66caaf7f1b02d0bffeb33`.
- Product identity: **VoPriPro v0.1**; internal CMake target remains `VocalPrepComp` for compatibility.
- Main Windows VST3 validation run: `36062768701` — SUCCESS.
- Main real-vocal validation run: `36062768702` — SUCCESS.
- Main VST3 artifact: `10834934001`, GitHub artifact digest `sha256:8bd284a46a4c3ca108b02cae996a39ba843f68bfc6d1557bbcf67c02c89090c4`.
- Main real-vocal artifact: `10836287907`, GitHub artifact digest `sha256:d7efccb6c4a2a493d59915ff389a7e3655b40e3b224e44966c66d119a7e96432`.
- Raw vocal audio is **not** imported into CIPI. Only derived CSV/text evidence and hashes are preserved here.

This record imports the current product-repository evidence into CIPI without promoting subjective claims that have not been listened to or target-host claims that have not been run in Cubase Pro 14.

## Existing evidence reused from CIPI

No new compressor theory research was required before this sync. The following CIPI assets already cover the reusable foundations:

- `research/dynamics/COMPRESSOR_CORE.md`: feed-forward/log-domain compressor baseline, explicit one-pole timing convention, quadratic soft knee.
- `research/dynamics/ADAPTIVE_BALLISTICS.md`: adaptive crest/timing remains hypothesis-level until corpus and listening evidence justify it.
- `research/measurements/COMPRESSOR_MEASUREMENT.md`: static/dynamic detector and trajectory measurement protocol.
- `research/measurements/VST3_CONFORMANCE_FINDINGS.md`: external validators catch host-facing defects not guaranteed to appear in ordinary DSP/build tests.
- `research/SOURCE_LEDGER.md`: DRC-001/002/003/004, JUCE and Steinberg VST3 sources already registered.
- `research/plugins/vopripro/`: existing formal product track, previously waiting for registered real-vocal AB evidence.

## SOURCE_FACT

The following are direct product-repository facts for `cc796d30`.

### Product purpose and public controls

VoPriPro is a transparent pre-mix vocal dynamics processor for stabilising vocal level/peaks before downstream EQ, de-essing and colour/main compression.

Public UI:

- INPUT: -12..+12 dB, default 0 dB.
- AMOUNT: 0..100%, default 50%.
- CHARACTER: 0..100%, default 50% Natural.
- OUTPUT: -12..+12 dB, default 0 dB.

Auto output normalisation/Auto Level is not part of the final v0.1 design.

### Product signal flow

`Input -> DC blocker 5 Hz -> split`

Calibration path before INPUT:

`80 Hz Q~0.707 HPF -> fixed Peak/RMS 35/65 -> Active Level -> Auto Threshold`

Compression path:

`INPUT -> 80 Hz Q~0.707 detector HPF -> CHARACTER Peak/RMS blend -> feed-forward gain computer -> GR envelope -> OUTPUT -> linked sample-peak limiter -> output`

The calibration path is before INPUT; the compression detector is after INPUT. INPUT therefore drives compression without moving the calibration reference by the same amount.

### Locked v0.1 numerical map

Natural 50:

- Ratio 2.7:1.
- Calibration GR 3.0 dB.
- Max GR 6.0 dB.
- Attack tau 20 ms.
- Release tau 110 ms.
- Peak/RMS amplitude blend 35/65.
- Knee 12 dB.
- Detector HPF 80 Hz.
- RMS exponential power tau 25 ms.
- Activity gate -55 dB.
- Startup bootstrap duration 200 ms.
- Bootstrap up/down tau 10/30 ms.
- Long active-level up/down tau 2000/8000 ms.
- INPUT/OUTPUT smoothing 25 ms multiplicative.
- AMOUNT/CHARACTER smoothing 50 ms sample-level.
- Linked sample-peak limiter: -1.0 dBFS, ~1 ms lookahead, 50 ms release.

AMOUNT anchors:

| Amount | Ratio | Calibration GR | Max GR |
|---:|---:|---:|---:|
| 0% | 1.0:1 | 0.0 dB | 0.0 dB |
| 10% | 1.2:1 | 0.5 dB | 1.0 dB |
| 25% | 1.5:1 | 1.2 dB | 2.5 dB |
| 40% | 2.1:1 | 2.2 dB | 4.5 dB |
| 50% | 2.7:1 | 3.0 dB | 6.0 dB |
| 60% | 3.1:1 | 3.7 dB | 7.0 dB |
| 75% | 3.6:1 | 4.7 dB | 8.5 dB |
| 90% | 4.2:1 | 5.7 dB | 9.5 dB |
| 100% | 4.5:1 | 6.0 dB | 10.0 dB |

CHARACTER anchors:

| Character | Attack tau | Release tau | Peak/RMS |
|---:|---:|---:|---:|
| 0% Smooth | 8 ms | 180 ms | 20/80 |
| 25% | 13 ms | 145 ms | 28/72 |
| 50% Natural | 20 ms | 110 ms | 35/65 |
| 75% | 31 ms | 80 ms | 50/50 |
| 100% Punch | 45 ms | 60 ms | 65/35 |

### Realtime/state facts

- Audio path has no deliberate file I/O/network/sleep/mutex wait.
- Limiter sliding maximum uses preallocated monotonic-queue storage.
- Character envelope coefficients use a prepared 1001-point sample-rate-specific LUT.
- NaN/Inf inputs are contained.
- Mono/stereo are supported.
- The reported DAW latency equals the limiter lookahead.
- Legacy states lacking INPUT/OUTPUT are migrated with 0 dB defaults without overwriting existing old parameter values.
- The JUCE high-level VST3 path is not claimed to reconstruct every intra-block host automation point sample-accurately.

## MEASURED

### Main VST3 / regression gate

Run `36062768701` at product commit `cc796d30` passed:

- Configure.
- Debug VST3 build.
- Release VST3 build.
- DSP regression test build.
- DSP regression execution.
- pluginval 1.0.4, Strictness 10.
- VST3 artifact upload.

The regression matrix in the product repo covers silence; Character direction; INPUT/threshold separation; OUTPUT; absence of Auto Level; mono/stereo; 44.1/48/88.2/96/176.4/192 kHz; block 32..2048; limiter; first-note startup; legacy state migration; parameter motion; DC; extreme finite values; and NaN/Inf.

This is external plug-in validation evidence, but it is **not** Cubase Pro 14 real-host evidence.

### Main real-vocal engineering gate

Run `36062768702` at `cc796d30` used four public adult singing recordings from HUST_Solfege:

- `man1_twinkle.wav`
- `man4_twinkle.wav`
- `woman1_twinkle.wav`
- `woman3_twinkle.wav`

Six product conditions per recording:

- Amount25-Natural
- Amount50-Smooth
- Amount50-Natural
- Amount50-Punch
- Amount75-Natural
- DrivePlus6

Result:

- 4 files processed.
- 24 DSP cases.
- 24 PASS / 0 hard failures.
- no NaN/Inf failures.
- all cases respected the -1.0 dBFS sample-peak safety ceiling within the declared numerical tolerance.
- gain-matched A/B WAV rendering succeeded.
- Natural50 limiter-use warnings (>0.25 dB block maximum): 0.

For Natural50 across the four recordings:

- 100 ms active-window P90-P10 dynamic-range reduction: **3.6985..4.8724 dB**, median **4.17195 dB**.
- output active-RMS match gain required for A/B: **4.9559..5.2391 dB**, median **5.0545 dB**.
- block-max compressor GR p50: **3.2424..4.2525 dB**, median **3.73495 dB**.
- block-max compressor GR p95: **5.9997 dB** on all four.
- max compressor GR: **5.9997 dB** on all four, matching the configured Natural50 6 dB cap.
- limiter max GR: **0.0 dB** on all four.
- crest-factor change: **-0.9991..+0.6051 dB**, median **-0.4077 dB**.

For DrivePlus6:

- output sample peak was **-1.0000 dBFS** on all four.
- limiter max GR was **0.9442..1.3809 dB**, demonstrating emergency peak limiting under stronger drive.

These values are objective engineering measurements only. They do not establish subjective preference or “professional mix” quality.

## INFERRED

- Natural50 behaves consistently enough on this small adult four-recording corpus to justify continued listening evaluation rather than an immediate numerical rollback.
- Because Natural50 reached its 6 dB GR cap at p95/max on all four files, the current mapping often operates at its intended ceiling on these sources. That is not itself a defect, but it makes broader-corpus and listening evidence important before claiming universal naturalness.
- The zero limiter activity in the four Natural50 renders supports the narrower inference that the final safety limiter did not materially shape those four Natural50 cases.
- DrivePlus6 confirms that INPUT remains a meaningful drive control and that the final limiter acts as a safety stage under stronger level, but it does not prove that +6 dB drive is aesthetically desirable.

## HYPOTHESIS

The following remain testable product-tuning hypotheses rather than shared truths:

- fixed 35/65 Natural detector blending is perceptually optimal or near-optimal across diverse singers;
- fixed 80 Hz detector HPF is broadly optimal for singing voices;
- fixed 12 dB knee is broadly optimal;
- 10/30 ms bootstrap and 2/8 s long Active-Level tracking are perceptually optimal;
- Natural50 is a generally preferred default after strict level matching;
- program-dependent release, crest-adaptive timing, percentile thresholding or a transient-specific detector would materially improve this product over the current simpler baseline.

CIPI already contains reusable adaptive-ballistics research, so these hypotheses should be compared against the simple current v0.1 baseline rather than researched from zero.

## REJECTED / retained negative evidence

Scope is important: these are rejected approaches or v0.1 product choices, not universal claims.

### Product-scope rejections for v0.1

- Auto Level / automatic output normalisation: removed; manual OUTPUT retained.
- True-peak limiting/oversampling: not justified for this pre-mix safety-limiter role in v0.1.
- Saturation/harmonic coloration: excluded from the transparent v0.1 product objective.
- Program-dependent release, crest-adaptive Character, percentile/median Auto Threshold, adaptive noise-floor gate and transient-specific secondary detector: not promoted without comparative real-vocal evidence.

### Build/validation negative evidence

These failures are retained because they are reusable CI/host-engineering evidence:

1. Run `36006545078`: self-hosted Windows Configure failed because PowerShell script execution was disabled. Explicit `-ExecutionPolicy Bypass` fixed the workflow class of failure.
2. Run `36020763317`: Configure failed because `cmake` was not on the self-hosted runner PATH. A workflow-local portable CMake setup removed this machine-state dependency.
3. Run `36035980367`: pluginval printed `SUCCESS`, but direct PowerShell `$LASTEXITCODE` handling produced an empty value and falsely failed the job. Using `Start-Process -Wait -PassThru` and its process `ExitCode`, plus checking the `SUCCESS` marker, made the gate reliable.
4. Run `36051325254`: the first real-vocal validation tool build failed under JUCE 9 because `WavAudioFormat::createWriterFor` requires a `std::unique_ptr<juce::OutputStream>&`, not `unique_ptr<FileOutputStream>`. Upcasting ownership before the call fixed it.

No negative result above is removed because the final build later succeeded.

## Listening record

A prior user impression in the development conversation described an earlier build as sounding good. It was not a blinded or gain-matched review of `main@cc796d30`, so CIPI must not promote it into MEASURED listening evidence.

The current main artifact contains delay-aligned, active-RMS-matched Natural50 A/B WAVs, but a formal human KEEP/REVISE/ROLLBACK decision has not yet been recorded.

## Cubase / host status

- Windows VST3 build: PASS.
- pluginval 1.0.4 Strictness 10: PASS.
- Product artifact produced from current main: PASS.
- Cubase Pro 14 scan/load/playback/automation/save/reopen on the user's actual machine: **not yet verified**.
- Steinberg official VST3 validator is not currently recorded for this VoPriPro main candidate.

CIPI's existing conformance research shows pluginval and Steinberg's official validator are complementary; therefore pluginval success alone is not promoted to full target-host completion.

## Current evidence interpretation

The current product has strong implementation, regression, objective real-vocal and pluginval evidence. The remaining decisive gates are:

1. human level-matched listening of the current main A/B pack;
2. broader-corpus/generalisation checks if listening exposes a weakness or if a tuning claim is to be broadened;
3. Cubase Pro 14 real-host scan/load/playback/automation/save/reopen;
4. final precision review.

## Reusable knowledge candidates

1. **Detector calibration / drive separation** — placing a slow calibration reference before a manual drive control while placing the compression detector after the drive creates a usable “drive without threshold escape” topology.
2. **Bounded vocal-prep macro** — explicit max-GR caps can make a one-knob intensity mapping measurable and constrain failure severity.
3. **First-note acquisition** — a separate short startup acquisition state can avoid long-term Active-Level timing from making the first note unrepresentative.
4. **Safety limiter implementation** — a preallocated monotonic queue provides an exact sliding sample-peak maximum with amortised O(1) work and no audio-thread allocation.
5. **Research artifact hygiene** — real-vocal A/B can be generated externally while CIPI stores only derived metrics, provenance and SHA256, keeping raw vocal audio out of the research repository.
6. **Windows validation harness** — self-contained toolchain setup and explicit process-exit capture reduce dependence on self-hosted runner machine state.

Promotion of these candidates must still respect their stated scope and evidence class.
