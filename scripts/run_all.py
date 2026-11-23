"""Run all years and pathways; write result tables."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from h2ind import model as m

RES = ROOT / "results"
RES.mkdir(exist_ok=True)
res = m.run()
w = m.load_weather()
lc = pd.concat({y: m.lcoh(y, w) for y in m.YEARS}, names=["year"]).reset_index()
lc.to_csv(RES / "lcoh_by_region.csv", index=False)
summ, detail, flows = [], [], []
for (y, pw), v in res.items():
    tot = {t: sum(d.values()) for t, d in v["prod"].items()}
    steel = tot["bf"] + tot["scrap"] + tot["h2dri"] + tot["ngdri"] + tot["eaf_hbi"]
    traded = {p: sum(x for (pp, a, b), x in v["flows"].items() if pp == p) / 1e6 for p in ("steel", "hbi", "nh3", "h2")}
    h2km = sum(x * m.distances().loc[a, b] for (pp, a, b), x in v["flows"].items() if pp == "h2") / 1e6 / 1000.0
    summ.append({"year": y, "pathway": pw, "cost_meur": v["cost_meur"], "co2_mt": v["co2_mt"],
                 "h2_use_twh": sum(v["h2_use_twh"].values()), "steel_mt": steel, "traded_steel_mt": traded["steel"],
                 "traded_hbi_mt": traded["hbi"], "traded_nh3_mt": traded["nh3"], "h2_pipeline_twh": traded["h2"],
                 "h2_pipeline_twh_1000km": h2km, "storage_twh": v.get("storage_twh", 0.0), "captured_mt": tot["ngdri"] * m.TECH["ngdri"]["cap"] + tot["nh3_ccs"] * m.TECH["nh3_ccs"]["cap"], **{f"{t}_mt": x for t, x in tot.items()}})
    for r in m.REGIONS:
        detail.append({"year": y, "pathway": pw, "region": r, "h2_prod_twh": v["h2_prod_twh"][r], "h2_use_twh": v["h2_use_twh"][r],
                       "steel_demand_mt": m.STEEL_MT[r],
                       **{f"{t}_mt": v["prod"][t][r] for t in v["prod"]}})
    for (p, a, b), x in v["flows"].items():
        flows.append({"year": y, "pathway": pw, "product": p, "from": a, "to": b, "flow": x / 1e6 if p != "h2" else x / 1e6})
pd.DataFrame(summ).to_csv(RES / "pathway_summary.csv", index=False)
pd.DataFrame(detail).to_csv(RES / "regional_detail.csv", index=False)
pd.DataFrame(flows).to_csv(RES / "flows.csv", index=False)
print(pd.DataFrame(summ).round(1).to_string())


# sensitivity of the value of seasonal storage in the system without pipelines (2050): storage cost and capacity multiples
import dataclasses  # noqa: E402
rows = []
w0 = m.load_weather()
lc50 = m.lcoh(2050, w0)
dist = m.distances()
base_cap = dict(m.STORAGE_CAP_TWH)
nopipe = [p for p in m.PATHWAYS if p.name == "hydrogen without pipelines"][0]
nopipe_st = dataclasses.replace(nopipe, storage=True)
ref = m.solve_year(2050, nopipe, lc50, dist)["cost_meur"]
allopt = [p for p in m.PATHWAYS if p.name == "all options"][0]
ref_all = m.solve_year(2050, allopt, lc50, dist)["cost_meur"]
for cost in (2.0, 8.0, 20.0, 50.0):
    for capx in (0.5, 1.0, 2.0):
        m.STORAGE_COST = cost
        m.STORAGE_CAP_TWH.update({k: v * capx for k, v in base_cap.items()})
        v = m.solve_year(2050, nopipe_st, lc50, dist)
        rows.append({"storage_cost_eur_mwh": cost, "capacity_multiple": capx, "cost_meur": v["cost_meur"], "saving_vs_no_storage_meur": ref - v["cost_meur"],
                     "saving_pct_of_system_cost": 100 * (ref - v["cost_meur"]) / ref, "storage_moved_twh": v["storage_twh"],
                     "gap_to_pipelines_meur": v["cost_meur"] - ref_all})
        m.STORAGE_CAP_TWH.update(base_cap)
m.STORAGE_COST = 8.0
pd.DataFrame(rows).to_csv(RES / "storage_sensitivity_no_pipelines_2050.csv", index=False)
print(pd.DataFrame(rows).round(2).to_string())
