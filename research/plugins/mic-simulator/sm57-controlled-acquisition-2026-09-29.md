# SM57 Controlled Reference Acquisition Gate — 2026-09-29

## Status

The manufacturer/source-fact inventory track `MIC-SIM-REFERENCE-SM57-001` completed successfully and terminated at `HUMAN_GATE` with `REFERENCE_SOURCE_FACT_INVENTORY_COMPLETE`.

The remaining gap is not an orchestration failure. It is a missing controlled measurement dataset.

## Evidence boundary

### SOURCE_FACT
- Shure SM57 official specifications and published response/polar material remain source facts.
- These facts do not constitute a complete measured unit transfer function.

### CANDIDATE external measurements
1. Liquid Instruments Moku:Go / LabVIEW SM57 characterization:
   - URL: https://liquidinstruments.com/blog/characterizing-microphone-frequency-response-and-directionality-with-labview-and-the-mokugo-frequency-response-analyzer/
   - Controlled setup described with SM57 as DUT, Oktava MK-12-01 reference microphone, Event PS6 loudspeaker and Apogee Duet preamplifier/interface.
   - Swept measurement described from 35 Hz to 20 kHz.
   - Manual polar measurements described.
   - Raw numerical dataset and reuse permission were not verified.
   - Classification: CANDIDATE, not MEASURED input for model fitting.

2. Scott Hawley Polar Pattern Plotter:
   - URL: https://www.scotthawley.com/ppp/
   - Demonstrates SM57 polar measurement and CSV-capable measurement tooling.
   - Published reusable raw SM57 dataset and reuse permission were not verified.
   - Classification: CANDIDATE.

## Implemented acquisition contract

Mic Simulator now stages a controlled-acquisition validator which requires:
- exact acquisition identity;
- source kind;
- MEASURED evidence class;
- provenance;
- explicit research-use permission;
- room/source/preamp/interface/gain/sample-rate/distance/angle/reference-unit controls;
- file SHA-256;
- capture format validation;
- explicit authority boundaries.

The validator supports independent dimensions:
- frequency response;
- phase/group delay;
- impulse/transient;
- polar/off-axis;
- proximity/distance;
- level dependency.

A phase/group-delay + impulse/transient pair is the first modeling-readiness milestone. Full hardware-fidelity remains blocked until the wider dimension set is available and validated.

## Do not do

- Do not digitize web graph images and silently promote them to raw MEASURED reference data.
- Do not infer phase as fact from magnitude response.
- Do not claim SM57 hardware parity from manufacturer curves.
- Do not redistribute third-party captures without explicit permission.
- Do not auto-promote a measured dataset to product adoption or release.

## Resume condition

Enable `MIC-SIM-MEASURED-SM57-001` only when at least one controlled acquisition manifest passes the Mic Simulator acquisition validator and has explicit research-use permission.

The first preferred dataset contains both:
- phase/group-delay data; and
- impulse/transient data.

Partial controlled measurements may be registered as MEASURED evidence without claiming full fidelity.
