# Vocal73 R33 — EQ deadband versus COLOR processing gate (2026-11-22)

## Evidence
Product source (read only): https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp
CIPI main health, track YAML, plan v2, latest R32 commit f29fc9726155204b9f7e2f05e1432080621a3ba8 and successful Research Gate run 44954388886 checked. No R31/R32 duplicate.

Source-derived: updateFilters() refreshes shelf coefficients if abs(blockColor-lastFilterColor)>0.0005f OR analogEnabled changes; saturation and DC stage instead execute when analogEnabled && blockColor>0.00001f. COLOR is 30 ms smoothed, evaluated at block end using skip(nSamples). Thus nonlinear/DC can process the new blockColor while shelf coefficients retain a previous value.

| previous COLOR | block COLOR | analog change | shelf update | saturation/DC |
|---:|---:|---|---|---|
| 0.4500 | 0.4504 | no | no | on |
| 0.4500 | 0.4506 | no | yes | on |
| 0.4500 | 0.4504 | off->on | yes | on |
| 0.0000 | 0.00002 | no | no | on |
| 0.4500 | 0.4500 | on->off | yes | off |

These are source predicate examples, not JUCE execution. Float32 boundary comparisons need bit-level logging. The nominal shelf-target gain difference while within the 0.0005 COLOR deadband is at most 4*0.0005=0.0020 dB (low) and 2.4*0.0005=0.0012 dB (high), assuming lastFilterColor matches the last coefficient target. NOT a measured frequency-response or perceptual bound. Subthreshold changes accumulate against lastFilterColor until the threshold is crossed.

## Decision
ACCEPT new test control distinguishing 0.0005 EQ coefficient refresh from R32's 0.00001 saturation/DC gate. No measured hardware fidelity, audio, JUCE run, or product improvement claimed. Vocal73Pre v0.2 unchanged; MELON not promoted.

## Job / continuation
READY independent CIPI research: isolated JUCE 9.0.2 fixture logs requested COLOR, float32 blockColor bits, lastFilterColor, analog flags, toneChanged, EQ coefficients before/after, saturation/DC gate; 48/96 kHz, 32/256/2048 samples, same absolute parameter timeline across block partitions. Record JUCE/compiler SHA, stimulus SHA256, exact sample positions and any failing indices. Falsify source oracle if coefficient arrays change with toneChanged=false, or do not change with toneChanged=true in a nondegenerate case.
BLOCKED dependent: external VOCAL73 track FAILED / LATEST_EXTERNAL_ACTION_FAILED; no unapproved retry/dispatch under No-Wait, Cross-Repo, MELON Bridge Contract or Global DAG.
HUMAN GATE: original 1073 licensed hardware A/B, listening, Cubase 14, final pluginval, adoption/release.
