# Iterated Research Plan (Proposal) — Calibrated Reward Uncertainty Under Domain Shift

Status: **agent-proposed revision, pending human decision.** This is not a replacement for
the submitted plan. It incorporates the closed MVE 2 result, MVE 3 v1 validity amendment,
and the MVE 3 v2 preregistered development-stop result. Experiments are closed; MVE 1 did
not run.

## Changelog: evidence to revision

| Evidence | Proposed change |
|---|---|
| MVE 2 frozen reward-model arm: visits cannot update a frozen model; apparent benefit followed static uncertainty/reward alignment | Remove the claim that frozen-MLLM exploration reduces epistemic uncertainty. Treat frozen MLLM uncertainty as a risk/selection signal, not an active-learning mechanism unless labels update the model. |
| MVE 2 learned bootstrap: error AUROC 0.532, Spearman 0.162; no unique online epistemic benefit | Replace “epistemic-only” with a calibrated-estimator eligibility gate. Do not claim an epistemic mechanism from a near-chance estimator. |
| MVE 3 v1 controlled signal passed quality but exploitation could not reach the goal; its original kill rule fired in that degenerate regime | Reclassify v1 as untested via a disclosed post-review validity amendment. Require oracle reachability, return headroom, and adaptation-over-none gates before interpreting a coupling factorial. |
| MVE 3 v2 complete 27-tuple development grid | No tuple met oracle success/none-separation gates. C3 remains untested: **not solvable within the preregistered grid**, not globally unsolvable. The boundary best tuple must not trigger outcome-driven retuning. |
| Reviews 08–15 and report-only audit | Make practical floors, factor-independent engagement, and symmetric support/negative rules preregistered; bar grid re-entry after either solvability or engagement failure without a new protocol, independent review, and human sign-off. Retain report-only metric audits and disclose deviations. |
| Freshness check, including DriveReward | Narrow C1 novelty away from “small beats large.” Isolate calibration from specialization, reward rescaling, data, capacity, and matched compute. Narrow novelty away from generic visual reward RL and pessimistic aggregation. |
| Hardware audit (no GPU, 5.8 GiB RAM) and explicit non-authorization of MVE 1 | Defer C1 rather than substituting an unfaithful local proxy. Preserve it as an untested full-scale question with paid-compute and control requirements. |

## 1 THE WHAT

### Claims after the sprint

1. **C1, calibration versus capacity:** untested at this scale. The sprint did not run a
   calibrated-small versus uncalibrated-large MLLM comparison. It is retained only as a
   full-scale empirical question, with calibrated-large and matched-compute controls now
   mandatory.
2. **C2, epistemic signal:** the submitted frozen information-acquisition rationale is
   structurally false: policy visits cannot reduce uncertainty in a frozen reward model.
   The broader claim that a strong calibrated epistemic estimator helps online reward-model
   adaptation is unresolved, because the tested bootstrap estimator barely discriminated
   target error.
3. **C3, coupled P/K/O:** untested at toy scale. v1 is untested because its
   trust-region/reference arithmetic made exploitation nearly unable to reach the target
   goal. In v2, no candidate passed the preregistered oracle reachability/none-separation
   gate; the boundary best tuple reached 16.44% oracle goal success and an 11.36-pp gap,
   below 25% and 15 pp. The result is **not solvable within the preregistered grid**, not a
   coupling null or a global impossibility claim.

### Revised one-sentence claim

For visual-domain adaptation, uncertainty should be used for coupled pessimism and
exploration only after it passes calibration, reachability, and adaptation-engagement
checks; a frozen reward model alone cannot supply the information-gain mechanism.

### C3 final line — filled from v2 development outcome

| Observed v2 outcome | Proposed C3 conclusion |
|---|---|
| Complete preregistered development grid: no tuple passed oracle reachability/none-separation | C3 remains **untested at toy scale**. The diagnosed obstacle is not a post-hoc factorial result but that the task was **not solvable within the preregistered grid**. The best tuple was on the relaxation boundary; do not iterate the gate, retune, or imply a coupling result. |

## 2 THE WHY

The useful scientific contribution shifts from “calibration beats capacity” to an honest
decision procedure: establish that an uncertainty signal predicts error, that the policy
can act on a known goal, and that adaptation exceeds the reference baseline before reading
a factorial interaction. This is useful for MLLM-as-reward work because a plausible-looking
uncertainty method can otherwise produce static priors, policy collapse, or tie-level
effects that masquerade as a coupling result.

## 3 THE HOW

### Revised full-scale experimental sequence

1. Audit reward-model error prediction and calibration on target data; gate estimator-level
   claims by target error AUROC/Spearman and calibration error.
2. Separate frozen-RM risk control from online-RM active learning. Only the latter may claim
   that exploration reduces reward uncertainty.
3. Before a coupling factorial, run an oracle-versus-none reachability and return-headroom
   check, then a factor-independent adaptation-over-none engagement check.
4. Use full P×K×O versus all component removals with shared signals, paired seeds, separate
   collection/evaluation, explicit hacking denominators, and practical effect floors.
5. Run C1 only once a realistic MLLM stack is available: calibrated-small, uncalibrated-
   large, calibrated-large, matched compute, source-only versus target-probe calibration,
   and specialization/data/reward-scale controls motivated by DriveReward.

### Decision rules

- A weak epistemic estimator cannot support or kill an epistemic mechanism.
- A frozen reward model cannot support an information-gain explanation.
- A coupling null can kill C3 only after solvability, return-AUC headroom, leakage,
  estimator-quality, and adaptation-engagement gates pass.
- A practical near-null is a negative result when it excludes meaningful full-over-half
  benefit; an invalid gate is untested, not negative.
- A failed bounded solvability grid says only “not solvable within the preregistered grid.”
  Any extension is a new experiment requiring a new protocol, independent review, and
  human sign-off.

### Full-scale controls retained

Control A remains epistemic versus aleatoric, point, matched-uniform, and shuffled signals.
Control B remains matched-compute capacity comparison. Control C now requires calibration of
both model sizes. Control D retains the complete coupling factorial but inherits v2’s
oracle-reachability and practical-headroom gates.

## 4 THE SO WHAT

The proposal is more falsifiable than the submitted plan. Its strongest transferable
finding is specific: frozen uncertainty behaved as a static alignment prior, and the tested
bootstrap-linear disagreement score barely predicted shifted reward error. Neither result
establishes an active epistemic-exploration mechanism. A future positive coupling result
must clear explicit evidence that the policy can exploit what it discovers; a future valid
null will be reported as a real constraint on the claim.

### Surviving research questions

The original questions on calibration-transfer sample complexity and MLLM-size thresholds
survive, but now require specialization/data controls and a realistic compute environment.
The question about recovering an active-learning oracle survives only for an online-updated
reward model; it is inapplicable to a frozen MLLM. The task-dependence question survives as
a comparison of valid uncertainty estimators after estimator-quality gates. The original
250–350 hour non-automatable estimate was not tested by this sprint and is withdrawn pending
a full-scale hardware and staffing estimate.

## What Only I Can Do — updated from sprint evidence

- The human must decide whether a toy result changes the strategic value of an expensive
  MLLM/robotics run and whether C1 merits paid compute after C2/C3 gates.
- The agent can implement paired, resumable, auditable toy experiments and catch arithmetic,
  pairing, and interpretation failures; it struggled to obtain external review while the
  reviewer account was credit-limited.
- Human judgment remains necessary to distinguish a scientifically meaningful mechanism
  from a well-instrumented synthetic proxy, and to choose any real-world deployment domain.

## Current cost and scope position

The sprint has spent approximately $20 of the $50 ceiling on driver inference; local MVEs
cost $0. MVE 3 v2 stopped at its fixed development gate; no pilot or locked-v2 seed was
opened. The full MLLM plan remains uncosted/unapproved and should not be initiated without
a separate estimate, hardware plan, and human approval.

## Preregistration and reporting deviations retained in the proposal

- MVE 3 v1's preregistered C3 kill rule fired, but independent review found its reachable-
  goal premise false. The post-review validity amendment reclassified it as untested;
  neither the v1 contrasts nor H3b floor-level moderation are a C3 conclusion.
- In v2, an original implementation included a non-binding fifth development guard
  (source competence >=0.80) although the written gate listed four conditions. It was
  non-binding (minimum 0.988) and was removed from the decision code.
- The required costliest-tuple timing pre-check was skipped before the completed v2 grid.
  This is a disclosed protocol deviation; it did not change the stop rule or open later
  namespaces.
- The development artifact was regenerated report-only to add per-severity return-AUC
  fields. Its pre-existing metrics had identical fingerprints before and after; it did not
  extend the grid, retune, or open any new seed.
- The v1 locked quality gate was implemented per severity although the preregistration
  specified an aggregate gate. This was stricter; all controlled severities passed, so it
  did not favor the reported outcome.
- The learned uncertainty tier was RMS-rescaled to controlled prior uncertainty using the
  generator's `u0`, which exposes oracle-scale information. That tier failed its quality
  gate and supports no claim.
- The driver initially reported four Review-13 safeguards as fully applied without checking
  the actual solvability-failure path and persisted artifact. The audit log was corrected,
  and Review 14 required the missing changes.
