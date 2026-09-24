# CIPI Comprehensive Plug-in Research Catalog

This catalog links every materially developed plug-in or plug-in research program currently known to the project into CIPI research governance.

## Reference-device / hardware-inspired tracks
- LA2ACompressor / LA-2A / T4 -> `research/reference_devices/la2a/`
- VL2A product implementation track -> `research/plugins/vl2a/` (reuses the LA-2A reference-device truth track; product measurements and decisions only)
- 76blackCompressor / 1176 family -> `research/reference_devices/1176/`

## Repository-backed imported tracks
- VoPriPro / VocalPrepComp -> `research/plugins/vopripro/`
- Vocal Control Comp -> `research/plugins/vocal-control-comp/`
- Vocal Surface Processor -> `research/plugins/vocal-surface/`
- Vocal One-Knob Doubler -> `research/plugins/vocal-one-knob-doubler/`
- Vocal Resonance Suppressor research -> `research/plugins/vocal-resonance/`
- Master Bus Comp -> `research/plugins/master-bus-comp/`
- Vo.Prep -> `research/plugins/vo-prep/`
- 610-B Research Pre -> `research/plugins/ua610/`
- Vocal 73 Pre (1073 direction) -> `research/plugins/vocal73pre/`

## Historical project tracks without a standalone connected repository
- Envelope Sculptor -> `research/plugins/envelope-sculptor/`
- Vocal Finisher -> `research/plugins/vocal-finisher/`
- Dynamic EQ -> `research/plugins/dynamic-eq/`
- Vocal Noise Gate -> `research/plugins/noise-gate/`

These historical tracks are deliberately provenance-limited until source and artifacts are imported.

## CIPI-native formal experiment tracks
These already have authoritative `status.yaml` files and are not duplicated:
- `research/experiments/VoxLevel/`
- `research/experiments/AirGuard/`
- `research/experiments/Density/`
- `research/experiments/PeakBody/`
- `research/experiments/MicroDouble/`
- `research/experiments/ResonancePilot/`

## Alias / duplication policy
- VoPriPro is the current identity of the VocalPrepComp repository.
- Vocal 73 Pre is the 1073-direction project nested under VocalPrepComp.
- LA-2A and 1176 implementation research reuses the formal reference-device truth tracks instead of duplicating claims.
- Idea-only concepts are excluded until they have a concrete experiment, implementation artifact, or formal research question.

## Knowledge extraction target
As tracks mature, promote reusable mechanisms out of product folders into shared CIPI knowledge: detectors, envelopes, program-dependent dynamics, vocal-event detection, spectral/resonance analysis, nonlinear color/antialiasing, stereo decorrelation/mono safety, gain-trajectory modeling, measurement and host validation.
