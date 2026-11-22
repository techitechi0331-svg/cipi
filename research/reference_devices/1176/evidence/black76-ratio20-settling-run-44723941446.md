# Black76 Ratio20 settling-window sensitivity — observed evidence

**Evidence source:** https://github.com/techitechi0331-svg/76blackCompressor/actions/runs/44723941446  
**Job:** diagnose / 136246517061, **conclusion:** SUCCESS, 2026-11-20 11:00 UTC.  
**CIPI action:** BLACK76-RATIO20-SETTLE-METHOD-20261120-001, COMPLETED.  
**Test code:** `tests/reve_ratio20_settle_sensitivity.cpp`, protocol `BLACK76_RATIO20_SETTLE_SENSITIVITY_V1`.  
**Authority:** `EXTERNAL_WORKFLOW_EVIDENCE_ONLY`; hardware fidelity **NOT** evaluated.

## Controlled settings
- Internal **production DSP**, 20:1 mode, 1-kHz sine; sample rates 176400 and 192000 Hz.
- Controls: input 0.78, output 0.45, attack 0.85, release 0.70.
- Input peak levels: -43, -35, -18 and -6 dBFS.
- Compare 14 ms, 250 ms and 1500 ms preconditioning; common 80-ms RMS window.
- All eight combinations finite; no invalid cases; no physical-Rev E comparator.

## Actual output (dB)
| Fs | Input | gain 14ms | gain 250ms | gain 1500ms | delta 14-to-1500ms |
|---:|---:|---:|---:|---:|---:|
| 176400 | -43 | 7.42659810 | 7.45166920 | 7.45207727 | -0.02547917 |
| 176400 | -35 | 5.33167236 | 5.34939029 | 5.34998652 | -0.01831416 |
| 176400 | -18 | -10.1761360 | -10.1294696 | -10.1295179 | -0.04661810 |
| 176400 | -6 | -20.1651004 | -20.0821172 | -20.0822785 | -0.08282191 |
| 192000 | -43 | 7.42502602 | 7.45165073 | 7.45202149 | -0.02699547 |
| 192000 | -35 | 5.33169364 | 5.34932135 | 5.35001917 | -0.01832553 |
| 192000 | -18 | -10.1760114 | -10.1293653 | -10.1293464 | -0.04666503 |
| 192000 | -6 | -20.1650187 | -20.0820362 | -20.0822045 | -0.08281421 |

- `max_abs_short_to_long_gain_difference_db = 0.0828219091`.
- All 250-ms vs 1500-ms differences have magnitude under 0.00070 dB for this fixed production model and four levels.
- This supports **small settled-window bias at the tested current working point only**; it does **not** prove the old `ratio20_source_sweep` candidate grid's 14-ms/8-ms windows are sufficient: those use different source-loading/gain/bias parameters and a shorter 8-ms integration window.
- A 1500-ms preconditioning period is not mathematically proven equilibrium for all release-history conditions.

## Separate negative research result
The earlier 20:1 source-loading family was rejected in run https://github.com/techitechi0331-svg/76blackCompressor/actions/runs/36296786162: no candidate passed the two production-rate criteria. A successful new settled-window diagnostic must not overwrite this negative evidence.

## Next bounded, non-duplicative experiment (READY)
Use the existing `tests/reve_ratio_control_probe.cpp` *without* modifying production DSP to identify which stage saturates or stops changing at high GR. At 96 kHz and 120-ms settling, print a small log-only control/FET/detector table for 4:1, 12:1 and 20:1 at selected levels. Specifically compare `actual_gr_db`, `fet_attenuation_db`, `gate_mean_v`, `gate_max_v`, `timing_mean_v`, `detected_mean_v`, `finite` and `gate_clamp_fraction_hint`. This distinguishes possible gate saturation, detector control-range limits or insufficient FET attenuation without arbitrary retuning.
- Separate an experimental hypothesis from a confirmed mechanism. Any hypothesis dependent on vintage Rev E parameter identity stays open.
- Use the CIPI Cross-Repo registry and one bounded self-hosted workflow. No artifact upload until GitHub storage quota is resolved; capture numerical results from job log and optionally GitHub job summary.
- No automatic retry of scientific/DSP failure. Preserve CIPI No-Wait, budget, Human Gate and MELON evidence boundaries.
