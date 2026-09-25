# VoPriPro Product Boundary v1.0

## Product scope decision

Product: VoPriPro
Product repo: techitechi0331-svg/VocalPrepComp
Production baseline: cc796d30d7e1885e0ca66caaf7f1b02d0bffeb33
Related product: techitechi0331-svg/Vo.Prep

VoPriPro is the Broadband Dynamics Preparation Compressor.
Vo.Prep is the separate Problem / Event Preparation Plugin.

VoPriPro owns broadband gain reduction, short-to-medium-term dynamics stabilization, INPUT drive, AMOUNT compression intensity, CHARACTER compressor response, operating-reference calibration, manual OUTPUT gain, and emergency-only sample-peak limiting.

VoPriPro does not absorb Plosive Guard, Sibilance Guard, Macro/Phrase Rider, resonance/noise cleanup, saturation/analog coloration, channel-strip functions, or finisher functions.

Current VoPriPro main remains the simple production baseline until a candidate clearly outperforms it.

## Vo.Prep transparent-compressor transfer policy

Reusable comparison candidates include:
- 25 ms Slow RMS
- instantaneous Fast Peak
- max(Slow, Fast - 6 dB) fusion
- 1.5:1 / 18 dB soft knee
- 8 ms attack / 70 ms release
- learned/relative operating point
- Amount mapping research
- stereo-link research

These are research inputs, not drop-in replacements. Each transfer must be compared against the current VoPriPro path on the same signals/corpus with predeclared gates.

## Evidence classes

SOURCE_FACT:
- VoPriPro public controls are INPUT / AMOUNT / CHARACTER / OUTPUT.
- Current main uses feed-forward broadband compression, Active Level / Auto Threshold calibration and a final sample-peak limiter.
- Vo.Prep separately researches event preparation and transparent-compressor mechanisms.

MEASURED:
- VoPriPro main cc796d30 has the existing build, DSP regression, pluginval and four-recording x six-setting engineering evidence registered in this track.
- Vo.Prep transparent-core measurements remain under the Vo.Prep track.

INFERRED:
- Product separation makes duplicate dynamics responsibilities and failure attribution clearer.
- Vo.Prep compressor findings are useful transfer candidates but need same-corpus comparison.

HYPOTHESIS:
- Slow+Fast Peak fusion may improve transient/body discrimination over the current Natural50 detector.
- 8/70 fixed ballistics or other CIPI timing mechanisms may improve some use cases.
- Alternative Amount mapping may improve intensity uniformity.
- Vo.Prep preprocessing may reduce unwanted event-triggered VoPriPro gain reduction without harmful double processing.

REJECTED FOR VOPRIPRO PRODUCT SCOPE:
- Plosive Guard
- Sibilance Guard / De-Esser
- Macro/Phrase Rider
- resonance/noise cleanup
- saturation/analog coloration
- channel-strip/finisher features

This is a scope rejection, not a technical rejection of those algorithms.

## Next research order

1. Detector transfer screen.
2. Ballistics transfer screen.
3. Amount mapping comparison.
4. Knee / sidechain HPF comparison only if still material.
5. Vo.Prep -> VoPriPro integration study.
6. Level-matched human listening.
7. Cubase Pro 14 target-host validation.
8. Final precision review.

No transfer mechanism enters product main unless it beats the current production baseline on predeclared gates, preserves regressions/realtime constraints, survives level-matched listening, and keeps the Vo.Prep / VoPriPro boundary intact.
