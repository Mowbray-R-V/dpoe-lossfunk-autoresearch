# MVE Ideas (FALLBACK ONLY)

**Agent: do not read this file before proposing your own MVE designs from
`research-plan.md`.** These are pre-drafted sketches written by a human+Claude before the
sprint. Use them only to (a) sanity-check coverage of C1/C2/C3 after you've made your own
proposals, or (b) unblock yourself if your proposals stall. If you take anything from this
file, say so explicitly in PROGRESS.md — it counts as human input, not agent effort.

---

## Idea A — Calibration under shift, no RL (targets C1 and C2; cheap; do-first candidate)
Use a small open VLM that runs on available hardware (e.g. Qwen2.5-VL-3B quantized, or a
SmolVLM/Idefics3-class model if resources are tight) as a reward scorer on
(image, goal-text) pairs from an offline dataset — rendered MetaWorld/robosuite frames, or
any scripted visual goal dataset generated locally. Create controlled shifts (textures,
colors, camera crop/pose).

Measure: reward accuracy vs Expected Calibration Error on source and shifted splits;
epistemic/aleatoric decomposition via MC-dropout on the reward head, small LoRA/prompt
ensembles, and last-layer Laplace.

Key question: does calibration degrade slower than accuracy under shift, and is the
epistemic estimator actually informative OOD? Informs C1/C2 with no RL loop at all.

Kill-condition sketch: if ECE and accuracy degrade at the same rate across shifts, or if
epistemic estimates are uninformative (uncorrelated with error) OOD, C1/C2 are in trouble
before any RL is run.

## Idea B — DPOE coupling with a synthetic reward model (targets C3; the mechanism test)
Small RL env that trains in minutes (gridworld / MiniGrid / low-dim continuous control,
state or pixel obs). Replace the MLLM with a SYNTHETIC reward model whose error and
uncertainty are controlled exactly: ground-truth reward + state-dependent bias + known
epistemic and aleatoric noise fields.

Run the plan's Control D ablation: full DPOE vs pessimism-only vs optimism-only vs
uncalibrated baseline. Also run Control A: epistemic vs aleatoric vs matched-magnitude
uniform noise vs zero.

This isolates the coupling logic from MLLM quality — it is where the plan's mechanism
lives or dies, and it is nearly free to run with many seeds.

Kill-condition sketch: if pessimism-only (or optimism-only) matches full DPOE, the
coupling story collapses; if aleatoric or matched-noise ties epistemic, C2 collapses at
toy scale.

## Idea C — One real MLLM-in-the-loop run (stretch; proof-of-life, not a result)
Only if time and budget remain after A and B. Smallest viable version: one
MetaWorld-style task, texture shift only, tiny PPO policy, small VLM reward using the best
uncertainty estimator found in Idea A, 2–3 seeds, heavily truncated env steps.

Purpose: verify the full pipeline (VLM scoring in the loop, uncertainty extraction,
DPOE coupling) actually runs end-to-end and produce one honest preliminary curve for the
deck. Explicitly label results as single-digit-seed and preliminary.

---

Notes for whichever ideas are used:
- Cache all VLM outputs aggressively; never pay for the same query twice.
- Prefer generating shift datasets locally (rendering + augmentation) over downloading
  large corpora.
- The plan's own success criteria are for the 6-month version; at sprint scale the bar is
  directional evidence + a working mechanism demo + honest kill/keep verdicts per claim.
