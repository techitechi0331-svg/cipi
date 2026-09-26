# VL2A Circuit Lab — Baseline inventory and fidelity audit

Date: 2026-09-26
Status: RESEARCH / no product integration authorized
Product repo audited: techitechi0331-svg/VocalPrepComp
Product branch audited: integration/vl2a-v060-rc2
CIPI base: latest main at branch creation
Evidence policy: SOURCE_FACT / MEASURED / INFERRED / HYPOTHESIS / REJECTED

## Protection boundary

This Circuit Lab branch does not modify the VL2A product branch.

Protected product behavior includes:
- Peak Reduction v8 operating-point behavior.
- PR50 / approximately -18 dBFS real-vocal target near 5–7 dB GR.
- Phase03G optical mean tau 8 ms / amount 0.054 / residual HP off.
- program-dependent optical release.
- COMP/LIMIT separation.
- factory-flat sidechain default.
- post-T4 user Gain / detector independence.
- retained Phase01H line-amplifier architecture.
- existing state / automation compatibility.
- measured sample-rate, latency and CPU behavior.

The chat instruction also names strict pluginval 10 PASS as a protected current baseline. The latest CIPI evidence located during this audit still listed strict pluginval 10 and Cubase as pending at that evidence snapshot, so Circuit Lab treats pluginval-10 as a REQUIRED REGRESSION GATE and does not independently reclassify it as MEASURED here.

## Current implementation inventory

### Input transformer
Implementation: TransformerModel, prepared as 12 Hz low-cut / colour=0.12.
Current mechanism:
- one-pole high-pass;
- 25 ms leaky "magnetisation" state;
- tanh saturation / blend.

Classification: HEURISTIC.
Important missing physical variables:
- HA-100X nominal impedance transformation;
- actual winding ratio;
- primary/secondary DCR;
- magnetizing inductance;
- leakage inductance;
- parasitic capacitance;
- core-loss branch;
- source/load interaction;
- explicit loading by the R5/R6/R7/Gain/T4 network.

Decision: highest-priority research gap.

### T4 audio attenuation / CdS state
Implementation: T4CellModel.
Current mechanism:
- fast attack/release state;
- medium and long exposure-history states;
- explicit CdS-like resistance mapping;
- resistor-divider audio attenuation.

Classification: REDUCED PHYSICAL + BEHAVIORAL HYBRID.
Strength: strong program-dependency and stable product behavior.
Gap: EL panel and CdS are not yet separate causal device models.

### Sidechain 12AX7
Implementation: generic TubeAmplifierModel reused as sidechainTube.
Classification: BEHAVIORAL / HEURISTIC.
Gap: no sidechain-specific 12AX7 operating point, plate/cathode network, load, or R37/6AQ5 interaction model.

### 6AQ5 EL driver
Implementation: not represented as a dedicated 6AQ5 stage. Its behavior is compressed into generic sidechain tube processing plus threshold/power-law excitation.
Classification: UNMODELED AS A DEVICE / HEURISTIC AS A TRANSFER.
Gap: no operating point, output impedance, EL-panel load, asymmetry, clipping or frequency-dependent drive model.

### EL panel
Implementation: implicit in the sidechain-excitation to T4-illumination mapping.
Classification: BEHAVIORAL.
Gap: voltage-to-light transfer and frequency/loading behavior are not separated.

### Main 12AX7 line-amplifier stage
Implementation: Phase01H reduced closed-loop polynomial derived from an approved offline reference.
Classification: REDUCED PHYSICAL MODEL.
Strength: removed the historical derivative discontinuity / low-level THD floor and passed compiled/regression measurements.
Gap: reduced model does not expose all physical nodes at runtime.

### 12BH7 cathode follower
Implementation: load-aware source-resistance trajectory inside LineAmplifierDSP.
Classification: REDUCED PHYSICAL MODEL.
Strength: load and source-impedance behavior are represented.
Gap: full device-current states are reduced away.

### UTC A-24 output transformer
Implementation: linear load-aware architecture in LineAmplifierDSP.
Known code anchors include primary DCR, nominal proxy ratio, reflected load, secondary series fit seed, and explicit low/high-frequency poles.
Classification: REDUCED PHYSICAL / LINEAR.
Strength: output impedance and load behavior are measured and stable.
Gap: A-24-specific nonlinear magnetic constants remain unsupported; hysteresis is intentionally absent.

### Main global feedback
Implementation: reduced into the approved Phase01H closed-loop transfer. The source documents a 20 dB feedback target and the offline relation used for the fitted closed-loop reference.
Classification: REDUCED CLOSED-LOOP MODEL.
Strength: stable and efficient.
Gap: no realtime implicit loop; dynamic loop/stability-margin observables are not explicit.

### Peak Reduction control law
Implementation: v8 monotonic saturating mapping from 0..100 to sidechain drive.
Classification: BEHAVIORAL / CALIBRATED.
Strength: real-vocal PR50 operating point is directly measured.
Gap: control law is not yet derived from the complete physical sidechain chain.

### COMP / LIMIT
Implementation: distinct detector-side topology using the 68k / 2.7k relationship and optical nodes.
Classification: REDUCED PHYSICAL + BEHAVIORAL.
Strength: measured separation is meaningful and protected.
Gap: exact analog node loading remains reduced.

### R37 / pre-emphasis
Implementation: factory-flat by setting the HF mix to zero while retaining a hook.
Classification: PRODUCT BEHAVIORAL with source-backed topology.
Decision: protected default; not a current fidelity blocker.

### Active-GR optical coloration
Implementation: stateful residual optical-ripple path, Phase03G amount 0.054, 8 ms mean state.
Classification: BEHAVIORAL / MECHANISM-INFORMED.
Strength: matches the selected active-GR harmonic envelope without moving the detector/control trajectory.
Gap: not a full EL/CdS physical derivation.

### Stereo detector
Implementation: shared 0.5 * (abs(L)+abs(R)) detector.
Classification: INTENTIONAL MODERN PRODUCT BEHAVIOR.
Decision: not claimed as exact 1966 one-sided law; protected unless new evidence reopens it.

## Circuit Fidelity — Assistant synthesis

Scale: 0 = absent, 5 = unusually strong for a realtime reduced model. These are synthesis scores, not measurements.

| Block | Topology | Component | Static | Dynamic | Frequency | Nonlinear | Load | Program dep. | Evidence | Realtime |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HA-100X input transformer | 2.0 | 0.5 | 1.5 | 1.0 | 1.5 | 1.0 | 0.5 | 0.5 | 1.5 | 5.0 |
| Main 12AX7 | 4.0 | 3.5 | 4.5 | 3.0 | 4.0 | 4.0 | 3.0 | 2.5 | 4.0 | 5.0 |
| 12BH7 follower | 4.0 | 3.5 | 4.0 | 3.0 | 4.0 | 3.5 | 4.5 | 2.5 | 4.0 | 5.0 |
| A-24 output transformer | 4.0 | 3.0 | 4.0 | 2.5 | 4.0 | 1.0 | 4.5 | 1.5 | 3.5 | 5.0 |
| Sidechain 12AX7 | 2.0 | 1.0 | 2.0 | 1.0 | 2.0 | 2.0 | 0.5 | 1.0 | 1.5 | 5.0 |
| 6AQ5 EL driver | 1.0 | 0.0 | 1.0 | 0.5 | 0.5 | 1.0 | 0.0 | 0.5 | 1.0 | 5.0 |
| EL + CdS / T4 | 3.0 | 2.0 | 3.5 | 4.5 | 1.5 | 3.0 | 3.0 | 5.0 | 4.0 | 5.0 |
| Global feedback | 3.5 | 3.0 | 4.5 | 2.5 | 4.0 | 4.0 | 4.0 | 2.5 | 4.0 | 5.0 |
| Peak Reduction v8 | 1.5 | 0.5 | 4.5 | 4.0 | 4.0 | 3.0 | 1.0 | 4.5 | 4.0 | 5.0 |

## Priority conclusion

Priority 1 remains the HA-100X input transformer.

Reason:
1. it is physically early enough to affect both audio and detector excitation;
2. the current model is heuristic and has little hardware-specific evidence;
3. downstream Phase01H, Peak v8 and Phase03G blocks are substantially better constrained;
4. a linear/load-aware HA-100X model can be researched independently without changing production DSP;
5. magnetic nonlinearity can remain disabled until the linear model demonstrably fails.
