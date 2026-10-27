#!/usr/bin/env python3
"""07_fig_geophys.py: Figure 2 (geophysics score and its spread) and Figure 3 (final score with targets).

Plain-language note: draws paper/figures/fig2_geophys_score.png and fig3_prospectivity.png.
Run after 08_combine.py for Figure 3. Pass --final to remove the DRAFT tag.
"""
import pathlib, sys
import numpy as np, pandas as pd, rasterio, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT = pathlib.Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; FIG = ROOT / "paper/figures"
FINAL = "--final" in sys.argv
with rasterio.open(P / "grid_template.tif") as t: H, W, tr = t.height, t.width, t.transform
EXT = [tr.c, tr.c + W * tr.a, tr.f + H * tr.e, tr.f]
dep = pd.read_csv(P / "ni_cu_pge_deposits.csv"); EAGLE = dep[dep.Deposit_na == "Eagle mine"]
SRC = "Source: USGS 2025 airborne survey (doi:10.5066/P14ESDF7), 200 m cells, UTM zone 16N."


def raster(df, col):
    img = np.full((H, W), np.nan); img[df.row, df.col] = df[col]; return img


def axes_style(ax, title):
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect("equal")
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.set_xticks(ax.get_xticks()[::2]); ax.tick_params(labelsize=7)
    ax.set_xlabel("Easting, m", fontsize=8); ax.set_ylabel("Northing, m", fontsize=8)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3])
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_title(title, loc="left", fontsize=9)


def eagle(ax, color="white"):
    ax.scatter(EAGLE.x, EAGLE.y, marker="*", s=220, facecolor="none", edgecolor=color, lw=1.3, zorder=5)


def stamp(fig):
    if not FINAL:
        fig.text(0.5, 0.5, "DRAFT", fontsize=70, color="#999", alpha=0.25, ha="center", va="center", rotation=15)


def legend(ax, extra=()):
    h = [Line2D([], [], marker="*", ls="", ms=12, mfc="none", mec="#222", label="Eagle mine (held out, never used for fitting)")]
    ax.legend(handles=h + list(extra), loc="lower left", fontsize=7, framealpha=0.9)


def fig2():
    g = pd.read_parquet(P / "geophys_scores.parquet")
    fig, axs = plt.subplots(2, 1, figsize=(10, 9.5), dpi=200, constrained_layout=True)
    for ax, col, title, lab, cmap in [
            (axs[0], "geo_score", "A. Geophysics score: how much each square looks like a small mafic-ultramafic intrusion",
             "Score, 0 (unlike) to 1 (like)", "viridis"),
            (axs[1], "geo_sd", "B. Uncertainty: spread of the score across 100 random weightings",
             "Standard deviation of score", "magma")]:
        im = ax.imshow(raster(g, col), extent=EXT, cmap=cmap, interpolation="nearest")
        eagle(ax); axes_style(ax, title); legend(ax)
        cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.01); cb.set_label(lab, fontsize=8); cb.ax.tick_params(labelsize=7)
    fig.text(0.0, -0.01, "Score = weighted mean of analytic signal, residual magnetic field, low K and low eTh memberships "
             "(weights 0.35/0.35/0.15/0.15, decision D6). " + SRC, fontsize=6, color="#555")
    stamp(fig); fig.savefig(FIG / "fig2_geophys_score.png", bbox_inches="tight")


def fig3():
    g = pd.read_parquet(P / "prospectivity_cells.parquet")
    tg = pd.read_csv(P / "targets_ranked.csv")
    with rasterio.open(P / "target_labels.tif") as t: lab = t.read(1)
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200, constrained_layout=True)
    im = ax.imshow(raster(g, "score"), extent=EXT, cmap="viridis", interpolation="nearest")
    ys, xs = np.where(lab > 0)
    ax.scatter(EXT[0] + (xs + 0.5) * tr.a, EXT[3] + (ys + 0.5) * tr.e, s=0.6, c="#ff4d6d", lw=0, zorder=4)
    top = tg.nsmallest(10, "rank")
    from pyproj import Transformer
    tx, ty = Transformer.from_crs(4326, 32616, always_xy=True).transform(top.longitude.values, top.latitude.values)
    for x, y, r in zip(tx, ty, top["rank"]):
        ax.annotate(str(r), (x, y), xytext=(4, 4), textcoords="offset points", fontsize=6, color="white",
                    bbox=dict(boxstyle="round,pad=0.1", fc="#222", ec="none", alpha=0.7))
    eagle(ax); axes_style(ax, "Final prospectivity score after the geology mask, with target cells (top 2%) and the ten highest-ranked targets")
    legend(ax, [Line2D([], [], marker="s", ls="", ms=5, mfc="#ff4d6d", mec="none", label=f"Target cell (top 2%, {len(tg):,} targets)")])
    cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.01); cb.set_label("Score after geology mask (0 to 1)", fontsize=8); cb.ax.tick_params(labelsize=7)
    fig.text(0.0, -0.02, "Geology mask (D11): iron formation +500 m x0.3, Mesoproterozoic volcanic x0.6 (USGS SGMC, doi:10.3133/ds1052). " + SRC,
             fontsize=6, color="#555")
    stamp(fig); fig.savefig(FIG / "fig3_prospectivity.png", bbox_inches="tight")


if __name__ == "__main__":
    fig2()
    if (P / "prospectivity_cells.parquet").exists():
        fig3()
