#!/usr/bin/env python3
"""01_fetch.py: download every raw input and log provenance.

Plain-language note: this script downloads the three public sources (USGS deposit
list, USGS airborne grids, MCR-GeoChem) into data/raw/ and writes a line per file
to data/raw/PROVENANCE.txt saying where it came from, when, its size and a
fingerprint (SHA-256). You do not need to open it. File lists are discovered
from the ScienceBase JSON API so the script survives USGS URL changes.
"""
import json
import pathlib
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
LOG = RAW / "PROVENANCE.txt"
SB = "https://www.sciencebase.gov/catalog"

# USGS Critical Mineral Deposits of the United States, ver. 3.0 (Sept 2026), doi:10.5066/P9K1HBNT
CMD_ITEM = "6464de5bd34ec179a83d9e6c"
CMD_FILES = ["critical_mineral_deposits_all_tables_v3.xlsx.xlsx",
             "critical_mineral_deposits_revisions_history_3.0.txt",
             "critical_mineral_deposits_metadata_v3.0.xml"]
# Airborne magnetic and radiometric survey, UP Michigan and parts of N Wisconsin, 2025, doi:10.5066/P14ESDF7
MAG_ITEM = "6a375ed61ba49b36765ff1ad"
RAD_ITEM = "6a3779551ba49b36765ff3c5"
GRID_KEYS = ["_RTP_", "_FVD_", "_K_", "_Th_", "_U_"]
MD_FILES = ["MagDataDictionary_AirborneMagRadUP.csv", "MagMetadata_AirborneMagRadUP.xml",
            "RadDataDictionary_AirborneMagRadUP.csv", "RadMetadata_AirborneMagRadUP.xml"]
# MCR-GeoChem v1.0.1 (Danso and Abdullah), doi:10.5281/zenodo.23516434
MCRG_REPO = "https://github.com/bkdanso/mcr-geochem"
MCRG_TAG = "v1.0.1"
MCRG_FILES = ["data/processed/mcr_geochem_samples.csv", "data/processed/mcr_geochem_wide.csv",
              "data/processed/stats.json"]


def sb_files(item):
    with urllib.request.urlopen(f"{SB}/item/{item}?format=json") as r:
        # Large files live in S3 behind the ScienceBase "manager"; their `url` returns an
        # HTML viewer, so use the catalog file/get?name= endpoint instead.
        return {f["name"]: (f"{SB}/file/get/{item}?name={f['name']}" if "/manager/" in f["url"] else f["url"]) for f in json.load(r).get("files", [])}


def get(url, dest, note=""):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 10000 or (dest.exists() and dest.suffix != ".tif"):
        print("have", dest.name)
        return
    print("get ", dest.name)
    subprocess.run(["curl", "-sSL", "--fail", "-o", str(dest), url], check=True)
    subprocess.run([sys.executable, str(ROOT / "code" / "provenance.py"), str(dest), url,
                    "--log", str(LOG), "--note", note], check=True)


def main():
    files = sb_files(CMD_ITEM)
    for n in CMD_FILES:
        get(files[n], RAW / "cmd_v3" / n, "ScienceBase item " + CMD_ITEM + " (doi:10.5066/P9K1HBNT)")
    for item, kind in [(MAG_ITEM, "mag"), (RAD_ITEM, "rad")]:
        files = sb_files(item)
        for n, u in files.items():
            if (n.endswith(".tif") and any(k in n for k in GRID_KEYS)) or n in MD_FILES:
                get(u, RAW / "earthmri_up" / n, f"ScienceBase item {item} (doi:10.5066/P14ESDF7, {kind})")
    # GitHub raw URLs are blocked in some sandboxes, so take the tagged tree with git.
    dest = RAW / "mcr_geochem"
    if not (dest / "mcr_geochem_wide.csv").exists():
        tmp = RAW / "_mcrg_clone"
        subprocess.run(["rm", "-rf", str(tmp)], check=True)
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", MCRG_TAG, MCRG_REPO, str(tmp)], check=True)
        dest.mkdir(parents=True, exist_ok=True)
        for f in MCRG_FILES:
            (dest / pathlib.Path(f).name).write_bytes((tmp / f).read_bytes())
            subprocess.run([sys.executable, str(ROOT / "code" / "provenance.py"), str(dest / pathlib.Path(f).name),
                            f"{MCRG_REPO}/blob/{MCRG_TAG}/{f}", "--log", str(LOG),
                            "--note", f"MCR-GeoChem {MCRG_TAG}, git tag; Zenodo doi:10.5281/zenodo.23516434"], check=True)
        subprocess.run(["rm", "-rf", str(tmp)], check=True)


if __name__ == "__main__":
    main()
