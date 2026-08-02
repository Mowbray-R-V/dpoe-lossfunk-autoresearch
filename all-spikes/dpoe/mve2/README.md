# MVE 2 implementation

Mechanism-level procedural visual contextual bandit for Control A and the frozen-versus-
online reward-model audit. This code does **not** use an MLLM.

From `all-spikes/dpoe/mve2/`:

```bash
../.venv/bin/python -m unittest -v test_mve2.py
../.venv/bin/python mve2.py --mode gate
../.venv/bin/python mve2.py --mode pilot --out ../results/mve2-pilot
../.venv/bin/python mve2.py --mode full --out ../results/mve2-full
```

The full command refuses to start policy runs if the development-only offline epistemic
estimator gate fails.
