# VL2A — Formal Product Research Track

## Provenance

- **Product repository:** `techitechi0331-svg/VocalPrepComp`
- **Product branch:** `build-vocal-leveler2a-v01`
- **Imported product head:** `27ea4b68d17c45b9ea43d1eb73d15764cb107c06`
- **Reference-device truth track:** `research/reference_devices/la2a/`
- **Import date:** 2026-09-25

This track records product-specific evidence and decisions for VL2A. It does not duplicate the LA-2A reference-device truth track. Hardware/reference claims continue to live under `research/reference_devices/la2a/`.

## Research target

Build a vocal-oriented optical leveler inspired by the documented LA-2A/Gray architecture while preserving explicit separation between:

- reference-device facts;
- product calibration choices;
- measured VL2A implementation behavior;
- unresolved hardware/model uncertainty.

Formal lifecycle:

`Research -> Review -> Parameter Lock -> Implementation -> Measurement -> Level-matched Audio AB -> Revision -> VST3 Host Validation -> Final Review`

## Current product architecture

Main signal path under active development:

`input transformer -> T4 optical attenuation -> Gain -> integrated line amplifier -> output`

The Phase 01-H integrated line-amplifier candidate replaces only the historical main-audio tube/output-transformer approximation. T4, R37/sidechain, Peak Reduction law, Compress/Limit behavior, parameter IDs, and UI were intentionally kept unchanged during the line-amplifier experiment.

## SOURCE_FACT

Reference-device facts are inherited from the CIPI LA-2A truth track and the source-led product research.

Key facts used by the product work:

- the documented line amplifier uses 12AX7 voltage-amplifier circuitry followed by a 12BH7 cathode-follower/output-driver stage and output transformer;
- the output transformer is documented as UTC A-24 in the studied revision;
- historical documentation describes approximately 20 dB overall amplifier feedback;
- A-24 catalog constraints include a 15 kOhm split primary, 600-ohm secondary option, catalog response envelope, primary DCR evidence, and no unbalanced primary DC for the catalog application;
- manufacturer complete-unit specifications are treated as system envelopes, not as per-device distortion targets.

These statements are product inputs, not proof of an exact surviving Gray-unit operating point.

## MEASURED

### Historical implementation audit

The previous line-amplifier approximation showed an artificial low-level distortion floor.

For the old 12AX7-like piecewise transfer:
- positive small-signal slope ~1.094325;
- negative small-signal slope ~1.069855;
- output value remains continuous at zero;
- first derivative is discontinuous at zero.

Extended 1 kHz tests showed relative THD remaining near ~0.49% through very low input levels instead of naturally decaying.

This historical path is retained as Baseline A but rejected as the final fidelity primitive.

### 12AX7 research/review

A measured-device-family 12AX7 reference based on Dempwolf/Zoelzer-style equations was used as a physical reference family, not as proof of the exact target tube.

A realtime reduced primitive was developed and strictly reviewed. The original LUT direction was later replaced during integrated implementation by a smooth fifth-order polynomial fit to the already-approved closed-loop reference.

The 12AX7 primitive remains conditional on final integrated loading/feedback calibration.

### 12BH7 research/review

The current generic follower `tanh` approximation was rejected as the final 12BH7 model.

The surviving architecture is:
- explicit two-section / load-aware follower behavior;
- open-circuit transfer plus finite source resistance;
- explicit load interaction.

The physical reference family remains conditional because exact target-unit tube/bias/loading values are unavailable.

### A-24 research/review

The surviving realtime/reference architecture is linear-first:
- nominal ratio/load interface;
- primary DCR;
- bounded LTI dynamics;
- magnetic nonlinearity disabled unless later integrated measurements justify it.

No A-24-specific saturation/hysteresis constants are promoted as facts.

### Integrated Phase 01-H compiled measurement

Authoritative Windows compiled measurement:
- workflow run: `36043621530`
- measurement artifact: `10829478410`
- VST3 artifact: `10829637923`

At 48 kHz host / 192 kHz internal:

Frequency response, -36 dBFS:
- 30 Hz: about -0.0436 dB
- 1 kHz: about -0.00050 dB
- 15 kHz: about -0.00810 dB

1 kHz THD:
- -48 dBFS: ~0.0000164%
- -24 dBFS: ~0.000294%
- -12 dBFS: ~0.001177%
- -6 dBFS: ~0.002295%
- 0 dBFS: ~0.004178%

Secondary output-source proxy:
- about 150.53 to 150.75 ohms over the tested range.

Sample-rate behavior:
- no material drift was observed from 44.1 to 192 kHz in the compiled block test.

Stress:
- finite through +30 dBFS-equivalent stress;
- no NaN/Inf observed.

Compiled block microbenchmark:
- ~17.96 ns/sample in the benchmark environment.

These are line-amplifier-block measurements, not complete VL2A/LA-2A THD specifications.

### Automated real-vocal objective AB

Workflow run:
- `36057598192`
- artifact: `10833729675`
- source corpus: VocalSet CC BY 4.0, pinned source selection

Matrix:
- breathy / straight / forte
- Peak Reduction 0 / 50 / 75
- same historical T4/sidechain/oversampling path
- Baseline line amp vs Phase 01-H candidate line amp only

After RMS level matching:
- correlation: ~0.999928 to ~0.999937
- residual relative level: ~-38.39 to ~-38.99 dB
- candidate match gain required: ~+1.105 to +1.146 dB

Interpretation:
- the candidate change is subtle but consistently measurable;
- compression GR itself is unchanged in the automated renders because the sidechain/T4 path was intentionally unchanged;
- objective metrics do not establish a subjective winner.

## INFERRED

- The historical low-level THD floor is structurally explained by the zero-crossing derivative mismatch in the old piecewise transfer.
- A load-aware V2 + transformer interface is more defensible than a generic post-tube waveshaper because it reproduces the integrated output-source target without hidden makeup hacks.
- The line-amplifier candidate is numerically mature enough that further coefficient tuning before listening would risk overfitting objective metrics.
- The automated vocal AB indicates a small, repeatable timbral/system response difference rather than a large gain/compression-law change.

## HYPOTHESIS

- The Phase 01-H line-amplifier candidate will sound at least as natural as Baseline A after strict level matching, with cleaner low-level texture and without added fuzz.
- The final product can keep transformer magnetic nonlinearity disabled unless later whole-system measurements/listening demonstrate a repeatable benefit.
- The final product Gain control can use the user-approved -18..+18 dB UX without changing the detector path, provided the final build preserves gain staging and preset/automation compatibility constraints.

These are not confirmed until the required listening/host gates pass.

## REJECTED

- Current historical 12AX7-like piecewise transfer as final fidelity model.
- Current historical generic 12BH7-like `tanh` blend as final fidelity model.
- Generic input/output transformer model as an exact A-24 representation.
- Assigning whole-unit LA-2A THD specifications directly to isolated tube or transformer blocks.
- Treating one measured 12AX7/12BH7 specimen model as "the Gray tube."
- Adding transformer hysteresis/saturation constants without target-specific evidence.
- Hard-coding a fixed Peak Reduction knob position to a target GR amount without input/reference calibration.

## Product numerical decisions currently carried forward

Strong/reference anchors:
- approximately 20 dB integrated feedback target at 1 kHz;
- output-source validation target approximately 150 ohms near 800 Hz;
- A-24 primary DCR 1430 ohms in the studied evidence set;
- nominal 5:1 ratio proxy for the selected load interface.

Product/reference calibration:
- -12 dBFS = +4 dBu;
- 0 dBFS = +16 dBu.

Phase 01-H implementation seeds/fit values:
- V2 central isolated source proxy ~233 ohms;
- A-24 effective secondary-series seed ~84 ohms;
- reduced A-24 HP seed 3 Hz;
- reduced A-24 LP seed 150 kHz;
- transformer magnetic nonlinearity OFF.

These fit values are not promoted as historical hardware facts.

Final user-approved product decision still pending implementation after AB:
- Gain range: -18..+18 dB, default/centre 0 dB.

## Real-audio AB plan

Current formal gate is human level-matched listening.

Use the dedicated blind AB pair from Phase 01-H, not unrelated historical builds.

Primary listening dimensions:
- natural vocal density;
- transient/consonant definition;
- low-level detail;
- harsh/fuzzy texture;
- low-end stability;
- high-frequency naturalness;
- noise/fizz between phrases.

The automated AB pack already contains level-matched and blinded files for breathy, straight and forte material at PR 0/50/75.

## VST3 / host validation

Windows VST3 compilation has passed for the Phase 01-H candidate.

Formal Cubase Pro 14 runtime validation is still pending and must include:
- scan/load;
- audio processing;
- parameter automation;
- state recall;
- coexistence/identity checks where relevant;
- final Gain -18..+18 build;
- top-left UI text/mojibake fix.

## Current location

**Level-matched Audio AB**

## Completed

- research;
- strict review;
- numeric determination;
- strict numeric review;
- regression-safe implementation;
- compiled Windows measurement;
- automated real-vocal render and objective AB analysis.

## Unresolved

- human blind listening verdict: KEEP / REVISE / ROLLBACK;
- final product Gain -18..+18 implementation;
- UI top-left text corruption fix;
- Cubase Pro 14 runtime validation;
- final product-level alias/oversampling decision;
- T4/R37/sidechain research remains intentionally downstream of this gate;
- final review.

## Next stage

Human level-matched real-vocal AB decision.

## Why this is the next stage

Objective/numeric gates have passed. The remaining question is whether the measurable replacement produces a repeatable audible benefit or regression on singing voice. Changing coefficients before that answer would introduce tuning without new evidence.

## What the next stage will confirm

Whether Phase 01-H is:
- KEEP;
- REVISE with a specific repeatable fault;
- ROLLBACK.

Only after KEEP should the product Gain/UI corrections be applied and the production VST3 move to Cubase validation.
