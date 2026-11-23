"""Regional steel and ammonia production from the EEA industrial reporting database (E-PRTR, version 15, release 15 Dec 2025).

Input: F1_4_Air_Releases_Facilities.csv (facility-level releases to air with coordinates), downloaded from the EEA data share (see
data/sources.csv). Steel: facilities with Annex I activity 2(b) (production of pig iron or steel) and CO2 releases in 2022. Ammonia: facilities
with activity 4(b)(i) whose name contains a fertiliser or ammonia producer keyword; the other 4(b)(i) facilities are merchant hydrogen and
industrial gas plants and are listed separately (not ammonia). Production is NOT reported: it is implied by the CO2 release divided by an
ASSUMED intensity (steel 1.9 t CO2 per tonne, the blast furnace value of the model; ammonia 1.8 t per tonne, the reforming value of the model).
Because steel made in electric arc furnaces emits less per tonne and facilities below the E-PRTR threshold are not listed, the implied steel
production is a lower bound of the real one.

Each facility goes to the nearest of the nine hub regions of the model if it lies within RADIUS_KM of the hub (the others are outside the domain).

    python scripts/build_regions_from_eprtr.py <path to F1_4_Air_Releases_Facilities.csv>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "z_data" / "z4_eprtr" / "F1_4_Air_Releases_Facilities.csv"
YEAR = 2022
RADIUS_KM = 700.0
STEEL_INTENSITY = 1.9
NH3_INTENSITY = 1.8
KEYWORDS = ("yara", "azoty", "fertil", "ammon", "nitrogen", "nitrog", "borealis", "oci ", "grande paroisse", "duslo", "achema", "azomures", "petrokemija",
            "agrofert", "sks", "skw", "basf", "ineos", "fertilizer", "kemira", "grupa", "lat nitrogen", "cf fertilisers", "nitrogenmuvek", "nitrogénművek", "ineos")
NAMES_EXCLUDED = ("air liquide", "air products", "linde", "hyco", "messer", "praxair", "dow ", "covestro", "total", "shell", "bp ")

w = json.loads((ROOT / "data" / "raw" / "weather_2023.json").read_text())
hubs = {k: (v["lat"], v["lon"]) for k, v in w.items()}

d = pd.read_csv(SRC, low_memory=False)
d["act"] = d.EPRTRAnnexIMainActivity.fillna("").astype(str)
c = d[(d.Pollutant == "Carbon dioxide (CO2)") & (d.reportingYear == YEAR)].copy()
c["co2_mt"] = c.Releases / 1e9          # releases are in kg
name = c.facilityName.fillna("").str.lower()
steel = c[c.act.str.startswith("2(b)")].copy()
nh3_pool = c[c.act.str.startswith("4(b)(i)")].copy()
nl = nh3_pool.facilityName.fillna("").str.lower()
is_nh3 = nl.apply(lambda s: any(k in s for k in KEYWORDS)) & ~nl.apply(lambda s: any(k in s for k in NAMES_EXCLUDED))
ammonia, hydrogen = nh3_pool[is_nh3].copy(), nh3_pool[~is_nh3].copy()


def assign(df):
    lat, lon = np.radians(df.Latitude.to_numpy(float)), np.radians(df.Longitude.to_numpy(float))
    best, dist = [], []
    for la, lo in zip(lat, lon):
        ds = {k: 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((la - np.radians(h[0])) / 2) ** 2 + np.cos(la) * np.cos(np.radians(h[0])) * np.sin((lo - np.radians(h[1])) / 2) ** 2))
              for k, h in hubs.items()}
        k = min(ds, key=ds.get)
        best.append(k); dist.append(ds[k])
    out = df.copy(); out["region"] = best; out["km_to_hub"] = dist
    out.loc[out.km_to_hub > RADIUS_KM, "region"] = "outside"
    return out


steel, ammonia, hydrogen = assign(steel), assign(ammonia), assign(hydrogen)
rows = []
for r in hubs:
    s, a, h = steel[steel.region == r], ammonia[ammonia.region == r], hydrogen[hydrogen.region == r]
    rows.append({"region": r, "steel_facilities": len(s), "steel_co2_mt": s.co2_mt.sum(), "steel_mt_implied": s.co2_mt.sum() / STEEL_INTENSITY,
                 "ammonia_facilities": len(a), "ammonia_co2_mt": a.co2_mt.sum(), "ammonia_mt_implied": a.co2_mt.sum() / NH3_INTENSITY,
                 "merchant_hydrogen_facilities": len(h), "merchant_hydrogen_co2_mt": h.co2_mt.sum()})
tab = pd.DataFrame(rows)
(ROOT / "data").mkdir(exist_ok=True)
tab.round(4).to_csv(ROOT / "data" / "regional_production_eprtr.csv", index=False)
fac = pd.concat([steel.assign(kind="steel 2(b)"), ammonia.assign(kind="ammonia (name filter)"), hydrogen.assign(kind="merchant hydrogen or other 4(b)(i)")])
fac[["kind", "countryName", "facilityName", "city", "Latitude", "Longitude", "co2_mt", "region", "km_to_hub"]].round(4).to_csv(
    ROOT / "data" / "eprtr_facilities_used.csv", index=False)
cover = {"steel_total_co2_mt_all_europe": float(steel.co2_mt.sum()), "steel_in_domain_co2_mt": float(steel[steel.region != "outside"].co2_mt.sum()),
         "ammonia_total_co2_mt": float(ammonia.co2_mt.sum()), "ammonia_in_domain_co2_mt": float(ammonia[ammonia.region != "outside"].co2_mt.sum()),
         "year": YEAR, "steel_intensity": STEEL_INTENSITY, "ammonia_intensity": NH3_INTENSITY, "radius_km": RADIUS_KM}
(ROOT / "data" / "eprtr_coverage.json").write_text(json.dumps(cover, indent=2), encoding="utf-8")
print(tab.round(2).to_string()); print(cover)
