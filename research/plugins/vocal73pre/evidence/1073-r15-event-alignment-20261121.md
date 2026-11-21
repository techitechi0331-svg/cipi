# Vocal73 R15 — event-alignment falsification fixture (2026-11-21)

## Scope / provenance
Synthetic timing-only arithmetic, **not** JUCE/VST3 audio, real Neve hardware, or measured DSP. Follows R14 commit 807321496d4fbd216dd70be57b28078ebf93bb85. Product Vocal73Pre v0.2 unchanged.

## Hypothesis
A parameter event at absolute sample 1440 (48 kHz, 30 ms) can be delayed if automation is applied only at the next buffer boundary; sample-accurate scheduling is the negative control. This is a conditional risk, **not** proof that current JUCE implementation schedules events this way.

## Reproducible minimal test
```python
FS=48000
EVENT=1440
for block in (32,256,2048):
    held=((EVENT+block-1)//block)*block
    assert held >= EVENT
    print(block, held, held-EVENT, (held-EVENT)*1000/FS)
```

## Results (locally executed Python, 2026-11-21)
| block | sample-accurate event | next-block event | delay samples | delay ms |
|---:|---:|---:|---:|---:|
| 32 | 1440 | 1440 | 0 | 0 |
| 256 | 1440 | 1536 | 96 | 2.000000 |
| 2048 | 1440 | 2048 | 608 | 12.666667 |

Assumptions: buffers begin at sample zero; event lies at sample 1440; ceil-to-next-boundary policy. Different block alignment or host automation delivery changes outcomes. These figures are arithmetic predictions only.

## Decision
Keep this distinct from R9 sample-index bookkeeping and R11–R14 COLOR smoothing/hold tests. The new falsification axis is **host event delivery / scheduling vs internal smoothing**, which must be measured separately. No model adoption, product modification, or hardware-fidelity claim.

## Next Job
Instrument existing JUCE fixture to log actual APVTS parameter notification sample/block index, COLOR smoother advancement, and first output change; compare 32/256/2048 at 48k with ANALOG OFF/ON and constant-COLOR negative control. Capture compiler version, JUCE 9.0.2 SHA, test command, hashes, max/RMS residual and event alignment. If unavailable, mark JUCE-dependent portion BLOCKED; retain independent source and arithmetic work. Human Gate: original hardware A/B, listening, Cubase 14, pluginval final, adoption/release.

## Operational gate
Latest checked CIPI automation-status: VOCAL73 track FAILED (LATEST_EXTERNAL_ACTION_FAILED), scheduler in NO_READY_WORK; do not dispatch a duplicate MELON job or override Global DAG/budgets.
