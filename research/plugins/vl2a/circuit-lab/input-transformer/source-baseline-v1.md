# HA-100X Input Transformer — source baseline v1

Date: 2026-09-26
Status: source research + model contract
Integration authority: NONE

## SOURCE_FACT

### Universal Audio LA-2A manual

Source:
https://media.uaudio.com/assetlibrary/l/a/la-2a_manual.pdf

Relevant facts:
- LA-2A input impedance is documented as 600 ohms balanced.
- maximum input level is +16 dBm.
- the input transformer provides isolation and impedance matching.
- after the input transformer, signal feeds both the sidechain circuit and the gain-reduction circuit.
- Figure 5 identifies the input transformer as HA-100X.
- Figure 5 shows the immediately relevant network including R6=68k, R7=2.7k, R5=68k and Gain R1=100k.

### UTC Hipermalloy catalog

Primary-document scan mirror:
https://www.opweb.de/pdf/utc-united-transformer-company--catalog-1960--catalog--ID8335.pdf

HA-100X catalog facts:
- application: low-impedance microphone/pickup/multiple line to grid.
- primary impedance taps include 50, 125/150, 200/250, 333 and 500/600 ohms.
- secondary: 60,000 ohms overall, split.
- response: 30–20,000 Hz within the catalog's +/-1 dB column.
- maximum level: +16 dBm.
- multiple alloy shields for very low hum pickup.

## SOURCE_FACT — current VL2A

Product branch:
techitechi0331-svg/VocalPrepComp @ integration/vl2a-v060-rc2

Current input transformer:
- TransformerModel.
- low-cut 12 Hz.
- colour amount 0.12.
- 25 ms state called magnetisation.
- tanh-based nonlinear blend.
- no explicit nominal turns/impedance ratio.
- no explicit source/load network.
- no HA-100X DCR/Lm/leakage/capacitance parameters.

## INFERRED

### Nominal impedance-derived ratio

Using the documented 600-ohm primary tap and 60,000-ohm overall secondary:

Ns/Np ~= sqrt(60000 / 600) = 10.

This is an impedance-derived nominal ratio, NOT a measured winding-count ratio.

Consequences under ideal matching:
- a 60k secondary load reflects to approximately 600 ohms at the 600-ohm primary tap;
- a physically explicit offline model should therefore represent source/load interaction before product-boundary normalization.

### +16 dBm context

+16 dBm is 39.81 mW.
Across 600 ohms this corresponds to approximately 4.887 Vrms.
A nominal 10:1 ideal winding relation would correspond to approximately 48.87 Vrms on the secondary for the same primary-winding voltage before loading/losses.

These are calculation contexts, not measured HA-100X internal voltages.

## MEASURED

No new hardware measurement is claimed in v1.

Existing product-side measurements do not identify HA-100X internal parameters because the current model is heuristic.

## HYPOTHESIS

- A normalized, load-aware linear model may already outperform the current heuristic in structural fidelity without audible or control regression.
- source/load dependency may matter more than an unsupported hysteresis state for the first useful fidelity increase.
- the documented 30–20k +/-1 dB response constrains parameter combinations but cannot uniquely identify Lm, leakage and capacitance separately.

## REJECTED

- Treating the current 12 Hz high-pass as an HA-100X measured pole.
- Treating the current 25 ms magnetisation state as measured magnetic memory.
- Treating colour=0.12 or tanh coefficients as hardware constants.
- deriving unique DCR/Lm/leakage/C values from the 30–20k +/-1 dB catalog response alone.
- adding hysteresis before a linear model fails against reproducible evidence.

## Parameter uncertainty map

| Parameter | Current evidence |
|---|---|
| nominal primary impedance / taps | source-backed |
| nominal secondary impedance | source-backed |
| nominal impedance-derived ratio | inferred |
| frequency-response envelope | source-backed |
| max level rating | source-backed |
| primary DCR | unknown |
| secondary DCR | unknown |
| magnetizing inductance | unknown |
| leakage inductance | unknown |
| winding/interwinding capacitance | unknown |
| core-loss resistance | unknown |
| exact turns ratio | unknown |
| hysteresis coefficients | unknown / prohibited for adoption |
| source-impedance dependency | topology-expected, not yet measured on hardware |
| level-dependent LF saturation | plausible, not yet hardware-quantified |

## Offline model contract

Reference B — ideal/load-aware:
- documented nominal ratio;
- explicit source R and secondary load;
- no arbitrary magnetic nonlinearity.

Reference C — linear LTI:
- Reference B plus optional Rp/Rs/Lm/Lleak/C/Rcore;
- every unsupported value remains a parameter or fit seed;
- fit seeds never become SOURCE_FACT.

Reference D — nonlinear magnetic:
- disabled by default;
- only created if B/C leave a repeatable error that the magnetic state reduces without causing regressions.
