# VOCAL73 R23 — DC bypass proxy block-length sensitivity (2026-11-21)

## Evidence
- Baseline: R22 commit d8ce5e9884b4dc2929a1f047409eea7d80cf6547; this extends R22 to **block length sensitivity**, not a new hardware claim.
- Product DSP source checked: `Vocal73Pre/Source/Vocal73DSP.cpp` blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`. No product write.
- CIPI health checked: `research/health/automation-status.md` reports VOCAL73-1073-IDENTIFIABILITY-001 FAILED / scheduler_eligible=false. Track and v2 plan read. Do not redispatch MELON or bypass Global DAG.
- Experiment: Python 3 / SciPy 1.17.0 / NumPy; `scipy.signal.butter(2,12,fs=48000,btype="highpass")`, `lfilter` with explicit 2-element state, mono constant +0.2, three equal blocks: enabled / bypass / enabled. During bypass output is dry. Hold leaves filter state untouched; update processes input into hidden state; reset zeroes state before re-enable. Update is **only a numerical comparison baseline**, not Neve ground truth. Each N uses a different total duration; this tests bypass duration sensitivity, **not** buffer invariance at equal elapsed time.
- Reproducible command:
```python
import numpy as np
from scipy.signal import butter,lfilter
b,a=butter(2,12,fs=48000,btype='highpass')
for N in (32,256,2048):
    x=np.full(3*N,.2); outputs={}
    for mode in ('hold','update','reset'):
        z=np.zeros(2); out=[]
        for i in range(3):
            seg=x[i*N:(i+1)*N]
            if i==1:
                if mode=='update': _,z=lfilter(b,a,seg,zi=z)
                if mode=='reset': z=np.zeros(2)
                out.extend(seg)
            else:
                y,z=lfilter(b,a,seg,zi=z); out.extend(y)
        outputs[mode]=np.array(out)
    ref=outputs['update'][2*N:]
    print(N,*(round(float(np.max(abs(outputs[m][2*N:]-ref))),8) for m in ('hold','reset')))
```
- Executed locally in isolated Python environment; outputs (max abs difference against hidden update, linear amplitude):
| N | hold | reset |
|---:|---:|---:|
| 32 | 0.01345214 | 0.02740887 |
| 256 | 0.06774575 | 0.16544582 |
| 2048 | 0.03071527 | 0.19803399 |
- At N=2048 hold difference is smaller than N=256; therefore a monotonic 'larger buffer = worse hold transient' claim is **falsified for this proxy**. Oscillatory filter response and unequal bypass durations are potential explanations; not proven causes. JUCE coefficients/state may differ from SciPy. No real 1073, JUCE, plugin audio or listening measurement performed.

## Decision
- Retain all three policies as experimental hypotheses. No claim of audibility, plugin bug, physical accuracy or 'match percentage'. Do not promote update policy automatically. Keep Vocal73Pre v0.2 untouched.
- For actual buffer-size invariance, hold the event timestamps fixed in samples and split the **same** full input into different processing blocks; otherwise confound duration with block size.

## Next CIPI Job / resume
- READY independent: create equal-timeline negative control (zero input; always enabled; bypass with identical absolute onset/end samples), record max/RMS and full sample-index trace across 32/256/2048. Add deterministic SHA256 of generated input and versions.
- BLOCKED external: JUCE 9.0.2 isolated fixture / Windows runner, until CIPI bridge authority permits. Never silently dispatch duplicate failed track.
- HUMAN GATE: identified original hardware A/B, listening, Cubase Pro 14, final pluginval, product adoption, release.
