# VL2A Peak Reduction sensitivity evidence / next gate — 2026-09-25

## Provenance
- Product repo: `techitechi0331-svg/VocalPrepComp`
- Current baseline for this later study: Phase 01-H KEEP candidate
- Obsolete research PR #13 was closed after re-audit because it targeted the older `feature/vocal2a-v0.3-reference` engine rather than the current Phase 01-H VL2A engine.
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
The next bounded sensitivity study must be rebuilt from the Phase 01-H KEEP / v0.5.0 production-candidate engine. The old PR #13 synthetic sweep is not eligible for calibration promotion and is retained only as discarded exploratory work.

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


## 2026-09-25 architecture re-audit

The earlier Peak Reduction study PR #13 is **REJECTED as a production research base**.
Reason: it was created from `feature/vocal2a-v0.3-reference`, while the actual
current VL2A product path is `build-vocal-leveler2a-v01` plus the retained
Phase 01-H line-amplifier integration.

This prevents numerical constants from crossing between two different detector /
T4 / side-chain implementations.

Required new baseline:
- Phase 01-H KEEP engine;
- final Gain -18..+18 dB integration;
- current `LA2AEngine::sidechainDrive()`, `sidechainExcitation()`, T4 cell and COMP/LIMIT path.

Old PR #13 status: **OBSOLETE / CLOSED / DO NOT MERGE**.
