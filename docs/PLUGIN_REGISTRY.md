# CIPI Plug-in Registry

| Plug-in | Stage | Core hypothesis | Evidence state | Next gate |
|---|---|---|---|---|
| VoxLevel 0.1 | measurement | dual-timescale detection can control vocal body while preserving peaks better than one envelope | core compressor E5; mapping PROVISIONAL | static/dynamic measurement + pluginval/validator |
| AirGuard 0.1 | measurement | normalized high-band/full-band energy ratio reduces level dependence of de-essing | spectral principle E4/E5; constants PROVISIONAL | detector/corpus measurement + pluginval/validator |
| Density 0.1 | measurement/revision | latency-aligned oversampled nonlinear parallel path can raise perceived density without obvious clipping | anti-alias foundation E5; mapping PROVISIONAL | alias/THD/IMD/level-match + pluginval/validator |
| PeakBody 0.1 | revision/test | 80 ms crest analysis can preserve short vocal transients while tightening sustained body with split-direction adaptive timing | adaptive-compression literature E5; Revision 02 MEASURED/HYPOTHESIS | autonomous Revision 02 replay -> dedicated product-repo handoff -> product VST3 gates -> level-matched AB |
| ResonancePilot 0.1 | research | harmonic-aware local prominence can suppress bad narrow resonances while preserving legitimate vocal structure | vocal/formant constraints E5; detector HYPOTHESIS | detector-model review + synthetic false-positive experiments |
| MicroDouble / Vocal One-Knob Doubler | revision / audio AB | protected center + two bounded micro-pitch/time voices can provide natural vocal width while preserving the lead anchor | v0.2/v0.3 product measurements imported; calibration/detector PROVISIONAL; exact-mono Side topology remains HYPOTHESIS | autonomous product-snapshot gate -> target Cubase v0.3 AB/host verification -> final review |
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
