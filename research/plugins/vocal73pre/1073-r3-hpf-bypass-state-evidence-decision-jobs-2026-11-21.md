# Vocal73 R3 — HPF OFF→ON state-freeze research probe (2026-11-21 JST)

Track: `VOCAL73-1073-IDENTIFIABILITY-001`
Evidence: `EVID-VOCAL73-R3-HPF-FREEZE-20261121`
Decision: `DEC-VOCAL73-R3-HPF-FIXTURE-20261121`
Job: `JOB-VOCAL73-R3-JUCE-HPF-TRANSITION-001`
Authority: CIPI research-only. Product v0.2 remains unchanged.

## Source and novelty
Product DSP blob: `691ceb53d773a8d23ed782a33c1c5ca47b29859c`. `Vocal73DSP::process` calls `hpfFirst.process` and `hpfSecond.process` only if `hpfChoice > 0`. Hence their IIR state is **not advanced** during HPF OFF. When re-enabled, the previously stored state is reused. Earlier work investigated DC blocker suspension; this is a separate **HPF pair** and is not a repeat of that probe. Filter coefficients are also replaced by `updateFilters` on switch, so the exact JUCE behavior needs its own fixture.

## Executed reproducible synthetic probe
Research-only code: `research/plugins/vocal73pre/tests/test_hpf_bypass_state.py` (first commit `e831500db6417dc8eed51b544fc074a57955c35b`).
Command: `python research/plugins/vocal73pre/tests/test_hpf_bypass_state.py -v`.
Local result: 2 tests passed (0.013 s); Python reference first-order HPF uses `a=exp(-2*pi*300/48000)`, recurrence `y[n]=a*(y[n-1]+x[n]-x[n-1])`; 1kHz sine at 48kHz, 8192 samples; HPF ON [0,2048), OFF [2048,6144), ON [6144,8192). State-frozen OFF versus dry-output-with-hidden-state-tracking OFF:
- Difference at first re-enabled sample: **-0.3506574440 (normalized amplitude)**.
- Maximum absolute difference over first 100 re-enabled samples: **0.3506574440**.
- Both output the same dry signal during OFF.
These are **synthetic single-pole illustrative values only**, not the actual Vocal73DSP cascaded 1st+2nd order HPF, not a measured click, and not Neve 1073 hardware evidence. This probe falsifies the idea that frozen and continuously updated IIR states are universally equivalent across OFF→ON transitions; it does not establish that the production plugin clicks.

## Decision
Do not patch the product or declare a defect based on synthetic values. Advance a JUCE 9.0.2 source-accurate headless fixture with actual `Vocal73DSP::process` and production coefficient factories; compare OFF→ON and ON→OFF discontinuity, output peak, state resets, filter settling, latency and block sizes 32/256/2048 at 44.1/48/96kHz. Use deterministic input/output SHA256 and compiler/JUCE/source SHA, measure click severity and test crossfade or shadow-processing alternatives. Keep switch automation in a fixed sample-time schedule, not just block index. The analog reference remains UNKNOWN.

## Status and gates
- CIPI health latest main checked this run: `FAILED` / `LATEST_EXTERNAL_ACTION_FAILED` for external MELON track, `scheduler_eligible=false`; global queued=2, dispatched=0, failed=29, runner alerts=0. This is **not** a claim of failed DSP fidelity.
- External MELON result upload path previously failed on GitHub artifact quota; do not repeatedly dispatch while capacity and evidence recovery are unverified. Only the external dependent job is BLOCKED; this independent research fixture is READY.
- Human Gate: identified licensed original 1073 hardware measurements, listening, Cubase 14, final adoption/release.
- Next: implement and execute actual JUCE headless HPF transition fixture; collect numerical deltas; then consider a product-side change only through review.
