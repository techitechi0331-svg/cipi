# R35 — JUCE 9.0.2 skip semantics and block-start DC gate oracle (2026-11-22)

## Evidence / inputs / rights
- Parent CIPI main: 5f234831e5e51bd86e13966d9e212c6fa5a183af (R34); Research Gate run 44964309175 SUCCESS. Health file reports VOCAL73-1073-IDENTIFIABILITY-001 FAILED (external action); no re-dispatch.
- Product source (read-only): https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp ; baseline v0.2 unchanged.
- JUCE 9.0.2 primary implementation: https://github.com/juce-framework/JUCE/blob/9.0.2/modules/juce_audio_basics/utilities/juce_SmoothedValue.h ; JUCE license header references JUCE 9 EULA or AGPLv3; reference/link and paraphrase only, no code copied.
- JUCE reset(sampleRate, seconds) uses floor(seconds * sampleRate). Default SmoothedValue smoothing is Linear; setTargetValue resets countdown only on changed target; skip(B) advances by B samples or snaps to target if B >= countdown.
- Product calls colorSmoothed.skip(B) BEFORE updateFilters and processes the entire buffer with that block-end color. Gate is analogEnabled && blockColor > 1e-5. Thus the *first block with zero block-end COLOR* is already fully bypassed from its first sample. R34 listed its END only, which is not the earliest audio-sample position of the bypass. No JUCE binary or audio executed.

## Deterministic source-derived oracle (COLOR 0.45 -> 0, no mid-ramp retarget, ANALOG ON)
N=floor(0.03*Fs), k=ceil(N/B), first-zero block index k-1 (zero-based), first-zero block START=(k-1)*B, END=k*B. Difference N-START measures how early the first zero-color *block* begins relative to nominal per-sample ramp completion. **This is not an audio latency measurement.** Strict >1e-5 threshold can make bypass start still earlier, so the table is a latest-start upper bound for the first bypassed block under this initialization.

| Fs | B | N | zero-color block start | block end | N - start | lead ms |
|---:|---:|---:|---:|---:|---:|---:|
| 48000 | 32 | 1440 | 1408 | 1440 | 32 | 0.667 |
| 48000 | 256 | 1440 | 1280 | 1536 | 160 | 3.333 |
| 48000 | 2048 | 1440 | 0 | 2048 | 1440 | 30.000 |
| 96000 | 32 | 2880 | 2848 | 2880 | 32 | 0.333 |
| 96000 | 256 | 2880 | 2816 | 3072 | 64 | 0.667 |
| 96000 | 2048 | 2880 | 2048 | 4096 | 832 | 8.667 |

Reproduce table with Python stdlib:
```python
import math
for fs in (48000,96000):
 for b in (32,256,2048):
  n=math.floor(.03*fs); k=math.ceil(n/b); start=(k-1)*b
  print(fs,b,n,start,k*b,n-start,round(1000*(n-start)/fs,3))
```

## Decision
- R34's end-of-block quantization is correct for *control-value observation* but cannot be interpreted as the beginning of DC filtering bypass. For B>=N, one block can use the target COLOR for its entire contents even though the smoothed control nominally takes N samples. This is a testable control-scheduling risk, not a demonstrated click or 1073 fidelity result.
- Keep product unchanged. No MELON promotion, no cross-repo write, no automatic release or hardware equivalence claims.

## Next CIPI Job R36
- READY independent: compute exact earliest bypass block for threshold 1e-5 using float32 JUCE-style skip arithmetic; test 0.45->0 and 0->1, repeated unchanged target, mid-ramp retarget, B=32/256/2048 at 48/96k; distinguish block-start sample and block-end control observation, and compare with this oracle.
- BLOCKED dependent: JUCE 9.0.2 compiled fixture logs blockColor, gate, EQ update flags and DC input/output; Windows runner and real audio artifact needed before measured-error claims.
- HUMAN GATE: licensed original-1073 hardware A/B, blind listening, Cubase 14, final pluginval, adoption/release.
