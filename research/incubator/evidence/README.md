# Plugin Incubator product-discrimination evidence

A plug-in proposal that overlaps an existing product may not advance merely because its research hypothesis passed.

To receive a non-final automated `INCUBATE` proposal, a reviewed measurement adapter must write a YAML evidence record under:

`research/incubator/evidence/<PLUGIN-PROPOSAL-ID>/<evidence-id>.yaml`

Required boolean gates:

- `baseline_improvement_pass`
- `holdout_pass`
- `regression_pass`
- `cpu_pass`
- `latency_pass`
- `overlap_advantage_pass`
- `negative_knowledge_reviewed`
- `raw_audio_persisted: false`

Passing these gates authorizes only an isolated experimental DSP prototype. It does not create an official repository, approve a VST3 release, close listening/Cubase gates or make a final product decision.
