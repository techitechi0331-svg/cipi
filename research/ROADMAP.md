# CIPI Research Roadmap

## Operating model

Every research track moves through:

`QUESTION -> SOURCES -> CONTRADICTIONS -> MODEL -> NUMBERS -> PROTOTYPE -> MEASUREMENT -> LISTENING -> DECISION`

Possible decisions:

- **PROMOTE** — reusable DSP block / recipe.
- **ITERATE** — measurable promise, unresolved weaknesses.
- **ARCHIVE** — valid knowledge, not currently useful.
- **REJECT** — hypothesis failed or benefit/cost is poor. Rejection archives evidence; it never deletes the run or reusable findings.

## Decision history

Decision history is event-sourced under `research/decisions/<job-id>/`.

- automation may create only pending ITERATE or REJECT proposals;
- final PROMOTE / ARCHIVE / REJECT decisions require review authority;
- rejection must retain negative evidence, reusable findings and explicit revisit conditions;
- prior decision events are immutable; later reviews supersede them by adding a new record;
- lineage fields connect superseded approaches, related jobs and related decisions.

## Priority A — foundations

1. Dynamic-range control
   - peak / RMS / energy / log-domain detection
   - feed-forward vs feedback
   - soft knees and gain computers
   - program-dependent timing
   - transient/body features
   - adaptive parameter mapping
2. Filter design
   - biquads / TPT / SVF
   - Linkwitz-Riley crossovers
   - minimum-phase vs linear-phase
   - dynamic filter coefficient interpolation
3. Nonlinear audio
   - waveshaping families
   - harmonic/intermodulation measurement
   - oversampling
   - ADAA
   - level calibration
4. Measurement
   - static transfer
   - step/burst response
   - frequency/phase/group delay
   - THD/IMD/alias energy
   - loudness / true peak
   - CPU / latency / denormal / NaN tests
5. Realtime implementation
   - allocation-free audio path
   - smoothing
   - automation
   - state recall
   - mono/stereo/sample-rate/block-size robustness

## Priority B — vocal intelligence

- sibilance and fricative detection;
- resonance / harshness detection;
- breath / plosive discrimination;
- pitch/formant-aware analysis;
- transient vs sustained vocal energy;
- adaptive leveling;
- vocal density;
- masking-aware presence;
- language/singer variability.

## Priority C — reference topologies

Study mechanisms rather than copying code:

- FET compression;
- optical leveling;
- VCA compression;
- variable-mu behaviour;
- tube / transformer / transistor nonlinearities;
- tape-like hysteresis/memory;
- classic de-essing;
- doubler / micro-pitch / decorrelation.

## Current experimental plug-ins

1. **VoxLevel 0.1** — dual-timescale vocal dynamics.
2. **AirGuard 0.1** — normalized split-band sibilance control.
3. **Density 0.1** — oversampled parallel nonlinear density.

## Next prototype queue

- **ResonancePilot** — vocal-only dynamic resonance suppression.
- **PeakBody** — transient/body-separated compressor.
- **BreathKeeper** — preserve intentional breath while controlling hiss-like excess.
- **VocalForward** — masking-aware presence without simple static high-mid boost.
- **MicroDouble** — mono-safe vocal doubler with controlled decorrelation.

Names are provisional. Each item must earn implementation through a research hypothesis and measurable target.

## Cross-track knowledge promotion discipline

Current synthesis:
`research/reports/cross-track-knowledge-review-2026-09-25.md`

CIPI separates **product evidence strength** from **knowledge generality**.

A result may be strongly MEASURED for one product and still remain product-scoped.

Before a broad reusable principle is promoted:
- require materially independent cross-track support, or authoritative mechanism evidence plus measured implementation support;
- do not count same-code/same-dataset reruns as independent confirmation;
- transfer mechanisms, metrics and failure boundaries before transferring numeric constants;
- keep exact thresholds, timings, knob positions, candidate counts and reference-level mappings product-scoped until independently reproduced;
- retain negative evidence as a boundary on the generalized claim;
- never use shared-knowledge promotion to close product listening, Cubase or release gates.

Cross-track synthesis itself is review evidence, not a new measurement. Shared candidates should therefore remain below CONFIRMED until their stated scope is independently challenged and survives contradiction review.

