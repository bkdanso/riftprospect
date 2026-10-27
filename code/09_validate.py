#!/usr/bin/env python3
"""09_validate.py: the validation study numbers, all written to paper/stats.json.

Plain-language note: gathers every number the paper, README and map quote, and runs the
validation tests: (1) the chemistry model under spatial cross-validation, with the exploratory
feature-set table; (2) Cu/Pd near versus far from known deposits; (3) the held-out Eagle test,
including how sensitive it is to the weights, the geology mask and the minimum target size.
"""
import json, pathlib, sys
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from riftprospect import chemmodel as cm, geophys as gp, geology as geo, combine as cb
P = ROOT / "data/processed"; out = {}
for k in ["grid_stats", "fertility_stats", "chem_model_stats", "geophys_stats", "combine_stats"]:
    out[k] = json.load(open(P / f"{k}.json"))

# (1) exploratory chemistry feature sets (pre-declared list; reported in full, none adopted)
f = pd.read_csv(P / "sample_fertility.csv")
dep = pd.read_csv(P / "ni_cu_pge_deposits.csv")
f["dep_km"], f["dep_name"] = cm.nearest_deposit(f[["x", "y"]].values, dep[["x", "y"]].values, dep.Deposit_na)
w = pd.read_csv(ROOT / "data/raw/mcr_geochem/mcr_geochem_wide.csv", low_memory=False)[["mcr_uid", "S_wt", "Cr_ppm", "Co_ppm"]]
f = f.merge(w, on="mcr_uid")
for c in ["S_wt", "Cr_ppm", "Co_ppm"]: f[c] = f[c].where(f[c] > 0)
f["log_cu"], f["log_ni"], f["log_s"] = np.log10(f.Cu_ppm), np.log10(f.Ni_ppm), np.log10(f.S_wt)
sets = {"main: Ni/Cu, MgO, Mg#": ["log_ni_cu", "MgO_wt", "mg_number"], "Cu, Ni, MgO": ["log_cu", "log_ni", "MgO_wt"],
        "Cu, Ni, MgO, Mg#, Cr, Co": ["log_cu", "log_ni", "MgO_wt", "mg_number", "Cr_ppm", "Co_ppm"],
        "Cu/Pd, Ni/Cu, MgO": ["log_cu_pd", "log_ni_cu", "MgO_wt"], "Cu, Ni, S": ["log_cu", "log_ni", "log_s"]}
rows = []
for name, feats in sets.items():
    cm.FEATURES = feats
    t = cm.training_table(f); t = t[t.state.eq("MN")]
    r = cm.spatial_cv_auc(t); r.update(feature_set=name, n_neg=int(r["n"] - r["n_pos"])); rows.append(r)
cm.FEATURES = ["log_ni_cu", "MgO_wt", "mg_number"]
out["chem_feature_sets"] = rows
# Sensitivity of the main chemistry model to the near radius (D2)
sens = {}
near0 = cm.NEAR_KM
for r_km in (2.0, 3.0, 5.0):
    cm.NEAR_KM = r_km
    t = cm.training_table(f); t = t[t.state.eq("MN")]
    sens[f"{r_km:g}km"] = round(cm.spatial_cv_auc(t)["auc"], 3)
cm.NEAR_KM = near0
out["chem_auc_by_near_km"] = sens
# (2) Cu/Pd near vs far (igneous, all states)
ig = f[f.rock_class.isin(["igneous_intrusive", "igneous_volcanic"]) & f.cu_pd.notna()]
a, b = ig[ig.dep_km <= cm.NEAR_KM].cu_pd, ig[ig.dep_km > 10].cu_pd
u = mannwhitneyu(a, b, alternative="two-sided")
out["cu_pd_near_far"] = {"near_km": cm.NEAR_KM, "n_near": len(a), "n_far": len(b), "median_near": float(a.median()), "median_far": float(b.median()),
                         "mannwhitney_p": float(u.pvalue)}
# (3) Eagle sensitivity
g = pd.read_parquet(P / "prospectivity_cells.parquet")
e = dep[dep.Deposit_na == "Eagle mine"].iloc[0]
near = np.hypot(g.x - e.x, g.y - e.y) <= 1000
pct = gp.evidence(g.rename(columns={}).assign(**{c: pd.read_parquet(P / "grid_features.parquet")[c].values for c in gp.LAYERS}))
rng = np.random.default_rng(1); base = np.array([gp.WEIGHTS[c] for c in gp.LAYERS]); ep = []
for i in range(200):
    wts = dict(zip(gp.LAYERS, rng.dirichlet(base * 20))); s = gp.score(pct, wts, mid=rng.uniform(65, 85))
    ep.append(float((s < s[near.values].max()).mean() * 100))
eq = gp.score(pct, {c: 0.25 for c in gp.LAYERS})
mag_only = gp.score(pct, {"rtp_asig": 0.5, "rtp_resid": 0.5, "k": 0.0, "th": 0.0})
rad_only = gp.score(pct, {"rtp_asig": 0.0, "rtp_resid": 0.0, "k": 0.5, "th": 0.5})
pr = lambda s: round(float((s < s[near.values].max()).mean() * 100), 2)
out["eagle_sensitivity"] = {
    "percentile_mc_median": round(float(np.median(ep)), 2), "percentile_mc_p05": round(float(np.percentile(ep, 5)), 2),
    "percentile_mc_p95": round(float(np.percentile(ep, 95)), 2),
    "equal_weights": pr(eq), "magnetics_only": pr(mag_only), "radiometrics_only": pr(rad_only),
    "unmasked_geophys": pr(g.geo_score.values), "masked_final": pr(g.score.values),
    "random_expectation_pct_area_at_or_above": round(100 - pr(g.score.values), 2)}
t3, _ = cb.targets(g, (out["grid_stats"]["grid_shape"][0], out["grid_stats"]["grid_shape"][1]), min_cells=3)
out["eagle_sensitivity"]["n_targets_min3"] = len(t3)
tg = pd.read_csv(P / "targets_ranked.csv")
out["targets"] = {"n": len(tg), "area_km2_total": round(float(tg.area_km2.sum()), 1),
                  "median_area_km2": float(tg.area_km2.median()), "single_cell": int((tg.area_km2 <= 0.04).sum()),
                  "by_block": tg.block.value_counts().to_dict(), "by_geo_class": tg.geo_class.value_counts().to_dict(),
                  "with_cu_pd_label": int((tg.cu_pd_label != "no sample within 5 km").sum()),
                  "top10": tg.head(10)[["target_id", "latitude", "longitude", "area_km2", "score_max", "geo_class"]].to_dict("records")}
(ROOT / "paper").mkdir(exist_ok=True)
json.dump(out, open(ROOT / "paper/stats.json", "w"), indent=1, default=float)
print(json.dumps({k: out[k] for k in ["chem_feature_sets", "cu_pd_near_far", "eagle_sensitivity"]}, indent=1, default=float))
