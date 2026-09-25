# CIPI Autonomous Research Architect

The architect is a **separate bounded automation layer**. It does not replace the existing Research Worker.

## Responsibilities

1. Scan evidence-bearing CIPI paths against a reviewed topic catalog.
2. Create deterministic Research Gap and Research Proposal candidates.
3. Run only explicitly allowlisted pilot adapters.
4. Emit normal CIPI research-run / knowledge-candidate / decision evidence for a pilot.
5. Hand unknown topics to `NEEDS_ADAPTER` instead of generating arbitrary executable code.
6. Forward product-relevant proposals to the Plugin Incubator.

## Safety

- no arbitrary shell from YAML;
- no dynamic package or code download;
- no production plug-in mutation;
- no automatic Adapter Registry edit;
- no automatic PROMOTE/CONFIRMED;
- no raw client audio;
- no official repository or release creation.

A fully new topic can therefore be **discovered and specified automatically** even when execution cannot yet be automated. The missing adapter becomes an explicit research artifact rather than a silent blocker.
