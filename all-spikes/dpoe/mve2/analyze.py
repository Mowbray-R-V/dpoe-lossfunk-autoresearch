"""Paired confirmatory and diagnostic analysis for MVE 2."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CONTROLS = ("aleatoric", "total", "shuffled", "uniform", "count", "point")
SIGNALS = ("epistemic", "aleatoric", "total", "point", "shuffled", "uniform", "count")
LAYOUTS = ("aligned", "decorrelated", "anti")


def load(path: Path) -> list[dict[str, object]]:
    numeric = {"seed", "severity", "return_auc", "final_window_return", "hacking_rate",
               "rm_mae_auc", "rm_mae_final", "epi_reward_spearman"}
    rows = []
    with path.open() as f:
        for raw in csv.DictReader(f):
            row: dict[str, object] = dict(raw)
            for key in numeric:
                row[key] = int(raw[key]) if key in {"seed", "severity"} else float(raw[key])
            rows.append(row)
    return rows


def seed_means(rows: list[dict[str, object]], regime: str, signal: str, metric: str,
               layouts: tuple[str, ...]) -> dict[int, float]:
    values: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        if r["regime"] == regime and r["signal"] == signal and r["layout"] in layouts:
            values[int(r["seed"])].append(float(r[metric]))
    return {seed: float(np.mean(v)) for seed, v in values.items()}


def paired_diff(rows: list[dict[str, object]], regime: str, lhs: str, rhs: str,
                metric: str, layouts: tuple[str, ...]) -> np.ndarray:
    a = seed_means(rows, regime, lhs, metric, layouts)
    b = seed_means(rows, regime, rhs, metric, layouts)
    seeds = sorted(set(a) & set(b))
    if len(seeds) != 50:
        raise ValueError(f"Expected 50 paired seeds, got {len(seeds)}")
    return np.asarray([a[s] - b[s] for s in seeds])


def bootstrap_ci(values: np.ndarray, confidence: float, rng: np.random.Generator,
                 draws: int = 30_000) -> tuple[float, float]:
    idx = rng.integers(0, len(values), size=(draws, len(values)))
    means = values[idx].mean(axis=1)
    alpha = 1.0 - confidence
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def permutation_p(values: np.ndarray, rng: np.random.Generator, draws: int = 100_000) -> float:
    observed = abs(float(np.mean(values)))
    signs = rng.choice((-1.0, 1.0), size=(draws, len(values)))
    null = np.abs((signs * values).mean(axis=1))
    return float((np.sum(null >= observed) + 1) / (draws + 1))


def holm(pvalues: list[float]) -> list[float]:
    order = np.argsort(pvalues)
    adjusted = np.empty(len(pvalues))
    running = 0.0
    m = len(pvalues)
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvalues[int(idx)])
        adjusted[int(idx)] = min(1.0, running)
    return adjusted.tolist()


def effect_dz(values: np.ndarray) -> float:
    sd = float(np.std(values, ddof=1))
    return float(np.mean(values) / sd) if sd > 0 else float("inf")


def confirmatory(rows: list[dict[str, object]], regime: str, metric: str) -> list[dict[str, object]]:
    rng = np.random.default_rng(20260717 + (0 if regime == "frozen" else 1))
    family_confidence = 1.0 - 0.05 / len(CONTROLS)
    results = []
    for control in CONTROLS:
        diff = paired_diff(rows, regime, "epistemic", control, metric, ("decorrelated", "anti"))
        lo, hi = bootstrap_ci(diff, family_confidence, rng)
        results.append({
            "regime": regime, "metric": metric, "contrast": f"epistemic - {control}",
            "mean_diff": float(np.mean(diff)), "simultaneous_ci_low": lo,
            "simultaneous_ci_high": hi, "cohens_dz": effect_dz(diff),
            "permutation_p": permutation_p(diff, rng),
            "individual_confidence": family_confidence,
        })
    adjusted = holm([float(x["permutation_p"]) for x in results])
    for row, p in zip(results, adjusted):
        row["holm_p"] = p
    return results


def layout_diagnostics(rows: list[dict[str, object]], regime: str) -> list[dict[str, object]]:
    rng = np.random.default_rng(1907 + (0 if regime == "frozen" else 1))
    result = []
    for layout in LAYOUTS:
        for control in CONTROLS:
            diff = paired_diff(rows, regime, "epistemic", control, "return_auc", (layout,))
            lo, hi = bootstrap_ci(diff, 0.95, rng, 15_000)
            result.append({"regime": regime, "layout": layout,
                           "contrast": f"epistemic - {control}",
                           "mean_diff": float(np.mean(diff)), "ci_low": lo, "ci_high": hi})
    return result


def group_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rng = np.random.default_rng(44)
    result = []
    for regime in ("frozen", "online"):
        for layout in LAYOUTS:
            for signal in SIGNALS:
                by_seed = seed_means(rows, regime, signal, "return_auc", (layout,))
                values = np.asarray([by_seed[s] for s in sorted(by_seed)])
                lo, hi = bootstrap_ci(values, 0.95, rng, 10_000)
                result.append({"regime": regime, "layout": layout, "signal": signal,
                               "mean_return_auc": float(np.mean(values)),
                               "ci_low": lo, "ci_high": hi})
    return result


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def plot_groups(summary: list[dict[str, object]], out: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 7), sharey=True)
    colors = plt.cm.tab10(np.linspace(0, 1, len(SIGNALS)))
    for i, regime in enumerate(("frozen", "online")):
        for j, layout in enumerate(LAYOUTS):
            ax = axes[i, j]
            subset = [r for r in summary if r["regime"] == regime and r["layout"] == layout]
            subset.sort(key=lambda r: SIGNALS.index(str(r["signal"])))
            means = np.asarray([r["mean_return_auc"] for r in subset], float)
            low = np.asarray([r["ci_low"] for r in subset], float)
            high = np.asarray([r["ci_high"] for r in subset], float)
            ax.bar(range(len(SIGNALS)), means, color=colors)
            ax.errorbar(range(len(SIGNALS)), means, yerr=(means-low, high-means), fmt="none", c="black", capsize=2)
            ax.set_title(f"{regime} / {layout}")
            ax.set_xticks(range(len(SIGNALS)), SIGNALS, rotation=45, ha="right", fontsize=8)
            ax.set_ylim(0.38, 0.68)
            if j == 0: ax.set_ylabel("True-return AUC")
    fig.suptitle("MVE 2: uncertainty-signal controls (mean and bootstrap 95% CI)")
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def markdown_report(gate: dict[str, object], confirm: list[dict[str, object]],
                    rm_error: list[dict[str, object]], hacking: list[dict[str, object]],
                    diagnostic: list[dict[str, object]], summary: list[dict[str, object]],
                    rows: list[dict[str, object]]) -> str:
    def fmt(x: object) -> str: return f"{float(x):.4f}"
    lines = ["# MVE 2 Results", "", "## Scope", "",
             "Procedural visual contextual-bandit mechanism test; no MLLM was used.", "",
             "## Offline estimator gate", "",
             f"Gate passed: **{gate['pass']}**. Epistemic error Spearman {fmt(gate['epi_spearman'])} "
             f"versus shuffled {fmt(gate['shuffled_spearman'])}; AUROC {fmt(gate['epi_auroc'])} "
             f"versus {fmt(gate['shuffled_auroc'])}.", "",
             "## Confirmatory aggregate: decorrelated + anti-correlated layouts", "",
             "Positive differences favor epistemic. Intervals have Bonferroni-adjusted simultaneous 95% family coverage.", "",
             "| Regime | Contrast | Return AUC difference | Simultaneous CI | Holm p | d_z |",
             "|---|---|---:|---:|---:|---:|"]
    for r in confirm:
        lines.append(f"| {r['regime']} | {r['contrast']} | {fmt(r['mean_diff'])} | "
                     f"[{fmt(r['simultaneous_ci_low'])}, {fmt(r['simultaneous_ci_high'])}] | "
                     f"{fmt(r['holm_p'])} | {fmt(r['cohens_dz'])} |")
    lines += ["", "## Frozen layout diagnostic: epistemic minus point", "",
              "| Layout | Difference | 95% CI |", "|---|---:|---:|"]
    for r in diagnostic:
        if r["regime"] == "frozen" and r["contrast"] == "epistemic - point":
            lines.append(f"| {r['layout']} | {fmt(r['mean_diff'])} | [{fmt(r['ci_low'])}, {fmt(r['ci_high'])}] |")

    lines += ["", "## Online posterior-error diagnostic", "",
              "Negative RM-MAE-AUC differences favor epistemic collection.", "",
              "| Contrast | RM-MAE AUC difference | Simultaneous CI | Holm p |",
              "|---|---:|---:|---:|"]
    for r in rm_error:
        lines.append(f"| {r['contrast']} | {fmt(r['mean_diff'])} | "
                     f"[{fmt(r['simultaneous_ci_low'])}, {fmt(r['simultaneous_ci_high'])}] | {fmt(r['holm_p'])} |")

    lines += ["", "## Hacking diagnostic", "",
              "Positive differences mean epistemic caused more proxy-high/true-low selections.", "",
              "| Regime | Contrast | Hacking-rate difference | Simultaneous CI |",
              "|---|---|---:|---:|"]
    for r in hacking:
        if r["contrast"] in {"epistemic - point", "epistemic - shuffled", "epistemic - aleatoric"}:
            lines.append(f"| {r['regime']} | {r['contrast']} | {fmt(r['mean_diff'])} | "
                         f"[{fmt(r['simultaneous_ci_low'])}, {fmt(r['simultaneous_ci_high'])}] |")

    def mean(regime: str, layout: str, signal: str) -> float:
        return float(next(r["mean_return_auc"] for r in summary if r["regime"] == regime and r["layout"] == layout and r["signal"] == signal))

    frozen = [r for r in confirm if r["regime"] == "frozen"]
    online = [r for r in confirm if r["regime"] == "online"]
    frozen_support = all(float(r["simultaneous_ci_low"]) > 0 and float(r["holm_p"]) < 0.05 for r in frozen)
    online_support = all(float(r["simultaneous_ci_low"]) > 0 and float(r["holm_p"]) < 0.05 for r in online)
    total_row = next(r for r in frozen if r["contrast"] == "epistemic - total")
    rng = np.random.default_rng(887)
    total_point_frozen = paired_diff(rows, "frozen", "total", "point", "return_auc", ("decorrelated", "anti"))
    total_point_online = paired_diff(rows, "online", "total", "point", "return_auc", ("decorrelated", "anti"))
    tpf_ci = bootstrap_ci(total_point_frozen, 0.95, rng)
    tpo_ci = bootstrap_ci(total_point_online, 0.95, rng)
    lines += ["", "## Pre-registered verdict", "",
              f"- Submitted frozen-RM C2 support criterion met: **{frozen_support}**. This is a structural failure of the information-gain rationale: visits cannot update a frozen reward model. On the correlation-neutral layout, epistemic tied point; the anti layout is a deliberately full rank reversal, so its loss magnitude is constructed rather than a natural effect size.",
              f"- Revised online-RM epistemic superiority criterion met: **{online_support}**, but the estimator was weak (error AUROC {float(gate['epi_auroc']):.3f}; Spearman {float(gate['epi_spearman']):.3f}), so this does not cleanly adjudicate a stronger epistemic estimator.",
              f"- Frozen epistemic-minus-total difference: {fmt(total_row['mean_diff'])}; "
              f"simultaneous CI [{fmt(total_row['simultaneous_ci_low'])}, {fmt(total_row['simultaneous_ci_high'])}].",
              f"- Exploratory post-hoc frozen total-minus-point difference: {np.mean(total_point_frozen):.4f}; 95% CI "
              f"[{tpf_ci[0]:.4f}, {tpf_ci[1]:.4f}]. Online: {np.mean(total_point_online):.4f}; "
              f"95% CI [{tpo_ci[0]:.4f}, {tpo_ci[1]:.4f}]. These contrasts were outside the corrected confirmatory family.",
              f"- Aligned frozen mean: epistemic {mean('frozen','aligned','epistemic'):.4f}, "
              f"point {mean('frozen','aligned','point'):.4f}. Anti-correlated frozen mean: "
              f"epistemic {mean('frozen','anti','epistemic'):.4f}, point {mean('frozen','anti','point'):.4f}.", "",
              "Interpretation must follow the kill criteria: an aligned-only gain with loss on anti-correlated layouts is a static uncertainty/reward-correlation artifact, not evidence that epistemic uncertainty is uniquely useful.", "",
              "Hacking rates use the 160 one-step collection episodes; the configured 200 evaluation episodes were unused. Development scales were fitted against base rewards before layout permutation. Target-render seed arithmetic overlaps for a few seed/severity pairs; paired comparisons remain intact, but this should be hash-mixed in future experiments.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    rows = load(args.results / "raw_results.csv")
    gate = json.loads((args.results / "offline_gate.json").read_text())
    confirm = confirmatory(rows, "frozen", "return_auc") + confirmatory(rows, "online", "return_auc")
    rm_error = confirmatory(rows, "online", "rm_mae_auc")
    hacking = confirmatory(rows, "frozen", "hacking_rate") + confirmatory(rows, "online", "hacking_rate")
    diagnostic = layout_diagnostics(rows, "frozen") + layout_diagnostics(rows, "online")
    summary = group_summary(rows)
    write_csv(args.results / "confirmatory_contrasts.csv", confirm)
    write_csv(args.results / "online_rm_error_contrasts.csv", rm_error)
    write_csv(args.results / "hacking_contrasts.csv", hacking)
    write_csv(args.results / "layout_diagnostics.csv", diagnostic)
    write_csv(args.results / "group_summary.csv", summary)
    plot_groups(summary, args.results / "returns_by_condition.png")
    report = markdown_report(gate, confirm, rm_error, hacking, diagnostic, summary, rows)
    (args.results / "RESULTS.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
