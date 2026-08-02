# Research Plan — Knowing What You Don't Know: Calibrated MLLM Uncertainty for Domain Adaptation in Visual Reinforcement Learning

Author: Mowbray Rajagopalan, IIT Madras (rvmowbray007@gmail.com)
Status: Submitted to and screened by Lossfunk (Stage 2 passed). This sprint (Stage 3) must
empirically stress-test and iterate it.

## 1 THE WHAT

### What I am claiming or showing
For a deep-RL policy adapting to a new visual domain under reward shaping from a frozen
multimodal LLM (MLLM), three claims:

1. The **calibration** of the MLLM's uncertainty over its reward judgments matters more for
   successful adaptation than the absolute **accuracy** of those judgments.
2. Only the **epistemic** component of uncertainty is useful for adaptation, since it
   reflects model ignorance reducible through additional experience (vs irreducible
   aleatoric label noise). Decomposition follows Kendall & Gal (2017).
3. The same epistemic signal should be used **pessimistically** for reward estimation and
   policy updates, but **optimistically** for exploration and state visitation.

The epistemic component provides:
- **Pessimism on the reward:** downweight shaped reward by a function of epistemic variance
  (LCB on the MLLM's reward prediction) — pessimism-in-the-face-of-uncertainty from offline
  RL (Jin et al., 2021; Rashidinejad et al., 2022). This is the only mechanism existing
  uncertainty-aware RLHF uses (Coste et al., 2024; Zhang et al., 2024).
- **Pessimism on the policy step:** tighten the KL trust region adaptively as a function of
  the same epistemic variance — smaller steps where the reward signal is least reliable.
  Standard fixed-β KL penalties don't depend on reward reliability at the current state
  (Zhai et al., 2024); this does.
- **Optimism on exploration:** exploration bonus proportional to the same epistemic
  variance (UCB / optimism-in-the-face-of-uncertainty, Auer et al., 2002). High epistemic
  uncertainty = the reward model needs more data here = the policy should visit these
  states. Also test optimism via posterior (Thompson) sampling over the MLLM reward head:
  each episode draws one reward realization from the reward-model posterior (one MC-dropout
  mask or one LoRA-ensemble member) and the policy acts greedily against it — optimism as a
  property of which reward sample the policy sees, not an additive term competing with the
  KL penalty.

**DPOE (Doubly Pessimistic and Optimistic Exploration):** pessimism alone suppresses
exploration of OOD states — precisely where adaptation is required. Optimism alone
propagates reward-model errors and induces reward hacking. Combining pessimistic
exploitation with optimistic exploration controls uncertainty-induced overestimation while
promoting efficient adaptation.

### The Surprise
The dominant MLLM-shaped-RL literature treats the MLLM's scalar reward or argmax preference
as the operative signal (PrefVLM — Verma et al., 2025; RL-VLM-F — Wang et al., 2024; TTRL —
Zuo et al., 2025; Eureka — Ma et al., 2024). The implicit prior: fix the MLLM under
distribution shift with more data / larger backbone / ensembles / human-in-the-loop /
dedicated reward models (RoboReward — Lee et al., 2026). Even uncertainty-aware variants
(Coste et al., 2024; Zhang et al., 2024; Zhai et al., 2024; Yan et al., 2024) use
uncertainty ONLY as a pessimism penalty on reward magnitude.

Closest prior work:
- Park et al. (2025): calibrate reward-model uncertainty to allocate inference compute at
  test time. DPOE instead uses calibrated uncertainty during RL training to shape rewards,
  adapt the trust region, and guide exploration.
- Cen et al. (2025): optimism-for-exploration / pessimism-for-exploitation in RLHF. DPOE
  extends to visual-domain adaptation with a frozen MLLM reward model, implementing
  optimism via Thompson sampling rather than an additive bonus (avoiding KL interaction,
  cf. Li et al., 2026).
- Liang et al. (2022): ensemble disagreement among learned reward models as an additive
  exploration bonus in MetaWorld. DPOE uses a frozen MLLM reward model and the same
  calibrated epistemic signal simultaneously for reward shaping, adaptive policy updates,
  and exploration.

Falsifiable violations of the prior:
- **Calibration dominates capacity under shift:** a small post-hoc-calibrated MLLM
  (Qwen2.5-VL-3B + temperature scaling + MC-dropout on the reward head) adapts a policy to
  a held-out visual domain faster than Qwen2.5-VL-32B with an uncalibrated head at matched
  wall-clock — contradicting the scaling intuition (Rocamonde et al., 2023).
- **DPOE coupling:** decomposed uncertainty should simultaneously (a) downweight shaped
  reward, (b) tighten the PPO/GRPO KL trust region, (c) inflate an exploration bonus. (a)
  is standard, (b) occasionally implicit, (c) largely absent from the MLLM-as-reward
  literature.

### One-Sentence Version
For visual-domain adaptation under a frozen MLLM reward model, a calibrated posterior over
reward uncertainty — used pessimistically for reward estimation and policy updates and
optimistically for state visitation — enables a small policy to adapt faster and with fewer
reward-hacking failures than a larger, more accurate, but poorly calibrated reward model.

### Alignment with Lossfunk
Research Direction 1 (AI that adapts to a domain): OOD generalization, exploration,
uncertainty modelling.

## 2 THE WHY — Fruitfulness

New questions opened:
- **Q1:** Does DPOE hold for purely textual RL (math/code-RL via GRPO) where the "MLLM" is
  the policy backbone? Is reward-uncertainty > reward-accuracy cross-modal or
  vision-specific?
- **Q2:** Can epistemic/aleatoric decomposition predict catastrophic reward-model failure
  on a new domain BEFORE policy collapse — an early-stopping criterion needing no held-out
  reward?
- **Q3:** Is there an MLLM scale beyond which calibration improves "for free," or does the
  calibration-vs-accuracy trade-off persist? Bears on whether reward-model scaling is the
  right move for adaptation.
- **Q4:** Does epistemic-uncertainty-driven exploration recover the state-visitation
  distribution an active-learning oracle would choose for fine-tuning the MLLM itself —
  closing a loop between RL and continual reward-model learning?

Who builds on this: RLHF/RLAIF reward-modelling groups (reward over-optimisation);
test-time RL community (replacing majority-vote pseudo-rewards); VLM-as-reward / robotics
groups (sim-to-real domain shift). Crossroads across deep-RL theory (OFU/UCB),
post-training, robotics/VLA, and the UQ/calibration community.

## 3 THE HOW

### Killer Alternative Explanation
Small calibrated MLLM wins via implicit smoothing / lucky seeds / small-model
regularisation, NOT via the uncertainty signal. Controls:
- **Control A (uncertainty ablation):** epistemic vs (i) zero (point reward), (ii) uniform
  noise of matched magnitude, (iii) aleatoric-only. Only true-epistemic should win; a tie
  kills the claim.
- **Control B (matched-compute ladder):** small-calibrated vs large-uncalibrated at three
  wall-clock budgets — rules out "small-model-is-cheaper" artifacts.
- **Control C (calibration intervention):** post-hoc calibrate the LARGE MLLM too.
  Prediction: calibrated-large ≥ calibrated-small ≥ uncalibrated-large. If calibrated-large
  doesn't beat uncalibrated-large, the story breaks.
- **Control D (coupling test):** full DPOE vs pessimism-only vs optimism-only. Prediction:
  full strictly dominates both. If either half matches it, DPOE collapses.

Calibration where it matters: ECE evaluated on held-out TARGET-domain splits, not just
source; source-to-target calibration-transfer study with small labelled probe sets when
target labels are unavailable by design. Multiple UQ estimators (MC-dropout, LoRA
ensembles, last-layer Laplace) to avoid single-method artifacts.

Epistemic-only is a HYPOTHESIS, not an assumption: the epistemic/aleatoric split has been
litigated in model-based RL (Chua et al., 2018 — productive in some settings, miscalibrates
under covariate shift), and is largely untested for frozen MLLM rewards. Control A
adjudicates directly. If epistemic-only fails to beat aleatoric-only even with calibration,
the contribution shifts to "use total calibrated uncertainty" and is reported as such.

### Experimental Design (full 6-month version)
- **Setting:** PPO (Schulman et al., 2017) policy (small ResNet/CNN encoder + MLP head,
  ~5–20M params) on procedurally-varied MetaWorld (Yu et al., 2020) / robosuite visual
  manipulation. Reward from a frozen MLLM (Qwen2.5-VL-3B and -32B, plus Idefics3 baseline)
  scoring (observation, goal-text) tuples. MLLM calibrated on a small ground-truth slice of
  the SOURCE domain only. Adaptation: fine-tune on held-out target domains (new textures,
  objects, camera angles); ground-truth reward unavailable; only MLLM reward accessible.
- **Manipulations:** (i) MLLM size 3B vs 32B; (ii) calibration status raw / temp-scaled /
  MC-dropout / LoRA-ensemble; (iii) coupling subset ⊆ {reward, KL, exploration};
  (iv) shift type (texture → object identity → camera pose).
- **Measurements:** primary — target-domain success vs env steps. Secondary — ECE on
  held-out labelled slice; policy entropy and KL(π‖π_ref) trajectories; rate of
  reward-hacking events.
- **Success criterion:** calibrated-3B reaches uncalibrated-32B target-domain success in
  ≤50% of env steps, across ≥3 of 4 shift severities, non-overlapping 95% bootstrap CIs
  over 5 seeds; removing any single coupling pathway must degrade the result.
- **Feasibility (full plan):** frozen 32B inference on a single A100/H100 with vLLM
  batching; tiny policy. ~5 seeds × 4 shifts × ~8 configs × ~5M env steps ≈ a few hundred
  GPU-hours.

### Rigor bar
≥5 seeds; mean ± bootstrap 95% CI, never bare means; permutation tests for small-vs-large;
effect sizes (Cohen's d on sample-efficiency AUC) alongside p-values. Negative results
reported as such if Control A ties or Control C fails.

### What Only I Can Do (& Agents Can't) — to be UPDATED with sprint evidence
- (i) Choosing the epistemic/aleatoric decomposition per model (MC-dropout vs LoRA-ensemble
  vs last-layer Laplace) — must be made empirically.
- (ii) The DPOE coupling schedule — how epistemic variance modulates reward, KL, and
  exploration simultaneously; interaction terms debugged by hand from learning curves and
  failure modes.
- (iii) Diagnosing reward-hacking vs reward-collapse vs honest-adaptation from trajectory
  videos.
Estimated non-automatable human time: ~250–350 hours over 5–6 months.

## 4 THE SO WHAT
- **Impact type:** conceptual (calibration > accuracy for reward-model scaling under
  shift) + methodological (drop-in uncertainty-coupling recipe for any MLLM-shaped RL
  pipeline).
- **Broadest truthful audience:** post-training/RLHF and robotic-learning communities; one
  step out, the UQ/calibration community (a downstream task where calibration measurably
  beats accuracy); two steps out, practitioners deploying AI under distribution shift.
- **Honest framing:** "When AI faces a new domain, knowing what it doesn't know matters
  more than knowing more."
- **Science version:** "Calibrated ignorance beats confident knowledge: a model's
  uncertainty about its own judgments accelerates adaptation to new domains."

## Key references
Auer et al. 2002 (UCB); Cen et al. 2025 (arXiv:2405.19320, value-incentivized preference
optimization); Chua et al. 2018 (arXiv:1805.12114, PETS); Coste et al. 2024 (ICLR, reward
model ensembles); Jin et al. 2021 (ICML, pessimism offline RL); Kendall & Gal 2017
(NeurIPS, uncertainty decomposition); Lee et al. 2026 (arXiv:2601.00675, RoboReward); Li et
al. 2026 (arXiv:2510.03269, exploratory bonus in RLHF); Liang et al. 2022
(arXiv:2205.12401, reward uncertainty for exploration in PbRL); Ma et al. 2024 (ICLR,
Eureka); Park et al. 2025 (arXiv:2506.09338, PRM uncertainty calibration); Rashidinejad et
al. 2022 (IEEE TIT, pessimism); Rocamonde et al. 2023 (arXiv:2310.12921, VLMs as zero-shot
reward models); Schulman et al. 2017 (PPO); Verma et al. 2025 (arXiv:2502.01616, PrefVLM);
Wang et al. 2025 (arXiv:2510.11689, Phys2Real); Wang et al. 2024 (ICML, RL-VLM-F); Yan et
al. 2024 (arXiv:2409.15360, reward-robust RLHF); Yu et al. 2020 (CoRL, Meta-World); Zhai et
al. 2024 (arXiv:2401.00243, uncertainty-penalized RLHF with LoRA ensembles); Zhang et al.
2024 (NeurIPS, AdvPO); Zuo et al. 2025 (arXiv:2504.16084, TTRL).
