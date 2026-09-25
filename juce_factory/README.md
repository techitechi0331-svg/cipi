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

## Phase 1 implemented here

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
- CI self-test + Windows VST3 build + external pluginval.

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

## Next gates

Phase 2 should add Factory-owned DSP/state/automation/sample-rate/block-size tests and Steinberg-validator integration for generated candidates. Phase 3 should add provenance/result bundles and CIPI failure-evidence ingestion. Queue/batch/resume and UI template expansion come only after manufacturing determinism is stable.
