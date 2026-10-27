# Codebook

*Plain-language note: every column in every output file, with its unit and where it comes from. Look a column up here when you open a file.*

## `data/processed/targets_ranked.csv` (the ranked target table; CC BY-SA 4.0)

One row is one target: a group of touching 200 m squares that are all in the top 2% of the final score, at least 1 km from a survey edge.

| Column | Meaning |
|---|---|
| `target_id` | Permanent ID, `MCR-T` + rank (zero-padded). Stable within a version only |
| `rank` | 1 = highest peak score; ties broken by size |
| `latitude`, `longitude` | Centre of the target's squares, WGS84 decimal degrees |
| `area_km2` | Number of squares x 0.04 km² |
| `score_mean`, `score_max` | Mean and peak final score of the target's squares, 0 to 1 |
| `score_sd_mean` | Mean uncertainty: standard deviation of the score across 100 random weightings, after the geology multiplier |
| `block` | USGS survey block: A (west, 150 m lines) or B (east, 400 m lines) |
| `geo_class` | Most common mapped setting (SGMC): intrusive, Mesoproterozoic volcanic, iron formation (+500 m), Phanerozoic sedimentary cover, other or unmapped |
| `cu_pd_label` | Most common Cu/Pd class of the nearest igneous MCR-GeoChem sample within 5 km, or "no sample within 5 km". Descriptive only; not part of the score |
| `km_to_known_ni_cu_pge` | Distance to the nearest Ni-Cu-PGE deposit in USGS CMD v3.0, km |

## `data/processed/prospectivity_cells.parquet` (one 200 m square)

`cell_id` (`C<row>_<col>`), `row`, `col`, `x`, `y` (cell centre, m, UTM 16N, EPSG:32616), `block`, `edge_dist_m` (distance to nearest no-data square, m), `geo_score` and `geo_sd` (geophysics score and SD before the mask), `geo_score_fixed` (score with the central weights only), `pct_rtp_asig`, `pct_rtp_resid`, `pct_k`, `pct_th` (within-block percentile of each layer), `geo_class`, `geo_class_label`, `geo_masked`, `geo_masked_sd`, `cu_pd_class_nearby`, `evidence`, `score`, `score_sd` (final score and SD).

## `data/processed/grid_features.parquet`

Mean of each USGS grid over the 200 m square: `rtp` (reduced-to-pole magnetic anomaly, nT), `fvd` (first vertical derivative, nT/m), `k` (%), `th` (eTh ppm), `u` (eU ppm); derived `rtp_asig` (analytic signal amplitude, nT/m), `rtp_std2km` (local SD of RTP, nT), `rtp_resid` (RTP minus its 2.2 km mean, nT), `th_k`.

## `data/processed/sample_fertility.csv` and `sample_scores.csv`

One MCR-GeoChem whole-rock sample. `cu_pd` = Cu (ppm) / Pd (ppm); `ni_cu` = Ni/Cu; `pd_pt` = Pd/Pt; `mg_number` = 100 Mg/(Mg + 0.9 FeT), molar; `cu_pd_class` (pge_depleted > 21,000; mantle_like 2,333 to 21,000; pge_enriched < 2,333); `*_censored` = a below-detection value was involved; `in_survey`; `dep_km`, `dep_name` (nearest CMD Ni-Cu-PGE deposit); `chem_score`, `chem_sd` (Part A model, bootstrap mean and SD); `in_domain` (intrusive, not altered: the rocks the model was trained on).
