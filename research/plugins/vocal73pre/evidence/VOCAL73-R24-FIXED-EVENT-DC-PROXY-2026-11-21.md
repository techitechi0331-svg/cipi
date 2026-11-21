# VOCAL73 R24 — fixed-event DC-blocker partition control (2026-11-21)

## Evidence / provenance
- CIPI main inspected at `28cfeeb548a7e4718a535dc8b80b7485d0c60904` (R23); Research Gate run 44906895158 SUCCESS. Inspected automation-status, track YAML, research plan v2. Track VOCAL73-1073-IDENTIFIABILITY-001 is FAILED (LATEST_EXTERNAL_ACTION_FAILED), not scheduler eligible. Do not dispatch/retry without CIPI authorization.
- Novelty versus R23: hold physical toggle sample indices fixed across block sizes; explicitly compare sample-accurate vs boundary-quantized toggles to isolate timing confound.
- Synthetic one-pole **proxy**, not JUCE DSP and not Neve hardware. 48 kHz, 9600 samples, x[n]=0.15+0.25 sin(2π137n/48000), z[n+1]=a*z[n]+(1-a)*x[n], a=exp(-2π12/48000), y=x-z; initial z=0. Off [2400,4800) samples (50–100 ms). Policies: continuous (update z even while bypassed), hold (freeze z), reset (z=0 on off transition). During bypass y=x. For quantized condition, each toggle moves to ceil(toggle/B)*B. Reference: continuous, sample-accurate.
- Metrics are full 9600-sample maximum absolute and RMS difference against reference, amplitude in normalized linear units; JS IEEE754 double precision, deterministic, no stochastic input.

| B | policy | fixed max | fixed RMS | quantized max | quantized RMS | quantized off/on samples |
|---:|---|---:|---:|---:|---:|---|
|32|continuous|0|0|0|0|2400/4800|
|32|hold|0.022149|0.004036|0.022149|0.004036|2400/4800|
|32|reset|0.155027|0.028251|0.155027|0.028251|2400/4800|
|256|continuous|0|0|0.156522|0.020993|2560/4864|
|256|hold|0.022149|0.004036|0.156522|0.021451|2560/4864|
|256|reset|0.155027|0.028251|0.156522|0.032022|2560/4864|
|2048|continuous|0|0|0.171806|0.084426|4096/6144|
|2048|hold|0.022149|0.004036|0.171806|0.084468|4096/6144|
|2048|reset|0.155027|0.028251|0.171806|0.089981|4096/6144|

### Reproduction (Node.js / JavaScript)
```js
const fs=48000,N=9600,off=2400,on=4800,a=Math.exp(-2*Math.PI*12/fs);
function run(B,policy,quant) {
 let z=0,out=[],start=quant?Math.ceil(off/B)*B:off,end=quant?Math.ceil(on/B)*B:on;
 for(let i=0;i<N;i++) {
  const x=.15+.25*Math.sin(2*Math.PI*137*i/fs), active=i<start||i>=end;
  if(active||policy==="continuous") {
   const y=x-z;z=a*z+(1-a)*x;out.push(active?y:x);
  } else {if(policy==="reset"&&i===start)z=0;out.push(x);}
 }
 return out;
}
const ref=run(32,"continuous",false);
for(const B of [32,256,2048])for(const p of ["continuous","hold","reset"]) {
 const metric=arr=>{const e=arr.map((x,i)=>x-ref[i]);return [Math.max(...e.map(Math.abs)),Math.sqrt(e.reduce((s,x)=>s+x*x,0)/N)];};
 console.log(B,p,metric(run(B,p,false)),metric(run(B,p,true)));
}
```

## Decision
- **Supported only within this proxy:** when event sample positions are identical, results are invariant across B for each state policy; the apparent B sensitivity in boundary-quantized runs is confounded by different actual toggle times. R23 non-monotonicity cannot alone establish DSP block dependence.
- **Not established:** actual Vocal73Pre JUCE filter state policy, host automation timing, audible clicks, original Neve response, physical fidelity. No product changes or MELON promotion. Keep reference mode/hardware claims blocked.

## Next CIPI Job (independent READY proposal, no external dispatch)
- `VOCAL73-R25-JUCE-DC-BLOCK-STATE-AND-EVENT-TIMING`: On authorized Windows/JUCE fixture, log host event sample index, actual DSP toggle index, filter z state and output; compare fixed sample positions vs block-boundary changes at B=32/256/2048. Require input hashes, sample rate, CPU/alloc trace, max/RMS, and regression failure cases. First read actual v0.2 source before implementing; do not modify product repo automatically.
- Dependent external runner task remains **BLOCKED** by FAILED track. Hardware A/B, licensed unit evidence, listening, Cubase14, final pluginval, adoption/release remain **Human Gate**. CIPI Global DAG, No-Wait, token and MELON bridge boundaries unchanged.
