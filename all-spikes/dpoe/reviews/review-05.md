# Review 05 — Revised MVE 3 Preregistration

Reviewer: Claude Code 2.1.209. Date: 2026-07-17.

The review approved the MVE 2-driven scope change, quality gate, interaction form,
hash/pairing concept, separate evaluation phase, kill rules, and $0 feasibility in
principle. It returned three blocking protocol issues:

1. The controlled-calibrated posterior generator was not specified tightly enough to rule
   out target-truth/error leakage; shrinkage must depend only on label receipt/history, not
   label correctness, with a leakage diagnostic.
2. The non-O collection policy was undefined, so P/K could inadvertently affect data
   collection only when O was absent and invalidate the factorial interaction.
3. Hacking contrasts did not specify checkpoint AUC versus final rate, and true-goal
   visitation was predicted without being declared confirmatory or exploratory.

Non-blocking suggestions: preserve own-state responsiveness in the shuffled control; pair
label noise by state/visit index; time a pilot with a symmetric seed-reduction rule; stream
summaries rather than trajectories; fix posterior-sampling terminology; make pilot a
distinct hash split.

**VERDICT: REVISE** — protocol text fixes; no execution authorized.

