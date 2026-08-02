# Review: MVE 3 locked-result audit

## Summary judgment

Implementation integrity, seed/pairing discipline, and the statistical machinery are solid — I verified several of the protocol's own invariants in the artifacts (exact equality of `none`-cell results across all four tiers, exact equality of non-O `collection_goal_auc` across cells, integrity audit clean at 4800/4800). The learned-H3c and frozen-MLLM components of the verdict stand. But the headline verdict — **conditional toy-scale C3 "killed"** — is not supported, because the locked configuration made the primary estimand insensitive by construction: **no exploitation policy in any of the 4,800 cells ever adapted to the goal.** This is a claim-calibration failure, and it is BLOCKING.

## BLOCKING

**B1 — Universal exploitation collapse; the kill verdict rests on a degenerate experiment.**
Evidence from the artifacts:

- `cell_summary.csv`: `eval_goal_auc` is 0.0000–0.0005 in every cell I inspected (all 32 conditions of replicates 0, all severities) — at most 1 goal hit in 2,200 evaluation episodes, i.e. the residual leak of `pi_ref` itself, not adaptation. `final_return` is *identical to 16 decimal places* across all 8 factorial cells and all 4 tiers within a scenario.
- `group_summary.csv`: every cell in every tier has return AUC 0.182–0.188 while mean goal strength is 0.713 (`locked-quality.json`). The `none` cell (0.1840) is indistinguishable from `pko` (0.1825). Meanwhile collection reaches the goal fine (collection_goal AUC ≈ 0.43; 0.98 in replicate 0/severity 1) — the posterior *knows* the answer; the exploitation policy cannot act on it.
- The cause is arithmetic, not stochastic. The goal is by design on a low-reference-probability branch (`core.py:318-319`), which sits across a root/branch gate where the converged `pi_ref` (trained on 1.0 vs −0.2 at `tau_reference=0.10`) has a log-odds gap of ~12 nats. Flipping that gate in `policy_from_rewards` (`core.py:157`) requires ΔQ ≥ 12 × `beta0` = 2.64, but rewards are clipped to ±1.25 (`core.py:316`), capping ΔQ at 2.5. Reaching the goal branch is impossible for **every** cell, under **any** posterior, at **any** true state of the coupling hypothesis. K only raises β; P only shrinks ΔQ. The outcome "full matches/loses to P+K or O" was therefore decided at lock time.

The protocol's own guard anticipates exactly this regime: "Low hacking achieved by never reaching the true goal is policy collapse, not support" (mve3-protocol.md, decision rules). `analyze.py` never implements that guard — `h3a_support` (analyze.py:253-255) checks contrasts and quality gates but never checks evaluation goal success — and maps *any* H3a failure to `killed-at-toy-scale` (analyze.py:257-259), which is broader than the preregistered kill list. Symmetric honesty requires that a kill, like a support, cannot rest on a regime where the goal is unreachable. The Holm p=0.0001 "losses" to O and P+O are real but microscopic (−0.002 to −0.005 on a ~0.5 headroom scale) tie-flips among reference-plausible terminals; the hacking results are equally static (hacking AUC 0.1586–0.1600 everywhere — it measures which seeds happened to place the trap under `pi_ref`, not policy behavior).

**Required fix:** reclassify `conditional_c3` in `verdict.json`, RESULTS.md, and the LEARNINGS.md claim table from "killed-at-toy-scale" to **uninformative/untested — design floor (universal policy collapse)**. LEARNINGS.md's "Even deliberately high-quality... controlled uncertainty did not rescue the coupling mechanism" (line 114) and the C3 row must be rewritten; as written they assert the mechanism got a fair test. RESULTS.md must also report true-goal success and absolute levels — the protocol requires reporting true-goal success at checkpoints, and surfacing it would have caught this before write-up.

**Does this require a rerun?** The verdict correction does not; no locked data can be salvaged into either a kill or a support. A rerun **is required if the sprint still wants any C3 mechanism answer**, and needs: (i) fixed anchoring arithmetic (reduce `beta0`, soften `tau_reference`, or widen the reward clip so max ΔQ exceeds the gate cost); (ii) a preregistered manipulation check — an oracle-posterior exploitation policy must reach the goal on development seeds, and none-vs-oracle separation must exceed a minimum detectable effect; (iii) fresh locked seeds, amended prereg, human sign-off. Cost is within envelope (~2.5 h CPU, $0), but with 7-17 start and today 7-20 that scope call is the human's.

## Non-blocking

1. **Learned-tier scale is oracle-rescaled**: `learned_scale` (core.py:328) matches learned u's RMS to RMS(`u0`), a target-generating-scale hint not derivable from source features. Irrelevant now (gate failed on rank metrics), but disclose it, and remove it before any future learned-tier claim.
2. Locked-side source-competence gate is never asserted (train_reference returns regardless; integrity.py doesn't check `reference_competence` ≥ 0.8). Report the minimum across locked cells — one line.
3. Trap prevalence/strength reported only in aggregate; protocol asks per severity.
4. `quality_gates` applies per-severity thresholds where the prereg specifies locked *aggregate* — stricter, passed anyway; note the deviation. Dead `path = Path()` at analyze.py:169.

VERDICT: REVISE — (1) reclassify conditional C3 as uninformative/untested due to universal exploitation collapse, correcting verdict.json, RESULTS.md, and LEARNINGS.md; (2) add the collapse evidence (eval goal success ≈ 0, none ≡ full, headroom arithmetic) to RESULTS.md; (3) record explicitly that a mechanism answer requires a redesigned, re-preregistered rerun with an adaptation manipulation check — or that C3 stays untested at toy scale.
