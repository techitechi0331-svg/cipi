# Original Vocal Preamp — Chat Handoff Snapshot

Date: 2026-09-26
Purpose: preserve the exact development state at the point this chat hands off to a new chat.
This file is additive. It does not replace older 610 / Original Vocal Pre evidence.

## SOURCE_FACT

### CIPI / Research OS
- CIPI repo: `techitechi0331-svg/cipi`
- CIPI main at handoff: `99e652f32a8a79dfacb5988d8a522c6c9ea927a5`
- Formal track: `UA610_ORIGINAL_VOCAL_PRE`
- Track path: `research/plugins/ua610/`
- Knowledge status remains `PROVISIONAL`.
- Current product direction remains **reference-informed original vocal preamp**, not a hardware-identical 610 clone.
- Existing CIPI evidence must be reused before new research.
- Negative results must remain preserved.

### Product repository
- Product repo: `techitechi0331-svg/610`
- Active branch: `original-vocal-pre-v0.1`
- Product HEAD at handoff: `c9feef43af6035b81d9cfb96f85d4d61ee8f5d31`
- HEAD message: `Build and archive dedicated Original VST3 separately from 610 research`

Recent product milestones on this branch:
- dedicated Original Vocal Pre processor added;
- simple four-control Original UI added;
- Original DSP wired into the dedicated processor;
- dedicated Original Vocal Pre VST3 target added;
- workflow updated to archive the dedicated Original VST3 separately from the preserved 610 research VST3.

### Current Windows run
- Workflow run: `36142804137`
- Source SHA: `c9feef43af6035b81d9cfb96f85d4d61ee8f5d31`
- State at handoff: **IN PROGRESS**.
- Already passed before this snapshot:
  - Set up job
  - Checkout
  - Setup CMake
  - Configure
  - Build analyzers
  - 610 baseline regression
  - Original research sweep
  - Original v0.2 tuning sweep
- In progress at snapshot: Character level compensation research.
- Still pending at snapshot:
  - Original shortlist extended measurement
  - dedicated Original Windows VST3 artifact upload
  - preserved 610 research VST3 artifact upload
  - final artifact uploads

Do not assume run 36142804137 succeeded merely because the above steps passed. The next chat must inspect its final conclusion and artifacts.

## MEASURED

### Preserved 610 baseline / Windows
Previously validated Windows self-hosted baseline remains green for:
- gain-step accuracy;
- small-signal frequency response;
- sample-rate consistency;
- buffer-size consistency;
- alias stress;
- automation;
- stereo independence;
- latency reporting;
- impulse/step stability.

### Original v0.1 negative result
The first Original candidate at source SHA `31adea261d5f82d3791ee3c3543974167c5f1e83` was formally rejected by fixed acoustic gates.
Key measured problems:
- Character 50 / 100 Hz THD: 11.8102%
- Character 50 / 1 kHz THD: 0.992178%
- LF/mid THD ratio: 11.9033
- Character 100 / 1 kHz THD: 11.4564%
- Character 100 / -6 dBFS stress THD: 30.7347%
- output-transformer-off 100 Hz THD: 1.48899%
- spectral-protection-off 100 Hz THD: 15.4374%
- Character 100 / 8x alias: -80.5881 dBc

CIPI Research Job `OVP-CANDIDATE-V01-GATE-002` verified checksum integrity and still rejected the candidate on acoustic criteria.

### Original v0.2 tuning sweep
Windows Run `36069962074`, source SHA `989b9540ac7dd273908678416ddc5d9afc246413`:
- 27 predeclared tuning candidates measured.
- 18 hard-pass candidates.
- all 2 dB Drive candidates failed the existing Character-100 minimum THD gate.
- 4 dB and 6 dB regions contained hard-pass candidates.
- reduced-drive default improved the original four failures to two remaining failures:
  - Character 100 stress THD still above the <=10% gate;
  - Character 50 LF/mid THD ratio still above the <=2 gate.
- 8x alias behavior remained comfortably inside the current gate.

This sweep is evidence for further narrowing, not permission to select a final product winner by numbers alone.

### MIC 2k / MIC 500 severe-host bug
User reported severe real-host behavior when selecting Mic 2k / Mic 500.

Measured fix snapshot:
- product source SHA: `f2819f2f67606c978bccbabebaa78022697666d4`
- Windows run: `36087412285` — SUCCESS.
- product host policy now bypasses the researched ~+30 dB Mic-mode jump for normal DAW insert use while preserving modeled Mic 2k / 500 loading differences.
- DAW-safe Mic finite gate: PASS.
- Mic 2k vs Line small-signal delta: **0.628168 dB** — PASS.
- Mic 500 vs Line small-signal delta: **2.27886 dB** — PASS.
- Line/Mic repeated-switch peak: **0.042973** — PASS.
- repeated-switch max sample delta: **0.0033295** — PASS.
- all other baseline regression gates remained PASS.

Important limitation:
- automated Windows regression says the catastrophic Mic jump is fixed;
- **Cubase Pro 14 user-side confirmation is still required** before closing the real-host bug.

Existing detailed CIPI evidence:
`research/plugins/ua610/evidence/2026-09-25-mic-input-daw-safety.md`

## INFERRED

- The user's severe Mic-only symptom is strongly consistent with applying the historical 610 research ~+30 dB virtual Mic gain to an already line-level DAW signal.
- For the Original DAW-insert product, retaining the virtual Mic loading difference while removing the +30 dB host gain jump is the safer architecture.
- The 610 research baseline and Original product must remain behaviorally separated so historical research behavior does not leak into the product host path.
- Output-transformer behavior can likely be retained only after retuning; the first candidate's LF distortion was dominated by the output-transformer configuration rather than by the mere existence of a transformer-inspired block.
- 8x oversampling remains the provisional nonlinear baseline; final CPU/latency cost is not yet closed.

## HYPOTHESIS

- One of the numerically valid 4 dB / 6 dB Original tuning regions can survive deeper IMD / alias / frequency / level / real-vocal testing.
- Character internal level compensation is required before fair real-vocal A/B so louder does not masquerade as better.
- The dedicated Original VST3 should expose only the product controls and should not inherit unnecessary 610 research controls or host behaviors.
- A Cubase retest of Mic 2k / 500 should confirm the automated DAW-safe fix unless a separate UI/state/host-recall problem exists.

## REJECTED

- Hardware-identical 610 reproduction as the Original product goal.
- Golden Dataset as a mandatory Original completion blocker.
- Original v0.1 candidate as parameter-locked product.
- Default Original DAW Mic mode with the historical ~+30 dB researched Mic gain jump.
- Treating the first output-transformer configuration as acceptable after the measured LF penalty.
- Choosing a final tuning winner from the 27-point numerical sweep without deeper measurement and real-vocal A/B.
- Treating environment/runner failures as DSP failures.

## CURRENT PRODUCT SHAPE

Intended user-facing Original control surface:
- INPUT
- CHARACTER / DRIVE
- TONE
- OUTPUT

Research/core assets retained:
- two-stage Koren-form tube model;
- negative-feedback interaction;
- transformer-inspired stateful stages;
- spectral drive protection / pre-de-emphasis concept;
- 8x FIR oversampling baseline;
- deterministic Windows regression;
- clean utility Output;
- research-only tuning and ablation surfaces.

Preserved separately:
- 610 research model / historical controls / clone-oriented evidence.

## UNRESOLVED / MUST NOT BE SILENTLY CLOSED

- Final Character mapping.
- Final Tone mapping.
- Final transformer tuning/retention decision.
- Character level compensation final mapping.
- IMD closure for the final Original candidate.
- CPU measurement and final 8x/latency tradeoff.
- level-matched real-vocal AB: Bypass vs preserved 610 baseline vs Original.
- Cubase Pro 14 Mic 2k / 500 retest.
- Cubase scan/load/automation/save-reopen/state recall.
- dedicated Original VST3 Run `36142804137` final result and artifact hash.
- final precision review.
- CIPI status must remain PROVISIONAL until those product-scope gates are closed.

## NEXT CHAT — REQUIRED STARTUP ORDER

1. Read latest `techitechi0331-svg/cipi` main.
2. Read this handoff snapshot.
3. Read `research/plugins/ua610/research.md`, `status.yaml`, and all evidence files.
4. Read latest `techitechi0331-svg/610` branch `original-vocal-pre-v0.1`.
5. Inspect final conclusion/artifacts of Windows Run `36142804137`.
6. Confirm no newer CIPI Research Job/evidence supersedes the numerical shortlist.
7. Continue formal flow:
   measurement -> real-vocal AB -> revision -> dedicated VST3 validation -> Cubase Pro 14 -> final review.

Do not repeat already-completed 610 clone research unless contradictory evidence requires it.
Do not delete or overwrite negative evidence.
Do not call the product complete until Cubase and real-vocal gates are actually closed.
