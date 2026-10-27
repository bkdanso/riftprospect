#!/usr/bin/env python3
"""06_geophys.py: Part B, rule-based geophysical score on every 200 m cell, with Monte Carlo spread,
and the held-out Eagle test.

Plain-language note: writes data/processed/geophys_scores.parquet and geophys_stats.json.
Weights were fixed in src/riftprospect/geophys.py BEFORE this test was run; Eagle is not used
to tune anything. (Disclosure: the Eagle cell's raw percentiles were looked at once during
the checkpoint 2 sanity check; weights were then set from the literature rationale only.)
"""
import json, pathlib, sys
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from riftprospect import geophys as gp
P = ROOT / "data/processed"
g = pd.read_parquet(P / "grid_features.parquet")
pct = gp.evidence(g)
g["geo_score"], g["geo_sd"] = gp.monte_carlo(pct)
g["geo_score_fixed"] = gp.score(pct)
for c in gp.LAYERS: g[f"pct_{c}"] = pct[c].astype("float32")
g[["cell_id", "row", "col", "x", "y", "block", "edge_dist_m", "geo_score", "geo_sd", "geo_score_fixed"] + [f"pct_{c}" for c in gp.LAYERS]].to_parquet(P / "geophys_scores.parquet", index=False)
dep = pd.read_csv(P / "ni_cu_pge_deposits.csv")
e = dep[dep.Deposit_na == "Eagle mine"].iloc[0]
d = np.hypot(g.x - e.x, g.y - e.y)
i = d.idxmin()
near = d <= 1000  # Eagle footprint: best cell within 1 km (deposit coordinates are a point)
rank_pct = lambda v: float((g.geo_score < v).mean() * 100)
# Area needed to capture Eagle: share of the survey with a score >= Eagle's best cell within 1 km
best = g.loc[near, "geo_score"].max()
st = {"n_cells": len(g), "weights": gp.WEIGHTS, "midpoint_pct": gp.MIDPOINT_PCT,
      "eagle_cell": g.loc[i, "cell_id"], "eagle_cell_dist_m": float(d.min()),
      "eagle_cell_score": float(g.loc[i, "geo_score"]), "eagle_cell_percentile": rank_pct(g.loc[i, "geo_score"]),
      "eagle_best_1km_percentile": rank_pct(best),
      "eagle_area_to_capture_pct": float((g.geo_score >= best).mean() * 100),
      "eagle_layer_percentiles": {c: float(pct.loc[i, c]) for c in gp.LAYERS},
      "geo_sd_median": float(g.geo_sd.median())}
json.dump(st, open(P / "geophys_stats.json", "w"), indent=1)
print(json.dumps(st, indent=1))
