# R30 — DC blocker control model / identifiability guard (2026-11-22)

## Scope and provenance
CIPI-only analytical evidence; Vocal73Pre v0.2 unchanged. Reviewed current CIPI automation-status, 1073 track YAML and research plan v2. Prior R25–R29 covered 1st/2nd-order mismatch, rate normalization, bypass state and measurement plan. This R30 does **not** repeat a JUCE measurement and does not assert the JUCE coefficients are Butterworth.

## Experiment / reproducibility
Purpose: establish a *negative control* for the upcoming JUCE 12 Hz second-order DC-blocker fixture. A standard digital second-order Butterworth HPF is deliberately an independent mathematical comparator, **not** a reverse-engineered Neve circuit or a claimed JUCE implementation.

Python 3, SciPy signal.butter(2, 12, fs=fs, btype='highpass', output='sos'); signal.sosfreqz(sos, worN=[6,12,24,100], fs=fs); amplitude=20log10(abs(H)); fs in {48000,96000}. No real audio, no product build, no hardware measurements.

| Frequency Hz | 48kHz gain dB | 96kHz gain dB |
|---:|---:|---:|
| 6 | -12.304492 | -12.304490 |
| 12 | -3.010300 | -3.010300 |
| 24 | -0.263289 | -0.263289 |
| 100 | -0.000900 | -0.000900 |

These are theoretical comparator values only. They cannot be used to label the JUCE IIR topology, the Neve 1073 HPF, or the actual product's transfer function.

## Decision
- **DO NOT** accept the synthetic comparator as JUCE or hardware truth.
- Require fixture to dump actual JUCE 9.0.2 coefficients, effective sample rate, and processing order; test actual magnitude/phase and bypass-state transition before any state-management recommendation.
- Separate 12 Hz *DC blocker* from user-selectable 50/80/160/300 Hz *HPF*. No extrapolation between them.
- No product write, no MELON dispatch while external track FAILED, no change to global DAG/budget/authority.

## Job / continuation
1. Read current product DSP and JUCE IIR coefficient creation path, identify actual DC blocker design and sample rate.
2. Independent JUCE fixture at 48/96kHz with 32/256/2048 buffers, same absolute sample transition time; record pre-filter samples, actual coefficients, state behavior, max error/RMS/settling time.
3. Compare JUCE results with this *negative control*; explicitly reject mismatched assumptions rather than fitting to synthetic outputs.
4. Keep real original 1073 unit A/B, listening, Cubase 14, final pluginval, adoption and release at Human Gate.

## Blockers
Current automation-status: VOCAL73-1073-IDENTIFIABILITY-001 FAILED (LATEST_EXTERNAL_ACTION_FAILED), scheduler ineligible. No verified licensed original 1073 unit measurement, JUCE fixture output, Windows host measurement or Cubase result. This independent analytical evidence does not unblock those gates.
