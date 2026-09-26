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


## Factory Result Bundle and CIPI evidence preview

Factory 0.2 adds a versioned Result Bundle after technical validation.

The bundle records:

- the semantic Plugin Contract SHA-256;
- a deterministic generated-source tree SHA-256;
- the source branch revision;
- the exact validation checkout/merge revision;
- the validation base revision;
- Factory/JUCE versions and declared validation matrix;
- mandatory validator outcomes;
- hashes of promoted VST3 files;
- a self-hash for tamper detection.

The workflow also creates a bounded CIPI evidence **preview**. It is not written to
canonical CIPI knowledge automatically. Both PASS and quarantine outcomes remain
`MEASURED` manufacturing/host-safety evidence only.

Factory Result Bundles and evidence records explicitly carry no authority for:

- CIPI knowledge promotion;
- a final product decision;
- product release;
- Cubase confirmation;
- listening or subjective audio-quality approval.

A quarantined result records the technical failure class and partial validator
outcomes. It does not automatically reject the DSP or product concept.


## Reproducibility probe

The next-stage comparator consumes two validated Factory Result Bundles and compares
their recorded inputs plus promoted VST3 file hashes.

Current classifications are observational:

- `ARTIFACT_HASH_MATCH`
- `ARTIFACT_HASH_DIFF`
- `NOT_COMPARABLE_SOURCE_DIFF`
- `NOT_COMPARABLE_RECORDED_CONTEXT_DIFF`

A hash match does **not** yet prove bit-reproducible builds. Factory Result Bundle v1
does not fully capture compiler, linker, Windows SDK and hosted-runner image identity.
A hash difference is retained as MEASURED investigation evidence and is not an
automatic product/release failure.


## Authorized build boundary

Factory 0.2 does not accept an Incubator `CONTRACT_CANDIDATE` as build permission.

A separate Factory Build Authorization must bind the exact Contract Candidate and
handoff receipt and set only `factory_build_authorized=true`. The authorization
cannot carry product release, Cubase or listening authority.

The generic candidate-build workflow consumes both the Plugin Contract and its Build
Authorization and reverifies pinned source hashes before generation/build.


## Generic authorized candidate build

The `juce-factory-authorized-build` workflow scans only
`research/incubator/factory_build_requests/`.

Every request is revalidated immediately before generation. The scan is bounded to
8 authorized requests and the Windows build matrix is limited to 2 parallel jobs.

For each authorized request, Factory runs:

1. Build Authorization + source provenance revalidation;
2. Plugin Contract semantic-hash verification;
3. deterministic JUCE project generation;
4. Release VST3 build;
5. Factory-owned DSP/state validation matrix;
6. pluginval strictness 5;
7. Steinberg official VST3 validator;
8. Factory Result Bundle + CIPI evidence preview;
9. Authorized Build Result Binding tying the result bundle to the exact
   `authorization_hash`.

Successful output remains a **validation-passed candidate artifact**, not a release.
Failed builds are quarantined and, when a Factory manifest exists, receive their own
quarantine Result Bundle and authorization/result binding.

The workflow never grants final product decision, release authority, Cubase
confirmation or listening approval.


## Certified DSP Module Registry

Factory 0.3 replaces the hard-coded DSP-template allowlist with a canonical certified
DSP Module Registry.

The Registry records, for each module:

- module and implementation IDs;
- Factory certification/build eligibility;
- supported Plugin Contract versions;
- exact required parameter IDs;
- supported mono/stereo layouts;
- validation profile;
- immutable source-revision requirement;
- `product_release_authority=false`.

Plugin Contract validation reads this Registry directly. The generator performs a
second implementation check, so adding a Registry entry alone cannot execute an
unknown DSP implementation.

The generated Factory manifest pins both the complete Registry SHA-256 and the
selected module-spec SHA-256. Registry certification is manufacturing eligibility
only; it is not a subjective audio-quality or release verdict.
