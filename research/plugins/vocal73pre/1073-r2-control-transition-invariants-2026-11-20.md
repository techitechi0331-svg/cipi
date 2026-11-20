# Vocal73 R2 — source-grounded control-transition invariants and executable fixture plan

Date: 2026-11-20 JST. Track: VOCAL73-1073-IDENTIFIABILITY-001.
Evidence: EVID-VOCAL73-R2-SOURCE-TRANSITIONS-20261120.
Decision: DEC-VOCAL73-R2-TRANSITION-MATRIX-20261120.
Job: JOB-VOCAL73-R2-CONTROL-TRANSITIONS-001 (READY: fixture implementation; NOT_EXECUTED).
Authority: CIPI research only; product integration off; MELON proposals not accepted as physical evidence.

## Verified baseline and reproducibility
- Product repo: techitechi0331-svg/VocalPrepComp, Vocal73Pre v0.2.
- DSP blob SHA: 691ceb53d773a8d23ed782a33c1c5ca47b29859c.
- Processor blob SHA: c072ce092c3dd8ca27234c622376346cf6973ff4.
- Sources:
  https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp
  https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/PluginProcessor.cpp
- Previous evidence: 1073-r1-baseline-measurement-contract-2026-11-20.md; 1073-r1-upload-quota-and-dsp-source-audit-2026-11-20.md.
- Current CIPI health snapshot: track FAILED/LATEST_EXTERNAL_ACTION_FAILED; cross-repo queue 2, dispatched 0, failed 29, runner-wait 0. Run 44714522345 artifact API still returned zero artifacts this run. This is not evidence that upload quota has recovered. Do not dispatch duplicate experiment or bypass Global DAG.

## New source-level deductions (NOT audio measurements)

1. The JUCE APVTS parameters are read once per processBlock and passed as scalars to DSP::process. Input, output and COLOR call SmoothedValue::skip(buffer.getNumSamples()) once per block, then a single block value is applied. This makes parameter updates **block-rate, not sample-accurate**, even though SmoothedValue is configured with 20 ms (input/output) and 30 ms (COLOR) ramps. The block's value is its smoothed endpoint, not a per-sample ramp.
2. At fs=48000, COLOR nominal ramp length is 1440 samples. A 32-sample block advances 32/1440=2.222% of a full linear step, while a 2048-sample block reaches the target in that single block. The 2048-sample block thus uses the final COLOR value for *all 2048 samples* even when the target was just changed at block start. These numbers are analytical consequences of source and nominal linear ramp semantics; verify against actual JUCE version in a compiled fixture.
3. HPF choice and ANALOG bool have **no smoothing/crossfade** in the source. HPF OFF skips two stateful IIR filters; ON re-enables existing filter states, and changing frequency swaps coefficient values without a documented reset/crossfade. ANALOG toggle switches lowShelfPre, nonlinear stage, highShelfTone and conditional dcBlocker in/out while oversampling stays on. This is a plausible transient/click risk, not an observed glitch.
4. Filter coefficient factories are invoked from DSP::process on HPF/ANALOG/COLOR changes. Possible real-time allocation remains a hypothesis until allocation instrumentation verifies JUCE's exact code path. No claim of proven allocation.

## Falsifiable R2 fixture cases (source-accurate build, no production write)

### R2-A: block-size invariance / smoothing
- Deterministic mono sine 997 Hz, peak -24 dBFS, 48 kHz, 2 seconds; seed 2026112003; 1-second pre-roll at COLOR 0/ANALOG ON, then target COLOR 100 at exact sample 48000. Repeat with 32, 256, 2048 sample process blocks; align event to block boundaries (separate tests for within-block automation capability).
- Repeat with INPUT from 0 to +12 dB and OUTPUT from 0 to -12 dB; keep COLOR 0 in those controls.
- Capture full WAV/raw input/output SHA256, output latency, sample-aligned residual between block sizes, per-block RMS and peak, first 100 ms after change; report max absolute difference, RMS residual, and settled comparison. Reject any claimed invariant until executable evidence.
- Pre-register: H0 = identical output after latency alignment across block sizes; source-level prediction H0 will fail in transition region; a post-transition difference would need further investigation.

### R2-B: HPF/ANALOG transition discontinuity
- 100 Hz and 997 Hz phase-controlled sine at -18 dBFS, separately pink noise with fixed seed; 48 kHz; controls HPF OFF→50→80→160→300→OFF, ANALOG OFF→ON→OFF, COLOR 0/50/100, buffer 32/256/2048.
- For each transition, compare against no-toggle matched reference at same sample index. Record adjacent-sample jump delta, pre/post RMS in 10 ms windows, DC transient, settling time and event alignment. Include silent input and steady 100 Hz for IIR state carryover.
- Do not classify an ordinary waveform derivative as a click; compute **excess** discontinuity relative to no-toggle reference and inspect time-frequency broadband transient.

### R2-C: real-time allocation
- On Windows JUCE 9.0.2 isolated headless build, instrument operator new/malloc and JUCE coefficient factory path after prepareToPlay warm-up. Count allocations inside processBlock for COLOR ramps, HPF switches and ANALOG toggles; record call stacks, compiler, flags, source hashes. Do not treat allocations during prepareToPlay as real-time violations.
- Pass = zero process-path allocations under declared cases; fail only on observed allocations. Add underflow/NaN/Inf policy and channel tests as in R1.

### R2-D: baseline controls vs original 1073
- Control-space mismatch remains structurally proven: v0.2 has no independent stepped HF/MF/LF controls or authentic mic/line gain-stage switching. Preserve that distinction from measured response fidelity, which remains UNKNOWN.
- Model comparison WDF / state-space / SPICE / black-box is deferred until R1/R2 baseline metrics and provenance constrain an identifiable hypothesis.

## Decision and boundaries
- Accept R2 as a deterministic **test specification and source-derived falsifiable predictions**, not execution evidence or a DSP fix.
- Product v0.2 unchanged; no unauthorized cross-repo writes, automatic knowledge promotion, release, or subjective listening claim.
- BLOCKED_EXTERNAL: original MELON R1 artifact-upload quota failure; no artifact recovered; retry only after independently verified capacity and existing retry/fingerprint authorization. Do not automatically delete prior artifacts or spend funds.
- HUMAN_GATE: calibrated original 1073 measurements and rights, level-matched blind listening, Cubase 14 host validation, product adoption and release.
- Next READY: implement minimal R2-A headless fixture; if JUCE build unavailable, first produce a pure test driver skeleton with declared expected JSON schema, then use a runner when authorized. Record exact command, environment, SHA256 and actual results in separate R2 execution evidence. Independently continue revision-tagged primary-source provenance ledger.
