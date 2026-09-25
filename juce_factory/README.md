# CIPI JUCE Factory

JUCE Factory is the deterministic manufacturing layer between CIPI/Plugin Incubator and a VST3 candidate.

It is deliberately **not** a DSP research system, product authority, or release bot.

## Authority boundary

- **CIPI** owns evidence, research state, review and knowledge authority.
- **MELON** explores candidate architectures and returns bounded evidence.
- **Plugin Incubator** decides whether a product candidate is eligible for manufacturing.
- **JUCE Factory** converts an approved, versioned Plugin Contract into a reproducible JUCE project and validates the resulting VST3 candidate.
- **Cubase / listening review** remain required release gates.

A Factory PASS means only that the manufacturing/technical gate passed. It does not mean that a DSP claim is CONFIRMED or that a plug-in is approved for release.

## Phase 1 + Phase 2 implemented here

- versioned JSON Plugin Contract v1;
- strict contract validation;
- JUCE 9.0.2 pinned generated project;
- local JUCE override through `JUCE_SOURCE_DIR` or a project-local `JUCE/` directory;
- APVTS `ParameterLayout` parameter creation;
- deterministic Golden Gain plug-in;
- state save/restore;
- mono/stereo layout check;
- smoothed real-time-safe gain;
- version label;
- non-overwriting generation;
- generation manifest with contract SHA-256;
- isolated MELON result-bundle adapter that cannot grant Factory eligibility;
- CI self-test + Windows VST3 build + external pluginval;
- Factory-owned JUCE validation executable compiled against the generated plug-in;
- 44.1 / 48 / 88.2 / 96 kHz validation matrix;
- block-size matrix including an irregular 257-sample block;
- silence, finite-output, denormal, unity-gain and settled-gain checks;
- rapid parameter-automation stress;
- state save/restore plus corrupt-state safety check;
- mono/stereo/mismatched-layout checks;
- bypass pass-through and declared-latency check;
- pinned Steinberg official VST3 validator in the Factory PR gate;
- validation report, provenance, SHA-256 manifest and failure quarantine classification.

## MELON decoupling

MELON is intentionally not imported as a Python package. The adapter accepts only the versioned JSON Result Bundle boundary already defined by MELON.

A valid MELON bundle still returns `factory_eligible=false`. CIPI + Incubator must create/approve the Plugin Contract. This allows MELON internals to change without requiring Factory rewrites.

## Commands

From the CIPI repository root:

```bash
python -m juce_factory.factory.cli validate juce_factory/examples/golden_gain.contract.json
python -m juce_factory.factory.cli self-test
python -m juce_factory.factory.cli generate juce_factory/examples/golden_gain.contract.json --output generated/GoldenGain
```

On Windows with a local JUCE checkout:

```powershell
$env:JUCE_SOURCE_DIR = "C:\JUCE"
cmake -S generated/GoldenGain -B generated/GoldenGain/build -G "Visual Studio 18 2026" -A x64
cmake --build generated/GoldenGain/build --config Release --parallel 4
```

Without `JUCE_SOURCE_DIR`, the generated project fetches JUCE tag 9.0.2.

## Current validation meaning

A successful Factory run now requires the generated C++ project to compile, the Factory-owned processor harness to pass its declared matrix, pluginval strictness 5 to pass, and the pinned Steinberg official validator to pass. Failed candidates are uploaded separately as quarantine artifacts and never promoted into the validation-passed artifact path.

These gates establish manufacturing and host-safety evidence only. They do not establish subjective audio quality, product superiority, Cubase approval, or CIPI CONFIRMED knowledge.

### Validation semantics

- `nan_inf` means that finite/silence/automation test inputs must not produce spontaneous NaN/Inf output. It does **not** claim that every product sanitizes deliberately injected NaN/Inf input.
- The Factory stress-tests parameter changes and the external validators exercise host automation. The current Golden template does **not** claim sample-accurate consumption of every intra-block automation point unless a future DSP contract explicitly requires it.
- The Factory-owned executable is intentionally headless and validates Processor/APVTS/DSP behavior. GUI/editor behavior remains covered by the real VST3 plus pluginval/Steinberg validation and later Cubase review.
- Phase 1 contracts that omit the newer Phase 2 validation-matrix fields remain valid and receive the locked default matrix.

## Next gates

Phase 3 should add a versioned Factory Result Bundle and CIPI failure-evidence ingestion, then reproducibility comparison across repeated builds. Queue/batch/resume and UI template expansion should follow only after those evidence/provenance gates are stable.
