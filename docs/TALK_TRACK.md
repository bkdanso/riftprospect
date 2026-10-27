# Talk track

*Plain-language note: what to say when someone asks about this project. Every number comes from paper/stats.json. Status: Released.*

## 60 seconds

Nickel, cobalt and the platinum-group metals are critical minerals for the United States, and the Eagle mine in Michigan's Upper Peninsula is the country's only primary nickel mine. The rocks around Lake Superior could hide more deposits like Eagle, but most are under glacial cover, and exploration is expensive. I built an open, reproducible model that uses the U.S. Geological Survey's new 2025 airborne survey to rank every 200-meter square of the Upper Peninsula and northern Wisconsin, about 39,368.6 square kilometers, by how much it looks like the kind of small magnetic intrusion that hosts Eagle. I never let the model see Eagle while building it, and it still put Eagle in the top 1.14 percent of the area. I also tested whether public rock-chemistry signals can predict where deposits are, and found that the commonly used ratios did not hold up when tested on new areas, which is useful for anyone designing sampling programs. The result is a free map, a ranked list of 1,629 targets with uncertainty, and an open Python package that state surveys and exploration geologists can use and check.

## Two sentences

I built an open model that ranks the Upper Peninsula and northern Wisconsin for nickel-copper-platinum deposits using the USGS 2025 airborne survey, and it placed the Eagle mine, which it never saw, in the top 1.14 percent of the area. The map, the ranked target list and the code are public so geological surveys and explorers can test them.

## Likely questions

**Does this mean there is a deposit at target 1?** No. It means the airborne data look most like Eagle's setting there. A geologist would check the ground, the existing drill records, and follow-up surveys.

**One deposit is a small test. Why trust it?** It is a small test, and the paper says so. Eagle stayed between the 97.6th and 98.77th percentile across 200 different ways of weighting the evidence, which shows the result is not a fluke of one setting, but more deposits are needed for a strong statistical claim.

**Why doesn't rock chemistry help?** Public samples are concentrated far from the Upper Peninsula's nickel prospects, and in Minnesota the standard ratios did not separate near-deposit from far-from-deposit rocks when whole areas were held out (scores between 0.29 and 0.48 depending on how close counts as near, where 0.5 is chance). That is a finding: it tells surveys where new sampling would add the most.
