# VL2A v0.6.1 — synthetic bypass-fade continuity contract

Date: 2026-11-20 (Asia/Tokyo)
Scope: DERIVED_OFFLINE_REGRESSION; not a product release approval, acoustic preference, actual VST3 runtime, or Cubase confirmation.
Research authority: CIPI evidence record, product implementation remains in VocalPrepComp.

## Source lineage

- Product repository: techitechi0331-svg/VocalPrepComp
- Tested branch and maintenance artifact source: release/vl2a-v061-compact-bypass
- Change PR: https://github.com/techitechi0331-svg/VocalPrepComp/pull/27
- Merge SHA: `9d77181e2252eabc7f781fe7375a2b673305ec9c`
- Offline CI: https://github.com/techitechi0331-svg/VocalPrepComp/actions/runs/44724323928
- Result: VL2A Compact Bypass Patch Contract — **PASS**

## Test matrix and evidence boundary

- Pure, independent mathematical model of 20 ms per-sample linear wet/dry interpolation.
- Cases: 44.1, 48, 96, and 192 kHz; mono/stereo opposing steady wet/dry signals; zero signal.
- Block partitions: 1, 16, 64 and 256 samples, with bypass state changes aligned to declared block boundaries (the processor reads bypass state once per block).
- Multiple reversals before fade completion; verify no discontinuous fade-state jumps, finite output, bounded blend gain, equivalent partitioned results and full endpoint recovery.
- Recalled initial bypass starts dry and ramps to wet after toggling.
- Existing packed-source patch contract still checks ID preservation, dry-delay allocation and oversampled DSP path.
- **Limit:** the Python reference is not a compiled C++ or actual Cubase audio measurement; it cannot establish click-free host hard-bypass, phase coherence in every source, or pluginval success. Do not infer proprietary hardware identity.

## Retained independent release gates

1. Compile the exact 0.6.1 maintenance branch into Windows VST3 and save artifact SHA.
2. Run pluginval strictness 10 non-GUI and Steinberg validator where available, with result IDs.
3. Verify in Cubase Pro 14: internal soft bypass and host bypass; mono/stereo; automation, rapid toggles, PDC, project save/reload. Host hard bypass may skip plugin processing entirely.
4. Preserve LA2A/HA100X earlier BUDGET_EXHAUSTED and HUMAN_GATE, and do not automatically promote product or knowledge.
