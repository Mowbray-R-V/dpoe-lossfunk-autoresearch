"""Shared primary-estimand metrics for MVE 3 analyses and v2 gates."""
from __future__ import annotations

import numpy as np


def normalized_auc(values: np.ndarray, x: np.ndarray | None = None) -> float:
    """Normalized trapezoidal AUC; singleton curves reduce to their sole value."""
    values = np.asarray(values, dtype=float)
    if x is None:
        x = np.arange(len(values), dtype=float)
    else:
        x = np.asarray(x, dtype=float)
    if len(values) == 1:
        return float(values[0])
    return float(np.trapezoid(values, x) / (x[-1] - x[0]))
