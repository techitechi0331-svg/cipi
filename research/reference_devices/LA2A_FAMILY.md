# LA-2A Family — reference-device research 0.1

Status: **RESEARCHING**  
Maturity: **L2/L6**

## Documented architecture

The LA-2A uses the T4 electro-optical attenuator as the core gain-reduction element.

Documented signal/control structure:

`input transformer -> optical attenuator -> gain/output amplifier -> output transformer`

with a sidechain that includes a voltage-amplifier / pre-emphasis path and a driver for the electro-luminescent panel.

The T4 combines:

- an electro-luminescent (EL) panel;
- a photo-conductive cell used in the gain-control divider.

More input drive produces more light, reducing the photocell resistance and increasing attenuation.

Primary contextual sources:
- historical Teletronix LA-2A manual scan preserved by the Library of Congress;
- Universal Audio LA-2A documentation/history.

## Documented timing behaviour

UA describes the T4 response as strongly program dependent:

- average attack around 10 ms;
- initial release of roughly 60 ms for about half of recovery;
- remaining recovery on the order of 1–15 seconds depending on prior program history.

The T4 can retain memory after sustained/heavy compression. Therefore, a single attack coefficient + single release coefficient is not an adequate model of documented behaviour.

## Modeling targets

1. EL-panel drive-to-light transfer.
2. photocell light-to-resistance relationship.
3. divider gain as photocell resistance changes.
4. multi-stage / history-dependent recovery.
5. sidechain pre-emphasis and frequency dependence.
6. compressor/limiter slope behaviour.
7. tube amplifier nonlinearities.
8. input/output transformer contribution.
9. differences among historical T4/T4A/T4B and hardware revisions.

## Reusable design lesson

The key reusable principle is not "slow optical compressor."

It is:

`signal history -> opto state -> nonlinear resistance -> gain`

where the opto state has memory over multiple time scales.

CIPI should promote a general **history-dependent leveler** pattern only after the state model has been fitted and measured.

## Current evidence

- T4 electro-optical gain element: **E5 documented**.
- photocell used as variable divider element: **E5 documented**.
- program/history-dependent release: **E5 documented**.
- single numerical state equation for a specific T4 cell: **not yet confirmed**.
- tube/transformer contribution vs opto contribution: **measurement/modeling required**.
