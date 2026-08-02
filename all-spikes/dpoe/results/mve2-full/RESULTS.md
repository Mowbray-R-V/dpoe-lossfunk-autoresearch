# MVE 2 Results

## Scope

Procedural visual contextual-bandit mechanism test; no MLLM was used.

## Offline estimator gate

Gate passed: **True**. Epistemic error Spearman 0.1616 versus shuffled -0.0292; AUROC 0.5324 versus 0.4782.

## Confirmatory aggregate: decorrelated + anti-correlated layouts

Positive differences favor epistemic. Intervals have Bonferroni-adjusted simultaneous 95% family coverage.

| Regime | Contrast | Return AUC difference | Simultaneous CI | Holm p | d_z |
|---|---|---:|---:|---:|---:|
| frozen | epistemic - aleatoric | -0.0149 | [-0.0198, -0.0104] | 0.0001 | -1.1637 |
| frozen | epistemic - total | -0.0045 | [-0.0073, -0.0016] | 0.0001 | -0.5871 |
| frozen | epistemic - shuffled | -0.0400 | [-0.0465, -0.0339] | 0.0001 | -2.3408 |
| frozen | epistemic - uniform | -0.0389 | [-0.0448, -0.0326] | 0.0001 | -2.3538 |
| frozen | epistemic - count | -0.0395 | [-0.0438, -0.0351] | 0.0001 | -3.3349 |
| frozen | epistemic - point | -0.0378 | [-0.0416, -0.0338] | 0.0001 | -3.5355 |
| online | epistemic - aleatoric | 0.0081 | [0.0030, 0.0131] | 0.0003 | 0.5968 |
| online | epistemic - total | 0.0002 | [-0.0031, 0.0036] | 0.8594 | 0.0253 |
| online | epistemic - shuffled | -0.0149 | [-0.0185, -0.0113] | 0.0001 | -1.5198 |
| online | epistemic - uniform | -0.0134 | [-0.0199, -0.0066] | 0.0001 | -0.7424 |
| online | epistemic - count | -0.0116 | [-0.0147, -0.0084] | 0.0001 | -1.3513 |
| online | epistemic - point | -0.0129 | [-0.0160, -0.0096] | 0.0001 | -1.4924 |

## Frozen layout diagnostic: epistemic minus point

| Layout | Difference | 95% CI |
|---|---:|---:|
| aligned | 0.0719 | [0.0673, 0.0765] |
| decorrelated | -0.0036 | [-0.0073, 0.0003] |
| anti | -0.0719 | [-0.0765, -0.0673] |

## Online posterior-error diagnostic

Negative RM-MAE-AUC differences favor epistemic collection.

| Contrast | RM-MAE AUC difference | Simultaneous CI | Holm p |
|---|---:|---:|---:|
| epistemic - aleatoric | -0.0044 | [-0.0061, -0.0027] | 0.0001 |
| epistemic - total | -0.0004 | [-0.0015, 0.0007] | 0.6534 |
| epistemic - shuffled | 0.0027 | [0.0016, 0.0039] | 0.0001 |
| epistemic - uniform | 0.0003 | [-0.0014, 0.0021] | 0.6534 |
| epistemic - count | 0.0046 | [0.0034, 0.0059] | 0.0001 |
| epistemic - point | 0.0027 | [0.0015, 0.0039] | 0.0001 |

## Hacking diagnostic

Positive differences mean epistemic caused more proxy-high/true-low selections.

| Regime | Contrast | Hacking-rate difference | Simultaneous CI |
|---|---|---:|---:|
| frozen | epistemic - aleatoric | -0.0054 | [-0.0144, 0.0037] |
| frozen | epistemic - shuffled | 0.0579 | [0.0390, 0.0774] |
| frozen | epistemic - point | 0.0484 | [0.0372, 0.0592] |
| online | epistemic - aleatoric | -0.0262 | [-0.0374, -0.0155] |
| online | epistemic - shuffled | 0.0195 | [0.0118, 0.0272] |
| online | epistemic - point | 0.0179 | [0.0116, 0.0247] |

## Pre-registered verdict

- Submitted frozen-RM C2 support criterion met: **False**. This is a structural failure of the information-gain rationale: visits cannot update a frozen reward model. On the correlation-neutral layout, epistemic tied point; the anti layout is a deliberately full rank reversal, so its loss magnitude is constructed rather than a natural effect size.
- Revised online-RM epistemic superiority criterion met: **False**, but the estimator was weak (error AUROC 0.532; Spearman 0.162), so this does not cleanly adjudicate a stronger epistemic estimator.
- Frozen epistemic-minus-total difference: -0.0045; simultaneous CI [-0.0073, -0.0016].
- Exploratory post-hoc frozen total-minus-point difference: -0.0332; 95% CI [-0.0362, -0.0302]. Online: -0.0131; 95% CI [-0.0158, -0.0105]. These contrasts were outside the corrected confirmatory family.
- Aligned frozen mean: epistemic 0.6105, point 0.5386. Anti-correlated frozen mean: epistemic 0.4395, point 0.5114.

Interpretation must follow the kill criteria: an aligned-only gain with loss on anti-correlated layouts is a static uncertainty/reward-correlation artifact, not evidence that epistemic uncertainty is uniquely useful.

Hacking rates use the 160 one-step collection episodes; the configured 200 evaluation episodes were unused. Development scales were fitted against base rewards before layout permutation. Target-render seed arithmetic overlaps for a few seed/severity pairs; paired comparisons remain intact, but this should be hash-mixed in future experiments.
