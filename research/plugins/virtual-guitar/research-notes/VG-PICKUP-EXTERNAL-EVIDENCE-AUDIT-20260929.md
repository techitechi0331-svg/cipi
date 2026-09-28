# Virtual Guitar Pickup / Cable / DI / Amp Input External Evidence Audit - 2026-09-29

## Decision
Proceed with public external evidence before asking for user-owned hardware.

Safe order:
1. manufacturer topology/specification facts;
2. peer-reviewed competing-model evidence;
3. licensed real DI for A/B, robustness and falsification;
4. restricted/noncommercial datasets kept outside product-linked fitting;
5. only after provenance and file-hash gates, dispatch MELON real-data model discrimination.

This audit does not claim that a pickup model, cable model, amp input, or STRAT_STYLE product is complete.

## Registered evidence
- Fender official SSS wiring and official SSS/HSS service-manual index.
- Mogami W2524: 0.033 ohm/m inner-conductor DCR, 130 pF/m capacitance, 0.2 uH/m inductance.
- Mogami W3368: 0.033 ohm/m inner-conductor DCR, 70 pF/m capacitance, 0.4 uH/m inductance.
- Canare GS-6: 1.8 ohm/100m conductor DCR, 2.5 ohm/100m shield DCR, 160 pF/m capacitance.
- Focusrite Scarlett 3rd Gen instrument input: 1.5 Mohm Reference Hi-Z candidate.
- Seymour Duncan SSL-1 published sanity anchor: 6.5 kohm DCR, 10 kHz resonant peak, Alnico V rods.
- Paiva/Pakarinen/Valimaki pickup-position, sensitivity-width, resonance and magnetic-nonlinearity model evidence.
- Paiva/Penttinen cable/load interaction evidence.
- Kotiuga distributed-capacitance transient counter-hypothesis.

## Real DI decision
Guitar-TECHS is the preferred first public real-DI corpus candidate because it contains direct input, amp-mic audio, synchronized MIDI and multiple players/guitars. The authors project page explicitly declares all data CC BY 4.0. The current rendered Zenodo Rights section does not expose a concrete license value in the captured page, so audio ingest remains gated until an authoritative license statement plus attribution manifest is captured.
It remains confounded by guitar, pickup selection, splitter, interface and player, so it is not isolated pickup transfer truth.
The project warns of up to about 100 ms cross-signal alignment error; alignment-sensitive comparisons must correct or explicitly tolerate that.

Fraunhofer IDMT-SMT-Guitar is useful only as optional noncommercial/evaluation evidence under its declared CC BY-NC-ND 4.0 terms. Keep it outside product-linked fitting and commercial parameter optimization.

## Still missing before final model selection
- real pickup frequency and phase measurements;
- real pickup transient measurements;
- pickup geometry/aperture provenance;
- exact cable/splitter/load conditions where available;
- real amp-input network evidence;
- perceptual error budget;
- out-of-sample A/B across multiple notes, strings and pickup states.

Unknown conditions remain UNKNOWN. Do not invent them.

## Next safe sequence
1. Review the corpus and preflight gate.
2. Run metadata/rights/provenance preflight only.
3. Prefer Guitar-TECHS as the first real-DI ingest candidate.
4. Build a per-file hash/provenance manifest before any model use.
5. Keep Fraunhofer NC/ND material outside product-linked fitting.
6. Only then create/enable the MELON real-data discrimination adapter.
7. Compare low-order vs higher-order and point vs finite-aperture candidates on real evidence.
8. Product integration remains a separate later gate.

## Authority
CIPI owns evidence/provenance/rights/continuation. MELON may only run bounded discrimination/falsification. Product repository writes, final tone adoption and release are not authorized by this stage.
