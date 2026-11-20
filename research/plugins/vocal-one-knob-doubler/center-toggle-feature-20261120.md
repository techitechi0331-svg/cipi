# Doubler CENTER ON/OFF — product feature handoff (2026-11-20)

## Development evidence, not research promotion

- Product truth: techitechi0331-svg/Vocal-One-Knob-Doubler
- Base branch: v0.5-research. Existing default main is not the latest research candidate.
- Feature PR: https://github.com/techitechi0331-svg/Vocal-One-Knob-Doubler/pull/1
- Feature spec: docs/CENTER_ON_OFF_FEATURE.md on the feature branch

Requested behavior:
- CENTER ON default: unchanged latency-aligned original dry center plus stereo generated doubles.
- CENTER OFF: remove only dry path; keep both generated voices audible.
- DOUBLE=0 and CENTER=OFF: intentional silence.
- APVTS CENTER boolean; 10 ms interpolated original-dry gain for click-safe switching.

## Research interpretation

This is a user-facing wet-only mode in the existing production architecture. It is **not** the MicroDouble antisymmetric-Side exact-mono mathematical proposal. Preserve previous v0.3 evidence, R1/R2 sibilance rejection, R3 results, and v0.5 transient necessity evidence separately. CENTER OFF can change mono sum and center-image level. No sound-quality or user-release claim is established by synthetic research.

## Required product acceptance before adoption/release

- Windows x64 VST3 build and pluginval strictness 5, including new APVTS state.
- Deterministic CoreTests for ON/OFF gain ramp, wet-only operation, and zero-knob silence.
- Cubase Pro 14 real-host automation, recall, bypass, loop/seek, mono/stereo buses, PDC, CPU, online/offline consistency.
- Level-matched real-vocal A/B and mono fold-down listening.
- Explicit human review and product adoption decision.

Do not automatically merge a development feature to product main, promote generic DSP knowledge, or mark release READY based on this handoff.
