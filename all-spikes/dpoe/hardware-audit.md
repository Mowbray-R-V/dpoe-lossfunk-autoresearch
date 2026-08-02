# Local Hardware and Software Audit

Audit time: 2026-07-17 06:38 UTC.

| Resource | Available |
|---|---|
| OS | Linux under WSL2, x86-64 |
| CPU | AMD Ryzen 3 7320U; 4 cores, 8 threads |
| RAM | 5.8 GiB total; 5.2 GiB available during audit |
| Swap | 4.0 GiB |
| GPU | No NVIDIA GPU visible; `nvidia-smi` absent |
| Disk | 952 GiB free in repository filesystem |
| Python | 3.12.3 |
| Scientific packages | NumPy, SciPy, scikit-learn, PyTorch, Gymnasium, pandas, and Matplotlib absent from system Python |
| Reviewer | Claude Code 2.1.209 available |

## Design consequence

Do not attempt local Qwen/Idefics inference, MetaWorld, or PPO-scale visual RL. Prefer
small CPU experiments that test the proposed causal mechanisms while explicitly avoiding
claims about real MLLM behavior. Any cloud/API alternative requires an advance estimate,
budget entry, and human approval.
