"""MVE 2: epistemic vs aleatoric exploration under procedural visual shift.

This is a mechanism-level toy experiment. It does not instantiate an MLLM.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


SIGNALS = ("epistemic", "aleatoric", "total", "point", "shuffled", "uniform", "count")
LAYOUTS = ("aligned", "decorrelated", "anti")
REGIMES = ("frozen", "online")


@dataclass(frozen=True)
class Config:
    n_arms: int = 12
    image_size: int = 16
    feature_size: int = 4
    source_train_per_arm: int = 18
    source_cal_per_arm: int = 8
    ensemble_size: int = 12
    ridge: float = 0.8
    steps: int = 160
    eval_episodes: int = 200
    bonus_strength: float = 0.35
    bonus_decay: float = 0.992
    policy_temperature: float = 0.16
    online_lr: float = 0.035
    gate_dev_seeds: int = 20
    gate_min_spearman_gain: float = 0.05
    gate_min_auroc_gain: float = 0.03


def rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    ranks[order] = np.arange(len(x), dtype=float)
    values, inverse, counts = np.unique(x, return_inverse=True, return_counts=True)
    del values
    for i, count in enumerate(counts):
        if count > 1:
            ranks[inverse == i] = ranks[inverse == i].mean()
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = rankdata(np.asarray(x)), rankdata(np.asarray(y))
    if np.std(rx) < 1e-12 or np.std(ry) < 1e-12:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=bool)
    n_pos, n_neg = labels.sum(), (~labels).sum()
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = rankdata(np.asarray(scores)) + 1.0
    return float((ranks[labels].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def risk_coverage_auc(uncertainty: np.ndarray, error: np.ndarray) -> float:
    order = np.argsort(uncertainty)  # retain least-uncertain points first
    risks = [np.mean(error[order[:k]]) for k in range(1, len(order) + 1)]
    return float(np.mean(risks))


def base_rewards(n_arms: int) -> np.ndarray:
    z = np.linspace(-1.7, 1.7, n_arms)
    return 0.15 + 0.75 / (1.0 + np.exp(-z))


def noise_scales(n_arms: int) -> np.ndarray:
    # Three visibly encoded texture groups carry irreducible label noise.
    pattern = np.array([0.04, 0.09, 0.23, 0.05])
    return np.resize(pattern, n_arms)


def render_arm(arm: int, reward: float, severity: int, rng: np.random.Generator,
               source: bool, cfg: Config) -> np.ndarray:
    n = cfg.image_size
    image = np.zeros((n, n), dtype=float)
    group = arm % 3
    cx = 3 + (arm * 5) % (n - 6)
    cy = 3 + (arm * 7) % (n - 6)
    if group == 0:
        image[max(0, cy - 2): min(n, cy + 3), max(0, cx - 1): min(n, cx + 2)] = 0.8
    elif group == 1:
        image[max(0, cy - 1): min(n, cy + 2), max(0, cx - 3): min(n, cx + 4)] = 0.8
    else:
        yy, xx = np.ogrid[:n, :n]
        image[(xx - cx) ** 2 + (yy - cy) ** 2 <= 6] = 0.8

    if source:
        texture = reward
        shift = 0
    else:
        # Target shift reverses the source shortcut and perturbs position/contrast.
        texture = (1.0 - reward) * (0.35 + 0.2 * severity)
        shift = severity - 1
    if arm % 4 == 2:
        image[:, ::2] += 0.18  # cue used by the heteroscedastic noise head
    image[::2, :] += 0.22 * texture
    if shift:
        image = np.roll(image, (shift, -shift), axis=(0, 1))
    image *= 1.0 - 0.08 * (0 if source else severity)
    image += rng.normal(0.0, 0.025 + 0.008 * severity, size=image.shape)
    return np.clip(image, 0.0, 1.0)


def features(image: np.ndarray, cfg: Config) -> np.ndarray:
    b = cfg.image_size // cfg.feature_size
    pooled = image.reshape(cfg.feature_size, b, cfg.feature_size, b).mean(axis=(1, 3))
    return np.concatenate(([1.0], pooled.ravel()))


def make_source(seed: int, cfg: Config) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    rewards, sigmas = base_rewards(cfg.n_arms), noise_scales(cfg.n_arms)
    train_x, train_y, train_arm = [], [], []
    cal_x, cal_y, cal_arm = [], [], []
    for arm in range(cfg.n_arms):
        # Unequal coverage creates epistemic structure without changing label noise.
        coverage = max(4, cfg.source_train_per_arm - arm)
        for split, count in (("train", coverage), ("cal", cfg.source_cal_per_arm)):
            for _ in range(count):
                x = features(render_arm(arm, rewards[arm], 0, rng, True, cfg), cfg)
                y = float(np.clip(rewards[arm] + rng.normal(0, sigmas[arm]), 0, 1))
                target = (train_x, train_y, train_arm) if split == "train" else (cal_x, cal_y, cal_arm)
                target[0].append(x); target[1].append(y); target[2].append(arm)
    return {
        "train_x": np.asarray(train_x), "train_y": np.asarray(train_y),
        "train_arm": np.asarray(train_arm), "cal_x": np.asarray(cal_x),
        "cal_y": np.asarray(cal_y), "cal_arm": np.asarray(cal_arm),
        "source_rewards": rewards, "noise": sigmas,
    }


def ridge_fit(x: np.ndarray, y: np.ndarray, ridge: float) -> np.ndarray:
    reg = np.eye(x.shape[1]) * ridge
    reg[0, 0] = ridge * 0.05
    return np.linalg.solve(x.T @ x + reg, x.T @ y)


def fit_reward_ensemble(source: dict[str, np.ndarray], seed: int, cfg: Config) -> np.ndarray:
    rng = np.random.default_rng(seed + 700_001)
    x, y = source["train_x"], source["train_y"]
    heads = []
    for _ in range(cfg.ensemble_size):
        idx = rng.integers(0, len(y), len(y))
        heads.append(ridge_fit(x[idx], y[idx], cfg.ridge))
    return np.asarray(heads)


def fit_aleatoric(source: dict[str, np.ndarray], heads: np.ndarray, cfg: Config) -> np.ndarray:
    x, y = source["cal_x"], source["cal_y"]
    residual2 = np.square(y - (x @ heads.T).mean(axis=1))
    # A linear non-negative variance head is calibrated on held-out source labels.
    w = ridge_fit(x, np.log(residual2 + 1e-3), cfg.ridge * 2)
    return w


def target_features(seed: int, severity: int, cfg: Config) -> np.ndarray:
    rng = np.random.default_rng(seed + 90_000 + severity)
    rewards = base_rewards(cfg.n_arms)
    return np.asarray([
        features(render_arm(a, rewards[a], severity, rng, False, cfg), cfg)
        for a in range(cfg.n_arms)
    ])


def uncertainty(heads: np.ndarray, aleatoric_w: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    predictions = x @ heads.T
    mean = np.clip(predictions.mean(axis=1), 0, 1)
    epi = predictions.std(axis=1, ddof=1)
    alea = np.sqrt(np.exp(np.clip(x @ aleatoric_w, -8, 0)))
    return mean, np.maximum(epi, 1e-5), np.maximum(alea, 1e-5)


def calibrate_scale(raw: np.ndarray, target: np.ndarray) -> float:
    return float(np.clip(np.dot(raw, target) / (np.dot(raw, raw) + 1e-9), 0.05, 20.0))


def make_layout(kind: str, epi: np.ndarray, rng: np.random.Generator, cfg: Config) -> np.ndarray:
    values = np.sort(base_rewards(cfg.n_arms))
    order = np.argsort(epi)
    reward = np.empty(cfg.n_arms)
    if kind == "aligned":
        reward[order] = values
    elif kind == "anti":
        reward[order] = values[::-1]
    elif kind == "decorrelated":
        best = None
        for _ in range(20_000):
            candidate = rng.permutation(values)
            corr = abs(spearman(candidate, epi))
            if best is None or corr < best[0]:
                best = (corr, candidate.copy())
            if corr < 0.05:
                break
        assert best is not None
        reward = best[1]
    else:
        raise ValueError(kind)
    return reward


def paired_layout(seed: int, severity: int, kind: str, epi: np.ndarray, cfg: Config) -> np.ndarray:
    """A layout seed deliberately independent of signal and regime."""
    rng = np.random.default_rng(seed * 65_537 + severity * 503 + LAYOUTS.index(kind) * 31)
    return make_layout(kind, epi, rng, cfg)


def normalize_rms(x: np.ndarray) -> np.ndarray:
    x = np.maximum(np.asarray(x, dtype=float), 0)
    return x / (math.sqrt(float(np.mean(x * x))) + 1e-9)


def softmax(x: np.ndarray) -> np.ndarray:
    z = x - np.max(x)
    e = np.exp(np.clip(z, -50, 50))
    return e / e.sum()


def update_heads(heads: np.ndarray, x: np.ndarray, y: float, rng: np.random.Generator,
                 cfg: Config) -> None:
    pred = heads @ x
    weights = rng.poisson(1.0, size=len(heads))
    grad = ((pred - y) * weights)[:, None] * x[None, :] + cfg.ridge * 0.002 * heads
    heads -= cfg.online_lr * grad


def signal_values(name: str, epi: np.ndarray, alea: np.ndarray, counts: np.ndarray,
                  fixed_shuffle: np.ndarray, fixed_uniform: np.ndarray) -> np.ndarray:
    if name == "epistemic": return normalize_rms(epi)
    if name == "aleatoric": return normalize_rms(alea)
    if name == "total": return normalize_rms(np.sqrt(epi * epi + alea * alea))
    if name == "point": return np.zeros_like(epi)
    if name == "shuffled": return normalize_rms(epi[fixed_shuffle])
    if name == "uniform": return normalize_rms(fixed_uniform)
    if name == "count": return normalize_rms(1.0 / np.sqrt(counts + 1.0))
    raise ValueError(name)


def run_one(seed: int, severity: int, layout: str, signal: str, regime: str,
            source: dict[str, np.ndarray], base_heads: np.ndarray, aleatoric_w: np.ndarray,
            epi_scale: float, alea_scale: float, cfg: Config) -> dict[str, float | int | str]:
    rng = np.random.default_rng(
        seed * 10_007 + severity * 503 + SIGNALS.index(signal) * 31 + REGIMES.index(regime) * 7
    )
    x = target_features(seed, severity, cfg)
    heads = base_heads.copy()
    proxy0, epi0, alea0 = uncertainty(heads, aleatoric_w, x)
    epi0 *= epi_scale; alea0 *= alea_scale
    true_reward = paired_layout(seed, severity, layout, epi0, cfg)
    true_noise = noise_scales(cfg.n_arms)
    fixed_shuffle = rng.permutation(cfg.n_arms)
    fixed_uniform = rng.uniform(0.0, math.sqrt(3.0), size=cfg.n_arms)
    counts = np.zeros(cfg.n_arms)
    returns, hacking, errors = [], [], []

    for step in range(cfg.steps):
        proxy, epi, alea = uncertainty(heads, aleatoric_w, x)
        epi *= epi_scale; alea *= alea_scale
        bonus = signal_values(signal, epi, alea, counts, fixed_shuffle, fixed_uniform)
        score = proxy + cfg.bonus_strength * (cfg.bonus_decay ** step) * bonus
        action = int(rng.choice(cfg.n_arms, p=softmax(score / cfg.policy_temperature)))
        counts[action] += 1
        returns.append(float(true_reward[action]))
        proxy_hi = proxy0[action] >= np.quantile(proxy0, 0.75)
        true_lo = true_reward[action] <= np.quantile(true_reward, 0.25)
        hacking.append(float(proxy_hi and true_lo))
        errors.append(float(np.mean(np.abs(proxy - true_reward))))
        if regime == "online":
            label = float(np.clip(true_reward[action] + rng.normal(0, true_noise[action]), 0, 1))
            update_heads(heads, x[action], label, rng, cfg)

    proxy_final, _, _ = uncertainty(heads, aleatoric_w, x)
    return {
        "seed": seed, "severity": severity, "layout": layout, "signal": signal,
        "regime": regime, "return_auc": float(np.mean(returns)),
        "final_window_return": float(np.mean(returns[-40:])),
        "hacking_rate": float(np.mean(hacking)), "rm_mae_auc": float(np.mean(errors)),
        "rm_mae_final": float(np.mean(np.abs(proxy_final - true_reward))),
        "epi_reward_spearman": spearman(epi0, true_reward),
    }


def offline_gate(cfg: Config) -> dict[str, float | bool | int]:
    epi_all, alea_all, error_all, shuffled_all = [], [], [], []
    for seed in range(cfg.gate_dev_seeds):
        source = make_source(seed, cfg)
        heads = fit_reward_ensemble(source, seed, cfg)
        aw = fit_aleatoric(source, heads, cfg)
        for severity in (1, 2, 3):
            x = target_features(seed, severity, cfg)
            mean, epi, alea = uncertainty(heads, aw, x)
            error = np.abs(mean - base_rewards(cfg.n_arms))
            epi_all.extend(epi); alea_all.extend(alea); error_all.extend(error)
            shuffled_all.extend(np.random.default_rng(seed + severity * 991).permutation(epi))
    epi = np.asarray(epi_all); alea = np.asarray(alea_all); error = np.asarray(error_all)
    shuffled = np.asarray(shuffled_all)
    hard = error >= np.quantile(error, 0.75)
    result = {
        "n_points": len(error), "epi_spearman": spearman(epi, error),
        "alea_spearman": spearman(alea, error), "shuffled_spearman": spearman(shuffled, error),
        "epi_auroc": auroc(epi, hard), "alea_auroc": auroc(alea, hard),
        "shuffled_auroc": auroc(shuffled, hard),
        "epi_risk_coverage_auc": risk_coverage_auc(epi, error),
        "shuffled_risk_coverage_auc": risk_coverage_auc(shuffled, error),
    }
    result["pass"] = bool(
        result["epi_spearman"] - result["shuffled_spearman"] >= cfg.gate_min_spearman_gain
        and result["epi_auroc"] - result["shuffled_auroc"] >= cfg.gate_min_auroc_gain
    )
    return result


def development_scales(cfg: Config) -> tuple[float, float]:
    raw_epi, target_error, raw_alea, target_noise = [], [], [], []
    for seed in range(10):
        source = make_source(50_000 + seed, cfg)
        heads = fit_reward_ensemble(source, 50_000 + seed, cfg)
        aw = fit_aleatoric(source, heads, cfg)
        for severity in (1, 2, 3):
            x = target_features(50_000 + seed, severity, cfg)
            mean, epi, alea = uncertainty(heads, aw, x)
            raw_epi.extend(epi); target_error.extend(np.abs(mean - base_rewards(cfg.n_arms)))
            raw_alea.extend(alea); target_noise.extend(noise_scales(cfg.n_arms))
    return calibrate_scale(np.asarray(raw_epi), np.asarray(target_error)), calibrate_scale(np.asarray(raw_alea), np.asarray(target_noise))


def run_experiment(outdir: Path, seeds: int, seed_start: int, cfg: Config) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    gate = offline_gate(cfg)
    (outdir / "offline_gate.json").write_text(json.dumps(gate, indent=2) + "\n")
    if not gate["pass"]:
        raise RuntimeError(f"Offline epistemic estimator gate failed: {gate}")
    epi_scale, alea_scale = development_scales(cfg)
    rows = []
    started = time.time()
    for seed in range(seeds):
        test_seed = seed_start + seed
        source = make_source(test_seed, cfg)
        heads = fit_reward_ensemble(source, test_seed, cfg)
        aw = fit_aleatoric(source, heads, cfg)
        for severity in (1, 2, 3):
            for layout in LAYOUTS:
                for regime in REGIMES:
                    for signal in SIGNALS:
                        rows.append(run_one(test_seed, severity, layout, signal, regime,
                                            source, heads, aw, epi_scale, alea_scale, cfg))
    with (outdir / "raw_results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    metadata = {
        "config": asdict(cfg), "seeds": seeds, "seed_start": seed_start,
        "epi_scale": epi_scale, "alea_scale": alea_scale,
        "elapsed_seconds": time.time() - started, "rows": len(rows),
        "note": "Toy procedural reward heads; not an MLLM experiment.",
    }
    (outdir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("gate", "pilot", "full"), default="gate")
    parser.add_argument("--out", type=Path, default=Path("results/mve2"))
    args = parser.parse_args()
    cfg = Config()
    if args.mode == "gate":
        print(json.dumps(offline_gate(cfg), indent=2))
    else:
        if args.mode == "pilot":
            run_experiment(args.out, seeds=3, seed_start=60_000, cfg=cfg)
        else:
            run_experiment(args.out, seeds=50, seed_start=200_000, cfg=cfg)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
