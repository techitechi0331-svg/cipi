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


## WINDOWS FIX VALIDATION

### SOURCE_FACT

- Windows workflow run: `36155252191` (Run 37).
- Source SHA: `87fb94468085323083edbb2db973f7483d263ecf`.
- The run was later cancelled by a newer workflow-only/test-harness refinement, but before cancellation it completed:
  - fail-fast analyzer build: PASS;
  - preserved 610 baseline regression: PASS;
  - full Original overload investigation: PASS;
  - overload artifact upload: SUCCESS.
- Overload artifact: `Original-Vocal-Pre-Overload`.
- Artifact digest: `sha256:98b110a26a13da5a2c1ac076f9cca254fb2874723154508c97c99da126534008`.
- Subsequent product commits through `5b00e453c5b7c0ee295d7fd42343fabc0ab9ecd3` refine only the overload test harness/workflow and do not change the validated Original DSP solver fix.

### MEASURED

With all Original blocks enabled, Character 100, input trim 0 dB, source -6 dBFS:
- 1 kHz fundamental gain: **-0.213888 dB**.
- 1 kHz peak: **0.504335**.
- 1 kHz THD: **3.02875%**.
- 10 kHz fundamental gain: **-0.319197 dB**.
- 10 kHz peak: **0.49369**.
- 10 kHz THD: **2.0258%**.
- Both points were finite and passed the new > -6 dB high-level fundamental gate.

Additional stress point, Character 100 / input trim 0 dB / source -3 dBFS:
- 1 kHz gain: **-0.746097 dB**, THD **8.79264%**.
- 10 kHz gain: **-0.521395 dB**, THD **4.08656%**.
- Both remained finite with the wanted fundamental intact.

The previous catastrophic 10 kHz / -6 dBFS loss of approximately -88 to -300 dB is therefore not present in this Windows measurement.

### INFERRED

- The opt-in bracketed current solve removes the observed latch/collapse while preserving the old 610 research solver path.
- The successful preserved 610 baseline regression in the same run is evidence that this fix did not silently alter the historical 610 product path.
- The corrected overload behavior is strong enough to resume extended Original measurements, but it does not by itself lock Character, Tone, transformer settings or CPU/latency policy.

### REMAINING

- Re-run the latest branch with the split fast gate and corrected trim-relative reporting.
- Inspect extended shortlist/IMD/alias/frequency results under the robust Original solver because numerical values can legitimately shift after the solver correction.
- Measure real-time CPU cost of the robust solver before parameter lock.
- Complete level-matched real-vocal A/B and Cubase Pro 14 host validation.


## LATEST-BRANCH FAIL-FAST CONFIRMATION

### SOURCE_FACT
- Latest product branch source under validation: `5b00e453c5b7c0ee295d7fd42343fabc0ab9ecd3`.
- Windows workflow run: `36156239641` (Run 39).
- Preserved 610 baseline regression: PASS.
- New split high-level overload fail-fast gate: PASS.
- Fail-fast artifact: `Original-Vocal-Pre-Overload-Gate`.
- Artifact digest: `sha256:a616018c68fd05da7e7ef22b6fa92a17d02984be68818afc8ab12a2218d45b02`.

### MEASURED
At Character 100, input trim 0 dB, source -6 dBFS:
- 1 kHz gain: **-0.213888 dB**, peak **0.504335**, THD **3.02875%**, finite.
- 10 kHz gain: **-0.319197 dB**, peak **0.493690**, THD **2.0258%**, finite.

The latest branch therefore reproduces the corrected high-level behavior at the permanent fast gate.
The longer shortlist / tuning / full-overload artifacts from this run remain separate evidence and must be inspected before parameter lock.


## RUN 39 EXTENDED-MEASUREMENT CLOSURE

### SOURCE_FACT
- Windows workflow run: `36156239641` (Run 39) — **SUCCESS**.
- Source SHA: `5b00e453c5b7c0ee295d7fd42343fabc0ab9ecd3`.
- Dedicated Original VST3 artifact digest: `sha256:833e527436dfe9999fe32e481a8d247865bacd9cc8c83bab87c10a8a63e8a5ca`.
- Extended shortlist artifact digest: `sha256:4c0bd1b55a50e7f5a96682c72b697498a2aab4878a5958dd9cb3713ad1c9739f`.
- Full overload characterization artifact digest: `sha256:863342afee053578b156766d31579ad53ae61a33e9d0b58c1b4fc1e54bb4c3e4`.
- Preserved 610 research VST3 artifact digest: `sha256:b6247f2d81e185359e42cfd8fcfadf28ee24e8475b17a5e6c2ab871010116d46`.

### MEASURED
All five refreshed shortlist profiles pass the current technical gate under the robust Original solver.

Small-signal Character compensation:
- gain spread across Character 0..100 is approximately **0.0060 dB** for every shortlist profile;
- maximum absolute small-signal gain error is approximately **0.0116–0.0133 dB**.

Frequency response at Character 50:
- no-output-transformer profiles: approximately **-0.16 to -0.17 dB at 20 Hz** and **-0.325 dB at 20 kHz** relative to 1 kHz;
- output-transformer profiles: approximately **-0.33 to -0.37 dB at 20 Hz** and **-0.853 dB at 20 kHz** relative to 1 kHz.

Character 100 / -6 dBFS, wanted-fundamental gain and THD:
- `simple4_no_output_tx`: 100 Hz **-0.240 dB / 1.108%**, 1 kHz **-0.207 dB / 3.030%**, 10 kHz **-0.185 dB / 2.114%**.
- `conservative`: 100 Hz **-0.250 dB / 1.118%**, 1 kHz **-0.213 dB / 3.028%**, 10 kHz **-0.319 dB / 2.026%**.
- `simple6_no_output_tx`: 100 Hz **-0.359 dB / 1.635%**, 1 kHz **-0.450 dB / 5.908%**, 10 kHz **-0.280 dB / 3.208%**.
- `balanced`: 100 Hz **-0.371 dB / 1.651%**, 1 kHz **-0.470 dB / 5.904%**, 10 kHz **-0.417 dB / 3.074%**.
- `color_contrast`: 100 Hz **-0.697 dB / 2.900%**, 1 kHz **-1.347 dB / 6.392%**, 10 kHz **-0.696 dB / 3.068%**.

Character 100 IMD at -18 dBFS:
- SMPTE-like: **0.369–0.467%** across the shortlist.
- CCIF-like: **0.312–0.418%** across the shortlist.

Alias:
- 8x oversampling alias result ranges from approximately **-136.7 to -147.2 dBc**.
- 16x ranges from approximately **-136.8 to -148.0 dBc**.
- All current shortlist profiles therefore remain comfortably inside the existing -70 dBc technical alias gate.

Full overload characterization confirms the corrected all-on Original path remains finite and retains the wanted fundamental through the tested -3 dBFS stress points:
- 1 kHz / -3 dBFS / Character 100: **-0.746 dB gain, 8.793% THD**.
- 10 kHz / -3 dBFS / Character 100: **-0.521 dB gain, 4.087% THD**.

### INFERRED
- The robust-solver correction is not merely a fail-fast-point fix; refreshed frequency, THD, IMD, alias and overload measurements remain numerically stable enough to resume product-candidate comparison.
- The output-transformer profiles introduce a measurable but still modest top/bottom spectral tilt relative to their no-output-transformer counterparts. Whether that tilt/body behavior is beneficial is a listening decision, not a numerical winner metric.
- 4 dB profiles are materially more conservative at high Character than the 6 dB profiles. The `color_contrast` profile is intentionally the strongest and shows the greatest gain compression / THD at Character 100.
- Numerical evidence does not justify selecting one final profile yet. The refreshed measurements narrow the candidate space and make level-matched vocal A/B the next meaningful discriminator.

### STATUS
- High-level HF solver collapse: **CLOSED for the measured Windows path**.
- Robust-solver extended measurement refresh: **COMPLETE**.
- Preserved 610 baseline compatibility: **PASS**.
- Product track remains **PROVISIONAL** pending real-vocal A/B, CPU/latency closure and Cubase Pro 14 validation.
