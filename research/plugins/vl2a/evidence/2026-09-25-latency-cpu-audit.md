# VL2A latency / PDC / CPU audit — 2026-09-25

## Classification

- MEASURED: JUCE oversampling latency and full-engine CPU benchmark
- SOURCE_FACT: product Processor source reports oversampling latency through JUCE API
- INFERRED: Cubase/VST3 PDC receives the same measured latency value through JUCE AudioProcessor latency reporting
- UNVERIFIED: Cubase Pro 14 host behavior itself remains user-host gate

## Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Branch:
- `integration/vl2a-v060-rc2`

Workflow:
- run `36179120522`
- conclusion: SUCCESS
- source SHA: `07cfaf4fa1e80b61b5796679e52dbae0f2a6d043`

Artifact:
- id `10883896054`
- digest:
  `sha256:57a87428505e1266e1a15b090f298a5fe45fb6e687b3d43321bf2e7d8b2220c3`

## MEASURED oversampling latency

JUCE configuration:
- factor: 4x
- two polyphase-IIR oversampling stages

Measured latency:
- mono, block 32..2048: **6 samples**
- stereo, block 32..2048: **6 samples**

Thus measured latency is block-size and channel-count invariant in the tested matrix.

## SOURCE / implementation audit

Embedded Processor source:
- creates the same JUCE `Oversampling<float>`
- calls `oversampling->getLatencyInSamples()`
- rounds that value
- calls `setLatencySamples(latency)`

Therefore the host-facing PDC value is derived directly from the same JUCE
oversampling object whose measured latency is 6 samples.

This closes the code-level PDC mismatch risk.

Cubase host compensation remains UNVERIFIED until the real host gate.

## MEASURED CPU benchmark

48 kHz host rate, full VL2A engine plus 4x oversampling, approximately 12 s of
audio per case.

Mono:
- block64: ~4.35% of one realtime core
- block128: ~4.30%
- block256: ~4.30%
- block512: ~4.28%
- block1024: ~4.31%

Stereo:
- block64: ~4.99%
- block128: ~5.00%
- block256: ~5.01%
- block512: ~5.01%
- block1024: ~4.86%

Worst measured:
- **~5.0115% of one realtime core**

Predeclared CPU safety gate:
- <50% of one realtime core

Result:
- **PASS with large margin**

## Decision

- oversampling latency measurement: PASS
- Processor latency declaration: PASS
- CPU safety gate: PASS
- Cubase PDC behavior: still UNVERIFIED host-only gate

No DSP change is required by this audit.
