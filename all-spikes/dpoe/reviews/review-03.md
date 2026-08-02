# Review — MVE 2 completed result

Reviewer: Claude Code 2.1.209. Date: 2026-07-17.

The reviewer audited RNG independence, seed provenance, row counts, aggregate arithmetic,
paired statistics, multiplicity handling, tests, and the plot. **No implementation bug or
statistical error requires a rerun.**

## Blocking interpretation fixes

1. Condition the C2 conclusion on the weak bootstrap-linear estimator (error AUROC 0.532,
   Spearman 0.162). Promote weak epistemic error discrimination under shift as a primary
   transferable result; online failure cannot distinguish mechanism failure from estimator
   insufficiency.
2. Describe the frozen result as structural, not as a horse-race effect size. The
   decorrelated layout ties point; the anti layout uses a full rank reversal and therefore
   constructs harm. The valuable result is that frozen uncertainty cannot acquire
   information and its effect follows static correlation.

## Disclosures requested

- Label total-versus-point as exploratory/post-hoc.
- State that hacking was measured over the 160 one-step collection episodes, while the
  unused `eval_episodes=200` config did not define a separate evaluation phase.
- Note target-render seed overlap across a few seed/severity pairs for future correction.
- Note that development uncertainty scaling used base rewards before layout permutation.

**VERDICT: REVISE** — text fixes only; no rerun.

