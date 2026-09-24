# PeakBody Revision 02 — Prototype Branch Gate

Date: 2026-09-24  
Classification: **MEASURED**

## Scope

This record captures the final experimental CIPI prototype-branch CI result before product/research repository separation became the required operating model.

Prototype branch:

`dev/peakbody-v0.1-current`

Validated commit:

`33f87ed5af8c1e60be019d2e8e5228a7cc3c609e`

GitHub Actions run:

`peakbody-revision-check #4` / run `36053788373`

## Result

All branch-gate steps completed successfully:

- Configure: PASS
- Build DSP tests: PASS
- Run deterministic DSP tests: PASS
- Build PeakBody VST3: PASS
- Verify PeakBody VST3 bundle: PASS

The deterministic test set at that commit included the Revision 02 behavioral policy:

- 80 ms crest integration;
- split-direction 6–40 ms attack;
- 120–400 ms release;
- 30 ms burst may not exceed fixed 40 ms attack by more than 0.15 dB;
- sustained body must reach at least 88% of final GR within 150 ms.

## Interpretation

This is **prototype implementation evidence**, not Cubase host validation and not release evidence.

The successful branch build demonstrates that the Revision 02 experimental implementation and its deterministic policy tests compiled and executed successfully on the Windows CI environment used by CIPI.

## Product-boundary note

Under the current operating rule, CIPI is the research/measurement/common-knowledge repository. Product DSP/VST3 implementation must live in a dedicated target plug-in repository.

Therefore this successful CIPI prototype branch is retained as historical implementation evidence, but its product PR must not be merged into CIPI main.

The next product implementation step is migration of the validated Revision 02 specification into a dedicated PeakBody product repository.
