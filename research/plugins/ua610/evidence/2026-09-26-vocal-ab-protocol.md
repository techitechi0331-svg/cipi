# Original Vocal Pre — level-matched real-vocal AB protocol

Date: 2026-09-26

## SOURCE_FACT

Product repo:
- `techitechi0331-svg/610`
- branch: `original-vocal-pre-v0.1`

CIPI track:
- `UA610_ORIGINAL_VOCAL_PRE`
- knowledge status remains `PROVISIONAL`.

A dedicated offline renderer has been added to prepare time-aligned, active-RMS-matched listening files:
- `Tests/OriginalABRenderer.cpp`

The renderer prepares:
- A: latency-aligned bypass;
- B: preserved 610 research baseline;
- C: Original 4 dB drive, output transformer disabled;
- D: Original 4 dB conservative output-transformer profile;
- E: Original 6 dB balanced output-transformer profile;
- F: Original 6 dB stronger color-contrast profile.

Initial open singing source:
- Wikimedia Commons file: `Twinkle Twinkle Little Star - sung with full lyrics.ogg`
- source page: https://commons.wikimedia.org/wiki/File:Twinkle_Twinkle_Little_Star_-_sung_with_full_lyrics.ogg
- performer/uploader: Dcoetzee / Derrick Coetzee
- approximately 2 min 6 s, a cappella human singing;
- the uploader describes the performance as their own singing;
- license: CC0 1.0 Universal public-domain dedication.

This source is selected as a first reproducible listening corpus, not as a claim that one singer represents all vocal production.

## MEASURED BASIS FOR SHORTLIST

Run 39 robust-solver measurements show all five numerical shortlist profiles pass the current technical gates.

The listening shortlist intentionally removes `simple6_no_output_tx` while retaining:
- `simple4_no_output_tx` — cleanest transformer ablation anchor;
- `conservative` — 4 dB with output transformer;
- `balanced` — 6 dB with output transformer;
- `color_contrast` — stronger nonlinear/transformer contrast.

Reason:
- the 4 dB no-TX / 4 dB TX pair directly tests output-transformer contribution at the same drive range;
- conservative vs balanced tests the practical 4 dB vs 6 dB Character range;
- color_contrast tests whether stronger coloration is ever perceptually useful or is consistently excessive;
- preserving the 610 baseline keeps the original research-derived reference audible.

## LEVEL-MATCH PROTOCOL

The renderer:
- uses 8x oversampling for the 610 and Original processed paths;
- aligns bypass to the larger reported integer latency of the processed paths;
- uses an active-sample RMS reference rather than raw unaligned whole-file RMS;
- matches each processed render back to the aligned bypass active RMS;
- emits matching gain, active RMS, peak and latency metadata.

The current active-RMS matcher is a controlled listening preparation method, not an EBU R128 compliance claim.

## LISTENING QUESTIONS

For every source, listening must explicitly inspect:
- vocal density/body;
- consonant and transient preservation;
- harshness/sibilance change;
- low-mid mud;
- pitch/formant naturalness;
- apparent forwardness after level matching;
- overload or grain on louder notes;
- whether output-transformer spectral tilt helps or dulls the vocal;
- whether 6 dB Character is meaningfully more useful than 4 dB;
- whether color_contrast adds musically useful color or merely more distortion.

## DECISION RULE

Do not select a final product profile from numerical metrics alone.

A profile may advance only if:
- Windows numerical gates remain green;
- no solver-collapse regression returns;
- CPU/latency is acceptable for normal DAW insert use;
- level-matched singing material does not reveal repeated audible regressions;
- the result still fits the intended minimal four-control product.

## HYPOTHESIS

The conservative 4 dB and balanced 6 dB profiles are expected to define the practical central range, while no-TX and color_contrast should help identify which coloration mechanisms are actually perceptually useful.

This remains a hypothesis until rendered listening evidence exists.

## REMAINING

- Build and validate the AB renderer on Windows.
- Measure 4x/8x/16x CPU and latency.
- Render the CC0 a-cappella source.
- Inspect metrics and listening files.
- Add at least one contrasting vocal source before parameter lock if a suitably licensed source is available.
- Complete user-side Cubase Pro 14 validation.
