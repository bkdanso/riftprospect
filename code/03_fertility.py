#!/usr/bin/env python3
"""03_fertility.py: fertility indicators per MCR-GeoChem sample, tagged by survey coverage.

Plain-language note: writes data/processed/sample_fertility.csv (one row per rock sample with
Cu/Pd, Ni/Cu, MgO, Mg-number) and prints counts. Provisional choices: docs/DECISIONS.md.
"""
import json, pathlib, sys
import numpy as np, pandas as pd, rasterio
from pyproj import Transformer
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from riftprospect.fertility import indicators, cu_pd_class

RAW = ROOT / "data/raw/mcr_geochem"; OUT = ROOT / "data/processed"
w = pd.read_csv(RAW / "mcr_geochem_wide.csv", low_memory=False)
w = w[w.sample_type.eq("whole_rock") & w.latitude.notna()].copy()
ind = indicators(w)
meta = w[["mcr_uid", "latitude", "longitude", "coord_quality", "state", "rock_class", "rock_name",
          "mcr_class", "altered_likely", "qa_flags"]]
f = meta.merge(ind, on="mcr_uid")
f["cu_pd_class"] = cu_pd_class(f.cu_pd)
x, y = Transformer.from_crs(4326, 32616, always_xy=True).transform(f.longitude.values, f.latitude.values)
f["x"], f["y"] = x, y
with rasterio.open(OUT / "grid_template.tif") as t:
    r, c = rasterio.transform.rowcol(t.transform, x, y)
    r, c = np.array(r), np.array(c)
    ok = (r >= 0) & (r < t.height) & (c >= 0) & (c < t.width)
    m = t.read(1)
    inside = np.zeros(len(f), bool); inside[ok] = m[r[ok], c[ok]] == 1
f["in_survey"] = inside
f.to_csv(OUT / "sample_fertility.csv", index=False)
s = f[f.in_survey]
st = {"n_whole_rock": len(f), "n_in_survey": int(inside.sum()),
      "in_survey_by_state": s.state.value_counts().to_dict(),
      "in_survey_by_rock_class": s.rock_class.value_counts().to_dict(),
      "n_cu_pd_all": int(f.cu_pd.notna().sum()), "n_cu_pd_in_survey": int(s.cu_pd.notna().sum()),
      "n_ni_cu_in_survey": int(s.ni_cu.notna().sum()), "n_mgo_in_survey": int(s.MgO_wt.notna().sum()),
      "n_mgnum_in_survey": int(s.mg_number.notna().sum()),
      "cu_pd_class_in_survey": s.cu_pd_class.value_counts().to_dict(),
      "cu_pd_class_all": f.cu_pd_class.value_counts().to_dict(),
      "mg_number_range_in_survey": [round(float(s.mg_number.min()), 1), round(float(s.mg_number.max()), 1)]}
json.dump(st, open(OUT / "fertility_stats.json", "w"), indent=1)
print(json.dumps(st, indent=1))
