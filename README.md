# Where should steel and ammonia be made in Europe, and how much hydrogen does each pathway need?

Research study: a regional linear programme for steel and ammonia production in nine European regions in 2030, 2040 and 2050 with hydrogen production, pipeline transport and trade of steel, direct reduced iron (HBI) and ammonia. Four pathways switch options on and off: all options, a hydrogen pathway without CCS, a CCS pathway without electrolytic hydrogen and hydrogen without pipelines. Hydrogen is balanced in two seasons (April to September and October to March) with the renewable potential of each region split by its own seasonal share of the weather year, and a seasonal store can be added to three of the pathways.

**What is real and what is assumed.** The hydrogen cost of each region is computed from hourly 2023 wind speed at 100 m and solar radiation (Open-Meteo archive, ERA5-based), a cubic power curve and an electrolyser sized to minimise cost. **Everything else is an assumption** (`data/sources.csv`): the nine regions are a stylised subset of Europe, not the EU ETS installation registry (it could not be obtained automatically; the real facility data of the EEA industrial reporting database are used only as a benchmark, see below); regional steel (59 Mt) and ammonia (6.9 Mt) production, the storage cost (8 EUR per MWh moved) and regional storage capacities, unit energy needs, costs, CCS capacities, renewable potentials, the CO2 price path (100, 150, 200 EUR/t), gas and electricity prices and the phase-out of blast furnaces are illustrative. Static annual cost per year, no investment dynamics, no sectors beyond steel and ammonia. The study shows how pathways differ in structure, hydrogen demand and location, not where plants will be built.

**Version note.** The tables from "Hydrogen cost" to "Benchmark with real facilities" are the v0.2 results (copies in `results/v0_2/`); the files in `results/` now contain v0.3 (Norway data, hydrogen from gas with CCS, CO2 shipping), which changes the all-options case: see the v0.3 section.

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

## v0.3: Norway and the three routes (electrons, molecules, CCS)
**Question.** What role does Norway play in European industrial decarbonisation: producer of hydrogen, exporter of hydrogen, ammonia and iron, or host of CO2 storage?

**What is new.** (1) Norwegian electricity is priced from data: the mean ENTSO-E day-ahead price of zone NO2 for 2023-2025 is 65.8 EUR/MWh (NO1 57.9), against the assumed 55-70 elsewhere (`data/no_prices.json`). (2) Hydrogen from hydropower grid electricity in NO-West, limited to 5 TWh of hydrogen a year (assumed surplus, 8,000 full-load hours). (3) Hydrogen from natural gas reforming with CCS in every region (assumed: 15 EUR/MWh of hydrogen without gas and CO2, 1.3 MWh of gas per MWh of hydrogen, 90% capture, 60 EUR/t for transport and storage). (4) Captured CO2 can be shipped to storage in NO-West (15 EUR/t per 1,000 km assumed); the storage available to imports is 5 Mt a year in 2030 (Northern Lights phase 1 and 2: 1.5 Mt a year in operation and at least 5 Mt from 2028, operator information) and an assumed 20 Mt in 2040 and 2050. (5) The 65 Norwegian facilities with CO2 reporting in the EEA industrial reporting database (latest year for Norway: 2017, 24.7 Mt in total including offshore platforms) are in `data/norway_eprtr_2017.csv`; the Norwegian region itself stays stylised. Setting `NORWAY_V03 = False` reproduces the v0.2 results exactly (test); the v0.2 tables are in `results/v0_2/`.

**Results (`results/norway_*.csv`, 2050 unless stated).**
- **The route depends on the price of gas and of CO2 storage, not on Norway.** With reforming plus CCS allowed, all 68.9 TWh of hydrogen for steel and ammonia come from gas with CCS at the base assumptions (gas 35 EUR/MWh, 60 EUR/t) and the system costs 31,620 million EUR; without it, 63.9 TWh come from renewable electricity and 5 TWh from the Norwegian grid, and the system costs 33,889 million EUR (+7.2%). The switch is sharp: with gas 50% dearer (52.5 EUR/MWh) and storage at 120 EUR/t the molecule route supplies 18 TWh, at 180 EUR/t none; with gas 2.5 times dearer electrolysis supplies everything (`norway_blue_vs_electrolysis.csv`). Upstream methane emissions of gas are not counted, which favours the gas route; the capture rate is assumed.
- **In 2030 the cheaper blue hydrogen already makes hydrogen steel competitive:** 44.5 TWh of hydrogen and 28.7 Mt of iron through the hydrogen route in the all-options case (v0.2: none), CO2 36 Mt against 88 Mt. This rests on the assumed availability of reforming plants with CCS in 2030.
- **Norway as an exporter.** NO-West produces 3.8 TWh of hydrogen from gas with CCS in the all-options case and exports 3.5 TWh by pipeline; without CCS it uses its full 5 TWh of hydropower hydrogen and exports 4.65 TWh; without pipelines it ships 2.25 Mt of iron (HBI) instead. In the pure CCS pathway Norway exports 2.25 Mt of steel made with gas and CCS instead of hydrogen. These are small flows against 69 TWh of demand: Norway does not decide the pathway.
- **Norway as a storage host.** Shipping CO2 to Norway saves 4 million EUR a year in the all-options case (0.8 Mt stored) and 56 million EUR in the CCS pathway (6.75 Mt); the saving falls to zero when shipping costs 40 EUR/t per 1,000 km and rises to 57 million EUR at 5 (`norway_sensitivity.csv`). The effect is small because the other regions are assumed to have their own storage.
- **Ammonia benchmark.** Yara Porsgrunn reports 0.49 Mt of CO2 in 2017, which at 1.8 t of CO2 per tonne of ammonia would be at most 0.27 Mt of ammonia (the stylised 0.5 Mt is higher); the system results with 0.27 Mt are 0.4% cheaper in the all-options case (`norway_ammonia_benchmark.csv`).

**Limits.** NO-West is one stylised region with the weather of an inland site (wind and solar hydrogen there costs 248 to 319 EUR/MWh); real Norwegian plants enter only as a benchmark. All plant, CCS and transport costs are assumed order-of-magnitude values; hydropower surplus and grid fees are not modelled; one static year per period; no hourly operation; no clearance of the pipeline route between Norway and the continent. Not a Norwegian or European policy forecast.

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
