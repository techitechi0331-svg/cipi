# PeakBody Product Handoff Contract

## Current state

CIPI is the formal common Research OS.

A dedicated PeakBody product repository is **not currently available** in the connected GitHub repositories.

The existing PeakBody code on CIPI branch `dev/peakbody-v0.1-current` is classified as an **experimental prototype implementation**, not the long-term product repository.

## Repository boundary

### CIPI owns

- research sources and provenance;
- SOURCE_FACT / MEASURED / INFERRED / HYPOTHESIS / REJECTED classification;
- equations and mechanism studies;
- parameter-lock history;
- negative results;
- Research Jobs and autonomous measurements;
- measurement artifacts and checksums;
- reusable Knowledge Candidates;
- validation methodology and research decisions.

### Dedicated PeakBody product repo must own

- JUCE/C++ product DSP;
- VST3 target and packaging;
- product CI;
- pluginval / Steinberg validator integration for the product binary;
- versioning and release artifacts;
- UI and product state;
- Cubase-facing implementation fixes.

## Current product specification to migrate

Revision 02 is the current implementation target:

- crest integration: 80 ms;
- `C2 = p2 / max(r2, epsilon)`;
- `t = clamp(log2(max(C2, 2) / 2) / 2, 0, 1)`;
- attack: `6 + 34*t` ms;
- release: `400 - 280*t` ms;
- Amount 0–100%:
  - threshold -8 to -24 dBFS;
  - ratio 1:1 to 4:1;
- knee: 6 dB;
- output: -12 to +12 dB.

These are prototype parameters and remain HYPOTHESIS/MEASURED, not release lock.

## Required first product-repo gates

When the dedicated repository exists:

1. port only the reviewed Revision 02 specification;
2. preserve the 30 ms burst and 150 ms body regression tests;
3. build Windows VST3;
4. run pluginval strictness 5;
5. run Steinberg VST3 SDK validator;
6. benchmark product CPU at 44.1 / 96 / 192 kHz;
7. perform level-matched vocal AB;
8. perform Cubase Pro 14 host validation;
9. return reusable findings to CIPI.

## Blocker

The connected GitHub toolset can inspect and modify existing repositories but does not expose repository creation.

Until a dedicated PeakBody repository exists, no additional product DSP implementation should be merged into CIPI main.
