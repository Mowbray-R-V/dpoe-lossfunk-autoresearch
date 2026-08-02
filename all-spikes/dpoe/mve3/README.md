# MVE 3 implementation

Signal-quality-conditional P×K×O coupling test. This is a synthetic online reward-posterior
experiment, not an MLLM experiment.

Commands from this directory:

```bash
../.venv/bin/python -m unittest -v test_mve3.py
../.venv/bin/python gates.py --split development --replicates 20 --out ../results/mve3-gates
../.venv/bin/python run.py --split pilot --replicates 5 --root ../results/mve3-pilot-corrected-v1
../.venv/bin/python integrity.py --root ../results/mve3-pilot-corrected-v1 --split pilot --replicates 5
../.venv/bin/python pilot_decision.py --pilot-root ../results/mve3-pilot-corrected-v1 \
  --out ../results/mve3-pilot-corrected-v1/locked-decision.json
../.venv/bin/python run.py --split locked --replicates 50 \
  --root ../results/mve3-locked --confirm-locked \
  --development-gate ../results/mve3-gates/development-gates.json \
  --pilot-decision ../results/mve3-pilot-corrected-v1/locked-decision.json
```

## Interruption and resume

Each cell is atomically committed to `cells/<cell-id>.npz`. Re-running the identical command
validates and skips completed cells, then resumes at the first missing cell. A partial cell
has only a temporary filename and is ignored; at most that one cell is recomputed. Use
`--max-new-cells N` to test or deliberately limit an invocation.
