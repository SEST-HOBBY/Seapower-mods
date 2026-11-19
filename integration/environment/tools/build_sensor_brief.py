"""Build the sensor-weather brief page for the GCO theatres (one self-contained HTML). BUILD-TESTED.

    python3 integration/environment/tools/build_sensor_brief.py --out /tmp/sensor-brief.html

Runs the procedural model over the campaign opening (default 14 Sep 2028, 7 days), samples each
theatre of data/gco-weather-2028.json at 00Z and 12Z, and derives the sensor environment
(mno_env/sensors.py) and brief lines (mno_env/sensor_brief.py). PROCEDURAL WEATHER and planning
notes; nothing here changes a mission or the game.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env import gco_weather, procedural, sensors  # noqa: E402
from mno_env.clock import MnoEnvState, to_seconds  # noqa: E402
from mno_env.mission_adapter import native_state  # noqa: E402
from mno_env.sensor_brief import brief_lines  # noqa: E402

TEMPLATE = HERE / "sensor_brief_template.html"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--start", default="2028-09-14T00:00:00Z")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--seed", default="gco-2028-opening")
    a = p.parse_args(argv)
    start = dt.datetime.fromisoformat(a.start.replace("Z", "+00:00"))
    snap = procedural.generate(a.seed, start, hours=a.days * 24, step_hours=6, res_deg=2.5)
    st = MnoEnvState(snap)
    theatres = []
    for th in gco_weather.load_spec()["theatres"]:
        rows = []
        for k in range(a.days * 2):
            t = start + dt.timedelta(hours=12 * k)
            v = st.sample(to_seconds(t), th["lat"], th["lon"]).values
            env = sensors.derive(v, th["lat"], th["lon"], t, th["name"])
            ns = native_state(v, initial=(k == 0))
            i = env.items
            rows.append({
                "t": t.strftime("%d %b %H%MZ"), "ss": ns.sea_state, "clouds": ns.clouds, "rain": ns.rain, "fog": ns.fog,
                "storm": ns.thunderstorm, "wind": ns.wind, "hs": round(v["wave_hs_m"], 1), "vis": i["visibility_km"].value,
                "amb": i["game_ambient_db"].value, "mld": i["mixed_layer_m"].value, "edh": i["evap_duct_m"].value,
                "rx": i["rain_atten_db_km"].value["X"], "ir": i["ir_range_factor_lwir"].value, "moon": i["moon"].value,
                "sun": i["sun_alt_deg"].value, "lines": brief_lines(env)})
        meta = sensors.THEATRES.get(th["name"], {})
        theatres.append({"id": th["name"], "name": meta.get("name", th["name"]), "lat": th["lat"], "lon": th["lon"],
                         "why": th.get("why", ""), "rows": rows})
    data = {"start": a.start, "days": a.days, "version": procedural.VERSION, "theatres": theatres,
            "game": sensors.GAME_SONAR}
    html = TEMPLATE.read_text(encoding="utf-8").replace("__MNO_SENSOR_DATA__", json.dumps(data, separators=(",", ":")))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(html, encoding="utf-8")
    print(f"wrote {a.out} ({a.out.stat().st_size / 1e3:.0f} kB): {len(theatres)} theatres x {a.days * 2} samples")


if __name__ == "__main__":
    main()
