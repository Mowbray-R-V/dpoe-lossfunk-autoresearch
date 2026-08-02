import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from core import (CELLS, TIERS, CellSpec, Config, collector_policy, factors,
                  make_scenario, posterior_update, stable_seed, tier_initial_u)
from run import execute


class MVE3Tests(unittest.TestCase):
    def test_hash_streams_are_stable_and_separated(self):
        a = stable_seed("pilot", 0, 1, "controlled_prior_mean")
        self.assertEqual(a, stable_seed("pilot", 0, 1, "controlled_prior_mean"))
        self.assertNotEqual(a, stable_seed("pilot", 0, 2, "controlled_prior_mean"))
        self.assertNotEqual(a, stable_seed("locked", 0, 1, "controlled_prior_mean"))

    def test_variance_update_ignores_label_value(self):
        _, va = posterior_update(0.1, 0.4, -10.0, 0.2)
        _, vb = posterior_update(0.1, 0.4, 10.0, 0.2)
        self.assertEqual(va, vb)

    def test_none_has_no_factors(self):
        self.assertEqual(factors("none"), (False, False, False))
        self.assertEqual(factors("pko"), (True, True, True))

    def test_non_o_collector_independent_of_p_and_k(self):
        cfg = Config()
        mean = np.linspace(-0.2, 0.5, 8); u = np.linspace(0.1, 0.8, 8)
        policies = [collector_policy(mean, u, CellSpec("pilot", 0, 1, "controlled", cell), 1, 1, cfg)
                    for cell in ("none", "p", "k", "pk")]
        for policy in policies[1:]: np.testing.assert_array_equal(policies[0], policy)

    def test_tiers_do_not_change_internal_mean_update(self):
        labels = [0.2, -0.1, 0.4]
        outputs = []
        for _tier in TIERS:
            mean, var = 0.3, 0.5
            for label in labels:
                mean, var = posterior_update(mean, var, label, 0.2)
            outputs.append(mean)
        self.assertTrue(np.allclose(outputs, outputs[0]))

    def test_shuffle_and_anti_preserve_initial_marginal(self):
        cfg = Config(source_episodes=80, source_max_episodes=120, source_eval_episodes=20,
                     source_competence=-1)
        scenario = make_scenario("pilot", 99, 1, cfg)
        np.testing.assert_allclose(np.sort(tier_initial_u(scenario, "shuffled")), np.sort(scenario.u0))
        np.testing.assert_allclose(np.sort(tier_initial_u(scenario, "anti")), np.sort(scenario.u0))

    def test_atomic_cell_resume_skips_completed(self):
        cfg = Config(iterations=2, collection_episodes=2, eval_every=1, eval_episodes=4,
                     source_episodes=60, source_max_episodes=80, source_eval_episodes=10,
                     source_competence=-1, ensemble_size=4)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = execute(root, "pilot", 1, cfg, max_new_cells=1)
            self.assertEqual(first["completed_cells"], 1)
            second = execute(root, "pilot", 1, cfg, max_new_cells=1)
            self.assertEqual(second["completed_before_resume"], 1)
            self.assertEqual(second["completed_cells"], 2)
            files = list((root / "cells").glob("*.npz"))
            self.assertEqual(len(files), 2)


if __name__ == "__main__":
    unittest.main()
