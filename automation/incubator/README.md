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
