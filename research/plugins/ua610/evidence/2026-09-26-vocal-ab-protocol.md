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


## CONTRASTING SOURCE ADDITION

### SOURCE_FACT
A second licensed/public-domain singing source is added to reduce dependence on one solo-style recording:

- Wikimedia Commons file: `Shenandoah.ogg`.
- Description: a cappella choral arrangement performed by the Singing Sergeants of the United States Air Force Band, featuring a soloist.
- Performance and recording are identified as United States Air Force work and documented as public domain in the United States on the Commons file page.
- Composition is traditional.
- Source page: `https://commons.wikimedia.org/wiki/File:Shenandoah.ogg`.

### AB RUNTIME BOUNDING
The renderer now supports deterministic source segments.

Initial reproducible render plan:
- Twinkle source: start 0 s, duration 30 s.
- Shenandoah source: start 0 s, duration 30 s.
- Source SHA-256 is written into each artifact's provenance file at workflow runtime.

Reason:
- robust-solver rendering can be computationally expensive;
- a bounded segment lets the four Original candidates plus bypass and preserved 610 be rendered reproducibly without requiring a full multi-minute song for every iteration;
- final perceptual closure may expand/relocate the segment if the bounded excerpts prove unrepresentative.

### INFERRED
The second source is a useful texture contrast because it adds denser a cappella choral/solo material, but it is not a substitute for singer-diverse solo-vocal validation. Final parameter lock must not claim broad singer generalization from these two sources alone.


## SPECTRAL-PROTECTION ABLATION ADDITION

### MEASURED
Run 39 `original_ablation.csv` under the robust Original solver measured Character 50 / -18 dBFS:

At 100 Hz:
- full path: gain **13.833 dB**, THD **1.01189%**;
- spectral protection off: gain **13.5977 dB**, THD **4.14854%**.

At 1 kHz:
- full path THD **0.234491%**;
- spectral protection off THD **0.234285%**.

At 10 kHz:
- full path THD **0.202057%**;
- spectral protection off THD **0.219435%**.

### INFERRED
The current pre/de-emphasis protection is materially changing low-frequency nonlinear drive rather than acting as a cosmetic EQ. It suppresses a large LF distortion increase while leaving the 1 kHz case almost unchanged in this measurement.

This numerical result does not prove the protection is perceptually preferable on vocals.

### AB REVISION
The real-vocal shortlist therefore adds:
- `conservative_no_protection`: same 4 dB / flux 8 / nonlinear 0.125 profile as `conservative`, but `spectralDriveProtection=false`.

This creates a controlled mechanism pair:
- conservative protection ON;
- conservative protection OFF.

The blinded listening artifact now contains seven files per corpus rather than six.

### STATUS
Spectral protection remains PROVISIONAL until the level-matched vocal pair is listened to. The Run 39 measurement justifies carrying the mechanism into AB; it does not authorize final retention.
