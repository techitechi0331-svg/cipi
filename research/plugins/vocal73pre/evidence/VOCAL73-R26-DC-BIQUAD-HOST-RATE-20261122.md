# VOCAL73 R26 — DC blocker topology and falsification fixture (2026-11-22 JST)

## Authority and inputs
CIPI research-only Evidence/Decision/Job; no product write, MELON promotion, or hardware fidelity claim. Read CIPI main automation-status, VOCAL73 track, research plan v2 and latest R25 commit 9bc97efdaf39ac757c689cfdb3917df0fa1f27cc. Product DSP blob 691ceb53d773a8d23ed782a33c1c5ca47b29859c. Existing R22–R25 synthetic first-order vs second-order proxy results are not repeated.

## Evidence E-R26-001 (source inspection, not runtime measurement)
Vocal73DSP::initialiseFilterCoefficients uses juce::dsp::IIR::Coefficients<float>::makeHighPass(sr,12.0f,0.70710678f) for dcBlocker (second-order biquad). dcBlocker.process(context) executes only when analogEnabled && blockColor>0.00001f. reset() resets dcBlocker but process() has no reset or continuous state advance while bypassed. The filter is after 2x oversampling/downsampling and high shelf, hence runs at HOST sample rate (not 2x). Its input includes the preceding nonlinear/tone processing, so isolating the DC blocker is necessary to avoid confounding. The HPF setting is an independent separate path and must be disabled for the fixture. No JUCE audio measurements performed.

## New falsifiable distinction
R25 established the one-pole proxy is not the implementation topology. R26 adds a **sample-rate domain** and **state-advance** constraint: at 48kHz the nominal biquad normalized cutoff is 12/48000=0.00025 cycles/sample; at 96kHz it is 0.000125. It is incorrect to derive its coefficients for 96kHz by reusing 48kHz coefficients, or to run it at 96kHz internally when the host is 48kHz merely because oversampling is 2x.

## Independent test fixture specification (READY; no product modifications)
1. Instantiate juce::dsp::IIR::Filter<float> and coefficients makeHighPass(hostRate,12,0.70710678f), prepare mono ProcessSpec; independently run at 48k and 96k host rates. Confirm coefficients and reset semantics against installed JUCE 9.0.2 source before numeric equivalence assertions.
2. Stimulus deterministic DC+step+6/12/24 Hz sines, amplitude <=0.2 FS; 2s warmup, then 250ms OFF and 500ms ON. Compare A=freeze state during OFF, B=process into throwaway buffer during OFF, C=reset at re-enable. Crucially output dry/unfiltered during OFF for all three.
3. Use fixed absolute event sample index; test block sizes 32/256/2048 with split blocks to align event at exact sample. Repeat with block-boundary-quantized events as a separate confound.
4. Measure max abs difference and RMS in first 100ms after ON, time to <=-80dBFS absolute difference for 50ms contiguous, output DC after 500ms, finite samples, 48k/96k consistency. Record exact source commit, compiler, JUCE version, coefficients, input/output SHA256.
5. Negative controls: uninterrupted ON; uninterrupted OFF; reset before start; no analog color; compare against direct JUCE filter implementation, not against real Neve hardware.
6. No claims about actual click audibility or hardware fidelity without Human Gate.

## Decision D-R26-001
HOLD any DSP implementation change. The 2x oversampling factor does not change the DC blocker coefficient sample-rate domain; prioritize JUCE biquad-state fixture over further one-pole proxy sweeps. The state-management alternatives are engineering hypotheses, not measured Neve 1073 behavior. No manufactured reference results.

## Job J-R27-001
READY independent: implement isolated JUCE biquad fixture with host-rate and event-time controls; report measured numerical outputs. BLOCKED dependent: Windows/Cubase and identified 1073 reference A/B. External VOCAL73 track currently FAILED (LATEST_EXTERNAL_ACTION_FAILED); do not auto-retry or bypass budget/authority. Human Gate: real unit, listening, Cubase 14, final pluginval, adoption, release.

## Provenance
Product source: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp (repository code, inspect-only; no third-party schematic reproduced). Original 1970s vs modern AMS Neve physical measurements remain unverified. No original unit data, commercial plugin reference, or licensed audio introduced in this run.
