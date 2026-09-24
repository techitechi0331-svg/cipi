# CIPI Plug-in Registry

| Plug-in | Stage | Core hypothesis | Evidence state | Next gate |
|---|---|---|---|---|
| VoxLevel 0.1 | measurement | dual-timescale detection can control vocal body while preserving peaks better than one envelope | core compressor E5; mapping PROVISIONAL | static/dynamic measurement + pluginval/validator |
| AirGuard 0.1 | measurement | normalized high-band/full-band energy ratio reduces level dependence of de-essing | spectral principle E4/E5; constants PROVISIONAL | detector/corpus measurement + pluginval/validator |
| Density 0.1 | measurement/revision | latency-aligned oversampled nonlinear parallel path can raise perceived density without obvious clipping | anti-alias foundation E5; mapping PROVISIONAL | alias/THD/IMD/level-match + pluginval/validator |
| PeakBody 0.1 | implementation/test | short-term crest factor can adapt vocal compressor timing to peak/body character | adaptive-compression literature E5; vocal constants HYPOTHESIS | branch VST3 build -> main full gates -> dynamic measurement |
| ResonancePilot 0.1 | research | harmonic-aware local prominence can suppress bad narrow resonances while preserving legitimate vocal structure | vocal/formant constraints E5; detector HYPOTHESIS | detector-model review + synthetic false-positive experiments |
| MicroDouble 0.1 | research | protected center + bounded decorrelated side voices can widen vocals with less mono damage than equal-level Haas copies | decorrelation literature E4/E5; vocal mapping HYPOTHESIS | topology review + mono/correlation simulations |
| BreathKeeper 0.1 | research | breath-event detection can reduce excessive breaths while protecting voiced breathy phonation | singing breath-event evidence E4/E5; detector mapping HYPOTHESIS | feature review + labelled-corpus protocol |
| VocalForward 0.1 | research | time-frequency masking-aware action can restore vocal audibility only when needed | masking-aware EQ evidence E4/E5; vocal topology HYPOTHESIS | masking-model review + routing design |

## Promotion rule

A plug-in is not marked **candidate** until it:

- builds as VST3;
- has repeatable measurements;
- passes numerical/stability checks;
- has a documented level-matched listening plan;
- has no known realtime-safety blocker;
- records remaining hypotheses explicitly.

A plug-in is not marked **release** until Cubase Pro 14 real-host validation is complete.
