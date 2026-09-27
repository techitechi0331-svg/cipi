# VL2A HA-100X Phase-2 shortlist baseline

Date: 2026-09-27
Parent track: VL2A-CIRCUIT-HA100X-001
Next track: VL2A-CIRCUIT-HA100X-SHORTLIST-002
Authority: research evidence only
Product mutation: PROHIBITED

## Phase-1 completion

The Phase-1 bounded HA-100X track completed:
- 5 / 5 runs;
- 60 / 60 measured candidates;
- 32 catalog-compatible candidates;
- no automatic product decision;
- no automatic knowledge promotion;
- no product repository write.

Evidence boundary remains:
**MEASURED_SIMULATION_NOT_HARDWARE_TRUTH**.

The Phase-1 result supports continuing with a linear/load-aware family before adding unsupported saturation or hysteresis.

## Shortlist method

The fixed shortlist below was selected from the 60 Phase-1 measured candidates using a conservative balance of:
- UTC catalog-envelope compatibility;
- soft-prior distance to the lower-tier DCR/Lm evidence neighborhood;
- source/load-matrix worst deviation;
- T4-dependent load interaction;
- parameter diversity, so Phase-2 does not collapse prematurely to one Lm/parasitic region.

The research-only ranking score from Phase-1 is not a product score and is not sufficient for adoption by itself.

## Fixed five candidates

### 1. HA100X-R4-012-591362e2
MEASURED simulation:
- primary DCR: 64.4205627169 ohm
- secondary DCR: 3031.53608905 ohm
- Lm: 23.7875627737 H
- leakage: 0.16910013055 mH
- Csec: 18.9716582714 pF
- core-loss R: 266576.914878 ohm
- nominal turns ratio: 10
- catalog max abs relative deviation: 0.0224244451 dB
- 30 Hz relative to 1 kHz: -0.0224244451 dB
- 20 kHz relative to 1 kHz: -0.0172009406 dB
- soft-prior distance: 0.0946526894
- max T4-load delta: 1.0744499821 dB
- source/load-matrix worst catalog deviation: 0.0397819572 dB
- Phase-1 research-only score: 0.0581113481

### 2. HA100X-R5-001-17927f57
MEASURED simulation:
- primary DCR: 61.8681313057 ohm
- secondary DCR: 3140.91945277 ohm
- Lm: 33.3567578586 H
- leakage: 0.61833863928 mH
- Csec: 23.6776043687 pF
- core-loss R: 53481.4914015 ohm
- nominal turns ratio: 10
- catalog max abs relative deviation: 0.0129276261 dB
- 30 Hz relative to 1 kHz: -0.0112773640 dB
- 20 kHz relative to 1 kHz: -0.0129276261 dB
- soft-prior distance: 0.1713969185
- max T4-load delta: 1.0898357546 dB
- source/load-matrix worst catalog deviation: 0.1382109637 dB
- Phase-1 research-only score: 0.0604338790

### 3. HA100X-R5-007-8542669a
MEASURED simulation:
- primary DCR: 64.7991826509 ohm
- secondary DCR: 3248.32203578 ohm
- Lm: 17.1753183001 H
- leakage: 0.29932397042 mH
- Csec: 28.9342542419 pF
- core-loss R: 147268.925458 ohm
- nominal turns ratio: 10
- catalog max abs relative deviation: 0.0429910620 dB
- 30 Hz relative to 1 kHz: -0.0429910620 dB
- 20 kHz relative to 1 kHz: -0.0377188962 dB
- soft-prior distance: 0.1207723009
- max T4-load delta: 1.0861909112 dB
- source/load-matrix worst catalog deviation: 0.0807052095 dB
- Phase-1 research-only score: 0.0828307254

### 4. HA100X-R2-006-ddb69925
MEASURED simulation:
- primary DCR: 58.4892533052 ohm
- secondary DCR: 3299.14778940 ohm
- Lm: 22.5298553992 H
- leakage: 0.43258513216 mH
- Csec: 27.6083573487 pF
- core-loss R: 31049.1331326 ohm
- nominal turns ratio: 10
- catalog max abs relative deviation: 0.0263235482 dB
- 30 Hz relative to 1 kHz: -0.0244133560 dB
- 20 kHz relative to 1 kHz: -0.0263235482 dB
- soft-prior distance: 0.2375964912
- max T4-load delta: 1.0736680115 dB
- source/load-matrix worst catalog deviation: 0.1142318293 dB
- Phase-1 research-only score: 0.0834363821

### 5. HA100X-R5-012-d9f4ef6a
MEASURED simulation:
- primary DCR: 66.9326790061 ohm
- secondary DCR: 3206.58232993 ohm
- Lm: 16.9247236768 H
- leakage: 0.18097972766 mH
- Csec: 34.1330962942 pF
- core-loss R: 78422.7186266 ohm
- nominal turns ratio: 10
- catalog max abs relative deviation: 0.0654680506 dB
- 30 Hz relative to 1 kHz: -0.0441371735 dB
- 20 kHz relative to 1 kHz: -0.0654680506 dB
- soft-prior distance: 0.1636941308
- max T4-load delta: 1.0853471029 dB
- source/load-matrix worst catalog deviation: 0.1196004831 dB
- Phase-1 research-only score: 0.1117291122

## Phase-2 stress protocol

Phase-2 keeps the five candidates fixed. It does not generate another broad random transformer family.

For each candidate, MELON will apply deterministic local parameter stress around:
- primary DCR: +/-5%
- secondary DCR: +/-5%
- Lm: +/-15%
- leakage inductance: +/-30%
- secondary capacitance: +/-30%
- core-loss resistance: +/-30%

This profile is classified as:
**SYNTHETIC_PARAMETER_STRESS_NOT_HARDWARE_TOLERANCE**.

It is only a numerical robustness test. The percentages are not claims about UTC manufacturing tolerance.

## Phase-2 gates

MELON may:
- remeasure the fixed shortlist;
- rank numerical robustness;
- repeat under denser deterministic stress;
- propose a CANDIDATE_FOR_CIPI_REVIEW.

MELON may not:
- adopt a candidate into VL2A;
- write the product repository;
- claim any candidate parameter as measured HA-100X hardware truth;
- unlock saturation/hysteresis;
- bypass compiled isolation, real-audio AB, Cubase confirmation or human product-adoption review.

Expected terminal state:
**HUMAN_GATE** after the bounded shortlist validation if a robust finalist survives.
