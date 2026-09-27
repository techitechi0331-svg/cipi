# Mic Simulator Foundation Inventory — 2026-09-27

## Existing evidence and integration state

### SOURCE_FACT
- Mic Simulator is registered in CIPI as the independent owner of microphone capture behavior.
- Virtual Guitar integration is a future optional/versioned dependency and must not reference Mic Simulator internals.
- Planned reference families include SM57, MD421, R-121, U87, C414 XLS and C414 XLII.
- Frequency-response copying alone is explicitly insufficient as microphone-simulation evidence.

### MEASURED / operational
- `MIC-E2E-CANARY-001` completed successfully through CIPI Cross-Repo orchestration on the dedicated Mic Simulator runner.
- At Foundation start, the product repository contains the canary workflow only; there is no validated real-microphone DSP evidence yet.

### Existing REJECTED / prohibited directions
- Treating a copied EQ curve as sufficient microphone simulation.
- Claiming hardware equivalence from build/canary success.
- Automatic product adoption, release, or CIPI knowledge promotion.
- Coupling Virtual Guitar to Mic Simulator internal classes or unversioned latest-main behavior.
- Folding Cabinet and Mic into one opaque response.
- Using fake stereo width as the default single-close-mic behavior.

## Foundation gaps before this track
- Deterministic DAW-independent measurement harness.
- Machine-readable Mic Result Bundle.
- Explicit baseline ladder A/B/C/D.
- Reusable Source Profile / Mic Model boundary.
- Dedicated core-validation workflow beyond canary.
- MELON Mic-domain adapter using existing cache/dedup/Pareto infrastructure.
- Closed CIPI -> MELON -> Runner -> Result Bundle -> CIPI evaluation loop.

## Non-goals of Foundation
- No SM57/R-121/MD421/U87/C414 parity claim.
- No subjective listening conclusion.
- No Cubase product confirmation.
- No production integration or release.

This inventory is the dedup baseline for `MIC-SIM-FOUNDATION-001`.
