# VL2A v0.6.0 final pre-host validation — 2026-09-26

## Status

**FINAL PRE-HOST VALIDATION: PASS**

This closes the automated/reproducible engineering validation available in CI.

The only remaining release gate is the real Cubase Pro 14 host confirmation:
- VST3 scan
- insert
- playback
- automation
- project save/reload
- host PDC behavior

Cubase remains explicitly **UNVERIFIED** until user confirmation.

## Product provenance

Repository:
- `techitechi0331-svg/VocalPrepComp`

Branch:
- `integration/vl2a-v060-rc2`

Final validation run:
- `36199539214`
- conclusion: SUCCESS
- source SHA: `4733b8a34450ef743b570b3d97951925502ea37f`

Final evidence artifact:
- id `10891648604`
- digest:
  `sha256:fbafa19f8b5825f21c82d6a8a408b44abd1aea8a87c7e256999a217a202d5416`

Final VST3 artifact:
- id `10891448870`
- digest:
  `sha256:9b314f0298bbf1680eb991eb7e9aae3a64ecc9ac443a89496721722d27ce12fe`

## Final production DSP selection

Peak Reduction:
- v8 operating curve
- `e(n) = 2 * (1 - (1-n)^2.70)`
- `drive = 0.18 * 10^e(n)`

Optical coloration:
- stateful optical v3 structure
- optical mean tau = **8 ms**
- optical amount = **0.054**
- residual HP experimental path = **not in production**
- rejected LF experimental path = **not in production**

Other retained decisions:
- Phase01-H line amplifier
- matched-GR T4 attack/release behavior
- current COMP/LIMIT topology
- factory-flat R37 product setting
- shared phase-safe stereo detector
- Gain = direct -18..+18 dB mapping
- processor-side GR numeric peak-hold meter

## MEASURED Peak Reduction real-vocal gate

Pinned VocalSet, peak-normalized to -18 dBFS, COMP, PR50:

- breathy max GR: **5.30939 dB**
- straight max GR: **5.55217 dB**
- forte max GR: **6.40301 dB**
- median: **5.55217 dB**

Product gate:
- approximately 5..7 dB GR

Result:
- **PASS**

## MEASURED matched-GR control regression

Target:
- approximately 6 dB GR at -18 dBFS

Final:
- Peak Reduction required: **41.77398682**
- start GR: **5.70246935 dB**
- 60 ms GR: **2.89953732 dB**
- retained at 60 ms: **0.50847048**
- 500 ms GR: **0.23098701 dB**
- 2 s GR: **0.09547304 dB**

Sample-rate GR spread:
- **0.03302384 dB** across 44.1 / 48 / 96 / 192 kHz

Result:
- **PASS**

## MEASURED final real-vocal A/B

### Same-knob comparison
Descriptive only; this intentionally includes the much stronger Peak v8
operating calibration and is not a color-isolation fidelity metric.

### Optical color isolation
Level-matched optical OFF vs final optical v3 / tau8ms / amount0.054:

Breathy:
- correlation: ~0.999782
- residual: ~-33.60 dB
- derivative RMS delta: ~+0.0308 dB
- max band-energy shift: **~0.191236 dB**

Straight:
- correlation: ~0.999951
- residual: ~-40.05 dB
- derivative RMS delta: ~-0.0069 dB
- max band-energy shift: **~0.058774 dB**

Forte:
- correlation: ~0.999919
- residual: ~-37.89 dB
- derivative RMS delta: ~0.000004 dB
- max band-energy shift: **~0.742962 dB**

Strict gate:
- correlation >=0.99
- |derivative RMS delta| <=0.50 dB
- max band-energy shift <=0.75 dB

Result:
- **PASS**

## MEASURED active-GR coloration

Phase03G selected the least-reduced coloration amount that passes all strict
gates.

Final G054:
- 1 kHz THD: **~0.767707%**
- 63 Hz THD: **~1.280933%**
- H3 dominant
- release/control/sample-rate/PR0/stress gates PASS

Result:
- **PASS**

## State / Automation compatibility

Run:
- `36193405591`
- conclusion: SUCCESS
- artifact id: `10888934402`
- digest:
  `sha256:b375458c1d49fef9f2ee0e53f9f8a75abe296449ef9dcb8df7476cf45d5b036e`

MEASURED:
- max automation equivalence delta:
  **0.008853912 dB**
- max state restore delta:
  **0.000000000 dB**
- max normalized parameter roundtrip delta:
  **0.000000060**

Result:
- **PASS**

## pluginval

Final VST3:
- name: VL2A
- plugin version: v0.6.0

pluginval:
- version 1.0.4
- strictness level 10
- skip GUI tests
- final result: **SUCCESS**

Passed categories include:
- cold/warm open
- audio processing
- non-releasing processing
- plugin state
- state restoration
- automation
- automatable parameters
- parameter checks
- parameter thread safety
- bus/layout checks
- parameter fuzzing

VST3-validator subtest was skipped because no validator path was configured;
this does not alter the pluginval strictness-10 SUCCESS result and is retained
as an explicit limitation.

## Source-state audit

Final source audit: **PASS**

Confirmed:
- Peak v8 present
- optical v3 present
- Phase03G tau 8 ms present
- Phase03G amount 0.054 present
- rejected residual-HP branch removed from production path
- rejected LF-blend branch removed from production path
- direct Gain dB mapping present
- GR peak-hold atomic state present
- GR peak consumer present
- UI version label present
- parameter IDs:
  - `peakReduction`
  - `gain`
  - `mode`
- UI parameter bindings match
- state get/set implementations present

## Exact final-VST3 host latency

A separate host probe loaded the **exact final VST3 artifact** produced by the
final validation.

Run:
- `36232663877`
- conclusion: SUCCESS
- artifact id: `10903535910`
- digest:
  `sha256:9ede1e594b6b5dd5f1ce56e33f049ea0d75cf5ae9bebc9ccb0ac040f521a82cc`

MEASURED host-reported latency:
- before prepare: **0 samples**
- 48 kHz / 512: **6 samples**
- 44.1 kHz / 64: **6 samples**
- 96 kHz / 1024: **6 samples**

Result:
- **PASS**

### Latency apparent discrepancy review

pluginval's Plugin Info section reports latency 0 before the processing
configuration is prepared.

The dedicated exact-artifact host probe shows:
- pre-prepare latency = 0
- post-prepare latency = 6 samples

The Processor source derives latency from the JUCE oversampling object and
calls `setLatencySamples(latency)` during prepare.

Therefore the two observations are lifecycle-consistent and are **not a
contradiction**.

Cubase-specific compensation remains UNVERIFIED.

## CPU / PDC prior audit

Previously measured:
- 4x oversampling latency: 6 samples across tested blocks/channels
- worst full-engine CPU:
  ~5.0115% of one realtime core

Result:
- code-level PDC: PASS
- CPU safety: PASS

## Final contradiction review

Checked against retained negative results and current production source.

No unresolved contradiction was found in:
- Peak calibration lineage
- T4 matched-GR timing
- COMP/LIMIT topology
- R37 decision
- stereo detector product decision
- Phase01-H line amplifier
- Phase03B -> Phase03G optical lineage
- rejected Phase03C/D/E/F branches
- State/Automation evidence
- latency/PDC evidence
- final source audit

Important retained boundaries:
- exact 1966 stereo one-sided detector law is not claimed
- Phase03G remains a reduced stateful model, not a component-level T4A SPICE
  reconstruction
- human subjective preference is not measured
- Cubase Pro 14 host behavior is not yet verified

## Decision

**PROMOTE TO PRE-HOST FINAL CANDIDATE**

Automated/reproducible engineering validation is complete.

Remaining release gate:
- real Cubase Pro 14 confirmation only.
