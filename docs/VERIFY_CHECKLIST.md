# Your verification checklist

*Plain-language version: before anything goes public under your name, you check it. Tick each box and write the date. Total time: about 2 to 3 hours. You can split it over two sittings (Parts 1 to 3, then 4 and 5). When everything is ticked, tell Claude in your own words that you have checked the package and approve publishing.*

## Part 1: Make sure the results can be rebuilt (20 to 30 min)

Pick one:
- [ ] **Option A, run it yourself.** In the project folder, run `./run_all.sh`. It downloads about 1 GB and takes about 10 minutes. The last lines should show `14 passed` and `Done`.
- [ ] **Option B, ask Claude.** In a new chat (Opus 5.5 or Fable 5), give it the repository and say: "Re-run this pipeline from scratch with run_all.sh and give me the headline numbers in paper/stats.json." Compare them with the list below.

Headline numbers to match (from `paper/stats.json`):
- `grid_stats.n_cells` = 984,215, and `grid_stats.area_km2` = 39,368.6
- `combine_stats.eagle_score_percentile` = 98.86
- `targets.n` = 1,629
- `chem_model_stats.spatial_cv.auc` = 0.485
- `fertility_stats.n_cu_pd_in_survey` = 94

Then:
- [ ] Every number in `README.md` and `docs/TALK_TRACK.md` matches `paper/stats.json`. These two files are generated from it, so a mismatch means they were edited by hand.
- [ ] The typed numbers in `docs/LIMITATIONS.md` (507 covered targets, 945 targets with the 3-square rule, 44,519 edge squares, 94 Cu/Pd samples) match `paper/stats.json`.

## Part 2: Check the sources (15 min)

- [ ] https://doi.org/10.5066/P9K1HBNT opens the USGS deposit list, ver. 3.0. The citation lists four authors: Hammarstrom, Woodruff, Dicken and Zach, 2026. License: CC0.
- [ ] https://doi.org/10.5066/P14ESDF7 opens the 2025 airborne survey (Drenth, Murchek, Brown and Connell). Public domain.
- [ ] https://doi.org/10.5281/zenodo.23516434 opens MCR-GeoChem **v1.0.1** (published today). CC BY-SA 4.0.
- [ ] https://doi.org/10.3133/ds1052 opens the State Geologic Map Compilation. Public domain.
- [ ] The README calls Eagle "the only U.S. mine that produces nickel as its main product." Confirm this is still true on a current USGS or Lundin Mining page. If it isn't, ask Claude to reword it.

## Part 3: Check values by hand (45 min)

**Known places (you can check these yourself):**
- [ ] Open `data/processed/ni_cu_pge_deposits.csv`. In the "Eagle mine" row, `Lat_WGS84` = 46.74815 and `Long_WGS84` = -87.89729. In the USGS spreadsheet (sheet `2026_CM_deposits`), the Eagle mine row shows the same values.
- [ ] Open the map (`site/index.html`) and click the gold star near Marquette. It says "Eagle mine". Zoom in: it sits on the Yellow Dog Plains, about 40 km northwest of Marquette.
- [ ] In `data/processed/targets_ranked.csv`, row 1 is MCR-T0001 at 46.06410, -90.35785. Paste those coordinates into Google Maps. It should fall in Iron County, Wisconsin, near Mercer, inside the survey area.

**Values from MCR-GeoChem (open `mcr_geochem_wide.csv` from your Zenodo record, then `data/processed/sample_fertility.csv`):**
- [ ] MCRG-S1-W254289: Cu 134 ppm, Pd 9.4 ppb. Cu/Pd = 134 / 0.0094 = **14,255**, so the class is mantle_like.
- [ ] MCRG-S1-W254324: Cu 92, Ni 200, Pd 2.1. Cu/Pd = **43,810** (pge_depleted). Ni/Cu = **2.17**. With MgO 8.29% and Fe2O3T 11.995%, Mg-number = **60.3**.
- [ ] MCRG-S1-W255488: Cu 210, Pd 1.5. Cu/Pd = **140,000** (pge_depleted).

**Extreme values:**
- [ ] The highest Cu/Pd in an igneous rock inside the survey is MCRG-S1-W254298: Cu 249 ppm, Pd 0.6 ppb, so Cu/Pd = 415,000. Is a Pd of 0.6 ppb believable for that rock, or is it near the detection limit? ___
- [ ] The highest Cu/Pd overall in the survey is in **sedimentary** rocks, for example MCRG-S1-C487249 (Cu 36,300 ppm). Confirm that sedimentary rocks are left out of the map's Cu/Pd layer (open the map, tick "Rock samples with Cu/Pd", click a few dots: all should say igneous).

**Geophysics at Eagle:**
- [ ] In `data/processed/grid_features.parquet` (or ask Claude to print it), cell C0417_0994 is the Eagle cell: RTP 63.2 nT, K 0.59%, eTh 1.35 ppm. Open the USGS release's `TotalMagAnom_AirborneMagRadUP.png` and check that there is a small magnetic high at Eagle.

## Part 4: Your decisions (20 min)

Each one is in `docs/DECISIONS.md`. Agree, or tell Claude what to change.
- [ ] **D2.** Rocks within 2 km of a deposit count as "near"; more than 10 km is "far". Going to 5 km "near" adds more samples, but the near group would then include more barren rock. My suggestion: keep 2 km. Your choice: ___
- [ ] **D3.** Fe2+ is taken as 0.9 of total iron for the Mg-number. 0.85 or 1.0 shift Mg-number by about 1 to 3 units. My suggestion: keep 0.9. Your choice: ___
- [ ] **D5.** Cu/Pd classes are based on a primitive-mantle value of 7,000. Please confirm the value and the citation (Barnes and others, 1993, or a newer estimate). Your value: ___
- [ ] **D6.** Weights: magnetics 0.35 + 0.35, radiometrics 0.15 + 0.15. Eagle stays between the 97.6th and 98.8th percentile across 200 random weightings, so this choice matters little for Eagle. It does change which targets lead the list. My suggestion: keep. Your choice: ___
- [ ] **D7.** Targets are the top 2% of squares, and single squares are allowed (see disclosure 2). Top 1% would give fewer, stronger targets. My suggestion: keep 2%. Your choice: ___
- [ ] **D11.** Iron formation x0.3, volcanic x0.6. Should Archean greenstone or granite units also be down-weighted? Your choice: ___
- [ ] **D12.** 507 targets sit under Phanerozoic cover. Keep them flagged (my suggestion), down-weight them, or drop them? Your choice: ___
- [ ] Read the four disclosures in `docs/DECISIONS.md`. You agree they will appear in the paper.

## Part 5: Before it goes public (20 min)

- [ ] Rewrite the "In plain terms" paragraph of `README.md` in your own words. Claude can do it with you line by line. Then copy it into `code/templates/README.md.tmpl` so it survives rebuilds.
- [ ] Your name, ORCID (0009-0006-1201-4129), affiliation and email (dansobez@msu.edu) are correct in `AUTHORS.json`. Do you want your email to be public? ___
- [ ] You have read `docs/LIMITATIONS.md` and agree with all ten points.
- [ ] Claude regenerates everything with `--final`, and `publish_gate.py` passes.
- [ ] On release day, log the evidence (GitHub URL, Zenodo DOI, date).
