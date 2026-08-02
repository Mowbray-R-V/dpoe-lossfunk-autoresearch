# Day 1 Freshness Literature Check

Date: 2026-07-17. Timebox: quick breadth-first check of arXiv and the local closest-work
library, focused on uncertainty-aware reward models, calibration under shift,
pessimism/optimism coupling, and reward-posterior exploration. This is not a systematic
review.

## Material recent work

1. **Hahami et al., “A Unifying Lens on Reward Uncertainty in RLHF,” arXiv:2606.09073
   (June 2026).** Derives a distributional-reward effective objective under Bayesian and
   KL-DRO views; its pessimistic branch places mean, worst-case, and uncertainty-weighted
   ensemble aggregation in one framework. This directly narrows DPOE's novelty: a paper
   cannot present pessimistic distributional reward aggregation itself as new. The
   prospective delta is joint use of one calibrated epistemic signal for reward, policy
   constraint, and exploration in visual adaptation.
2. **Chen et al., “VLM-AR3L,” arXiv:2607.00483 (IJCAI 2026).** Combines absolute
   state rewards and relative progress rewards learned from VLM preferences across
   control, manipulation, and Minecraft. It crowds the visual-reward application space
   but, from the abstract-level check, does not claim calibrated epistemic uncertainty or
   pessimism/optimism coupling.
3. **Chen et al., “DriveReward,” arXiv:2606.08525 (June 2026).** A specialized 1B
   vision-language reward model reportedly outperforms larger VLMs on task-specific
   driving reward alignment and is used in RL fine-tuning. This weakens the surprise of
   the broad slogan “small beats large”: DPOE must causally distinguish calibration from
   specialization, training data, and regularization.
4. **Wu et al., “Large Reward Models,” arXiv:2603.16065 (March 2026).** Uses a VLM
   reward generator for closed-loop online robotic policy refinement. This increases the
   relevance of the application but also means DPOE must compare against multifaceted
   process/completion/temporal reward design, not only scalar zero-shot VLM rewards.
5. **Li et al., “General Exploratory Bonus for Optimistic Exploration in RLHF,”
   arXiv:2510.03269 (ICLR 2026).** Shows that naive additive bonuses under KL or
   alpha-divergence regularization can remain biased toward high-reference-probability
   regions, and proposes a reference-dependent correction. This was already cited in the
   submitted plan, but its 2026 revision/acceptance makes a naive UCB bonus an inadequate
   baseline. Thompson sampling must be compared with the corrected GEB form or explicitly
   scoped as a mechanism test.
6. **Liu et al., “Uncertainty Quantification for Large Language Model Reward Learning
   under Heterogeneous Human Feedback,” arXiv:2512.03208.** Models annotator
   heterogeneity and uses confidence intervals in best-of-N. It reinforces that label
   heterogeneity/aleatoric structure must be modeled rather than treating ensemble
   disagreement as a clean epistemic decomposition.

## Existing closest work reconfirmed

- Park et al. (arXiv:2506.09338; NeurIPS 2025) calibrates process-reward success
  probabilities with quantile regression and uses confidence bounds for adaptive
  inference compute, not RL-time visual adaptation.
- Cen et al. (arXiv:2405.19320; ICLR 2025) chooses optimism for online RLHF and
  pessimism for offline RLHF through sign-modulated value regularization. It does not, at
  abstract level, establish that simultaneous optimism and pessimism from the same signal
  is superior within one adaptation loop.

## Novelty consequence for this sprint

Treat the broad C1 slogan and pessimistic half as crowded. The strongest surviving target
is narrower: under controlled visual shift, does a *calibrated and correctly decomposed*
reward posterior improve true policy adaptation, and is there a genuine positive
interaction between pessimistic exploitation and optimism-driven data collection? The
experiment must rule out specialization, simple reward rescaling/smoothing, and static
novelty-bonus effects.

## URLs

- https://arxiv.org/abs/2606.09073
- https://arxiv.org/abs/2607.00483
- https://arxiv.org/abs/2606.08525
- https://arxiv.org/abs/2603.16065
- https://arxiv.org/abs/2510.03269
- https://arxiv.org/abs/2512.03208
- https://arxiv.org/abs/2506.09338
- https://arxiv.org/abs/2405.19320

