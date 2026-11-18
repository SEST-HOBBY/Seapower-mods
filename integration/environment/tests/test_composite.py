import datetime as dt
import unittest

from helpers import UTC

from mno_env.clock import MnoEnvState, to_seconds
from mno_env.composite import MnoEnvComposite
from mno_env.grid import LatLonGrid
from mno_env.ingest import build

T0 = dt.datetime(2028, 9, 14, tzinfo=UTC)


def const(grid, value, start, hours, step=6, wave_dir=None):
    frames = []
    for h in range(0, hours + 1, step):
        vals = {"msl_pressure_hpa": [value] * grid.size}
        if wave_dir is not None:
            vals["wave_dir_deg"] = [wave_dir] * grid.size
        frames.append((start + dt.timedelta(hours=h), None, vals))
    kinds = {k: "reanalysis" for k in frames[0][2]}
    prov = {"provider": "t", "product": "t", "product_version": "1", "licence": "x", "attribution": "x", "source_url": None,
            "downloaded_utc": None, "source_time_utc": None, "forecast_issue_utc": None}
    return MnoEnvState(build(snapshot_id=f"c{value}", data_class="reanalysis", provenance=prov,
                             mapping={"mode": "historical_analogue", "offset_seconds": 0, "statement": "test; not a forecast"},
                             grid=grid, frames=frames, kinds=kinds, created=start))


class Fallback:
    fields = ["msl_pressure_hpa", "wave_dir_deg", "sea_ice_conc_pct"]

    def sample(self, t, lat, lon, names=None):
        class S:
            values = {n: {"msl_pressure_hpa": 900.0, "wave_dir_deg": 0.0, "sea_ice_conc_pct": 50.0}[n] for n in names}
        return S()


GLOBAL = LatLonGrid(-180, -80, 4, 4, 90, 41)
TILE = LatLonGrid(52.5, 22.5, 1, 1, 9, 9)  # 22.5..30.5 N, 52.5..60.5 E


class TestComposite(unittest.TestCase):
    def setUp(self):
        self.tile = const(TILE, 1010.0, T0, 168, 1, wave_dir=350.0)
        self.opening = const(GLOBAL, 1000.0, T0, 168, 3, wave_dir=10.0)
        self.s0 = const(GLOBAL, 990.0, T0, 336)
        self.s1 = const(GLOBAL, 980.0, T0 + dt.timedelta(days=14), 336)
        self.c = MnoEnvComposite([("tile", self.tile, True, True), ("opening", self.opening, False, True),
                                  ("s0", self.s0), ("s1", self.s1)], ("PROC", Fallback()))
        self.t = to_seconds(T0 + dt.timedelta(hours=24))

    def p(self, t, lat, lon):
        return self.c.sample(t, lat, lon, ["msl_pressure_hpa"])

    def test_inside_tile_and_feathered_border(self):
        self.assertEqual(self.p(self.t, 26.5, 56.5).values["msl_pressure_hpa"], 1010.0)
        edge = self.p(self.t, 23.0, 56.5)  # 0.5 deg inside the tile's southern border
        self.assertAlmostEqual(edge.values["msl_pressure_hpa"], 1005.0, places=3)
        self.assertEqual(self.p(self.t, 21.0, 56.5).values["msl_pressure_hpa"], 1000.0)  # outside: opening grid

    def test_opening_hands_over_to_season_smoothly(self):
        end = to_seconds(T0 + dt.timedelta(hours=168))
        vals = [self.p(end - h * 3600, 0, 0).values["msl_pressure_hpa"] for h in (13, 12, 6, 0)]
        self.assertEqual(vals[0], 1000.0)
        self.assertAlmostEqual(vals[2], 995.0, places=3)  # half-way through the 12 h feather
        self.assertAlmostEqual(vals[3], 990.0, places=3)
        self.assertEqual(self.p(end + 3600, 0, 0).values["msl_pressure_hpa"], 990.0)

    def test_season_chunks_never_fall_back_to_procedural(self):
        b = to_seconds(T0 + dt.timedelta(days=14))
        for dh in (-6, -1, 0, 1, 6):
            v = self.p(b + dh * 3600, 0, 0)
            self.assertIn(v.sources["msl_pressure_hpa"], ("s0", "s1"))
            self.assertIn(v.values["msl_pressure_hpa"], (990.0, 980.0))
        self.assertEqual(self.p(to_seconds(T0 + dt.timedelta(days=40)), 0, 0).sources["msl_pressure_hpa"], "PROC")

    def test_direction_not_averaged_and_ice_from_fallback(self):
        s = self.c.sample(self.t, 23.0, 56.5, ["wave_dir_deg", "sea_ice_conc_pct"])
        self.assertIn(s.values["wave_dir_deg"], (350.0, 10.0))  # never 180, the meaningless mean
        self.assertEqual(s.sources["sea_ice_conc_pct"], "PROC")


if __name__ == "__main__":
    unittest.main()
