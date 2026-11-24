"""v0.3: Norway in the European pathways. Role of NO-West as producer of hydrogen, exporter of hydrogen, ammonia and HBI, and CO2 storage host.
Run after run_all.py. Writes results/norway_*.csv and data/norway_eprtr_2017.csv."""
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from h2ind import model as m

RES = ROOT / "results"
DATA = ROOT / "data"
EPRTR = Path(r"C:\Users\user\z_data\z4_eprtr\F1_4_Air_Releases_Facilities.csv")

# (1) real Norwegian facilities, E-PRTR 2017 (latest year in the EEA file for Norway)
if EPRTR.exists():
    f = pd.read_csv(EPRTR, low_memory=False)
    n = f[(f.countryName == "Norway") & (f.reportingYear == 2017) & (f.Pollutant == "Carbon dioxide (CO2)")].copy()
    n["co2_mt"] = n.Releases / 1e9            # kg to Mt
    n = n.sort_values("co2_mt", ascending=False)[["facilityName", "city", "EPRTR_SectorName", "EPRTRAnnexIMainActivity", "Longitude", "Latitude", "co2_mt"]]
    n.to_csv(DATA / "norway_eprtr_2017.csv", index=False)

pr = json.loads((DATA / "no_prices.json").read_text()) if (DATA / "no_prices.json").exists() else None
if pr:
    m.ELEC_NO = pr["NO2_mean_2023_2025"]

w = m.load_weather()
dist = m.distances()
lcs = {y: m.lcoh(y, w) for y in m.YEARS}


def norway_row(y, pwname, v, tag):
    ex = {p: sum(x for (pp, a, b), x in v["flows"].items() if pp == p and a == "NO-West") / 1e6 for p in ("h2", "nh3", "hbi", "steel")}
    im = {p: sum(x for (pp, a, b), x in v["flows"].items() if pp == p and b == "NO-West") / 1e6 for p in ("h2", "nh3", "hbi", "steel")}
    r = "NO-West"
    return {"case": tag, "year": y, "pathway": pwname, "cost_meur": v["cost_meur"], "co2_mt": v["co2_mt"],
            "no_h2_twh_total": v["h2_prod_twh"][r], "no_h2_grid_twh": v["h2_grid_twh"][r], "no_h2_blue_twh": v["h2_blue_twh"][r],
            "no_h2_renewable_twh": v["h2_prod_twh"][r] - v["h2_grid_twh"][r] - v["h2_blue_twh"][r], "no_h2_use_twh": v["h2_use_twh"][r],
            "export_h2_twh": ex["h2"], "export_nh3_mt": ex["nh3"], "export_hbi_mt": ex["hbi"], "export_steel_mt": ex["steel"],
            "import_hbi_mt": im["hbi"], "co2_stored_in_norway_from_abroad_mt": v["co2_to_norway_mt"]}


rows = []
for y in m.YEARS:
    for pw in m.PATHWAYS:
        rows.append(norway_row(y, pw.name, m.solve_year(y, pw, lcs[y], dist), "v0.3"))
base = pd.DataFrame(rows)
base.to_csv(RES / "norway_role.csv", index=False)
print(base[base.year == 2050].round(2).to_string())

# (2) comparison with v0.2 (stylised Norway): same pathways, switch off the v0.3 options
m.NORWAY_V03 = False
old = [norway_row(y, pw.name, m.solve_year(y, pw, lcs[y], dist), "v0.2") for y in m.YEARS for pw in m.PATHWAYS if not pw.co2_trade] if False else []
v02 = []
for y in m.YEARS:
    for pw in m.PATHWAYS:
        if pw.co2_trade:
            continue
        v = m.solve_year(y, pw, lcs[y], dist)
        v02.append({"year": y, "pathway": pw.name, "cost_meur_v02": v["cost_meur"], "co2_mt_v02": v["co2_mt"]})
m.NORWAY_V03 = True
cmp_ = pd.DataFrame(v02).merge(base[["year", "pathway", "cost_meur", "co2_mt"]], on=["year", "pathway"])
cmp_["cost_change_meur"] = cmp_.cost_meur - cmp_.cost_meur_v02
cmp_.to_csv(RES / "norway_v02_vs_v03.csv", index=False)

# (3) sensitivities, 2050 and 2040, case "all options, CO2 shipped to Norway"
sens = []
pw_co2 = [p for p in m.PATHWAYS if p.name == "all options, CO2 shipped to Norway"][0]
pw_all = [p for p in m.PATHWAYS if p.name == "all options"][0]
pw_nopipe = [p for p in m.PATHWAYS if p.name == "hydrogen without pipelines"][0]
for y in (2040, 2050):
    for elec in (30.0, m.ELEC_NO, 70.0):
        for cap in (0.0, 5.0, 20.0):
            for ship in (5.0, 15.0, 40.0):
                m.GRID_H2_CAP_TWH["NO-West"] = cap; m.CO2_SHIP = ship
                e0 = m.ELEC_NO; m.ELEC_NO = elec
                v = m.solve_year(y, pw_co2, lcs[y], dist)
                v2 = m.solve_year(y, pw_all, lcs[y], dist)
                m.ELEC_NO = e0
                sens.append({**norway_row(y, pw_co2.name, v, "sens"), "elec_no": elec, "grid_h2_cap_twh": cap, "co2_ship_eur_t_1000km": ship,
                             "saving_vs_all_options_meur": v2["cost_meur"] - v["cost_meur"]})
m.GRID_H2_CAP_TWH["NO-West"] = 5.0; m.CO2_SHIP = 15.0
pd.DataFrame(sens).to_csv(RES / "norway_sensitivity.csv", index=False)

# (4) ammonia in Norway at the level implied by the E-PRTR facility CO2 (Yara Porsgrunn 0.487 Mt CO2 at 1.8 t CO2 per t NH3 = 0.27 Mt, an upper bound of
# the ammonia share because part of the CO2 is process CO2 sold or used for urea)
nh0 = m.NH3_MT["NO-West"]; m.NH3_MT["NO-West"] = 0.27
bench = [norway_row(y, pw.name, m.solve_year(y, pw, lcs[y], dist), "NH3 0.27 Mt") for y in m.YEARS for pw in (pw_all, pw_co2)]
m.NH3_MT["NO-West"] = nh0
pd.DataFrame(bench).to_csv(RES / "norway_ammonia_benchmark.csv", index=False)
# (5) hydrogen from reforming with CCS against electrolysis: all options, 2040 and 2050, gas price and CO2 transport and storage cost (the CCS cost of all
# routes is varied together); blue hydrogen on and off. Upstream methane emissions of gas are not counted, which favours the blue route.
bl = []
gas0 = dict(m.GAS); ccs0 = {k: v.get("ccs") for k, v in m.TECH.items()}; blue_ccs0 = m.BLUE["ccs"]
for y in (2040, 2050):
    for on in (True, False):
        for gmult in (1.0, 1.5, 2.5):
            for ccs in (60.0, 120.0, 180.0):
                m.BLUE_ON = on
                m.GAS.update({k: v * gmult for k, v in gas0.items()})
                m.BLUE["ccs"] = ccs
                for k in ("ngdri", "nh3_ccs"):
                    m.TECH[k]["ccs"] = ccs
                v = m.solve_year(y, pw_all, lcs[y], dist)
                bl.append({"year": y, "blue_hydrogen_allowed": on, "gas_price_multiple": gmult, "gas_eur_mwh": m.GAS[y], "ccs_eur_t": ccs, "cost_meur": v["cost_meur"],
                           "co2_mt": v["co2_mt"], "h2_total_twh": sum(v["h2_prod_twh"].values()), "h2_blue_twh": sum(v["h2_blue_twh"].values()),
                           "h2_grid_twh": sum(v["h2_grid_twh"].values()), "h2_renewable_twh": sum(v["h2_prod_twh"].values()) - sum(v["h2_blue_twh"].values()) - sum(v["h2_grid_twh"].values()),
                           "captured_mt": sum(v["prod"]["ngdri"].values()) * m.TECH["ngdri"]["cap"] + sum(v["prod"]["nh3_ccs"].values()) * m.TECH["nh3_ccs"]["cap"] + sum(v["h2_blue_twh"].values()) * m.BLUE["cap"]})
m.BLUE_ON = True; m.GAS.update(gas0); m.BLUE["ccs"] = blue_ccs0
for k in ("ngdri", "nh3_ccs"):
    m.TECH[k]["ccs"] = ccs0[k]
pd.DataFrame(bl).to_csv(RES / "norway_blue_vs_electrolysis.csv", index=False)
print("done")
