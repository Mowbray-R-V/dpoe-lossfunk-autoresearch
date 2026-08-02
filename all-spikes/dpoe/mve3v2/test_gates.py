import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gates
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mve3"))
import analyze


class V2GateTests(unittest.TestCase):
    def test_actual_gate_return_path_uses_shared_auc(self):
        cfg = next(gates.candidates())[0]
        with patch.object(gates, "auc", wraps=gates.auc) as shared_auc:
            metrics = gates.oracle_none_metrics(cfg, replicates=1)
        self.assertIs(analyze.normalized_auc, gates.auc)
        self.assertGreater(shared_auc.call_count, 0)
        for curve in (call.args[0] for call in shared_auc.call_args_list):
            self.assertEqual(len(curve), 1)
            self.assertAlmostEqual(gates.auc(curve), float(curve[0]))
        self.assertAlmostEqual(
            metrics["oracle_minus_none_return_auc"],
            sum(metrics["severity_oracle_minus_none_return_auc"].values()) / 3,
        )

    def test_lexicographic_tuple_selection(self):
        rows = [
            {"tau_reference": .10, "beta0": .10, "clip": 1.25, "metrics": {"passes_solvability": True}},
            {"tau_reference": .14, "beta0": .18, "clip": 1.25, "metrics": {"passes_solvability": True}},
            {"tau_reference": .10, "beta0": .18, "clip": 1.50, "metrics": {"passes_solvability": True}},
        ]
        chosen = gates.choose_tuple(rows)
        self.assertEqual((chosen["clip"], chosen["beta0"], chosen["tau_reference"]), (1.25, .18, .14))

    def test_no_passing_tuple(self):
        self.assertIsNone(gates.choose_tuple([{"metrics": {"passes_solvability": False}}]))


if __name__ == "__main__":
    unittest.main()
