# Pre-registered Minimum Viable Experiment Proposals

Status: **proposal only; do not execute before reviewer clearance and human sign-off.**

Designed independently from `research-plan.md` on 2026-07-17. At the time this draft was
written, the driver had not read `mve-ideas.md`. These are mechanism stress tests, not
substitutes for experiments with an actual MLLM, robot simulator, or natural visual shift.

**Post-draft fallback sanity check:** After preserving the independent draft, the driver
read `mve-ideas.md`. Its Ideas A/B independently converged on offline calibration checks
and a synthetic coupling environment. One concrete addition taken from that file is the
offline estimator-validity gate below; this is human+Claude-originated input, not an
independent driver contribution. Idea C (one real MLLM loop) is infeasible on the audited
host and is not proposed without separately approved cloud compute.

## Shared protocol and scope

- Generate procedural 16×16 grayscale “observations” containing shape, texture, and
  position. Source data has a spurious texture/reward correlation; target generators
  weaken, reverse, or replace that correlation and perturb position/contrast. Ground-truth
  task reward is used only for simulated labels where a condition explicitly permits it
  and for evaluation, never silently as a training reward.
- Use CPU-light NumPy/scikit-learn models and tabular policies. Install only free local
  dependencies after approval. No API or cloud spend.
- Split random generators into development instances for hyperparameter selection and
  locked test instances for results. Never tune on test seeds. Store every config and raw
  per-seed trajectory.
- Use at least 50 independent seeds where the tabular runs remain sub-second; otherwise
  reduce only after timing a pilot and state the reason. Report means with paired
  seed-bootstrap 95% confidence intervals, paired effect sizes, and the pre-registered
  contrasts below. Curves are summarized by normalized true-return AUC and time/steps to a
  fixed success threshold. Also report target NLL, Brier score, adaptive-bin ECE, reward
  hacking rate, visitation, policy entropy, and KL to the reference where applicable.
- ECE is descriptive and bin-sensitive; NLL/Brier are primary calibration metrics.
- Comparisons explicitly named in each support criterion are confirmatory; other contrasts
  and sensitivity sweeps are exploratory. Within each MVE, use paired permutation tests
  with Holm correction at familywise 0.05 and paired bootstrap intervals Bonferroni-
  adjusted to simultaneous 95% coverage. Also report unadjusted effect sizes and intervals
  as descriptive quantities.
- **Offline stop/go gate (added from fallback Idea A):** before policy training, measure
  whether epistemic uncertainty predicts absolute reward error on held-out target data
  (rank correlation, error-detection AUROC, and risk-coverage curve), separately from
  aleatoric uncertainty. If it is no better than shuffled uncertainty, do not interpret a
  downstream bonus result as evidence for calibrated epistemic uncertainty; either repair
  the estimator on development data or record C2 as untestable with that estimator.
- Repeat key comparisons over three target-shift severities. A result on this procedural
  family can falsify the proposed mechanism or expose implementation contradictions, but
  cannot validate claims about MLLM scale, semantics, or real visual robotics.

## MVE 1 — Calibration/capacity crossover under procedural visual shift

### Question and claim

Tests **C1** at reward-head scale: can post-hoc calibration, independently of raw predictive
capacity, cause a smaller reward model to drive better KL-regularized policy adaptation
than a more flexible but miscalibrated model?

Train a small linear reward/preference head and a larger two-layer MLP on identical source
observations and labels. Select a setting in development instances—not test instances—in
which the larger model has higher target pairwise accuracy but worse probabilistic
calibration. For the primary, protocol-faithful contrast, fit a one-parameter temperature
on held-out **source-domain labels only**. Separately fit temperature on a fixed, small
labeled target probe as a secondary, explicitly label-assisted condition. The downstream
contextual-bandit policy receives reward-model outputs and updates with a fixed KL penalty
to the source policy.

Conditions:

1. small raw;
2. small source-temperature-calibrated;
3. large raw;
4. large source-temperature-calibrated (**Control C**);
5. small and large target-probe-temperature-calibrated (secondary labeled conditions);
6. each raw model with an affine reward-scale transform matching each calibrated output's
   mean and variance, without using labels (smoothing/scale control);
7. oracle true reward as a ceiling and constant/point reward as a floor.

Model inputs, training examples, policy optimizer, policy steps, and number of reward calls
are identical across paired conditions. Record parameter counts and wall-clock separately;
this is not a literal MLLM matched-compute ladder.

### Support criterion fixed before running

C1 receives toy-scale support only if, across at least two of three held-out shift
severities:

- large-raw retains strictly higher target pairwise accuracy than
  small-source-calibrated;
- small-source-calibrated has lower target NLL/Brier and higher true-return AUC than
  large-raw, with the simultaneous interval for the AUC difference excluding zero; and
- large-source-calibrated is no worse than small-source-calibrated, while scale-matched
  raw controls do not reproduce the calibrated condition's AUC gain.

The confirmatory family is small-source-calibrated versus large-raw,
small-source-calibrated versus small-raw, large-source-calibrated versus large-raw, and
small-source-calibrated versus its scale-matched raw control, crossed with all three shift
severities at central `beta` (12 corrected comparisons in one MVE 1 family). Repeat at
locked `beta/2` and `2*beta` as exploratory sensitivity analyses and report all results;
do not select a coefficient from test performance.

### Kill or weakening criterion

- **Kill the tested C1 mechanism:** calibration improves NLL/Brier but not true-return AUC;
  large-raw matches/beats small-calibrated; or simple affine scale matching reproduces the
  gain.
- **Weaken/reframe:** small-calibrated wins only because the larger model loses target
  accuracy or in only one hand-selected shift. If target-probe calibration wins but
  source-only calibration does not, conclude that calibration transfer fails and labeled
  target adaptation—not the submitted protocol—is required. This is an existence result
  for this architecture/shift family, not a prevalence claim or evidence that calibration
  beats MLLM capacity. The full matched-wall-clock Control B remains untested.

### Estimate

Implementation 4–6 hours; execution/analysis 30–90 minutes on the audited CPU; **$0**.

## MVE 2 — Epistemic vs aleatoric vs matched-noise exploration, with a frozen-model audit

### Question and claim

Tests **C2** and the plan's **Control A**. Construct a forked visual contextual bandit with:

- a rarely sampled region where the reward posterior has high reducible epistemic
  uncertainty and contains potentially high true reward; and
- a frequently sampled region with known mean reward but input-dependent stochastic
  labels, producing high irreducible aleatoric uncertainty.

Estimate epistemic uncertainty as bootstrap-head variance and aleatoric uncertainty with a
heteroscedastic label-noise head. Calibrate both on development data. Compare otherwise
identical collection policies driven by:

1. epistemic uncertainty;
2. aleatoric uncertainty;
3. total uncertainty;
4. zero uncertainty / point reward;
5. seed-paired shuffled uncertainty preserving the empirical magnitude and marginal
   distribution;
6. uniform noise matched to the epistemic bonus RMS (**literal Control A**);
7. generic count-based novelty.

Crucially run two regimes:

- **Frozen RM (faithful to the submitted plan):** visits do not update the reward model.
- **Online RM:** visits receive a simulated preference label and update the reward head.
  This tests the active-learning rationale but is explicitly a proposed plan change.

All bonuses are normalized to the same RMS magnitude and share a locked decay schedule.

For the frozen arm, cross the comparison with three pre-generated layout families:

- **aligned:** epistemic rank is positively correlated with true-reward rank;
- **decorrelated:** permute true-reward assignments until absolute Spearman correlation
  with epistemic uncertainty is below 0.05;
- **anti-correlated:** give the highest-epistemic region median-to-low true reward and
  require Spearman correlation below -0.5.

Generate these layouts before policy runs and pair them across methods. A frozen-regime
advantage counts as signal-specific only if it remains positive on average over the
decorrelated and anti-correlated families, does not increase low-reward uncertain-state
visitation, and beats shuffled and matched-uniform controls under simultaneous intervals.
An aligned-only gain is a static correlation artifact, not C2 support.

Under the static-correlation explanation, the pre-registered expected signs for the frozen
epistemic effect are positive in aligned layouts, approximately zero in decorrelated
layouts, and negative in anti-correlated layouts. Report all three family-specific effects
and intervals, not only their aggregate.

A **reward-hacking event** in MVE 2 is an evaluation episode selecting an action whose
frozen proxy mean is in the layout's top quartile while its true expected reward is in the
bottom quartile. Hacking rate is such episodes divided by all evaluation episodes for that
seed and checkpoint.

### Support criterion fixed before running

C2's **primary confirmatory family is the frozen-RM regime**, because that is faithful to
the submitted claim. C2 receives toy-scale support only if epistemic-only beats
aleatoric-only, shuffled,
matched-uniform, count-based, and point conditions in true-return AUC with simultaneous
intervals excluding zero,
and does so without a higher reward-hacking rate. In the online regime it must also reduce
held-out reward-posterior error faster per acquired label. Online-RM comparisons are a
separate confirmatory family for the *proposed revised mechanism* and cannot support the
submitted frozen-RM C2. A robust frozen-regime benefit must persist after controlling the
correlation between uncertainty and true reward.

### Kill or weakening criterion

- **Plan kill-switch:** if aleatoric-only or total uncertainty matches/beats epistemic-only,
  abandon “only epistemic”; if total wins, reframe to calibrated total uncertainty.
- If shuffled matched-magnitude uncertainty ties epistemic, attribute the effect to
  smoothing/random exploration rather than epistemic information.
- If epistemic helps only with online RM updates, the frozen-MLLM rationale is killed: the
  iterated plan must add target feedback/reward-head updating or replace the
  information-gain story with an explicitly static novelty prior.
- If epistemic helps only because it was constructed to correlate with the optimal region,
  C2 is untested rather than supported.

### Estimate

Implementation 4–6 hours; execution/analysis 30–90 minutes; **$0**.

## MVE 3 — Factorial coupling test in a reward-hacking gridworld

**Revised after MVE 2:** The canonical preregistration is now `mve3-protocol.md`. It
supersedes this original section where they differ. In particular, MVE 3 now predicts a
positive P×K×O interaction only conditional on an uncertainty signal that reliably tracks
reducible reward-model error. It crosses the factorial with controlled-calibrated,
learned-bootstrap, shuffled, and anti-aligned signal tiers; uses an online-updated reward
posterior; hash-mixes component seeds; and has a separate 200-episode evaluation phase
with an exact hacking denominator. No locked run is authorized pending renewed human
sign-off after Claude review.

### Question and claim

Tests **C3** and **Control D**: is there a positive interaction from using one epistemic
signal for pessimistic reward, uncertainty-adaptive policy constraint, and optimistic data
collection, rather than merely an additive benefit from one component?

Use a small visual gridworld with two target-domain branches: an initially rare route to
the true goal and a proxy-reward trap whose reward-model mean is high but whose posterior
is uncertain. Keep separate collection and exploitation policies so “optimism for data
collection” is not silently combined with the reward optimized for deployment.

For each seed, train reference policy `pi_ref` for 2,000 episodes on the unshifted source
layout using source ground-truth reward, then freeze it before target adaptation. Use the
identical frozen `pi_ref` in all paired target conditions and report its source and target
true return. Thus K is a trust region to the source policy, not uncertainty-weighted
entropy regularization.

Before opening test layouts, require the source-learning procedure on development layouts
to achieve at least 80% of oracle source return over 200 evaluation episodes within at
most 10,000 training episodes. If it cannot, stop MVE 3 and repair the learner on
development layouts; do not discard or replace unfavorable test seeds.

Run the full 2×2×2 factorial over:

- **P:** pessimistic reward, `mean − λ·epistemic_SD`;
- **K:** statewise KL coefficient, `β(s)=β0·(1+η·epistemic_SD(s))`;
- **O:** episode-wise posterior/Thompson sampling for the collection policy.

This includes point, P-only, K-only, O-only, all pairwise combinations, and full P+K+O.
Add pessimism-only (P+K) and optimism-only (O) as the named Control D comparison, plus a
locked UCB bonus and a reference-frequency-aware exploratory baseline motivated by GEB.
Use the same posterior samples and paired environment seeds across conditions. Lock λ, η,
and exploration schedules on development layouts, and report a sensitivity grid rather
than choosing the best test result.

A **reward-hacking event** in MVE 3 is an evaluation episode terminating in the designated
proxy trap, which has non-positive true terminal reward but a high learned proxy mean.
Hacking rate is proxy-trap terminations divided by all evaluation episodes for that seed
and checkpoint. Also report proxy return conditional on hacking.

### Support criterion fixed before running

C3 receives toy-scale support only if the controlled-calibrated tier passes its quality
target and:

- full P+K+O has higher true-return AUC than both P+K and O, with both simultaneous
  intervals excluding zero;
- removing any one of P, K, or O degrades AUC; and
- the factorial interaction contrast
  `AUC(PKO)-AUC(PK)-AUC(PO)-AUC(KO)+AUC(P)+AUC(K)+AUC(O)-AUC(none)`
  is positive with a simultaneous interval excluding zero, while full DPOE does not increase
  proxy-reward hacking.

The confirmatory family contains full-versus-P+K, full-versus-O, each of the three
single-component removals, the three-way interaction, and full-versus-none hacking rate.
All other pairwise comparisons and lambda/eta sweeps are exploratory.

### Kill or weakening criterion

- **Kill coupling:** pessimism-only or optimism-only matches full; the three-way interaction
  is non-positive; or K has no marginal benefit once P is present.
- **Weaken:** full wins only for one hyperparameter/layout, only against naive UCB but not
  Thompson/GEB-motivated collection, or by suppressing all exploration and never reaching
  the true goal.
- Any posterior-sampling benefit is called Thompson/posterior sampling, not guaranteed
  optimism, unless its sampled policies measurably favor uncertain actions.
- MVE 2 delta: learned-signal failure is uninformative if error AUROC <0.70 or Spearman
  <0.40. The controlled-calibrated interaction must exceed shuffled and anti-aligned
  interactions; otherwise the coupling explanation is weakened even if full DPOE wins.
- Even a positive revised MVE 3 result does not support the submitted frozen-MLLM C3,
  because the revised mechanism receives online target labels.

### Estimate

Revised implementation 8–12 hours; execution/analysis 2–4 hours; **$0**.

## Recommended order and decision gate

1. Run MVE 2 first because it tests a logical precondition of the frozen-reward proposal.
   A frozen/online split result can prevent spending time on a coupling mechanism whose
   information-gain rationale is unavailable.
2. Run MVE 3 next if MVE 2 yields a usable uncertainty signal; otherwise use MVE 3 chiefly
   to document the failure mode.
3. Run MVE 1 last. It is the weakest proxy for the submitted capacity claim and must never
   be described as evidence about Qwen 3B versus 32B.

After reviewer feedback, the human may approve all three, select a subset, or reject the
toy abstraction in favor of separately budgeted real-model/cloud work. No execution begins
until that decision is logged.
