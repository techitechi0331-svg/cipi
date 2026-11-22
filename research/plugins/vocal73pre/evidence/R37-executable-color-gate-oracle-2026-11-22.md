# R37 — executable synthetic COLOR gate oracle (2026-11-22)

## Evidence / provenance
CIPI main checked: health shows VOCAL73-1073-IDENTIFIABILITY-001 FAILED (LATEST_EXTERNAL_ACTION_FAILED), no local READY job; Cross-Repo enabled, 2 queued / 0 dispatched / 29 failed. Track budget max_runs=3, max_runtime=300; no external dispatch attempted. Research plan v2 checked. R36 commit 54c75613e3e977dce80b7bd31667860c57e4640e; Research Gate run 44974328626 succeeded. Product DSP source blob 691ceb53d773a8d23ed782a33c1c5ca47b29859c read-only. No manufacturer or hardware measurements and no JUCE execution.

## R37 difference
Added stdlib-only executable oracle at `research/plugins/vocal73pre/tests/test_r37_color_gate_oracle.py` (commit acfe6ef4adc4538d298dc5c2a6e319d72afe00c4). Models a 30 ms *linear* COLOR ramp from 0.45 with block-end skip and strict gate `blockColor > 0.00001`. Targets 0 and 0.000005 must eventually disable; target 0.00002 remains enabled. Distinguishes DSP gate threshold from EQ coefficient refresh threshold 0.0005. This is a falsifiable **synthetic model**, not a JUCE, hardware, audio, or 1073-fidelity result.

| fs | block | first disabled block start (samples; target 0 or 0.000005) | target 0.00002 |
|---:|---:|---:|---|
| 48000 | 32 | 1408 | remains enabled |
| 48000 | 256 | 1280 | remains enabled |
| 48000 | 2048 | 0 | remains enabled |
| 96000 | 32 | 2848 | remains enabled |
| 96000 | 256 | 2816 | remains enabled |
| 96000 | 2048 | 2048 | remains enabled |

Independent local Python arithmetic reproduced all 12 disable predictions. Test fixture was committed but not executed in a JUCE runner. No CPU or spectral results.

## Decision
KEEP as a non-authoritative regression oracle only. The model uses ideal arithmetic; exact JUCE float rounding and real coefficient-state/audio consequences remain unverified. Do not promote to reference 1073 fidelity or modify Vocal73Pre v0.2. Do not dispatch a failed external track or exceed its budget. No MELON promotion.

## Next Job R38
On a READY permitted environment, run `python -m unittest research/plugins/vocal73pre/tests/test_r37_color_gate_oracle.py`, then instrument a separate JUCE 9.0.2 fixture to record actual `blockColor`, EQ coefficient update count, DC processing gate and output waveforms at 48/96kHz x 32/256/2048. Compare first disabled block and numerical error against the oracle. Dependent JUCE/Windows work BLOCKED by external track failure; independent provenance and fixture review remain eligible under CIPI No-Wait. Human Gate: original-unit A/B, licensed audio, blind listening, Cubase 14, final pluginval, product/release decision.
