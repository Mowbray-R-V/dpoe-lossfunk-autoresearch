# papers/INDEX.md — local library of closest prior work

Agent: consult these on demand (see voila.md). Each entry says why the paper matters to
the DPOE plan. Filenames follow `firstauthor_year_shortname.md` (or .pdf if unconverted).
This folder is .gitignore'd — never commit it to the submitted repo.

<!-- User: drop files in and fix filenames below. Delete entries you don't include. -->

| File | Paper | Why it matters here |
|---|---|---|
| cen_2025_vpo.md | Cen et al. 2025, Value-incentivized preference optimization (arXiv:2405.19320) | CLOSEST PRIOR. Optimism-for-exploration / pessimism-for-exploitation in RLHF. DPOE's claimed delta: frozen MLLM reward, visual-domain adaptation, optimism via Thompson sampling instead of additive bonus. Check their exact formulation before positioning. |
| park_2025_prm_calibration.md | Park et al. 2025, Uncertainty calibration of process reward models (arXiv:2506.09338) | Calibrated reward-model uncertainty, but used at TEST TIME for compute allocation. DPOE's delta: use during RL training for reward shaping + trust region + exploration. |
| li_2026_exploratory_bonus.md | Li et al. 2026, General exploratory bonus for optimistic exploration in RLHF (arXiv:2510.03269) | Source of the additive-bonus-vs-KL interaction argument that motivates Thompson sampling in DPOE. Verify the exact claim. |
| lee_2026_roboreward.md | Lee et al. 2026, RoboReward (arXiv:2601.00675) | The "fix the reward model with training/scale" alternative DPOE argues against. Strongest capacity-side baseline framing. |
| zhai_2024_uncertainty_penalized.md | Zhai et al. 2024, Uncertainty-penalized RLHF with reward LoRA ensembles (arXiv:2401.00243) | Implementation reference for LoRA-ensemble epistemic estimates; also the fixed-β KL argument DPOE's adaptive trust region responds to. |
| liang_2022_reward_uncertainty_exploration.md | Liang et al. 2022, Reward uncertainty for exploration in PbRL (arXiv:2205.12401) | Prior use of reward-uncertainty as exploration bonus in MetaWorld (learned RMs, not frozen MLLM). Exact bonus form is the reference point for MVE exploration terms. |
| coste_2024_ensembles.md | Coste et al. 2024, Reward model ensembles mitigate overoptimization (ICLR) | Canonical pessimism-only uncertainty use in RLHF — the "first half" DPOE extends. |
| zhang_2024_advpo.md | Zhang et al. 2024, AdvPO (NeurIPS) | Lightweight uncertainty estimation reference (last-layer / LoRA); pessimism-only baseline. |
| rocamonde_2023_vlm_zeroshot_rm.md | Rocamonde et al. 2023, VLMs are zero-shot reward models (arXiv:2310.12921) | Source of the "bigger VLM = better reward" scaling intuition that C1 contradicts. |

Conversion tip (run once per PDF):
  pip install pymupdf && python -c "import fitz,sys; d=fitz.open(sys.argv[1]); print('\n'.join(p.get_text() for p in d))" paper.pdf > paper.md
