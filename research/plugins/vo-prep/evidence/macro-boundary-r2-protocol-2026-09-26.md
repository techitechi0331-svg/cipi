# Vo.Prep Macro Boundary R2 — diagnostic protocol

## Purpose

R1 is retained as a failed final-proof gate. R2 does **not** relax R1.
R2 asks a narrower diagnostic question: were the R1 short-window failures caused by genuine transient-shape flattening, or by the intended slow scalar Macro gain changing absolute short-window level?

## Frozen DSP

- Vo.Prep main: 28afccdf6d863f1c874ecd086fcb62d5b4f21a82.
- Macro v2.1 remains unchanged: 700 ms short detector, 2.5 s reference, 0.18/0.08 cut/boost ratios, -2/+1.25 dB caps, 1.5/0.6 dB/s slew at 50%.
- Plosive and Sibilance remain at 50%.
- VoPriPro overlap evidence from R1 is retained; R2 does not retune VoPriPro.
- Same 11 anonymized vocals and the same dry-selected 90 s segment starts are reused only as a diagnostic cohort, not as an independent holdout.

## R2 measurements

1. **10 ms crest-shape preservation**: compare per-window crest factor (sample peak dB minus RMS dB) between B and C. Scalar gain cancels from crest.
2. **50 ms and 100 ms slow-gain-compensated spread**: multiply C by the inverse recorded Macro gain curve before measuring short-window level spread versus B. Remaining change reflects Plosive/Sibilance interaction and within-window shape effects rather than the intentional Macro level offset.
3. **Macro slope / ceiling occupancy**: measure gain-rate distribution and fraction of time at or near the -2 dB / +1.25 dB limits.
4. **R1 outliers**: inspect V01, V02 and V05 by anonymous ID only.

## Predeclared R2 gates

- Median absolute change in 10 ms crest-factor p95 across files <= **0.05 dB**.
- Worst-file absolute change in 10 ms crest-factor p95 <= **0.20 dB**.
- Median absolute change in slow-gain-compensated 50 ms spread <= **0.10 dB**.
- Worst-file absolute change in compensated 50 ms spread <= **0.30 dB**.
- Median absolute change in slow-gain-compensated 100 ms spread <= **0.10 dB**.
- Worst-file absolute change in compensated 100 ms spread <= **0.30 dB**.
- Macro gain-rate p99 must remain <= **1.55 dB/s** on the cut side and <= **0.65 dB/s** on the boost side, allowing only small numerical tolerance above the frozen 1.5/0.6 dB/s limits.
- All outputs and derived metrics must remain finite.

## Interpretation rule

- Passing R2 supports the narrower claim that Macro does not flatten short-term transient **shape** even though R1 absolute short-window level gates failed.
- Passing R2 does not erase R1, does not by itself finalize Macro, and does not authorize tuning expansion.
- Failing R2 means current Macro tuning must be revised before final Vo.Prep boundary lock.

## Privacy

Raw audio and raw filenames remain local. Only anonymized derived metrics may enter CIPI.
