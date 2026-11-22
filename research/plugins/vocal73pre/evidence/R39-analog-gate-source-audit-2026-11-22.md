# R39 — source-level ANALOG gate audit and synthetic test rerun (2026-11-22 JST)

## Provenance / boundaries
CIPI main before this run: `03a819b601676617b824140f82d91824dbb20843` (R38). Read CIPI automation-status, VOCAL73 track YAML, plan v2, latest commits and Research Gate. Latest Research Gate run 44983103458: success for R38, not an external 1073 hardware/JUCE validation. External track remains FAILED (LATEST_EXTERNAL_ACTION_FAILED), scheduler_eligible=false. Product source VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c` (unchanged v0.2).

## New source-level finding (not a signal measurement)
Read product DSP lines covering process(). `if (analogEnabled)` encloses both `highShelfTone.process(context)` and the inner `if (blockColor > 0.00001f) dcBlocker.process(context)`. Thus DC blocker is *not* run when ANALOG is off, even when COLOR is above threshold. The oversampler, however, is always processed up/down, intentionally keeping on/off time alignment; the nonlinear sample loop requires BOTH analogEnabled and blockColor > threshold. This corrects any overly broad interpretation of the COLOR-only gate in earlier synthetic descriptions.

| ANALOG | blockColor | nonlinear loop | high shelf | DC blocker | oversampler |
|---|---:|---|---|---|---|
| off | 0.45 | skipped | skipped | skipped | up/down |
| on | 0 | skipped | processed | skipped | up/down |
| on | 0.000005 | skipped | processed | skipped | up/down |
| on | 0.00002 | processed | processed | processed | up/down |

The table is a control-flow oracle, not a numerical/audio output claim. The EQ updateFilters also runs regardless of ANALOG, but the tone processing is gated. Distinguish source logic from runtime state.

## Reproducibility
Fetched original committed R37 test at `research/plugins/vocal73pre/tests/test_r37_color_gate_oracle.py`, blob `8a7b0c72724553f8769da55d84e376f847f52b64`. Recreated same test logic in a temporary file and ran `python -m unittest discover -s /tmp/v73r39 -v` using Python 3.13.5: **2 tests passed, 0 failures** (12 boundary subcases + 6 above-threshold subcases, plus 3 assertions). Temporary copy SHA256 `82c30352f881d8673b1308547bbf175589f7fb96c28fa4f9590002145958f0df`; this is **not** an exact checkout of the original file and does not validate JUCE behavior. Six fs/buffer pairs: 48/96kHz × 32/256/2048; targets 0, 0.000005, 0.00002. Expected first skipped block starts [1408,1280,0] at 48kHz and [2848,2816,2048] at 96kHz for targets <= 0.000005. The predictions are from idealized linear skip arithmetic, not audio measurements.

## Decision
Keep product v0.2 untouched. Do not treat synthetic tests as Neve fidelity or JUCE parity. No cross-repo write, MELON promotion, dispatch, or budget override. Dependent JUCE/Windows external execution BLOCKED due FAILED track. Independent source audit completed.

## Next job R40
Add a standalone deterministic gate truth-table test to CIPI that checks ANALOG × COLOR conditions, including unconditional oversampling and the 0.00001f strict comparison; then compare against an instrumented JUCE 9.0.2 run when authorized runner is available. Record exact JUCE version, sample-rate, buffer sizes, state reset and float traces. Human Gate: licensed original hardware A/B, listening, Cubase Pro 14, final pluginval, adoption and release.
