"""Hourly 100 m wind speed and shortwave radiation for the 9 regions, 2023, Open-Meteo archive (ERA5-based)."""
import json
from pathlib import Path
import requests

REGIONS = {
    "NO-West": (59.1, 9.6), "SE-North": (65.6, 22.2), "DE-North": (53.6, 10.0), "DE-West": (51.4, 6.8),
    "NL-Rotterdam": (51.9, 4.1), "FR-North": (51.0, 2.3), "PL-Silesia": (50.3, 19.0), "IT-North": (45.0, 9.5),
    "ES-Iberia": (41.6, -0.9),
}
out = Path(__file__).resolve().parents[1] / "data" / "raw" / "weather_2023.json"
res = {}
for name, (lat, lon) in REGIONS.items():
    r = requests.get("https://archive-api.open-meteo.com/v1/archive", params={
        "latitude": lat, "longitude": lon, "start_date": "2023-01-01", "end_date": "2023-12-31",
        "hourly": "wind_speed_100m,shortwave_radiation", "wind_speed_unit": "ms", "timezone": "UTC"}, timeout=120)
    r.raise_for_status()
    res[name] = {"lat": lat, "lon": lon, **r.json()["hourly"]}
    print(name, len(res[name]["wind_speed_100m"]))
out.write_text(json.dumps(res), encoding="utf-8")
