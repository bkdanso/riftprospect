# Modeling decisions log

*Plain-language note: every choice that changes the results, with the options, what each would change, and who decided. Claude proposed; Bezali decided every item on 2026-10-27 (verification checklist, Part 4).*

| ID | Decision | Current setting | Where in code | Status |
|---|---|---|---|---|
| D1 | Training-label strategy | Two-part model: chemistry trained in Minnesota; geophysics rule-based; Eagle held out of all fitting | `chemmodel.py`, `geophys.py` | DECIDED by Bezali, 2026-10-27 |
| D2 | "Near a deposit" for chemistry labels | within 3 km positive, beyond 10 km negative, 3 to 10 km left out (changed from the suggested 2 km) | `chemmodel.NEAR_KM, FAR_KM` | DECIDED by Bezali, 2026-10-27 |
| D3 | Fe2+ share of total iron for Mg-number | 0.9 | `fertility.FE2_FRACTION` | DECIDED by Bezali, 2026-10-27 |
| D4 | Below-detection values in ratios | dropped (ratio left blank) | `fertility.CENSORED_RULE` | DECIDED by Bezali, 2026-10-27 |
| D5 | Cu/Pd classes | mantle 7,000 (rounded from McDonough and Sun, 1995: Cu 30 ppm, Pd 3.9 ppb, ratio about 7,700); depleted > 21,000; enriched < 2,333 | `fertility.CU_PD_*` | DECIDED by Bezali, 2026-10-27 |
| D6 | Geophysics evidence and weights | analytic signal 0.35, residual magnetic 0.35, low K 0.15, low eTh 0.15; logistic membership centred at the 75th percentile | `geophys.WEIGHTS` | DECIDED by Bezali, 2026-10-27 |
| D7 | Targets | top 2% of non-edge squares; single squares allowed; ranked by peak score | `combine.TARGET_TOP_PCT, MIN_TARGET_CELLS` | DECIDED by Bezali, 2026-10-27 (see disclosure 2) |
| D8 | Rocks for the chemistry model | intrusive, not flagged altered | `chemmodel.ROCK_CLASSES` | DECIDED by Bezali, 2026-10-27 |
| D9 | Role of chemistry | No chemistry score on the map (spatial CV AUC 0.29 at 3 km; 0.48 at 2 km). Cu/Pd shown as a label. Feature-set comparison reported as exploratory | `08_combine.py`, `09_validate.py` | DECIDED by Bezali, 2026-10-27 |
| D10 | Reach of the Cu/Pd label | nearest igneous sample within 5 km | `combine.CHEM_RADIUS_KM` | DECIDED by Bezali, 2026-10-27 |
| D11 | Geology mask | iron formation +500 m x0.3; Mesoproterozoic volcanic x0.6 (USGS SGMC) | `geology.CLASSES` | DECIDED by Bezali, 2026-10-27 |
| D12 | Phanerozoic sedimentary cover | not down-weighted, flagged in the table | `geology.CLASSES[4]` | DECIDED by Bezali, 2026-10-27 |
| QA | Edge rule | squares within 1 km of a data edge cannot be targets | `combine.EDGE_M` | QA rule (removes filter artifacts) |

## Disclosures for the paper

1. Before the weights in D6 were set, Eagle's raw layer percentiles were looked at once during the checkpoint 2 sanity check (analytic signal 93rd, K 33rd). The weights were then set from the deposit model, not tuned.
2. D7 originally required at least 3 squares per target. That rule dropped Eagle, whose anomaly is one square, so it was changed to 1, on the grounds that Eagle-type intrusions are about one square across. With the original rule there would be 945 targets and Eagle would not be one.
3. D11 was added after old USGS MRDS records of an iron mine (Pence) and Keweenaw nickel occurrences scored at the 98th percentile or higher. Those records are therefore not independent tests.
4. D9: five chemistry feature sets were compared, and the main model was re-run with near = 2, 3 and 5 km (AUC 0.48, 0.29, 0.35). The chemistry conclusion does not depend on the radius; the exact AUC does (paper/stats.json, `chem_feature_sets`). No feature set was adopted. Their AUCs change sharply with the near radius (for example, Cu, Ni, S: 0.84 at 2 km, 0.33 at 3 km), which is itself evidence that none is a stable predictor.

## D1 background

USGS CMD v3.0 lists one magmatic Ni-Cu-PGE deposit inside the survey (Eagle mine) and 10 in Minnesota, outside it. MCR-GeoChem has no samples within 10 km of Eagle. A model trained on one deposit is not defensible, so chemistry was trained where deposits and samples overlap (Minnesota), and geophysics was scored by rules from the deposit model.
