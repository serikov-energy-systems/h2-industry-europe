"""Regional optimisation of steel and ammonia production, hydrogen supply and trade in Europe, 2030, 2040 and 2050.

The hydrogen cost per region comes from hourly 2023 wind and solar data (Open-Meteo, ERA5-based). Production volumes by
region, unit energy needs, costs, CCS capacities and the CO2 price are ASSUMPTIONS (see data/sources.csv): the nine regions
are a stylised subset of Europe, not the EU ETS installation registry. The study shows how pathways differ, not where
specific plants will be.

One linear programme per year (static, annualised costs) with two seasons for hydrogen (April to September and October to March): the
renewable potential of a region is split by its own seasonal share of the weather year, the hydrogen demand is the same in both seasons,
and an optional seasonal store (assumed cost and regional capacity) moves hydrogen between the seasons. Products: steel, HBI (direct reduced iron, tradable), ammonia;
energy carrier: hydrogen (pipeline between regions). Pathways are scenarios that switch options off.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

ROOT = Path(__file__).resolve().parents[2]
REGIONS = ["NO-West", "SE-North", "DE-North", "DE-West", "NL-Rotterdam", "FR-North", "PL-Silesia", "IT-North", "ES-Iberia"]
YEARS = [2030, 2040, 2050]
ANN = 0.08 / (1 - 1.08 ** -20)

# assumed regional data (Mt per year; stylised)
STEEL_MT = dict(zip(REGIONS, [0.3, 3.0, 5.0, 12.0, 6.0, 5.0, 6.0, 10.0, 12.0]))
NH3_MT = dict(zip(REGIONS, [0.5, 0.0, 0.6, 0.6, 2.0, 0.5, 1.8, 0.4, 0.5]))
CCS_CAP_MT = dict(zip(REGIONS, [20.0, 0.0, 10.0, 5.0, 25.0, 15.0, 0.0, 10.0, 0.0]))     # Mt CO2 per year
H2_CAP_TWH = dict(zip(REGIONS, [15.0, 40.0, 30.0, 10.0, 15.0, 20.0, 20.0, 15.0, 80.0]))  # renewable potential, TWh H2
SCRAP_SHARE = 0.25                         # scrap-EAF at most this share of regional steel demand (assumed)
BF_CAP = {2030: 0.8, 2040: 0.4, 2050: 0.1}  # blast furnace capacity left, share of today's steel demand (assumed)

CO2_PRICE = {2030: 100.0, 2040: 150.0, 2050: 200.0}
GAS = {2030: 40.0, 2040: 35.0, 2050: 35.0}          # EUR/MWh
ELEC = {2030: 70.0, 2040: 60.0, 2050: 55.0}         # EUR/MWh for non-hydrogen electricity (assumed, equal in all regions)
CAPEX = {  # EUR/kW
    2030: dict(wind=1300.0, solar=600.0, el=800.0), 2040: dict(wind=1200.0, solar=500.0, el=600.0),
    2050: dict(wind=1100.0, solar=450.0, el=500.0)}
OM = 0.025
EL_EFF = 0.65
STORAGE_COST = 8.0          # EUR per MWh of hydrogen moved between seasons through a store (assumed; salt cavern order of magnitude)
STORAGE_CAP_TWH = dict(zip(REGIONS, [0.0, 0.5, 20.0, 5.0, 10.0, 5.0, 5.0, 3.0, 5.0]))   # TWh movable per year (assumed)
H2_TRANSPORT = 4.5          # EUR/MWh H2 per 1000 km by pipeline (assumed)
SHIP = {"steel": 25.0, "hbi": 12.0, "nh3": 8.0}   # EUR/t per 1000 km (assumed)

# unit data per tonne of product: (cost EUR/t excluding listed energy, H2 MWh, electricity MWh, gas MWh, CO2 emitted t, CO2 captured t)
TECH = {
    "bf":      dict(cost=330.0, h2=0.0, el=0.0, gas=0.0, co2=1.9, cap=0.0),
    "scrap":   dict(cost=300.0, h2=0.0, el=0.55, gas=0.0, co2=0.1, cap=0.0),
    "h2dri":   dict(cost=280.0, h2=1.67, el=3.5, gas=0.0, co2=0.05, cap=0.0),
    "ngdri":   dict(cost=300.0, h2=0.0, el=0.9, gas=2.8, co2=0.35, cap=1.0, ccs=60.0),
    "dri_hbi": dict(cost=170.0, h2=1.55, el=0.3, gas=0.0, co2=0.0, cap=0.0),     # hydrogen DRI producing HBI
    "eaf_hbi": dict(cost=150.0, h2=0.0, el=0.6, gas=0.0, co2=0.05, cap=0.0),
    "nh3_smr": dict(cost=120.0, h2=0.0, el=0.0, gas=7.8, co2=1.8, cap=0.0),
    "nh3_ccs": dict(cost=120.0, h2=0.0, el=0.1, gas=8.3, co2=0.3, cap=1.5, ccs=60.0),
    "nh3_el":  dict(cost=110.0, h2=5.93, el=0.6, gas=0.0, co2=0.0, cap=0.0),
}


def load_weather() -> dict:
    return json.loads((ROOT / "data" / "raw" / "weather_2023.json").read_text())


def lcoh(year: int, weather: dict) -> pd.DataFrame:
    """Hydrogen cost (EUR/MWh H2) per region: wind plus solar (equal capacities) feeding an electrolyser, ratio of
    electrolyser to renewable capacity chosen to minimise the cost. Power curve: cubic between 3 and 12 m/s, rated to 25 m/s."""
    c = CAPEX[year]
    rows = []
    for r in REGIONS:
        w = np.array(weather[r]["wind_speed_100m"], float)
        g = np.array(weather[r]["shortwave_radiation"], float)
        cfw = np.where(w < 3, 0, np.where(w < 12, ((w - 3) / 9) ** 3, np.where(w < 25, 1.0, 0.0)))
        cfs = np.clip(g / 1000.0 * 0.85, 0, 1)
        re = 0.5 * (cfw + cfs)                              # per kW of the 50/50 mix
        best = None
        for ratio in np.linspace(0.2, 1.0, 17):
            h2_mwh = np.minimum(re, ratio).sum() * EL_EFF / 1000.0   # MWh H2 per kW of renewables
            cost = (ANN + OM) * (0.5 * c["wind"] + 0.5 * c["solar"] + ratio * c["el"])    # EUR per kW renewables per year
            v = cost / h2_mwh
            best = v if best is None or v < best else best
        summer = np.zeros(len(re), bool)
        summer[2160:6552] = True                                    # April to September of a 365-day year
        sh_s = float(re[summer].sum() / re.sum())
        rows.append({"region": r, "lcoh_eur_mwh": best, "cf_wind": cfw.mean(), "cf_solar": cfs.mean(), "cf_mix": re.mean(),
                     "share_summer": sh_s, "share_winter": 1.0 - sh_s})
    return pd.DataFrame(rows).set_index("region")


def distances() -> pd.DataFrame:
    w = load_weather()
    lat = np.radians([w[r]["lat"] for r in REGIONS]); lon = np.radians([w[r]["lon"] for r in REGIONS])
    d = 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((lat[:, None] - lat[None]) / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None]) * np.sin((lon[:, None] - lon[None]) / 2) ** 2)) * 1.2
    return pd.DataFrame(d, index=REGIONS, columns=REGIONS)


@dataclass(frozen=True)
class Pathway:
    name: str
    ccs: bool = True
    hydrogen: bool = True
    h2_trade: bool = True
    storage: bool = False


PATHWAYS = [Pathway("all options"), Pathway("hydrogen pathway (no CCS)", ccs=False), Pathway("CCS pathway (no electrolytic hydrogen)", hydrogen=False),
            Pathway("hydrogen without pipelines", h2_trade=False),
            Pathway("all options, seasonal storage", storage=True), Pathway("hydrogen pathway (no CCS), seasonal storage", ccs=False, storage=True),
            Pathway("hydrogen without pipelines, seasonal storage", h2_trade=False, storage=True)]


class Builder:
    def __init__(self):
        self.names, self.cost, self.ub = [], [], []
        self.rows = []     # (coef dict, kind, rhs)

    def var(self, name, cost=0.0, ub=np.inf):
        self.names.append(name); self.cost.append(cost); self.ub.append(ub)
        return len(self.names) - 1


def solve_year(year: int, pw: Pathway, lc: pd.DataFrame, dist: pd.DataFrame) -> dict:
    B = Builder()
    R = REGIONS
    idx = {}
    for r in R:
        for t in TECH:
            t_ok = True
            if not pw.ccs and t in ("ngdri", "nh3_ccs"):
                t_ok = False
            if not pw.hydrogen and t in ("h2dri", "dri_hbi", "nh3_el"):
                t_ok = False
            d = TECH[t]
            c = d["cost"] + d["el"] * ELEC[year] + d["gas"] * GAS[year] + d["co2"] * CO2_PRICE[year] + d.get("ccs", 0.0) * d["cap"]
            idx[(t, r)] = B.var(f"{t}@{r}", c, np.inf if t_ok else 0.0)
        for si, sname in enumerate(("summer", "winter")):
            share = lc.loc[r, "share_summer" if si == 0 else "share_winter"]
            idx[("h2", r, si)] = B.var(f"h2@{r}:{sname}", lc.loc[r, "lcoh_eur_mwh"], H2_CAP_TWH[r] * 1e6 * share if pw.hydrogen else 0.0)
        sc = STORAGE_CAP_TWH[r] * 1e6 if (pw.storage and pw.hydrogen) else 0.0
        idx[("st_sw", r)] = B.var(f"store summer->winter@{r}", STORAGE_COST, sc)
        idx[("st_ws", r)] = B.var(f"store winter->summer@{r}", STORAGE_COST, sc)
        idx[("co2c", r)] = B.var(f"co2cap@{r}", 0.0, CCS_CAP_MT[r] * 1e6 if pw.ccs else 0.0)
    flows = {}
    for p in ("steel", "hbi", "nh3", "h2"):
        for a in R:
            for b in R:
                if a == b or (p == "h2" and not pw.h2_trade):
                    continue
                c = (H2_TRANSPORT if p == "h2" else SHIP[p]) * dist.loc[a, b] / 1000.0
                if p == "h2":
                    for si in (0, 1):
                        flows[(p, a, b, si)] = B.var(f"{p}:{a}->{b}:{si}", c)
                else:
                    flows[(p, a, b)] = B.var(f"{p}:{a}->{b}", c)
    n = len(B.names)
    A_eq, b_eq, A_ub, b_ub = [], [], [], []

    def row(coefs, rhs, eq=True):
        (A_eq if eq else A_ub).append(coefs); (b_eq if eq else b_ub).append(rhs)

    for r in R:
        s = {idx[(t, r)]: 1.0 for t in ("bf", "scrap", "h2dri", "ngdri", "eaf_hbi")}
        for a in R:
            if a != r:
                s[flows[("steel", a, r)]] = s.get(flows[("steel", a, r)], 0) + 1.0
                s[flows[("steel", r, a)]] = s.get(flows[("steel", r, a)], 0) - 1.0
        row(s, STEEL_MT[r] * 1e6)
        hb = {idx[("dri_hbi", r)]: 1.0, idx[("eaf_hbi", r)]: -1.0}
        for a in R:
            if a != r:
                hb[flows[("hbi", a, r)]] = 1.0; hb[flows[("hbi", r, a)]] = -1.0
        row(hb, 0.0)
        nh = {idx[(t, r)]: 1.0 for t in ("nh3_smr", "nh3_ccs", "nh3_el")}
        for a in R:
            if a != r:
                nh[flows[("nh3", a, r)]] = 1.0; nh[flows[("nh3", r, a)]] = -1.0
        row(nh, NH3_MT[r] * 1e6)
        for si in (0, 1):      # hydrogen balance per season: half of the annual use in each season
            h = {idx[("h2", r, si)]: 1.0}
            for t in ("h2dri", "dri_hbi", "nh3_el"):
                h[idx[(t, r)]] = -0.5 * TECH[t]["h2"]
            for a in R:
                if a != r and pw.h2_trade:
                    h[flows[("h2", a, r, si)]] = 1.0; h[flows[("h2", r, a, si)]] = -1.0
            sgn = 1.0 if si == 1 else -1.0       # summer -> winter: leaves the summer balance, enters the winter balance
            h[idx[("st_sw", r)]] = sgn
            h[idx[("st_ws", r)]] = -sgn
            row(h, 0.0)
        row({idx[("bf", r)]: 1.0}, BF_CAP[year] * STEEL_MT[r] * 1e6, eq=False)
        row({idx[("scrap", r)]: 1.0}, SCRAP_SHARE * STEEL_MT[r] * 1e6, eq=False)
        row({idx[("ngdri", r)]: TECH["ngdri"]["cap"], idx[("nh3_ccs", r)]: TECH["nh3_ccs"]["cap"], idx[("co2c", r)]: -1.0}, 0.0, eq=False)
    c = np.array(B.cost); ub = np.array(B.ub)
    def mat(rows_):
        M = lil_matrix((len(rows_), n))
        for i, d in enumerate(rows_):
            for j, v in d.items():
                M[i, j] = v
        return M.tocsr()
    res = linprog(c, A_eq=mat(A_eq), b_eq=b_eq, A_ub=mat(A_ub), b_ub=b_ub, bounds=list(zip(np.zeros(n), ub)), method="highs")
    if res.status != 0:
        return {"status": res.status, "message": res.message}
    x = res.x
    prod = {t: {r: x[idx[(t, r)]] / 1e6 for r in R} for t in TECH}
    h2_use = {r: sum(TECH[t]["h2"] * x[idx[(t, r)]] for t in ("h2dri", "dri_hbi", "nh3_el")) / 1e6 for r in R}   # TWh
    h2_prod = {r: (x[idx[("h2", r, 0)]] + x[idx[("h2", r, 1)]]) / 1e6 for r in R}
    storage_twh = sum(x[idx[(k, r)]] for k in ("st_sw", "st_ws") for r in R) / 1e6
    co2 = sum((TECH[t]["co2"]) * x[idx[(t, r)]] for t in TECH for r in R) / 1e6   # Mt emitted
    flows_out = {}
    for k, v in flows.items():
        kk = k[:3]
        flows_out[kk] = flows_out.get(kk, 0.0) + x[v]
    flows_out = {k: v for k, v in flows_out.items() if v > 1.0}
    return {"status": 0, "cost_meur": res.fun / 1e6, "co2_mt": co2, "prod": prod, "h2_use_twh": h2_use, "h2_prod_twh": h2_prod,
            "flows": flows_out, "storage_twh": storage_twh, "captured_mt": sum(x[idx[("co2c", r)]] for r in R) / 1e6}


def run() -> dict:
    w = load_weather()
    dist = distances()
    out = {}
    for y in YEARS:
        lc = lcoh(y, w)
        for pw in PATHWAYS:
            out[(y, pw.name)] = solve_year(y, pw, lc, dist)
    return out
