# VOCAL73-1073 R1 — 2026-11-20 executable source-equation evidence and decision

Track: VOCAL73-1073-IDENTIFIABILITY-001. Product: VocalPrepComp/Vocal73Pre v0.2; product code unchanged.
Source SHA: 691ceb53d773a8d23ed782a33c1c5ca47b29859c.
Job: JOB-VOCAL73-1073-R1-SOURCE-EQUATIONS-003.
Evidence: EVID-VOCAL73-R1-SOURCE-EQUATIONS-003 (E1 mathematical/source-equation check only).
Decision: DEC-VOCAL73-R1-SOURCE-EQUATIONS-003 = KEEP_BASELINE; HEADLESS_JUCE_NEXT.

## Reproducible experiment
Added Python unittest:
`research/plugins/vocal73pre/tests/test_vocal73_r1_source_equations.py`.
Command: `python research/plugins/vocal73pre/tests/test_vocal73_r1_source_equations.py`.
Locally tested a functionally equivalent Python source-equation fixture (4 tests passed, 0 failures). GitHub file is independently readable; CI/Windows execution of the committed version is **NOT VERIFIED**.

Cases: (1) COLOR zero nonlinear bypass; (2) central-difference small-signal derivative of source tanh/bias equation at c=0.1/0.5/1.0, epsilon 1e-6, tolerance 2e-9; (3) gain compensation in dB at c=0.5 and c=1.0; (4) 48kHz, 30ms smoothing, start COLOR 0.45 to target 1.0, block lengths 32/256/2048.

Source-derived expected results:
- 50%: 20log10(1.1) = 0.827853703 dB; 100%: 20log10(1.2) = 1.583624921 dB, before shelf filtering.
- For linear skip approximation with ramp 1440 samples and initial 0.45, first-block COLOR values at N=32,256,2048: 0.4622222222, 0.5477777778, 1.0. This is a block-application effect, **not** proof of an audible defect. Confirm exact JUCE 9.0.2 SmoothedValue semantics with compiled fixture.
- The unit tests do not execute JUCE DSP, oversampling, filters, state switching, audio thread allocation or real hardware. They do not measure THD, phase, CPU, audio quality or original Neve fidelity.

## Health and BLOCKED
CIPI health latest: track FAILED / LATEST_EXTERNAL_ACTION_FAILED, scheduler_eligible false; runner_wait 0. MELON run https://github.com/techitechi0331-svg/melon/actions/runs/44714522345 had successful computation/export but failed artifact upload due to GitHub Actions artifact storage quota. Its artifact list still empty when checked in this run. This **only** blocks dependent MELON result ingestion, not independent CIPI test research. No unbounded retry, no paid storage, no evidence deletion.

## Next jobs and gates
- READY: JOB-VOCAL73-1073-R1-BASELINE-001 — compile actual JUCE 9.0.2 headless fixture; test sample-rate/block invariance, HPF/ANALOG switching, real-time allocations, finite outputs, and output SHA256, with source and toolchain SHA.
- READY: JOB-VOCAL73-1073-R1-SCHEMA-002 — primary-source vintage-vs-reissue revision/rights ledger and uncertain transformer parameters.
- BLOCKED_EXTERNAL: R1 MELON artifact intake until storage quota resolved, within existing dedup/retry budget.
- HUMAN_GATE: licensed original 1073 reference measurements, level-matched listening, Cubase Pro 14, pluginval final acceptance, product adoption/release.
- Do not promote proxy/source-equation results to measured Neve 1073 equivalence.
