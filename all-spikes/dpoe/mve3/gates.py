"""Development and locked signal-quality diagnostics for MVE 3."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from core import (Config, N_TERMINALS, PROTOCOL_VERSION, auroc, make_scenario,
                  partial_spearman, risk_coverage_auc, spearman, stable_seed,
                  terminal_probabilities, tier_initial_u)


def gate_metrics(split: str, replicates: int, cfg: Config) -> dict[str, object]:
    by_severity: dict[str, dict[str, list[float]]] = {
        str(s): {k: [] for k in ("error", "controlled", "learned", "truth", "mu0", "ref_prob")}
        for s in (1, 2, 3)
    }
    competence, traps, goals = [], [], []
    for replicate in range(replicates):
        for severity in (1, 2, 3):
            scenario = make_scenario(split, replicate, severity, cfg)
            competence.append(scenario.reference_competence)
            traps.append(float(scenario.trap_present)); goals.append(scenario.goal_strength)
            error = np.abs(scenario.true_rewards - scenario.mu0)
            learned = tier_initial_u(scenario, "learned")
            ref_prob = terminal_probabilities(scenario.reference)
            target = by_severity[str(severity)]
            for key, value in (("error", error), ("controlled", scenario.u0),
                               ("learned", learned), ("truth", scenario.true_rewards),
                               ("mu0", scenario.mu0), ("ref_prob", ref_prob)):
                target[key].extend(np.asarray(value, float).tolist())

    result: dict[str, object] = {
        "protocol_version": PROTOCOL_VERSION, "split": split, "replicates": replicates,
        "source_competence_min": float(np.min(competence)),
        "source_competence_mean": float(np.mean(competence)),
        "trap_prevalence": float(np.mean(traps)), "goal_strength_mean": float(np.mean(goals)),
        "severities": {},
    }
    controlled_pass, learned_pass = True, True
    leakage_parts = []
    for severity in (1, 2, 3):
        d = {k: np.asarray(v) for k, v in by_severity[str(severity)].items()}
        hard = d["error"] >= np.quantile(d["error"], 0.75)
        partial = partial_spearman(d["controlled"], d["truth"],
                                   np.column_stack([d["mu0"], d["ref_prob"]]))
        leakage_parts.extend(zip(d["controlled"], d["truth"], d["mu0"], d["ref_prob"]))
        entry = {
            "controlled_spearman": spearman(d["controlled"], d["error"]),
            "controlled_auroc": auroc(d["controlled"], hard),
            "controlled_risk_coverage_auc": risk_coverage_auc(d["controlled"], d["error"]),
            "learned_spearman": spearman(d["learned"], d["error"]),
            "learned_auroc": auroc(d["learned"], hard),
            "learned_risk_coverage_auc": risk_coverage_auc(d["learned"], d["error"]),
            "leakage_partial_spearman": partial,
            "n_points": len(d["error"]),
        }
        controlled_pass &= entry["controlled_auroc"] >= 0.75 and entry["controlled_spearman"] >= 0.50
        learned_pass &= entry["learned_auroc"] >= 0.70 and entry["learned_spearman"] >= 0.40
        result["severities"][str(severity)] = entry
    leak = np.asarray(leakage_parts)
    aggregate_partial = partial_spearman(leak[:, 0], leak[:, 1], leak[:, 2:])
    result.update({
        "controlled_quality_pass": bool(controlled_pass),
        "learned_development_gate_pass": bool(learned_pass),
        "leakage_partial_spearman_aggregate": float(aggregate_partial),
        "leakage_guard_pass": bool(abs(aggregate_partial) <= 0.10),
        "source_gate_pass": bool(np.min(competence) >= cfg.source_competence),
    })
    result["proceed"] = bool(result["controlled_quality_pass"] and result["leakage_guard_pass"]
                             and result["source_gate_pass"])
    return result


def write_seed_manifest(path: Path, split: str, replicates: int) -> None:
    components = ("source_training", "source_evaluation", "controlled_prior_mean",
                  "controlled_prior_scale", "controlled_truth_draw", "visual_render")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=("protocol", "split", "replicate", "severity", "component", "seed"))
        writer.writeheader()
        for replicate in range(replicates):
            for severity in (1, 2, 3):
                for component in components:
                    parts = (split, replicate, component) if component.startswith("source_") else (split, replicate, severity, component)
                    writer.writerow({"protocol": PROTOCOL_VERSION, "split": split,
                                     "replicate": replicate, "severity": severity,
                                     "component": component, "seed": stable_seed(*parts)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "locked"), default="development")
    parser.add_argument("--replicates", type=int, default=20)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cfg = Config()
    args.out.mkdir(parents=True, exist_ok=True)
    result = gate_metrics(args.split, args.replicates, cfg)
    (args.out / f"{args.split}-gates.json").write_text(json.dumps(result, indent=2) + "\n")
    write_seed_manifest(args.out / f"{args.split}-seed-manifest.csv", args.split, args.replicates)
    print(json.dumps(result, indent=2))
    if args.split == "development" and not result["proceed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
