#!/usr/bin/env python3
"""02_grid.py: put the airborne grids on one 200 m grid and derive magnetic features.

Plain-language note: writes data/processed/grid_features.parquet, one row per 200 m square
inside the survey, with magnetism and radioactivity values. You do not need to open it.
"""
import json, pathlib, sys
import numpy as np, pandas as pd, rasterio
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from riftprospect.grid import common_transform, mosaic_average, analytic_signal, local_std, local_mean

CELL = 200.0
RAW = ROOT / "data/raw/earthmri_up"; OUT = ROOT / "data/processed"; OUT.mkdir(parents=True, exist_ok=True)
LAYERS = {"rtp": "_RTP_", "fvd": "_FVD_", "k": "_K_", "th": "_Th_", "u": "_U_"}

def files(key):
    return sorted(p for p in RAW.glob("*.tif") if key in p.name)  # BlockA before BlockB

bounds = []
for p in RAW.glob("*.tif"):
    with rasterio.open(p) as r:
        bounds.append(tuple(r.bounds)); crs = r.crs
tr, h, w = common_transform(bounds, CELL)
grids = {k: mosaic_average(files(v), tr, (h, w), crs) for k, v in LAYERS.items()}
block = np.full((h, w), "", dtype=object)
for b in "AB":
    g = mosaic_average([RAW / f"Block{b}_RTP_AirborneMagRadUP.tif"], tr, (h, w), crs)
    block[~np.isnan(g)] = b
grids["rtp_asig"] = analytic_signal(grids["rtp"], CELL)
grids["rtp_std2km"] = local_std(grids["rtp"], 5)
grids["rtp_resid"] = grids["rtp"] - local_mean(grids["rtp"], 5)  # RTP minus its 2.2 km x 2.2 km mean
valid = ~np.isnan(grids["rtp"])
rows, cols = np.where(valid)
xs = tr.c + (cols + 0.5) * CELL; ys = tr.f - (rows + 0.5) * CELL
df = pd.DataFrame({"row": rows, "col": cols, "x": xs, "y": ys, "block": block[valid]})
for k, g in grids.items():
    df[k] = g[valid]
df["th_k"] = df.th / df.k.where(df.k > 0)
from scipy.ndimage import distance_transform_edt
# Distance from each cell to the nearest no-data cell. Derivative filters are unreliable near
# survey edges and internal gaps, so cells closer than EDGE_M are excluded from targets (QA rule).
df["edge_dist_m"] = (distance_transform_edt(valid) * CELL)[valid].astype("float32")
df["cell_id"] = [f"C{r:04d}_{c:04d}" for r, c in zip(rows, cols)]
df.to_parquet(OUT / "grid_features.parquet", index=False)
with rasterio.open(OUT / "grid_template.tif", "w", driver="GTiff", height=h, width=w, count=1,
                   dtype="uint8", crs=crs, transform=tr) as dst:
    dst.write(valid.astype("uint8"), 1)
st = {"cell_m": CELL, "crs": str(crs), "grid_shape": [h, w], "n_cells": int(valid.sum()),
      "area_km2": round(valid.sum() * CELL * CELL / 1e6, 1),
      "cells_by_block": df.block.value_counts().to_dict(),
      "missing_by_layer": {k: int(df[k].isna().sum()) for k in grids}}
json.dump(st, open(OUT / "grid_stats.json", "w"), indent=1)
print(json.dumps(st, indent=1))
