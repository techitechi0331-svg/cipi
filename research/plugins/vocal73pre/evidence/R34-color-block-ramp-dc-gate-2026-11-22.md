# R34 — COLOR block-ramp scheduling and DC gate boundary (2026-11-22)

## Evidence / provenance
- CIPI main before this change: 945b1769f1b3509e57e2854cae1c804973335fe9 (R33). Read automation-status.md, VOCAL73-1073-IDENTIFIABILITY-001.yaml, 1073-replication-research-plan-v2.md and latest Global DAG Actions metadata.
- Product source inspected: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp . Product remains unchanged.
- In process(), colorSmoothed.setTargetValue(color) then colorSmoothed.skip(buffer.getNumSamples()) once per block; updateFilters(blockColor,...) once per block. dcBlocker.process only if analogEnabled and blockColor > 0.00001. Saturation shares this threshold. 30 ms smoothing reset in prepare().
- **Prediction only**, assuming JUCE SmoothedValue default linear interpolation and a fresh 0.45 -> 0.0 ramp, no subsequent target changes. At sample rate Fs, nominal ramp length N=0.03 Fs. At block size B, first all-zero block-end color occurs at B*ceil(N/B) samples after command. The DC gate is evaluated once per block using the *end-of-block* color, not a per-sample ramp; therefore its transition is block-quantized. No JUCE binary executed here.

| Fs | B | nominal N | predicted first zero-color block end | overshoot vs N |
|---:|---:|---:|---:|---:|
| 48000 | 32 | 1440 | 1440 | 0 |
| 48000 | 256 | 1440 | 1536 | 96 |
| 48000 | 2048 | 1440 | 2048 | 608 |
| 96000 | 32 | 2880 | 2880 | 0 |
| 96000 | 256 | 2880 | 3072 | 192 |
| 96000 | 2048 | 2880 | 4096 | 1216 |

- Interpretation: the table is a control-update timing bound, **not** a measured audio latency, not a DC-filter settling time, not Neve fidelity. A block whose end color reaches zero can bypass DC filtering for that entire block; the exact gate edge must be captured by a JUCE fixture. If the JUCE ramp algorithm or initial conditions differ, this prediction must be revised.
- Formula and table are reproducible by integer arithmetic: N=round(0.03*Fs), edge=((N+B-1)//B)*B, overshoot=edge-N. The strictly positive 1e-5 threshold can trigger slightly earlier than zero for sufficiently small blocks; table specifically reports the *zero-color* boundary, not exact threshold crossing.

## Decision
- R33 deadband and R32 threshold are not sufficient to establish sample-accurate gate timing. Introduce an explicit block-boundary timing oracle; do not alter product v0.2 or claim acoustic quality. Preserve original-vs-reissue provenance and Human Gate.
- Existing external VOCAL73 track remains FAILED per automation-status.md; no automatic dispatch, budget expansion, MELON promotion or product write authorized. Global DAG latest observed success is not evidence of the failed external track's recovery.

## Next Job — R35
- READY independent: inspect JUCE 9.0.2 SmoothedValue::skip semantics and construct an isolated source-level gate timing test; compare expected block edges for 48/96 kHz, B=32/256/2048, initial 0.45 and both 0->1 and 0.45->0 ramps; record exact sample index, raw smoothed value, EQ coefficient update flag and DC gate state.
- BLOCKED dependent: compile/run JUCE fixture on compatible runner; log max sample error, RMS and settling against R31 oracle. Do not mark completed without actual output artifact.
- HUMAN GATE: original 1073 measured A/B, blind listening, Cubase 14, final pluginval, adoption and release.
