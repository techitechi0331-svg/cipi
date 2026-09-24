# CIPI Research Charter v1.0

## Mission

CIPI is not a bookmark collection. A topic is mature only when it can be translated into a practical plug-in design.

For important mechanisms, research should converge toward: purpose and audible goal; signal flow; equations; parameter ranges and constants; sample-rate behaviour; stability/failure modes; CPU/latency; measurement; listening tests; and JUCE/VST3 implementation notes.

## Formal development rule

Research -> verification -> numerical specification -> implementation -> measurement -> level-matched listening -> correction -> VST3 host check -> final verification.

A stage returns to an earlier stage whenever a material contradiction or measurement failure is found.

## Precision gate

Before promoting a conclusion, check evidence sufficiency, contradictions, fact/inference/hypothesis separation, mathematical consistency, realtime feasibility, measurable acceptance criteria, vocal relevance, compatibility risk, and unresolved items.

## Source policy

Prefer primary technical sources, standards, peer-reviewed work, official SDK documentation, service documentation, patents, datasheets, and reproducible measurements.

Product-specific claims must never be presented as internal facts when implementation is proprietary and undocumented.

## Design principle

Extract reusable patterns. A study of a classic compressor should yield reusable knowledge about detector placement, gain computers, ballistics, nonlinearities, calibration, and measurement—not only a description of that product.
