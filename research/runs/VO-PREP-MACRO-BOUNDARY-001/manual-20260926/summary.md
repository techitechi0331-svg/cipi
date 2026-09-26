# Vo.Prep Macro Boundary R1 — private-corpus derived evidence

Decision: **REVISE / R1 boundary proof did not pass every predeclared gate.**

## Strong positive evidence

- Median 2 s phrase-spread reduction: **0.3953 dB**.
- Median 1 s phrase-spread reduction: **0.2595 dB**.
- 9/11 files did not worsen at 2 s beyond the predeclared 0.05 dB tolerance.
- Macro ON changed downstream VoPriPro mean GR by only **0.0230 dB median**.
- Macro ON changed downstream VoPriPro p95 GR by only **0.0115 dB median**.
- Worst downstream mean-GR retention F/E was **0.9933**, so VoPriPro did not become idle.
- Combined gain-movement gate passed **11/11**.
- VoPriPro limiter-risk flag was 0 files in D/E/F for this offline boundary replay.

## Triggered R1 gates

- Median absolute 50 ms spread change was **0.3364 dB**, above the predeclared 0.20 dB ceiling.
- Median absolute 10 ms p99 peak change was **0.2940 dB**, above 0.20 dB; worst case was **1.2643 dB**, above 0.60 dB.
- Median Macro p95 absolute gain movement was **1.7760 dB**, above 1.50 dB.

## Interpretation

The core product-overlap counter-hypothesis is strongly disfavored on this corpus: current Macro does not materially replace VoPriPro broadband compression. The R1 failure is instead concentrated in short-window absolute-level and gain-movement gates.

Because a slow broadband gain offset changes absolute 10/50 ms peak or window level even when it does not flatten within-window transient shape, the next experiment must distinguish **slow gain offset** from **short-term shape destruction**. This does not retroactively change or pass R1; R1 remains a failed gate with preserved negative evidence.

## Privacy

Only anonymized derived metrics are stored. No raw vocal audio and no raw filenames are committed.
