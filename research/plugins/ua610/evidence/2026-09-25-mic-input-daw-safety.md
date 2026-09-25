# Original Vocal Pre — Mic 2k / Mic 500 DAW-safety bug

Date: 2026-09-25

## SOURCE_FACT

- User reported a severe real-host bug when selecting `Mic 2k` or `Mic 500` in the current 610-derived VST3.
- The Original product is intended for normal DAW-insert use on already-recorded vocal tracks, not for recreating a physical microphone-preamp gain jump at the host input.
- Historical 610 research behavior is preserved separately and may still model approximately +30 dB Mic-vs-Line gain when the DAW-safe host policy is disabled.

## MEASURED

Product repo: `techitechi0331-svg/610`
Branch: `original-vocal-pre-v0.1`
Source SHA: `f2819f2f67606c978bccbabebaa78022697666d4`
Windows workflow run: `36087412285` — SUCCESS.

The Original VST3 host wrapper now sets the DAW-safe Mic-input policy so Mic 2k / 500 no longer add the researched approximately +30 dB virtual Mic gain.

Windows regression gates:
- DAW-safe Mic modes finite: PASS.
- Mic 2k vs Line small-signal gain delta: 0.628168 dB absolute — PASS (limit 1.0 dB).
- Mic 500 vs Line small-signal gain delta: 2.27886 dB absolute — PASS (limit 3.0 dB).
- Line/Mic repeated switching peak: 0.042973 absolute — PASS (limit 1.25).
- Line/Mic repeated switching maximum sample delta: 0.0033295 — PASS (limit 1.25).
- Existing 610 baseline gain/frequency/alias/automation/stereo/latency/transient gates remained PASS.

Latest Windows VST3 artifact:
- Artifact name: `Original-Vocal-Pre-Windows-VST3`
- Artifact SHA256: `2878f5fc9f5e9ad86728442beeaf2011e086a075621709877f686c0eb4df8f11`.

## INFERRED

- The severe Mic-only failure is consistent with the old host behavior applying the 610-research approximately +30 dB Mic gain to an already line-level DAW signal, causing excessive input-transformer and tube-stage drive.
- The remaining Mic 2k / 500 gain differences after the fix are explained by the modeled virtual loading terms rather than a 30 dB mode jump.
- The Windows automated evidence verifies bounded/finite switching and gain behavior, but does not by itself prove the user's Cubase symptom is fully resolved.

## HYPOTHESIS

- The DAW-safe host policy is the correct product behavior for the Original vocal preamp, while the historical +30 dB Mic behavior should remain available only in the preserved research baseline.
- A user-side Cubase retest of the fixed VST3 should close the real-host bug if no separate host-state/UI issue is present.

## REJECTED

- Using the approximately +30 dB researched Mic-mode gain jump as the default behavior of the Original DAW-insert VST3.
- Treating Line/Mic switching as safe without dedicated regression coverage.

## Remaining gate

Cubase Pro 14 must still verify:
- Line -> Mic 2k -> Mic 500 switching;
- no explosive gain jump / severe distortion;
- automation of Input mode;
- save/reopen state recall.
