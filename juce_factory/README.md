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

## Implemented

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
- Factory-owned pure C++ DSP core harness;
- sample-rate matrix: 44.1 / 48 / 88.2 / 96 / 192 kHz;
- regular and irregular block-size coverage;
- rapid-automation finite-output test;
- silence / NaN / Inf defense checks;
- block-segmentation invariance regression test;
- pinned Steinberg official VST3 validator in addition to pluginval.

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

## Validation layers

The generated Golden plug-in is checked at multiple layers:

1. Python Contract/Generator tests.
2. Factory-owned deterministic DSP matrix built with the generated project.
3. VST3 Release build.
4. External pluginval strictness 5, which exercises plug-in/host behavior including parameters and state.
5. Pinned Steinberg official VST3 validator.

A technical PASS still does not grant release or CIPI knowledge-promotion authority.

## Next gates

Phase 3 should add a versioned Factory Result Bundle, structured failure classification/evidence, and CIPI ingestion. Queue/batch/resume and UI-template expansion come after the result/evidence boundary is stable.
