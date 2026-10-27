"""Command line: `riftprospect fertility my_table.csv` scores your own samples.

Plain-language note: lets anyone compute the fertility indicators (Cu/Pd, Ni/Cu, MgO,
Mg-number, Cu/Pd class) on their own spreadsheet laid out like MCR-GeoChem's wide table.
"""
import argparse
import sys

import pandas as pd

from . import __version__
from .fertility import indicators, cu_pd_class


def main(argv=None):
    ap = argparse.ArgumentParser(prog="riftprospect", description=__doc__)
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fertility", help="compute fertility indicators for a CSV of samples")
    f.add_argument("csv"); f.add_argument("--out", default="-")
    f.add_argument("--id-col", default="mcr_uid")
    f.add_argument("--censored", choices=["drop", "half"], default="drop")
    a = ap.parse_args(argv)
    df = pd.read_csv(a.csv, low_memory=False)
    need = ["Cu_ppm", "Ni_ppm", "Pd_ppb", "Pt_ppb", "MgO_wt", "Fe2O3T_wt"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        sys.exit(f"missing columns: {', '.join(missing)} (units: Cu, Ni ppm; Pd, Pt ppb; oxides wt%)")
    out = indicators(df.rename(columns={a.id_col: "mcr_uid"}), rule=a.censored)
    out["cu_pd_class"] = cu_pd_class(out.cu_pd)
    out.rename(columns={"mcr_uid": a.id_col}).to_csv(sys.stdout if a.out == "-" else a.out, index=False)


if __name__ == "__main__":
    main()
