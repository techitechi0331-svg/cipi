# Vocal Surface — Harmonic / Formant Safety R1

Date: 2026-09-26
Track: `VOCAL_SURFACE_FORMAL`
Knowledge status: **PROVISIONAL / RESEARCH**
Product main preserved at: `b89a1de4cd856b02ca9e0716b6775c576421d99d`

## Objective

Test the unresolved risk recorded in the v0.3 handoff: the Smooth spectral-prominence stage may reduce legitimate voiced harmonics/formant transitions together with genuinely unwanted narrow high-frequency prominence.

This experiment does **not** promote a new product calibration and does not modify product `main`.

## SOURCE_FACT

- Product repo: `techitechi0331-svg/VocalSurfaceProcessor`
- Product main at investigation start: `b89a1de4cd856b02ca9e0716b6775c576421d99d`
- Baseline research branch: `surface-harmonic-safety-r1`
- Baseline transition-sensitive probe SHA: `4103108313a623ac8f21cb40ffd6eefa7c7355fb`
- Candidate-A branch: `surface-harmonic-safety-candidate-a`
- Candidate-A initial implementation SHA: `fe055ec2292a0f8debc9cfcaac94c758ec51d8a1`\n- Candidate-A current head SHA: `ae411ded6a237ee15ccad6b6b17c58e6b5ad7a0e`
- Baseline Draft PR: `VocalSurfaceProcessor#2`
- The diagnostic probe compares:
  - a voiced 200 Hz harmonic source whose 3.2 kHz formant region strengthens over a 30 ms transition; and
  - the same base voiced source with a new 3.275 kHz inharmonic narrow prominence.
- Probe measurement uses Smooth only at nominal 50%; Clean, Density and Air are zero, Auto Gain is disabled.
- Candidate A estimates low-band periodicity from a separate low-passed mono history and applies partial protection only to the harshness term near estimated harmonic multiples.
- Candidate A leaves the independent sibilance-reduction term unchanged.
- Candidate A currently caps harmonic protection at 55%; this is a research constant, not a locked product value.\n- Candidate A current head selects the slowly dominant stereo input channel for pitch evidence, avoiding L+R cancellation on strongly anti-correlated material.
- Candidate A current probe also runs a deliberately anti-phase stereo variant and records `stereo_phase_delta_db`; the provisional diagnostic guard is < 0.20 dB.

## MEASURED

No new DSP measurement is promoted from this R1 experiment yet.

GitHub Actions infrastructure state is directly observed:

- baseline run `36248453725`: failed before any workflow step began; `runner_id=0`, no runner name, empty step list;
- candidate-A run `36248820776`: same pre-step failure state;\n- candidate-A stereo-robust revision run `36249146288`: same pre-step failure state;
- candidate-A anti-phase regression revision run `36249229137`: same pre-step failure state;
- an earlier retry of baseline run `36248280882` also failed with no assigned runner;
- historical product-main run `36051783935` on 2026-09-24 completed successfully on `windows-2022` and ran the DSP reference suite, VST3 build, pluginval strictness 10 and Steinberg validator.

Therefore the current R1 CI failures are **not evidence that the new C++ fails to compile or that the DSP tests fail**. They are an external runner-allocation block.

## INFERRED

- The existing v0.3 detector is intentionally transient-sensitive: a slow spectral baseline is combined with a local spectral reference, so a fast vowel/formant transition is a more relevant stress case than a stationary vowel.
- A static steady-state tone/formant test is insufficient as the primary false-positive probe because it does not represent the transition condition this detector is designed to react to.
- Harmonic-aware protection should be applied only to the harshness/prominence term, not globally to the full spectral gain curve, so that independent sibilance control remains available.
- Low-pass conditioning before periodicity estimation reduces the chance that a newly appearing high-frequency narrow tone becomes the pitch reference itself.

## HYPOTHESIS

Candidate A may improve discrimination between legitimate voiced harmonic structure and inharmonic narrow prominence without materially weakening the existing nominal-50 harshness/sibilance behavior.

Candidate A is **not adopted** until all of the following are observed on the actual C++ implementation:

1. baseline transition probe completes and establishes current discrimination;
2. candidate probe completes on the same deterministic signal;
3. existing bypass, macro-sweep, sample-rate and Air consistency tests remain passing;
4. pluginval strictness 10 and Steinberg validator remain passing;
5. representative real-vocal level-matched listening confirms less dulling / fewer false positives without restoring painful harshness;
6. the numerical protection limit and confidence thresholds are calibrated from evidence rather than left as prototype values.

## REJECTED / NOT SELECTED

- **Stationary-only harmonic probe as the main R1 gate:** insufficiently targeted for a detector with a slow adaptive baseline; retained conceptually only as a stability case.
- **Broad-formant-width protection without periodicity evidence:** not selected because spectral width alone cannot reliably distinguish a desirable formant from a broad undesirable resonance/noise feature.
- **Disabling spectral reduction at harmonic frequencies:** rejected. Candidate A is deliberately partial; legitimate harmonics can themselves be harsh and may still need reduction.
- **Applying harmonic protection to sibilance reduction:** rejected for Candidate A. Sibilance safety remains independent.

## BLOCKED_EXTERNAL

Current GitHub-hosted Windows jobs are failing before runner assignment (`runner_id=0`, zero steps). This blocks new compiled/reference-test evidence but does not block source review, test design, research logging or real-vocal test preparation.

Resume condition: a Windows GitHub-hosted runner is assigned again, or an explicitly configured compatible Windows runner is made available to this product repo.

## Next executable work

When CI execution is available:

1. rerun baseline SHA `4103108313...` and capture the `spectral_discrimination_probe` line;
2. rerun candidate current head SHA `ae411ded6a2...`;
3. compare harmonic attenuation, inharmonic attenuation and discrimination delta;
4. use the baseline/candidate pair to set a numerical acceptance gate;
5. only then tune the 55% cap, pitch-confidence thresholds or harmonic tolerance if required;
6. proceed to real-vocal level-matched AB/ABX and Cubase Pro 14 PDC validation before any product-main promotion.

## Promotion status

**NOT READY FOR PRODUCT MAIN.**

The v0.3 product main remains the verified reference. Candidate A is a reversible research prototype only.
