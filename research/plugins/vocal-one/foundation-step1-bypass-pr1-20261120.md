# Vocal ONE STEP 1: master-bypass implementation and PR CI observation (2026-11-20)

Evidence class: **SOURCE_FACT (GitHub source/CI observation)**. This is NOT a CIPI MEASURED sound-quality claim.

## Baseline
- Product: `techitechi0331-svg/Vocal-ONE`
- Baseline main SHA: `ae38bc6e95c31f5219ab426f15b804f3b6827f32`
- Prior foundation run: https://github.com/techitechi0331-svg/Vocal-ONE/actions/runs/44695877831 (Linux portable PASS; Windows VST3 build/test PASS; private draft snapshot saved)
- Prior 2026-11-19 Actions failure was artifact quota, not identified DSP compilation failure.

## New candidate (NOT PRODUCT-LOCKED)
- Branch: `feat/p0-master-bypass-20261120`
- Commit: `f6ac1be356c6cdf8c049e0011eebe2003d107fa7`
- Draft PR: https://github.com/techitechi0331-svg/Vocal-ONE/pull/1
- PR CI: https://github.com/techitechi0331-svg/Vocal-ONE/actions/runs/44714539807
- Scope: stable `masterBypass` APVTS boolean (default false); sample-smoothed 10 ms dry/wet crossfade; preallocated dry scratch; oversized host-buffer chunking; explicit host-native passthrough; Linux/Windows read-only PR CI; portable crossfade regressions.
- Windows draft snapshot remains restricted to trusted main pushes.
- Linux portable tests: **PASS** observed on PR CI; Windows VST3 PR build **IN_PROGRESS** at observation. CI execution timestamps are shown at the linked run.
- Test source: `Tests/CoreTests.cpp`, `Source/DSP/BypassMixer.h`; review the PR diff for exact assertions. Code's test matrix covers 44.1, 48, 96, 192 kHz; tests do not establish actual-host bypass quality.

## Review questions / counterexamples
1. Does VST3 wrapper use host-native `processBlockBypassed` as expected for the target hosts, including automation and preset restore?
2. Does `dryScratch_` remain allocation-free for an oversized render block and is mono/stereo output correct in all supported layouts?
3. Is smoothing audibly click-free for fast toggles and zero/silent/extreme signals across 44.1/48/96/192 kHz and buffer sizes 0/1/irregular?
4. Does pluginval and Steinberg Validator pass for a pinned actual VST3 binary?
5. Are loaded pre-upgrade APVTS states and new `masterBypass` backward compatible in Cubase 14?
6. No listening preference, actual vocal improvement, plugin release, or externally researched DSP integration is authorized by this record.

## Governance
- CIPI remains evidence and review authority; MELON is independent and has no product-write permission.
- Current CIPI Cross-Repo registry has Vocal ONE foundation workflow with `monitor: true`, `dispatch: false` at this observation. Do not claim the CIPI bridge has already dispatched this PR.
- Release status unchanged: NOT_RELEASED; research knowledge status unchanged: HYPOTHESIS.
