# CIPI Factory evidence

JUCE Factory evidence is stored under:

`research/factory_evidence/<plugin_id>/<source_bundle_hash>.json`

These records are transport-safe **MEASURED manufacturing evidence only**.

A `VALIDATION_PASS` record means the candidate passed the declared JUCE Factory
manufacturing/host-safety gates for that exact Contract and Factory revision.

A `QUARANTINED` record means the candidate failed a Factory technical gate under
the recorded conditions. It does not by itself reject the DSP or product concept.

Factory evidence never grants:

- CIPI knowledge promotion;
- final product decisions;
- release authority;
- Cubase confirmation;
- listening/audio-quality confirmation.

Raw vocal/audio material must never be persisted in Factory evidence.
