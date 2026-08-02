## Review: MVE 3 v2 amended preregistration (draft)

Read against `research-philosophy.md`, `mve3-protocol.md` (v1), `reviews/review-08.md`, `reviews/review-10.md`.

The four requested elements are all present and mostly operational. The delta table is genuinely evidence-mapped, each row citing Review 08/10. The tuning section correctly firewalls `development-v2` from pilot/locked seeds, gives a closed grid, a fixed lexicographic selection rule, and an immutable frozen config written before any pilot seed opens. The grid is feasible against Review 08's arithmetic. Truth handling in the oracle gate is clean: development-only for tuning, locked oracle run only after cells complete, never into a policy, collector, or posterior.

## BLOCKING

1. **No minimum effect magnitude:** a CI upper bound <=0 would let v2 recreate v1's statistically real but scientifically tiny -0.002 to -0.005 losses. Preregister a headroom-relative magnitude floor and require the CI upper bound below `-delta`.
2. **Solvability wrong metric:** goal-success gates do not establish return-AUC headroom for the primary estimand. Add oracle-minus-none return-AUC separation to development and locked gates.
3. **Outcome-conditioned engagement:** requiring P+K+O goal success makes a null unfalsifiable. Gate on factor-independent oracle-none separation plus a maximum across factorial cells, expressed as a fraction of that separation.
4. **I3 is incorrect in the disjunctive kill list:** negative I3 can coexist with full beating every half. Drop it from the kill disjunction or separately label no-superadditivity.
5. **Asymmetric standard:** support requires all directions and 2-of-3 severity agreement; kill needs one aggregate contrast. Apply the same 2-of-3 severity direction rule to kills.

## Non-blocking

1. Resolve exhaustive versus sequential candidate evaluation.
2. Restate the source-competence >=80% gate for the selected reference tuple.
3. Remove learned-tier oracle RMS rescaling in v2, not merely before a future claim.
4. Time one tuple before committing to a 27-tuple tuning budget; the under-1-hour estimate is unrealistic.
5. Align the v1 status wording to the post-review validity amendment.

VERDICT: REVISE
