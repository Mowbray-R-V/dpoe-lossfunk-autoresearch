# MVE 3 v2 Development Solvability Gate

Status: **failed under the complete preregistered 27-tuple grid.** No pilot-v2 or
locked-v2 seed was opened. This report and its JSON artifact were regenerated once in a
report-only pass to add omitted per-severity return-AUC fields: all pre-existing metric
fields were bit-identical (SHA-256 `0c38a4f4b062c844c8153796ac9f147b54b077ff8f7d61509f083bcd33a600bf`).
That pass did not re-enter the grid, select a tuple, retune, or create any new seed.

## Prespecified gate

A tuple required aggregate oracle true-goal success >=25%, every severity >=15%, aggregate
oracle-minus-none goal-success >=15 percentage points, and oracle-minus-none true-return
AUC >=0.10. The gate actually used 1,000 evaluation episodes per scenario; the original
archived config blocks incorrectly showed the base 200-episode setting, which is corrected
in the regenerated artifact.

## Result

No tuple passed all conditions. The best oracle-goal tuple was
`tau_reference=0.18`, `beta0=0.10`, clip ±1.75:

| Metric | Result | Required |
|---|---:|---:|
| Aggregate oracle goal success | 16.44% | >=25% |
| Severity 1 / 2 / 3 oracle success | 14.53% / 15.60% / 19.19% | each >=15% |
| Oracle-minus-none goal success | 11.36 percentage points | >=15 pp |
| Oracle-minus-none true-return AUC | 0.3485 | >=0.10 |
| Severity 1 / 2 / 3 oracle-minus-none return AUC | 0.3142 / 0.2891 / 0.4422 | Reported diagnostic |
| Minimum source competence | 0.988 | Descriptive (source threshold 0.80) |

The return-AUC condition was attainable, but the oracle could not reach the true goal often
enough and did not separate enough from the none policy. The initial implementation also
treated source competence >=0.80 as a fifth development guard although the written
development gate listed four conditions; this stricter guard was non-binding (minimum
0.988), and the code now follows the written four-condition gate. Per the frozen protocol,
this is a development solvability failure, not evidence for or against conditional C3.

The best candidate lies at the prespecified grid boundary (`tau_reference=0.18`, clip
±1.75, `beta0=0.10`), and oracle success increased with the available `tau_reference` and
clip relaxations. Thus the correct conclusion is **not solvable within this preregistered
grid**, not globally unsolvable. Extending that boundary after seeing these results would be
outcome-driven and is forbidden without a new protocol, independent review, and human
sign-off. The required costliest-tuple timing pre-check was inadvertently skipped before the
original exhaustive grid; this protocol deviation is disclosed here. It did not affect the
claim decision, because the complete grid finished and the hard stop was determined by the
prespecified solvability thresholds. Do not expand the grid, retune, run the
adaptation-engagement gate, or open pilot/locked-v2 seeds. The v2 C3 outcome is **untested
— preregistered solvability gate failed**.
