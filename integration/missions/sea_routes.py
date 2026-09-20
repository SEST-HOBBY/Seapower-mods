#!/usr/bin/env python3
"""Route civil shipping lanes through water.

A lane is a chain of lat/lon "via" points that name the real corridor
(Lombok Strait, Makassar Strait, Ombai Strait ...). Between consecutive via
points this module finds the shortest all-water path on the 1 km land mask
(global_land_mask) sampled on a 0.025 degree grid, with a mild penalty for
cells that touch land so lanes sit a mile or two off the beach wherever the
channel allows, then drops every waypoint within the leg that the
line-of-sight check says is redundant. The via points themselves always
survive, so the lane follows the corridor it was given rather than the
shortest water line; a via point that falls on land (a harbour) is snapped to
the nearest water cell.

Routing a long lane costs a few seconds of A*, so results are cached in a
JSON file next to the mission generator, keyed on the via chain; the cache
is committed and only lanes whose via points changed are re-routed.

    from sea_routes import Router
    r = Router(cache_path)
    pts = r.route([(-7.6, 116.6), (-5.3, 118.0), ...])   # -> [(lat, lon), ...]
    r.save()
"""
import heapq
import json
import math
from pathlib import Path

import numpy as np

try:
    from global_land_mask import globe
except ImportError:                       # the checkers still run; routing does not
    globe = None

STEP = 0.025                              # degrees, about 1.5 nm at the equator
COAST_PENALTY = 0.6                       # extra cost fraction for a water cell touching land


class Grid:
    """Land/water grid over a lat/lon box. Row 0 is the northern edge."""

    def __init__(self, lat_min, lat_max, lon_min, lon_max, step=STEP):
        self.step = step
        self.lat0, self.lon0 = lat_max, lon_min
        self.rows = int(round((lat_max - lat_min) / step)) + 1
        self.cols = int(round((lon_max - lon_min) / step)) + 1
        lats = lat_max - np.arange(self.rows) * step
        lons = lon_min + np.arange(self.cols) * step
        LAT, LON = np.meshgrid(lats, lons, indexing="ij")
        self.land = globe.is_land(LAT, LON)
        coast = np.zeros_like(self.land)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                coast |= np.roll(np.roll(self.land, dr, 0), dc, 1)
        self.coast = coast & ~self.land
        self.coslat = np.cos(np.radians(lats))

    def cell(self, lat, lon):
        return int(round((self.lat0 - lat) / self.step)), int(round((lon - self.lon0) / self.step))

    def latlon(self, r, c):
        return self.lat0 - r * self.step, self.lon0 + c * self.step

    def inside(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def nearest_water(self, r, c):
        if not self.land[r, c]:
            return r, c
        for radius in range(1, 40):
            for dr in range(-radius, radius + 1):
                for dc in (-radius, radius):
                    for rr, cc in ((r + dr, c + dc), (r + dc, c + dr)):
                        if self.inside(rr, cc) and not self.land[rr, cc]:
                            return rr, cc
        raise ValueError(f"no water within {40 * self.step:.1f} deg of {self.latlon(r, c)}")

    def dist(self, a, b):
        """nm between two cells, equirectangular."""
        (r0, c0), (r1, c1) = a, b
        cl = self.coslat[(r0 + r1) // 2]
        return math.hypot((r1 - r0) * self.step * 60.0, (c1 - c0) * self.step * 60.0 * cl)

    def astar(self, start, goal):
        land, coast = self.land, self.coast
        step_nm = self.step * 60.0
        openq = [(0.0, start)]
        g = {start: 0.0}
        came = {}
        moves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        while openq:
            _, cur = heapq.heappop(openq)
            if cur == goal:
                path = [cur]
                while cur in came:
                    cur = came[cur]
                    path.append(cur)
                return path[::-1]
            r, c = cur
            gc = g[cur]
            cl = self.coslat[r]
            for dr, dc in moves:
                rr, cc = r + dr, c + dc
                if not (0 <= rr < self.rows and 0 <= cc < self.cols) or land[rr, cc]:
                    continue
                if dr and dc and (land[r, cc] or land[rr, c]):      # no cutting corners past land
                    continue
                cost = math.hypot(dr * step_nm, dc * step_nm * cl)
                if coast[rr, cc]:
                    cost *= 1.0 + COAST_PENALTY
                ng = gc + cost
                nxt = (rr, cc)
                if ng < g.get(nxt, 1e18):
                    g[nxt] = ng
                    came[nxt] = cur
                    heapq.heappush(openq, (ng + self.dist(nxt, goal), nxt))
        return None

    def clear(self, a, b):
        """True when the straight line between two cells stays off land on the
        real 1 km mask, sampled every half mile (finer than the grid, so a
        simplified lane cannot clip a headland the grid rounded away)."""
        (la0, lo0), (la1, lo1) = self.latlon(*a), self.latlon(*b)
        n = max(2, int(self.dist(a, b) / 0.5))
        lats = np.linspace(la0, la1, n + 1)
        lons = np.linspace(lo0, lo1, n + 1)
        return not globe.is_land(lats, lons).any()

    def simplify(self, path):
        """Greedy line-of-sight: keep a waypoint only where the lane must turn."""
        out = [path[0]]
        i = 0
        while i < len(path) - 1:
            j = len(path) - 1
            while j > i + 1 and not self.clear(path[i], path[j]):
                j -= 1
            out.append(path[j])
            i = j
        return out


class Router:
    def __init__(self, cache_path, pad=4.0):
        self.cache_path = Path(cache_path)
        self.cache = json.loads(self.cache_path.read_text()) if self.cache_path.exists() else {}
        self.pad = pad
        self.dirty = False
        self._grids = {}

    @staticmethod
    def key(vias):
        return ";".join(f"{la:.4f},{lo:.4f}" for la, lo in vias)

    def grid_for(self, vias):
        lats = [la for la, _ in vias]
        lons = [lo for _, lo in vias]
        box = (math.floor(min(lats) - self.pad), math.ceil(max(lats) + self.pad),
               math.floor(min(lons) - self.pad), math.ceil(max(lons) + self.pad))
        if box not in self._grids:
            self._grids[box] = Grid(*box)
        return self._grids[box]

    def route(self, vias):
        k = self.key(vias)
        if k in self.cache:
            return [tuple(p) for p in self.cache[k]]
        if globe is None:
            raise SystemExit("sea_routes: global_land_mask is not installed (pip install global-land-mask)")
        grid = self.grid_for(vias)
        cells = [grid.nearest_water(*grid.cell(la, lo)) for la, lo in vias]
        full = [cells[0]]
        for a, b in zip(cells, cells[1:]):
            leg = grid.astar(a, b)
            if leg is None:
                raise SystemExit(f"sea_routes: no water path between {grid.latlon(*a)} and {grid.latlon(*b)}")
            full += grid.simplify(leg)[1:]       # per leg: every via point survives, the corridor holds
        pts = []
        for r, c in full:
            pt = tuple(round(v, 3) for v in grid.latlon(r, c))
            if not pts or pt != pts[-1]:
                pts.append(pt)
        self.cache[k] = pts
        self.dirty = True
        return pts

    def save(self):
        if self.dirty:
            self.cache_path.write_text(json.dumps(self.cache, indent=0, sort_keys=True) + "\n")
            self.dirty = False
