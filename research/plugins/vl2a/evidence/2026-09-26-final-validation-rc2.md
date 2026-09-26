# VL2A v0.6.0 RC2 final validation — 2026-09-26

## Status

**MEASURED / assistant-side final validation PASS**

This record does not claim the final Cubase Pro 14 host gate is complete.

## Product provenance

Repository:
- `techitechi0331-svg/VocalPrepComp`

Branch:
- `integration/vl2a-v060-rc2`

Validated source SHA:
- `4733b8a34450ef743b570b3d97951925502ea37f`

Workflow:
- run `36199539214`
- conclusion: SUCCESS

Evidence artifact:
- id `10891648604`
- digest:
  `sha256:fbafa19f8b5825f21c82d6a8a408b44abd1aea8a87c7e256999a217a202d5416`

Final VST3 artifact:
- id `10891448870`
- digest:
  `sha256:9b314f0298bbf1680eb991eb7e9aae3a64ecc9ac443a89496721722d27ce12fe`

## Final production DSP state

Peak Reduction:
- v8 mapping
- real-vocal -18 dBFS / COMP / PR50 operating target retained

Optical coloration:
- stateful optical variant v3
- optical mean tau: **8 ms**
- coloration amount: **0.054**
- residual HP: **none**
- rejected residual-LF structures removed

Gain:
- direct -18..+18 dB mapping

Meter:
- atomic audio-block GR peak capture
- numeric GR peak-hold
- smooth 20 dB bar retained

## MEASURED final PR50 real-vocal gate

Peak-normalized to -18 dBFS / COMP / PR50:

- breathy max GR: **5.30939 dB**
- straight: **5.55217 dB**
- forte: **6.40301 dB**
- median: **5.55217 dB**

Gate:
- median 5..7 dB
- all clips inside the accepted per-clip window

Result:
- **PASS**

## MEASURED matched-GR control gate

- matched Peak Reduction: ~41.77399
- start GR: ~5.70247 dB
- retained at 60 ms: ~0.508470
- sample-rate GR spread: ~0.033024 dB

Result:
- **PASS**

## MEASURED final color-isolation A/B

Level-matched optical-off vs final G054:

Breathy:
- correlation ~0.999782
- derivative delta ~+0.0308 dB
- max band shift ~0.1912 dB

Straight:
- correlation ~0.999951
- derivative delta ~-0.0069 dB
- max band shift ~0.0588 dB

Forte:
- correlation ~0.999919
- derivative delta ~0.000004 dB
- max band shift **~0.742962 dB**

Strict gate:
- correlation >=0.99
- |derivative delta| <=0.50 dB
- max band shift <=0.75 dB

Result:
- **PASS**

## pluginval

pluginval:
- v1.0.4
- strictness: 10
- GUI tests skipped
- result: **SUCCESS**

Passed areas include:
- cold/warm open
- audio processing at 44.1 / 48 / 96 kHz
- block sizes 64..1024
- non-releasing processing
- plugin state
- state restoration
- automation
- automatable parameters
- parameter fuzzing
- parameter thread safety
- bus/layout checks

## State / source audit

PASS:
- Peak v8 present
- optical v3 present
- Phase03G 8 ms present
- Phase03G amount 0.054 present
- rejected HP removed
- rejected LF blend removed
- direct Gain mapping present
- GR peak atomic / consumer present
- UI RC2 version present
- parameter IDs:
  - peakReduction
  - gain
  - mode
- UI parameter attachments match
- state get/set present

## Latency caveat / open precision check

Earlier code-level audit measured JUCE 4x oversampling latency at **6 samples**
and confirmed the Processor derives its latency declaration from
`oversampling->getLatencyInSamples()` and calls `setLatencySamples(latency)`.

However pluginval's generic "Plugin info" section printed:
- `Reported latency: 0`

This line is observed before the exact post-`prepareToPlay` host-latency
state has been independently verified.

Therefore:
- internal oversampling latency: MEASURED 6 samples
- code-level declaration path: PASS
- exact loaded-VST3 post-prepare host latency: **REOPEN / precision check**
- do not classify the pluginval pre-prepare 0 as a confirmed PDC bug yet

Dedicated workflow:
- `VL2A Exact VST3 Host Latency`
- intended to load the exact final VST3 artifact and verify latency after
  prepare at 44.1/48/96 kHz.

## Remaining external host-only gate

Cubase Pro 14:
- VST3 scan
- insert
- playback
- automation
- project save/reload
- practical PDC confirmation

Status:
- **UNVERIFIED / user-host-only**
