# VoPriPro AMOUNT Static Mapping Audit v1

Date: 2026-09-27
Scope: deterministic source-level audit only
Product mutation: none
Baseline: `techitechi0331-svg/VocalPrepComp@cc796d30d7e1885e0ca66caaf7f1b02d0bffeb33`

## Purpose

Audit the current VoPriPro AMOUNT mapping without changing the protected production baseline.

This study is intentionally narrower than listening or real-vocal validation. It asks what the existing piecewise AMOUNT map mathematically does to ratio, calibration gain reduction, maximum gain reduction, threshold placement and the 12 dB soft-knee operating region.

It does **not** decide that the current mapping is perceptually optimal or that it should be changed.

## SOURCE_FACT

The protected source maps AMOUNT as follows:

| Amount | Ratio | Calibration GR | Max GR |
|---:|---:|---:|---:|
| 0% | 1.0:1 | 0.0 dB | 0.0 dB |
| 10% | 1.2:1 | 0.5 dB | 1.0 dB |
| 25% | 1.5:1 | 1.2 dB | 2.5 dB |
| 40% | 2.1:1 | 2.2 dB | 4.5 dB |
| 50% | 2.7:1 | 3.0 dB | 6.0 dB |
| 60% | 3.1:1 | 3.7 dB | 7.0 dB |
| 75% | 3.6:1 | 4.7 dB | 8.5 dB |
| 90% | 4.2:1 | 5.7 dB | 9.5 dB |
| 100% | 4.5:1 | 6.0 dB | 10.0 dB |

Between anchors, all three values are linearly interpolated.

The static compressor curve uses:
- knee width: 12 dB;
- threshold solved so that the current Active Level produces the mapped Calibration GR;
- final static DesiredGR capped by mapped Max GR.

The formal Natural50 reference therefore remains:
- Ratio 2.7:1;
- Calibration GR 3.0 dB;
- Max GR 6.0 dB.

## DERIVED_MEASURED

The exact source equations were evaluated at every published AMOUNT anchor with Active Level defined as 0 dB relative reference.

### Threshold location relative to Active Level

| Amount | Threshold relative to Active Level |
|---:|---:|
| 10% | -2.485 dB |
| 25% | -3.295 dB |
| 40% | -4.040 dB |
| 50% | -4.694 dB |
| 60% | -5.449 dB |
| 75% | -6.508 dB |
| 90% | -7.481 dB |
| 100% | -7.714 dB |

Because the knee is 12 dB wide, the lower edge of the soft-knee region moves from about -8.485 dB relative to Active Level at Amount 10% to about -13.714 dB at Amount 100%.

### DesiredGR at representative detector excursions

| Amount | -6 dB | Active Level | +3 dB | +6 dB |
|---:|---:|---:|---:|---:|
| 10% | 0.043 | 0.500 | 0.916 | 1.000 |
| 25% | 0.151 | 1.200 | 2.098 | 2.500 |
| 40% | 0.356 | 2.200 | 3.688 | 4.500 |
| 50% | 0.578 | 3.000 | 4.844 | 6.000 |
| 60% | 0.838 | 3.700 | 5.724 | 7.000 |
| 75% | 1.274 | 4.700 | 6.867 | 8.500 |
| 90% | 1.777 | 5.700 | 7.986 | 9.500 |
| 100% | 1.929 | 6.000 | 8.333 | 10.000 |

Values are dB of static DesiredGR before attack/release smoothing.

At +6 dB above Active Level, every nonzero published anchor reaches its mapped Max GR ceiling.

Approximate excursion above Active Level where the static Max GR ceiling is first reached:

| Amount | Ceiling onset |
|---:|---:|
| 10% | +3.515 dB |
| 25% | +4.205 dB |
| 40% | +4.551 dB |
| 50% | +4.836 dB |
| 60% | +4.885 dB |
| 75% | +5.262 dB |
| 90% | +4.988 dB |
| 100% | +5.143 dB |

## Interpretation

1. **Natural50 is internally coherent.** The current threshold solver produces the intended 3.0 dB static GR at Active Level, with 6.0 dB Max GR reached at roughly +4.84 dB above that reference.

2. **AMOUNT is deliberately multi-dimensional, not a simple linear GR scaler.** Moving the knob changes ratio, operating threshold through Calibration GR, and Max GR together.

3. **The high-AMOUNT region is not perceptually proven uniform.** Calibration GR rises from 5.7 to 6.0 dB between 90% and 100%, while ratio rises 4.2:1 to 4.5:1 and Max GR rises 9.5 to 10.0 dB. The top 10% therefore changes shape/ceiling more than reference-level GR.

4. **Higher AMOUNT extends compression farther below Active Level.** This follows directly from the threshold shift plus the fixed 12 dB knee. It is not by itself a defect, but it is a meaningful perceptual variable that a one-dimensional AMOUNT control hides.

5. **The existing mapping is mathematically continuous and monotonic at the source anchors.** This audit found no static discontinuity requiring an immediate product fix.

## Decision

**KEEP BASELINE / OPEN PERCEPTUAL UNIFORMITY QUESTION.**

No AMOUNT value is changed.

The current map remains the protected production baseline because:
- existing source regression already protects continuity/monotonicity;
- this static audit found no mathematical fault;
- static equations cannot determine whether control travel feels perceptually even on singing.

## Next independent research

The next useful AMOUNT-specific study should compare the current map on the same real-vocal material at a minimum of:
- 10%;
- 25%;
- 40%;
- 50%;
- 60%;
- 75%;
- 90%;
- 100%.

Required derived metrics should include:
- active-window mean / p95 GR;
- fraction of active samples at Max GR;
- short-window dynamic-range reduction;
- GR ripple;
- phrase-tail recovery;
- output level after gain matching.

The listening gate should then ask whether adjacent AMOUNT regions produce useful, ordered and non-abrupt perceptual steps. No alternative mapping should be tuned against the final listening holdout.

## Precision boundary

This is a deterministic static-map audit, not a real-time render, listening result, VST3 result, Cubase result or product-adoption decision.
