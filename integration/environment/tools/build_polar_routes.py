"""Build data/polar-routes.json: the polar sea routes used by the polar route chart. BUILD-TESTED.

    python3 integration/environment/tools/build_polar_routes.py

Each route is a list of ANCHORS: named straits, seas and ports taken from public charts
(approximate positions). Between anchors the tool finds the shortest path that stays at sea
on the bundled Natural Earth low-resolution land mask and outside the Natural Earth 1:10m ice
shelves, then simplifies it while keeping every 5 NM sample at sea. The coarse mask closes or
shifts some narrow channels, so a route follows the mask's water, not the real fairway. These
are game-rule previews for GCO logistics, not navigation advice.
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env.geo import default_land_mask, great_circle_nm, lon_delta, sample_leg, wrap_lon  # noqa: E402
from mno_env.ice import load_shelves  # noqa: E402

OUT = HERE.parent / "data" / "polar-routes.json"

# name -> (hemisphere, anchors [(lat, lon, label)])
ROUTES = {
    "Northern Sea Route (coastal)": ("north", [
        (69.6, 33.8, "Kola Bay (Murmansk)"), (71.0, 40.0, "Barents Sea"), (70.6, 50.0, "Pechora Sea"),
        (70.4, 57.6, "Kara Gate"), (72.5, 65.0, "Kara Sea"), (75.0, 80.0, "Kara Sea (Dikson approaches)"),
        (76.6, 92.0, "Nordenskiold Archipelago"), (77.8, 104.0, "Vilkitsky Strait"), (77.0, 115.0, "Laptev Sea"),
        (75.5, 130.0, "Laptev Sea (east)"), (74.6, 140.0, "Sannikov Strait"), (72.5, 155.0, "East Siberian Sea"),
        (71.0, 170.0, "Chukchi approaches"), (70.0, 178.5, "Long Strait"), (68.5, -172.0, "Chukchi Sea"),
        (65.8, -169.0, "Bering Strait"), (63.0, -173.0, "Bering Sea")]),
    "Northern Sea Route (high latitude)": ("north", [
        (69.6, 33.8, "Kola Bay (Murmansk)"), (72.5, 40.0, "Barents Sea"), (76.0, 55.0, "Barents Sea (north)"),
        (77.3, 69.0, "Cape Zhelaniya"), (79.5, 80.0, "Kara Sea (north)"), (81.8, 100.0, "North of Severnaya Zemlya"),
        (79.5, 120.0, "Laptev Sea (north)"), (77.0, 140.0, "North of the New Siberian Islands"),
        (76.5, 155.0, "East Siberian Sea (north)"), (73.5, 170.0, "De Long Strait approaches"),
        (71.5, 178.0, "Long Strait"), (68.5, -172.0, "Chukchi Sea"), (65.8, -169.0, "Bering Strait"), (63.0, -173.0, "Bering Sea")]),
    "Northwest Passage (southern)": ("north", [
        (66.5, -58.0, "Davis Strait"), (72.0, -66.0, "Baffin Bay"), (74.2, -82.0, "Lancaster Sound"),
        (74.3, -91.0, "Barrow Strait"), (73.8, -95.5, "Peel Sound (north)"), (72.5, -96.0, "Peel Sound"),
        (71.3, -96.6, "Franklin Strait"), (69.8, -96.5, "James Ross Strait"), (68.6, -97.8, "Simpson Strait"),
        (68.3, -102.0, "Queen Maud Gulf"), (68.8, -107.0, "Dease Strait"), (69.2, -114.0, "Dolphin and Union Strait"),
        (70.5, -124.0, "Amundsen Gulf"), (71.0, -135.0, "Beaufort Sea"), (71.8, -156.5, "Point Barrow"),
        (70.0, -165.0, "Chukchi Sea"), (65.8, -168.8, "Bering Strait"), (63.0, -173.0, "Bering Sea")]),
    "Northwest Passage (Parry Channel)": ("north", [
        (66.5, -58.0, "Davis Strait"), (72.0, -66.0, "Baffin Bay"), (74.2, -82.0, "Lancaster Sound"),
        (74.3, -91.0, "Barrow Strait"), (74.3, -105.0, "Viscount Melville Sound"), (74.6, -116.0, "M'Clure Strait"),
        (74.3, -122.0, "M'Clure Strait (west)"), (73.0, -130.0, "Beaufort Sea"), (71.8, -156.5, "Point Barrow"),
        (70.0, -165.0, "Chukchi Sea"), (65.8, -168.8, "Bering Strait"), (63.0, -173.0, "Bering Sea")]),
    "Transpolar Sea Route": ("north", [
        (63.0, -173.0, "Bering Sea"), (65.8, -169.0, "Bering Strait"), (75.0, -170.0, "Chukchi Borderland"),
        (85.0, -170.0, "Central Arctic"), (89.9, 0.0, "North Pole"), (84.0, 5.0, "Nansen Basin"),
        (79.0, 2.0, "Fram Strait"), (72.0, 5.0, "Norwegian Sea"), (69.0, 12.0, "Norwegian Sea (Lofoten)")]),
    "Ross Sea: McMurdo resupply": ("south", [
        (-60.0, 175.0, "Southern Ocean (south of New Zealand)"), (-66.0, 178.0, "Ross Sea pack belt"),
        (-72.0, 178.0, "Ross Sea"), (-76.0, 170.0, "Ross Sea (west)"), (-77.7, 166.4, "McMurdo Sound")]),
    "Prydz Bay: Davis station": ("south", [
        (-60.0, 80.0, "Southern Ocean (south Indian)"), (-66.0, 78.0, "Prydz Bay approaches"), (-68.5, 77.9, "Davis station")]),
    "Antarctic Peninsula: Rothera": ("south", [
        (-55.0, -65.0, "Drake Passage (north)"), (-62.0, -62.0, "Bransfield Strait approaches"),
        (-65.0, -65.0, "Gerlache / Bellingshausen coast"), (-67.6, -68.2, "Rothera (Marguerite Bay)")]),
}

DLA = 0.1


class Water:
    def __init__(self):
        self.land = default_land_mask()
        self.shelves = load_shelves()

    def __call__(self, p) -> bool:
        if self.land.is_land(p[0], p[1]):
            return False
        return not (p[0] < -60 and any(s.contains(p[0], p[1]) for s in self.shelves))

    def leg_ok(self, a, b) -> bool:
        return all(self(p) for p in sample_leg(a, b, 5.0))

    def snap(self, p):
        if self(p):
            return p
        for r in range(1, 60):
            best = None
            for k in range(16 * r):
                ang = 2 * math.pi * k / (16 * r)
                q = (p[0] + r * 0.05 * math.sin(ang), wrap_lon(p[1] + r * 0.05 * math.cos(ang) / max(0.15, math.cos(math.radians(p[0])))))
                if abs(q[0]) < 89.9 and self(q):
                    d = great_circle_nm(p, q)
                    if best is None or d < best[0]:
                        best = (d, q)
            if best:
                return best[1]
        raise ValueError(f"no water near {p}")

    def path(self, a, b):
        """Shortest water path on a 0.1-degree latitude lattice between two water points."""
        if self.leg_ok(a, b):
            return [a, b]
        lat0, lat1 = max(-89.5, min(a[0], b[0]) - 4), min(89.5, max(a[0], b[0]) + 4)
        dlo = DLA / max(0.12, math.cos(math.radians((lat0 + lat1) / 2)))
        span = lon_delta(b[1], a[1])
        lo_start = a[1] + min(0.0, span) - 8
        nlo, nla = int((abs(span) + 16) / dlo) + 1, int((lat1 - lat0) / DLA) + 1

        def node(p):
            return round((p[0] - lat0) / DLA), round(lon_delta(p[1], lo_start) / dlo)

        def pt(n):
            return lat0 + n[0] * DLA, wrap_lon(lo_start + n[1] * dlo)

        cache = {}

        def ok(n):
            if n not in cache:
                cache[n] = 0 <= n[0] < nla and 0 <= n[1] < nlo and self(pt(n))
            return cache[n]

        s, g = node(a), node(b)
        cache[s] = cache[g] = True
        queue, came, cost = [(0.0, 0.0, s)], {s: None}, {s: 0.0}
        while queue:
            _, c, n = heapq.heappop(queue)
            if n == g:
                break
            if c > cost[n] + 1e-9:
                continue
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    m = (n[0] + di, n[1] + dj)
                    if (di or dj) and ok(m):
                        nc = c + great_circle_nm(pt(n), pt(m))
                        if nc < cost.get(m, 1e18):
                            cost[m], came[m] = nc, n
                            heapq.heappush(queue, (nc + great_circle_nm(pt(m), pt(g)), nc, m))
        if g not in came:
            raise ValueError(f"no water path {a} -> {b}")
        path, n = [], g
        while n is not None:
            path.append(pt(n))
            n = came[n]
        path = path[::-1]
        path[0], path[-1] = a, b
        out, i = [path[0]], 0
        while i < len(path) - 1:  # greedy simplification that keeps every leg at sea
            j = len(path) - 1
            while j > i + 1 and not self.leg_ok(path[i], path[j]):
                j -= 1
            out.append(path[j])
            i = j
        return out


def build() -> dict:
    w = Water()
    routes = []
    for name, (hemi, anchors) in ROUTES.items():
        snapped = [w.snap((la, lo)) for la, lo, _ in anchors]
        pts = [snapped[0]]
        for a, b in zip(snapped, snapped[1:]):
            pts += w.path(a, b)[1:]
        pts = [(round(p[0], 3), round(wrap_lon(p[1]), 3)) for p in pts]
        bad = sum(1 for a, b in zip(pts, pts[1:]) for p in sample_leg(a, b, 10.0) if not w(p))
        if bad:
            raise ValueError(f"{name}: {bad} samples on land or ice shelf after routing")
        dist = sum(great_circle_nm(a, b) for a, b in zip(pts, pts[1:]))
        routes.append({"name": name, "hemisphere": hemi, "distance_nm": round(dist, 1), "points": pts,
                       "anchors": [{"lat": la, "lon": lo, "label": lab, "snapped": [round(s[0], 3), round(s[1], 3)]}
                                   for (la, lo, lab), s in zip(anchors, snapped)]})
    return {"schema": "mno.environment.polar-routes.v1",
            "note": ("Anchors are approximate positions of named straits, seas and ports from public charts. Paths are "
                     "the shortest water path on the bundled Natural Earth low-resolution land mask, outside the "
                     "Natural Earth 1:10m ice shelves; the coarse mask shifts some narrow channels. Game-rule preview, "
                     "not navigation advice."),
            "routes": routes}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=OUT)
    a = p.parse_args(argv)
    doc = build()
    a.out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    for r in doc["routes"]:
        print(f"{r['name']}: {len(r['points'])} points, {r['distance_nm']:.0f} nm")


if __name__ == "__main__":
    main()
