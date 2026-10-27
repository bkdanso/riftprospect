"""Geology mask (decision D11): down-weight rock types that are magnetic but not Ni-Cu hosts.

Plain-language note: iron formation and the thick Keweenawan lava pile are strongly magnetic,
so the geophysics score flags them even though magmatic nickel deposits are not hosted there.
This module paints each 200 m square with its mapped rock type from the USGS State Geologic
Map Compilation and applies a multiplier. Multipliers are DECISION D11.
"""
from __future__ import annotations
import numpy as np
import geopandas as gpd
from rasterio.features import rasterize

# class code: (label, multiplier)
CLASSES = {0: ("other or unmapped", 1.0),
           1: ("iron formation (+500 m)", 0.3),
           2: ("Mesoproterozoic volcanic", 0.6),
           3: ("intrusive", 1.0),
           4: ("Phanerozoic sedimentary cover", 1.0)}  # D12: kept at 1.0 but flagged; depth to target unknown
PHANEROZOIC = "Cambrian|Ordovician|Silurian|Devonian|Mississippian|Pennsylvanian|Permian|Jurassic|Cretaceous|Paleozoic"
IF_BUFFER_M = 500.0


def classify(sgmc: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    g = sgmc.copy()
    lith = g.GENERALIZED_LITH.fillna("")
    iron = lith.str.contains("iron formation", case=False) | g.MAJOR1.fillna("").str.contains("iron-formation", case=False)
    meso = (g.AGE_MIN.fillna("") + g.AGE_MAX.fillna("")).str.contains("Mesoproterozoic")
    volc = lith.str.contains("volcanic", case=False) & meso
    intr = lith.str.contains("intrusive", case=False)
    phan = g.AGE_MIN.fillna("").str.contains(PHANEROZOIC) & lith.str.contains("Sedimentary")
    g["geo_class"] = np.select([iron, intr, volc, phan], [1, 3, 2, 4], 0)
    return g


def rasterize_classes(g: gpd.GeoDataFrame, transform, shape) -> np.ndarray:
    """Paint class codes in increasing priority: volcanic, intrusive, then buffered iron formation on top."""
    out = np.zeros(shape, dtype="uint8")
    for code in (4, 2, 3):
        sub = g[g.geo_class == code]
        if len(sub):
            out = np.where(rasterize(((geom, 1) for geom in sub.geometry), out_shape=shape,
                                     transform=transform, fill=0, dtype="uint8") == 1, code, out)
    iron = g[g.geo_class == 1]
    if len(iron):
        m = rasterize(((geom.buffer(IF_BUFFER_M), 1) for geom in iron.geometry), out_shape=shape,
                      transform=transform, fill=0, dtype="uint8")
        out[m == 1] = 1
    return out


def multiplier(codes: np.ndarray) -> np.ndarray:
    lut = np.array([CLASSES[k][1] for k in sorted(CLASSES)], dtype="float32")
    return lut[codes]
