# DPOE Sprint Learnings

This file records claim-level evidence, surprises, limitations, agent/human division of
labor, cost/time calibration, and novelty updates.

## Feasibility and process

- **Local-compute constraint (2026-07-17):** The available machine has 4 CPU cores,
  5.8 GiB RAM, and no accessible NVIDIA GPU. The full MLLM-plus-visual-RL proposal cannot
  be approximated faithfully on this host. The sprint must distinguish mechanism-level
  toy tests from evidence about actual MLLMs and visual domain shift.
- **Agent capability:** Codex completed repository bootstrap, instruction synthesis, and
  local hardware/software auditing without human intervention beyond the required session
  duration.
- **Human input:** The human allocated three hours for Session 1. No research-design or
  experiment-selection decision has yet been requested.

## Claim status

| Claim | Current verdict | Evidence |
|---|---|---|
| C1: calibration > capacity | Untested | No MVE executed |
| C2: epistemic is the signal | **Frozen rationale structurally killed; broader empirical claim unresolved with a weak estimator** | Bootstrap-linear epistemic error AUROC was only 0.532. Frozen effects followed static uncertainty/reward correlation; online updating showed no unique benefit but cannot cleanly test C2 with near-chance discrimination. |
| C3: pessimism/optimism coupling | **Untested at toy scale — v1 design floor and v2 preregistered solvability-gate failure; submitted frozen-MLLM C3 remains untested** | v1 factorial contrasts were invalidated by policy collapse. The complete v2 development grid could not make the oracle reach the goal >=25% or separate from none by >=15 pp, so the protocol stopped before pilot/locked seeds. |

## MVE 3 — Signal-quality-conditional P×K×O coupling

- **What was tested:** A preregistered synthetic binary-tree visual gridworld with an
  online conjugate reward posterior, separate collection and frozen 200-episode evaluation
  phases, 50 locked paired seeds, three target severities, four uncertainty-quality tiers,
  and the complete P×K×O factorial. This is an online-posterior mechanism test, not an
  MLLM or frozen-reward-model experiment.
- **Execution integrity:** Corrected v1 pilot completed 480/480 cells before the locked
  decision. The locked run completed all 4,800/4,800 cells and its post-run audit found
  zero missing, invalid, temporary, pairing, or scenario-violation files. The earlier
  `mve3-pilot` remains debugging-only because a detected factor-parser bug invalidated its
  factorial pairing before lock.
- **Signal validity:** Controlled uncertainty cleared every locked severity gate (AUROC
  0.850/0.924/0.899; Spearman 0.647/0.710/0.708); the leakage partial Spearman was 0.0124,
  within the ±0.10 guard. Therefore the primary negative is not explained by a failed
  controlled-signal quality gate. Learned-bootstrap failed all realized quality thresholds
  (AUROC 0.579–0.656; Spearman 0.133–0.220), so H3c is quality-invalid/untested rather
  than evidence against a usable learned epistemic estimator.
- **Primary H3a result:** Full P+K+O versus P+K was only +0.0005 true-return AUC
  (simultaneous CI [0.0000, 0.0014], Holm p=0.0892); it lost to O by -0.0021
  ([-0.0058, -0.0002], Holm p=0.0001) and to P+O by -0.0050
  ([-0.0130, -0.0005], Holm p=0.0001). The three-way interaction was effectively zero
  (-0.0000, [-0.0006, 0.0004], Holm p=0.8646). Collection-goal visitation did not improve
  (+/- direction was -0.0025, [-0.0111, 0.0054]), and full was non-inferior to P+K on the
  preregistered hacking margin but did not have lower hacking than O. Thus the required
  all-direction H3a criterion fails.
- **Moderation H3b:** Controlled minus shuffled I3 was -0.0005 ([-0.0018, 0.0002],
  Holm p=0.4097); controlled minus anti I3 was -0.0010 ([-0.0026, 0.0001], Holm p=0.2570).
  Neither interval supports the prediction that correct alignment is what makes coupling
  work. This further weakens the causal coupling story.
- **Post-review validity amendment and scope:** The preregistered kill rule literally
  fired (controlled quality passed, full lost to O/P+O, and I3 was non-positive), but the
  independent result review found that this rule's implicit reachable-goal premise failed.
  The resulting reclassification is therefore a disclosed post-review preregistration
  deviation, adopted before any rerun, rather than a claim that the locked test supported
  coupling. The frozen-reference exploitation policy almost never reached the true goal:
  across controlled cells, mean evaluation true-goal-success AUC was 0.0004 (P+K+O: 0.0002), and
  98.7% of controlled cells were at or below 0.005. This reflects an anchoring/reachability
  floor, not evidence that coupling fails. Conditional C3 is therefore **untested at this
  toy scale**, despite the valid controlled uncertainty signal. A future mechanism run
  requires softened anchoring or a wider reward range, an oracle-posterior reachability
  check, fresh locked seeds, amended preregistration, review, and human sign-off. The
  submitted frozen-MLLM C3 remains untested by design. H3b's null moderation results are
  likewise floor-uninformative.

## MVE 2 — Epistemic versus aleatoric and matched controls

- **What was tested:** A procedural visual contextual bandit with a bootstrap linear reward
  ensemble, learned aleatoric residual head, three shifts, 50 locked seeds, aligned /
  decorrelated / anti-correlated uncertainty-reward layouts, frozen and online reward-model
  regimes, and epistemic / aleatoric / total / point / shuffled / matched-uniform / count
  signals. This is a mechanism test, not an MLLM experiment.
- **Estimator gate:** Passed only weakly. Epistemic uncertainty predicted absolute target
  error better than shuffled (Spearman 0.162 vs -0.029; error AUROC 0.532 vs 0.478).
- **Primary frozen result is structural, not a horse race:** A frozen reward model cannot
  turn visits into information. On the correlation-neutral layout, epistemic tied point
  (-0.0036, 95% CI [-0.0073, 0.0003]), which already fails Control A's requirement that it
  uniquely win. The combined decorrelated+anti confirmatory family rejected epistemic
  superiority, but its aggregate loss magnitude is not a natural effect size because the
  layout mixture and anti-correlation strength were designed interventions.
- **Static-correlation diagnosis:** Epistemic minus point was +0.0719 on aligned layouts,
  -0.0036 on decorrelated layouts, and -0.0719 on anti-correlated layouts. The apparent
  benefit exactly tracks whether uncertainty points toward reward, so frozen epistemic
  exploration behaves as a static prior, not information acquisition. The anti layout was
  implemented as a full rank reversal (Spearman approximately -1), more extreme than the
  preregistered minimum below -0.5; the symmetric magnitude is therefore constructed and
  should not be generalized.
- **Online result:** Epistemic beat aleatoric by 0.0081 but tied total (+0.0002, simultaneous
  CI [-0.0031, 0.0036]) and lost to shuffled, uniform, count, and point by 0.0116–0.0149.
  It reduced reward-model error faster than aleatoric, but was worse than point, shuffled,
  and count on RM-error AUC. It also increased hacking relative to point by 0.0179 and
  shuffled by 0.0195.
- **Estimator boundary:** Error AUROC 0.532 and Spearman 0.162 are weak. Thus the online
  result cannot distinguish “epistemic exploration is ineffective” from “this
  bootstrap-linear estimator is too weak to direct exploration.” A transferable negative
  finding is that ensemble disagreement barely identifies reward error under this shift,
  itself a threat to using the same estimator with an MLLM.
- **Kill-switch outcome:** The submitted *frozen information-gain rationale* is killed
  structurally, and no unique epistemic benefit appears with this estimator. The broader
  C2 claim remains unresolved rather than globally killed. An exploratory post-hoc
  total-minus-point contrast also disfavors the “use total uncertainty” fallback, but it
  was outside the corrected confirmatory family and is not a confirmatory conclusion.
- **Metric/protocol disclosures:** In this one-step bandit, hacking was counted over the
  160 collection episodes; the configured `eval_episodes=200` was unused and no separate
  evaluation phase ran. Development uncertainty scales were fitted against unpermuted base
  rewards, so total's epistemic/aleatoric mixing ratio is calibrated before the layout
  intervention. Target-render RNG also overlaps for a few seed/severity pairs; pairing is
  intact, but future MVEs should hash-mix these seeds.
- **Claim boundary:** This exposes a structural contradiction in the frozen setup and a
  weak-estimator failure in a controlled toy family. It does not establish that a strong,
  calibrated epistemic estimator cannot help with real MLLMs or robotics.

## Surprises and failure prevention

- Online reward-head updating did not rescue epistemic exploration, despite the active-
  learning rationale. Generic/random/count controls achieved better policy return.
- The MVE 3 factorial looked negative despite deliberately high-quality, low-leakage
  controlled uncertainty, but independent review exposed a more basic failure: the
  frozen-reference exploitation policy almost never reached the true goal. The apparent
  O/P+O advantages are therefore not a coupling verdict; they are static tie-level
  differences in a collapsed regime. The learned-bootstrap tier remains separately gated
  out for weak uncertainty estimates.
- A first debugging pilot accidentally used signal-specific RNG for decorrelated reward
  layouts. The driver caught the pairing violation before locked tests, invalidated that
  pilot, separated RNG streams, and added a regression test.
- A second audit found the pilot had opened three intended test seeds. The driver excluded
  those seeds before confirmatory execution and declared a fresh untouched block
  (200000–200049) without using outcomes to select it.
- The experiment was easy to implement and run locally; rigorous seed/RNG provenance was
  the fragile part and required explicit judgment and auditing.

## Cost and time actuals

- MVE 2 implementation, dependency setup, two debugging pilots, locked execution, and
  first analysis completed in about 58 minutes of wall-clock session time, substantially
  below the 4–7.5 hour estimate. The locked 50-seed run itself took 257.7 seconds.
- MVE 3 locked execution took 8,462.3 seconds (about 2.35 hours) after two already
  committed cells, plus a short integrity/analysis pass. This was below the preregistered
  8-hour cap but substantially slower than the pilot's 3,324.9-second projection; future
  planning should retain a large safety factor for extrapolating resumable CPU runs.
- Monetary cost: **$0.00**. Claude review uses the human's personal account and is outside
  the sprint compute/API budget.

## Literature and novelty updates

- **Pessimism is more crowded than the submitted plan reflects.** Hahami et al.
  (arXiv:2606.09073, June 2026) gives a distributional/Bayesian and KL-DRO derivation
  unifying mean, worst-case, and uncertainty-weighted pessimistic reward aggregation.
- **“Small beats large” is not itself surprising enough.** DriveReward
  (arXiv:2606.08525, June 2026) reports a specialized 1B vision-language reward model
  outperforming larger VLMs on a task-specific reward benchmark. C1 must isolate
  calibration from specialization, data, regularization, and reward rescaling.
- **Visual reward-model RL is rapidly crowding.** VLM-AR3L (arXiv:2607.00483) and Large
  Reward Models (arXiv:2603.16065) add recent visual/robot RL reward pipelines, though the
  quick check found no calibrated epistemic pessimism/optimism coupling in their stated
  contributions.
- **Naive additive optimism is an inadequate baseline.** Li et al.'s GEB is now an ICLR
  2026 paper and explicitly corrects the interaction between exploratory bonuses and
  KL/divergence regularization. Any DPOE test must compare against that corrected idea or
  limit its claim to a toy mechanism test.
- **Surviving narrow novelty target:** a causal positive interaction from using the same
  calibrated, correctly decomposed epistemic signal for pessimistic exploitation and
  optimistic collection during visual-domain adaptation.
