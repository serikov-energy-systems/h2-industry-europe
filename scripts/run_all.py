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
                 "h2_pipeline_twh_1000km": h2km, "captured_mt": tot["ngdri"] * m.TECH["ngdri"]["cap"] + tot["nh3_ccs"] * m.TECH["nh3_ccs"]["cap"], **{f"{t}_mt": x for t, x in tot.items()}})
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
