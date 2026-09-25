# CIPI Autonomous Research Architect

The architect is a **separate bounded automation layer**. It does not replace the existing Research Worker.

## Responsibilities

1. Scan evidence-bearing CIPI paths against a reviewed topic catalog.
2. Create deterministic Research Gap and Research Proposal candidates.
3. Run only explicitly allowlisted pilot adapters.
4. Emit normal CIPI research-run / knowledge-candidate / decision evidence for a pilot.
5. Hand unknown topics to `NEEDS_ADAPTER` instead of generating arbitrary executable code.
6. Convert one unresolved `NEEDS_ADAPTER` proposal at a time into a non-executable Adapter Candidate specification for review.
7. Forward product-relevant proposals to the Plugin Incubator.

## Safety

- no arbitrary shell from YAML;
- no dynamic package or code download;
- no production plug-in mutation;
- no automatic Adapter Registry edit;
- no automatic PROMOTE/CONFIRMED;
- no raw client audio;
- no official repository or release creation.

A fully new topic can therefore be **discovered and specified automatically** even when execution cannot yet be automated. The missing adapter becomes an explicit research artifact rather than a silent blocker.


## Adapter Candidate bridge

A `NEEDS_ADAPTER` proposal is not a dead end. The architect may generate an append-only, non-executable Adapter Candidate under `research/architect/adapter_candidates/`.

The candidate fixes the research question, baseline, variants, metrics, acceptance/rejection rules, bounded operations, dependency/network policy, timeout and forbidden operations before implementation.

Automation may never mark that candidate executable or add it to `automation/adapter_registry.yaml`. Implementation and registry promotion require a separate reviewed change that passes the normal gates.
