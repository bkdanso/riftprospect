#!/usr/bin/env python3
"""04_fig_overview.py: Figure 1, the survey area with magnetic field, samples, and deposits.

Plain-language note: draws paper/figures/fig1_overview.png. Pass --final to remove the DRAFT tag.
"""
import pathlib, sys
import numpy as np, pandas as pd, rasterio, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pyproj import Transformer
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"
FINAL = "--final" in sys.argv
g = pd.read_parquet(P / "grid_features.parquet")
with rasterio.open(P / "grid_template.tif") as t: H, W, tr = t.height, t.width, t.transform
img = np.full((H, W), np.nan); img[g.row, g.col] = g.rtp
f = pd.read_csv(P / "sample_fertility.csv"); f = f[f.in_survey]
cmd = pd.read_excel(ROOT / "data/raw/cmd_v3/critical_mineral_deposits_all_tables_v3.xlsx.xlsx", sheet_name="2026_CM_deposits")
cmd = cmd[cmd.State.isin(["MI", "WI"])]
cx, cy = Transformer.from_crs(4326, 32616, always_xy=True).transform(cmd.Long_WGS84.values, cmd.Lat_WGS84.values)
ext = [tr.c, tr.c + W * tr.a, tr.f + H * tr.e, tr.f]
lim = np.nanpercentile(np.abs(img), 98)
fig, ax = plt.subplots(figsize=(11, 5.2), dpi=200)
im = ax.imshow(img, extent=ext, cmap="RdBu_r", vmin=-lim, vmax=lim, interpolation="nearest")
ax.scatter(f.x, f.y, s=6, c="#3a3a3a", lw=0, label=f"MCR-GeoChem sample (n = {len(f):,})")
fc = f[f.cu_pd.notna()]
ax.scatter(fc.x, fc.y, s=16, facecolor="none", edgecolor="#111111", lw=0.8, label=f"  with Cu/Pd (n = {len(fc):,})")
ni = cmd.DepType.eq("Nickel-copper-PGE sulfide")
inb = (cx > ext[0]) & (cx < ext[1]) & (cy > ext[2]) & (cy < ext[3])
ax.scatter(cx[inb & ~ni], cy[inb & ~ni], marker="^", s=30, facecolor="white", edgecolor="#111", lw=0.8, label="Other CMD v3 deposit")
ax.scatter(cx[inb & ni], cy[inb & ni], marker="*", s=260, facecolor="#f2c200", edgecolor="#111", lw=0.9, label="CMD v3 Ni-Cu-PGE deposit (Eagle mine)")
ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal")
ax.ticklabel_format(style="plain", useOffset=False); ax.set_xlabel("Easting, m (UTM zone 16N)"); ax.set_ylabel("Northing, m (UTM zone 16N)")
for s in ["top", "right"]: ax.spines[s].set_visible(False)
cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.01); cb.set_label("Reduced-to-pole magnetic anomaly, nT")
ax.legend(loc="lower left", fontsize=7, frameon=True, framealpha=0.9)
ax.set_title("Survey area, magnetic field, rock samples and known deposits", loc="left", fontsize=10)
fig.text(0.01, 0.005, "Sources: USGS airborne survey 2025 (doi:10.5066/P14ESDF7), 200 m cells; MCR-GeoChem v1.0.1; "
         "USGS Critical Mineral Deposits v3.0 (doi:10.5066/P9K1HBNT).", fontsize=6, color="#555")
if not FINAL:
    fig.text(0.5, 0.5, "DRAFT", fontsize=70, color="#999", alpha=0.25, ha="center", va="center", rotation=20)
(ROOT / "paper/figures").mkdir(parents=True, exist_ok=True)
fig.savefig(ROOT / "paper/figures/fig1_overview.png", bbox_inches="tight")
