# Review — Day 1 pre-registered MVE designs

Reviewer: Claude Code 2.1.209 (independent reviewer). Date: 2026-07-17.

## Blocking issues

1. **MVE 1 target-label confound:** Add source-only calibration as the primary faithful
   contrast; retain target-probe calibration only as a labeled secondary condition.
2. **MVE 2 frozen-regime control not operationalized:** Add concrete decorrelated and
   anti-correlated uncertainty/true-reward layouts and a pass condition.
3. **Undefined reward-hacking rate:** Define the event and denominator separately for MVE
   2 and MVE 3.
4. **MVE 3 reference policy unspecified:** Pre-register the KL reference as a
   source-layout-pretrained policy and state its training budget.

## Non-blocking suggestions

- Report MVE 1 sensitivity over 2–3 fixed KL coefficients.
- Add the plan's exact matched-magnitude uniform-noise Control A arm.
- Record the matched-compute part of C1 as untested.
- Declare primary versus exploratory contrasts and multiplicity handling.
- Increase implementation estimates.
- Frame MVE 1 as an existence test, not a prevalence claim.

Feasibility was judged credible on the audited CPU-only host at $0.

**VERDICT: REVISE** — add source-only calibration; pre-register decorrelated and
anti-correlated frozen layouts; define hacking events; specify a source-pretrained
reference policy.

