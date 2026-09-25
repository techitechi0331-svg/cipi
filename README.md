# CIPI Plugin Engineering Knowledge Base

CIPI is a research-first audio DSP repository for building vocal-oriented VST3 plug-ins.

The project follows this loop:

**research -> verification -> numerical specification -> implementation -> measurement -> level-matched listening -> revision -> VST3 host verification -> final review**

## Goals

- Convert audio-engineering ideas into signal flow, equations, initial constants, implementation plans, and measurable acceptance criteria.
- Keep reusable DSP blocks independent from product-specific code.
- Track evidence quality and unresolved assumptions.
- Build experimental plug-ins while the knowledge base grows.
- Target JUCE 9 / C++20 / VST3, with Cubase Pro 14 as the primary real-host validation target.

## No-Wait orchestration

CIPI uses a No-Wait / Work-Stealing rule for CI and external dependencies. A GitHub Actions run, runner, external tool, listening gate, or host check blocks only the task that depends on it; independent READY work should continue instead of ending the work pass.

The canonical rule is `RULES/NO_WAIT_WORK_STEALING.md`. Autonomous queue selection skips explicit blockers, unresolved `depends_on_jobs`, and already-claimed research-bot branches, then steals the next READY job. Successful worker completion can chain into the next READY job through the No-Wait Queue Orchestrator.

## Initial experimental plug-ins

- **CIPI VoxLevel** — dual-detector vocal leveler / compressor.
- **CIPI AirGuard** — split-band adaptive vocal de-esser.
- **CIPI Density** — oversampled parallel nonlinear density processor.

These are R&D prototypes, not yet release-certified products.

## Evidence levels

- **E5 Confirmed** — primary source or direct measurement.
- **E4 Strong** — multiple high-quality sources agree.
- **E3 Probable** — strong engineering basis but incomplete confirmation.
- **E2 Hypothesis** — plausible and testable, not yet validated.
- **E1 Anecdotal** — observation/user report only.
