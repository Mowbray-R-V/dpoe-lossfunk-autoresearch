# MVE 3 Revised Preregistration — Signal-Quality-Conditional Coupling

Status: **approved for implementation and locked execution on 2026-07-18** after Claude
review and final human sign-off. MVE 1 remains unauthorized.

Revision date: 2026-07-17. This document supersedes the original MVE 3 protocol in
`mve-proposals.md` wherever they differ.

## Evidence-driven delta from MVE 2

| Original MVE 3 assumption | MVE 2 evidence | Revision |
|---|---|---|
| A supplied epistemic signal is usable | Bootstrap-linear error detection was barely above chance (AUROC 0.532; Spearman 0.162) | Make signal quality a manipulated factor and gate any learned-signal claim |
| Optimistic visits can reduce ignorance with a frozen RM | Frozen uncertainty acted as a static prior; visits cannot update it | Primary mechanism test uses an online-updated reward posterior; frozen C3 as submitted remains structurally incoherent |
| One P×K×O factorial is enough | Benefits can reverse with uncertainty/error alignment | Cross the factorial with calibrated, learned, shuffled, and anti-aligned signal tiers |
| Ordinary integer seed arithmetic is sufficient | MVE 2 had cross-severity render-seed overlap | Use stable hash-derived component seeds and write a seed manifest |
| “Evaluation episodes” can share the training loop | MVE 2 accidentally measured hacking on collection steps | Add a separate, update-free 200-episode evaluation phase at every checkpoint |

## Revised question and claim scope

**Question:** In an online-updated synthetic visual reward model, does using the *same*
epistemic signal for pessimistic reward (P), uncertainty-adaptive trust region (K), and
posterior-sampling collection (O) produce a positive interaction **when and only when that
signal reliably predicts reducible reward error**?

This tests a revised, conditional form of **C3**. A positive result can support a toy
mechanism claim about an online reward posterior. It cannot support the submitted frozen-
MLLM claim, because MVE 2 showed that its information-acquisition premise is unavailable.

## Environment and online loop

- A small procedural visual gridworld has a source layout and three target shifts. Each
  target is designed with (i) low-reference-probability candidate goal branches and (ii)
  shorter candidate trap branches. The one-pass generative draw may yield a weak goal,
  non-tempting trap, or no non-positive terminal; never rejection-sample to force them.
- A tabular/linear softmax policy is sufficient; 16×16 rendered observations preserve the
  “visual shift” abstraction without claiming robotics fidelity.
- Train `pi_ref` on source ground-truth reward, then freeze it. Before test seeds open, the
  source learner must reach at least 80% of oracle source return over a separate 200-episode
  development evaluation within 10,000 training episodes. Failure stops the experiment;
  test seeds are never discarded or replaced.
- Target adaptation runs 100 iterations. Each iteration collects 16 episodes, receives a
  noisy simulated preference/reward label for visited terminal outcomes, updates the reward
  posterior, then updates the exploitation policy. Thus visits can reduce posterior
  uncertainty. True target reward is never supplied directly to the policy optimizer.
- Keep collection and exploitation policies logically separate. O changes collection; P
  and K change exploitation updates. Both consume the same online reward-posterior state.

## P×K×O factorial

Run all eight subsets of:

- Let `mu(s)` denote the posterior mean terminal reward; action values `Q_mu(s,a)` follow
  from planning under `mu`. **P — pessimistic reward:** `r_P(s)=mu(s)-lambda*u(s)`.
- **K — adaptive trust region:** `beta(s)=beta0*(1+eta*u(s))` in the KL penalty to the
  frozen source policy `pi_ref`.
- **O — posterior-sampling collection:** at each collection episode, draw one reward head
  with mean `mu(s)` and statewise spread `u(s)` and act greedily/stochastically against that
  sampled head. Always call this Thompson/posterior sampling; call it empirically
  optimistic only if uncertain-state visitation is measurably higher.

The **non-O collector is fixed and factor-independent**:
`pi_collect_nonO(a|s) proportional_to exp(Q_mu(s,a)/tau_collect)`, with one locked
development-tuned temperature. It is identical in none, P, K, and P+K cells and never uses
the exploitation policy, pessimistic reward, or adaptive KL. Likewise, the O collector is
identical across O, P+O, K+O, and P+K+O cells. Therefore P/K change exploitation only and O
changes collection only.

`lambda`, `eta`, update counts, label budgets, reward calls, and policy budgets are locked
on development layouts. Include a fixed UCB collector and reference-frequency-aware/GEB-
motivated collector as exploratory baselines; they are not part of the 2×2×2 interaction.

## Uncertainty-signal quality intervention

Every P/K/O pathway within a condition receives the identical `u(s)`. Cross the factorial
with four tiers:

1. **Controlled-calibrated (primary):** Use a conjugate normal posterior specified before
   target rewards are realized. For each state, first obtain source-only/generated prior
   parameters `mu0(s)` and `u0(s)` from independent component streams, then draw and freeze
   `r_true(s) ~ Normal(mu0(s), u0(s)^2)` as the environment truth. Thus `u0` controls error
   variance in the data-generating model but is never computed from a realized target
   reward or error. The algorithm receives only `mu0`, `u0`, states, and subsequent noisy
   labels—not `r_true` or realized error. Labels follow
   `y_t(s) ~ Normal(r_true(s), sigma_label(s)^2)`. Conjugate
   updates condition only on `(prior, state, visit count, received label values,
   sigma_label)`; posterior variance shrinks after **every received label**, independent of
   its value or correctness. No test seed is resampled to produce a tempting trap.

   After the one-pass joint draw, define the true goal as the highest-true-reward terminal
   on a low-reference-probability branch and the proxy trap as the non-positive terminal
   with highest initial proxy mean. Include seeds with a weak goal or non-tempting trap and
   report both strengths rather than replacing them. Development
   target: error-detection AUROC >=0.75 and Spearman >=0.50.
2. **Learned-bootstrap (transfer tier):** Bootstrap reward heads infer uncertainty from
   source/online visual features. It is eligible for a C3 learned-signal verdict only if a
   locked development gate reaches error AUROC >=0.70 and Spearman >=0.40 at every target
   shift. Confirmatory H3c additionally requires realized locked aggregate AUROC >=0.70
   and Spearman >=0.40; a locked miss makes H3c quality-invalid/untested without seed
   replacement. If either gate fails, run it descriptively but do not support or kill C3
   for this estimator.
3. **Shuffled-initial:** A fixed state permutation of initial calibrated `u0` preserves its
   marginal distribution and removes error alignment. Thereafter each state's reported
   uncertainty shrinks according to **that state's own** visit count with the same
   conjugate functional form, preserving own-state visit responsiveness.
4. **Anti-aligned-initial:** A fixed rank reversal of initial calibrated `u0` makes high
   reported uncertainty correspond to low posterior error. Thereafter it also shrinks by
   own-state visit count. This is a stress intervention, not a natural-effect estimate.

**Tier interventions are signal-only.** Every tier uses the same correctly specified
calibrated prior variance internally for conjugate posterior-mean precision updates and
therefore has the identical `mu` update given identical label history. Shuffled/anti
transformations alter only the reported `u(s)` consumed by P, K, and O's sampling spread.
They never alter `mu`, label likelihood, posterior-mean learning rate, or data. Unit tests
must confirm identical posterior means across tiers for identical visit/label histories.

### Truth-leakage guard

- Posterior construction/update modules may not accept true reward or realized error as
  arguments; only the environment/metrics module may access them. A unit test must show
  identical posterior-variance updates for two different label values at the same prior
  and visit count.
- Record generator order and component seeds in the manifest: `u0` is drawn before and
  independently of true reward and proxy error; no rejection sampling is allowed.
- On development and locked splits, report marginal and partial rank association of `u0`
  with true reward after controlling for `mu0` and source/visit count. If absolute partial
  Spearman exceeds 0.10 on the locked aggregate, mark the controlled tier leakage-invalid
  and do not claim H3a support; never resample seeds to repair it.

Quality is measured with absolute reward-mean error, top-quartile error AUROC, Spearman
rank correlation, and risk-coverage AUC. Development parameters may be repaired before
locking; locked seeds are never resampled to meet a gate. Report realized quality for every
tier and severity.

## Predictions fixed before execution

### H3a — high-quality conditional coupling (primary)

For controlled-calibrated uncertainty, predict that full P+K+O:

- has higher evaluation true-return AUC than P+K and O;
- degrades when P, K, or O is removed (full > P+O, K+O, and P+K);
- has a positive three-way interaction
  `I3=AUC(PKO)-AUC(PK)-AUC(PO)-AUC(KO)+AUC(P)+AUC(K)+AUC(O)-AUC(none)`;
- has higher collection true-goal visitation-rate AUC than P+K and lower evaluation
  hacking-rate AUC than O; and
- is non-inferior to P+K in hacking rate within a 0.02 absolute margin.

Prediction: the full-versus-P+K gain comes from O discovering informative states, while P
and K prevent O's uncertain proxy errors from dominating exploitation.

### H3b — signal-quality moderation (primary boundary test)

Predict `I3(controlled-calibrated) > I3(shuffled-initial)` and
`I3(controlled-calibrated) > I3(anti-aligned-initial)`, with simultaneous intervals excluding
zero. Full DPOE is not predicted to dominate under shuffled uncertainty and is predicted
to match or underperform under anti-alignment. Therefore, failure at weak/anti quality does
not by itself kill conditional C3; absence of moderation does weaken the causal story.

Across seeds/tiers, the exploratory prediction is a positive relationship between realized
error AUROC and the full-minus-best-half AUC contrast.

### H3c — learned signal (gated transfer test)

If and only if the learned-bootstrap tier passes its development gate, predict the H3a
directions for that tier. If it fails the gate, its coupling result is descriptive and
cannot support or kill learned-signal C3. MVE 2 makes gate failure plausible.

## Separate evaluation phase and hacking denominator

At iterations 0, 10, ..., 100, freeze the collection policy, exploitation policy, reward
posterior, and all counts. Run **200 evaluation episodes** with the exploitation policy:

- no posterior sampling or exploration bonus;
- no labels, reward-model updates, policy updates, or count updates;
- environment truth used only for metrics;
- fixed evaluation-randomness seeds paired across factorial conditions but disjoint from
  source training, target collection, model bootstrap, and plotting/bootstrap seeds.

A **reward-hacking event** is an evaluation episode terminating in the designated proxy
trap, whose true terminal reward is <=0. Hacking rate at a checkpoint is proxy-trap
terminations divided by exactly 200 evaluation episodes. Also report conditional proxy
return, true-goal success, timeout/collapse rate, policy entropy, and KL to `pi_ref`.
Reward-hacking AUC uses these evaluation checkpoint rates, never collection steps.

If a generative seed has no non-positive terminal, mark `trap_present=false`, set its
hacking numerator to zero without replacing the seed, and include it in the /200
denominator. Report trap prevalence/strength by tier and severity; a coupling claim cannot
rest on low hacking from absent traps or weak goals.

The confirmatory hacking estimand is **normalized trapezoidal AUC across the 11 checkpoint
rates (iterations 0–100)**. H3a predicts lower hacking-rate AUC for full versus O, and
non-inferiority of full versus P+K with absolute AUC margin +0.02. Final-checkpoint hacking
rate is secondary. Collection true-goal visitation is true-goal terminations divided by 16
collection episodes at each iteration; its normalized AUC is a confirmatory mechanistic
estimand for full versus P+K. Truth is used only to score this metric, never by collection.

## Seed and pairing protocol

Use a stable BLAKE2b-derived 64-bit seed from the tuple
`(protocol_version, split, replicate, severity, quality_tier, factorial_cell, component)`.

- Omit `quality_tier` and `factorial_cell` from layout, source-policy, true-reward, and
  evaluation-environment seeds so paired conditions see identical exogenous randomness.
- Include them for condition-specific policy sampling and posterior draws.
- Components include source training, target layout, label noise, reward bootstrap,
  collection dynamics, evaluation dynamics, analysis bootstrap, and plotting.
- Controlled-generator manifest components are explicitly named
  `controlled_prior_mean`, `controlled_prior_scale`, and `controlled_truth_draw`; all must
  resolve to distinct streams in the declared one-pass order.
- Write every resolved seed to `seed-manifest.csv`; assert uniqueness where independence is
  required and equality where pairing is required.
- Label-noise values are keyed by `(protocol, split, replicate, severity, state,
  visit_index, label_noise)` without quality/factorial fields. Conditions visiting the
  same state for the same ordinal time receive identical counterfactual label noise.
- Development split: replicates 0–19. Pilot split: replicates 0–4 with explicit
  `split="pilot"`. Locked test split: replicates 0–49 with `split="locked"`. Split tags
  enter the hash, so numeric replicate overlap cannot cause stream overlap.
- No locked test seed is opened before final human sign-off. Never replace a failed or
  unfavorable locked seed.

## Statistics and decision rules

- 50 paired locked seeds, three target severities, all eight factorial cells, and four
  signal-quality tiers. Report per-severity and aggregate results; aggregate each seed over
  severities before paired inference.
- Primary H3a family: full-minus-PK, full-minus-O, full-minus-PO, full-minus-KO, and `I3`
  on evaluation true-return AUC; full-minus-PK collection true-goal visitation AUC;
  full-minus-O evaluation hacking-rate AUC; and full-versus-PK hacking-AUC
  non-inferiority.
- Primary H3b family: `I3(calibrated)-I3(shuffled-initial)` and
  `I3(calibrated)-I3(anti-initial)`. H3c uses a separate family only if its gate passes.
- Paired seed bootstrap intervals with Bonferroni simultaneous 95% family coverage;
  paired permutation tests with Holm familywise 0.05; paired effect sizes alongside raw
  differences. Hacking non-inferiority passes only if its simultaneous upper confidence
  bound is below +0.02.
- H3a support requires all AUC directions and `I3` to pass in aggregate, the direction to
  agree in at least two of three severities, hacking lower than O, and hacking non-inferior
  to P+K. Low hacking achieved by never reaching the true goal is policy collapse, not
  support.
- “Controlled-calibrated passes” requires both the preregistered development gate before
  lock and realized locked aggregate AUROC >=0.75 and Spearman >=0.50. If locked quality
  misses either threshold, H3a is signal-quality-invalid/untested; never resample seeds.

### Pilot timing and symmetric reduction rule

Before locked seeds open, time all factorial/quality cells on the five-replicate pilot and
project locked runtime/storage. Stream per-episode summaries to disk; do not retain frames
or full trajectories in RAM. If projected locked runtime exceeds 8 hours or raw artifacts
exceed 2 GiB, reduce locked replicates symmetrically from 50 to 30 across every severity,
tier, and factorial cell before opening `split="locked"`. Make no outcome-based reduction
and log the projection and decision. Evaluation remains exactly 200 episodes.
If the 30-replicate projection still exceeds either cap, stop and request a new human-
approved scope; do not open locked seeds.

## Kill, weaken, and scope rules

- **Kill conditional coupling at toy scale:** controlled-calibrated signal passes its
  quality target, but full matches/loses to P+K or O, any component removal does not hurt,
  `I3` is non-positive, or the hacking/success guard fails.
- **Weaken causal coupling:** H3a passes but H3b moderation fails; full wins only against
  naive UCB; or results depend on one severity/hyperparameter.
- **Learned estimator unresolved:** learned-bootstrap fails its gate. Do not call its
  downstream failure evidence against epistemic coupling.
- **Submitted C3 remains untested:** even a positive result uses online target labels and a
  synthetic posterior, unlike the submitted frozen MLLM.

## Cost and decision gate

Estimated implementation and validation: 8–12 hours. Estimated locked CPU run and
analysis: 4–8 hours before pilot calibration. Dollar cost: **$0**. No paid API or cloud
compute.

Required sequence: protocol review -> blocking fixes -> human final sign-off ->
implementation/development pilot -> integrity audit -> locked run. Final sign-off was
received on 2026-07-18 with the additional requirement of cell-level interruption resume.
