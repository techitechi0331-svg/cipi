# SM57 Reference Inventory — 2026-09-28

## Purpose

Prepare the first post-Foundation Mic Simulator reference track without reopening solved Foundation work or turning manufacturer specifications into hardware-fidelity evidence.

## Existing evidence to preserve

- `MIC-SIM-FOUNDATION-001` completed deterministic research plumbing and terminated with duplicate-only convergence.
- Independent `mic_simulator` repository ownership is established.
- CIPI/MELON cross-repo dispatch, evidence intake, semantic dedup and bounded budgets are operational.
- Virtual Guitar integration remains versioned, optional and product-gated.

## SM57 SOURCE_FACT baseline

Primary manufacturer evidence is the Shure SM57 user guide/product page. The reference profile records dynamic moving-coil type, 40 Hz–15 kHz stated response, cardioid polar pattern, 310 ohm actual output impedance, -56.0 dBV/Pa sensitivity (1.6 mV/Pa at 1 kHz), and the documented close-distance proximity-effect behavior.

These are SOURCE_FACTS. They are not measured unit-specific transfer functions and are not proof of hardware fidelity.

## Explicitly unresolved

- digitized magnitude curve with uncertainty
- frequency-dependent off-axis/polar transfer
- phase response and group delay
- transient behavior
- distance transfer beyond the manufacturer placement/proximity statements
- level dependency
- unit-to-unit variation
- controlled reference audio
- listening and Cubase host confirmation

## Do not reopen

- MIC Foundation canary/runner connectivity
- independent repository ownership
- generic Result Bundle plumbing
- Foundation synthetic identifiability
- optional/versioned Virtual Guitar integration policy

## Rejected shortcuts

- EQ-only = SM57 fidelity
- minimum/maximum frequency range = exact transfer function
- derive phase from manufacturer magnitude plot without evidence
- treat synthetic geometry as measured SM57 geometry
- treat CI/build success as listening/fidelity validation
- automatic product adoption/release
