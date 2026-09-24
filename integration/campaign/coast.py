"""Is this point on water, and how far is the nearest coast?

The proof of position the Southern Watch builder uses - a spot some loading
mission already put a ship on - does not exist south of Bass Strait. This is
the other proof: the coastline itself, from the committed Natural Earth
extract in geo/ (see tools/make_coast_extract.py). It answers two questions
and nothing else:

    on_land(lat, lon)       ray-cast against every land ring whose box holds
                            the point
    nm_to_coast(lat, lon)   great-circle-ish distance (nautical miles) to the
                            nearest coastline segment, with a cell index so a
                            campaign of a thousand units checks in a second

It says nothing about depth, ice, harbour geometry or whether the game's own
terrain agrees with Natural Earth to the metre. A ship 3 NM off a Natural
Earth coast is at sea by any chart; the game's rendering of that coast is
the play test's to confirm.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Coast:
    CELL = 0.5          # degrees; the segment index bucket

    def __init__(self, path=None):
        path = Path(path) if path else HERE / "geo" / "southern_theatre_coast.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.box = tuple(data["box"])
        self.rings = [[(p[0], p[1]) for p in ring] for ring in data["rings"]]
        self.bboxes = [(min(x for x, _ in r), min(y for _, y in r),
                        max(x for x, _ in r), max(y for _, y in r)) for r in self.rings]
        self.cells = {}
        for ring in self.rings:
            for a, b in zip(ring, ring[1:]):
                for cx in range(int(math.floor(min(a[0], b[0]) / self.CELL)),
                                int(math.floor(max(a[0], b[0]) / self.CELL)) + 1):
                    for cy in range(int(math.floor(min(a[1], b[1]) / self.CELL)),
                                    int(math.floor(max(a[1], b[1]) / self.CELL)) + 1):
                        self.cells.setdefault((cx, cy), []).append((a, b))

    def covers(self, lat, lon):
        w, s, e, n = self.box
        return w <= lon <= e and s <= lat <= n

    def on_land(self, lat, lon):
        """Point-in-polygon over the outer rings. Holes are lakes, ignored."""
        inside = False
        for ring, (w, s, e, n) in zip(self.rings, self.bboxes):
            if not (w <= lon <= e and s <= lat <= n):
                continue
            hit = False
            for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
                if (y1 > lat) != (y2 > lat):
                    x = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
                    if x > lon:
                        hit = not hit
            if hit:
                inside = not inside
        return inside

    @staticmethod
    def _seg_nm(lat, lon, a, b):
        """Distance from a point to a segment, in NM, on a local flat frame."""
        k = math.cos(math.radians(lat))
        ax, ay = (a[0] - lon) * 60.0 * k, (a[1] - lat) * 60.0
        bx, by = (b[0] - lon) * 60.0 * k, (b[1] - lat) * 60.0
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        if l2 == 0:
            return math.hypot(ax, ay)
        t = max(0.0, min(1.0, -(ax * dx + ay * dy) / l2))
        return math.hypot(ax + t * dx, ay + t * dy)

    def nm_to_coast(self, lat, lon, limit_nm=400.0):
        """Nearest coastline within limit_nm, else limit_nm. Searches the
        index in growing rings of cells, so open ocean is cheap too."""
        cx0, cy0 = int(math.floor(lon / self.CELL)), int(math.floor(lat / self.CELL))
        best = limit_nm
        k = math.cos(math.radians(lat))
        cell_nm = self.CELL * 60.0 * min(1.0, k)
        max_r = int(math.ceil(limit_nm / cell_nm)) + 1
        for r in range(0, max_r + 1):
            # everything at cell-ring r is at least (r-1)*cell_nm away
            if (r - 1) * cell_nm > best:
                break
            for cx in range(cx0 - r, cx0 + r + 1):
                for cy in range(cy0 - r, cy0 + r + 1):
                    if max(abs(cx - cx0), abs(cy - cy0)) != r:
                        continue
                    for a, b in self.cells.get((cx, cy), ()):
                        d = self._seg_nm(lat, lon, a, b)
                        if d < best:
                            best = d
        return best

    def check(self, lat, lon):
        """(on_land, nm_to_coast) in one call."""
        return self.on_land(lat, lon), self.nm_to_coast(lat, lon)


_COAST = None


def coast():
    global _COAST
    if _COAST is None:
        _COAST = Coast()
    return _COAST
