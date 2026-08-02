"""Outcome-blind runtime/storage decision after the completed five-replicate pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import atomic_write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    state = json.loads((args.pilot_root / "run-state.json").read_text())
    integrity = json.loads((args.pilot_root / "integrity.json").read_text())
    if not state.get("invocation_complete") or not integrity.get("pass"):
        raise SystemExit("Pilot must be complete and pass integrity")
    # Sum all artifacts, then scale the cell payload; manifests/state are negligible.
    pilot_bytes = sum(p.stat().st_size for p in args.pilot_root.rglob("*") if p.is_file())
    # Extrapolate the measured resume invocation to all pilot cells; this avoids relying on
    # outcome files or on the short first invocation's startup overhead.
    pilot_seconds = (float(state["elapsed_seconds_this_invocation"])
                     * int(state["total_cells"]) / int(state["new_cells_this_invocation"]))
    projection_50_seconds = pilot_seconds * 10.0
    projection_50_bytes = pilot_bytes * 10
    if projection_50_seconds <= 8 * 3600 and projection_50_bytes <= 2 * 1024**3:
        locked_replicates = 50
    else:
        locked_replicates = 30
    projection_30_seconds = pilot_seconds * 6.0
    projection_30_bytes = pilot_bytes * 6
    if locked_replicates == 30 and (projection_30_seconds > 8 * 3600 or projection_30_bytes > 2 * 1024**3):
        raise SystemExit("Even 30 replicates exceed caps; human rescoping required")
    decision = {
        "basis": "runtime_and_storage_only_no_outcomes_read", "pilot_replicates": 5,
        "pilot_seconds": pilot_seconds, "pilot_bytes": pilot_bytes,
        "projection_50_seconds": projection_50_seconds,
        "projection_50_bytes": projection_50_bytes,
        "projection_30_seconds": projection_30_seconds,
        "projection_30_bytes": projection_30_bytes,
        "runtime_cap_seconds": 8 * 3600, "storage_cap_bytes": 2 * 1024**3,
        "locked_replicates": locked_replicates,
    }
    atomic_write_json(args.out, decision)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
