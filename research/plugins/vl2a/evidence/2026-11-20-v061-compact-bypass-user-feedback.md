# VL2A v0.6.1: reported Cubase usability and bypass de-click maintenance

Date: 2026-11-20 (Asia/Tokyo)
Authority: USER_REPORTED_HOST_FEEDBACK / PRODUCT_CODE_CHANGE; not a measured host-quality certification.
Product repository: techitechi0331-svg/VocalPrepComp
Base (frozen): integration/vl2a-v060-rc2
Maintenance branch: release/vl2a-v061-compact-bypass
Product PR: https://github.com/techitechi0331-svg/VocalPrepComp/pull/26
Product merge commit: 211e770422f99bf5a0c2e9b069883326c7f44172

## User observation

The user reports that existing VL2A playback in Cubase Pro 14 works and the listening impression is good. They also report two outstanding UX defects: the plug-in editor is too large, and bypass toggling produces an audible click.

This is user-reported real-host listening and use, not an independent validation of project save/reload, automation, PDC, Steinberg validator, hardware LA-2A parity or formal subjective blind A/B. Do not mark these other gates PASS.

## Targeted maintenance changes, not sound-model research

- Compact the default existing editor geometry from 1000x563 to 750x422; retained scale-aware UI and parameter attachments.
- The archived product already has latency-aligned dry/wet interpolation with a 15 ms per-sample bypass ramp and an APVTS `bypass` parameter. The missing native `getBypassParameter()` mapping was identified as a likely reason a VST3 host bypass may not use that ramp.
- Map JUCE's native host bypass to the existing `bypass` parameter; lengthen the existing ramp to 20 ms and initialize wet/dry state from the recalled bypass state.
- Expose an editor-local **BYPASS** toggle bound to the same state parameter. This is the reliable in-plug-in path even if Cubase's separate hard-bypass operation skips plug-in processing.
- Keep the existing latency-aligned dry branch, audio engine, Peak Reduction law, T4 optical constants, DSP oversampling and VST3 parameter IDs unchanged.
- Apply changes to unpacked product only during the VST3 maintenance build; retain v0.6.0 RC2 baseline unchanged.
- Host bypass behavior remains host-implementation dependent. A host that bypasses the plug-in outside its processing cannot be forced to fade by its plug-in code.

## Verification and remaining gates

- Offline archived-source patch/GUI contract: PASS, GitHub Actions run 44718122389.
- Windows v0.6.1 VST3 compilation, pluginval strictness 10, Cubase re-validation of **this new build**, bypass rapid-toggle stress and host PDC: **NOT YET VERIFIED** by this evidence note.
- No new CPU, fidelity, human blind-listening or commercial-hardware matching score claimed.
- CIPI's older HA100X BUDGET_EXHAUSTED and HUMAN_GATE track states are unchanged.
- Next evidence must attach the exact maintenance SHA, Windows build/validator artifact and Cubase-v0.6.1 soft/hard bypass findings before any product approval.
