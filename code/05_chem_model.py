#!/usr/bin/env python3
"""05_chem_model.py: Part A, train the chemistry similarity model in Minnesota and apply it everywhere.

Plain-language note: writes data/processed/sample_scores.csv (each sample's chemistry
similarity score and its spread) and data/processed/chem_model_stats.json (validation numbers).
"""
import json, pathlib, sys
import numpy as np, pandas as pd
from pyproj import Transformer
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from riftprospect import chemmodel as cm
P = ROOT / "data/processed"

f = pd.read_csv(P / "sample_fertility.csv")
dep = pd.read_excel(ROOT / "data/raw/cmd_v3/critical_mineral_deposits_all_tables_v3.xlsx.xlsx", sheet_name="2026_CM_deposits")
dep = dep[dep.DepType.eq("Nickel-copper-PGE sulfide") & dep.State.isin(["MN", "MI", "WI"])].reset_index(drop=True)
dx, dy = Transformer.from_crs(4326, 32616, always_xy=True).transform(dep.Long_WGS84.values, dep.Lat_WGS84.values)
dep[["x", "y"]] = np.c_[dx, dy]
dep.to_csv(P / "ni_cu_pge_deposits.csv", index=False)
f["dep_km"], f["dep_name"] = cm.nearest_deposit(f[["x", "y"]].values, dep[["x", "y"]].values, dep.Deposit_na)
# Eagle is a held-out test: it must never contribute a training positive.
assert not ((f.dep_name == "Eagle mine") & (f.dep_km <= cm.NEAR_KM)).any(), "Eagle-area sample would leak"
train = cm.training_table(f)
train = train[train.state.eq("MN")]  # training region: Minnesota only
cv = cm.spatial_cv_auc(train)
lodo = cm.leave_one_deposit_out(train)
apply = cm.add_features(f)
apply = apply[apply.rock_class.isin(["igneous_intrusive", "igneous_volcanic"])].dropna(subset=cm.FEATURES)
mean, sd, coefs = cm.bootstrap_predict(train, apply)
apply["chem_score"], apply["chem_sd"] = mean, sd
apply["in_domain"] = apply.rock_class.isin(cm.ROCK_CLASSES) & ~apply.altered_likely.fillna(False).astype(bool)
cols = ["mcr_uid", "state", "rock_class", "x", "y", "latitude", "longitude", "in_survey", "in_domain",
        "dep_km", "dep_name", "log_ni_cu", "MgO_wt", "mg_number", "cu_pd", "cu_pd_class", "chem_score", "chem_sd"]
apply[cols].to_csv(P / "sample_scores.csv", index=False)
# Part of the validation study: do Cu/Pd classes differ by distance to deposit? (all states, igneous)
ig = f[f.rock_class.isin(["igneous_intrusive", "igneous_volcanic"]) & f.cu_pd.notna()]
st = {"training_region": "MN", "n_train": len(train), "n_pos": int(train.label.sum()),
      "n_neg": int((train.label == 0).sum()), "pos_deposits": train.loc[train.label == 1, "dep_name"].value_counts().to_dict(),
      "features": cm.FEATURES, "near_km": cm.NEAR_KM, "far_km": cm.FAR_KM, "spatial_cv": cv,
      "lodo": lodo.to_dict("records"),
      "coef_mean_std_units": dict(zip(cm.FEATURES, np.round(coefs.mean(0), 3).tolist())),
      "coef_sd": dict(zip(cm.FEATURES, np.round(coefs.std(0), 3).tolist())),
      "n_applied": len(apply), "n_applied_in_survey": int(apply.in_survey.sum()),
      "n_applied_in_survey_in_domain": int((apply.in_survey & apply.in_domain).sum()),
      "cu_pd_median_near": float(ig[ig.dep_km <= cm.NEAR_KM].cu_pd.median()),
      "cu_pd_median_far_10km": float(ig[ig.dep_km > 10].cu_pd.median()),
      "n_cu_pd_near": int((ig.dep_km <= cm.NEAR_KM).sum()), "n_cu_pd_far": int((ig.dep_km > 10).sum())}
json.dump(st, open(P / "chem_model_stats.json", "w"), indent=1)
print(json.dumps(st, indent=1))
