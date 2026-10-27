# Limitations

*Plain-language note: what this project cannot tell you. Written before any paper text, so the paper cannot claim more than this page allows. Please read it before using the map.*

1. **One held-out deposit.** Only the Eagle mine is a known magmatic Ni-Cu-PGE deposit inside the survey (USGS CMD v3.0). Its high rank is encouraging, but one deposit cannot give a statistically strong accuracy estimate. Under pure chance, any one point lands at or above Eagle's score 1.1% of the time.
2. **Eagle was not perfectly blind.** Eagle's raw percentiles were seen once during a sanity check before the weights were set. Two choices were made after seeing results involving Eagle: the minimum target size was lowered from 3 squares to 1 after Eagle's single-square anomaly fell out of the target list (with 3, there would be 945 targets and Eagle would not be one), and the geology mask was introduced after old MRDS records of an iron mine and Keweenaw nickel occurrences scored high. Both are disclosed in DECISIONS.md.
3. **The map is a geophysics map.** The chemistry model did not survive spatial cross-validation (AUC 0.29 with the 3 km near radius; 0.48 at 2 km; 0.35 at 5 km), so chemistry does not change any score. Cu/Pd is shown only as a label.
4. **Magnetic rocks of all kinds score high.** The mask down-weights mapped iron formation and Keweenawan lavas, but unmapped magnetic rocks (other iron formations, magnetite-bearing granitoids, Archean greenstones) remain false positives.
5. **Depth is unknown.** 507 targets sit under mapped Paleozoic sedimentary cover, mostly in the east. A magnetic source there may be hundreds of metres deep. The score does not estimate depth.
6. **Survey blocks differ.** Block B was flown on 400 m lines (Block A: 150 m), so small intrusions are less resolved in the east. Scores are ranked within each block, which makes them comparable in rank but not in absolute signal.
7. **Edges and gaps.** Squares within 1 km of a data edge cannot become targets because derivative filters are unreliable there. 44,519 squares (about 4.5%) are affected.
8. **Chemistry coverage is uneven.** MCR-GeoChem has no samples within 10 km of Eagle, and only 94 samples inside the survey have both Cu and Pd. Statistics comparing samples near and far from deposits treat clustered samples as independent, so p-values overstate certainty.
9. **Labels are incomplete.** Absence from CMD v3.0 does not mean absence of mineralization. Industry drill data are not public and were not used.
10. **Not an investment or land-use tool.** Scores rank geophysical similarity. They are not resource estimates and say nothing about economics, land status or permitting.
