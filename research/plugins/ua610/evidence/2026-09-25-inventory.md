# Original Vocal Preamp — Evidence Inventory 2026-09-25

This file is additive evidence. It does not delete or overwrite the historical 610 research track.

## SOURCE_FACT

- Source repository: `techitechi0331-svg/610`.
- Preserved 610 baseline branch: `model-v0.1`.
- Original product branch: `original-vocal-pre-v0.1`.
- Product direction is reference-informed original design, not a hardware-identical 610 clone.
- The 610 research origin remains part of provenance: 610-B / 2-610, 12AX7-family, 12AT7/6072-family, transformer coupling, negative feedback and class-A tube stages.
- Current Original control concept: INPUT / CHARACTER / TONE / OUTPUT.
- Raw client/user vocal audio must not be committed to CIPI.

## MEASURED — preserved 610 baseline

Windows self-hosted run `36041422739`, source SHA `d09eb39cce73e0fe974606079b9c5c9f58822a01`, completed successfully through Configure, VST3/Analyzer build, CI validation, extended validation and artifact upload.

Final 610 baseline quality-gate examples:
- gain-switch step error: 0.0000193657 dB — PASS.
- line max-gain error: 0.00978468 dB — PASS.
- sample-rate gain spread: 0.000952971 dB — PASS.
- 20 Hz small-signal error: 0.343079 dB — PASS.
- 20 kHz small-signal error: 0.803461 dB — PASS.
- 8x alias stress: -88.5968 dBc — PASS.
- automation finite / stereo independence / latency reporting / impulse / step: PASS.
- Output utility THD delta: 5.43843e-09 percentage points — PASS.

Artifact provenance:
- Windows VST3 artifact SHA256: `d5c6b15b9527a9fc91182c5729b028f60339db50d3b4cf7d133d8028e317eabe`.
- Validation artifact SHA256: `1c406021a2eeb1cea8d65e32a670df79eb9b60da0516455cafc77e2f95971d09`.

Cubase Pro 14 real-host confirmation was not completed in this chat at the time of this inventory; do not promote the baseline to HOST_CONFIRMED from automated Windows evidence alone.

## MEASURED — Original candidate v0.1

Windows Original research run `36060427037`, source SHA `31adea261d5f82d3791ee3c3543974167c5f1e83`, completed successfully. Baseline regression and Original research sweep both passed as workflows; the product candidate itself intentionally contains failed acceptance gates.

Candidate gate results:
- Character 0, 1 kHz, -18 dBFS: THD 0.202882% vs <=0.15% target — FAIL.
- Character 50, 1 kHz, -18 dBFS: THD 0.992178% vs 0.15–1.0% target — PASS.
- Character 100, 1 kHz, -18 dBFS: THD 11.4564% vs 0.5–3.0% target — FAIL.
- Character 100, 1 kHz, -6 dBFS stress: THD 30.7347% vs <=10% target — FAIL.
- Character 50 upper-harmonic ratio: 0.0126702 vs <=0.5 — PASS.
- Character 50 LF/mid THD ratio: 11.9033 vs <=2 — FAIL.
- Character 100, 8x alias: -80.5881 dBc vs <=-70 dBc — PASS.
- finite stress — PASS.

Ablation at Character 50 / -18 dBFS:
- full at 100 Hz: 11.8102% THD.
- output transformer OFF at 100 Hz: 1.48899% THD.
- spectral protection OFF at 100 Hz: 15.4374% THD.
- full at 1 kHz: 0.992178% THD.
- output transformer OFF at 1 kHz: 0.846036% THD.

Aliasing:
- Character 50: 4x -12.1095 dBc; 8x -119.527 dBc; 16x -119.405 dBc.
- Character 100: 4x +15.2301 dBc with near-collapsed fundamental; 8x -80.5881 dBc; 16x -80.0718 dBc.

Sample-rate sweep 44.1–192 kHz remained finite and tightly consistent in gain for all tested Character settings.

The committed snapshot under `research/experiments/OriginalVocalPre/measurements/610repo-31adea2/` is the authoritative CIPI copy of this run.

## INFERRED

- The current output-transformer configuration is the dominant measured contributor to excessive low-frequency nonlinearity at the Character 50 test point. This inference is supported by the large 100 Hz THD reduction when that block is removed, while 1 kHz THD changes much less.
- The current spectral-drive protection acts in the intended direction at 100 Hz, because disabling it increases 100 Hz THD, but its present strength is insufficient.
- The current Character mapping becomes too aggressive above the moderate region and must not be parameter-locked unchanged.
- 8x is the current preferred oversampling baseline over 4x because the measured alias reduction is dramatic, while 16x gives little alias improvement over 8x in these tests. CPU/latency still needs direct measurement before this becomes a final product decision.
- Some high-frequency heavy-drive rows show fundamental collapse and extreme THD ratios; these are measured anomalies that require a revised stress interpretation before they are used as listening-quality evidence.

## HYPOTHESIS

- Retuning or simplifying the output-transformer saturation/memory model may preserve useful transformer color while removing the excessive LF penalty.
- A smaller maximum Character drive range plus feedback remapping may keep Character 50 near the useful density region while making Character 100 a usable extreme rather than fuzz-like overload.
- Spectral pre/de-emphasis should be re-evaluated after transformer retuning rather than simply made stronger.
- A gain-compensated ablation design is needed for Tube 1 / Tube 2 removal because removing a gain stage changes the drive presented to later nonlinear stages.

## REJECTED

- Hardware-identical 610 reproduction as the final product goal.
- Golden Dataset acquisition as a mandatory completion blocker for the Original product.
- Current Original candidate v0.1 as a parameter-locked release candidate.
- 4x oversampling as the default for the current nonlinear candidate.
- Treating infrastructure failures as DSP failures. Earlier self-hosted setup failures included missing `pwsh`, PowerShell execution-policy blocking, and missing `cmake`; these were workflow/environment issues and were corrected without changing DSP.

## Real-audio / Cubase inventory

- No level-matched Bypass vs preserved 610 baseline vs Original real-vocal AB result is registered in this chat yet.
- No Original VST3 Cubase Pro 14 scan/load/save-reopen result exists yet.
- Therefore audio_ab and HOST_CONFIRMED remain pending.

## Unresolved measurement gaps

- Original IMD.
- Original group delay as an explicit report.
- CPU cost at 44.1/48/96 kHz.
- latency-versus-oversampling tradeoff.
- gain-compensated ablation.
- real-vocal level-matched AB.
- final VST3 validator/pluginval/Cubase gate.
