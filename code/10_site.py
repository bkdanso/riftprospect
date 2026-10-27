#!/usr/bin/env python3
"""10_site.py: build the public interactive map in site/ (served by GitHub Pages).

Plain-language note: makes picture overlays of the score and its uncertainty, and small
data files of targets, deposits and samples, then writes site/index.html. Pass --final to
remove the DRAFT banner. Numbers shown on the page come from paper/stats.json.
"""
import json, pathlib, sys
import numpy as np, pandas as pd, rasterio, matplotlib
from rasterio.warp import reproject, calculate_default_transform, Resampling
from pyproj import Transformer
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; S = ROOT / "site"
(S / "data").mkdir(parents=True, exist_ok=True); (S / "img").mkdir(exist_ok=True)
FINAL = "--final" in sys.argv
st = json.load(open(ROOT / "paper/stats.json"))
g = pd.read_parquet(P / "prospectivity_cells.parquet")
with rasterio.open(P / "grid_template.tif") as t: H, W, tr, crs = t.height, t.width, t.transform, t.crs
dst_crs = "EPSG:3857"
left, bottom, right, top = rasterio.transform.array_bounds(H, W, tr)
dtr, dw, dh = calculate_default_transform(crs, dst_crs, W, H, left, bottom, right, top)
to_ll = Transformer.from_crs(dst_crs, 4326, always_xy=True)
b_ll = [to_ll.transform(dtr.c, dtr.f + dh * dtr.e)[::-1], to_ll.transform(dtr.c + dw * dtr.a, dtr.f)[::-1]]


def overlay(col, cmap, name, vmin=None, vmax=None):
    img = np.full((H, W), np.nan, "float32"); img[g.row, g.col] = g[col]
    out = np.full((dh, dw), np.nan, "float32")
    reproject(img, out, src_transform=tr, src_crs=crs, dst_transform=dtr, dst_crs=dst_crs,
              src_nodata=np.nan, dst_nodata=np.nan, resampling=Resampling.nearest)
    vmin = np.nanmin(out) if vmin is None else vmin; vmax = np.nanmax(out) if vmax is None else vmax
    rgba = plt.get_cmap(cmap)((out - vmin) / (vmax - vmin)); rgba[np.isnan(out), 3] = 0
    plt.imsave(S / "img" / f"{name}.png", rgba)
    return [float(vmin), float(vmax)]


rng_score = overlay("score", "viridis", "score", 0, 1)
rng_sd = overlay("score_sd", "magma", "uncertainty", 0)
tg = pd.read_csv(P / "targets_ranked.csv")
feat = lambda lon, lat, props: {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}
tfeat = []
for r in tg.to_dict("records"):
    tfeat.append(feat(r["longitude"], r["latitude"], {k: (None if pd.isna(v) else v) for k, v in r.items()}))
json.dump({"type": "FeatureCollection", "features": tfeat}, open(S / "data/targets.geojson", "w"))
dep = pd.read_excel(ROOT / "data/raw/cmd_v3/critical_mineral_deposits_all_tables_v3.xlsx.xlsx", sheet_name="2026_CM_deposits")
dep = dep[dep.State.isin(["MI", "WI", "MN"])]
json.dump({"type": "FeatureCollection", "features": [feat(r.Long_WGS84, r.Lat_WGS84, {"name": r.Deposit_na, "type": r.DepType, "minerals": r.CritMin, "state": r.State}) for r in dep.itertuples()]},
          open(S / "data/deposits.geojson", "w"))
sm = pd.read_csv(P / "sample_fertility.csv"); sm = sm[sm.cu_pd.notna() & sm.state.isin(["MI", "WI"]) & sm.rock_class.isin(["igneous_intrusive", "igneous_volcanic"])]
json.dump({"type": "FeatureCollection", "features": [feat(round(r.longitude, 5), round(r.latitude, 5), {"id": r.mcr_uid, "rock": r.rock_class, "cu_pd": round(r.cu_pd), "class": r.cu_pd_class}) for r in sm.itertuples()]},
          open(S / "data/samples_cupd.geojson", "w"))
cfg = {"bounds": b_ll, "draft": not FINAL, "n_targets": len(tg), "eagle_pct": st["combine_stats"]["eagle_score_percentile"],
       "eagle_rank": st["combine_stats"]["eagle_target_rank"], "area_km2": st["grid_stats"]["area_km2"]}
html = (ROOT / "code/site_template.html").read_text().replace("/*CONFIG*/", "const CFG = " + json.dumps(cfg) + ";")
if FINAL:  # drop the draft banner element entirely
    import re
    html = re.sub(r'<div class="draft" id="draft">.*?</div>\n', "", html)
    html = html.replace("if(!CFG.draft) document.getElementById('draft').remove();\n", "")
(S / "index.html").write_text(html)
print("site built", cfg)
