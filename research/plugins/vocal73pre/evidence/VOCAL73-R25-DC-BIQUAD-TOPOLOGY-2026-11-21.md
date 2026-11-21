# VOCAL73 R25 — DC-blocker proxy topology mismatch (2026-11-21)

## Evidence
- CIPI main last inspected commit `36a2289590750e3b1fbad3c10f57474ceaa71ad0` (R24). Reviewed automation health, track YAML and v2 plan. External track remains FAILED / LATEST_EXTERNAL_ACTION_FAILED and scheduler-ineligible. No external dispatch or product write.
- Source inspected: `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp`, blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`. `dcBlocker.state` is initialized with `juce::dsp::IIR::Coefficients<float>::makeHighPass(sr,12.0f,0.70710678f)` and `dcBlocker.process(context)` only runs if ANALOG and blockColor>0.00001. This is a **second-order IIR** with Q argument, not R22–R24's first-order proxy.
- R22–R24 used `z[n+1]=a*z[n]+(1-a)*x[n]`, `y=x-z` with `a=exp(-2π12/fs)`: a first-order highpass, hence its quantitative waveform/state results cannot predict the JUCE biquad without a topology-matched fixture.

## New numerical check (synthetic analytical comparator, NOT JUCE output)
- 48 kHz; nominal f0=12 Hz; Q=1/sqrt(2); bilinear/RBJ-style second-order highpass comparator (not an assertion of JUCE's exact coefficient implementation). b0=(1+cos w)/2, b1=-(1+cos w), b2=b0, a0=1+sin(w)/(2Q), a1=-2cos(w), a2=1-sin(w)/(2Q), normalize by a0. First-order comparator: |H|=f/sqrt(f²+12²) (continuous-time magnitude approximation).
- Normalized biquad coefficients b=[0.9988898958872262,-1.9977797917744524,0.9988898958872262], a=[1,-1.9977785594429316,0.9977810241059734].
- Magnitudes (dB):

| Hz | 2-pole comparator | 1-pole comparator | 2-pole minus 1-pole |
|---:|---:|---:|---:|
|3|-24.099335|-12.304489|-11.794846|
|6|-12.304492|-6.989700|-5.314792|
|12|-3.010300|-3.010300|0.000000|
|24|-0.263289|-0.969100|+0.705811|
|48|-0.016931|-0.263289|+0.246358|
|100|-0.000900|-0.062092|+0.061192|
|1000|-0.00000009|-0.00062534|+0.00062525|

### Reproduce
```js
const fs=48000,f0=12,Q=Math.SQRT1_2,w=2*Math.PI*f0/fs,alpha=Math.sin(w)/(2*Q),c=Math.cos(w),a0=1+alpha;
const b=[(1+c)/2/a0,-(1+c)/a0,(1+c)/2/a0],a=[1,-2*c/a0,(1-alpha)/a0];
function mag(f){const t=2*Math.PI*f/fs;const re=p=>p[0]+p[1]*Math.cos(t)+p[2]*Math.cos(2*t),im=p=>-p[1]*Math.sin(t)-p[2]*Math.sin(2*t);return Math.hypot(re(b),im(b))/Math.hypot(re(a),im(a));}
for(const f of [3,6,12,24,48,100,1000])console.log(f,20*Math.log10(mag(f)),20*Math.log10(f/Math.hypot(f,12)));
```

## Decision
- **Falsified as a structural match:** R22–R24 first-order proxy is not a topology-matched predictor of v0.2's actual DC-blocker. Its state-hold/quantization findings are *hypothesis-generating only*, not measured v0.2 behavior. Difference in filter order is confirmed by source; numerical dB differences above apply only to the explicit comparators.
- No evidence for audible clicks, actual JUCE coefficient values, Neve original transfer, or product defect. Do not promote candidate, change v0.2 or declare hardware fidelity.

## Next CIPI Job / BLOCKED / Human Gate
- Proposed independent READY analysis `VOCAL73-R26-BIQUAD-STATE-EXPERIMENT`: verify JUCE 9.0.2 makeHighPass exact coefficients and IIR processing/state convention, then implement two-pole 48 kHz fixture with 32/256/2048 block sizes, fixed event indices and held/reset/continuously-updated state; report sample-accurate output hashes, max/RMS, pre/post switch states, source version and limitations. Do not reuse R24 one-pole numbers as JUCE validation.
- External runner dependent job remains BLOCKED (FAILED track); do not override CIPI budget, Cross-Repo Token, MELON Bridge or Global DAG.
- Original 1073 licensed hardware measurements, A/B, blind listening, Cubase 14, final pluginval, adoption and release remain Human Gate.
