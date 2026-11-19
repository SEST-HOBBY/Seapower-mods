"""Fog/visibility and polar routes."""
import datetime as dt
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "tools"))

from mno_env import procedural, seaice, snapshot  # noqa: E402
from mno_env import visibility as V  # noqa: E402
from mno_env.geo import default_land_mask, sample_leg  # noqa: E402
from mno_env.mission_adapter import native_state  # noqa: E402

UTC = dt.timezone.utc
JUL = dt.datetime(2029, 7, 10, tzinfo=UTC)
JAN = dt.datetime(2029, 1, 10, tzinfo=UTC)


class TestVisibility(unittest.TestCase):
    def test_fog_climatology_where_and_when(self):
        self.assertGreater(V.fog_frequency(45, -50, JUL), 0.25)    # Grand Banks summer
        self.assertLess(V.fog_frequency(45, -50, JAN), 0.08)       # rare in winter
        self.assertGreater(V.fog_frequency(46, 152, JUL), 0.3)     # Kuril / Oyashio
        self.assertLess(V.fog_frequency(24, -40, JUL), 0.01)       # open subtropical ocean
        self.assertLess(V.fog_frequency(0, -140, JAN), 0.01)

    def test_weather_modulates_fog(self):
        calm = V.fog_probability(lat=45, lon=-50, t=JUL, wind_ms=5, v_ms=2, rain_mm_h=0, land=False)
        gale = V.fog_probability(lat=45, lon=-50, t=JUL, wind_ms=20, v_ms=2, rain_mm_h=0, land=False)
        wet = V.fog_probability(lat=45, lon=-50, t=JUL, wind_ms=5, v_ms=2, rain_mm_h=3, land=False)
        self.assertGreater(calm, 3 * gale)
        self.assertEqual(wet, 0.0)

    def test_rain_snow_dust_and_sea_smoke(self):
        base = dict(lat=10, lon=-30, t=JUL, v_ms=0, ice_pct=0, land=False, fog_noise=1.0, dust_noise=0.0)
        self.assertGreater(V.visibility_km(wind_ms=5, rain_mm_h=0, temp_c=25, **base), 15)
        self.assertLess(V.visibility_km(wind_ms=5, rain_mm_h=20, temp_c=25, **base), 2.5)   # heavy rain
        self.assertLess(V.visibility_km(wind_ms=5, rain_mm_h=2, temp_c=-3, **base), 1.0)    # heavy snow
        gulf = dict(base, lat=26, lon=56, dust_noise=0.6)
        self.assertLess(V.visibility_km(wind_ms=12, rain_mm_h=0, temp_c=35, **gulf), 3.0)   # shamal dust
        arctic = dict(base, lat=75, lon=40, t=JAN)
        self.assertLess(V.visibility_km(wind_ms=8, rain_mm_h=0, temp_c=-30, **arctic), 1.5)  # sea smoke

    def test_procedural_writes_visibility_and_game_sees_fog(self):
        snap = procedural.generate("fog-test", JUL, hours=6)
        self.assertEqual(snapshot.validate(snap), [])
        self.assertIn("visibility_km", snap["fields"])
        st = native_state({"cloud_fraction_pct": 90, "visibility_km": 0.4, "wave_hs_m": 1.0}, initial=False)
        self.assertTrue(st.fog)


class TestPolarRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((HERE.parent / "data" / "polar-routes.json").read_text(encoding="utf-8"))

    def test_routes_stay_at_sea_on_the_game_mask(self):
        land = default_land_mask()
        for r in self.doc["routes"]:
            pts = [tuple(p) for p in r["points"]]
            bad = [p for a, b in zip(pts, pts[1:]) for p in sample_leg(a, b, 10.0) if land.is_land(*p)]
            self.assertEqual(bad, [], r["name"])

    def test_data_file_matches_the_generator(self):
        import build_polar_routes
        built = build_polar_routes.build()
        self.assertEqual([[list(p) for p in r["points"]] for r in built["routes"]], [r["points"] for r in self.doc["routes"]])

    def test_northern_sea_route_season(self):
        nsr = next(r for r in self.doc["routes"] if r["name"].startswith("Northern Sea Route (coastal)"))
        pts = [tuple(p) for p in nsr["points"]]
        samples = [p for a, b in zip(pts, pts[1:]) for p in sample_leg(a, b, 30.0)]

        def peak(t):
            e = seaice.edges_on(t)
            return max(seaice.ice_at(la, lo, e) for la, lo in samples)
        self.assertLess(peak(dt.datetime(2029, 9, 15, tzinfo=UTC)), 30)   # open at the September minimum
        self.assertGreater(peak(dt.datetime(2029, 3, 15, tzinfo=UTC)), 90)  # closed in winter


if __name__ == "__main__":
    unittest.main()
