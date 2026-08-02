"""Preregistered development-v2 tuning and solvability gates; no locked execution."""
from __future__ import annotations

import argparse
import json
import hashlib
from dataclasses import asdict, replace
from pathlib import Path
from typing import Iterable

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mve3"))
from core import (Config, atomic_write_json, evaluate_policy, exploitation_policy,
                  make_scenario, policy_from_rewards)
from metrics import normalized_auc as auc

# Keep these constants literal and synchronized with mve3-v2-protocol.md.
TAUS = (0.10, 0.14, 0.18)
BETAS = (0.10, 0.14, 0.18)
CLIPS = (1.25, 1.50, 1.75)
DEVELOPMENT_SPLIT = "development-v2"


def update_free_return_auc(evaluation: dict[str, np.ndarray | float]) -> float:
    """Use the shared AUC on an actual update-free policy evaluation.

    The gate has one update-free checkpoint, so the singleton normalized AUC equals the
    measured checkpoint mean. Factorial learning curves use the same imported function.
    """
    checkpoint_curve = np.asarray([np.mean(evaluation["true_return"])], dtype=float)
    return auc(checkpoint_curve)


def candidates() -> Iterable[tuple[Config, float]]:
    for tau in TAUS:
        for beta in BETAS:
            for clip in CLIPS:
                yield replace(Config(), tau_reference=tau, beta0=beta, reward_clip=clip), clip


def oracle_none_metrics(cfg: Config, replicates: int = 20) -> dict[str, float | bool | dict[str, float]]:
    """Development-only oracle/none solvability metrics, using 1,000 paired episodes."""
    gate_cfg = replace(cfg, eval_episodes=1000)
    oracle_goal, none_goal, oracle_return, none_return, competences = [], [], [], [], []
    by_severity = {str(s): {"oracle_goal": [], "oracle_return": [], "none_return": []}
                   for s in (1, 2, 3)}
    for replicate in range(replicates):
        for severity in (1, 2, 3):
            scenario = make_scenario(DEVELOPMENT_SPLIT, replicate, severity, gate_cfg)
            oracle = policy_from_rewards(scenario.true_rewards, gate_cfg.beta0, reference=scenario.reference,
                                         beta_by_state=np.full(7, gate_cfg.beta0))
            none = exploitation_policy(scenario.mu0, scenario.u0, scenario.reference, "none", gate_cfg)
            oracle_eval = evaluate_policy(oracle, scenario, 0, scenario.true_rewards, gate_cfg)
            none_eval = evaluate_policy(none, scenario, 0, scenario.mu0, gate_cfg)
            og, ng = float(np.mean(oracle_eval["goal"])), float(np.mean(none_eval["goal"]))
            oracle_goal.append(og); none_goal.append(ng)
            oracle_auc = update_free_return_auc(oracle_eval)
            none_auc = update_free_return_auc(none_eval)
            oracle_return.append(oracle_auc)
            none_return.append(none_auc)
            severity_metrics = by_severity[str(severity)]
            severity_metrics["oracle_goal"].append(og)
            severity_metrics["oracle_return"].append(oracle_auc)
            severity_metrics["none_return"].append(none_auc)
            competences.append(scenario.reference_competence)
    metrics = {
        "oracle_goal_success": float(np.mean(oracle_goal)),
        "none_goal_success": float(np.mean(none_goal)),
        "oracle_minus_none_goal_success": float(np.mean(oracle_goal) - np.mean(none_goal)),
        "oracle_minus_none_return_auc": float(np.mean(oracle_return) - np.mean(none_return)),
        "source_competence_min": float(np.min(competences)),
        "severity_oracle_goal_success": {
            s: float(np.mean(v["oracle_goal"])) for s, v in by_severity.items()
        },
        "severity_oracle_minus_none_return_auc": {
            s: float(np.mean(v["oracle_return"]) - np.mean(v["none_return"]))
            for s, v in by_severity.items()
        },
    }
    metrics["passes_solvability"] = bool(metrics["oracle_goal_success"] >= .25
        and all(v >= .15 for v in metrics["severity_oracle_goal_success"].values())
        and metrics["oracle_minus_none_goal_success"] >= .15
        and metrics["oracle_minus_none_return_auc"] >= .10)
    return metrics


def choose_tuple(records: list[dict[str, object]]) -> dict[str, object] | None:
    passing = [r for r in records if r["metrics"]["passes_solvability"]]
    if not passing:
        return None
    return sorted(passing, key=lambda r: (r["clip"], -r["beta0"], r["tau_reference"]))[0]


def write_frozen_config(root: Path, selected: dict[str, object], records: list[dict[str, object]]) -> None:
    """Atomically freezes all tuning evidence before pilot/locked-v2 is permitted."""
    payload = {"status": "development-solvability-passed", "split": DEVELOPMENT_SPLIT,
        "selected": selected, "all_candidates": records,
        "auc_formula": "trapz(values, checkpoint_index)/(last_checkpoint_index)",
        "flat_policy_identity": "For update-free oracle/none policies, normalized AUC equals the checkpoint mean.",
        "locked_execution_authorized": False}
    atomic_write_json(root / "mve3-v2-frozen-config.json", payload)


def metrics_fingerprint(records: list[dict[str, object]]) -> str:
    """Stable digest of exactly the metric fields present before report regeneration."""
    payload = json.dumps([record["metrics"] for record in records], sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def report_only_regenerate(root: Path, replicates: int) -> None:
    """Add omitted report fields without tuning, selecting, or opening new seed namespaces."""
    path = root / "development-solvability-failed.json"
    previous = json.loads(path.read_text())
    old_records = previous["candidates"]
    records = []
    for cfg, clip in candidates():
        gate_cfg = replace(cfg, eval_episodes=1000)
        records.append({"tau_reference": cfg.tau_reference, "beta0": cfg.beta0,
                        "clip": clip, "config": asdict(gate_cfg),
                        "metrics": oracle_none_metrics(cfg, replicates)})
    if len(old_records) != len(records):
        raise RuntimeError("Report-only audit failed: candidate count changed")
    for old, new in zip(old_records, records):
        if (old["tau_reference"], old["beta0"], old["clip"]) != (new["tau_reference"], new["beta0"], new["clip"]):
            raise RuntimeError("Report-only audit failed: candidate ordering changed")
        for key, old_value in old["metrics"].items():
            if new["metrics"].get(key) != old_value:
                raise RuntimeError(f"Report-only audit failed: pre-existing metric changed: {key}")
    old_fingerprint = metrics_fingerprint(old_records)
    regenerated_fingerprint = metrics_fingerprint([
        {"metrics": {key: new["metrics"][key] for key in old["metrics"]}}
        for old, new in zip(old_records, records)
    ])
    if old_fingerprint != regenerated_fingerprint:
        raise RuntimeError("Report-only audit failed: metric fingerprint changed")
    payload = {
        "candidates": records,
        "report_only_regeneration": {
            "purpose": "Add omitted per-severity return-AUC reporting; no grid re-entry or new seeds.",
            "pre_existing_metric_fingerprint_sha256": old_fingerprint,
            "regenerated_pre_existing_metric_fingerprint_sha256": regenerated_fingerprint,
            "pre_existing_metrics_bit_identical": True,
            "evaluation_episodes": 1000,
            "auc_formula": "trapz(values, checkpoint_index)/(last_checkpoint_index); singleton curve equals its sole value",
            "flat_policy_identity": "For update-free oracle/none policies, normalized AUC equals the checkpoint mean.",
        },
    }
    atomic_write_json(path, payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--execute-development", action="store_true")
    parser.add_argument("--report-only-regenerate", action="store_true")
    parser.add_argument("--replicates", type=int, default=20)
    args = parser.parse_args()
    if args.report_only_regenerate:
        report_only_regenerate(args.root, args.replicates)
        return
    if not args.execute_development:
        raise SystemExit("Refusing to open development-v2 scenarios without --execute-development")
    records = []
    for cfg, clip in candidates():
        records.append({"tau_reference": cfg.tau_reference, "beta0": cfg.beta0,
                        "clip": clip,
                        "config": asdict(cfg), "metrics": oracle_none_metrics(cfg, args.replicates)})
    selected = choose_tuple(records)
    if selected is None:
        atomic_write_json(args.root / "development-solvability-failed.json", {"candidates": records})
        raise SystemExit("No preregistered development tuple passed; refusing pilot/locked-v2")
    write_frozen_config(args.root, selected, records)
    print(json.dumps(selected, indent=2))


if __name__ == "__main__":
    main()
