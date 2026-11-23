# Where should steel and ammonia be made in Europe, and how much hydrogen does each pathway need?

Research study: a regional linear programme for steel and ammonia production in nine European regions in 2030, 2040 and 2050 with hydrogen production, pipeline transport and trade of steel, direct reduced iron (HBI) and ammonia. Four pathways switch options on and off: all options, a hydrogen pathway without CCS, a CCS pathway without electrolytic hydrogen and hydrogen without pipelines. Hydrogen is balanced in two seasons (April to September and October to March) with the renewable potential of each region split by its own seasonal share of the weather year, and a seasonal store can be added to three of the pathways.

**What is real and what is assumed.** The hydrogen cost of each region is computed from hourly 2023 wind speed at 100 m and solar radiation (Open-Meteo archive, ERA5-based), a cubic power curve and an electrolyser sized to minimise cost. **Everything else is an assumption** (`data/sources.csv`): the nine regions are a stylised subset of Europe, not the EU ETS installation registry (it could not be obtained automatically; the real facility data of the EEA industrial reporting database are used only as a benchmark, see below); regional steel (59 Mt) and ammonia (6.9 Mt) production, the storage cost (8 EUR per MWh moved) and regional storage capacities, unit energy needs, costs, CCS capacities, renewable potentials, the CO2 price path (100, 150, 200 EUR/t), gas and electricity prices and the phase-out of blast furnaces are illustrative. Static annual cost per year, no investment dynamics, no sectors beyond steel and ammonia. The study shows how pathways differ in structure, hydrogen demand and location, not where plants will be built.

## Question
Where should steel and ammonia be produced under different decarbonisation pathways, and how much hydrogen and which infrastructure does each pathway need?

## Hydrogen cost from the weather data (EUR per MWh of hydrogen, `results/lcoh_by_region.csv`)
| Region | 2030 | 2050 |
|---|---:|---:|
| NL-Rotterdam | 137 | 104 |
| FR-North | 141 | 107 |
| ES-Iberia | 157 | 119 |
| DE-West | 188 | 144 |
| DE-North | 206 | 157 |
| PL-Silesia | 219 | 168 |
| SE-North | 225 | 172 |
| IT-North | 317 | 247 |
| NO-West | 319 | 248 |

The coast of the North Sea and the Iberian interior have the cheapest wind and solar mixes in this single-year, single-site data; the costs are higher than many published estimates because of one weather year, one site per region and assumed capital costs.

## Results (`results/pathway_summary.csv`, `regional_detail.csv`, `flows.csv`)
2050, 59 Mt of steel and 6.9 Mt of ammonia in the nine regions:

| Pathway | Cost, million EUR | CO2 emitted, Mt | Hydrogen, TWh | Steel route | Ammonia | Trade |
|---|---:|---:|---:|---|---|---|
| All options | 33,955 | 5.8 | 68.6 | 44 Mt hydrogen DRI with electric arc furnaces, 15 Mt scrap | all reforming with CCS | 42 TWh hydrogen by pipeline, no steel or HBI traded |
| Hydrogen, no CCS | 35,229 (+3.8%) | 16.1 | 68.9 | as above | reforming without CCS | 42 TWh hydrogen |
| CCS, no electrolytic hydrogen | 35,272 (+3.9%) | 19.1 | 0 | 44.5 Mt gas DRI with CCS | reforming with CCS | 19.8 Mt of steel moved to regions with CCS |
| Hydrogen without pipelines | 34,150 (+0.6%) | 8.1 | 57.2 | 37 Mt hydrogen DRI, 8 Mt gas DRI with CCS | reforming with CCS | 19.6 Mt of HBI shipped, no hydrogen pipelines |
| Hydrogen without pipelines, with seasonal storage | 34,096 (+0.4%) | 7.4 | 60.6 | 39 Mt hydrogen DRI, 5 Mt gas DRI with CCS | reforming with CCS | 21.8 Mt of HBI shipped, 1.7 TWh moved between seasons |

- **Hydrogen demand follows the steel route.** The steel in these regions needs 69 TWh of hydrogen in 2050 (1.67 MWh per tonne in the electric arc route), 31 TWh in 2040 and nothing in 2030, when blast furnaces (80% of capacity) and scrap supply the steel and reforming with CCS the ammonia. Electrolytic ammonia is never chosen: at 200 EUR/t CO2 reforming with CCS is cheaper than 5.9 MWh of hydrogen per tonne at 104 to 119 EUR/MWh, so the limited cheap hydrogen goes to steel first.
- **Hydrogen is produced where it is cheap and piped to the steel regions.** In 2050 hydrogen comes from the Netherlands (15 TWh, at the assumed potential), northern France (20 TWh, at the potential) and Iberia (34 TWh of 80), and 42 TWh moves by pipeline over a transport work of 45 TWh x 1,000 km, to Germany, Poland, Italy and Sweden. Steel itself does not move.
- **Pipelines are worth little in cost and much in location.** Without pipelines and without storage the system is only 0.6% (195 million EUR) dearer, because the iron can be reduced where hydrogen is cheap and shipped as HBI (19.6 Mt); without hydrogen at all the steel moves 19.8 Mt to regions with CCS capacity and CO2 emissions are three times higher (19.1 against 5.8 Mt).
- **Neither pure pathway is cheaper than the mixed one**: hydrogen only costs 3.7% and CCS only 3.9% more in 2050 (1.3 billion EUR each); CCS-only emits 19.1 Mt because the capture rate of reforming and gas DRI is below 100% (stated in the unit data).
- **CCS bridges 2040.** In 2040 the cheapest system is gas DRI with CCS for 24.7 Mt of steel and hydrogen DRI for 19.8 Mt (HBI route); capture reaches 35 Mt of CO2 of the assumed 85 Mt capacity.

## Storage between seasons (`results/pathway_summary.csv`, `results/storage_sensitivity_no_pipelines_2050.csv`)
The renewable potential of each region is split into April to September and October to March by the region's own share of the 2023 weather year (the winter share is the `share_winter` column of `results/lcoh_by_region.csv`), hydrogen demand is the same in both seasons, and an optional store moves hydrogen between the seasons at 8 EUR per MWh with regional capacities (0 to 20 TWh a year). **Cost and capacity of the store are assumptions** (salt cavern order of magnitude, no source).
- **With pipelines, storage has no value.** The all-options system costs 33,955 million EUR in 2050 with or without storage (the seasonal split itself costs about 2 million EUR over the annual model): presumably because regions with winter-rich wind and summer-rich solar exchange hydrogen by pipeline instead (the mechanism was not tested separately).
- **Without pipelines storage is worth 54 million EUR a year (0.16% of the system cost) and moves 1.7 TWh between seasons.** It disappears when the store costs 50 EUR per MWh and grows to 65 million EUR at 2 EUR per MWh; the capacity of the stores (half to twice the assumed values) does not bind. Even with storage the system without pipelines stays 141 million EUR above the system with pipelines: pipelines and storage are partial substitutes, and pipelines are the stronger one in this model.

## Benchmark with real facilities (EEA industrial reporting database, E-PRTR, version 15 of December 2025; `scripts/build_regions_from_eprtr.py`, `data/regional_production_eprtr.csv`, `data/eprtr_facilities_used.csv`)
Facility-level CO2 releases of 2022 with coordinates: 41 facilities with Annex I activity 2(b) (pig iron and steel) in the nine hub regions (within 700 km of a hub, each plant to the nearest hub), 74 of 82 Mt CO2 of all reporting countries. Steel production is not reported; dividing CO2 by the 1.9 t per tonne of the blast furnace in the model gives an implied production that is a **lower bound** (electric arc plants emit less per tonne, facilities under the reporting threshold are missing).

| Hub region | Steel in the model (Mt, stylised) | Steel implied by E-PRTR CO2 (Mt) |
|---|---:|---:|
| NO-West | 0.3 | 0.9 (2 plants) |
| SE-North | 3.0 | 2.3 (3 plants) |
| DE-North | 5.0 | 6.2 (6 plants) |
| DE-West | 12.0 | 4.2 (9 plants) |
| NL-Rotterdam | 6.0 | 5.0 (3 plants) |
| FR-North | 5.0 | 0.0 (0 plants) |
| PL-Silesia | 6.0 | 13.5 (9 plants) |
| IT-North | 10.0 | 4.2 (7 plants) |
| ES-Iberia | 12.0 | 2.6 (2 plants) |

Implied steel in the nine hubs is 39 Mt against 59 Mt in the model, with large regional differences (no plant at all in the French hub; I did not check why, but it means this activity is not a complete register of steel plants; the Polish hub collects plants from the Czech Republic, Slovakia, Austria and Romania because every plant goes to its nearest hub). For ammonia the database is not usable: only three facilities under activity 4(b)(i) are fertiliser producers by name (Yara France, Yara Brunsbüttel, LAT Nitrogen France; 1.7 Mt CO2, about 1 Mt of ammonia at 1.8 t per tonne against 6.9 Mt in the model); the other 4(b)(i) facilities are merchant hydrogen and industrial gas plants (steam methane reforming, 0.1 to 0.7 Mt CO2 each). **The model therefore keeps the stylised production**; the benchmark shows what open facility data can and cannot give, and it lists the merchant hydrogen plants that a hydrogen study would have to replace first.

## Limits
- Stylised regions and production, assumed unit data and costs, one weather year, one site per region; the regions are not the EU ETS installation registry, so location results show mechanisms, not plants. Norway is represented by one region (Porsgrunn area coordinates) with stylised production and no Norwegian storage; E-PRTR lists two Norwegian steel plants in that hub (0.9 Mt implied), which the model does not use.
- No investment dynamics, no stranded assets (blast furnaces are free of capital cost); storage only as a seasonal move between two seasons with assumed cost and capacity (no hourly operation, no storage losses, no cavern siting); hydrogen supply is a cost curve with a potential, not a system model. Pipelines have a linear cost without capacity limits; no electricity grid constraints, no free allocation, no policy beyond the CO2 price.
- Only steel and ammonia are modelled.

## Run
```
pip install -e .
python scripts/download_weather.py
python scripts/run_all.py
pytest
```
`docs/research_plan.pdf` is the one-page research plan for the NTNU application (separate document).
