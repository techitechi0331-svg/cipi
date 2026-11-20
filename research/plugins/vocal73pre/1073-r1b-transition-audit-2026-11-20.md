# Vocal73 R1b — falsifiable automation-transition audit (2026-11-20)

Track: `VOCAL73-1073-IDENTIFIABILITY-001`  
Decision: `DEC-VOCAL73-R1B-20261120-TRANSITIONS`  
Authority: CIPI research-only. Product source unchanged; no Neve hardware fidelity assertion.

## Provenance / recheck
- Product `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp` Git blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`, re-fetched this run and unchanged from R1.
- CIPI `research/health/automation-status.json`: track lifecycle `FAILED`, reason `LATEST_EXTERNAL_ACTION_FAILED`, scheduler_eligible=false. Cross-repo external run `44714522345` artifacts API still returned empty list. Previously inspected job log identifies GitHub artifact-storage quota exhaustion, not DSP test failure. Do not dispatch a duplicate job while unresolved.
- Existing contract: `research/plugins/vocal73pre/1073-r1-baseline-measurement-contract-2026-11-20.md`; existing quota/source audit: `1073-r1-upload-quota-and-dsp-source-audit-2026-11-20.md`.

## EVIDENCE-VOCAL73-R1B-TRANSITION-CODE: three new testable hypotheses

**H1: HPF OFF/ON resumes frozen IIR history.** In `process`, `hpfFirst.process` and `hpfSecond.process` execute only when `hpfChoice > 0`. `updateFilters` updates coefficients but does not reset these filter states when HPF is disabled or re-enabled. Thus internal filter delay states may remain from the last ON block and are not advanced by intervening OFF blocks. The audible magnitude and direction of any transient is **UNKNOWN**, not measured.

**H2: COLOR=0 / ANALOG toggle resumes frozen DC blocker state.** `dcBlocker.process` runs only when `analogEnabled && blockColor > 0.00001`; the same `dcBlocker` is not advanced otherwise. Its state can be stale when nonlinear coloration resumes. Analog mode also switches low/high shelf processing abruptly at the block boundary, with no explicit wet/dry crossfade. The gain/color smoothing is separate and does not smooth this boolean. Audible clicks are a **hypothesis**, not a proven failure.

**H3: control smoothing is sampled at block end for nonlinear/filter parameters.** `colorSmoothed.skip(buffer.getNumSamples())` is called once per block, then a single `blockColor` is used to update shelves and for every sample's nonlinear function in the block. Thus COLOR interpolation is *block-rate* for the nonlinear and tone stages, unlike true per-sample smoothing. Block-size dependence is testable for automation; exact differences are **UNKNOWN** until a headless render.

## Analytic control-space invariants (not audio measurements)

From the source's `saturateSample` equation, at zero input the normalized asymmetric shaping has zero output; its derivative at zero equals one for all c in [0,1], so `dy/dx|x=0 = 1 + 0.20*c` when ANALOG enabled. Derived compensation gain, excluding shelves and oversampling:

| COLOR | compensation dB | low shelf nominal dB | high shelf nominal dB |
| ---: | ---: | ---: | ---: |
| 0% | 0.000000 | 0.0 | 0.0 |
| 25% | 0.423786 | +1.0 | -0.6 |
| 50% | 0.827854 | +2.0 | -1.2 |
| 75% | 1.213957 | +3.0 | -1.8 |
| 100% | 1.583625 | +4.0 | -2.4 |

Calculation: `20*log10(1+0.2*c)`, `4*c`, `-2.4*c`. Verified independently using Python 3 `math.log10` on this run. This is an *analytic formula verification*, not JUCE executable validation.

## JOB-VOCAL73-R1B-TRANSITIONS-001 (READY, independent of MELON artifacts)

Build a source-accurate, isolated headless fixture using JUCE 9.0.2 and the unchanged v0.2 DSP. At 48 kHz, mono, block sizes 32/256/2048, run the following **paired tests** with the same sample sequence and initial reset:
1. HPF state: 1 kHz -18 dBFS sine for 2 s with HPF 300 Hz ON; 1 s OFF; switch ON again. Compare against a control run that advances equivalent IIR state through the OFF interval in a test-only fork. Report max absolute difference over the first 20 ms and click metric `abs(y[n]-y[n-1])` versus no-toggle control.
2. DC state: 100 Hz and 1 kHz -18 dBFS tones, COLOR 100%, ANALOG ON for 2 s, then OFF for 1 s, then ON; compare against an explicitly reset DC state in a fixture-only fork. Do not claim a true hardware artifact.
3. Automation granularity: ramp COLOR 0→100% over 0.5 s in blocks 32/256/2048; compare RMS/THD/FFT residual of matched sections and record exact automation event timing. Keep input/output gain and HPF constant.
4. Boolean switching: step ANALOG ON↔OFF at nonzero signal; compare direct switching versus an isolated test-only 5 ms crossfade, accounting for filter latency and loudness.
5. Allocation: instrument allocations only around `process`, not `prepare`, then vary COLOR by >0.0005 and HPF choices; record call stacks, count and max real-time cost. Source-based risk alone is not proof.

Acceptance: capture fixture SHA, compiler, JUCE SHA, exact parameter event sample indices, WAV input/output SHA256, measured numeric metrics, CPU and NaN/Inf assertions. No fabricated pass/fail. If test-only alternative wins, propose a product change behind explicit approval; do not modify production v0.2 automatically.

## DECISION / blocked gates / next step

- **Decision:** prioritize real-time state-continuity, boolean toggle, and block-rate automation falsification *before* attempting more complex 1073 transformer models; these tests can reject known DSP weaknesses without an original 1073.
- **BLOCKED_EXTERNAL:** R1 MELON artifact intake failed at GitHub artifact quota. Keep dependent action failed; check capacity before existing bounded retry, avoid deletion of provenance and duplicate dispatch.
- **HUMAN_GATE:** licensed/calibrated original-unit measurement, listening, Cubase 14 validation, pluginval final gate, product adoption/release.
- **Next READY:** implement and execute headless fixture (or independent source-licence ledger if runner unavailable), attach hashed results to CIPI, and only then decide whether smoothing/state reset or crossfade is justified.
