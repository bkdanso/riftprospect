#!/usr/bin/env bash
# Rebuild everything from public sources. About 10 minutes plus about 1 GB of downloads.
set -euo pipefail
cd "$(dirname "$0")"
pip install -e ".[test]"
python code/01_fetch.py
python code/01b_fetch_sgmc.py
python code/02_grid.py
python code/03_fertility.py
python code/04_fig_overview.py "$@"
python code/05_chem_model.py
python code/06_geophys.py
python code/08_combine.py
python code/07_fig_geophys.py "$@"
python code/09_validate.py
python code/10_site.py "$@"
pytest -q
echo "Done. Headline numbers: paper/stats.json"
