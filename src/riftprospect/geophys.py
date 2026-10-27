"""Part B: rule-based geophysical evidence for small mafic-ultramafic intrusions.

Plain-language note: magmatic nickel deposits like Eagle sit in small, dense, magnetic
intrusions of mafic and ultramafic rock, which are low in potassium and thorium. This file
turns each airborne measurement into a 0-to-1 "how much does this square look like that"
score, then combines them with weights. Weights are DECISION D6 (yours). Uncertainty comes
from re-running with randomly varied weights and transition points (Monte Carlo).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Evidence layers: (column, direction). +1 = higher is more favorable; -1 = lower is.
# Rationale (to be checked by Bezali, D6):
#   rtp_asig  : strong magnetic gradients mark discrete magnetic bodies (pyrrhotite/magnetite-bearing intrusions)
#   rtp_resid : magnetic high relative to the surrounding 2 km
#   k, th     : mafic-ultramafic rocks are poor in K and Th
LAYERS = {"rtp_asig": +1, "rtp_resid": +1, "k": -1, "th": -1}
# DECISION D6: provisional equal-ish weights, magnetics favored because cover attenuates gamma rays.
WEIGHTS = {"rtp_asig": 0.35, "rtp_resid": 0.35, "k": 0.15, "th": 0.15}
MIDPOINT_PCT = 75.0   # logistic membership centred at this percentile (direction-adjusted)
SPREAD_PCT = 10.0


def percentile_rank(v: np.ndarray) -> np.ndarray:
    """0-100 percentile of each value within the survey (NaN stays NaN)."""
    out = np.full(v.shape, np.nan)
    ok = ~np.isnan(v)
    order = v[ok].argsort().argsort()
    out[ok] = 100.0 * order / max(ok.sum() - 1, 1)
    return out


def membership(pct: np.ndarray, direction: int, mid=MIDPOINT_PCT, spread=SPREAD_PCT) -> np.ndarray:
    p = pct if direction > 0 else 100.0 - pct
    return 1.0 / (1.0 + np.exp(-(p - mid) / spread))


def evidence(df: pd.DataFrame, by_block: bool = True) -> pd.DataFrame:
    """Percentile ranks per layer. Ranked within each survey block because the blocks differ
    in line spacing (150 m vs 400 m) and therefore in how sharp the gradients are."""
    out = pd.DataFrame(index=df.index)
    groups = df.groupby("block").groups if by_block else {"all": df.index}
    for col in LAYERS:
        r = pd.Series(np.nan, index=df.index)
        for _, idx in groups.items():
            r.loc[idx] = percentile_rank(df.loc[idx, col].to_numpy(dtype=float))
        out[col] = r
    return out


def score(pct: pd.DataFrame, weights=None, mid=MIDPOINT_PCT, spread=SPREAD_PCT) -> np.ndarray:
    """Weighted mean of memberships; a missing layer is skipped and the weights renormalized."""
    weights = weights or WEIGHTS
    num = np.zeros(len(pct)); den = np.zeros(len(pct))
    for col, d in LAYERS.items():
        m = membership(pct[col].to_numpy(), d, mid, spread)
        ok = ~np.isnan(m)
        num[ok] += weights[col] * m[ok]; den[ok] += weights[col]
    return num / np.where(den > 0, den, np.nan)


def monte_carlo(pct: pd.DataFrame, n: int = 100, seed: int = 0, concentration: float = 20.0):
    """Mean and SD of the score when weights ~ Dirichlet around WEIGHTS and the midpoint ~ U(65, 85)."""
    rng = np.random.default_rng(seed)
    base = np.array([WEIGHTS[c] for c in LAYERS])
    runs = np.empty((n, len(pct)), dtype="float32")
    for i in range(n):
        w = dict(zip(LAYERS, rng.dirichlet(base * concentration)))
        runs[i] = score(pct, w, mid=rng.uniform(65, 85))
    return runs.mean(0), runs.std(0)
