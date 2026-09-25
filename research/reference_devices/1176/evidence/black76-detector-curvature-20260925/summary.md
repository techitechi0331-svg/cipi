# Black76 shared detector-curvature ablation — 2026-09-25

## Scope

Imported derived numeric evidence from the Black76 product repository.

The experiment is diagnostic only. Production/VST3 detector behavior was not replaced.

## Research question

Can one shared superlinear detector power exponent, with per-ratio detector gain and bias retuned, recover the supplemental LN-era low/mid/deep static-ratio curvature?

## MEASURED

Baseline gamma=1:
- onset MAE: 0.5 dB
- ratio log-RMSE: 0.446926
- max relative ratio error: 0.630159
- minimum deep-ratio fraction: 0.422243

Best tested shared exponent gamma=2.35:
- onset MAE: 0.5 dB
- ratio log-RMSE: 0.384355
- max relative ratio error: 0.52155
- minimum deep-ratio fraction: 0.547092
- log-RMSE improvement versus gamma=1: about 14.0%

Predeclared product-side gates were:
- onset MAE <= 1 dB
- ratio log-RMSE <= 0.20
- >=30% improvement vs gamma=1
- max relative ratio error <=0.35
- minimum deep-ratio fraction >=0.80

Only onset passed.

## REJECTED candidate claim

Within the tested Black76 architecture:

"A single shared power-law detector curvature plus per-ratio gain and bias is sufficient to reproduce the supplemental low/mid/deep ratio curves."

The data reject this as a sufficient final mechanism.

## INFERRED

The remaining shape mismatch needs a mechanism that changes with ratio and/or operating point.

Open candidates:
- switched source/loading interaction before the rectifier;
- diode-bias operating-point interaction;
- control-amplifier / feedback-loop level dependence.

This evidence does not establish which candidate is correct.

## Hardware honesty

The fit target is the committed supplemental UA LN-era proxy, not a directly measured vintage Rev-E unit.
