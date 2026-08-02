"""Resumable cell runner for MVE 3."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from core import (CELLS, TIERS, Config, PROTOCOL_VERSION, atomic_save_npz,
                  atomic_write_json, cell_path, cell_specs, run_cell, stable_seed,
                  validate_cell)


def write_run_manifest(path: Path, split: str, replicates: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ("protocol", "split", "replicate", "severity", "tier", "cell", "component", "seed")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for replicate in range(replicates):
            for severity in (1, 2, 3):
                for tier in TIERS:
                    # O collection is shared across all O-bearing P/K cells; non-O is shared globally.
                    for component, seed in (
                        ("o_collection_root", stable_seed(split, replicate, severity, tier, "posterior_sampling_collector")),
                        ("non_o_collection_root", stable_seed(split, replicate, severity, "shared", "collection_dynamics")),
                        ("evaluation_root", stable_seed(split, replicate, severity, "evaluation_dynamics")),
                    ):
                        writer.writerow({"protocol": PROTOCOL_VERSION, "split": split,
                                         "replicate": replicate, "severity": severity,
                                         "tier": tier, "cell": "shared", "component": component,
                                         "seed": seed})
                    for cell in CELLS:
                        writer.writerow({"protocol": PROTOCOL_VERSION, "split": split,
                                         "replicate": replicate, "severity": severity,
                                         "tier": tier, "cell": cell, "component": "cell_identity",
                                         "seed": stable_seed(split, replicate, severity, tier, cell, "cell_identity")})


def execute(root: Path, split: str, replicates: int, cfg: Config,
            max_new_cells: int | None = None) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=True)
    specs = cell_specs(split, replicates)
    manifest = root / "seed-manifest.csv"
    if not manifest.exists():
        write_run_manifest(manifest, split, replicates)
    completed_before = 0
    for spec in specs:
        path = cell_path(root, spec)
        if path.exists():
            if not validate_cell(path, spec, cfg):
                raise RuntimeError(f"Invalid completed cell; refusing overwrite: {path}")
            completed_before += 1
    started, new = time.time(), 0
    last = None
    for spec in specs:
        path = cell_path(root, spec)
        if path.exists():
            continue
        arrays = run_cell(spec, cfg)
        atomic_save_npz(path, arrays)
        if not validate_cell(path, spec, cfg):
            raise RuntimeError(f"Atomic cell failed validation: {path}")
        new += 1; last = spec.cell_id
        state = {
            "protocol_version": PROTOCOL_VERSION, "split": split, "replicates": replicates,
            "total_cells": len(specs), "completed_cells": completed_before + new,
            "completed_before_resume": completed_before, "new_cells_this_invocation": new,
            "last_completed_cell": last, "elapsed_seconds_this_invocation": time.time() - started,
            "updated_unix": time.time(),
        }
        atomic_write_json(root / "run-state.json", state)
        if max_new_cells is not None and new >= max_new_cells:
            break
    result = json.loads((root / "run-state.json").read_text()) if (root / "run-state.json").exists() else {}
    result["invocation_complete"] = result.get("completed_cells", 0) == len(specs)
    result["elapsed_seconds_this_invocation"] = time.time() - started
    atomic_write_json(root / "run-state.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("pilot", "locked"), required=True)
    parser.add_argument("--replicates", type=int, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--max-new-cells", type=int)
    parser.add_argument("--confirm-locked", action="store_true")
    parser.add_argument("--development-gate", type=Path)
    parser.add_argument("--pilot-decision", type=Path)
    args = parser.parse_args()
    if args.split == "locked":
        if not args.confirm_locked:
            raise SystemExit("Locked run requires --confirm-locked after recorded human sign-off")
        if args.development_gate is None:
            raise SystemExit("Locked run requires --development-gate")
        gate = json.loads(args.development_gate.read_text())
        if not gate.get("proceed"):
            raise SystemExit("Development gate does not permit locked execution")
        if args.pilot_decision is None:
            raise SystemExit("Locked run requires --pilot-decision")
        decision = json.loads(args.pilot_decision.read_text())
        if int(decision.get("locked_replicates", -1)) != args.replicates:
            raise SystemExit("Replicate count disagrees with preregistered pilot decision")
    result = execute(args.root, args.split, args.replicates, Config(), args.max_new_cells)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
