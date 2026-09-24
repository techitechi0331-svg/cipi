# VL2A — Evidence Inventory 2026-09-25

This inventory is additive. It does not overwrite the CIPI LA-2A/T4 reference track or the product repository.

## SOURCE_FACT

- Product repository: `techitechi0331-svg/VocalPrepComp`.
- Audited product branch: `build-vocal-leveler2a-v01`.
- Import head: `27ea4b68d17c45b9ea43d1eb73d15764cb107c06`.
- Phase 01-H changes only the main line amplifier; T4, sidechain, Peak Reduction law and COMP/LIMIT are intentionally unchanged.
- Final product Gain decision: `-18..+18 dB`, default 0 dB.
- Phase 01-H test artifact still carries `-30..+30 dB`; do not treat that temporary range as final.
- Input trim is not approved as a sidechain-calibration workaround.
- No raw user/client vocal audio is stored in CIPI.

## MEASURED

### Compiled line-amplifier snapshot
Source run: `36043621530`, source SHA `7bf08c28bd2032f08db36faa2e8c318275fe29f8`.

Imported exact CSV snapshots:
- `phase01h-compiled/frequency_response.csv`
- `phase01h-compiled/thd_1k.csv`
- `phase01h-compiled/output_impedance_proxy.csv`
- `phase01h-compiled/sample_rate.csv`
- `phase01h-compiled/stress.csv`
- `phase01h-compiled/cpu_microbenchmark.csv`
- `phase01h-compiled/alias_diagnostic.csv`

Measurement artifact: `10829478410`  
Artifact SHA256: `324e169fd9a1de0040392a12b81ed4ca99cc28df6bc5e99dc727a9a0498528c1`.

VST3 artifact: `10829637923`  
VST3 artifact SHA256: `67fbf022162d2b48cb7cb0c38204201d6a30a43d701eb0d8f6f634b931172f8c`.

### Automated VocalSet AB snapshot
Source run: `36057598192`, source SHA `27ea4b68d17c45b9ea43d1eb73d15764cb107c06`.

Imported exact objective CSV snapshots:
- `phase01h-free-vocal-ab/metrics.csv`
- `phase01h-free-vocal-ab/render_stats.csv`

AB artifact: `10833729675`  
Artifact SHA256: `27a755d40beaecfa242c6cb229690bc3481915dcd6a9e8cd337c45720d3fd523`.

No WAV files are imported into CIPI.

### User real-host observation
An earlier VL2A audition reported that Peak Reduction near ~80 was needed to obtain only around 3 dB GR in one vocal test. Treat this as an anecdotal real-host observation requiring controlled sidechain/T4 calibration, not as a locked numeric defect.

## INFERRED

- The Phase 01-H line-amplifier candidate is stable enough to listen to; further pre-listening tuning is not supported by new numeric evidence.
- The objective AB is correctly isolated at the GR level because paired baseline/candidate renders report identical max-GR values across all nine cases.
- The candidate must be level matched because its raw RMS is consistently roughly 1.1 dB below the historical baseline in the imported VocalSet matrix.

## HYPOTHESIS

- Human listening will prefer or at least not regress with the Phase 01-H candidate after level matching.
- Later opto/sidechain work will be the dominant source of further compression-feel changes.
- The current Peak Reduction sensitivity concern can be resolved by T4/R37/sidechain calibration without adding an Input control.

## REJECTED

- Old composite 12AX7/12BH7 heuristic as the final fidelity path.
- Generic load-independent 12BH7 soft clipping as final architecture.
- Unsupported A-24 magnetic constants.
- Final Gain range of -30..+30 dB.
- Human-preference claims from automated objective AB metrics.

## VST3 / Cubase

- Phase 01-H Windows VST3 build: MEASURED successful.
- Phase 01-H Cubase Pro 14 runtime confirmation: not yet registered.
- Therefore this track is not HOST_CONFIRMED.

## Failures preserved

Historical workflow/setup failures remain infrastructure evidence and are not classified as DSP failure, including:
- failed hosted/self-hosted 12AX7 review attempts caused by runner/Python setup;
- early offline AB build/headless-startup failures corrected before run `36057598192`.

The successful runs above supersede those infrastructure failures for reproducibility, but the failures are not deleted.


## Chat / product-repo recovery addendum

The current chat history was reconciled against the latest product branch before continuing. The following useful details are preserved here because they are reusable beyond the final Phase 01-H summary.

### SOURCE_FACT

- The product parameter IDs `peakReduction`, `gain`, and `mode` are compatibility-sensitive and are intended to remain stable.
- The product signal-flow decision keeps the user Gain after the T4 audio attenuation node and outside the sidechain detector drive. This detector independence is a retained architectural constraint.
- The 12AX7, 12BH7, and A-24 isolated research histories remain available in the product repository and were not overwritten by the integrated Phase 01-H result.

### MEASURED

- Historical 12AX7-like Baseline A was independently shown to be value-continuous but first-derivative-discontinuous at zero. The positive/negative small-signal slopes were approximately 1.094325 and 1.069855, respectively.
- The same historical 12AX7-like baseline retained roughly 0.49% relative low-level THD across a wide low-level range instead of decaying naturally toward zero.
- The reduced 12AX7 LUT research candidate used 2049 float32 points in the reviewed prototype and reproduced the physical-reference transfer with maximum normalized error on the order of 4e-7 in the tested domain. The point count remained a provisional engineering choice rather than historical truth.
- 12BH7 strict review found that the old generic follower approximation had no load dependence/current sharing/source-impedance model and rejected it as the final architecture. The accepted direction was a load-aware two-section cathode-follower reference with a reduced realtime architecture.
- A-24 strict review accepted only a linear physical/load architecture as the current evidence-backed baseline. Nonlinear magnetic saturation/hysteresis constants remained unapproved due to insufficient A-24-specific evidence.

### INFERRED

- A slope discontinuity in a piecewise memoryless nonlinearity can create a persistent low-level distortion floor even when the transfer value itself is continuous.
- For a cathode-follower output driver, load dependence and source-impedance behavior are more diagnostic of architectural fidelity than simply matching a static soft-clipping curve.
- Transformer model complexity should be gated by measurable error reduction; adding magnetic hysteresis without device-specific evidence increases model complexity without increasing evidentiary confidence.

### HYPOTHESIS

- The slope-discontinuity / low-level-distortion finding is likely reusable as a generic screening test for other vocal saturation and preamp models.
- The load-aware follower methodology is likely reusable for other tube-output stages where the transformer or line load materially affects current/headroom.

### REJECTED

- Treating the old 12AX7/12BH7 composite waveshaper as acceptable because it sounded analog-like.
- Treating 2049 LUT points as a universally optimal nonlinear-model resolution.
- Treating unsupported transformer magnetic constants as historical truth.
