# Start Here: Midcontinent Rift Nickel-Copper Prospectivity Model

*Read this first. It explains your project in plain language. Words in bold are explained in [GLOSSARY.md](GLOSSARY.md).*

## What you are building

A free, open tool and map that ranks places in Michigan's Upper Peninsula and northern Wisconsin by how likely they are to hide nickel, copper, cobalt, and platinum-group metal deposits, using only public data.

## Why it matters

The United States lists nickel, cobalt, and the platinum-group metals as critical minerals. The Midcontinent Rift, a 1.1-billion-year-old crack in the continent, hosts the Eagle mine near Marquette, the only active US nickel mine. Finding the next deposit is expensive because it hides under glacial cover. Your model turns two kinds of free public evidence into a ranked list of places worth testing:

- **Rock chemistry.** Magma that formed a metal deposit leaves a fingerprint: it gets stripped of copper and platinum metals, which shows up as unusual ratios such as Cu/Pd and Ni/Cu.
- **Airborne surveys.** The US Geological Survey flew low-level planes over the region in 2025 and measured magnetism and natural radioactivity. Buried magma bodies show up as magnetic highs.

Think of it like a weather forecast for ore: it does not say "dig here," it says "the odds are higher here, and here is how sure we are."

## Where the information comes from

All sources are free and public.

| Source | In plain terms | What one row looks like | Link |
|---|---|---|---|
| USGS Critical Mineral Deposits of the United States, ver. 3.0 (Sept 2026), Hammarstrom, Woodruff, Dicken and Zach | The government's list of known critical-mineral deposits; your "answer key" for training | One deposit: name, location, deposit type, metals | https://doi.org/10.5066/P9K1HBNT (public domain, CC0) |
| USGS Earth MRI airborne magnetic and radiometric survey, Upper Peninsula and northern Wisconsin, 2025 (Drenth and others, 2026) | Magnetic and radioactivity maps flown by plane | One grid cell: location, magnetic field strength, potassium, thorium, uranium | https://doi.org/10.5066/P14ESDF7 |
| MCR-GeoChem v1.0.1 (your dataset, with Saadatu Abdullah) | Rock chemistry samples from the rift | One rock sample: location, MgO, Ni, Cu, Pd, Pt, and other elements | https://doi.org/10.5281/zenodo.23516434 (CC BY-SA 4.0) |
| USGS State Geologic Map Compilation | The mapped rock type at every place | One map area: rock type and age | https://doi.org/10.3133/ds1052 (public domain) |

## What you will have at the end

- [ ] **An open Python package** anyone can install, with tests: on PyPI and GitHub, with a DOI
- [ ] **A public interactive map** of prospectivity, on GitHub Pages
- [ ] **A ranked target table** with model scores and uncertainty, on Zenodo with a DOI
- [ ] **A validation study** (preprint) testing whether public geochemical anomalies line up with known deposits

## How it connects to your work

It extends published statistical and machine-learning methods for predicting mineralogy from geochemistry into a public, reproducible tool for critical-mineral exploration in the rift, the same region your MCR-GeoChem work covers.

## What you need to do

| Your task | When | Time |
|---|---|---|
| Create accounts (ORCID, GitHub, Zenodo, PyPI) | Now | 20 min |
| Answer five setup questions | Now | 10 min |
| Make each modeling decision as it comes up | During the build | 10 min each |
| Check the results using the checklist | When the draft is ready | 2 to 3 hours |
| Approve publishing | After checking | 5 min |
| Submit the preprint yourself, using the guide | After publishing | 20 min |

## The steps ahead

1. **Data collected.** Done.
2. **Data combined.** Done: 984,215 squares of 200 m.
3. **Fertility indicators computed.** Done. The chemistry model did not hold up when tested on new areas, so the map does not use it (your decision D9).
4. **First map.** Done. Geology mask added (your decision D11).
5. **Model validated.** Done. Eagle, never used to build the score, ranks at the 98.9th percentile.
6. **Package, map, table ready for your check.** Done. You verify, then we publish. The validation paper is written after you verify, so it only uses checked numbers.

*You are here: step 6, your check (docs/VERIFY_CHECKLIST.md)*
