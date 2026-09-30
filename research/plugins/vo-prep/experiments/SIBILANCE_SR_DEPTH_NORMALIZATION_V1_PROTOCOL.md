# Vo.Prep Sibilance SR Depth Normalization v1 — Candidate Protocol

Status: **LOCKED BEFORE PRODUCT IMPLEMENTATION**

## Evidence basis

Actual-VST3 Sibilance SR Sweep v1 returned `DEPTH_SCALING_SUFFICIENT`.

The high-rate diagnostic rows show that approximately 35% effective depth at 88.2/96 kHz preserves the compatibility envelope of the current 48 kHz / 50% behavior.

## Candidate hypothesis

Keep the Sibilance detector and topology unchanged. Normalize only the requested reduction depth as sample rate rises.

Candidate scale:

```
normalizedRate = clamp(sampleRate, 44100, 96000)
depthScale = sqrt(44100 / normalizedRate)
effectiveRequestedReduction = requestedReduction * depthScale
```

Properties:
- <=44.1 kHz: scale 1.0;
- 48 kHz: ~0.9585;
- 88.2 kHz: ~0.7071;
- >=96 kHz: ~0.6778 (clamped at the 96 kHz validated boundary).

The 96 kHz clamp prevents unvalidated continued attenuation shrinkage at 176.4/192 kHz.

## Product code allowed to change

Only Sibilance reduction depth scaling.

Do not change:
- detector filters;
- detector-divider cadence;
- probability feature weights;
- activation/release/re-arm thresholds;
- attack/hold/release timing;
- amount parameter range/default;
- 33% wide / 67% high topology;
- latency;
- other Vo.Prep modules.

## Predeclared source-level gates

Existing Vo.Prep Sibilance regression suite must remain green.

Add a deterministic cross-sample-rate event attenuation regression at Sibilance 50%:

- sample rates: 44.1 / 48 / 88.2 / 96 kHz;
- all outputs finite;
- each event attenuation >= 0.10 dB;
- max-min event attenuation spread <= 0.05 dB;
- 0% remains dry-null from fresh state;
- bright-vowel and breath safety tests remain unchanged and pass.

Do not weaken existing maximum-reduction ceilings.

## Actual VST3 candidate gate

Build the candidate Vo.Prep VST3 and the protected VoPriPro VST3.

Reuse the locked Actual VST3 Chain Validation v1 matrix and every original numerical gate without relaxation:

- finite output;
- latency;
- neutrality;
- Plosive;
- Sibilance;
- Phrase;
- cross-sample-rate consistency.

The only permitted difference is the Vo.Prep candidate commit ref.

Required decision:
- **GO_TO_REAL_VOCAL_AB** only if every original gate passes.
- **REVISE_AGAIN** if any original gate fails.
- **BLOCKED_EXTERNAL** only for infrastructure failure.

## Promotion rule

Even a full engineering PASS does not close:
- human level-matched listening;
- Cubase Pro 14 scan/load/playback/automation/save-reopen;
- final release review.

No product merge before candidate CI and actual-binary gate evidence are recorded.
