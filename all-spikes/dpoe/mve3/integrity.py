"""Integrity audit for completed pilot/locked MVE 3 cells."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from core import CELLS, TIERS, Config, cell_path, cell_specs, validate_cell


def audit(root: Path, split: str, replicates: int, cfg: Config) -> dict[str, object]:
    specs = cell_specs(split, replicates)
    invalid, missing = [], []
    for spec in specs:
        path = cell_path(root, spec)
        if not path.exists(): missing.append(spec.cell_id)
        elif not validate_cell(path, spec, cfg): invalid.append(spec.cell_id)
    temp_files = [str(p) for p in root.rglob("*.tmp-*")]
    pairing_violations = []
    scenario_violations = []
    if not missing and not invalid:
        for replicate in range(replicates):
            for severity in (1, 2, 3):
                scenario_meta = []
                for tier in TIERS:
                    arrays = {}
                    metas = {}
                    for cell in CELLS:
                        path = root / "cells" / f"r{replicate:03d}_s{severity}_{tier}_{cell}.npz"
                        with np.load(path, allow_pickle=False) as data:
                            arrays[cell] = {k: data[k].copy() for k in ("collection_terminal", "collection_label", "posterior_mean")}
                            metas[cell] = json.loads(str(data["metadata"]))
                    for group in (("none", "p", "k", "pk"), ("o", "po", "ko", "pko")):
                        base = arrays[group[0]]
                        for cell in group[1:]:
                            for key in base:
                                if not np.array_equal(base[key], arrays[cell][key]):
                                    pairing_violations.append(f"r{replicate}s{severity}:{tier}:{group[0]}!={cell}:{key}")
                    scenario_meta.append((tier, metas["none"]))
                base_meta = scenario_meta[0][1]
                for tier, meta in scenario_meta[1:]:
                    for key in ("mu0", "u0", "true_rewards", "goal_terminal", "trap_terminal", "trap_present"):
                        if meta[key] != base_meta[key]:
                            scenario_violations.append(f"r{replicate}s{severity}:{tier}:{key}")
                # Non-O collection and calibrated posterior means must also match across tiers.
                with np.load(root / "cells" / f"r{replicate:03d}_s{severity}_controlled_none.npz", allow_pickle=False) as d:
                    base_term, base_label, base_mean = d["collection_terminal"].copy(), d["collection_label"].copy(), d["posterior_mean"].copy()
                for tier in TIERS[1:]:
                    with np.load(root / "cells" / f"r{replicate:03d}_s{severity}_{tier}_none.npz", allow_pickle=False) as d:
                        for key, a, b in (("terminal", base_term, d["collection_terminal"]),
                                          ("label", base_label, d["collection_label"]),
                                          ("mean", base_mean, d["posterior_mean"])):
                            if not np.array_equal(a, b):
                                pairing_violations.append(f"r{replicate}s{severity}:cross-tier-none:{tier}:{key}")
    report = {
        "split": split, "replicates": replicates, "expected_cells": len(specs),
        "present_cells": len(list((root / "cells").glob("*.npz"))) if (root / "cells").exists() else 0,
        "missing_count": len(missing), "invalid_count": len(invalid),
        "temporary_file_count": len(temp_files), "pairing_violation_count": len(pairing_violations),
        "scenario_violation_count": len(scenario_violations), "missing_examples": missing[:5],
        "invalid_examples": invalid[:5], "pairing_examples": pairing_violations[:5],
        "scenario_examples": scenario_violations[:5],
    }
    report["pass"] = not any((missing, invalid, temp_files, pairing_violations, scenario_violations))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--split", choices=("pilot", "locked"), required=True)
    parser.add_argument("--replicates", type=int, required=True)
    args = parser.parse_args()
    report = audit(args.root, args.split, args.replicates, Config())
    (args.root / "integrity.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["pass"]: raise SystemExit(2)


if __name__ == "__main__":
    main()

