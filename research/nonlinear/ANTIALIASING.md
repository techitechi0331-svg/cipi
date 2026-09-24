# Nonlinear Antialiasing — research snapshot 0.1

Status: **VERIFYING**  
Maturity: **L3/L6**

Memoryless nonlinear processing creates harmonics that can exceed Nyquist and fold back as aliasing.

JUCE provides 2x/4x/8x/16x oversampling with FIR or polyphase-IIR half-band filters. ADAA is a peer-reviewed alternative/complement for memoryless nonlinearities, with further research extending the idea to stateful systems.

## CIPI policy

1. Oversampling is the conservative baseline for nonlinear prototypes.
2. Alias products must be measured; never assume the factor is sufficient.
3. Investigate ADAA when the nonlinearity has tractable antiderivatives and CPU/latency matter.
4. Do not automatically replace oversampling with ADAA; state/interpolation details matter.

## Density 0.1

Uses 4x JUCE polyphase-IIR oversampling around a smooth `tanh` nonlinearity.

Later compare 1x/2x/4x/8x, ADAA where applicable, alias energy, CPU, latency, and high-frequency vocal consonants.
