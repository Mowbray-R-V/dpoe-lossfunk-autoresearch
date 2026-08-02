"""Core mechanisms for MVE 3's synthetic signal-quality coupling test."""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


PROTOCOL_VERSION = "mve3-v2-approved-2026-07-18"
TIERS = ("controlled", "learned", "shuffled", "anti")
CELLS = ("none", "p", "k", "o", "pk", "po", "ko", "pko")
CELL_FACTORS = {
    "none": frozenset(), "p": frozenset("p"), "k": frozenset("k"),
    "o": frozenset("o"), "pk": frozenset("pk"), "po": frozenset("po"),
    "ko": frozenset("ko"), "pko": frozenset("pko"),
}
N_INTERNAL = 7
N_TERMINALS = 8
DEPTH = 3


@dataclass(frozen=True)
class Config:
    iterations: int = 100
    collection_episodes: int = 16
    eval_every: int = 10
    eval_episodes: int = 200
    source_episodes: int = 2_000
    source_max_episodes: int = 10_000
    source_eval_episodes: int = 200
    source_competence: float = 0.80
    beta0: float = 0.22
    eta: float = 2.0
    pessimism_lambda: float = 0.65
    tau_collect: float = 0.18
    tau_reference: float = 0.10
    label_sigma: float = 0.22
    reward_clip: float = 1.25
    ensemble_size: int = 12
    ridge: float = 0.7
    ensemble_lr: float = 0.025


@dataclass(frozen=True)
class CellSpec:
    split: str
    replicate: int
    severity: int
    tier: str
    cell: str

    @property
    def cell_id(self) -> str:
        return f"r{self.replicate:03d}_s{self.severity}_{self.tier}_{self.cell}"


def stable_seed(*parts: object) -> int:
    payload = json.dumps([PROTOCOL_VERSION, *parts], separators=(",", ":"), sort_keys=False).encode()
    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "little")


def seeded_rng(*parts: object) -> np.random.Generator:
    return np.random.default_rng(stable_seed(*parts))


def rankdata(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), float)
    ranks[order] = np.arange(len(x), dtype=float)
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    for i, count in enumerate(counts):
        if count > 1:
            ranks[inv == i] = ranks[inv == i].mean()
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = rankdata(np.asarray(x)), rankdata(np.asarray(y))
    if np.std(rx) < 1e-12 or np.std(ry) < 1e-12:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def partial_spearman(x: np.ndarray, y: np.ndarray, controls: np.ndarray) -> float:
    rx, ry = rankdata(x), rankdata(y)
    c = np.asarray(controls, float)
    if c.ndim == 1:
        c = c[:, None]
    rc = np.column_stack([np.ones(len(c)), *[rankdata(c[:, j]) for j in range(c.shape[1])]])
    ex = rx - rc @ np.linalg.lstsq(rc, rx, rcond=None)[0]
    ey = ry - rc @ np.linalg.lstsq(rc, ry, rcond=None)[0]
    if np.std(ex) < 1e-12 or np.std(ey) < 1e-12:
        return 0.0
    return float(np.corrcoef(ex, ey)[0, 1])


def auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    labels = np.asarray(labels, bool)
    n_pos, n_neg = int(labels.sum()), int((~labels).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = rankdata(np.asarray(scores)) + 1
    return float((ranks[labels].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def risk_coverage_auc(uncertainty: np.ndarray, error: np.ndarray) -> float:
    order = np.argsort(uncertainty)
    return float(np.mean([np.mean(error[order[:k]]) for k in range(1, len(order) + 1)]))


def softmax(logits: np.ndarray) -> np.ndarray:
    z = np.asarray(logits, float) - np.max(logits)
    e = np.exp(np.clip(z, -60, 60))
    return e / e.sum()


def children(state: int) -> tuple[int, int]:
    return 2 * state + 1, 2 * state + 2


def terminal_descendants(state: int) -> list[int]:
    frontier, terminals = [state], []
    while frontier:
        node = frontier.pop()
        if node >= N_INTERNAL:
            terminals.append(node - N_INTERNAL)
        else:
            frontier.extend(children(node))
    return terminals


DESCENDANTS = tuple(tuple(terminal_descendants(s)) for s in range(N_INTERNAL))


def policy_from_rewards(terminal_rewards: np.ndarray, temperature: float,
                        reference: np.ndarray | None = None,
                        beta_by_state: np.ndarray | None = None) -> np.ndarray:
    values = np.zeros(N_INTERNAL)
    policy = np.zeros((N_INTERNAL, 2))
    for state in range(N_INTERNAL - 1, -1, -1):
        q = []
        for child in children(state):
            q.append(terminal_rewards[child - N_INTERNAL] if child >= N_INTERNAL else values[child])
        qv = np.asarray(q)
        if reference is None:
            p = softmax(qv / temperature)
            values[state] = temperature * (np.log(np.exp((qv - qv.max()) / temperature).sum()) + qv.max() / temperature)
        else:
            beta = float(beta_by_state[state] if beta_by_state is not None else temperature)
            logits = np.log(np.maximum(reference[state], 1e-9)) + qv / beta
            p = softmax(logits)
            m = float(np.max(qv / beta))
            values[state] = beta * (m + math.log(float(np.sum(reference[state] * np.exp(qv / beta - m)))))
        policy[state] = p
    return policy


def sample_terminal(policy: np.ndarray, uniforms: Iterable[float]) -> int:
    state = 0
    for u in uniforms:
        action = 0 if float(u) < policy[state, 0] else 1
        state = children(state)[action]
    if state < N_INTERNAL:
        raise RuntimeError("episode did not reach terminal")
    return state - N_INTERNAL


def terminal_probabilities(policy: np.ndarray) -> np.ndarray:
    probs = np.zeros(N_INTERNAL + N_TERMINALS)
    probs[0] = 1.0
    for state in range(N_INTERNAL):
        for action, child in enumerate(children(state)):
            probs[child] += probs[state] * policy[state, action]
    return probs[N_INTERNAL:]


def policy_entropy(policy: np.ndarray) -> float:
    p = np.maximum(policy, 1e-12)
    return float(np.mean(-np.sum(p * np.log(p), axis=1)))


def policy_kl(policy: np.ndarray, reference: np.ndarray) -> float:
    p, q = np.maximum(policy, 1e-12), np.maximum(reference, 1e-12)
    return float(np.mean(np.sum(p * np.log(p / q), axis=1)))


def train_reference(split: str, replicate: int, cfg: Config) -> tuple[np.ndarray, float, np.ndarray]:
    rewards = np.full(N_TERMINALS, -0.2)
    rewards[0] = 1.0
    rng = seeded_rng(split, replicate, "source_training")
    q = np.zeros((N_INTERNAL, 2))
    visits = np.zeros_like(q)
    episodes = cfg.source_episodes
    for episode in range(cfg.source_max_episodes):
        state, path = 0, []
        epsilon = max(0.02, 0.35 * (1 - episode / cfg.source_max_episodes))
        for _ in range(DEPTH):
            action = int(rng.integers(2)) if rng.random() < epsilon else int(np.argmax(q[state]))
            path.append((state, action))
            state = children(state)[action]
        reward = rewards[state - N_INTERNAL]
        target = reward
        for s, a in reversed(path):
            visits[s, a] += 1
            lr = max(0.03, 1.0 / math.sqrt(visits[s, a]))
            q[s, a] += lr * (target - q[s, a])
            target = float(np.max(q[s]))
        if episode + 1 == episodes:
            candidate = np.asarray([softmax(row / cfg.tau_reference) for row in q])
            competence = evaluate_source(candidate, rewards, split, replicate, cfg)
            if competence >= cfg.source_competence:
                return candidate, competence, rewards
            episodes = cfg.source_max_episodes
    policy = np.asarray([softmax(row / cfg.tau_reference) for row in q])
    return policy, evaluate_source(policy, rewards, split, replicate, cfg), rewards


def evaluate_source(policy: np.ndarray, rewards: np.ndarray, split: str, replicate: int,
                    cfg: Config) -> float:
    rng = seeded_rng(split, replicate, "source_evaluation")
    observed = [rewards[sample_terminal(policy, rng.random(DEPTH))]
                for _ in range(cfg.source_eval_episodes)]
    return float(np.mean(observed))


def render_terminal(terminal: int, severity: int, split: str, replicate: int) -> np.ndarray:
    rng = seeded_rng(split, replicate, severity, terminal, "visual_render")
    image = np.zeros((16, 16), float)
    x, y = 2 + (terminal * 5) % 12, 2 + (terminal * 7) % 12
    image[max(0, y - 1):min(16, y + 2), max(0, x - 2):min(16, x + 3)] = 0.8
    image[::2, :] += 0.05 * terminal
    if severity:
        image = np.roll(image, (severity, -severity), axis=(0, 1))
        image[:, ::2] += 0.10 * severity
        image *= 1 - 0.08 * severity
    image += rng.normal(0, 0.025 + 0.01 * severity, image.shape)
    return np.clip(image, 0, 1)


def image_features(image: np.ndarray) -> np.ndarray:
    pooled = image.reshape(4, 4, 4, 4).mean(axis=(1, 3))
    return np.concatenate([[1.0], pooled.ravel()])


def ridge_fit(x: np.ndarray, y: np.ndarray, ridge: float) -> np.ndarray:
    reg = np.eye(x.shape[1]) * ridge
    reg[0, 0] *= 0.05
    return np.linalg.solve(x.T @ x + reg, x.T @ y)


def learned_ensemble(split: str, replicate: int, source_rewards: np.ndarray,
                     cfg: Config) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for terminal in range(N_TERMINALS):
        base = render_terminal(terminal, 0, split, replicate)
        for sample in range(14):
            rng = seeded_rng(split, replicate, terminal, sample, "reward_bootstrap_source")
            xs.append(image_features(np.clip(base + rng.normal(0, 0.03, base.shape), 0, 1)))
            ys.append(float(source_rewards[terminal] + rng.normal(0, 0.08)))
    x, y = np.asarray(xs), np.asarray(ys)
    heads = []
    for member in range(cfg.ensemble_size):
        rng = seeded_rng(split, replicate, member, "reward_bootstrap_member")
        idx = rng.integers(0, len(y), len(y))
        heads.append(ridge_fit(x[idx], y[idx], cfg.ridge))
    return np.asarray(heads), x


def update_ensemble(heads: np.ndarray, x: np.ndarray, label: float, weight_seed: int,
                    cfg: Config) -> None:
    rng = np.random.default_rng(weight_seed)
    weights = rng.poisson(1.0, len(heads))
    pred = heads @ x
    grad = ((pred - label) * weights)[:, None] * x[None, :] + cfg.ridge * 0.001 * heads
    heads -= cfg.ensemble_lr * grad


@dataclass
class Scenario:
    split: str
    replicate: int
    severity: int
    reference: np.ndarray
    reference_competence: float
    source_rewards: np.ndarray
    mu0: np.ndarray
    u0: np.ndarray
    true_rewards: np.ndarray
    label_sigma: np.ndarray
    goal_terminal: int
    trap_terminal: int
    trap_present: bool
    goal_strength: float
    trap_strength: float
    target_features: np.ndarray
    ensemble0: np.ndarray
    learned_scale: float


def make_scenario(split: str, replicate: int, severity: int, cfg: Config) -> Scenario:
    reference, competence, source_rewards = train_reference(split, replicate, cfg)
    ref_terminal_p = terminal_probabilities(reference)
    mu_rng = seeded_rng(split, replicate, severity, "controlled_prior_mean")
    scale_rng = seeded_rng(split, replicate, severity, "controlled_prior_scale")
    truth_rng = seeded_rng(split, replicate, severity, "controlled_truth_draw")
    mu0 = mu_rng.normal(0.12 + 0.04 * severity, 0.32, N_TERMINALS)
    lo, hi = math.log(0.035), math.log(0.85 + 0.15 * severity)
    u0 = np.exp(scale_rng.uniform(lo, hi, N_TERMINALS))
    true_rewards = np.clip(truth_rng.normal(mu0, u0), -cfg.reward_clip, cfg.reward_clip)
    label_sigma = np.full(N_TERMINALS, cfg.label_sigma + 0.025 * severity)
    low_ref = np.argsort(ref_terminal_p)[:N_TERMINALS // 2]
    goal = int(low_ref[np.argmax(true_rewards[low_ref])])
    trap_candidates = np.flatnonzero(true_rewards <= 0)
    trap_present = len(trap_candidates) > 0
    trap = int(trap_candidates[np.argmax(mu0[trap_candidates])]) if trap_present else -1
    trap_strength = float(mu0[trap] - true_rewards[trap]) if trap_present else 0.0
    ensemble0, _ = learned_ensemble(split, replicate, source_rewards, cfg)
    tx = np.asarray([image_features(render_terminal(t, severity, split, replicate))
                     for t in range(N_TERMINALS)])
    learned_raw = np.std(tx @ ensemble0.T, axis=1, ddof=1)
    learned_scale = float(np.sqrt(np.mean(u0 * u0)) / (np.sqrt(np.mean(learned_raw * learned_raw)) + 1e-9))
    return Scenario(split, replicate, severity, reference, competence, source_rewards,
                    mu0, u0, true_rewards, label_sigma, goal, trap, trap_present,
                    float(true_rewards[goal]), trap_strength, tx, ensemble0, learned_scale)


def posterior_update(mean: float, variance: float, label: float, label_sigma: float) -> tuple[float, float]:
    precision = 1.0 / variance
    label_precision = 1.0 / (label_sigma * label_sigma)
    new_variance = 1.0 / (precision + label_precision)
    new_mean = new_variance * (precision * mean + label_precision * label)
    return float(new_mean), float(new_variance)


def tier_initial_u(scenario: Scenario, tier: str) -> np.ndarray:
    if tier == "controlled":
        return scenario.u0.copy()
    if tier == "shuffled":
        rng = seeded_rng(scenario.split, scenario.replicate, scenario.severity, "shuffled_initial")
        return scenario.u0[rng.permutation(N_TERMINALS)]
    if tier == "anti":
        return np.sort(scenario.u0)[::-1][np.argsort(np.argsort(scenario.u0))]
    if tier == "learned":
        raw = np.std(scenario.target_features @ scenario.ensemble0.T, axis=1, ddof=1)
        return np.maximum(raw * scenario.learned_scale, 1e-5)
    raise ValueError(tier)


def reported_u(tier: str, initial_u: np.ndarray, internal_variance: np.ndarray,
               counts: np.ndarray, label_sigma: np.ndarray, heads: np.ndarray,
               target_features: np.ndarray, learned_scale: float) -> np.ndarray:
    if tier == "controlled":
        return np.sqrt(internal_variance)
    if tier in {"shuffled", "anti"}:
        return 1.0 / np.sqrt(1.0 / np.square(initial_u) + counts / np.square(label_sigma))
    if tier == "learned":
        return np.maximum(np.std(target_features @ heads.T, axis=1, ddof=1) * learned_scale, 1e-5)
    raise ValueError(tier)


def exploitation_policy(mean: np.ndarray, u: np.ndarray, reference: np.ndarray,
                        cell: str, cfg: Config) -> np.ndarray:
    present = CELL_FACTORS[cell]
    rewards = mean - cfg.pessimism_lambda * u if "p" in present else mean
    state_u = np.asarray([np.mean(u[list(DESCENDANTS[s])]) for s in range(N_INTERNAL)])
    beta = cfg.beta0 * (1 + cfg.eta * state_u) if "k" in present else np.full(N_INTERNAL, cfg.beta0)
    return policy_from_rewards(rewards, cfg.beta0, reference=reference, beta_by_state=beta)


def collector_policy(mean: np.ndarray, u: np.ndarray, spec: CellSpec, iteration: int,
                     episode: int, cfg: Config) -> np.ndarray:
    if "o" not in CELL_FACTORS[spec.cell]:
        return policy_from_rewards(mean, cfg.tau_collect)
    rng = seeded_rng(spec.split, spec.replicate, spec.severity, spec.tier,
                     iteration, episode, "posterior_sampling_collector")
    sampled = rng.normal(mean, u)
    return policy_from_rewards(sampled, cfg.tau_collect)


def label_for_visit(scenario: Scenario, terminal: int, visit_index: int) -> float:
    rng = seeded_rng(scenario.split, scenario.replicate, scenario.severity,
                     terminal, visit_index, "label_noise")
    return float(rng.normal(scenario.true_rewards[terminal], scenario.label_sigma[terminal]))


def evaluate_policy(policy: np.ndarray, scenario: Scenario, checkpoint: int,
                    mean: np.ndarray, cfg: Config) -> dict[str, np.ndarray | float]:
    terminals = np.empty(cfg.eval_episodes, np.int8)
    for episode in range(cfg.eval_episodes):
        rng = seeded_rng(scenario.split, scenario.replicate, scenario.severity,
                         checkpoint, episode, "evaluation_dynamics")
        terminals[episode] = sample_terminal(policy, rng.random(DEPTH))
    true_return = scenario.true_rewards[terminals]
    proxy_return = mean[terminals]
    hacking = (terminals == scenario.trap_terminal) if scenario.trap_present else np.zeros(cfg.eval_episodes, bool)
    goal = terminals == scenario.goal_terminal
    return {"terminals": terminals, "true_return": true_return, "proxy_return": proxy_return,
            "hacking": hacking.astype(np.int8), "goal": goal.astype(np.int8),
            "entropy": policy_entropy(policy), "kl": policy_kl(policy, scenario.reference)}


def factors(cell: str) -> tuple[bool, bool, bool]:
    present = CELL_FACTORS[cell]
    return "p" in present, "k" in present, "o" in present


def run_cell(spec: CellSpec, cfg: Config) -> dict[str, np.ndarray]:
    if spec.tier not in TIERS or spec.cell not in CELLS:
        raise ValueError(spec)
    scenario = make_scenario(spec.split, spec.replicate, spec.severity, cfg)
    mean = scenario.mu0.copy()
    variance = np.square(scenario.u0)
    counts = np.zeros(N_TERMINALS, int)
    heads = scenario.ensemble0.copy()
    initial_u = tier_initial_u(scenario, spec.tier)
    checkpoints = np.arange(0, cfg.iterations + 1, cfg.eval_every)
    n_checkpoints = len(checkpoints)
    eval_terminals = np.empty((n_checkpoints, cfg.eval_episodes), np.int8)
    eval_true = np.empty((n_checkpoints, cfg.eval_episodes), np.float32)
    eval_proxy = np.empty_like(eval_true)
    eval_hacking = np.empty((n_checkpoints, cfg.eval_episodes), np.int8)
    eval_goal = np.empty_like(eval_hacking)
    eval_entropy = np.empty(n_checkpoints, np.float32)
    eval_kl = np.empty(n_checkpoints, np.float32)
    posterior_mean = np.empty((n_checkpoints, N_TERMINALS), np.float32)
    posterior_u = np.empty_like(posterior_mean)
    collection_terminal = np.empty((cfg.iterations, cfg.collection_episodes), np.int8)
    collection_true = np.empty((cfg.iterations, cfg.collection_episodes), np.float32)
    collection_proxy = np.empty_like(collection_true)
    collection_label = np.empty_like(collection_true)
    collection_goal = np.empty((cfg.iterations, cfg.collection_episodes), np.int8)

    def record(index: int, iteration: int) -> None:
        u = reported_u(spec.tier, initial_u, variance, counts, scenario.label_sigma,
                       heads, scenario.target_features, scenario.learned_scale)
        policy = exploitation_policy(mean, u, scenario.reference, spec.cell, cfg)
        result = evaluate_policy(policy, scenario, iteration, mean, cfg)
        eval_terminals[index] = result["terminals"]
        eval_true[index] = result["true_return"]
        eval_proxy[index] = result["proxy_return"]
        eval_hacking[index] = result["hacking"]
        eval_goal[index] = result["goal"]
        eval_entropy[index] = result["entropy"]
        eval_kl[index] = result["kl"]
        posterior_mean[index] = mean
        posterior_u[index] = u

    record(0, 0)
    checkpoint_index = 1
    for iteration in range(1, cfg.iterations + 1):
        for episode in range(cfg.collection_episodes):
            u = reported_u(spec.tier, initial_u, variance, counts, scenario.label_sigma,
                           heads, scenario.target_features, scenario.learned_scale)
            collector = collector_policy(mean, u, spec, iteration, episode, cfg)
            rng = seeded_rng(spec.split, spec.replicate, spec.severity,
                             spec.tier if "o" in CELL_FACTORS[spec.cell] else "shared",
                             iteration, episode, "collection_dynamics")
            terminal = sample_terminal(collector, rng.random(DEPTH))
            visit_index = int(counts[terminal])
            label = label_for_visit(scenario, terminal, visit_index)
            collection_terminal[iteration - 1, episode] = terminal
            collection_true[iteration - 1, episode] = scenario.true_rewards[terminal]
            collection_proxy[iteration - 1, episode] = mean[terminal]
            collection_label[iteration - 1, episode] = label
            collection_goal[iteration - 1, episode] = int(terminal == scenario.goal_terminal)
            mean[terminal], variance[terminal] = posterior_update(
                mean[terminal], variance[terminal], label, scenario.label_sigma[terminal])
            counts[terminal] += 1
            update_ensemble(heads, scenario.target_features[terminal], label,
                            stable_seed(spec.split, spec.replicate, spec.severity, terminal,
                                        visit_index, "bootstrap_online_weight"), cfg)
        if iteration % cfg.eval_every == 0:
            record(checkpoint_index, iteration)
            checkpoint_index += 1

    meta = {
        "complete": True, "protocol_version": PROTOCOL_VERSION, "spec": asdict(spec),
        "config": asdict(cfg), "reference_competence": scenario.reference_competence,
        "goal_terminal": scenario.goal_terminal, "trap_terminal": scenario.trap_terminal,
        "trap_present": scenario.trap_present, "goal_strength": scenario.goal_strength,
        "trap_strength": scenario.trap_strength, "mu0": scenario.mu0.tolist(),
        "u0": scenario.u0.tolist(), "true_rewards": scenario.true_rewards.tolist(),
        "learned_scale": scenario.learned_scale,
    }
    return {
        "metadata": np.asarray(json.dumps(meta)), "checkpoints": checkpoints,
        "eval_terminal": eval_terminals, "eval_true": eval_true, "eval_proxy": eval_proxy,
        "eval_hacking": eval_hacking, "eval_goal": eval_goal, "eval_entropy": eval_entropy,
        "eval_kl": eval_kl, "posterior_mean": posterior_mean, "posterior_u": posterior_u,
        "collection_terminal": collection_terminal, "collection_true": collection_true,
        "collection_proxy": collection_proxy, "collection_label": collection_label,
        "collection_goal": collection_goal,
    }


def atomic_save_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp-{os.getpid()}")
    try:
        with temp.open("wb") as f:
            np.savez_compressed(f, **arrays)
            f.flush(); os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp-{os.getpid()}")
    try:
        with temp.open("w") as f:
            json.dump(value, f, indent=2, sort_keys=True); f.write("\n")
            f.flush(); os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def validate_cell(path: Path, spec: CellSpec, cfg: Config) -> bool:
    try:
        with np.load(path, allow_pickle=False) as data:
            meta = json.loads(str(data["metadata"]))
            expected_eval = cfg.iterations // cfg.eval_every + 1
            return bool(meta.get("complete") and meta.get("protocol_version") == PROTOCOL_VERSION
                        and meta.get("spec") == asdict(spec)
                        and data["eval_terminal"].shape == (expected_eval, cfg.eval_episodes)
                        and data["collection_terminal"].shape == (cfg.iterations, cfg.collection_episodes))
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


def cell_specs(split: str, replicates: int) -> list[CellSpec]:
    return [CellSpec(split, r, severity, tier, cell)
            for r in range(replicates) for severity in (1, 2, 3)
            for tier in TIERS for cell in CELLS]


def cell_path(root: Path, spec: CellSpec) -> Path:
    return root / "cells" / f"{spec.cell_id}.npz"
