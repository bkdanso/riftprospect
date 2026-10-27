# Build spec: riftprospect (MCR magmatic Ni-Cu-Co-PGE prospectivity)

*Plain-language note: this is the one-page plan the whole build follows. If the project changes shape, this page changes first. The table at the bottom says what each line means for you.*

```
PROJECT:     riftprospect. Archetypes: pipeline/tool (Python package) + atlas (web map)
             + open dataset (ranked target table) + validation study (preprint).
QUESTION:    Where in the 2025 Earth MRI survey area (Upper Peninsula of Michigan and
             northern Wisconsin) do public rock chemistry and airborne geophysics most
             resemble the setting of known magmatic Ni-Cu-Co-PGE sulfide deposits, and how
             confident is that ranking?
SOURCES:
  S1 USGS Critical Mineral Deposits of the United States, ver. 3.0, Sept 2026
     (Hammarstrom, Woodruff, Dicken and Zach), doi:10.5066/P9K1HBNT, CC0. Labels.
  S2 Airborne magnetic and radiometric survey, Upper Peninsula, Michigan, and parts of
     northern Wisconsin, 2025 (Drenth, Murchek, Brown and Connell, 2026),
     doi:10.5066/P14ESDF7, public domain. Grids: RTP, FVD, K, eTh, eU; Block A 37.5 m,
     Block B 100 m cells, UTM 16N (EPSG:32616).
  S3 MCR-GeoChem v1.0.1 (Danso and Abdullah, 2026), github.com/bkdanso/mcr-geochem tag
     v1.0.1; Zenodo doi:10.5281/zenodo.23516434. Data CC BY-SA 4.0.
  S4 (candidate, pending decision D1) USGS Mineral Resources Data System (MRDS), 2011
     snapshot, mrdata.usgs.gov/mrds, public domain. Weak labels only.
  All accessed 2026-10-27; hashes in data/raw/PROVENANCE.txt.
UNIT:        200 m x 200 m grid cell inside the survey footprint (map and target table);
             one rock sample (fertility indicators).
MEASURES:
  Per sample: Cu/Pd (Cu ppm / Pd ppm), Ni/Cu, MgO wt%, Mg-number = 100*Mg/(Mg+Fe2+)
     molar with Fe2+ = 0.9 * FeT (provisional, D3), censored values handled per D4.
  Per cell: mean RTP, FVD, K, eTh, eU; derived analytic signal, Th/K, local texture;
     distance-weighted fertility indicators with sample-density mask.
  Model: decided at D1; scores 0-1 with ensemble uncertainty (spread across resamples).
OUTPUTS:     src/riftprospect/ (package) + tests/; data/processed/grid_features.parquet,
             sample_fertility.csv, targets_ranked.csv; site/ (Leaflet map, GitHub Pages);
             paper/ (validation-study preprint, built from paper/stats.json).
VENUES:      GitHub + PyPI + Zenodo (package); GitHub Pages (map); Zenodo (target table);
             ESSOAr preprint (validation study), then a journal (e.g. Natural Resources
             Research, or Ore Geology Reviews).
VERIFY POINTS (Bezali rules on each):
  D1 training-label strategy (see checkpoint 1: only one CMD deposit is in the survey)
  D2 positive radius around deposits; D3 Fe2+/FeT ratio; D4 censored-value rule
  D5 Cu/Pd and Ni/Cu fertility thresholds; D6 evidence weights in any knowledge-driven layer
  D7 cutoff for "target" in the ranked table; D8 wording of all claims
LICENSE:     Code MIT. Target table and map data CC BY-SA 4.0 (required: built from
             MCR-GeoChem, which is CC BY-SA). Docs CC BY 4.0.
ASSUMPTIONS: package name riftprospect (free on PyPI 2026-10-27); study area = survey
             footprint; grid 200 m (coarser than Block A, finer than Block B line spacing).
```

## What each line means for you

| Line | In plain words |
|---|---|
| Question | The one thing the project answers. Every output serves it. |
| Sources | Three free public datasets. One is your own MCR-GeoChem. |
| Unit | The map is cut into squares 200 m on a side. Each row of the target table is one square. |
| Measures | The chemistry ratios you named, plus the airborne magnetism and radioactivity in each square. |
| Outputs | The package, the map, the table, and the paper. |
| Verify points | Choices only you should make. I will ask each one in plain words with a suggestion. |
| License | The table must be CC BY-SA, not CC BY, because MCR-GeoChem is CC BY-SA. "Share-alike" means anyone who reuses it must share their version under the same terms. |
