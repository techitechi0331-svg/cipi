# CIPI Plugin Incubator

The Incubator receives reviewed Research Proposals and decides whether a product opportunity should be:

- `REJECT`
- `ITERATE`
- `MERGE_EXISTING`
- `INCUBATE`
- `ARCHIVE`

It never mutates an existing product repository.

A proposal must pass overlap and measurement checks before an isolated prototype is allowed. Experimental prototypes are research artifacts only; official repo creation, product naming, release and Cubase approval remain human/assistant gates.

## Evidence-gated INCUBATE

Overlap is not a permanent dead end. A candidate may receive a **non-final** automated `INCUBATE` proposal only after a product-discrimination evidence record proves all declared gates:

- baseline improvement;
- disjoint holdout;
- regression safety;
- CPU;
- latency;
- independent advantage over merging into existing products;
- explicit negative-knowledge review;
- no raw audio persistence.

Only then may an allowlisted isolated DSP prototype run. This still does not authorize an official repository, VST3 release, product naming, Cubase approval or final product adoption.


## Factory handoff

An automated `INCUBATE` decision still cannot create or build a production plug-in.

Before a JUCE Factory Plugin Contract candidate can be emitted, CIPI additionally
requires a Manufacturing Review under `research/incubator/manufacturing_reviews/`.

The review must be authored as `HUMAN` or `ASSISTANT_REVIEW`, reference the exact
INCUBATE decision and product evidence, and contain a Plugin Contract that passes
the Factory validator. Automation cannot grant this review to itself.

The handoff emits only a `CONTRACT_CANDIDATE` plus a provenance receipt. The receipt
pins the SHA-256 of all source records and explicitly keeps Factory build authority,
final product decision, release authority, Cubase confirmation and listening
confirmation false.
