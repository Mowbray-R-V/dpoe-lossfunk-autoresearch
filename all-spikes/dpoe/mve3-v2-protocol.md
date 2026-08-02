# MVE 3 v2 Amended Preregistration — Reachable Conditional Coupling Test

Status: **Claude-approved amended protocol; development grid completed and failed its preregistered solvability gate.** No pilot-v2 or locked-v2 execution is authorized or permitted. This amendment follows the completed v1 run, whose result is a `post-review-validity-amendment` with conditional C3 untested for a policy-collapse design floor; it does not alter any v1 artifact.

Revision date: 2026-07-21. The v1 protocol is preserved at `mve3-protocol.md`.

## Motivation

MVE 3 v1 passed the controlled-signal quality gate (locked AUROC 0.850–0.924; Spearman 0.647–0.710) but could not test conditional C3. Review 08 found a reference-policy anchoring floor: a low-reference branch required about 2.64 reward-value units to flip, versus at most 2.5 available under the v1 clip. Mean controlled evaluation true-goal-success AUC was 0.0004 (P+K+O 0.0002). Reviews 08–10 require a fresh solvability gate and fresh seeds before any new C3 claim.

## Evidence-mapped delta from v1

| v1 element | Evidence | v2 amendment | Frozen before locked seeds |
|---|---|---|---|
| Low-reference goal, `beta0=0.22`, `tau_reference=0.10`, clip ±1.25 | Review 08: branch flip required ~2.64 versus ≤2.5 available; exploitation collapsed | Tune anchoring/reward range only on development-v2 under a fixed grid | One tuple and all other settings written to frozen config |
| No proof exploitation could act on a known goal | v1 collection reached goals but evaluation did not; Review 08 required oracle check | Add development oracle-reachability/none-separation gate plus locked replication | Gate failure stops or makes result untested |
| Kill rule fired in a degenerate regime | Reviews 08–10 made v1 a post-review validity amendment | Require signal, leakage, solvability, and engagement gates before a v2 null may kill C3 | Validity failure is untested, never a kill |
| Learned `u` RMS was scaled with generator `u0` | Review 08 called this oracle-scale information; learned tier failed | Learned tier descriptive only; remove oracle RMS rescaling from v2 implementation | No learned C3 verdict in v2 |
| Code used stricter per-severity rather than written aggregate quality gate | Reviews 08/10 required disclosure | Aggregate gate is confirmatory; per-severity values are diagnostics | Both reported explicitly |

## Scope and carried-forward design

**Question:** In a *solvable* online-updated synthetic visual reward-posterior task, does using the same calibrated epistemic signal for pessimistic reward (P), adaptive trust region (K), and posterior-sampling collection (O) beat every component-removal half?

This is a conditional toy mechanism test only; it cannot validate submitted frozen-MLLM C3. Unless amended here, v2 incorporates v1's binary-tree visual environment, three severities, conjugate online posterior, separate collection/exploitation policies, P×K×O factorial, controlled/shuffled/anti signal-only tiers, paired labels, BLAKE2b streams, 200-episode evaluation checkpoints, statistics, atomic resume, and no-replacement rules. P/K/O definitions and the factor-independent collectors are unchanged. Tiers retain identical posterior means for matched label histories. The learned-bootstrap tier is descriptive only.

## Development-only anchoring and reward-range tuning

Use only `split="development-v2"`, replicates 0–19, in a new hash namespace. No pilot-v2 or locked-v2 seed may be generated, listed, inspected, or opened during tuning.

| Parameter | Candidate values |
|---|---|
| `tau_reference` | 0.10, 0.14, 0.18 |
| `beta0` | 0.10, 0.14, 0.18 |
| Target reward clip | ±1.25, ±1.50, ±1.75 |

Evaluate **every** tuple, train its source reference as in v1, and run the oracle gate below. A tuple is eligible only if its source learner reaches >=80% of oracle source return over the v1 separate 200-episode source evaluation within 10,000 training episodes. Choose the eligible passing tuple with the **smallest clip**, then **largest beta0**, then **smallest tau_reference**. This fixed lexicographic rule minimizes relaxation without outcome-based selection. If no tuple passes, record v2 infeasible and stop; no pilot or locked-v2 seed opens. Re-entering the candidate grid after this solvability gate is evaluated is forbidden without a new protocol, independent review, and human sign-off; disclose the failed bounded grid rather than silently extending or retuning it.

Before a pilot or locked seed is opened, write `mve3-v2-frozen-config.json` containing the complete selected tuple, source/posterior/label settings, non-O temperature, every candidate's gate results, code hash, seed namespace, and the exact normalized trapezoidal true-return-AUC expression used by both oracle/none and factorial policies. It must state that for update-free oracle/none policies the checkpoint curve is flat and this AUC equals its mean. A unit test must assert this identity. The file is immutable thereafter. Any change requires a new protocol, Claude review, and human sign-off.

## Preregistered development solvability gate

For each development replicate × severity, freeze the target layout and evaluate two update-free exploitation policies:

- **Oracle:** plans from true terminal rewards under the frozen reference and selected tuple, with P and K absent. Truth is used only for this gate, never in a factorial policy, collector, posterior update, or outcome analysis.
- **None baseline:** same frozen-reference policy from initial posterior mean `mu0`, with P/K/O absent.

Evaluate both for exactly **1,000 paired episodes** per scenario and calculate normalized evaluation true-return AUC on the same paired episodes. The gate passes only if all conditions hold:

1. Aggregate oracle true-goal success is **>=25%**.
2. Each severity's mean oracle success is **>=15%**.
3. Aggregate oracle-minus-none success is **>=15 percentage points**.
4. Aggregate oracle-minus-none true-return AUC is **>=0.10**.

If no candidate passes, stop and **never open pilot or locked-v2 seeds**. The locked split cannot repair or retune anchoring, reward range, posterior settings, or this threshold.

After selection and implementation, but still using development-v2 only, run the eight controlled-tier factorial cells under the frozen tuple. The **development adaptation-engagement gate** passes only if `max_cell(cell true-goal-success AUC − none true-goal-success AUC)` is at least **20% of the oracle-minus-none true-goal-success separation**. This is a stop gate, never a tuning objective: failure records v2 as development-engagement-invalid and blocks pilot/locked-v2 seed opening. Re-entering the candidate grid after this gate is evaluated is forbidden without a new protocol, independent review, and human sign-off; disclose the failed frozen tuple rather than silently reselecting one.

## Locked validity and adaptation-engagement gates

After implementation/pilot approval and final human sign-off, run the frozen oracle and none policies on every fresh locked-v2 scenario for 1,000 paired episodes. This happens after locked cells complete, never triggers replacement/tuning, and is required for any C3 verdict. Conditional-C3 eligibility requires all of:

1. Locked aggregate oracle success >=25%, each severity >=15%, oracle-minus-none success >=15 percentage points, oracle-minus-none true-return AUC >=0.10, and minimum retrained source-reference competence >=0.80. Integrity audit must assert and report that minimum across locked-v2 scenarios.
2. Controlled signal passed its development gate and the preregistered locked **aggregate** quality gate (AUROC >=0.75; Spearman >=0.50). Per-severity quality is reported diagnostically.
3. Absolute locked partial-Spearman leakage <=0.10.
4. `max_cell(cell true-goal-success AUC − none true-goal-success AUC)` over the eight controlled-tier factorial cells is at least **20% of the locked oracle-minus-none true-goal-success separation**. This factor-independent engagement guard measures actual adaptation rather than an elevated reference baseline, without conditioning validity on P+K+O's outcome.

Failure of any gate yields `untested-validity-or-engagement-gate-failed`; factorial contrasts remain reported but cannot support, weaken, or kill C3.

## Confirmatory estimands and v2 decision rules

H3a/H3b, evaluation, hacking, collection-goal visitation, contrast families, simultaneous bootstrap intervals, Holm tests, and the two-of-three-severity direction requirement are unchanged from v1. The primary controlled-tier return contrasts are full-minus-PK, full-minus-O, full-minus-PO, full-minus-KO, and I3. H3a support still requires every v1 direction, after all validity/engagement gates pass. H3b is interpretable only after those gates pass. Report per-severity oracle-minus-none true-return-AUC separation alongside all severity directions.

### Fixed v2 null and kill condition

Define the practical contrast floor `delta = 0.10 × (locked aggregate oracle-minus-none true-return AUC)`. The return-AUC gate guarantees `delta >=0.01`. The gate policies and factorial contrasts use the identical normalized trapezoidal true-return-AUC definition and checkpoint normalization, so `delta` is on the primary-estimand scale by construction.

**Yes: conditional C3 is killed at toy scale in v2 if every validity and engagement gate passes, but full DPOE demonstrably and practically does not beat one of its halves.** Specifically, classify `conditional_c3 = killed-at-toy-scale-v2` if, for at least one primary controlled-tier return contrast below, both conditions hold: (a) its Bonferroni-simultaneous 95% CI has an **upper bound <= -delta** and (b) its mean direction is <=`-delta` in at least two of the three severities:

- full-minus-PK;
- full-minus-O;
- full-minus-PO;
- full-minus-KO.

I3 remains required for H3a support but is not a half-superiority kill criterion: additive full-over-half effects can have non-positive I3. This kill rule is a directional, practical contrary result—not merely non-significance—and uses the same two-of-three-severity standard as support. Clean `supported-at-toy-scale-v2` also requires each of the four full-minus-half return point estimates and I3 to be at least `delta`; if all H3a directional/statistical requirements pass but any is below `delta`, classify `statistically-real-but-practically-null-v2` rather than clean support.

**Binding interpretation for a valid near-null:** If every validity and engagement gate passes; none of the four full-minus-half kill criteria is met; every full-minus-half simultaneous interval lies within `[-delta, +delta]`; and the I3 simultaneous interval has upper bound `< +delta`, classify `no-support-for-conditional-c3-at-toy-scale-v2`. This is a negative result for the conditional C3 claim, not an uncertain state: the experiment had solvability and practical headroom but excluded a practically meaningful positive interaction. If gates pass but neither this near-null rule nor support, weakening, or the practical-harm kill rule applies, classify `inconclusive-at-toy-scale-v2`.

If H3a passes but H3b moderation fails, classify `weakened-causal-coupling-v2`. A positive result remains limited to this online synthetic mechanism.

## Seed, timing, and cost controls

Use a new protocol version and `development-v2`, `pilot-v2`, and `locked-v2` split tags in all BLAKE2b seeds; no v1 stream may recur. Preserve v1 manifests, equality/pairing audits, atomic commits, five-replicate pilot, and symmetric 50-to-30 reduction rule under the 8-hour/2-GiB cap. If even 30 projected replicates exceed a cap, stop and return to the human.

Before evaluating the full 27-tuple grid, time the plausibly costliest tuple (`tau_reference=0.18`, `beta0=0.18`, clip ±1.75) without inspecting any gate outcome. If its extrapolated full-grid runtime exceeds 3 CPU hours, stop and request human scope approval. During the exhaustive grid, stop again and request scope approval if cumulative wall-clock time reaches that 3-hour cap before completion; otherwise run every tuple. Estimated dollar cost: **$0**. Development tuning/gate is conservatively 1–3 CPU hours after this timing check. Implementation/validation: 6–10 hours. Locked run/analysis: projected ~2.5 CPU hours, subject to the outcome-blind pilot projection.

## Hard scope cutoff

If the development solvability and adaptation-engagement gates have not passed within the preregistered tuning budget by **mid-day 6** of the seven-day sprint, stop v2. Do not iterate the gate, extend the candidate grid, retune an already frozen tuple, or start pilot/locked work. Ship C3 as untested with the diagnosed solvability/adaptation cause and the attempted fixed-budget gate record.

## Required sequence

1. Claude review of this draft and correction of blocking issues.
2. Human final protocol sign-off; implementation remains unauthorized until then.
3. Implement and unit-test development-only tuning plus the solvability gate.
4. Freeze configuration; run development gate and pilot integrity/timing checks.
5. Request/confirm locked-execution authorization before generating or opening `locked-v2` seeds.
