# Black76 actual-VST3 real-vocal snapshot — packaging revision 2

## Purpose

Append-only repair of the Snapshot-001 evidence-integrity failure.

The underlying Black76 VST3 render metrics, product commit, source artifact, test material and test conditions are unchanged. Only the CIPI evidence packaging is revised so that the SHA256 ledger describes the exact bytes committed in this directory.

## MEASURED payload retained

Two public/CC0-scope source clips, three modes, 48 kHz, actual built VST3:

- Attack-OFF color working point;
- moderate 4:1 compression;
- stress 20:1 compression.

Snapshot-001 behavior findings are retained unchanged:
- clipped samples: 0;
- non-finite samples: 0;
- latency: 6 samples;
- maximum output peak: 0.504726;
- maximum sample-to-sample step: 0.284703;
- Attack-OFF gain: -0.300513 dB and -0.00462832 dB.

## Packaging correction

Snapshot-001 used the source-artifact CSV hash after the CIPI copy had line endings normalized. The earlier failed gate is preserved.

Snapshot-002 computes the metrics hash from the exact LF-normalized bytes committed here.

No raw audio is stored in CIPI.

## Scope limit

This repairs evidence integrity only. It does not establish subjective preference, exact Rev-E ratio fidelity, vintage-hardware equivalence or Cubase Pro 14 host validation.
