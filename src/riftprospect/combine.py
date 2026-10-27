"""Combine chemistry and geophysics on the grid, and turn high-scoring cells into ranked targets.

Plain-language note: each 200 m square gets a geophysics score everywhere, and a chemistry
score only where rock samples are close enough. Where chemistry exists the two are blended;
where it does not, the square is marked "geophysics only". Adjacent high-scoring squares are
grouped into targets and ranked. Choices marked DECISION are in docs/DECISIONS.md.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

CHEM_RADIUS_KM = 5.0     # DECISION D10: how far a sample's chemistry is allowed to reach
CHEM_WEIGHT = 0.3        # DECISION D10: share of the blended score from chemistry
TARGET_TOP_PCT = 2.0     # DECISION D7: cells in the top 2% of combined score become target cells
EDGE_M = 1000.0          # QA rule: cells within 1 km of a data edge cannot become targets (derivative artifacts)
MIN_TARGET_CELLS = 1     # DECISION D7: single 200 m cells kept, because Eagle-type intrusions are about one cell across (changed from 3 after Eagle dropped out: disclosed)


def chem_to_grid(cells_xy, samp_xy, samp_mean, samp_sd, radius_km=CHEM_RADIUS_KM, power=2.0):
    """Inverse-distance-weighted chemistry score per cell from samples within `radius_km`."""
    n = len(cells_xy)
    mean = np.full(n, np.nan); sd = np.full(n, np.nan); count = np.zeros(n, dtype=int)
    if len(samp_xy) == 0:
        return mean, sd, count
    tree = cKDTree(samp_xy)
    nbrs = tree.query_ball_point(cells_xy, r=radius_km * 1000)
    for i, js in enumerate(nbrs):
        if not js:
            continue
        d = np.hypot(*(samp_xy[js] - cells_xy[i]).T)
        w = 1.0 / np.maximum(d, 100.0) ** power
        w /= w.sum()
        mean[i] = (w * samp_mean[js]).sum()
        sd[i] = np.sqrt((w * samp_sd[js] ** 2).sum())
        count[i] = len(js)
    return mean, sd, count


def blend(g_mean, g_sd, c_mean, c_sd, wc=CHEM_WEIGHT):
    has = ~np.isnan(c_mean)
    m = g_mean.copy(); s = g_sd.copy()
    m[has] = (1 - wc) * g_mean[has] + wc * c_mean[has]
    s[has] = np.sqrt(((1 - wc) * g_sd[has]) ** 2 + (wc * c_sd[has]) ** 2)
    return m, s, np.where(has, "geophysics+chemistry", "geophysics only")


def targets(grid: pd.DataFrame, shape, score_col="score", top_pct=TARGET_TOP_PCT,
            min_cells=MIN_TARGET_CELLS) -> tuple[pd.DataFrame, np.ndarray]:
    """Connected groups (8-neighbour) of cells above the top-`top_pct` threshold (computed on non-edge
    cells), excluding edge cells, ranked by peak score then size."""
    from scipy.ndimage import label
    thr = np.nanpercentile(grid.loc[grid["edge_dist_m"] >= EDGE_M, score_col], 100 - top_pct)
    img = np.zeros(shape, bool)
    hi = (grid[score_col] >= thr) & (grid["edge_dist_m"] >= EDGE_M)
    img[grid.row[hi], grid.col[hi]] = True
    lab, _ = label(img, structure=np.ones((3, 3)))
    g = grid.assign(target=lab[grid.row, grid.col])
    g = g[g.target > 0]
    agg = g.groupby("target").agg(
        n_cells=("cell_id", "size"), score_mean=(score_col, "mean"), score_max=(score_col, "max"),
        score_sd_mean=("score_sd", "mean"), x=("x", "mean"), y=("y", "mean"),
        block=("block", "first"))
    agg = agg[agg.n_cells >= min_cells].sort_values(["score_max", "n_cells"], ascending=False)
    agg["rank"] = np.arange(1, len(agg) + 1)
    keep = set(agg.index)
    lab[~np.isin(lab, list(keep))] = 0
    return agg.reset_index(), lab
