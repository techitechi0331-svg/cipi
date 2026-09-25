# Original Vocal Pre — Tone mapping gap and isolated study

Date: 2026-09-26

## SOURCE_FACT

Current product code maps Tone after the nonlinear/transformer path using:
- low shelf center: 180 Hz;
- high shelf center: 7 kHz;
- negative Tone: up to +0.75 dB low shelf and -1.25 dB high shelf;
- positive Tone: up to -0.50 dB low shelf and +1.50 dB high shelf.

Existing `OriginalTuningSweep.cpp` uses a helper named `tone()`, but that helper is a generic tone-signal measurement routine. It does **not** sweep the user Tone control.

Existing `OriginalAnalyzer.cpp`:
- exercises Tone +100 only inside a finite-stress safety case;
- includes a `tone_off` ablation while the normal measured control is neutral, so it does not characterize the audible Tone mapping.

Therefore the current CIPI statement “final Tone mapping is not locked” is supported by a concrete measurement gap: the -100..+100 control curve has not been systematically characterized.

## INFERRED

The current shelf values are deliberately subtle, but without a real control sweep there is not enough evidence to determine:
- whether the full range is perceptually useful;
- whether negative and positive endpoints are balanced;
- whether Character changes the apparent shelf response;
- whether post-nonlinear harmonic weighting changes materially at hot input;
- whether the control is too weak to justify UI space.

## ISOLATED STUDY

Research branch:
- `original-tone-study`
- based from product SHA `1f0ad46c9603c9437892e4304b19d29c8676c038`.

Prepared analyzer:
- `7a5cd3f9788bf0ba61df17a68aadd0c798e2ce53`: `Tests/OriginalToneStudy.cpp`;
- `aad2616bf3fa1d24322fe35bb6f31eb5512efb90`: CMake target.

Planned measurements:
- Tone: -100, -50, 0, +50, +100;
- Character: 0, 50, 100;
- small-signal frequencies: 50, 100, 180, 500, 1k, 3k, 7k, 10k, 16k Hz;
- stress checks at 100 Hz / 1 kHz / 10 kHz, -18 and -6 dBFS;
- gain delta relative to Tone 0;
- THD and finite-output status;
- basic direction check for low/high shelving.

Representative tuning is the current balanced 6 dB / flux 8 / nonlinear 0.125 profile with Character level compensation.

## HYPOTHESIS

The existing Tone mapping may prove appropriately subtle for a vocal-first four-control product, but it may also be too weak or asymmetrical once level-matched real vocals are used.

No range extension, reduction, removal, or endpoint change is authorized until measurement and vocal AB evidence exist.

## REJECTED

- Treating the existing helper name `tone()` as evidence that the Tone knob had already been swept.
- Locking Tone from code constants alone.
- Increasing shelf gains just to make the control more obvious before measurement.
- Removing Tone solely because the current mapping is subtle.

## STATUS

Tone study is prepared on an isolated branch. Product branch remains unchanged and Tone remains PROVISIONAL.
