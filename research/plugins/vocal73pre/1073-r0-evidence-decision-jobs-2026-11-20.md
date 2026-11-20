# Vocal 73 / original Neve 1073 — R0 evidence, decision, next job
Date: 2026-11-20 (Asia/Tokyo)
Track: VOCAL73-1073-IDENTIFIABILITY-001
Session: initial user-requested CIPI autonomous-research setup + source audit
Status: R0_SOURCE_FACT_INVENTORY_DONE; real-hardware fidelity not evaluated.

## Evidence ledger — authoritative manufacturer claims, not independently measured samples

| ID | Claim | Evidence class | Source & scope | Caveat |
| --- | --- | --- | --- | --- |
| EV-1073-001 | Classic 1073 nominal mic input +20..+80 dB in 5 dB steps, line -10..+20 dB, line input 10k ohm | E5 SOURCE_SPEC | AMS Neve Classic 1073 official page, preamp specification | Current Classic docs follow original design; not a measurement of a 1970s specimen |
| EV-1073-002 | HF shelf fixed 12kHz +/-16 dB, LF 35/60/110/220 Hz +/-16 dB, MF 0.36/0.7/1.6/3.2/4.8/7.2 kHz +/-18 dB | E5 SOURCE_SPEC | AMS Neve Classic 1073 official page, EQ specification | Nominal frequencies and maximum gain not measured full response curves |
| EV-1073-003 | HPF switch 50/80/160/300 Hz nominal 18 dB/oct | E5 SOURCE_SPEC | AMS Neve Classic 1073 official page | v0.2 matches nominal positions/slope, but its generic cascaded filters are not proven identical phase/Q |
| EV-1073-004 | 10468 mic transformer; 31267 line transformer; LO1166 gapped output transformer | E5 SOURCE_DESIGNATION | AMS Neve Classic 1073 and Marinair pages | Exact proprietary winding geometry, loss, hysteresis and parasitics are NOT published in these pages |
| EV-1073-005 | Discrete Class A; stepped gain selects among amplifier gain paths; mic 300/1.2k ohm switch | E5 SOURCE_TOPOLOGY | AMS Neve Classic 1073 official page | Precise transfer function, transistor and switch topology remains to be verified from revisioned primary schematic |
| EV-1073-006 | Official Classic spec reports output >+26 dBu into 600 ohm; distortion <=0.07% at +20 dBu output 50 Hz..10 kHz (80kHz BW); EQ-out response +/-0.5dB 20Hz..20kHz | E5 SOURCE_SPEC | AMS Neve Classic 1073 official page, audio performance | These are manufacturer specification limits, not a device-measured harmonic signature or calibration curve |
| EV-1073-007 | Current product uses fixed COLOR tanh+bias saturator, linked +4dB low shelf at 120 Hz and -2.4dB high shelf around 10.5kHz; nominal 3rd-order Butterworth HPF and 2x oversampling | SOURCE_CODE_OBSERVATION | VocalPrepComp main, Vocal73Pre/Source/Vocal73DSP.cpp and README v0.2 | No physical-reference calibration |
| EV-1073-008 | AMS describes modern transformer components built to original specifications | E5 MANUFACTURER_CLAIM | AMS Neve About Marinair | Original 1970s unit and modern Classic/DPX/SPX still require separate revision/unit labels in all comparisons |

Primary manufacturer sources:
- https://www.ams-neve.com/outboard/1073-range/1073-mic-preamp-equaliser/
- https://www.ams-neve.com/about-marinair/
- https://www.ams-neve.com/outboard/1073-range/1073dpx/
Product source:
- https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/README.md
- https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp

Source usage rights: only short engineering paraphrases and links are included in CIPI. Do not import vendor-controlled images/schematics or duplicate manuals. Older service PDF hosted by third parties may inform *verification queries*, but its provenance, copyright and circuit revision must be resolved before encoding component values as verified historical facts.

## R0 contradiction/fidelity audit
- PASS: v0.2's HPF switch labels, nominal slope correspond to the manufacturer control positions.
- FAIL as FULL_1073_FEATURE_SET: no adjustable HF/MF/LF 1073-style EQ bands or preamp stepped mic/line gain stage; v0.2 COLOR is a custom nonlinear DSP, not documented analog stage emulation.
- UNPROVEN: exact nonlinearity, impedance, transformer loading, hysteresis, phase, noise/hum, EQ filter shapes; physical 1970s hardware comparison.
- These differences are *source/feature observations*, not a claim of measured sound quality; do not convert them to a fidelity percentage.

## Initial Decision (DEC-VOCAL73-R0-20261120)
- Preserve Vocal73Pre v0.2 as immutable comparison baseline. No product write or VST3 release.
- First executable research is a traceable topology/control-source ledger and a deterministic **v0.2** measurement harness specification, independent of CIPI/MELON's synthetic proxy; never fit proxy output as if it were original hardware.
- Treat precise transformer electrical parameters, BA283 revision, gain switch topology and all 1970s unit-specific curves as unknown until primary source and/or measured reference evidence is obtained.
- Reference Model: ORIGINAL_1970S_1073_VINTAGE_UNIT_UNMEASURED; official modern Classic page is specification evidence only.
- Provisional benchmark: extract current v0.2 responses, then compare nominal EQ/control coverage, frequency/phase, level-dependent harmonics, aliasing and CPU. Real-unit comparison is a separate gated stage.
- Track authority: CIPI; Human Gates preserved (licensed hardware measurements, listening, Cubase, product adoption/release).

## Next CIPI research jobs
1. `JOB-VOCAL73-1073-R1-BASELINE-001` — **READY**: compile source-accurate response/harmonic test matrix for existing Vocal73DSP and identify scriptable headless harness. Required evidence: source SHA, command, sample rates, level, impulse/sine sweep, filters, harmonic and aliasing spectra, FFT parameters, measured output hashes. Do not label source estimates as measured values.
2. `JOB-VOCAL73-1073-R1-SCHEMA-002` — **READY**: map original 1073 revisions/service documentation and source rights for 10468/31267/LO1166, Class A gain paths, inductors, EQ and HPF. Keep undocumented parameters unknown.
3. `JOB-VOCAL73-1073-R2-TRANSFORMER-003` — **DEPENDENCY_BLOCKED** on validated source-bound LTI topology and laboratory measurements. Draft WDF/state-space/SPICE model comparison without inventing transformer constants.
4. `JOB-VOCAL73-1073-R4-REAL-UNIT-004` — **HUMAN_GATE / BLOCKED_EXTERNAL**: identifiable original 1073 unit or properly licensed measured reference plus a calibrated signal chain; cannot be replaced by manufactured estimates.
5. `JOB-VOCAL73-1073-R5-HOST-005` — **HUMAN_GATE**: real Cubase 14/pluginval and listener approval following qualifying candidate.

## Operational notes / restart
- CIPI track YAML: `research/autonomous_bridge/tracks/VOCAL73-1073-IDENTIFIABILITY-001.yaml`; finite budget 3 runs, 24 candidate maximum, no auto product write/auto knowledge promotion.
- CIPI cross_repo registry: `vocal73pre.build` allowlists existing GitHub-hosted `build-vocal73pre.yml`; allowlisting is not proof the workflow has dispatched or passed.
- Automation checks/continues hourly; the first immediate inline run created this report and registration.
- Existing CIPI automation health observed 2026-11-20: cross-repo queued=4, dispatched=0, failed=20; this is a *global snapshot* and not evidence a new 1073 job failed.
- Next resume: re-read this file + CIPI health/track and investigate exact current Actions/READY status; prioritize first unblocked research job rather than redoing R0.
