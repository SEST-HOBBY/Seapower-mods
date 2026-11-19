"""Build the offline weather viewer (one self-contained HTML page) from the procedural model.

    python3 integration/environment/tools/build_weather_viewer.py --out /tmp/gco-weather.html

Embeds: every 6 h for --days days at --res degrees (pressure, 10 m wind, cloud, rain, waves,
sea ice), the live storm list per frame, a 0.5-degree land mask, Natural Earth coastlines and
1:10m ice shelves (decimated), the GCO bounds and the chokepoint tiles of
data/gco-weather-2028.json. VISUAL DEMO ONLY: procedural weather, not real weather.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import math
import struct
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env import gco_weather, procedural  # noqa: E402
from mno_env.clock import MnoEnvState, to_seconds  # noqa: E402
from mno_env.geo import PROTOTYPE_COAST, LandMask  # noqa: E402
from mno_env.ice import DEFAULT_SHELVES  # noqa: E402

TEMPLATE = HERE / "weather_viewer_template.html"


def b64(fmt: str, vals) -> str:
    return base64.b64encode(struct.pack(f"<{len(vals)}{fmt}", *vals)).decode("ascii")


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seed", default="gco-2028-opening")
    p.add_argument("--start", default="2028-09-14T00:00:00Z")
    p.add_argument("--days", type=int, default=10)
    p.add_argument("--res", type=float, default=2.5)
    a = p.parse_args(argv)
    start = dt.datetime.fromisoformat(a.start.replace("Z", "+00:00"))
    t_build = time.time()
    snap = procedural.generate(a.seed, start, hours=a.days * 24, step_hours=6, res_deg=a.res)
    st = MnoEnvState(snap)
    g = st.grid
    fields = {k: [] for k in "puvcrwi"}
    storms = []
    for f, fr in enumerate(snap["times"]):
        t = dt.datetime.fromisoformat(fr["valid_utc"].replace("Z", "+00:00"))
        vals = {n: st._values(f, n) for n in ("msl_pressure_hpa", "wind_u10_ms", "wind_v10_ms", "cloud_fraction_pct",
                                              "precip_rate_mm_h", "wave_hs_m", "sea_ice_conc_pct")}
        fields["p"].append(b64("H", [int(clamp(round((v - 900) * 10), 0, 65535)) for v in vals["msl_pressure_hpa"]]))
        fields["u"].append(b64("b", [int(clamp(round(v * 3), -127, 127)) for v in vals["wind_u10_ms"]]))
        fields["v"].append(b64("b", [int(clamp(round(v * 3), -127, 127)) for v in vals["wind_v10_ms"]]))
        fields["c"].append(b64("B", [int(clamp(round(v * 2.5), 0, 250)) for v in vals["cloud_fraction_pct"]]))
        fields["r"].append(b64("B", [int(clamp(round(v * 10), 0, 255)) for v in vals["precip_rate_mm_h"]]))
        fields["w"].append(b64("B", [int(clamp(round(v * 10), 0, 255)) for v in vals["wave_hs_m"]]))
        fields["i"].append(b64("B", [int(clamp(round(v * 2.5), 0, 250)) for v in vals["sea_ice_conc_pct"]]))
        if "visibility_km" in st.fields:  # extinction (1/km) on a log scale, so fog survives interpolation
            fields.setdefault("x", []).append(b64("B", [int(clamp(round((math.log10(1.0 / max(0.01, v)) + 2) * 63.75), 0, 255))
                                                       for v in st._values(f, "visibility_km")]))
        storms.append([{"k": "T" if s["kind"] == "tropical" else "X", "lat": round(s["lat"], 2), "lon": round(s["lon"], 2),
                        "d": round(s["deficit"] * s["intensity"], 1), "r": round(s["radius"], 1),
                        "id": f"{s['kind'][0]}{s['t0']}{round(s['lat0'], 1)}", "b": s.get("basin", "")}
                       for s in procedural.active_storms(a.seed, t)])
    mask = LandMask.from_file()
    bits = bytearray()
    acc = nbits = 0
    for j in range(360):
        lat = 89.75 - j * 0.5
        for i in range(720):
            acc = (acc << 1) | (1 if mask.is_land(lat, -179.75 + i * 0.5) else 0)
            nbits += 1
            if nbits == 8:
                bits.append(acc)
                acc = nbits = 0
    coast = json.loads(PROTOTYPE_COAST.read_text(encoding="utf-8"))["polygons"]
    shelf_doc = json.loads(DEFAULT_SHELVES.read_text(encoding="utf-8"))
    shelves = []
    for s in shelf_doc["shelves"]:
        for poly in s["polygons"]:
            ring = poly[0]
            step = max(1, len(ring) // 120)
            r = [[round(x, 2), round(y, 2)] for x, y in ring[::step]]
            if len(r) >= 4:
                shelves.append(r)
    spec = gco_weather.load_spec()
    data = {
        "meta": {"seed": a.seed, "start": a.start, "step_h": 6, "frames": len(snap["times"]), "res": a.res,
                 "nx": g.nx, "ny": g.ny, "lon_min": g.lon_min, "lat_min": g.lat_min, "version": procedural.VERSION,
                 "snapshot_id": snap["snapshot_id"], "payload_sha256": snap["integrity"]["payload_sha256"],
                 "seaice": snap["provenance"]["product_version"]},
        "fields": fields, "storms": storms, "land": base64.b64encode(bytes(bits)).decode("ascii"),
        "coast": coast, "shelves": shelves,
        "gco": {"lat_min": -62, "lat_max": 74, "lon_min": -100, "lon_max": 258},
        "tiles": [{"name": t["name"], "lat": t["lat"], "lon": t["lon"], "h": t["half_deg"]} for t in spec["theatres"]],
    }
    html = TEMPLATE.read_text(encoding="utf-8").replace("__MNO_WEATHER_DATA__", json.dumps(data, separators=(",", ":")))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(html, encoding="utf-8")
    print(f"wrote {a.out} ({a.out.stat().st_size / 1e6:.2f} MB) in {time.time() - t_build:.0f} s: "
          f"{len(snap['times'])} frames, {g.nx}x{g.ny} grid, {sum(len(s) for s in storms)} storm positions")


if __name__ == "__main__":
    main()
