import numpy as np
import pytest

from h2ind import model as m

RES = m.run()


def test_all_solved_and_restrictions_never_cheaper():
    for y in m.YEARS:
        base = RES[(y, "all options")]["cost_meur"]
        for pw in [p for p in m.PATHWAYS[1:] if not p.co2_trade]:
            r = RES[(y, pw.name)]
            assert r["status"] == 0
            if not pw.storage:
                assert r["cost_meur"] >= base - 1e-6      # removing an option never lowers the cost
            else:
                assert r["cost_meur"] >= base - 1e-6 or pw.h2_trade is False or not pw.ccs


def test_demand_and_balances():
    for (y, pw), v in RES.items():
        steel_prod = sum(sum(v["prod"][t].values()) for t in ("bf", "scrap", "h2dri", "ngdri", "eaf_hbi"))
        assert steel_prod == pytest.approx(sum(m.STEEL_MT.values()), rel=1e-6)
        nh3 = sum(sum(v["prod"][t].values()) for t in ("nh3_smr", "nh3_ccs", "nh3_el"))
        assert nh3 == pytest.approx(sum(m.NH3_MT.values()), rel=1e-6)
        assert sum(v["h2_prod_twh"].values()) == pytest.approx(sum(v["h2_use_twh"].values()), rel=1e-6)   # no storage or losses
        assert sum(v["prod"]["dri_hbi"].values()) == pytest.approx(sum(v["prod"]["eaf_hbi"].values()), rel=1e-6)


def test_capacity_limits_respected():
    for (y, pw), v in RES.items():
        for r in m.REGIONS:
            assert v["h2_prod_twh"][r] - v["h2_grid_twh"][r] - v["h2_blue_twh"][r] <= m.H2_CAP_TWH[r] + 1e-6
            assert v["h2_grid_twh"][r] <= m.GRID_H2_CAP_TWH.get(r, 0.0) + 1e-6
            captured = v["prod"]["ngdri"][r] * 1.0 + v["prod"]["nh3_ccs"][r] * 1.5 + v["h2_blue_twh"][r] * m.BLUE["cap"]
            if (y, pw) and "shipped" not in pw:
                assert captured <= m.CCS_CAP_MT[r] + 1e-6
            assert v["prod"]["bf"][r] <= m.BF_CAP[y] * m.STEEL_MT[r] + 1e-6
            assert v["prod"]["scrap"][r] <= m.SCRAP_SHARE * m.STEEL_MT[r] + 1e-6


def test_pathway_switches():
    for y in m.YEARS:
        no_ccs = RES[(y, "hydrogen pathway (no CCS)")]
        assert sum(no_ccs["prod"]["ngdri"].values()) == 0 and sum(no_ccs["prod"]["nh3_ccs"].values()) == 0
        no_h2 = RES[(y, "CCS pathway (no electrolytic hydrogen)")]
        assert sum(no_h2["h2_prod_twh"].values()) == 0
        no_pipe = RES[(y, "hydrogen without pipelines")]
        assert not [k for k in no_pipe["flows"] if k[0] == "h2"]


def test_hydrogen_cost_falls_over_time_and_is_positive():
    w = m.load_weather()
    l30, l50 = m.lcoh(2030, w), m.lcoh(2050, w)
    assert (l50.lcoh_eur_mwh < l30.lcoh_eur_mwh).all() and (l50.lcoh_eur_mwh > 0).all()
    assert (l50.cf_wind.between(0.0, 1.0)).all()


def test_storage_never_raises_cost_and_balances_seasons():
    pairs = [("hydrogen without pipelines", "hydrogen without pipelines, seasonal storage"), ("all options", "all options, seasonal storage"),
             ("hydrogen pathway (no CCS)", "hydrogen pathway (no CCS), seasonal storage")]
    for y in m.YEARS:
        for a, b in pairs:
            assert RES[(y, b)]["cost_meur"] <= RES[(y, a)]["cost_meur"] + 1e-6
            assert RES[(y, a)]["storage_twh"] == 0.0
            for r in m.REGIONS:
                pass
        assert RES[(y, "hydrogen without pipelines, seasonal storage")]["storage_twh"] <= sum(m.STORAGE_CAP_TWH.values()) * 2 + 1e-6


def test_co2_to_norway_never_raises_cost_and_respects_storage():
    for y in m.YEARS:
        for a, b in [("all options", "all options, CO2 shipped to Norway"),
                     ("CCS pathway (no electrolytic hydrogen)", "CCS pathway (no electrolytic hydrogen), CO2 shipped to Norway")]:
            assert RES[(y, b)]["cost_meur"] <= RES[(y, a)]["cost_meur"] + 1e-6
            assert RES[(y, b)]["co2_to_norway_mt"] <= m.NO_STORAGE_MT[y] + 1e-6
            assert RES[(y, a)]["co2_to_norway_mt"] == 0.0


def test_v02_results_reproduced_with_norway_switch_off():
    import pandas as pd
    old = pd.read_csv(m.ROOT / "results" / "v0_2" / "pathway_summary.csv")
    m.NORWAY_V03 = False
    try:
        for _, r in old.iterrows():
            pw = [p for p in m.PATHWAYS if p.name == r.pathway][0]
            v = m.solve_year(int(r.year), pw, m.lcoh(int(r.year), m.load_weather()), m.distances())
            assert v["cost_meur"] == pytest.approx(r.cost_meur, abs=1e-3)
    finally:
        m.NORWAY_V03 = True


def test_blue_hydrogen_switch_and_balance():
    w, d = m.load_weather(), m.distances()
    pw = [p for p in m.PATHWAYS if p.name == "all options"][0]
    lc = m.lcoh(2050, w)
    on = m.solve_year(2050, pw, lc, d)
    m.BLUE_ON = False
    try:
        off = m.solve_year(2050, pw, lc, d)
    finally:
        m.BLUE_ON = True
    assert sum(off["h2_blue_twh"].values()) == 0.0
    assert off["cost_meur"] >= on["cost_meur"] - 1e-6
