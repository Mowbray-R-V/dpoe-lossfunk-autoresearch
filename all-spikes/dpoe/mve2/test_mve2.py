import unittest

import numpy as np

import mve2


class MVE2Tests(unittest.TestCase):
    def setUp(self):
        self.cfg = mve2.Config(ensemble_size=6, gate_dev_seeds=3, steps=10)

    def test_layout_correlations(self):
        epi = np.linspace(0, 1, self.cfg.n_arms)
        rng = np.random.default_rng(4)
        self.assertGreater(mve2.spearman(mve2.make_layout("aligned", epi, rng, self.cfg), epi), 0.9)
        self.assertLess(mve2.spearman(mve2.make_layout("anti", epi, rng, self.cfg), epi), -0.9)
        self.assertLess(abs(mve2.spearman(mve2.make_layout("decorrelated", epi, rng, self.cfg), epi)), 0.05)

    def test_uncertainties_are_finite(self):
        source = mve2.make_source(1, self.cfg)
        heads = mve2.fit_reward_ensemble(source, 1, self.cfg)
        aw = mve2.fit_aleatoric(source, heads, self.cfg)
        x = mve2.target_features(1, 2, self.cfg)
        mean, epi, alea = mve2.uncertainty(heads, aw, x)
        self.assertTrue(np.isfinite(mean).all() and np.isfinite(epi).all() and np.isfinite(alea).all())
        self.assertTrue((epi > 0).all() and (alea > 0).all())

    def test_layout_seed_is_condition_independent(self):
        epi = np.linspace(0, 1, self.cfg.n_arms)
        first = mve2.paired_layout(9, 2, "decorrelated", epi, self.cfg)
        second = mve2.paired_layout(9, 2, "decorrelated", epi, self.cfg)
        np.testing.assert_array_equal(first, second)

    def test_frozen_does_not_update_heads(self):
        source = mve2.make_source(2, self.cfg)
        heads = mve2.fit_reward_ensemble(source, 2, self.cfg)
        before = heads.copy()
        aw = mve2.fit_aleatoric(source, heads, self.cfg)
        mve2.run_one(2, 1, "aligned", "epistemic", "frozen", source, heads, aw, 1, 1, self.cfg)
        np.testing.assert_array_equal(heads, before)


if __name__ == "__main__":
    unittest.main()
