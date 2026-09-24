# VO-PREP-SYNC-001 protocol repair

The original 2026-09-25 import manifest was created before the CIPI Research Result manifest contract was rechecked. Its original bytes are preserved as `manifest.imported-original.json`.

This repair changes **protocol metadata only**:

- adds the required Research Result manifest fields;
- adds `environment.json`;
- adds a SHA-256 ledger;
- keeps the existing `metrics.json`, `parameters.json`, and `summary.md` contents unchanged;
- does not change Vo.Prep measurements, product parameters, evidence classes, knowledge status, confidence, current stage, or release state;
- does not add raw client audio.

`acceptance_met: true` means only that this bounded manual evidence-import run completed its import contract. It is **not** a product-quality promotion and does not close the pending subjective/Cubase gates.
