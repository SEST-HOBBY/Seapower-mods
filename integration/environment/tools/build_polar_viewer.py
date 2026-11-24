"""Build the polar route chart (one self-contained HTML page). BUILD-TESTED.

    python3 integration/environment/tools/build_polar_viewer.py --out /tmp/polar-routes.html

Embeds, for every week of a campaign year from --start: sea-ice concentration on a 1-degree
grid poleward of 50 degrees in both hemispheres (the NSIDC-calibrated climatology of
seaice.py, which the procedural weather uses), the polar routes of data/polar-routes.json with
the ice along each route, and each route's transit evaluated by routes.evaluate for every ship
ice capability (ship departs that week at --speed knots and meets the ice as it advances).
Also: Natural Earth coastlines, the 1:10m ice shelves, the GCO theatre bounds.
CLIMATOLOGY, NOT A FORECAST; game-rule previews, not navigation advice.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env import routes as R, seaice  # noqa: E402
from mno_env.clock import from_seconds, to_seconds  # noqa: E402
from mno_env.geo import PROTOTYPE_COAST, LandMask, great_circle_nm, sample_leg  # noqa: E402
from mno_env.ice import ACCESS_THRESHOLDS, load_shelves  # noqa: E402

TEMPLATE = HERE / "polar_routes_template.html"
ROUTES_FILE = HERE.parent / "data" / "polar-routes.json"
LAT_EDGE = 50


class ClimatologyState:
    """routes.evaluate reads the environment through .sample(); this one serves the sea-ice
    climatology for the moment the ship reaches each point (edges cached per day)."""

    def __init__(self):
        self._edges = {}

    def edges(self, t: dt.datetime) -> dict:
        key = t.date()
        if key not in self._edges:
            self._edges[key] = seaice.edges_on(dt.datetime(key.year, key.month, key.day, 12, tzinfo=dt.timezone.utc))
        return self._edges[key]

    def sample(self, seconds, lat, lon, names=None):
        return SimpleNamespace(values={"sea_ice_conc_pct": seaice.ice_at(lat, lon, self.edges(from_seconds(seconds)))})


def route_samples(points, step_nm=30.0):
    out = [tuple(points[0])]
    for a, b in zip(points, points[1:]):
        out += sample_leg(tuple(a), tuple(b), step_nm)[1:]
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--start", default="2028-09-14T00:00:00Z")
    p.add_argument("--weeks", type=int, default=53)
    p.add_argument("--speed", type=float, default=12.0)
    a = p.parse_args(argv)
    start = dt.datetime.fromisoformat(a.start.replace("Z", "+00:00"))
    weeks = [start + dt.timedelta(days=7 * k) for k in range(a.weeks)]
    mask = LandMask.from_file()
    shelves = load_shelves()
    land_memo = {}

    class MemoLand:  # route samples repeat every week and class: test each point once
        def is_land(self, lat, lon):
            k = (round(lat, 5), round(lon, 5))
            if k not in land_memo:
                land_memo[k] = mask.is_land(lat, lon)
            return land_memo[k]
    state = ClimatologyState()
    rows = 90 - LAT_EDGE + 1
    land = {"north": [], "south": []}
    for h, sign in (("north", 1), ("south", -1)):
        for j in range(rows):
            lat = sign * (90 - j)
            for i in range(360):
                lon = -180 + i
                land[h].append(mask.is_land(max(-89.9, min(89.9, lat)), lon)
                               or (h == "south" and lat < -60 and any(s.contains(lat, lon) for s in shelves)))
    ice = {"north": [], "south": []}
    extent = []
    for t in weeks:
        e = state.edges(t)
        for h, sign in (("north", 1), ("south", -1)):
            vals = bytearray()
            for j in range(rows):
                lat = sign * (90 - j)
                for i in range(360):
                    k = j * 360 + i
                    vals.append(255 if land[h][k] else int(round(seaice.ice_at(lat, -180 + i, e))))
            ice[h].append(base64.b64encode(bytes(vals)).decode("ascii"))
        extent.append({h: {"target": round(seaice.target_extent(h, t), 2),
                           "model": round(seaice.extent_with_marginal(h, e), 2)}  # as the pixels: regional seas included
                       for h in ("north", "south")})
    doc = json.loads(ROUTES_FILE.read_text(encoding="utf-8"))
    routes = []
    for r in doc["routes"]:
        pts = [tuple(x) for x in r["points"]]
        samples = route_samples(pts)
        along, d = [0.0], 0.0
        for s0, s1 in zip(samples, samples[1:]):
            d += great_circle_nm(s0, s1)
            along.append(round(d, 1))
        ice_along, evals = [], {c: [] for c in ACCESS_THRESHOLDS}
        for t in weeks:
            e = state.edges(t)
            ice_along.append(base64.b64encode(bytes(int(round(seaice.ice_at(la, lo, e))) for la, lo in samples)).decode("ascii"))
            for cap in ACCESS_THRESHOLDS:
                res = R.evaluate(pts, state, to_seconds(t), speed_kn=a.speed, capability=cap,
                                 shelves=shelves if r["hemisphere"] == "south" else (), max_step_nm=20.0,
                                 land_mask=MemoLand())
                evals[cap].append({"w": res.worst_access, "h": res.hours, "d": res.distance_nm, "p": round(res.peak_ice_pct),
                                   "b": res.blocked, "at": [round(x, 2) for x in res.blocked_at] if res.blocked_at else None})
        routes.append({"name": r["name"], "hemisphere": r["hemisphere"], "distance_nm": r["distance_nm"],
                       "points": [[round(x, 2), round(y, 2)] for x, y in pts],
                       "samples": [[round(x, 2), round(y, 2)] for x, y in samples], "along": along,
                       "anchors": r["anchors"], "ice": ice_along, "eval": evals})
    coast = []
    for ring in json.loads(PROTOTYPE_COAST.read_text(encoding="utf-8"))["polygons"]:
        if any(abs(y) >= LAT_EDGE - 8 for _, y in ring):
            coast.append([[round(x, 2), round(y, 2)] for x, y in ring])
    shelf_polys = []
    for s in json.loads((HERE.parent / "data" / "ice-shelves-naturalearth-10m.json").read_text(encoding="utf-8"))["shelves"]:
        for poly in s["polygons"]:
            ring = poly[0]
            if len(ring) < 4:
                continue
            step = max(1, len(ring) // 160)
            shelf_polys.append({"n": s.get("name", ""), "r": [[round(x, 2), round(y, 2)] for x, y in ring[::step]]})
    data = {
        "meta": {"start": a.start, "weeks": [t.strftime("%Y-%m-%d") for t in weeks], "speed_kn": a.speed,
                 "lat_edge": LAT_EDGE, "rows": rows, "baseline": seaice.DEFAULT_BASELINE},
        "thresholds": ACCESS_THRESHOLDS, "ice": ice, "extent": extent, "routes": routes,
        "coast": coast, "shelves": shelf_polys, "gco": {"lat_min": -62, "lat_max": 74},
    }
    html = TEMPLATE.read_text(encoding="utf-8").replace("__MNO_POLAR_DATA__", json.dumps(data, separators=(",", ":")))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(html, encoding="utf-8")
    print(f"wrote {a.out} ({a.out.stat().st_size / 1e6:.2f} MB): {len(weeks)} weeks, {len(routes)} routes")
    for r in routes:
        open_weeks = {c: sum(1 for ev in r["eval"][c] if not ev["b"]) for c in ACCESS_THRESHOLDS}
        print(f"  {r['name']}: passable weeks by capability {open_weeks}")


if __name__ == "__main__":
    main()
