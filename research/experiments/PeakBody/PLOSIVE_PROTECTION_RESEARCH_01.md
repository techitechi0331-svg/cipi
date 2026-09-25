# PeakBody Plosive-Protection Research 01

Status: **PROTOCOL LOCKED BEFORE MEASUREMENT**

## Research Question

Can PeakBody retain the private noise-rejection benefit of the strong-periodicity veto while restoring weakly periodic plosive-like transients by adding an **independent plosive-protection veto**?

And, under the Simple Baseline rule, is the full Vo.Prep Plosive Guard v2.2 contextual probability measurably better than a single low-frequency-concentration feature?

## Evidence that motivates this study

### REJECTED predecessor

Strong-periodicity veto:

`uP = clamp((periodicity - 0.55) / 0.25, 0, 1)`

`Vperiodic = smoothstep(uP)`

improved the private fixed noise-like reference mask:

- current proportional-periodicity guard median retention: **0.492622**
- strong-periodicity veto median retention: **0.295898**

while preserving private low-frequency/body/processing-invariance metrics.

However the locked synthetic gate rejected it:

- simple-veto plosive retention minimum: **0.054583**
- context-veto plosive retention minimum: **0.045417**
- required: >= **0.85**

Other synthetic classes passed.

### SOURCE_FACT / repository-verified Vo.Prep evidence

Vo.Prep Plosive Guard v2.2 uses:

- 20–80 Hz sub band;
- 250–1000 Hz mid reference;
- 80–4000 Hz broad reference;
- fast power envelope: 8 ms;
- sub local reference: 250 ms;
- broad local reference: 80 ms.

Features:

`subOnsetDb = subFastDb - subSlowDb`

`subToMidDb = subFastDb - midFastDb`

`subConcentrationDb = subFastDb - broadFastDb`

`broadOnsetDb = broadFastDb - broadSlowDb`

Mappings:

`c1 = sigmoid((subOnsetDb - 7.0) / 2.0)`

`c2 = sigmoid((subToMidDb - 12.0) / 3.5)`

`c3 = sigmoid((subConcentrationDb - 2.5) / 1.8)`

`c4 = sigmoid((broadOnsetDb - 1.0) / 3.0)`

Full contextual probability:

`Pplosive = exp(0.44 ln c1 + 0.30 ln c2 + 0.20 ln c3 + 0.06 ln c4)`

Vo.Prep product activation/release references are 0.75 / 0.55.

These values are repository-verified product evidence, not universal PeakBody constants.

## Common PeakBody base

Spectral noise evidence remains the existing PeakBody normalized high-band guard `S`.

Strong periodicity veto remains frozen:

`Vperiodic = smoothstep(clamp((P - 0.55) / 0.25, 0, 1))`

Protection terms are combined by maximum, not addition, to remain bounded:

`V = max(Vperiodic, Vplosive)`

Guard:

`G = 0.75 * S * (1 - V)`

Output transient factor:

`Tout = T * (1 - G)`

## Baseline A — rejected predecessor

No plosive protection:

`Vplosive = 0`

This is retained as the direct comparison baseline.

## Candidate C1 — Simple LF-Concentration Protection

Use **only** Vo.Prep's third normalized feature:

`Qsimple = c3`

Convert it to a conservative high-confidence veto using Vo.Prep's release/activation region:

`uQ = clamp((Qsimple - 0.55) / 0.20, 0, 1)`

`Vplosive = smoothstep(uQ)`

No onset, LF/mid ratio, broadband onset, event state, hysteresis or duration cap is used.

Purpose:
test whether one normalized LF-concentration cue is enough to rescue the current PeakBody failure.

## Candidate C2 — Full Contextual Plosive Protection

Use the complete repository-verified continuous Vo.Prep v2.2 probability `Pplosive`.

`uQ = clamp((Pplosive - 0.55) / 0.20, 0, 1)`

`Vplosive = smoothstep(uQ)`

Only the detector probability is reused.

Do **not** import:

- Vo.Prep audio attenuation;
- 140 Hz processing shelf;
- event hysteresis;
- 120 ms event cap;
- product Amount mapping.

Those belong to a different product purpose.

## Candidate-selection rule

Complexity is not free.

1. C1 is the preferred candidate if it passes every hard synthetic and private non-regression gate.
2. C2 may supersede C1 only if:
   - C1 fails a hard gate that C2 passes; or
   - C2 improves a predeclared target metric by >=0.03 absolute without worsening another hard gate.
3. If both fail, preserve both negative results and return to research.
4. Baseline A remains negative evidence and is not revived.

## Synthetic matrix

Run at:

- 44.1 kHz
- 48 kHz
- 96 kHz
- 192 kHz

Required cases:

### Existing PeakBody cases

- voiced low;
- voiced high;
- bright high-F0 harmonic;
- 6 dB SNR noisy bright voiced;
- sibilant;
- breath;
- long S;
- steady vowel;
- low-frequency plosive-like transient;
- startup bright vowel.

### Added plosive false-protection stresses

- sustained low male/proximity-like vowel;
- fry-like low harmonic/pulse stress;
- abrupt growl-like onset;
- LF-contaminated sibilant: high-band noise mixed with a low-frequency component.

These extra cases test whether plosive protection becomes a blanket exemption for any LF-heavy material.

## Synthetic hard gates

For C1/C2 independently:

- all values finite;
- standard voiced retention minimum >= **0.90**;
- bright/startup voiced retention minimum >= **0.95**;
- 6 dB SNR noisy-voiced retention minimum >= **0.90**;
- low-frequency plosive retention minimum >= **0.85**;
- sibilant/breath/long-S false-preservation maximum <= **0.25**;
- LF-contaminated-sibilant false-preservation maximum <= **0.35**;
- steady-vowel mean transient-factor delta <= **0.03**.

False-protection diagnostic:
- sustained-low/fry/growl protection strength is recorded.
- It is not by itself a hard failure unless it causes a target noise-like false-preservation gate to fail, because protection alone does not alter audio when spectral noise evidence is low.

## Private replay

Use the same four SHA-256-bound processing variants and the same **candidate-independent baseline masks**.

Required pooled reference counts already established:

- noise-like high-band: 246;
- low-frequency transient: 11,969;
- periodic body: 10,612;
- bright voiced: 0 (still an open corpus gap).

Private hard gates:

- noise-like median retention <= **0.35**;
- low-frequency transient median retention >= **0.90**;
- low-frequency transient p10 retention >= **0.80**;
- periodic-body mean absolute delta <= **0.03**;
- pairwise processing-variant correlation median >= **0.80**;
- correlation median not more than 0.05 below the current proportional-periodicity guard.

## Complexity gate for C2

If both C1 and C2 pass:

C2 requires at least one:

- private noise-like median improves >= **0.03** absolute vs C1;
- synthetic LF-contaminated-sibilant false-preservation improves >= **0.03** absolute vs C1;
- C2 materially rescues a hard gate that C1 fails.

Otherwise C1 wins by simplicity.

## No-tuning rule

All feature formulas, 0.55/0.75 protection mapping, 0.75 PeakBody guard ceiling and acceptance thresholds are locked before measurement.

Do not retune them from the result of this run.

## Scope limitation

Passing this study would create a **Revision-03 implementation candidate**, not a release candidate.

Still required afterward:

- broader multi-singer/high-register real-vocal corpus;
- realtime C++ CPU/block-size validation;
- dedicated product-repository implementation;
- level-matched audio AB;
- VST3 / Cubase Pro 14 gates.
