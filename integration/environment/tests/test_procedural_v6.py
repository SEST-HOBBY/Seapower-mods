"""Regression tests for procedural weather v6: land and coast (answers to the land review)."""
import datetime as dt
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env import landphys, procedural as P, seaice  # noqa: E402
from mno_env.clock import MnoEnvState, to_seconds  # noqa: E402
from mno_env.mission_adapter import mission_weather_plan, native_state  # noqa: E402

UTC = dt.timezone.utc


def sample_at(seed, t, points, res=2.5):
    snap = P.generate(seed, t, hours=0, res_deg=res)
    st = MnoEnvState(snap)
    return {k: st.sample(to_seconds(t), la, lo).values for k, (la, lo) in points.items()}


class TestLandV6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pts = {"yakutsk": (62.0, 129.7), "riyadh": (24.7, 46.7), "bab": (12.6, 43.4), "taiwan": (24.5, 119.5),
               "gulf": (27.0, 51.0), "aegean": (37.5, 25.0), "atlantic": (45.0, -30.0)}
        cls.jan = [sample_at(s, dt.datetime(2029, 1, d, tzinfo=UTC), pts) for s in ("a", "b") for d in (8, 22)]
        cls.jul = [sample_at(s, dt.datetime(2029, 7, d, tzinfo=UTC), pts) for s in ("a", "b") for d in (8, 22)]
        cls.aug = [sample_at(s, dt.datetime(2029, 8, d, tzinfo=UTC), pts) for s in ("a", "b") for d in (8, 22)]

    @staticmethod
    def mean(rows, k, f):
        return sum(r[k][f] for r in rows) / len(rows)

    def test_continental_and_desert_temperature(self):
        self.assertLess(self.mean(self.jan, "yakutsk", "air_temp_2m_c"), -25)
        self.assertGreater(self.mean(self.jul, "yakutsk", "air_temp_2m_c"), 12)
        self.assertGreater(self.mean(self.jul, "riyadh", "air_temp_2m_c"), 33)
        self.assertLess(self.mean(self.jan, "riyadh", "air_temp_2m_c"), 20)

    def test_bab_el_mandeb_is_dry_in_summer(self):
        self.assertTrue(all(not native_state(r["bab"], initial=False).rain for r in self.jul + self.aug))
        self.assertLess(self.mean(self.jul, "riyadh", "cloud_fraction_pct"), 40)

    def test_regional_winds(self):
        import math
        def frm(rows, k):
            u = sum(r[k]["wind_u10_ms"] for r in rows); v = sum(r[k]["wind_v10_ms"] for r in rows)
            return (math.degrees(math.atan2(-u, -v)) + 360) % 360
        self.assertTrue(10 <= frm(self.jan, "taiwan") <= 60)     # winter north-east monsoon
        self.assertTrue(300 <= frm(self.jul, "gulf") <= 350)     # shamal from the north-west
        d = frm(self.jul, "aegean")
        self.assertTrue(d >= 330 or d <= 40)                      # etesians from the north

    def test_snowfall_and_land_wind(self):
        r = self.jan[0]["yakutsk"]
        self.assertIn("snowfall_rate_mm_h", r)
        self.assertLessEqual(r["snowfall_rate_mm_h"], r["precip_rate_mm_h"] + 1e-6)
        self.assertLess(landphys.roughness(1.0, 50.0), 0.8)
        self.assertEqual(landphys.roughness(0.2, 50.0), 1.0)
        self.assertGreater(landphys.continentality(62.0, 129.7), 0.8)
        self.assertLess(landphys.continentality(55.75, 37.6), 0.6)


class TestSeaFillAndFog(unittest.TestCase):
    def test_coastal_land_nodes_carry_sea_ice(self):
        g = P.LatLonGrid(-180.0, -90.0, 2.5, 2.5, 144, 73)
        t = dt.datetime(2029, 2, 15, tzinfo=UTC)
        out = P._frame("fill", t, g, seaice.edges_on(t, res=2.5), P._hours(t) / 6.0)
        land = P._land_nodes(g)
        plan = P._fill_plan(g, land)
        filled = [k for k, nb in enumerate(plan) if nb]
        self.assertTrue(any(out["sea_ice_conc_pct"][k] > 50 for k in filled))
        for k in filled[:500]:
            nb = plan[k]
            self.assertAlmostEqual(out["wave_hs_m"][k], sum(out["wave_hs_m"][q] for q in nb) / len(nb), places=1)

    def test_extinction_interpolation_keeps_fog(self):
        from mno_env.snapshot import pack_int16
        snap = P.generate("ext", dt.datetime(2029, 7, 10, tzinfo=UTC), hours=6)
        g = P.LatLonGrid.from_dict(snap["grid"])
        vis = [20.0] * (g.nx * g.ny)
        k = 30 * g.nx + 30
        vis[k] = 0.3
        for fr in snap["times"]:
            fr["values"]["visibility_km"] = pack_int16(vis, P.PACK["visibility_km"])
        st = MnoEnvState(snap)
        la, lo = g.lat(30) + 0.3 * g.lat_step, g.lon(30) + 0.3 * g.lon_step  # off the foggy node
        self.assertLess(st.sample(to_seconds(dt.datetime(2029, 7, 10, 3, tzinfo=UTC)), la, lo, ["visibility_km"]).values["visibility_km"], 1.0)

    def test_fog_needs_two_samples_to_change(self):
        class Flicker:
            def sample(self, t, lat, lon):
                from types import SimpleNamespace
                vis = 0.5 if (t // 1800) % 4 == 1 else 15.0   # a single foggy sample every 4
                return SimpleNamespace(values={"visibility_km": vis, "cloud_fraction_pct": 50, "wave_hs_m": 1.0,
                                               "precip_rate_mm_h": 0.0, "wind_u10_ms": 4.0, "wind_v10_ms": 0.0})
        plan = mission_weather_plan(Flicker(), 0, 0.0, 0.0, duration_s=8 * 3600, step_s=1800)
        self.assertEqual(len(plan), 1)  # one-sample fog never becomes a trigger


if __name__ == "__main__":
    unittest.main()
