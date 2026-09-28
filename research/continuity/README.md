# CIPI Continuity

Continuity is generated, rebuildable context for safe re-entry from a fresh chat or other
client. It has `CONTEXT_RECONSTRUCTION_ONLY` authority.

Generated layout:

```text
research/continuity/
  index.json
  global/current.json
  projects/<project-id>/current.json
  projects/<project-id>/HANDOFF.md
  schemas/*.schema.json
```

The project list comes from `automation/cross_repo/registry.yaml`.

`current.json` is the machine-readable L0 context. `HANDOFF.md` is rendered from the same
snapshot and must not be edited as an independent source of truth.

If product-repository head resolution is unavailable, the snapshot is deliberately
`STALE`; a client must refresh the product ref before autonomous continuation.

See `RULES/CONTINUITY_LAYER.md`.
