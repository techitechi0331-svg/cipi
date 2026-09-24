# CIPI Research Roadmap

## Operating model

Every research track moves through:

`QUESTION -> SOURCES -> CONTRADICTIONS -> MODEL -> NUMBERS -> PROTOTYPE -> MEASUREMENT -> LISTENING -> DECISION`

Possible decisions:

- **PROMOTE** — reusable DSP block / recipe.
- **ITERATE** — measurable promise, unresolved weaknesses.
- **ARCHIVE** — valid knowledge, not currently useful.
- **REJECT** — hypothesis failed or benefit/cost is poor.

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
