# VoPriPro Amount Transfer Assessment v1

## Question

Should any existing Vo.Prep transparent-compressor Amount-mapping result be transferred directly into VoPriPro now?

## Current VoPriPro baseline

VoPriPro currently maps AMOUNT to a product-specific combination of:

- ratio;
- calibration GR;
- max GR.

The current map is already implemented, regression-tested, and part of the protected production baseline.

## Reused CIPI evidence from Vo.Prep

No new Amount experiment was started before reviewing existing CIPI evidence.

### VO-PREP-AMOUNT-MAP-001

MEASURED / reviewed:

- post-curve DesiredGR scaling was mathematically exact for zero-null, 100% endpoint and linear strength in the deterministic model;
- threshold sweep and ratio interpolation were less linear in that model;
- review decision was **ITERATE**, not final product adoption.

Reusable principle:

DesiredGR scaling is a clean mathematical intensity control for a frozen static curve.

### VO-PREP-AMOUNT-R2-001

MEASURED / reviewed:

- selected DesiredGR-scaling candidate failed the untouched HUST final-holdout ripple gate;
- Amount 100 aggregate ripple was about 0.080343 dB versus the locked 0.080000 dB ceiling;
- decision: **REJECT** for that product revision.

### VO-PREP-AMOUNT-R3-VOCALSET-001

MEASURED / reviewed:

- all tested candidates failed selection before final holdout;
- dominant failure was insufficient mean GR at Amount 50/75/100 on the VocalSet selection singers;
- decision: **REJECT** for the tested fixed-offset family.

### VO-PREP-AMOUNT-R4-LEARN-SOLVE-001

MEASURED / reviewed:

- Learn-time threshold solve was highly accurate and input-gain invariant;
- it still failed the unchanged high-Amount ripple gate;
- the declared holdout-isolation procedure was also violated at data-access level;
- decision: **REJECT** for the tested R4 architecture.

## INFERRED transfer assessment

There is currently no Vo.Prep Amount candidate with source-side evidence strong enough to justify direct transplantation into VoPriPro.

This does not mean the mathematical DesiredGR-scaling principle is invalid. It means that the concrete Vo.Prep product mappings tested through R2-R4 did not survive their own full product gates, and their fixed 1.5:1 / 18 dB / 8/70 ms core differs materially from VoPriPro's current Amount architecture.

Therefore a direct comparison job would currently be premature and partly redundant.

## Decision for VoPriPro

- Keep current VoPriPro AMOUNT mapping as the production baseline.
- Do not copy Vo.Prep R2/R3/R4 Amount mapping into VoPriPro.
- Preserve DesiredGR scaling as reusable general Dynamics knowledge.
- Reopen Amount transfer only if a new candidate is defined specifically for the current VoPriPro architecture with predeclared same-corpus gates.

## Scope

This assessment is a reuse decision based on existing CIPI evidence. It does not claim that the current VoPriPro Amount curve is perceptually optimal.

The current map still needs its own level-matched listening/generalisation gate.

## Next work

The next higher-value cross-product question is Vo.Prep -> VoPriPro integration: whether event/phrase preprocessing reduces unwanted compressor reactions without creating harmful double gain movement.
