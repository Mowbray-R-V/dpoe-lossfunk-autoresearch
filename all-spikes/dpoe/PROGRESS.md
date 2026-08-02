# DPOE Autoresearch Progress

## Session 5 — Day 4 — 2026-07-21

- **Manual Review 17 — REVISE; single citation fix applied:** Reconciled the paper's
  inherited Zhang/AdvPO entry to the actual local source of truth: Kang and Oh,
  “Adversarial Policy Optimization for Offline Preference-Based Reinforcement Learning,”
  ICLR 2025, arXiv:2503.05306. The related-work sentence remains substantively correct
  under the corrected citation. Recompiled twice; the citation resolves as Kang and Oh
  (2025) in rendered text and no undefined citations/references remain. Per human
  instruction, the paper's reviewer-provenance paragraph was not extended with a
  Review-17 line.
- **Deck skeleton completed:** Added and compiled a 17-slide Beamer deck with the starting
  claims, customized Autovoila flow, compute de-scope, MVE 2/MVE 3 results and plots,
  closed claim table, proposed plan delta, exact prompt/user-decision appendix, reviewer
  highlights, cost/time actuals, and artifact map. The critique and reflection slides are
  clearly marked human-only placeholders and contain no agent-written critique or
  reflection. All slides were rasterized for visual inspection; post-layout checks covered
  the dense tables, appendix, and placeholder slides. Final: `deck/deck.pdf`.
- **Repository handoff completed:** Added `README.md` with artifact layout, analysis and
  reproduction commands, closed-scope warnings, paper/deck build commands, and an honest
  stage-by-stage human/AI intervention statement. Expanded the root `.gitignore` for the
  local paper library, environments, caches, Windows metadata, and LaTeX intermediates.
  `git check-ignore` confirms those categories are ignored; both final PDFs are explicitly
  not ignored and remain available for version control.

- **Review 15 audit correction — REVISE, not APPROVE:** When the manual file became
  available, it showed `VERDICT: REVISE`, contrary to the earlier human-reported APPROVE.
  Five Review-14 items passed; one stale `LEARNINGS.md` phrase still called the corrected
  v1 pilot “pilot-v2.” Corrected it to “Corrected v1 pilot.” This naming fix does not alter
  any result or reopen experiments. Review 15 has not yet independently re-verified the
  correction; experiments remain closed by the human's explicit decision, not by a
  nonexistent Review-15 APPROVE.
- **Final deliverables started with strongest driver model:** Completed the iterated
  research plan before paper drafting, with the complete evidence changelog,
  DriveReward-driven C1 reframing, closed C2/C3 statuses, the exact bounded wording
  not solvable within the preregistered grid, and retained deviations. Read the
  draft-format directory in full and saved paper-outline.md before drafting the
  CAISc-format negative/methods paper source at paper/dpoe_negative_result.tex. The source
  includes the claim table, appendices, AI-involvement and reproducibility checklists, and
  explicit Codex-driver/Claude-reviewer disclosure.
- **Paper PDF compilation environment blocked:** No LaTeX engine is installed. An approved
  escalation to install local TeX packages reached sudo, but this environment requires an
  interactive sudo password and rejected the non-interactive command. No workaround or PDF
  is claimed; source-level checks and reviewer request proceed, while PDF rendering awaits
  TeX installation or a user-provided build environment.
- **Final plan/paper reviewer checkpoint unavailable:** The redirected Claude Review 16
  request and its one permitted explicit retry both produced zero-byte captures
  (reviews/review-16-plan-paper.md and reviews/review-16-plan-paper-retry.md). No verdict
  is inferred and no further retry was made. The final plan and paper source retain the
  required reviewer checkpoint record; a usable manual review is still needed before the
  paper can be called independently reviewed.
- **Manual Review 16 — REVISE:** The human subsequently supplied `reviews/review-16.md`.
  Its numerical audit found no fabricated or drifted quantities, but it identified five
  blocking paper/plan issues: missing related work; incomplete disclosure of reviewer
  failures; three omitted deviations; a title that mislabeled untested C3 as a negative
  result; and uncompilable LaTeX. These are being corrected before PDF build. Review 16 is
  human-mediated reviewer output, not a successful recovery of the two empty CLI captures.
- **Review 16 fixes and paper build completed:** Added the missing related-work positioning
  (Cen, Park, Li, Zhai, Liang, Coste, Zhang, Kendall--Gal, and Liu); disclosed automated
  review failures and human-mediated manual reviews; added the Review-13 audit gap,
  per-severity-vs-aggregate quality-gate deviation, and learned-tier oracle-scale
  rescaling to both paper and iterated plan; retitled the paper away from “negative
  result”; reported v1's recorded-and-withdrawn kill and the favorable MVE-2
  epistemic-over-aleatoric contrast; and corrected the plan table, C1 deferral cause,
  bootstrap-linear scope, and surviving questions. The updated LaTeX compiles twice with
  no undefined citations/references, overfull boxes, or fatal warnings. The PDF is seven
  pages (four-page main paper, references/appendix, and required checklists), uses only
  embedded Type-1 fonts, contains the 2880x720 result figure, and all seven rasterized
  pages were visually inspected. Final PDF: `paper/dpoe_negative_result.pdf`.

- **Audit correction before Review 14 fixes:** The prior log said the four Review 13
  safeguards were applied because their text had been added to the amended protocol and
  one forward-looking gate-output field had been added to code. That check did not verify
  the safeguard against the actual failure path and persisted development artifacts: the
  re-entry bar was absent from the solvability-stop paragraph, the AUC identity test did
  not exercise the gate path, and the existing failed-grid artifacts predated the
  per-severity field. The statement was therefore incomplete and should not have been
  reported as full application. This is a factual audit gap, not a change to the v2 stop
  decision.

- **Session budget:** Human specified 4 hours after the required session bootstrap.
- **Review 13 safeguards applied:** The approved v2 protocol now explicitly bars any
  post-engagement grid re-entry without a new protocol, independent review, and human
  sign-off; treats sub-`delta` H3a effects as statistically real but practically null;
  records the normalized-AUC formula and flat oracle/none identity with its unit test; and
  makes the gate output retain per-severity oracle-minus-none return-AUC separations. The
  previously completed development grid was not rerun merely to regenerate summaries.
  The v2 protocol status was corrected to record its completed, preregistered solvability
  failure and the resulting bar on pilot/locked-v2 work. The v2 gate unit tests pass.
- **Review 14 re-verification unavailable:** Following the human-requested redirect
  capture pattern, `claude -p` was requested to re-verify the four safeguards and v2 stop
  decision into `reviews/review-14.md`. The file was zero bytes. One explicit retry,
  requesting a `VERDICT:` first line and captured as `reviews/review-14-retry.md`, was
  also zero bytes. Per the standing empty-response policy, no further retry was made and
  no APPROVE verdict is inferred. Final plan/paper work is paused pending a usable Claude
  verdict or a human-supplied manual review; this avoids proceeding past the critical
  review checkpoint without authorization.
- **Later Claude diagnostic and re-verification attempt:** At the human's direction,
  `claude -p "Reply with exactly: OK"` returned `OK`. A fresh redirected Review 14 request
  was then attempted, but `reviews/review-14.md` contains `API Error: Unable to connect to
  API (ENOTIMP)`, not a verdict. Treat this as another failed review rather than approval;
  no additional retry was made.
- **Manual Review 14 — REVISE; six blocking fixes applied:** The review correctly found
  that the prior Review-13 application was incomplete on the actual failed-gate artifact.
  The protocol now mirrors the no-re-entry-without-new-protocol/independent-review/human-
  sign-off bar in the solvability-gate paragraph. Gate and factorial analysis now share a
  single normalized-AUC implementation, and the identity test exercises a real update-free
  gate evaluation with `assertAlmostEqual`. Under the human-authorized report-only
  regeneration, the same 27 already-opened development scenarios were deterministically
  evaluated only to backfill per-severity return-AUC reporting; all prior metric fields had
  the identical SHA-256 fingerprint
  `0c38a4f4b062c844c8153796ac9f147b54b077ff8f7d61509f083bcd33a600bf`. It did not select,
  retune, expand the grid, or create pilot/locked-v2 seeds. The regenerated report corrects
  best-tuple source competence to 0.988, records the 1,000-episode gate configuration,
  discloses the non-binding historical fifth source-competence implementation guard, the
  boundary solution, and the skipped timing pre-check. The v1 corrected-pilot directory is
  renamed `mve3-pilot-corrected-v1` to avoid collision with v2-reserved `pilot-v2`.

- **Session budget:** Human previously specified 4 hours for this resumed Day 4 work.
- **Final human MVE 3 v2 implementation sign-off:** Human authorized implementation of
  the development-only tuning and solvability-gate machinery under `mve3-v2-protocol.md`,
  not tuning execution, pilot execution, or locked-v2 execution. Binding interpretation:
  if validity gates pass and full neither harms nor meaningfully beats its halves while
  the simultaneous I3 interval excludes a practically meaningful positive effect, report
  `no-support-for-conditional-c3-at-toy-scale-v2` as a negative claim result rather than
  uncertainty. Binding scope cutoff: if gates cannot pass by mid-day 6 under the fixed
  tuning budget, stop without gate iteration and ship C3 untested with its diagnosed cause.
  Locked-v2 execution, if separately authorized later, must resume from its last committed
  cell after interruption.
- **v2 development machinery implemented, not executed:** Added `mve3v2/gates.py` and
  tests. It enumerates the frozen 27-tuple anchoring/reward-clip grid on the isolated
  `development-v2` namespace; computes source-competence, oracle/none goal-success and
  true-return-AUC solvability metrics; applies the fixed lexicographic selection rule; and
  atomically writes a frozen configuration only after a pass. It refuses to open even
  development-v2 scenarios without `--execute-development`, and has no locked-v2 CLI path.
  Added `reward_clip` to the shared config with v1's unchanged default ±1.25 so v2 clips
  can be represented explicitly. Python compilation plus the v2 and existing MVE 3 suites
  passed (10 tests). No development tuning/gate, pilot, or locked-v2 seed was executed.
- **Human-authorized v2 development grid executed once:** Ran the complete fixed 27-tuple
  `development-v2` oracle/none solvability grid. It failed: no candidate met all gates, so
  the runner atomically recorded `results/mve3v2-development/development-solvability-failed.json`
  and refused pilot/locked-v2 work. The best oracle-reachability tuple
  (`tau_reference=0.18`, `beta0=0.10`, clip ±1.75) reached only 16.44% aggregate true-goal
  success (severity 1/2/3: 14.53%/15.60%/19.19%) and a 11.36-pp oracle-minus-none gap,
  below the 25%/15-pp requirements; its return-AUC separation (0.3485) and source
  competence (0.988) passed. Per the protocol and human hard-stop instruction, no grid
  extension, retuning, adaptation-engagement gate, pilot, or locked-v2 run will occur.
  C3 is untested with diagnosed solvability failure pending required Claude result review.

## Session 4 — Day 4 — 2026-07-21

- **Session budget:** Human specified 4 hours after the required new-session bootstrap.
- **Claude result-review recovery:** The previously unusable MVE 3 review artifact is now
  available as `reviews/review-08.md`. It returned **VERDICT: REVISE** with a blocking
  claim-calibration issue: the locked frozen-reference exploitation policy almost never
  reached the true goal, so the apparent H3a/H3b failures cannot kill C3. The required
  correction is to classify conditional C3 as uninformative/untested due to a design floor,
  surface true-goal-success diagnostics, and require a redesigned/re-preregistered run
  with an oracle-reachability manipulation check for any future C3 answer. No rerun is
  authorized or started.
- **Correction implemented and locally verified:** Added a post-review exploitation-floor
  diagnostic to `mve3/analyze.py`, regenerated the locked report/verdict, and corrected
  `LEARNINGS.md`. Controlled evaluation true-goal-success AUC averages 0.0004 (P+K+O
  0.0002); 98.7% of controlled cells are at or below 0.005. The verdict is now
  `untested-design-floor-policy-collapse`. Regeneration completed and all seven MVE 3
  unit tests pass. The new 1% floor is explicitly disclosed as a post-review diagnostic,
  not a new confirmatory criterion.
- **Claude correction-verification retry blocked:** A fresh non-interactive `claude -p`
  verification request was accepted and returned after about 29 seconds but emitted no
  text, so it produced no usable verdict. The original `review-08.md` remains the only
  independent review of this correction. Per `voila.md`, no further experiment or plan
  revision will proceed until a usable Claude verdict or human-supplied manual review is
  available.
- **Claude empty-response policy (human instruction):** Going forward, an empty-text
  Claude response is a failed review. Make at most one explicit retry, then escalate to
  the human; do not silently make further retries.
- **Review 09 failed after its allowed retry:** Following the human's report that the
  account-credit issue was resolved, sent the pending corrected-MVE-3 review request and
  then one explicit retry requesting a `VERDICT:` first line. Both calls returned after
  about 29 seconds with empty stdout and no usable verdict. Per the new policy, no more
  retries were made. `review-09` is therefore unavailable, and no post-correction plan or
  experiment decision has been taken.
- **Claude account root cause:** Human diagnosed the empty review responses as a Claude
  monthly-spend-limit issue, not a local environment failure. A minimal later diagnostic
  (`claude -p "Reply with the single word OK"`) returned `OK`, confirming basic CLI
  operation.
- **Human-provided Review 09:** `reviews/review-09.md` was subsequently added from the
  human's manual run with **VERDICT: REVISE**. Its blocking B1 required naming the C3
  reclassification as a post-review validity amendment and disclosing that the original
  preregistered kill rule fired but was overridden because its reachable-goal premise
  failed. Non-blocking requests were H3b floor-uninformative wording; per-tier/severity
  trap/goal statistics, minimum locked reference competence, learned-tier oracle-RMS
  rescaling disclosure; and a pointer to retained entropy/KL/terminal metrics.
- **Review 09 fixes applied and tested:** Regenerated `results/mve3-locked/RESULTS.md`
  and `verdict.json` from the amended analysis. The report now carries a “Verdict
  (post-review validity amendment)” section with the fired-rule disclosure; reports H3b
  as floor-uninformative; adds the requested scenario table, 1.000 minimum locked
  reference competence, learned-scale disclosure, and secondary-metric pointer. Updated
  `LEARNINGS.md` with the same amendment history. Python compilation, regeneration, and
  all seven MVE 3 unit tests passed.
- **Review 10 verification unavailable:** The initial Claude verification request and
  the one permitted explicit retry both returned empty stdout (raw output: empty). No
  verdict is inferred and no further retry is made under the human-specified policy.
- **Review 10 completed with prescribed long-timeout capture:** After the human supplied
  a response-text-only pattern, the first process remained live for roughly two minutes
  (not a timeout/kill) and exited **0** with a complete review. It is preserved at
  `reviews/review-10.md` and returned **VERDICT: APPROVE**: Review 09 B1 and all three
  requested non-blocking disclosures were verified. The Claude review itself noted four
  non-blocking cleanup items.
- **Review 10 cleanup:** Repaired the duplicated/dangling LEARNINGS sentence; made
  `preregistered_kill_rule_fired` reflect the actual gated rule rather than any H3a
  failure; stated the operative 0.0100 design-floor threshold alongside the descriptive
  0.005 fraction; disclosed the stricter per-severity rather than preregistered aggregate
  quality gate; and removed dead analysis code. Regenerated locked results and reran all
  seven MVE 3 tests successfully. No rerun has started.
- **Human authorization — v2 protocol only:** Human authorized drafting an amended MVE 3
  v2 protocol for review, explicitly not implementation or execution. Required elements:
  a preregistered oracle-reachability solvability gate that blocks locked-seed opening on
  failure; development-only anchoring/reward-range retuning frozen before any locked seed;
  an evidence-mapped delta table; and an answerable pre-run v2 null/kill rule. Drafted
  `mve3-v2-protocol.md`; no v2 code, pilot, development run, or locked seed has been
  opened.
- **MVE 3 v2 protocol review loop:** Claude Review 11 returned **REVISE** with five
  blocking decision-rule issues; Review 12 returned **REVISE** with one remaining
  factor-independent engagement-gate flaw. All were corrected in the draft: practical
  headroom-relative kill floor, return-AUC solvability headroom, adaptation-over-none
  engagement, direct-half rather than I3 kill inference, and symmetric severity evidence.
  Review 13 returned **APPROVE**. Its four non-blocking safeguards were incorporated:
  forbid post-engagement grid re-entry, practical support floor, frozen AUC-normalization
  formula/unit test, and per-severity return-headroom reporting. No execution authorization
  was inferred or used.

## Session 3 — Day 3 — 2026-07-20

- **Session budget:** Human specified 4 hours after the required new-session bootstrap.
- **Budget correction and human input:** Human reported that the prior session halted at a
  $20 API credit limit and that the limit is now raised by $30. Recorded driver-inference
  actual spend of approximately $20.00 in `BUDGET.md`; $30.00 remains under the $50.00
  sprint ceiling.
- **MVE 3 resume audit (outcome-blind):** The corrected `mve3-pilot-corrected-v1` was already
  complete at 480/480 cells and remains the valid pilot; the earlier `mve3-pilot` root
  remains debugging-only after its known factorial bug. Contrary to the interruption
  concern, `mve3-locked` is also complete: its resume ledger records 4,800/4,800 cells
  (50 replicates × 3 severities × 4 quality tiers × 8 P×K×O conditions), beginning this
  invocation with two cells already committed and finishing the remaining 4,798. No cells
  will be rerun. The prescribed locked integrity audit passed: zero missing, invalid,
  temporary, pairing, or scenario-violation files. The next uncompleted checkpoint is
  outcome analysis, followed by learnings and independent result review.
- **Locked analysis completed:** Generated locked summaries, quality gates, preregistered
  H3a/H3b contrasts, verdict, and factorial plot in `results/mve3-locked/`. Controlled
  uncertainty passed all locked quality thresholds (AUROC 0.850–0.924; Spearman
  0.647–0.710) and the leakage guard (partial Spearman 0.0124). Nevertheless, full P+K+O
  lost to O (-0.0021 true-return AUC; simultaneous CI [-0.0058, -0.0002]) and P+O
  (-0.0050, [-0.0130, -0.0005]), had a null I3 (-0.0000, [-0.0006, 0.0004]), and did not
  improve collection goal visitation. Both H3a and H3b therefore fail; the preregistered
  conditional C3 verdict is `killed-at-toy-scale`. Learned-bootstrap again failed its
  locked quality gate (AUROC 0.579–0.656; Spearman 0.133–0.220), so H3c is
  `untested-quality-gate-failed`. The frozen-MLLM C3 remains untested by design.
- **Cost/time:** MVE 3 local locked execution recorded 8,462.3 seconds (about 2.35 hours),
  below the 8-hour cap but above the outcome-blind pilot projection; monetary experiment
  cost remains $0.00. Updated `LEARNINGS.md` with the result, scope boundary, and
  projection discrepancy. Required next step: Claude Code result review before any
  additional experiment or plan revision.
- **Claude result-review checkpoint blocked:** Invoked `claude -p` three times for the
  required MVE 3 result audit (including one structured JSON retry capped at $1 on the
  Claude-side account). The CLI was installed and returned after 19–29 seconds each time,
  but emitted no text and left no usable review verdict. `reviews/review-08.md` records
  the failed checkpoint. Per `voila.md`, no self-review is substituted and no further
  experiment/plan decision will proceed until Claude Code returns review feedback or the
  human supplies a manual reviewer response.

## Session 2 — Day 2 — 2026-07-18

- **Session budget:** Human specified 8 hours after the required new-session bootstrap.
- **Bootstrap:** Re-read `voila.md` and this progress log in full before planning work.
- **Final human MVE 3 sign-off:** Human stated, “Final sign-off: implement and execute
  MVE 3 exactly under the approved protocol. Ensure the locked run can resume from the
  last completed cell after an interruption rather than restarting. Log this as a user
  decision.” Authorization covers MVE 3 implementation, development/pilot gates, and
  locked execution under `mve3-protocol.md`, at $0 local cost. MVE 1 remains unauthorized.
- **Checkpoint requirement:** A cell is one `(split, replicate, severity, quality tier,
  factorial condition)` run. Each completed cell will be written atomically and validated
  on resume; incomplete temporary files are ignored. A run-state ledger is updated after
  each atomic cell, so interruption repeats at most the current incomplete cell and never
  restarts completed cells.
- **MVE 3 implementation:** Added a deterministic binary-tree visual gridworld, source
  Q-learned reference, conjugate online reward posterior, signal-only quality tiers,
  independent collection/exploitation policies, full P×K×O factorial, separate frozen
  200-episode evaluations, BLAKE2b streams, per-cell compressed episode summaries, atomic
  cell commits, resume ledger, manifests, and five invariant tests under `mve3/`. All tests
  passed, including an interruption simulation that resumed after one completed cell.
- **Development gates:** Controlled uncertainty passed all three shifts (AUROC
  0.900–0.938; Spearman 0.723–0.745); source-policy competence min/mean 1.0; leakage
  partial Spearman 0.036; trap prevalence 0.90. Learned-bootstrap failed its preregistered
  gate (AUROC 0.581–0.644; Spearman 0.171–0.225), so H3c is descriptive/untested. Overall
  `proceed=true`; full report in `results/mve3-gates/development-gates.json`.
- **Pilot integrity gate caught a factorial bug before lock:** The first 480-cell pilot
  resumed correctly but failed pairing with 675 violations. Root cause: substring factor
  detection treated condition name `none` as O-present because `"o" in "none"`. No locked
  seed was opened and no result was interpreted. Replaced substring parsing with an
  explicit factor map, added `none` and non-O collector regression tests, and designated
  the original `results/mve3-pilot/` as debugging-only. The corrected pilot uses a new
  `mve3-pilot-corrected-v1/` root.
- **Corrected pilot and outcome-blind lock decision:** Corrected pilot deliberately stopped
  after two cells and resumed at cell three, then completed 480/480 cells. Integrity audit
  found zero missing/invalid/temp files, pairing violations, or scenario violations.
  Runtime/storage-only projection (no outcomes read) was 3,324.9 seconds and 84.3 MB for
  50 seeds, below the 8-hour/2-GiB caps; locked replicate count is therefore fixed at 50
  in `results/mve3-pilot-corrected-v1/locked-decision.json`.

### Session 2 plan

1. Implement the MVE 3 environment, posterior, factorial, quality tiers, hash streams,
   separate evaluation, atomic cell checkpoints, and invariant tests.
2. Run development quality/leakage/source-policy gates and a five-replicate full pilot.
3. Apply the preregistered symmetric runtime/storage rule before opening locked seeds.
4. Execute/resume the locked run, analyze C3, update learnings, and request result review.

## Session 1 — Day 1 — 2026-07-17

- **Session budget:** Human specified 3 hours.
- **Driver:** OpenAI Codex (GPT-5) for research design, analysis, and artifact work.
- **Bootstrap:** Read `voila.md` in full; no prior progress file existed; read
  `research-philosophy.md`, `research-plan.md`, `AGENTS.md`, and `CLAUDE.md` before
  substantive work.
- **Human decision:** Proceed with a three-hour Day 1 session. Planned scope: context and
  hardware audit, timeboxed freshness literature check, 2–3 falsifiable MVE proposals,
  Claude Code review, and presentation to the human for sign-off. No experiments will run
  before sign-off.
- **Fallback MVE sketches:** `mve-ideas.md` has deliberately not been read. The driver will
  design proposals independently first, as required by `voila.md`.
- **Hardware audit:** WSL2 Linux; AMD Ryzen 3 7320U, 4 physical cores / 8 logical CPUs;
  5.8 GiB RAM plus 4 GiB swap; about 952 GiB disk free; no `nvidia-smi` and hence no
  accessible NVIDIA GPU. Python 3.12.3 is present, but NumPy, SciPy, scikit-learn,
  PyTorch, Gymnasium, pandas, and Matplotlib are not installed in the system interpreter.
  Claude Code 2.1.209 is available. Consequence: local multi-billion-parameter MLLM
  inference and full visual RL are infeasible; MVE design must use CPU-light abstractions
  or request explicit approval for paid compute.
- **Spend:** $0.00. Hardware inspection used only local resources.
- **Freshness literature check completed:** Grounded arXiv search found four material
  2026 additions. Hahami et al. (arXiv:2606.09073) crowds the pessimistic aggregation
  contribution; VLM-AR3L (arXiv:2607.00483) and Large Reward Models
  (arXiv:2603.16065) crowd visual reward-guided RL; DriveReward
  (arXiv:2606.08525) reports a specialized 1B reward model beating larger VLMs, weakening
  the broad C1 surprise. Li et al.'s exploratory-bonus work is now ICLR 2026 and makes a
  naive UCB baseline insufficient. Full notes and URLs are in `literature-check.md` and
  implications are recorded in `LEARNINGS.md`. No paid service was used.
- **Independent MVE design completed before consulting fallback sketches:** Drafted three
  pre-registered, CPU-local proposals in `mve-proposals.md`: (1) a calibrated-small versus
  uncalibrated-large procedural visual reward-head crossover with calibrated-large and
  reward-scale controls; (2) epistemic/aleatoric/matched-noise Control A with a frozen-RM
  versus online-RM audit; and (3) a full P×K×O coupling factorial with Control D and a
  reward-hacking trap. Each states support, kill/weaken criteria, statistics, limits,
  runtime, and $0 cost. A key identified contradiction is that visits cannot reduce
  epistemic uncertainty in the submitted frozen-MLLM/no-target-label setup; MVE 2 tests
  this explicitly rather than assuming the active-learning rationale.
- **Fallback sanity-check consulted after independent proposal was saved:** Read
  `mve-ideas.md` only after the preceding draft existed. Its Ideas A/B converged with the
  offline calibration and synthetic coupling proposals. Adopted one explicit offline
  stop/go gate—epistemic uncertainty must predict target reward error better than shuffled
  uncertainty before any downstream result is interpreted—as human+Claude-originated
  input. Did not adopt its real-MLLM stretch run because 5.8 GiB RAM/no GPU makes it
  locally infeasible; cloud execution would require a new estimate and human approval.
- **Claude review 01:** Initial sandboxed call failed with `Unable to connect to API
  (ENOTIMP)`; retried with approved network access. Claude Code returned **VERDICT:
  REVISE** with four blocking issues: missing source-only calibration in MVE 1;
  non-operational correlation control in MVE 2's frozen arm; undefined reward-hacking
  events; and unspecified `pi_ref` in MVE 3. Review preserved at
  `reviews/review-01.md`.
- **Blocking review fixes applied:** Made source-only calibration the primary MVE 1
  contrast and target-probe calibration secondary; added decorrelated and anti-correlated
  frozen layouts; defined hacking event denominators; and specified a 2,000-episode
  source-pretrained frozen reference policy. Also added KL-coefficient sensitivity, the
  literal matched-uniform Control A, confirmatory families with multiplicity handling,
  explicit Control B non-coverage, and more conservative time estimates. No experiments
  run.
- **Claude review 02:** Verification pass returned **VERDICT: APPROVE**; no blocking
  issues remain. Preserved at `reviews/review-02.md`. Its four non-blocking clarifications
  were also incorporated before execution: frozen MVE 2 is the primary submitted-claim
  test and online updating is a separate revised-mechanism family; correlation-layout
  effects will be reported separately; `pi_ref` must meet an 80%-of-oracle development
  threshold; and MVE 1's corrected family spans 12 central-beta shift/contrast tests while
  adjacent beta values are exploratory sensitivity checks.
- **Human sign-off:** The human stated, “Approved, start MVE 2 now, log the sign-off.”
  Authorization covers MVE 2 under the reviewed CPU-local, $0 protocol. It does not
  authorize MVE 1, MVE 3, paid APIs, or cloud compute. Execution begins with dependency
  setup, implementation, and a development-only pilot; locked test results will follow
  only after the implementation and estimator gate are verified.
- **MVE 2 implementation and unit checks:** Added a NumPy-only procedural visual bandit,
  bootstrap reward-head ensemble, held-out residual aleatoric head, frozen/online regimes,
  all seven preregistered signals, three correlation layout families, raw trajectory-level
  metrics, and three unit tests under `mve2/`. All tests passed. NumPy and Matplotlib were
  installed in an ignored local virtual environment; monetary cost remains $0.
- **Offline estimator gate passed on development seeds:** 720 shifted points; epistemic
  error-rank Spearman 0.162 versus shuffled -0.029; top-quartile-error AUROC 0.532 versus
  shuffled 0.478; risk-coverage AUC 0.170 versus shuffled 0.189 (lower is better). The
  estimator clears the preregistered relative thresholds but absolute discrimination is
  weak, so any downstream interpretation must remain cautious.
- **Pilot caught and prevented a pairing violation:** The first three-seed pilot produced
  finite outputs but inspection found that decorrelated layout generation shared the
  signal-specific RNG, giving different true-reward permutations to different controls.
  Those pilot comparisons are invalid and are retained only as debugging output. Before
  opening locked test seeds, separated layout RNG from policy/control RNG and added a
  deterministic pairing regression test. No claim-level result was taken from the faulty
  pilot.
- **Seed-blinding correction before full run:** The corrected pilot passed all integrity
  checks (378 expected rows, no non-finite metrics, zero paired-layout violations), but a
  pre-test audit found it used seeds 100000–100002, which had been intended as the locked
  prefix. Those seeds are now considered opened and will not enter confirmatory results.
  Separated future pilots to development seeds 60000+ and, before execution, moved the
  untouched 50-seed locked block to 200000–200049. This change is logistical, not based on
  favorable outcomes.
- **MVE 2 locked run completed:** Untouched seeds 200000–200049, three shifts, three
  correlation layouts, two regimes, and seven signals produced exactly 6,300 unique rows
  in 257.7 seconds. Integrity checks found no missing/duplicate cells, non-finite metrics,
  or pairing violations. Results live in `results/mve2-full/`.
- **MVE 2 C2 verdict — frozen rationale structurally killed; broader claim unresolved with
  weak estimator:** Frozen epistemic tied point on the decorrelated layout (-0.0036, 95% CI
  [-0.0073, 0.0003]), helped only when uncertainty was aligned with reward, and harmed
  under a deliberately full-rank-reversed anti layout. This demonstrates a static prior,
  not information gain; aggregate anti-layout loss magnitudes are design artifacts, not
  natural effect sizes. Online updating showed no unique epistemic benefit, but the
  estimator's error AUROC was only 0.532 (Spearman 0.162), so it cannot cleanly adjudicate
  a stronger estimator. The transferable negative is that bootstrap-linear disagreement
  barely predicts error under this shift. The post-hoc total-minus-point diagnostic was
  also negative but is exploratory, not a corrected confirmatory result. Full statistics
  and plot: `results/mve2-full/RESULTS.md` and `results/mve2-full/returns_by_condition.png`.
- **Protocol disclosures after result audit:** Hacking uses all 160 one-step collection
  episodes, not a separate 200-episode evaluation phase (`eval_episodes` is unused);
  development scales use base rewards before layout permutation; and target-render seed
  arithmetic overlaps for a few seed/severity pairs. None breaks within-cell pairing or
  requires rerun, but all bound interpretation and will be corrected in future MVEs.
- **Time/cost actual:** MVE 2 through first analysis took about 58 minutes of session time;
  locked execution took 257.7 seconds; paid spend remains $0.00.
- **Claude result review 03:** Implementation/statistical audit found no bug requiring a
  rerun but returned **VERDICT: REVISE** on over-broad interpretation. Required the
  estimator-quality boundary and structural framing above. Review preserved at
  `reviews/review-03.md`; text fixes applied pending verification.
- **Claude result review 04:** Verification returned **VERDICT: APPROVE**. Estimator
  boundary, structural framing, anti-layout intervention strength, exploratory contrast,
  hacking denominator, scale timing, and seed-overlap disclosures are consistent and
  reproducible from the analysis generator. No rerun required. Preserved at
  `reviews/review-04.md`.
- **Human authorization for MVE 3 protocol revision (not locked execution):** Human
  approved proceeding toward MVE 3 subject to: update predictions from MVE 2 and condition
  coupling on signal quality/alignment; carry over hash-mixed seeds, a real evaluation
  phase, and defined hacking denominators; obtain Claude review; then return for final
  human sign-off. MVE 1 remains explicitly unauthorized.
- **MVE 2-driven MVE 3 delta preregistered:** Created `mve3-protocol.md`. Revised the
  question from unconditional coupling with a supplied signal to signal-quality-
  conditional coupling in an online-updated synthetic reward posterior. Added calibrated,
  learned-bootstrap, shuffled, and anti-aligned quality tiers; explicit AUROC/Spearman
  eligibility gates; moderation predictions; separate collection/exploitation and
  update-free 200-episode evaluation phases; exact proxy-trap/200 hacking denominator;
  BLAKE2b component seeds with a manifest; and explicit scope that even success does not
  validate submitted frozen-MLLM C3. This is a protocol change before any locked run.
- **Claude MVE 3 protocol review 05:** Returned **VERDICT: REVISE**. Blocking issues were
  possible truth leakage/undefined calibrated generator, undefined non-O collection
  policy confounding the factorial, and unpinned hacking/true-goal estimands. Review saved
  at `reviews/review-05.md`.
- **Review 05 fixes applied:** Specified a no-rejection conjugate generator with `u0`
  generated independently before environment truth, variance updates based on label
  receipt rather than correctness, module/test and partial-correlation leakage guards;
  fixed non-O mean-softmax collection independent of P/K; pinned hacking and true-goal
  visitation to normalized checkpoint AUC with a +0.02 hacking non-inferiority margin.
  Also preserved own-state decay in shuffled/anti controls, paired label noise by
  state/visit index, separated pilot hash tags, fixed terminology, and added a symmetric
  pilot-based 50-to-30 seed reduction rule. No implementation or locked execution
  occurred.
- **Claude MVE 3 protocol review 06:** Verified review-05 fixes but returned **VERDICT:
  REVISE** because shuffled/anti signals could ambiguously alter posterior-mean precision,
  confounding H3b. Review saved at `reviews/review-06.md`.
- **Review 06 fix applied:** Tier transformations now change only `u(s)` exposed to P/K/O;
  all tiers share identical calibrated-prior posterior-mean updates and a required equality
  unit test. Also defined absent-trap scoring/prevalence, required both development and
  locked quality thresholds, normalized reward/action-value notation, and required human
  rescoping if even 30 seeds exceed pilot runtime/storage caps. No implementation or locked
  execution occurred.
- **Claude MVE 3 protocol review 07:** Final verification returned **VERDICT: APPROVE**;
  no blocking issues remain. Review saved at `reviews/review-07.md`. Incorporated its two
  non-blocking safeguards: learned-bootstrap H3c must pass both development and realized
  locked quality thresholds, and controlled prior mean/scale/truth streams have explicit
  manifest component names. Revised protocol is ready for the required final human
  sign-off; no implementation or locked seed was opened.

### Next steps

1. Present the Claude-approved `mve3-protocol.md` to the human for final MVE 3 sign-off.
2. Do not implement/open MVE 3 locked seeds or start MVE 1 without explicit human sign-off.
4. Execute no paid call or cloud work without a separate estimate, budget entry, and
   explicit confirmation.
