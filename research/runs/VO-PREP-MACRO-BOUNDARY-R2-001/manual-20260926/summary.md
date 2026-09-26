# Vo.Prep Macro Boundary R2 — isolated short-term shape diagnostic

Decision: **PASS for the R2 diagnostic scope.**

R2 does not overwrite R1. R1 remains a failed final-proof gate because absolute 50 ms/10 ms level metrics and Macro p95 movement exceeded the original limits.

## R2 result

- Median change in 10 ms crest p95: **0.00171 dB**.
- Worst-file change in 10 ms crest p95: **0.00349 dB**.
- Maximum across files of 10 ms gain-excursion p99: **0.01497 dB**.
- 50 ms gain-excursion p99: **0.07497 dB**.
- 100 ms gain-excursion p99: **0.14997 dB**.
- Maximum cut-rate p99: **1.50354 dB/s**.
- Maximum boost-rate p99: **0.60194 dB/s**.
- Median occupancy near the -2 dB cut ceiling: **0.354%**.
- Worst-file occupancy near the -2 dB cut ceiling: **5.255%**.
- All values finite.

All predeclared R2 gates passed.

## Interpretation

The current Macro stage behaves as a slow scalar phrase-level gain process, not as a 10–100 ms compressor-like transient flattener. This explains why R1 absolute short-window level metrics can move even though within-window crest shape is essentially preserved.

Combined with R1's downstream VoPriPro evidence (median mean-GR change 0.023 dB; worst mean-GR retention 99.33%), the current evidence supports retaining Macro as a Vo.Prep boundary candidate without retuning it yet.

Final product lock still requires integrated level-matched listening and later target-host QA.
