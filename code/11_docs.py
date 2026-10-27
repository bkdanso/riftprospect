#!/usr/bin/env python3
"""11_docs.py: write README.md and docs/TALK_TRACK.md from templates, filling every number from paper/stats.json.

Plain-language note: this is why the numbers in the README can never disagree with the data.
Pass --final to change the status line from DRAFT to Released.
"""
import datetime, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from riftprospect import __version__
s = json.load(open(ROOT / "paper/stats.json"))
es, cs = s["eagle_sensitivity"], s["combine_stats"]
v = dict(status="Released" if "--final" in sys.argv else "DRAFT (not yet verified by the author)",
         version=__version__, date=datetime.date.today().isoformat(),
         area_km2=s["grid_stats"]["area_km2"], n_cells=s["grid_stats"]["n_cells"],
         eagle_pct=cs["eagle_score_percentile"], eagle_area=cs["eagle_area_to_capture_pct"],
         eagle_p05=es["percentile_mc_p05"], eagle_p95=es["percentile_mc_p95"],
         eagle_mag=es["magnetics_only"], eagle_rad=es["radiometrics_only"],
         chem_auc=s["chem_model_stats"]["spatial_cv"]["auc"],
         cupd_near=s["cu_pd_near_far"]["median_near"], cupd_far=s["cu_pd_near_far"]["median_far"],
         n_near=s["cu_pd_near_far"]["n_near"], near_km=s["cu_pd_near_far"]["near_km"], auc_2km=s["chem_auc_by_near_km"]["2km"], auc_5km=s["chem_auc_by_near_km"]["5km"], auc_min=min(s["chem_auc_by_near_km"].values()), auc_max=max(s["chem_auc_by_near_km"].values()), n_far=s["cu_pd_near_far"]["n_far"],
         n_targets=s["targets"]["n"], target_area=s["targets"]["area_km2_total"],
         eagle_rank=cs["eagle_target_rank"], n_targets_min3=es["n_targets_min3"])
for tmpl, out in [("README.md.tmpl", "README.md"), ("TALK_TRACK.md.tmpl", "docs/TALK_TRACK.md")]:
    p = ROOT / "code/templates" / tmpl
    if p.exists():
        (ROOT / out).write_text(p.read_text().format(**v))
        print("wrote", out)
