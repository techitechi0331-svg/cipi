# CIPI Plug-in Registry

| Plug-in | Stage | Core hypothesis | Evidence state | Next gate |
|---|---|---|---|---|
| VoxLevel 0.1 | implementation | dual-timescale detection can control vocal body while preserving peaks better than one envelope | core compressor E5; mapping E2 | build + static/dynamic measurement |
| AirGuard 0.1 | implementation | normalized high-band/full-band energy ratio reduces level dependence of de-essing | spectral principle E4/E5; constants E2 | build + crossover/null + corpus false-trigger test |
| Density 0.1 | implementation | moderate oversampled nonlinear parallel path can raise perceived density without obvious clipping | anti-alias foundation E5; mapping E2 | build + latency/alias/THD/level-match test |
| ResonancePilot | research queue | adaptive narrow-band suppression can distinguish stable vocal resonances from musical brightness | E1/E2 | literature + detector prototype |
| PeakBody | research queue | separate peak/body features can automate dynamics timing | DRC automation literature E5; product mapping E2 | derive features + offline experiment |
| BreathKeeper | research queue | temporal/spectral classification can avoid flattening expressive breath | E1 | corpus + features |
| VocalForward | research queue | masking-aware dynamic presence can improve intelligibility with less harshness than fixed EQ | E1/E2 | psychoacoustic research |
| MicroDouble | research queue | bounded time/pitch decorrelation can create width while constraining mono loss | E2 | spatial research + correlation tests |

## Promotion rule

A plug-in is not marked **candidate** until it:

- builds as VST3;
- has repeatable measurements;
- passes numerical/stability checks;
- has a documented level-matched listening plan;
- has no known realtime-safety blocker;
- records remaining hypotheses explicitly.

A plug-in is not marked **release** until Cubase Pro 14 real-host validation is complete.
