#!/usr/bin/env python3
"""08_combine.py: apply the geology mask, blend chemistry where present, rank targets, run held-out tests.

Plain-language note: writes data/processed/prospectivity_cells.parquet (every square),
data/processed/targets_ranked.csv (the ranked target table), target_labels.tif, and combine_stats.json.
"""
import json, pathlib, sys
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from pyproj import Transformer
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from riftprospect import geology as geo, combine as cb, fertility as fe
P = ROOT / "data/processed"
g = pd.read_parquet(P / "geophys_scores.parquet")
with rasterio.open(P / "grid_template.tif") as t: H, W, tr, crs = t.height, t.width, t.transform, t.crs
codes = geo.rasterize_classes(geo.classify(gpd.read_file(ROOT / "data/raw/sgmc/sgmc_MI_WI.geojson")), tr, (H, W))
g["geo_class"] = codes[g.row, g.col]
g["geo_class_label"] = g.geo_class.map({k: v[0] for k, v in geo.CLASSES.items()})
mult = geo.multiplier(g.geo_class.values)
g["geo_masked"] = g.geo_score * mult; g["geo_masked_sd"] = g.geo_sd * mult
# Chemistry (D9 decided): no machine-learning chemistry score on the map. Cu/Pd fertility class of the
# nearest in-survey igneous sample within 5 km is attached as a descriptive label only.
s = pd.read_csv(P / "sample_fertility.csv")
s = s[s.in_survey & s.rock_class.isin(["igneous_intrusive", "igneous_volcanic"]) & s.cu_pd.notna()]
from scipy.spatial import cKDTree
d, j = cKDTree(s[["x", "y"]].values).query(g[["x", "y"]].values, distance_upper_bound=cb.CHEM_RADIUS_KM * 1000)
has = np.isfinite(d)
g["cu_pd_class_nearby"] = np.where(has, s.cu_pd_class.values[np.minimum(j, len(s) - 1)], "no sample within 5 km")
g["evidence"] = np.where(has, "geophysics + Cu/Pd label", "geophysics only")
g["score"], g["score_sd"] = g.geo_masked, g.geo_masked_sd
tg, lab = cb.targets(g, (H, W))
lon, lat = Transformer.from_crs(32616, 4326, always_xy=True).transform(tg.x.values, tg.y.values)
tg["longitude"], tg["latitude"] = np.round(lon, 5), np.round(lat, 5)
tg["area_km2"] = tg.n_cells * 0.04
g["target"] = lab[g.row, g.col]
dom = g[g.target > 0].groupby("target").agg(geo_class=("geo_class_label", lambda v: v.value_counts().index[0]),
                                             cu_pd_label=("cu_pd_class_nearby", lambda v: v.value_counts().index[0]))
tg = tg.merge(dom, left_on="target", right_index=True, how="left")
dep = pd.read_csv(P / "ni_cu_pge_deposits.csv")
tg["km_to_known_ni_cu_pge"] = np.round(np.min(np.hypot(tg.x.values[:, None] - dep.x.values[None], tg.y.values[:, None] - dep.y.values[None]), 1) / 1000, 1)
tg["target_id"] = [f"MCR-T{r:04d}" for r in tg["rank"]]
cols = ["target_id", "rank", "latitude", "longitude", "area_km2", "score_mean", "score_max", "score_sd_mean",
        "block", "geo_class", "cu_pd_label", "km_to_known_ni_cu_pge"]
tg[cols].round(4).to_csv(P / "targets_ranked.csv", index=False)
g.drop(columns=["target"]).to_parquet(P / "prospectivity_cells.parquet", index=False)
with rasterio.open(P / "target_labels.tif", "w", driver="GTiff", height=H, width=W, count=1, dtype="int32", crs=crs, transform=tr) as o:
    o.write(lab.astype("int32"), 1)
# Held-out Eagle test on the final score
e = dep[dep.Deposit_na == "Eagle mine"].iloc[0]
dd = np.hypot(g.x - e.x, g.y - e.y); best = g.loc[dd <= 1000, "score"].max()
eagle_t = int(g.loc[dd <= 1000, "target"].max())
st = {"n_cells": len(g), "geo_class_cells": g.geo_class_label.value_counts().to_dict(),
      "multipliers": {v[0]: v[1] for v in geo.CLASSES.values()},
      "target_top_pct": cb.TARGET_TOP_PCT, "min_target_cells": cb.MIN_TARGET_CELLS, "n_targets": len(tg),
      "target_area_km2": round(float(tg.area_km2.sum()), 1),
      "target_area_pct": round(float(tg.area_km2.sum() / (len(g) * 0.04) * 100), 2),
      "eagle_score_percentile": round(float((g.score < best).mean() * 100), 2),
      "eagle_area_to_capture_pct": round(float((g.score >= best).mean() * 100), 2),
      "eagle_in_target": eagle_t > 0, "eagle_edge_dist_m": float(g.loc[dd.idxmin(), "edge_dist_m"]),
      "edge_excluded_cells": int((g.edge_dist_m < cb.EDGE_M).sum()),
      "eagle_target_rank": int(tg.loc[tg.target == eagle_t, "rank"].iloc[0]) if eagle_t > 0 and (tg.target == eagle_t).any() else None,
      "eagle_geo_class": g.loc[dd.idxmin(), "geo_class_label"],
      "cells_with_cu_pd_label": int(has.sum()),
      "targets_by_geo_class": tg.geo_class.value_counts().to_dict()}
json.dump(st, open(P / "combine_stats.json", "w"), indent=1)
print(json.dumps(st, indent=1)); print(tg[cols].head(12).to_string())
