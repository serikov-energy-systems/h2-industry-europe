# Where should steel and ammonia be made in Europe, and how much hydrogen does each pathway need?

Research study: a regional linear programme for steel and ammonia production in nine European regions in 2030, 2040 and 2050 with hydrogen production, pipeline transport and trade of steel, direct reduced iron (HBI) and ammonia. Four pathways switch options on and off: all options, a hydrogen pathway without CCS, a CCS pathway without electrolytic hydrogen and hydrogen without pipelines.

**What is real and what is assumed.** The hydrogen cost of each region is computed from hourly 2023 wind speed at 100 m and solar radiation (Open-Meteo archive, ERA5-based), a cubic power curve and an electrolyser sized to minimise cost. **Everything else is an assumption** (`data/sources.csv`): the nine regions are a stylised subset of Europe, not the EU ETS installation registry (it could not be obtained automatically); regional steel (59 Mt) and ammonia (6.9 Mt) production, unit energy needs, costs, CCS capacities, renewable potentials, the CO2 price path (100, 150, 200 EUR/t), gas and electricity prices and the phase-out of blast furnaces are illustrative. Static annual cost per year, no investment dynamics, no sectors beyond steel and ammonia. The study shows how pathways differ in structure, hydrogen demand and location, not where plants will be built.

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
| All options | 33,953 | 5.8 | 68.6 | 44 Mt hydrogen DRI with electric arc furnaces, 15 Mt scrap | all reforming with CCS | 42 TWh hydrogen by pipeline, no steel or HBI traded |
| Hydrogen, no CCS | 35,227 (+3.7%) | 16.1 | 68.9 | as above | reforming without CCS | 42 TWh hydrogen |
| CCS, no electrolytic hydrogen | 35,272 (+3.9%) | 19.1 | 0 | 44.5 Mt gas DRI with CCS | reforming with CCS | 19.8 Mt of steel moved to regions with CCS |
| Hydrogen without pipelines | 34,082 (+0.4%) | 7.4 | 60.6 | 39 Mt hydrogen DRI, 5 Mt gas DRI with CCS | reforming with CCS | 21.8 Mt of HBI shipped, no hydrogen pipelines |

- **Hydrogen demand follows the steel route.** The steel in these regions needs 69 TWh of hydrogen in 2050 (1.67 MWh per tonne in the electric arc route), 29 TWh in 2040 and nothing in 2030, when blast furnaces (80% of capacity) and scrap supply the steel and reforming with CCS the ammonia. Electrolytic ammonia is never chosen: at 200 EUR/t CO2 reforming with CCS is cheaper than 5.9 MWh of hydrogen per tonne at 104 to 119 EUR/MWh, so the limited cheap hydrogen goes to steel first.
- **Hydrogen is produced where it is cheap and piped to the steel regions.** In 2050 hydrogen comes from the Netherlands (15 TWh, at the assumed potential), northern France (20 TWh, at the potential) and Iberia (34 TWh of 80), and 42 TWh moves by pipeline over a transport work of 45 TWh x 1,000 km, to Germany, Poland, Italy and Sweden. Steel itself does not move.
- **Pipelines are worth little in cost and much in location.** Without pipelines the system is only 0.4% (129 million EUR) dearer, because the iron can be reduced where hydrogen is cheap and shipped as HBI (21.8 Mt); without hydrogen at all the steel moves 19.8 Mt to regions with CCS capacity and CO2 emissions are three times higher (19.1 against 5.8 Mt).
- **Neither pure pathway is cheaper than the mixed one**: hydrogen only costs 3.7% and CCS only 3.9% more in 2050 (1.3 billion EUR each); CCS-only emits 19.1 Mt because the capture rate of reforming and gas DRI is below 100% (stated in the unit data).
- **CCS bridges 2040.** In 2040 the cheapest system is gas DRI with CCS for 26 Mt of steel and hydrogen DRI for 19 Mt; capture reaches 36 Mt of CO2 of the assumed 85 Mt capacity.

## Limits
- Stylised regions and production, assumed unit data and costs, one weather year, one site per region; the regions are not the EU ETS installation registry, so location results show mechanisms, not plants. Norway is represented by one region (Porsgrunn area coordinates) with no real production data.
- No investment dynamics, no stranded assets (blast furnaces are free of capital cost), no storage and no hourly operation; hydrogen supply is a cost curve with a potential, not a system model. Pipelines have a linear cost without capacity limits; no electricity grid constraints, no free allocation, no policy beyond the CO2 price.
- Only steel and ammonia are modelled.

## Run
```
pip install -e .
python scripts/download_weather.py
python scripts/run_all.py
pytest
```
`docs/research_plan.pdf` is the one-page research plan for the NTNU application (separate document).
