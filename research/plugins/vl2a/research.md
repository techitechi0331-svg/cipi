# VL2A Phase 01-H — reference-informed optical leveler / line-amplifier track

## Provenance

- Product repository: `techitechi0331-svg/VocalPrepComp`
- Product branch audited here: `build-vocal-leveler2a-v01`
- Latest audited branch head at import: `27ea4b68d17c45b9ea43d1eb73d15764cb107c06`
- Reference direction: mid-1960s LA-2A / Gray / T4A family behavior, with original VL2A product UX rather than a hardware-identical clone.

The product repository remains authoritative for VST3/DSP implementation. CIPI stores reusable research, measurements and review evidence only.

## Current scope

This CIPI track imports the completed Phase 01-B..H work around the VL2A main audio line amplifier:

`12AX7 research -> 12BH7 research -> UTC A-24 research -> integrated feedback/numeric determination -> compiled C++ measurement -> real-vocal AB gate`

T4, R37/sidechain, Peak Reduction law and final product oversampling remain separate later work.

## Current synthesis — 2026-09-25 non-destructive content audit

The early Phase 01-H sections below are preserved as historical stage records. They are no longer the authoritative statement of the track's current location.

Current evidence state:
- Phase 01-H line amplifier received an engineering **KEEP** decision and was integrated into VL2A v0.5.0.
- The final product Gain range was restored to `-18..+18 dB` with a `0 dB` centre, and the mojibake-prone UI separator was corrected during that integration.
- Phase 02 measured the exact current T4 / sidechain / Peak Reduction / COMP-LIMIT baseline and passed its hard-correctness gates.
- R37 / sidechain emphasis remains factory-flat for the music/vocal product default.
- A later strict reference-parity review **reopened** the user-facing Peak Reduction operating range, gain-reduction meter presentation, stereo detector/link law and active-compression nonlinear coloration.
- The UAD LA-2A Collection `-12 dBFS` value is a plug-in internal reference level; it must not be conflated with the separate laboratory convention `-18 dBFS = +4 dBu`.
- Human subjective preference is still not measured, and Cubase Pro 14 release-candidate validation is still pending.

For current work, use `status.yaml` plus the later Phase 01-H integration, Phase 02, R37 and strict reference-parity sections in this document. Earlier "Current location", "Unresolved" and "Next stage" paragraphs are historical snapshots and must not override newer evidence.

## SOURCE_FACT

- The product architecture keeps input transformer, T4 attenuation, Gain, line amplifier and output transformer as separable concerns.
- Phase 01-H intentionally changed only the main line-amplifier path. Input transformer, T4 model, sidechain, Peak Reduction law, COMP/LIMIT behavior and parameter IDs were left unchanged.
- The final product decision is Gain `-18..+18 dB`, center `0 dB`; the current Phase 01-H test VST3 still carries the temporary `-30..+30 dB` research range.
- An optional Input trim is not approved as a fix for sidechain/T4 calibration.
- The white-digital UI remains the chosen product direction; top-left text rendering/mojibake still requires product-side correction.
- CIPI's existing LA-2A/T4 formal reference track remains the authority for optical timing/source facts. This VL2A track does not duplicate T4 truth.

## MEASURED

### 12AX7 / 12BH7 / A-24 research carry-forward

- Historical 12AX7-like transfer was rejected as the final fidelity primitive after a zero-crossing derivative mismatch and an approximately fixed low-level THD floor were reproduced.
- A measured-device 12AX7 family model was retained as offline/reference evidence; a compact LUT architecture was conditionally accepted as a realtime primitive.
- 12BH7 research rejected reuse of the generic 12AX7/tanh-style follower as final architecture. A load-aware two-section cathode-follower architecture received conditional pass.
- A secondary 12BH7 model-interpretation error involving the factor of two in a PSpice relation was found during review and corrected; negative evidence was retained.
- UTC A-24 research conditionally accepted a linear physical/load architecture and explicitly did not approve unsupported magnetic saturation/hysteresis constants.

### Integrated line-amplifier numeric/compiled result

Authoritative product run:
- workflow run `36043621530`
- source SHA `7bf08c28bd2032f08db36faa2e8c318275fe29f8`
- measurement artifact `10829478410`, artifact SHA256 `324e169fd9a1de0040392a12b81ed4ca99cc28df6bc5e99dc727a9a0498528c1`
- VST3 artifact `10829637923`, artifact SHA256 `67fbf022162d2b48cb7cb0c38204201d6a30a43d701eb0d8f6f634b931172f8c`

Compiled block measurements include:
- 30 Hz: -0.04364 dB; 1 kHz: -0.00050 dB; 15 kHz: -0.00810 dB at the documented small-signal condition.
- THD at 1 kHz rises smoothly with level: about 0.0000164% at -48 dBFS, 0.001177% at -12 dBFS, 0.004178% at 0 dBFS.
- estimated secondary output source impedance stays about 150.53..150.75 ohm over -24..+3 dBFS test levels.
- 44.1..192 kHz sample-rate sweep stays finite with very small gain drift at 1 kHz / -12 dBFS.
- stress through +30 dBFS-equivalent input remains finite.
- standalone compiled block benchmark: about 17.96 ns/sample, about 290x realtime at 192 kHz in that benchmark environment.

These are block-level measurements, not complete LA-2A/VL2A whole-unit THD specifications.

### Automated real-vocal objective AB

Authoritative product run:
- workflow run `36057598192`
- source SHA `27ea4b68d17c45b9ea43d1eb73d15764cb107c06`
- artifact `10833729675`
- artifact SHA256 `27a755d40beaecfa242c6cb229690bc3481915dcd6a9e8cd337c45720d3fd523`

VocalSet CC BY 4.0 material was rendered for breathy / straight / forte conditions at Peak Reduction 0 / 50 / 75.

Across the 9 objective comparisons:
- correlation: 0.999928..0.999937
- candidate RMS match gain: +1.10499..+1.14611 dB
- matched candidate peak difference versus baseline: 0.0078..0.17533 dB absolute
- residual relative level: about -38.99..-38.39 dB
- baseline and candidate max-GR values are identical per paired render.

This proves the offline comparison is tightly isolated to the line-amplifier difference and is suitable for listening. It does **not** prove a subjective preference.

## INFERRED

- The old roughly fixed low-level distortion floor came from the historical composite tube approximation rather than being required by the reference architecture.
- The Phase 01-H reduced line amplifier is numerically stable enough to enter listening without further arbitrary retuning.
- Identical max-GR in paired vocal renders supports that Phase 01-H did not unintentionally alter the T4/sidechain gain-reduction trajectory in the tested matrix.
- The approximately 1.1 dB candidate-vs-baseline level offset is a comparison/calibration difference that must be level matched before sonic judgment; louder-is-better bias would otherwise dominate.

## HYPOTHESIS

- The Phase 01-H candidate will sound at least as natural as the historical line-amplifier path after strict level matching, while reducing low-level fuzz and preserving consonant/transient definition.
- The later T4/R37/Peak-Reduction study may materially change compression depth and program dependence even if the line-amplifier candidate is kept.
- Final product Gain `-18..+18 dB` can be restored without changing the validated line-amplifier transfer, provided gain staging remains post-T4 and detector-independent.

## REJECTED

- Historical composite `TubeAmplifierModel` as the final 12AX7/12BH7 fidelity model.
- Treating 12BH7 as merely an extra generic soft clip.
- Unsupported A-24 magnetic saturation/hysteresis constants as historical truth.
- Using an Input trim to conceal unresolved sidechain/T4 sensitivity.
- Temporary `-30..+30 dB` Gain range as the final product UX.
- Treating automated objective vocal rendering as a substitute for human level-matched listening.

## Real-audio / Cubase status

- Automated objective vocal render gate: complete.
- Human blind/level-matched listening decision: pending.
- Earlier VL2A builds have been auditioned by the user, including a report that high Peak Reduction was needed for modest GR in one test; this remains an anecdotal calibration clue, not a controlled acceptance result.
- Phase 01-H VST3 Windows build: successful.
- Phase 01-H Cubase Pro 14 scan/load/automation/state-recall confirmation: pending.

## Current location

**Audio AB gate for Phase 01-H line amplifier.**

## Completed

- isolated research and strict review for 12AX7, 12BH7 and A-24;
- integrated line-amplifier research and strict review;
- numeric determination and review;
- regression-safe C++ implementation;
- compiled Windows measurements;
- Windows VST3 build;
- automated objective real-vocal render and level-match pack.

## Unresolved

- human KEEP / REVISE / ROLLBACK decision for Phase 01-H;
- final product Gain `-18..+18 dB` application;
- top-left UI text/mojibake fix;
- Cubase Pro 14 validation of the production candidate;
- final product-level alias/oversampling approval;
- later T4 / R37 / sidechain / Peak Reduction research and calibration.

## Next stage

Human level-matched vocal AB.

## Why this is the next stage

The line-amplifier block has already passed the current numeric gates. Retuning it again before listening would introduce changes without new evidence.

## What the next stage will confirm

Whether Phase 01-H is KEEP, REVISE or ROLLBACK based on natural vocal density, transient definition, low-level texture, harshness/fuzz, low-end stability, high-frequency naturalness and consonant clarity at matched level.

## Reusable knowledge targets

- separated tube-device reference vs realtime reduced-model design;
- load-aware cathode-follower modeling;
- transformer model complexity gates;
- closed-loop line-amplifier calibration;
- block-isolated real-vocal AB with invariant GR checks;
- measurement maturity separation between model, compiled DSP, VST3 and real-host confirmation.


## 2026-09-25 Phase 01-H strict engineering decision

Decision: **KEEP**.

Evidence boundary:
- This is an engineering/signal-analysis decision, not a claim of human blind-listening preference.
- The user delegated the decision to the assistant.
- The recovered 9-pair VocalSet A/B artifact was independently re-analysed.
- Baseline/Candidate GR was identical in every pair.
- Level-matched correlation was 0.999928..0.999937.
- Residual relative level was -38.9898..-38.3867 dB.
- Maximum absolute matched peak difference was 0.17533 dB.
- Independent band analysis found a maximum absolute 250 Hz..20 kHz energy shift of about 0.103 dB and a systematic 20..80 Hz shift of about +0.381..+0.436 dB.
- The compiled Phase 01-H block removed the previously reproduced approximately fixed low-level distortion floor while retaining finite, level-dependent behavior.

Interpretation:
- no material objective regression was found;
- the candidate fixes a known modeling defect without changing the T4/sidechain GR trajectory;
- the sub-80 Hz shift is retained as a known small tonal difference, not erased from evidence.

Actions authorized:
- retain Phase 01-H line amplifier;
- restore final Gain -18..+18 dB, 0 dB centre;
- fix the remaining mojibake-prone UI glyph;
- build/validate the production candidate;
- after that, continue T4/R37/sidechain/Peak Reduction research.

Human subjective preference remains **not measured** and must not be represented as confirmed evidence.


## 2026-09-25 v0.5.0 Phase 01-H integration

Product integration is complete on the VL2A development line.

Product merge:
- repository: `techitechi0331-svg/VocalPrepComp`
- target branch: `build-vocal-leveler2a-v01`
- merge commit: `a74b6d735774ff23de0342c008bcbe32381fbdd6`

Validated pre-merge executable-equivalent build:
- workflow run: `36076772730`
- validated source SHA: `d0419a90d5050b8cb1d5ced672989ca2276fe6c0`
- Windows VST3 artifact id: `10840940568`
- VST3 artifact digest: `sha256:fd0413a34b0a3b4ec7e1735aeb51d48cd4ee9ffff13d764854c63d4aa4a3e18c`
- Phase 01-H measurement artifact id: `10839914317`
- measurement artifact digest: `sha256:c778c72bcbf2efd285a223db4e8fde1fe7c5ddbf7701b2f05b6dcb40b9a970a4`

Integration changes:
- Phase 01-H line amplifier retained;
- final Gain restored to -18..+18 dB with 0 dB centre;
- mojibake-prone UI separator replaced with ASCII;
- generated product version set to v0.5.0.

The commits after the validated source SHA changed CI metadata, evidence text,
and one source comment only. No post-validation DSP or executable behaviour
change remained at merge.

Current stage now advances to **Phase 02 baseline measurement of the existing
T4 / sidechain / Peak Reduction / COMP-LIMIT subsystem**.

No optical/sidechain production constants are yet approved for change.


## 2026-09-25 Phase 02 exact current-engine baseline

Status: **MEASURED / hard correctness gate PASS**.

Product source:
- repo: `techitechi0331-svg/VocalPrepComp`
- branch: `research/vl2a-phase02-t4-sidechain-baseline`
- measured SHA: `76d84dbccc9339348c7fd2a2b0e456e49f7285e9`
- workflow run: `36084297057`
- artifact id: `10842459304`
- artifact digest:
  `sha256:2f7698d1353dcf131afd4be06c5778036be558c9f9a2ce1a552e6503300733e8`

Key measured facts:
- PR0: 0 dB GR in both COMP and LIMIT across the sweep.
- COMP / -18 dBFS / PR80: 2.9216 dB GR.
- COMP / -12 dBFS / PR75: 5.1614 dB GR.
- COMP / -6 dBFS / PR100: 14.7671 dB GR.
- LIMIT / -6 dBFS / PR100: 16.1580 dB GR.
- LIMIT / 0 dBFS / PR100: 22.1558 dB GR.
- 60 ms retained GR after 0.1..15 s exposure:
  47.47% .. 53.49%.
- representative 44.1..192 kHz GR spread:
  about 0.014 dB.
- sidechain frequency sensitivity at -12 dBFS / PR75:
  about 5.11..5.16 dB GR from 100 Hz to 15 kHz, confirming the present
  factory-flat emphasis implementation.

Static I/O slope diagnostic:
- PR100 COMP implied ratio rises from ~1.45:1 at the lower step to ~4.48:1
  in the strongest measured step.
- PR100 LIMIT reaches ~7.81:1 before the final step effectively becomes
  horizontal under the study's ratio clamp.
- therefore COMP/LIMIT topology is meaningfully separated and should not be
  rewritten merely because equal-input GR values initially looked similar.

Exact Moore-style reference-condition clue:
- current VL2A at -18 dBFS / about 6 dB GR / 1 kHz produces only a few
  hundredths of a percent THD.
- this is far below the 2026 six-unit hardware measurements under the same
  nominal +4 dBu / 6 dB GR condition.

Engineering interpretation:
- Peak Reduction calibration: **KEEP for now**.
- current release trajectory: **KEEP for now**.
- COMP/LIMIT topology: **KEEP for now**.
- sample-rate behavior: **KEEP**.
- active-compression nonlinear coloration: **priority research gap**.
- R37 / sidechain emphasis remains a later dedicated gate.

No production DSP constant was changed by Phase 02.


## 2026-09-25 R37 / Limit Response product decision

Decision: **KEEP factory-flat / no front-panel control**.

Evidence:
- the 1966 circuit contains R37 = 1 MOhm and C12 = 0.001 uF;
- Universal Audio documents the sidechain equalization as normally set flat
  for musical applications;
- Phase 02 measured the current VL2A at about 5.11..5.16 dB GR from
  100 Hz through 15 kHz under the representative -12 dBFS / PR75 condition.

Interpretation:
- the current flat product response is compatible with the normal music/vocal
  hardware use case;
- an adjustable R37 network remains historically real, but is not a required
  front-panel feature for VL2A;
- the internal hook may remain for future research/broadcast modes.

Status: **closed unless new original-hardware measurements contradict the
factory-flat assumption**.


## 2026-09-25 strict reference-parity re-audit

Trigger:
- real-use comparison reported substantially deeper gain reduction near maximum
  Peak Reduction in both UAD and Waves LA-2A-family plug-ins than current VL2A
  under ordinary vocal use.

Policy change:
- internal consistency is no longer sufficient for KEEP;
- every user-facing control and meter must be cross-checked against original
  source material, controlled current-engine measurement, and at least one
  commercial reference when the comparison is operational/UX rather than
  circuit-physical.

### REOPEN — Peak Reduction operating range
Phase 02 explained the current VL2A curve but did not prove that the available
user-facing range is appropriate. UAD officially documents:
- 0..100 front-panel values are arbitrary;
- Peak Reduction lowers trigger threshold;
- available Peak Reduction range is described as 0 to -40 dB;
- LA-2A Leveler Collection internal reference is -12 dBFS.

Current VL2A Phase 02 examples:
- -18 dBFS / PR80 COMP: ~2.92 dB GR
- -18 dBFS / PR100 COMP: ~6.22 dB GR
- -12 dBFS / PR100 COMP: ~10.28 dB GR

Status: **REOPEN / calibration candidates required**.
T4 timing must remain fixed while sidechain-drive mapping is studied.

### REOPEN — Gain Reduction meter
Current white-digital UI clamps displayed GR to 20 dB and labels the display
0/5/10/15/20. This is a UI limitation, not a DSP limit.

Official hardware documentation supports up to 40 dB gain limiting.
Status: **REOPEN**. Do not alter DSP merely to satisfy the meter.

### UNRESOLVED — stereo detector/link law
Current stereo detector:
`0.5 * (abs(L) + abs(R))`.

This means a one-sided event generates less detector level than the same event
present equally in both channels.

Historical/UA linked operation supports linked gain reduction that preserves the
stereo image, but available documentation does not prove that sample-by-sample
max(L,R) is the correct historical law.

Status: **UNRESOLVED / measure before changing**.
Previous informal claims that max detection is necessarily correct are
withdrawn.

### NORMALIZATION RULE — reference levels
Never mix:
- UAD Leveler Collection internal reference: -12 dBFS;
- Moore 2026 laboratory calibration: -18 dBFS = +4 dBu.

Every comparison must state its reference context.

### KEEP PROVISIONALLY
- T4 60 ms first-stage recovery behavior;
- program-dependent long release;
- R37 factory-flat musical default;
- main Phase 01-H line amplifier;
- sample-rate stability.

All provisional KEEP items must be rerun after any Peak Reduction calibration
change.

### ACTIVE
Phase 03 active-GR nonlinearity candidate research continues separately.
Reference-parity audit branch:
`research/vl2a-reference-parity-audit`.

Completion now requires:
- normalized Peak Reduction range validation;
- meter decision;
- stereo-link measurement;
- active-GR nonlinearity decision;
- real-vocal validation;
- strict pluginval;
- Cubase Pro 14 host confirmation;
- final CIPI contradiction review.


## 2026-09-25 Reference-Parity Audit measured result

Audit run `36088776046` passed its hard implementation gate.

The main new conclusion is a separation of **capability** from **calibration**:

- VL2A can already reach about 32 dB COMP and 36.8 dB LIMIT at very hot
  PR100 input, so the T4 maximum-reduction capability is not the primary
  blocker.
- At ordinary reference contexts it is much more conservative:
  - -18 dBFS / PR50 COMP: ~0.61 dB GR
  - -18 dBFS / PR100: ~6.22 dB
  - -12 dBFS / PR100: ~10.28 dB
- therefore the Peak Reduction / sidechain operating sensitivity remains
  **REOPEN / high priority**.

Stereo detector:
- centered stereo == mono in the current implementation;
- one-sided stereo produces materially less GR;
- L/R symmetry is correct;
- exact historical/commercial one-sided sensitivity is not source-established.
Status remains **UNRESOLVED**; do not switch to max detection by inference.

Meter:
- current 50 ms editor rise smoothing can under-display short-event GR by
  approximately 1..5.6 dB in the measured matrix;
- by 250..500 ms the displayed value is close to DSP GR;
- this can affect perceived responsiveness but does not explain the sustained
  Peak Reduction operating-range discrepancy.
- 20 dB meter full scale is not automatically a defect; meter scale and
  compressor maximum capability are separate.

Artifact:
- id `10844739826`
- digest `sha256:757c94d102433c210fecd4fe7d901fc9eb2246f2a938a2bcdf52f242b79915df`

Next:
- revised Peak candidate matrix;
- Phase 03 active-GR nonlinearity decision;
- level-matched free-vocal validation;
- controlled commercial-reference host comparison.


## 2026-09-25 Phase 03 active-GR candidate result

Strict candidate matrix completed successfully on product run `36108289078`.

Selected numeric candidate:
- **v4**
- ~0.9408% THD at -18 dBFS / ~6 dB GR / 1 kHz
- H3 dominant at ~-40.67 dBc
- fixed-control GR drift versus baseline: 0.0000 dB
- matched 60 ms release-retention drift: 0
- sample-rate GR drift versus baseline: 0
- PR0 THD remains ~0.01157%

Interpretation:
- v4 demonstrates that the missing active-compression harmonic envelope can be
  reproduced without changing the validated T4/control trajectory.
- v4 is **not production-approved** because its memoryless coloration mechanism
  is not yet physically justified.
- v1/v2/v3 are rejected in their current form because they either miss the
  target harmonic window or perturb the control law beyond predeclared limits.

Next:
- stateful/optical-modulation follow-up;
- then level-matched real-vocal validation;
- only then production consideration.


## 2026-09-25 stereo-link product decision

Decision: **KEEP current shared phase-safe detector as an intentional modern
VL2A design**.

Current law:
`0.5 * (abs(L) + abs(R))`

Evidence boundary:
- 1966 Teletronix stereo linking makes the control voltage common so either
  channel can cause equal gain reduction in both units;
- Waves CLA-2A documents one detector for both stereo channel paths;
- neither source publishes a digital-equivalent one-sided L/R combine law;
- current VL2A is symmetric, centered-stereo == mono, and phase-safe.

Therefore:
- one shared detector: KEEP;
- current average-of-magnitudes combine: KEEP as product design;
- exact 1966 one-sided sensitivity: not claimed;
- max(L,R) as historical truth: rejected as unsupported.

This closes stereo-link as a release blocker unless new controlled reference
measurements justify reopening it.


## 2026-09-25 Phase 03B stateful optical-ripple result

Run `36112297868` completed successfully.

Strict winner:
- **v3**
- 1 kHz / ~6 dB GR THD: ~0.7830%
- H3: ~-42.22 dBc
- fixed-control GR drift: 0.00000 dB
- matched T4 release/control path preserved

Five-frequency active-GR THD:
- 63 Hz: ~1.366%
- 125 Hz: ~1.178%
- 250 Hz: ~1.119%
- 500 Hz: ~1.029%
- 1 kHz: ~0.783%

Decision:
- promote Phase 03B v3 to **integration candidate**;
- retain Phase 03 v4 as numeric benchmark only;
- do not promote to release until combined Peak calibration and real-vocal
  regression pass.


## 2026-09-25 Peak Reduction calibration v3

Strict matrix run `36142898418` completed successfully.

Selected:
- `0.18 * 10^(2.00 * n^0.85)`
- -18 dBFS COMP:
  - PR30 ~0.50 dB
  - PR50 ~1.94 dB
  - PR75 ~6.38 dB
  - PR100 ~12.44 dB
- -12 dBFS / PR100 COMP ~17.07 dB
- matched-GR T4 release unchanged
- high-drive finite through +18 dBFS

Decision:
- **Peak calibration v3 -> integration candidate**
- current v0 calibration -> superseded for final integration
- no T4 timing change.


## 2026-09-25 Peak Reduction midpoint specification change

New product requirement:
- real vocal approximately -18 dBFS peak
- mode = COMP
- Peak Reduction = 50
- target GR = approximately 5..7 dB

This new operating-point requirement supersedes the previous Peak calibration
v3 integration decision for the final product.

Previous selected v3 measured only about 1.94 dB GR at -18 dBFS / PR50 in the
1 kHz calibration context and is therefore no longer acceptable as the final
VL2A Peak curve.

Current status:
- prior Peak v3: **SUPERSEDED**
- T4 timing: unchanged / still provisionally KEEP
- COMP/LIMIT topology: unchanged
- R37: unchanged
- Phase 03B optical v3: remains integration candidate
- new active research branch:
  `research/vl2a-peak-calibration-v4-midpoint`

The final calibration gate is now based on normalized real VocalSet material,
not only a sine-wave proxy.


## 2026-09-25 Phase03C low-band refinement

Shortening the optical mean-tracking tau was tested and rejected.

Measured forte 20..80 Hz max band shift:
- current 4.0 ms: ~0.789805 dB
- 3.5 ms: ~0.799981 dB
- 3.0 ms: ~0.813955 dB
- 2.5 ms: ~0.836254 dB

All candidates retained ~0.783% 1 kHz active-GR THD and H3 dominance, but all
failed the strict <=0.75 dB real-vocal band gate.

Decision:
- shorter tau direction: REJECTED
- next experiment: longer tau 4.5 / 5.0 / 6.0 ms
