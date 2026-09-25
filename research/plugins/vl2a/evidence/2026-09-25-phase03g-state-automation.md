# VL2A Phase03F/03G + State/Automation evidence — 2026-09-25

## Status

- Phase03F residual-HP structure: **REJECTED**
- Phase03G minimal amount trim: **G054 SELECTED**
- State / automation compatibility audit: **PASS**
- Final release: still pending full final validation + Cubase host gate

---

## Phase03F — residual modulation HP

### Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Branch:
- `integration/vl2a-v060-rc2`

Workflow:
- run `36179913385`
- source SHA `ee8343897231b08675f90c597c896f83255850ff`
- artifact id `10883634465`
- digest:
  `sha256:b0e205b05d61120dd62f90c011ede06fdf9e726cd4fb0caa4044eca189fbd044`

### MEASURED result

Simple baseline:
- 8 ms optical mean tau
- no residual HP
- amount 0.055

Max real-vocal band shift:
- F0 / HP off: **0.768085 dB**
- F25: **0.809483 dB**
- F50: **0.850192 dB**
- F75: **0.891880 dB**

The controlling row remained forte / 20..80 Hz.

Active-GR remained healthy:
- F0 1 kHz THD ~0.782401%
- F25 ~0.782534%
- F50 ~0.782541%
- F75 ~0.782420%
- H3 dominant in all candidates

63 Hz THD:
- F0 ~1.2990%
- F25 ~1.3890%
- F50 ~1.4216%
- F75 ~1.4064%

Release / sample-rate / PR0 / finite gates remained valid.

### Decision

Residual HP on the optical-ripple coloration path is **REJECTED**.
It worsens the strict real-vocal low-band metric.

---

## Phase03G — minimal coloration amount trim

### Provenance

Workflow:
- run `36192420105`
- source SHA `82f338246fcf340c2167c94f35cfd3740218b1e4`
- artifact id `10888234709`
- digest:
  `sha256:7143b0a1588de18a387efa3781de2be11f2f518e10975aac2b35e804d62cff0e`

### Candidate set

All candidates:
- optical mean tau = 8 ms
- residual HP = OFF
- all compressor control/DSP topology unchanged

Coloration amount:
- G055 = 0.0550
- G054 = 0.0540
- G0535 = 0.0535
- G053 = 0.0530

### Strict selection result

- G055:
  - max band shift ~0.768085 dB
  - 1 kHz THD ~0.782401%
  - FAIL color gate

- **G054**:
  - max band shift **~0.742962 dB**
  - 1 kHz THD **~0.767707%**
  - 63 Hz THD **~1.280933%**
  - H3 **~-42.393 dBc**
  - PASS all gates

- G0535:
  - max band shift ~0.730678 dB
  - 1 kHz THD ~0.760359%
  - PASS but lower coloration than necessary

- G053:
  - max band shift ~0.718259 dB
  - 1 kHz THD ~0.753010%
  - PASS but lower coloration than necessary

Selection preference was the highest coloration amount that passes all gates.

### SELECTED

**G054 / amount = 0.0540**

Detailed G054 active-GR THD:
- 63 Hz: ~1.280933%
- 125 Hz: ~1.129801%
- 250 Hz: ~1.087031%
- 500 Hz: ~1.006710%
- 1 kHz: ~0.767707%

G054 control:
- matched release retained at 60 ms: ~0.565533
- sample-rate GR spread: ~0.04503 dB
- PR0 THD: ~0.011568%
- stress finite
- fixed-GR COMP/LIMIT rows finite

### Product integration decision

Final optical-coloration product setting:
- optical mean tau: **8 ms**
- optical amount: **0.054**
- residual HP: **none**
- residual LF blend: **none**

Rejected research-only HP/LF branches are not required in the final production path.

---

## State / Automation compatibility

### Provenance

Workflow:
- run `36193405591`
- source SHA `90450b1760b5813caa0e2db6eaf8958c45b64b57`
- artifact id `10888934402`
- digest:
  `sha256:b375458c1d49fef9f2ee0e53f9f8a75abe296449ef9dcb8df7476cf45d5b036e`

### MEASURED

- max automation equivalence delta:
  **~0.008854 dB**
- max state restore delta:
  **0.000000 dB**
- max normalized roundtrip delta:
  **~0.000000060**
- legacy normalized default mapping:
  `45 -> ~0.704097748`
- new direct Gain range endpoints:
  `0 -> -18 dB`
  `1 -> +18 dB`

Result:
- **PASS**

### Decision

Parameter/state migration logic and automation-equivalence test pass the current
compatibility gate.

Real Cubase automation/project recall remains part of the final host-only gate.

---

## Current release status

Ready for complete final validation with:
- Peak v8
- Phase03G optical 8 ms / 0.054
- accurate GR peak-hold meter
- state/automation compatibility PASS
- code-level PDC PASS
- CPU safety PASS

Still required:
1. full final matched-GR regression
2. final PR50 real-vocal regression
3. final level-matched color A/B
4. final VST3 Release build
5. pluginval strictness 10
6. source-state audit
7. final CIPI contradiction review
8. Cubase Pro 14 real-host gate
