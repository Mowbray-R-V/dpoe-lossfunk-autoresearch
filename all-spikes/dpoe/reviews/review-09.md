## (3) One preregistered rule DOES literally fire against the reclassification — disclose it

The prereg kill rule — "controlled-calibrated signal passes its quality target, but full matches/loses to P+K or O … or `I3` is non-positive" — is satisfied by the locked data: quality passed (AUROC 0.850–0.924, Spearman 0.647–0.710), full lost to O (−0.0021, simultaneous CI [−0.0058, −0.0002], Holm p < 0.001) and to P+O, and I3 is non-positive. The reclassification therefore *overrides* a fired preregistered rule. The override is right, but it is a preregistration deviation and must be labeled as one.

**BLOCKING B1:** RESULTS.md's header "## Preregistered verdict" (RESULTS.md:50) mislabels a post-hoc-amended verdict as preregistered. Retitle it (e.g. "Verdict (post-review validity amendment)") and add one disclosure sentence: the preregistered kill rule's conditions were met, and the kill is set aside because that rule presupposes a reachable goal, per the manipulation check above; the amendment was adopted after independent review (see reviews/review-08.md), before any rerun. The `exploitation_floor` docstring in analyze.py already says this ("does not convert this locked run into a new confirmatory test") — it just needs to appear in the artifact readers will actually cite.

## Non-blocking

1. Add the H3b caveat above (one clause: H3b is likewise floor-uninformative).
2. Review-08 carryovers still open in RESULTS.md: trap prevalence/strength per tier and severity (protocol requires it; only aggregate 0.967/0.713 is shown), minimum locked `reference_competence`, and disclosure of the learned-tier oracle RMS rescaling.
3. Entropy/KL/timeout checkpoint metrics are in cell_summary.csv but unreported; a one-line pointer suffices.

VERDICT: REVISE — B1 only: relabel the verdict section as a post-review amendment and explicitly disclose that the preregistered kill rule fired and why it is overridden.
