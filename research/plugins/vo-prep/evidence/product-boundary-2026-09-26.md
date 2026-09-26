# Vo.Prep Product Boundary Evidence — 2026-09-26

## Decision

Vo.Prep is a Problem / Event Preparation Plugin.
VoPriPro / VocalPrepComp owns broadband vocal dynamics preparation.

The transparent-compressor research is preserved but is out of scope for Vo.Prep product adoption.

## SOURCE_FACT

- Vo.Prep main 28afccdf contains Plosive Guard v2.2, Macro Level v2.1, Sibilance Guard v2.3 and utility/metering infrastructure.
- VocalPrepComp main cc796d30 is the VoPriPro broadband vocal-dynamics product track.
- VoPriPro current evidence includes Peak/RMS broadband detection, Amount mapping, Character mapping, attack/release timing, max-GR caps, detector HPF and a safety limiter.

## MEASURED retained from transparent-compressor research

- Slow RMS 25 ms.
- Fast instantaneous peak.
- max(Slow, Fast - 6 dB) fusion.
- Ratio 1.5:1.
- Knee 18 dB.
- Attack 8 ms.
- Release 70 ms.
- Hold 0.
- Lookahead 0.
- Objective integrated validation reached GO_FOR_BLIND.
- Amount mapping R1-R4 contains preserved negative evidence.

## INFERRED

- Productizing this broadband compressor inside Vo.Prep would overlap VoPriPro responsibility and blur the distinction between problem/event preparation and broadband dynamics preparation.
- Macro Level may still coexist because its current 700 ms / 2.5 s time scale is substantially slower and weaker than VoPriPro, but this requires dedicated boundary measurement.

## HYPOTHESIS

- A slow Macro/Phrase Guard can reduce 1–2 s phrase spread while leaving 50–100 ms dynamics and VoPriPro downstream gain reduction substantially intact.
- Plosive and Sibilance Guards can improve downstream VoPriPro detector behavior without materially removing useful low-vocal body or presence/air.

## REJECTED

- REJECTED BY PRODUCT SCOPE: broadband Transparent Compressor adoption inside Vo.Prep.
- NOT REJECTED: the transparent compressor DSP research itself.

## Next product research

1. Macro/Phrase boundary study versus VoPriPro.
2. Plosive false-positive / false-negative refinement.
3. Sibilance false-positive / false-negative refinement.
4. Vo.Prep -> VoPriPro integration validation.

No raw audio is stored in CIPI.
