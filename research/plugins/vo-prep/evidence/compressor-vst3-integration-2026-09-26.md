# Vo.Prep Transparent Compressor — VST3 Integration Evidence 2026-09-26

Status: **PARTIAL / HOST GATE OPEN**

## Product source

Repository: `techitechi0331-svg/Vo.Prep`

Frozen research-core baseline:
- product branch: `research/integrated-vocal-compressor-core`
- product SHA reviewed: `a832458c87884f5cf9a7f152879785c4ee9277ca`

Priority-0 integration branch:
- `integration/vocal-compressor-vst3-v1`
- latest reviewed HEAD: `fee5207b43f104c5385c96de22c8e02f4b2fac77`

Post-integration hardening already present on that branch:
- `3ff2c936686a98b4aae276a6cf07cff3ceff136c` — non-empty Default program name
- `fee5207b43f104c5385c96de22c8e02f4b2fac77` — runner-compatible CMake generator

## Implemented product-side integration work

The existing MacroLevel product path was deliberately left intact.

A separate research compressor path was added:
- `Source/dsp/LinkedStereoVocalCompressor.h`
- `Source/dsp/CompressorAudioPath.h`
- `Source/CompressorPluginProcessor.h`
- `Source/CompressorPluginProcessor.cpp`
- `tests/CompressorAudioPathTests.cpp`

The new research VST3 target is separate from the existing MacroLevel target:
- target: `VoPrepCompressorResearch`
- product name: `Vo.Prep Vocal Compressor Research`
- formats: VST3 + Standalone

Frozen DSP routed through the shared audio path:
- Slow body RMS: 25 ms
- Fast detector: instantaneous sample peak
- Fusion: max(Slow, Fast - 6 dB)
- Ratio: 1.5:1
- Knee: 18 dB
- Attack: 8 ms
- Release: 70 ms
- Hold: 0 ms
- Lookahead: 0 ms
- Mono: direct frozen VocalCompressorCore
- Stereo: fresh MAX-linked wrapper built on the current 8/70 core
- Amount mapping intentionally absent from this Priority-0 integration path

## MANUAL_MEASURED

A local C++ equivalence check of the shared `CompressorAudioPath` reported:
- mono path vs direct VocalCompressorCore max sample error: **0**
- stereo path vs direct current linked wrapper max sample error: **0**
- frozen timing/constants assertion: PASS

This is useful wiring evidence but is **not** a replacement for repository CI, VST3 build or host validation.

## CI / host blocker

Vo.Prep GitHub Actions runs:
- original integration run: `36173066852`
- latest run after Default-program and generator fixes: `36181089099`

In both runs, both jobs:
- `core-path`
- `windows-vst3`

failed before any workflow step was created/executed (**0 steps**).

The latest run therefore still did not reach checkout, compiler invocation, CMake configure, JUCE generation, or VST3 build.

Interpretation:
- no C++ compiler diagnostic was produced by either run;
- no JUCE/VST3 compiler diagnostic was produced;
- the latest source-side hardening was therefore not actually exercised by CI;
- these runs do **not** establish a DSP or source-code failure;
- actual Windows VST3 build remains unverified.

## No-Wait blocker checkpoint

[BLOCKED対象]

Repository-backed CI execution for the research compressor target:
- core-path CI
- Windows VST3 compile
- downstream pluginval / Steinberg validator

[待っている結果]

A runner allocation that creates workflow steps and reaches at least checkout / compile, or an available authorized self-hosted runner capable of executing the same workflow.

[再開条件]

Any new `Vocal Compressor VST3 Integration` run where either job contains real workflow steps and produces build/test output.

[再開直後の処理]

1. inspect the first real compiler/test failure if any;
2. apply the smallest source/build correction;
3. rerun AudioPath equivalence and Windows VST3 build;
4. if build passes, run pluginval and Steinberg validator;
5. preserve Cubase Pro 14 as a separate human-only host gate.

[checkpoint]

- DSP wiring: PASS by local exact-equivalence evidence;
- current core: 25 ms RMS / instantaneous peak / 6 dB fusion / 1.5:1 / 18 dB / 8 ms / 70 ms;
- separate research VST3 path implemented without replacing MacroLevel;
- current integration branch HEAD: `fee5207b43f104c5385c96de22c8e02f4b2fac77`;
- latest GitHub-hosted CI run: `36181089099`, zero workflow steps in both jobs;
- no source/compiler failure has yet been observed.

[未完了Task]

- repository-backed AudioPath CI;
- Windows VST3 compile;
- pluginval;
- Steinberg validator;
- VST3 render parity / automation / state recall;
- Cubase Pro 14 validation.

## JUCE Factory assessment

CIPI JUCE Factory Phase 1 was reviewed as an alternate manufacturing route.

Current Factory contract schema permits only:
- `dsp.template = golden_gain_v1`

Therefore the Factory cannot honestly manufacture the current custom Vo.Prep compressor DSP yet.

No Golden Gain contract is used as a substitute for the compressor.

## OPEN

- repository-backed C++ AudioPath CI
- Windows VST3 compile
- pluginval
- Steinberg validator
- VST3 mono/stereo render parity
- parameter automation/state recall
- Cubase Pro 14 realtime/offline validation
- final Amount integration
- final operating-point Learn state integration

## Precision conclusion

**Implemented:** independent product-side research signal path around the frozen compressor core.

**Measured locally:** mono/stereo path equivalence to the direct DSP references.

**Not established:** actual VST3 build or host validity.

Priority 0 is therefore **DSP-WIRING PASS / VST3-HOST GATE OPEN**, not complete.
