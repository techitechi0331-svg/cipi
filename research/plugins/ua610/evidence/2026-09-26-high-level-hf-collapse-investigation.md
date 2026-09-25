# Original Vocal Pre — high-level HF fundamental collapse investigation

Date: 2026-09-26

## SOURCE_FACT

- Product repo: `techitechi0331-svg/610`
- Active branch: `original-vocal-pre-v0.1`
- Previous shortlist workflow run `36081328274`, source `d288081e397c4417341b6243094c0b8f902264f3`, completed successfully.
- Dedicated Original VST3 workflow run `36142804137`, source `c9feef43af6035b81d9cfb96f85d4d61ee8f5d31`, completed successfully.
- Run 31 dedicated Original VST3 artifact digest: `sha256:c750dd15c8ec90be506980517655b210b78f45e1a2f6da1d31dd73a255a40e28`.
- The earlier shortlist technical gate did not reject high-level loss of the wanted fundamental.
- A dedicated overload investigation analyzer has now been added.
- Candidate product solver fix: `62b9bc533ec8d4f98c9bd134213561c26feb40d7`.
- Fail-fast workflow ordering: `a08e413f9caa7393cdbb1f4a86857fa09334ef1f`.
- Product branch head at this evidence write: `87fb94468085323083edbb2db973f7483d263ecf`.

## MEASURED

Existing `shortlist_thd.csv` evidence exposed a failure mode that the old summary gate did not catch.

At 10 kHz / -6 dBFS:
- `simple4_no_output_tx`: fundamental gain approximately -299 to -300 dB depending on Character.
- `simple6_no_output_tx`: fundamental gain approximately -300 dB.
- `conservative`: fundamental gain approximately -88 to -89 dB.
- `balanced`: fundamental gain approximately -89 to -91 dB.
- `color_contrast`: fundamental gain approximately -107 to -109 dB.

The same candidates did not show the same catastrophic fundamental collapse at the lower 10 kHz / -12 dBFS test point.

Despite the above, all five profiles had `technical_gate_pass=1` in the earlier shortlist summary. The old gate was therefore incomplete for high-level HF behavior.

## INFERRED

Code-path isolation and an independent numerical reproduction strongly indicate that the collapse originates in the stateful Newton-style current solve in `TriodeStage`, especially Stage 1 at high instantaneous drive.

The symptom is consistent with the solver reaching a current rail and using the previous-sample current as the next initial state, allowing a high-level/high-frequency sequence to latch into an invalid quasi-constant output state.

Transformer removal and spectral-protection removal do not explain the fundamental disappearance by themselves. Removing Tube 1 removes the reproduced collapse, making Stage 1 solver behavior the primary suspect.

Because `TriodeStage` is shared by the preserved 610 research model, a global behavior change would silently invalidate historical baseline evidence. The safer architecture is an opt-in robust solve used by the Original product only.

## HYPOTHESIS

A bracketed root solve for the Original tube stages will remove the high-level HF latch without changing the preserved 610 research path.

The candidate implementation:
- leaves the legacy solver as the default;
- adds an opt-in bracketed solver to `TriodeStage`;
- enables it only from `OriginalPreampModel`;
- adds a permanent high-level fundamental regression gate at 1 kHz and 10 kHz / -6 dBFS;
- requires relative gain greater than -6 dB at those fail-fast points;
- runs the preserved 610 baseline regression before the long Original measurement suite.

This remains a hypothesis until the Windows workflow passes the new gate and the resulting extended measurements are inspected.

## REJECTED

- Treating `technical_gate_pass=1` from the earlier shortlist as sufficient proof that high-level behavior was safe.
- Choosing a final Original profile before closing this collapse.
- Fixing the issue by globally replacing solver behavior in the preserved 610 research model.
- Treating finite output alone as evidence of acceptable overload behavior.

## STATUS

- Product track remains `PROVISIONAL`.
- Current formal stage remains measurement/revision.
- Real-vocal A/B must not select a final winner until this regression is closed.
- Cubase Pro 14 Mic 2k / Mic 500 confirmation remains a separate open host gate.
