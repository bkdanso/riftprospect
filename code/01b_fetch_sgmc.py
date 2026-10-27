#!/usr/bin/env python3
"""01b_fetch_sgmc.py: USGS State Geologic Map Compilation polygons for Michigan and Wisconsin.

Plain-language note: downloads the state geology map (Horton and others, 2017,
doi:10.3133/ds1052) for the two states, used for decision D11 (geology mask). Logs provenance.
"""
import json, pathlib, subprocess, sys, urllib.parse, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]
FS = ("https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/"
      "SB_5888bf4fe4b05ccb964bab9d_USGS_SGMC_feature/FeatureServer/3/query")
OUT = ROOT / "data/raw/sgmc/sgmc_MI_WI.geojson"
if not OUT.exists():
    feats, off = [], 0
    while True:
        q = urllib.parse.urlencode({"where": "STATE IN ('MI','WI')", "outFields": "*", "outSR": 32616,
                                    "f": "geojson", "resultOffset": off, "resultRecordCount": 500})
        with urllib.request.urlopen(FS + "?" + q) as r:
            j = json.load(r)
        feats += j["features"]; off += len(j["features"])
        if len(j["features"]) < 500: break
    j["features"] = feats
    j["crs"] = {"type": "name", "properties": {"name": "EPSG:32616"}}
    OUT.write_text(json.dumps(j))
    subprocess.run([sys.executable, str(ROOT / "code/provenance.py"), str(OUT), FS,
                    "--log", str(ROOT / "data/raw/PROVENANCE.txt"),
                    "--note", "SGMC (doi:10.3133/ds1052) ArcGIS FeatureServer layer 3, STATE IN ('MI','WI'), outSR 32616"], check=True)
print(OUT, OUT.stat().st_size)
