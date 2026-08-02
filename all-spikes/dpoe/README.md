# DPOE Autoresearch Artifact

This repository is the unedited output of a seven-day stress test of a screened research
plan: calibrated MLLM reward uncertainty for visual-domain adaptation. The available host
had no GPU, so the artifact contains CPU-scale synthetic mechanism tests, not an MLLM or
robotics validation.

## Closed claim status

- **C1 (calibration versus capacity): untested.** MVE 1 did not run.
- **C2 (epistemic is the signal):** the frozen information-gain rationale is structurally
  killed analytically and corroborated by MVE 2; the stronger online-estimator claim is
  unresolved.
- **C3 (P/K/O coupling): untested at toy scale.** MVE 3 v1 had an exploitation floor; v2
  was **not solvable within the preregistered grid**.

Experiments are closed. No pilot-v2 or locked-v2 seed was opened.

## Artifact map

| Path | Contents |
|---|---|
| `mve2/`, `results/mve2-full/` | Frozen/online uncertainty-signal experiment, raw rows, analysis, plot |
| `mve3/`, `results/mve3-locked/` | Resumable v1 P×K×O factorial, raw cells, audits, amended verdict, plot |
| `mve3v2/`, `results/mve3v2-development/` | Development-only v2 solvability gate and report-only audit |
| `paper/` | CAISc LaTeX source and visually verified seven-page PDF |
| `deck/` | Beamer source and PDF; critique/reflection slides are human-only placeholders |
| `iterated-research-plan.md` | Agent-proposed plan revision with evidence changelog |
| `PROGRESS.md`, `LEARNINGS.md`, `BUDGET.md` | Session audit, claim evidence, time/cost record |
| `reviews/` | Claude review artifacts, including failed and human-mediated captures |

The local `papers/` literature library is intentionally excluded from version control.

## Environment

The runs used Python 3.12, NumPy, and Matplotlib in `.venv/`; no GPU or paid experiment
compute was used. From `all-spikes/dpoe/`, install the local dependencies if needed:

```bash
python3 -m venv .venv
.venv/bin/pip install numpy matplotlib
```

## Reproduce or audit MVE 2

Analysis-only regeneration from the retained locked rows:

```bash
cd mve2
../.venv/bin/python -m unittest -v test_mve2.py
../.venv/bin/python analyze.py --results ../results/mve2-full
```

A full rerun is documented in `mve2/README.md`. It is not necessary to inspect the
canonical artifact and would create a new execution record.

## Reproduce or audit MVE 3 v1

Validate retained locked cells and regenerate analysis:

```bash
cd mve3
../.venv/bin/python -m unittest -v test_mve3.py
../.venv/bin/python integrity.py --root ../results/mve3-locked --split locked --replicates 50
../.venv/bin/python analyze.py --root ../results/mve3-locked --replicates 50
```

The resumable full-run command and corrected-v1 pilot path are documented in
`mve3/README.md`. The earlier `results/mve3-pilot/` is debugging-only.

## Audit MVE 3 v2

```bash
../.venv/bin/python -m unittest -v mve3v2/test_gates.py
```

The canonical development result is
`results/mve3v2-development/development-solvability-failed.json`. Its report-only
regeneration records identical SHA-256 fingerprints for every pre-existing metric. Do not
interpret the boundary best tuple as global unsolvability or as permission to extend the
grid.

## Build the paper and deck

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error dpoe_negative_result.tex
pdflatex -interaction=nonstopmode -halt-on-error dpoe_negative_result.tex

cd ../deck
pdflatex -interaction=nonstopmode -halt-on-error deck.tex
pdflatex -interaction=nonstopmode -halt-on-error deck.tex
```

## Human intervention and AI effort

| Stage | Division of labor |
|---|---|
| Research question | Human-authored, Lossfunk-screened plan; the agent did not choose a new topic |
| MVE design | Codex drafted protocols; Claude reviewed; the human selected scope and authorized each execution |
| Implementation/execution | Codex implemented, tested, ran, resumed, and analyzed local experiments after authorization |
| Interpretation | Codex drafted conclusions; Claude reviews exposed the v1 exploitation floor and later audit defects; the human supplied several manual review files and closure decisions |
| Plan and paper | Codex wrote both with the strongest available driver model; the human did not edit the paper |
| Deck | Codex prepared factual slides; critique and reflection remain blank human-only placeholders |

Review transport was imperfect: several Claude CLI calls returned empty output or API
errors, after which the human supplied manual Claude runs. Review 15 was initially reported
as APPROVE but its saved file said REVISE; the audit log and stale pilot name were corrected.
This failure history is part of the artifact rather than being sanitized away.
