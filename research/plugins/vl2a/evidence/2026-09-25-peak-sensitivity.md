# VL2A Peak Reduction sensitivity evidence / next gate — 2026-09-25

## Provenance
- Product repo: `techitechi0331-svg/VocalPrepComp`
- Current baseline for this later study: Phase 01-H KEEP candidate
- Research PR prepared in product repo: #13 (Draft)
- Current source-side clue: Peak Reduction around 80 produced approximately 3 dB GR on one Cubase vocal test.

## SOURCE_FACT
- LA-2A topology is feedback-based; Peak Reduction controls side-chain drive / effective threshold.
- Original front-panel 0..100 markings are not a calibrated GR-in-dB scale.
- T4 recovery is program dependent; Peak Reduction sensitivity must not be 'fixed' by retuning release behavior.

## MEASURED / OBSERVED
- One real-host observation: PR ~80 -> ~3 dB GR on the tested vocal.
- This is source-level/material dependent and is not a universal knob law.
- Existing Phase 01-H A/B proved the main line-amplifier swap did not change GR trajectory, so this clue belongs to the T4/sidechain/Peak Reduction subsystem rather than the retained line amp.

## HYPOTHESIS
The current side-chain sensitivity may be conservative at lower vocal levels.
Product PR #13 contains a bounded synthetic sweep comparing:
- baseline calibration;
- minimal side-chain gain adjustment;
- an audio-taper-informed candidate.

## REJECTED
- adding a user Threshold control to conceal calibration;
- changing attack/release merely to increase meter movement;
- promoting a synthetic-tone winner without real-vocal measurement;
- using Input trim as a hidden side-chain calibration patch.

## Gate order
1. finish v0.5.0 production-candidate build/validation;
2. run deterministic sensitivity sweep and regression tests;
3. run real-vocal multi-level measurement;
4. level-matched audio review;
5. only then promote or reject a new Peak Reduction calibration.

Status: **QUEUED / not yet product-approved**.
