# VOCAL73 R27 — host-rate second-order proxy state experiment (2026-11-22 JST)

## Scope and provenance
CIPI research Evidence E-R27-001 / Decision D-R27-001 / Job J-R28-001. Reviewed CIPI main health, track YAML, plan v2, latest R26 (2ec0560), and product DSP blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`. No product edits, MELON promotions, real hardware data, or JUCE measurements. Source: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp . R22–R26 already established bypass and sample-rate concerns; this run adds a **numerical second-order** state experiment rather than repeating the one-pole tests.

## Evidence: reproducible SciPy biquad proxy (NOT JUCE coefficient-equivalence)
SciPy `scipy.signal.butter(2,12,btype='highpass',fs=fs)` followed by `lfilter` in float64. This is a Butterworth 2nd-order HPF, conceptually similar to JUCE makeHighPass(sr,12,Q=1/sqrt(2)), but actual coefficient and state equivalence is UNVERIFIED. Input for 2.75 seconds: `x[n]=0.025+0.04*sin(2*pi*6*n/fs)+0.03*sin(2*pi*24*n/fs)` FS, no random seed. Initial filter state zeros. ON 0–2.00 s; OFF 2.00–2.25 s; ON 2.25–2.75 s. During OFF output is dry for all modes. Mode A freezes filter state; mode B processes OFF samples into discarded buffer to advance state; mode C resets state at 2.25 s. Compare A and C to B in first 100 ms after re-enable. Fixed sample event times at both rates; no block quantization.

| Host rate | Mode A max abs vs B (FS) | Mode A RMS vs B (FS) | Mode C max abs vs B (FS) | Mode C RMS vs B (FS) |
|---|---:|---:|---:|---:|
| 48 kHz | 0.013848689 | 0.006760614 | 0.012127994 | 0.005920817 |
| 96 kHz | 0.013848686 | 0.006759929 | 0.012125449 | 0.005919580 |

48 kHz normalized coefficients (b then a): `[0.99888990,-1.99777979,0.99888990]`, `[1,-1.99777856,0.99778102]`. 96 kHz: `[0.99944479,-1.99888959,0.99944479]`, `[1,-1.99888928,0.99888990]` (rounded for reporting). Results show reset is not universally worse than freeze for this input; both differ from continuously advanced state. These are *engineering proxy* differences, not audible-click or Neve 1073 fidelity evidence. Buffer-size independence was not re-tested (R24 addressed event-time confounding).

### Reproduction
```python
import numpy as np
from scipy.signal import butter,lfilter
for fs in (48000,96000):
    b,a=butter(2,12,btype='highpass',fs=fs)
    n=np.arange(int(fs*2.75))
    x=.025+.04*np.sin(2*np.pi*6*n/fs)+.03*np.sin(2*np.pi*24*n/fs)
    off,on=2*fs,int(2.25*fs)
    _,z=lfilter(b,a,x[:off],zi=np.zeros(2))
    frozen,_=lfilter(b,a,x[on:],zi=z)
    _,zrun=lfilter(b,a,x[off:on],zi=z)
    continuous,_=lfilter(b,a,x[on:],zi=zrun)
    reset,_=lfilter(b,a,x[on:],zi=np.zeros(2))
    k=fs//10
    for name,y in [('freeze',frozen),('reset',reset)]:
        d=y[:k]-continuous[:k]
        print(fs,name,float(np.max(np.abs(d))),float(np.sqrt(np.mean(d*d))))
```

## Decision D-R27-001
HOLD product changes. Advance an isolated JUCE 9.0.2 fixture before claiming implementation-equivalent behavior. No assertion that continuous update is sonically preferable; its behavior during ANALOG OFF may differ because the upstream nonlinear processing is bypassed. A real reference measurement is required for fidelity claims.

## Job J-R28-001
READY independent: implement actual JUCE `makeHighPass` + `IIR::Filter<float>` test and verify coefficients, filter state, sample-by-sample event splitting, 32/256/2048 blocks, 48/96k, input/output hashes, max/RMS, NaN, and recovery. Negative controls uninterrupted ON/OFF. If JUCE toolchain unavailable, keep only this dependent fixture BLOCKED and pursue separate source/provenance work. External CIPI track FAILED (LATEST_EXTERNAL_ACTION_FAILED); no unauthorized rerun or budget bypass. Human Gate: licensed original hardware A/B, listening, Cubase 14, final pluginval, adoption, release.
