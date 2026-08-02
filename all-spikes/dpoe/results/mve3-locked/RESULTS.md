# MVE 3 Results

Synthetic online reward-posterior mechanism test; no MLLM was used.

## Quality and validity gates

- Controlled locked quality passed: **True**.
- Learned locked quality passed: **False**.
- Leakage guard passed: **True** (partial Spearman 0.0124).
- Locked reference competence minimum: **1.000** (required >=0.800).
- Trap prevalence: 0.967; mean goal strength: 0.713.
- The locked quality gate is evaluated per severity here, whereas the preregistered wording specified an aggregate gate. This is stricter; all severities passed, so the deviation does not favor the result.
- Learned-tier uncertainty was RMS-rescaled to the controlled prior uncertainty using the generator's `u0`; this is oracle-scale information and is disclosed for reproducibility. It does not affect a learned-tier claim because that tier failed its quality gate.

### Scenario statistics by tier and severity

Truth is paired across tiers, so the per-tier rows below are intentionally identical within each severity.

| Tier | Severity | Trap prevalence | Mean trap strength | Mean goal strength |
|---|---:|---:|---:|---:|
| controlled | 1 | 1.000 | 0.282 | 0.621 |
| controlled | 2 | 0.960 | 0.401 | 0.734 |
| controlled | 3 | 0.940 | 0.513 | 0.784 |
| learned | 1 | 1.000 | 0.282 | 0.621 |
| learned | 2 | 0.960 | 0.401 | 0.734 |
| learned | 3 | 0.940 | 0.513 | 0.784 |
| shuffled | 1 | 1.000 | 0.282 | 0.621 |
| shuffled | 2 | 0.960 | 0.401 | 0.734 |
| shuffled | 3 | 0.940 | 0.513 | 0.784 |
| anti | 1 | 1.000 | 0.282 | 0.621 |
| anti | 2 | 0.960 | 0.401 | 0.734 |
| anti | 3 | 0.940 | 0.513 | 0.784 |

Entropy and KL AUCs are retained per cell in `cell_summary.csv`; raw checkpoint terminal arrays in `cells/*.npz` support any secondary timeout/collapse audit.

## Exploitation manipulation check (post-review diagnostic)

- Mean controlled evaluation true-goal-success AUC: **0.0004**; P+K+O mean: **0.0002**.
- The operative post-review design-floor trigger is mean controlled goal-success AUC < **0.0100**. Separately, 98.7% of controlled cells are at or below 0.005; the maximum is 0.0498.
- **Design floor detected:** the exploitation policy almost never reaches the true goal. The original protocol did not preregister an oracle-reachability manipulation check, so these locked contrasts cannot support or kill the coupling mechanism.

## H3a confirmatory family

Positive values support the named superiority contrast; hacking non-inferiority instead requires the CI upper bound < 0.02.

| Contrast | Mean | Simultaneous CI | Holm p | d_z |
|---|---:|---:|---:|---:|
| return:pko-pk | 0.0005 | [0.0000, 0.0014] | 0.0892 | 0.275 |
| return:pko-o | -0.0021 | [-0.0058, -0.0002] | 0.0001 | -0.266 |
| return:pko-po | -0.0050 | [-0.0130, -0.0005] | 0.0001 | -0.289 |
| return:pko-ko | 0.0004 | [0.0001, 0.0008] | 0.0003 | 0.371 |
| return:I3 | -0.0000 | [-0.0006, 0.0004] | 0.8646 | -0.026 |
| collection_goal:pko-pk | -0.0025 | [-0.0111, 0.0054] | 0.8603 | -0.118 |
| hacking:o-pko | -0.0004 | [-0.0012, -0.0000] | 0.1272 | -0.216 |
| hacking_NI:pko-pk | -0.0001 | [-0.0004, 0.0000] | 0.7491 | -0.186 |

## H3b signal-quality moderation

| Contrast | Mean | Simultaneous CI | Holm p |
|---|---:|---:|---:|
| I3:controlled-shuffled | -0.0005 | [-0.0018, 0.0002] | 0.4097 |
| I3:controlled-anti | -0.0010 | [-0.0026, 0.0001] | 0.2570 |

H3b is likewise floor-uninformative: its null moderation contrasts cannot adjudicate signal-quality moderation while exploitation cannot act on the true goal.

## Per-severity directions

- return:pko-pk: s1=0.0002, s2=0.0006, s3=0.0008
- return:pko-o: s1=-0.0004, s2=-0.0035, s3=-0.0023
- return:pko-po: s1=-0.0010, s2=-0.0072, s3=-0.0069
- return:pko-ko: s1=0.0002, s2=0.0004, s3=0.0006
- return:I3: s1=-0.0001, s2=0.0000, s3=-0.0000
- collection_goal:pko-pk: s1=0.0023, s2=-0.0042, s3=-0.0056
- hacking:o-pko: s1=-0.0000, s2=-0.0000, s3=-0.0011

## Verdict (post-review validity amendment)

- The preregistered kill rule did fire: controlled quality passed, full lost to O and P+O, and I3 was non-positive. This post-review amendment sets that kill aside because the rule presupposes a reachable true goal; independent review `reviews/review-08.md` identified the failed manipulation check before any rerun.
- Controlled H3a support: **False**.
- H3b moderation support: **False**.
- Conditional C3 verdict: **untested-design-floor-policy-collapse**.
- Learned H3c status: **untested-quality-gate-failed**.
- Submitted frozen-MLLM C3 remains untested by design.
