# VOCAL ONE — Formal Research Charter

**Track:** VOCAL_ONE_FORMAL  
**Date:** 2026-11-19  
**Evidence:** HYPOTHESIS for the combined product; no audio/host validation yet.  
**Product repo:** https://github.com/techitechi0331-svg/Vocal-ONE (private)

## Product hypothesis
A vocal-specific VST3 comprising validated, individually bypassable modules can provide a usable near-complete lead-vocal MIX from one instance while permitting expert control, safe routing and repeatable evidence-driven auto configuration.

User-decided boundary: **MIX only**, excluding pitch/timing editing, mastering and cross-instance harmony routing. Q1–Q26 decisions are summarized in the product repo.

## Baseline + acceptance experiment
Use at least three baselines: (B0) simple clean EQ + compressor + de-esser manual chain; (B1) deterministic audio-feature auto-tuning; (B2) Vocal ONE proposed auto-MIX. Before adopting ML, compare (B2+ML) against (B2 deterministic) on held-out licensed vocal recordings.

For each candidate stage collect:
- DSP static/dynamic calibration with declared test units and reproducible seeds;
- worst-case CPU and latency at 44.1/48/96/192 kHz and relevant buffer sizes;
- NaN, silence, extreme-level, denormal, bypass, automation and state-recall tests;
- exact source/commit, API/parameter contract and license/provenance;
- level-matched A/B with sufficient dry vocal diversity, plus counterexamples;
- effects ablation to prove benefit and prevent destructive double-processing.

Do not claim that an adaptive system is superior because its settings are more complex. Preserve neutral/dry fallback.

## Module adoption decisions
| Module | Source research | Adoption |
|---|---|---|
| Event preparation | Vo.Prep | Review source and regression tests |
| Transparent compression | Vocal Surface / VoPriPro | Compare against clean baseline and avoid redundant gain loops |
| FET compression | 76blackCompressor | Wait for production-rate curve calibration and host evidence |
| Optical compression | VL2A / LA-2A reference research | Provisional; require transfer and dynamic accuracy |
| Vocal riding | vocal_rider | Research unfinished; test gain trajectories and pumping/masking |
| Doubling and width | Vocal One-Knob Doubler | Core tests exist; Cubase/A-B pending |
| Harmonic color | 610 | Provisional, not hardware-exact; require alias/THD/IMD tests |
| Resonance suppression | Vocal_resonance | Prior NO-GO evidence; do not productize until detector recall/false triggers pass |
| EQ, dynamic EQ, de-esser, delay, reverb, graph | CIPI / new development | Define portable DSP contracts and measure separately |

## CIPI / MELON / Factory governance
- CIPI reviews evidence, failures, decision lineage, architecture and release gates.
- MELON explores bounded alternatives only; experiment outcomes are not product permissions.
- JUCE Factory generates/tests approved plugin contracts; Factory PASS is not Cubase or audio approval.
- Only explicitly authorized research jobs may dispatch cross-repo workflows. No secret keys/recordings in repos.
- Follow RULES/DSP_RESEARCH_RULES.md, RULES/EVIDENCE_POLICY.md, RULES/NO_WAIT_WORK_STEALING.md, docs/VALIDATION_GATES.md.
- Don't modify existing product repositories automatically to import DSP. Review license, provenance and tests first.

## First research tasks
1. Inventory exact reusable blocks, APIs, license status and known failure boundaries without copying the code blindly.
2. Define fixed input/output, sidechain, state, latency, sample-rate and realtime safety contracts.
3. Create a minimal clean baseline with repeatable DSP tests and a small audio-review protocol.
4. Quantify detector conflicts, stereo phase/mono safety, oversampling latency and mode switching.
5. Review the full findings and lock only the justified product parameters.

Research registration **does not** approve the product, start a runner, mark Human Gates passed, or certify quality.
