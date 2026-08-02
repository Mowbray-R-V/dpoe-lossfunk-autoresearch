### Review-16 blocking items — all five verified applied

- **B1 related work — APPLIED.** New §2 (tex:22–26) covers Cen, Park, Coste, Zhai, Zhang, Liang, Li, Kendall & Gal, Liu, plus DriveReward. Characterizations are faithful to `papers/` where I could check: Cen's sign-modulated optimism-online/pessimism-offline framing matches `cen_2025_vpo.md:27–34`, and Li's reference-dependent correction and the "naive UCB is now inadequate" consequence match `li_2026_exploratory_bonus.md:13–19, 44–47`. The stated DPOE delta (one signal, both directions, one visual-adaptation loop) is preserved.
- **B2 reviewer provenance — APPLIED, and honestly.** tex:76 and checklist item 6 (tex:131) now name the automated failures, the human-mediated Reviews 09/14–16, the two empty Review-16 captures, and the Review-15 misreport. The `\begin{ack}` overclaim is gone. This is the disclosure Review 16 asked for.
- **B3 three missing deviations — APPLIED.** tex:74 now reads seven, including the per-severity-vs-aggregate v1 gate (3), the learned-tier `u0` RMS rescale exposing oracle-scale information (3), and the Review-13 false audit statement (7). Mirrored at `iterated-research-plan.md:132–154`.
- **B4 title — APPLIED.** Now "When Reward-Uncertainty Coupling Cannot Be Tested: Validity Gates for DPOE." No longer contradicts tex:78.
- **B5 compilation — APPLIED.** `dpoe_negative_result.log:400`: "Output written … (7 pages)". Math-mode faults are gone (`$P\times K\times O$` at tex:52, `$\geq25\%$` at tex:54).

### PDF checks

- **Seven pages** — confirmed (log:400).
- **Citations resolved** — confirmed. The log contains **zero** `LaTeX Warning` lines. LaTeX unconditionally emits `Citation undefined` / `There were undefined references` when `??` or `[?]` would print; their absence rules out unresolved refs.
- **Figure visible, not a broken box** — confirmed. log:371–374 records `mve3_return_auc_factorial.png, id=16, 1156.32pt x 289.08pt`, `Graphic file (type png)`, `used on input line 65`; log:377 places it on page 3.
- **No reader-visible LaTeX errors** — confirmed. No Overfull hbox at all. Three Underfull warnings only (log:358, 363, 368), at tex:39–40 — the C2/C3 table cells — meaning loose interword spacing in Table 1, plus one page-breaking vbox. Cosmetic, log-only, no rules or black boxes. Noted, not proposed for edit.
- **"not solvable within the preregistered grid"** — verbatim in source at tex:40 and bolded at tex:71, and at `iterated-research-plan.md:15, 37, 50`. **Not independently verified in rendered PDF text** per the caveat above; a one-line `pdftotext | grep` would close this.

### Claim table (tex:38–40) — confirmed as specified

C1 **Untested**, MVE 1 did not run, with the DriveReward control list. C2 frozen information-gain rationale **structurally killed** analytically and corroborated by MVE 2, online estimator claim explicitly unresolved (this also absorbs Review-16 N6). C3 **untested at toy scale**, v1 floor plus v2 grid, no pilot/locked-v2 seeds. Matches `iterated-research-plan.md:24–38`. No softening.

### Review-15 correction — real

`PROGRESS.md:5–11` states plainly that the manual file showed `VERDICT: REVISE` against the earlier human-reported APPROVE, and that experiments stay closed "not by a nonexistent Review-15 APPROVE." `LEARNINGS.md:33` now reads "Corrected v1 pilot completed 480/480 cells" — the stale `pilot-v2` string is gone from the file, and it was Review 15's single blocking item. Surfaced in the paper twice (tex:76, tex:131). Correction is genuine, not asserted.

Review-16's non-blocking items also landed: N1 (tex:61 names *killed-at-toy-scale* and the withdrawal), N2 (tex:58 reports the +0.0081 epistemic-over-aleatoric contrast that cuts *toward* C2, then explains why the 0.532 AUROC blocks reading it), N3, N4 (plan:18), N5 (plan:100 "bootstrap-linear disagreement score"), N7 (plan:105–113, 250–350 h withdrawn).

### BLOCKING

**B1. The Zhang/AdvPO citation does not match the paper stored in `papers/`.** tex:98 reads "Zhang, et al. (2024). AdvPO: uncertainty-aware pessimistic preference optimization. NeurIPS." But `papers/zhang_2024_advpo.md:1–12` is **Kang & Oh, "Adversarial Policy Optimization for Offline Preference-Based Reinforcement Learning," ICLR 2025, arXiv:2503.05306** — different authors, year, and venue. The entry was inherited verbatim from `research-plan.md:195` ("Zhang et al. 2024 (NeurIPS, AdvPO)"), which per CLAUDE.md is exactly the one-line summary that `papers/` supersedes. It is also the only bibliography entry carrying no arXiv ID, i.e. the one that was never checked against a source. A real Zhang et al. 2024 AdvPO exists (arXiv:2403.05171), so this is recoverable — but as written, either the author string or the stored PDF is wrong, and the venue is unverified on both readings. In a paper whose entire contribution is an audit procedure, and in a related-work section that exists *because* Review 16 demanded positioning, a citation that doesn't match its own source-of-truth file is the first thing a screener greps. The substantive sentence at tex:24 survives under either reading; the fix is bibliographic, not a claim change.

### Non-blocking

**N1.** tex:76 "Reviews 01--08 and 10--13 produced usable automated CLI verdicts" flattens Review 10: `PROGRESS.md:180–186` records two empty captures, then a successful exit-0 run only after the human supplied a response-text-only invocation pattern. Automated in the end, human-unblocked. The binary automated/manual split slightly favors the paper.

**N2.** tex:76 "claims reviewer assistance and a manual Review-16 pass" — "pass" reads as *passed* on first encounter, when Review 16 returned REVISE. The preceding sentence disambiguates, so this is a wording risk only.

**N3.** The provenance paragraph is already stale by one checkpoint: it cannot mention this review. Correctly, the paper claims no final independent approval, so nothing is overclaimed — but if a Review-17 line is added later, note that I verified the built PDF and the Review-15 correction, and did **not** verify rendered PDF text or re-run the test suite.

The empirical reporting remains clean, and the response to Review 16 was substantive rather than cosmetic — B2 in particular is disclosed more fully than it had to be. One inherited citation is the remaining defect.

VERDICT: REVISE — single blocking fix: reconcile the `zhang` bibliography entry (tex:98) with `papers/zhang_2024_advpo.md`, either by citing Kang & Oh (ICLR 2025, arXiv:2503.05306) as stored or by supplying the actual Zhang et al. AdvPO (arXiv:2403.05171) and correcting the venue. Everything else in Reviews 15 and 16 is verified applied.
