# Vocal ONE — CIPI autonomous STEP 1 P0 lane (2026-11-20)

## Execution
- CIPI is the sole research-job, Evidence/Decision, budget and Global-DAG authority.
- MELON main contains dedicated \`melon/vocal_one_research.py\` (commit \`8e6e05c3147e3135c16e52c51f3000687b165f43\`), routed from \`integration/cipi/research_driver.py\` for \`VOCAL-ONE-\` tracks. The test-only adapter validates synthetic fade envelopes.
- The active bridge registration is \`research/autonomous_bridge/tracks/VOCAL-ONE-P0-BYPASS-001.yaml\`. CIPI's existing Global DAG (every five minutes) bootstraps its first bounded job, queues the reviewed MELON research workflow and ingests the result through existing evidence/continuation handlers. This is runner-availability and valid-token dependent; the registration itself is not evidence of dispatch.
- Product source remains **only** in \`techitechi0331-svg/Vocal-ONE\`. Its existing foundation CI is already monitored with \`monitor: true\` and \`dispatch: false\` in \`automation/cross_repo/registry.yaml\`. Do not run repeatedly to regenerate the private draft build snapshot on the same commit.
- The product P0 master bypass implementation remains a separate PR #1; its Linux and Windows CI succeeded. CIPI must not merge it, change source code, or mark it production approved.

## Authority and honest evidence labels
The MELON candidate tests do **not** run the actual Vocal ONE VST3, infer musical quality, use real vocals, or prove Cubase automation/state behavior. Record them only as model-conditional synthetic measurements and negative/counterexample evidence. Human gates stay explicit for host, real-vocal listening, product adoption and release.

## Next independent READY engineering tasks (product repo)
1. Run pluginval and Steinberg Validator in a reviewed CI workflow with pinned versions and reproducible logs.
2. Add JUCE processor state roundtrip, automation, host bypass and offline/realtime parity tests; do not claim passing until observed.
3. Extend common DSP interfaces and bounded parameter/latency testing without external compressor/reverb dependencies.
4. Add measured EQ and De-esser baselines only after stage-specific acceptance gates.

Cross-Repo and Autonomous Research Bridge do not generate arbitrary product implementation patches. Implementing ongoing coding autonomously requires a separately reviewed, narrowly scoped product-change mechanism or executor; do not misreport this initial research registration as that capability.
