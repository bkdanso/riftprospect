"""Geochemical fertility indicators for magmatic Ni-Cu-PGE sulfide systems.

Plain-language note: this file computes the chemistry ratios you named (Cu/Pd,
Ni/Cu, MgO, Mg-number) for each rock sample, and records whether each value is a
real measurement or rests on a "below detection" value. The provisional choices
(marked DECISION) are listed in docs/DECISIONS.md for you to rule on.

Conventions follow MCR-GeoChem's wide table: Pd and Pt in ppb, Cu and Ni in ppm,
oxides in wt%, and a negative number means "below detection, limit = |value|".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MW = {"MgO": 40.304, "FeO": 71.844, "Fe2O3": 159.688}

# DECISION D3: share of total iron taken as Fe2+ for Mg-number (0.9 is a common choice for
# basalts near the FMQ buffer; 0.85 and 1.0 are also used).
FE2_FRACTION = 0.9

# DECISION D4: how to treat a below-detection value in a ratio.
#   "drop": ratio is NaN.  "half": use half the limit and flag the ratio as censored.
CENSORED_RULE = "drop"


def _value(series, rule=CENSORED_RULE):
    s = pd.to_numeric(series, errors="coerce")
    censored = s < 0
    if rule == "drop":
        v = s.where(s > 0)
    elif rule == "half":
        v = s.where(s > 0, s.abs() / 2).where(s != 0)
    else:
        raise ValueError(rule)
    return v, censored


def mg_number(mgo_wt, fe2o3t_wt, fe2_fraction=FE2_FRACTION):
    """Molar 100*Mg/(Mg+Fe2+), with Fe2+ = fe2_fraction * total Fe (from Fe2O3T)."""
    mg = mgo_wt / MW["MgO"]
    fet = 2 * fe2o3t_wt / MW["Fe2O3"]
    return 100 * mg / (mg + fe2_fraction * fet)


def indicators(wide: pd.DataFrame, rule: str = CENSORED_RULE) -> pd.DataFrame:
    """Return one row per sample with Cu/Pd, Ni/Cu, Pd/Pt, MgO, Mg#, and censoring flags."""
    cu, cu_c = _value(wide["Cu_ppm"], rule)
    ni, ni_c = _value(wide["Ni_ppm"], rule)
    pd_, pd_c = _value(wide["Pd_ppb"], rule)
    pt, pt_c = _value(wide["Pt_ppb"], rule)
    mgo, _ = _value(wide["MgO_wt"], "drop")
    fe, _ = _value(wide["Fe2O3T_wt"], "drop")
    out = pd.DataFrame({"mcr_uid": wide["mcr_uid"]})
    out["Cu_ppm"], out["Ni_ppm"], out["Pd_ppb"], out["Pt_ppb"] = cu, ni, pd_, pt
    out["MgO_wt"] = mgo
    out["mg_number"] = mg_number(mgo, fe)
    # Cu/Pd uses both in ppm; primitive mantle about 7,000 (see D5).
    out["cu_pd"] = cu / (pd_ / 1000.0)
    out["ni_cu"] = ni / cu
    out["pd_pt"] = pd_ / pt
    out["cu_pd_censored"] = cu_c | pd_c
    out["ni_cu_censored"] = ni_c | cu_c
    return out


# DECISION D5 (kept by Bezali 2026-10-27): fertility classes from Cu/Pd. Primitive-mantle Cu/Pd is
# taken as 7,000, rounded from McDonough and Sun (1995) primitive mantle Cu 30 ppm and Pd 3.9 ppb
# (ratio about 7,700). Values well above mantle mean the magma lost PGE to sulfide earlier
# (PGE-depleted, sulfide saturation upstream); values below mantle mean PGE-enriched
# (sulfide-bearing or cumulate). Thresholds below are provisional.
CU_PD_MANTLE = 7000.0
CU_PD_DEPLETED = 3 * CU_PD_MANTLE   # above this: PGE-depleted
CU_PD_ENRICHED = CU_PD_MANTLE / 3   # below this: PGE-enriched


def cu_pd_class(cu_pd: pd.Series) -> pd.Series:
    c = pd.Series("undetermined", index=cu_pd.index, dtype="object")
    c[cu_pd > CU_PD_DEPLETED] = "pge_depleted"
    c[(cu_pd <= CU_PD_DEPLETED) & (cu_pd >= CU_PD_ENRICHED)] = "mantle_like"
    c[cu_pd < CU_PD_ENRICHED] = "pge_enriched"
    return c
