## Review: MVE 3 v2 re-verification

Review-11 B1/B2/B4/B5 and all five non-blocking items are resolved. One blocking issue remains.

### BLOCKING B3

The locked engagement gate compares a maximum factorial-cell goal-success level with an oracle-minus-none difference. Because `none` is among the maximum, a raised reference baseline can pass it with zero adaptation. Require instead:

`max over controlled factorial cells of (cell goal-success AUC - none goal-success AUC) >= 0.20 × (oracle-minus-none goal-success separation)`.

Mirror this as a development gate. It remains factor-independent and measures adaptation rather than baseline reachability.

### Non-blocking

1. Use a plausibly costliest tuple or a running wall-clock abort for tuning.
2. Assert/report source competence >=0.8 across locked-v2 scenario retraining.
3. Explicitly state return-AUC normalization is identical for gate policies and factorial contrasts.

VERDICT: REVISE
