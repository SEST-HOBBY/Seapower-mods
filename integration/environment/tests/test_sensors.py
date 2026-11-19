"""Sensor environment: reference values from the sensor review's acceptance list."""
import datetime as dt
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env import sensors as S  # noqa: E402
from mno_env.sensor_brief import brief_lines  # noqa: E402

UTC = dt.timezone.utc


class TestSensors(unittest.TestCase):
    def test_sonar_terms(self):
        self.assertAlmostEqual(S.duct_cutoff_hz(30.48), 580, delta=30)       # Urick
        self.assertAlmostEqual(S.duct_cutoff_hz(100.0), 97, delta=3)
        self.assertEqual(S.rain_noise_suggest(0.1, 3), 15.0)                  # no Rain flag: game value
        self.assertGreater(S.rain_noise_suggest(10.0, 2), S.rain_noise_suggest(1.0, 2))
        self.assertTrue(3.0 <= S.rain_noise_suggest(1.0, 5) <= 20.0)
        self.assertTrue(57 <= S.ambient_suggest(6, 1, False) <= 66)
        self.assertLessEqual(S.ambient_suggest(20, 1, False), 66)             # shipping capped
        _, h = S.mixed_layer_m(60, dt.datetime(2028, 7, 14, tzinfo=UTC), 20.0)
        self.assertTrue(40 <= h <= 70)                                        # summer layer deepened by a gale
        _, h = S.mixed_layer_m(3, dt.datetime(2028, 9, 14, tzinfo=UTC), 10.0, "shallow")
        self.assertLessEqual(h, 80)

    def test_radar_terms(self):
        self.assertAlmostEqual(S.rain_atten_db_km(10, "X"), 0.22, delta=0.01)  # ITU-R P.838-3
        self.assertAlmostEqual(S.rain_atten_db_km(10, "S"), 0.0024, delta=0.0003)
        self.assertAlmostEqual(S.sea_clutter_db(3, 1.0), -43.7, delta=0.6)    # NRL, X band
        self.assertLess(S.multipath(3.0, 10.0)["rho_1deg"], 0.15)
        self.assertAlmostEqual(S.multipath(3.0, 10.0)["rho_0.115deg"], 0.85, delta=0.04)
        self.assertTrue(2 <= S.evaporation_duct_m(4, 3, 85, 12)[0] <= 10)     # cold
        self.assertTrue(9 <= S.evaporation_duct_m(28, 28, 78, 7)[0] <= 16)    # neutral tropical
        self.assertEqual(S.evaporation_duct_m(30, 33, 60, 6)[1], "stable")
        self.assertEqual(S.evaporation_duct_m(20, 20, 100, 5)[0], 0.0)

    def test_eo_ir_and_moon(self):
        self.assertTrue(0.4 <= S.ir_range_factor(30, 80, 0, 23, "LWIR") <= 0.65)
        self.assertTrue(0.9 <= S.ir_range_factor(0, 85, 0, 23, "LWIR") <= 1.3)
        self.assertLess(S.ir_range_factor(15, 80, 10, 23, "LWIR"), 0.5)
        self.assertAlmostEqual(S.sun_moon(dt.datetime(2028, 9, 14, tzinfo=UTC))["illum"], 0.29, delta=0.03)
        self.assertLess(S.sun_moon(dt.datetime(2028, 9, 18, 18, 30, tzinfo=UTC))["illum"], 0.01)   # new moon
        self.assertGreater(S.sun_moon(dt.datetime(2028, 10, 3, 16, 30, tzinfo=UTC))["illum"], 0.99)  # full moon

    def test_derive_and_brief_never_fail(self):
        t = dt.datetime(2028, 9, 14, tzinfo=UTC)
        for th in list(S.THEATRES) + [None]:
            env = S.derive({}, 26.5, 56.5, t, th)                             # empty sample: climatology only
            lines = brief_lines(env)
            self.assertTrue(3 <= len(lines) <= 12)
            self.assertTrue(all(l.startswith(("GAME:", "REAL-WORLD:", "UNTESTED")) for l in lines))
        env = S.derive({"wind_u10_ms": 5, "wind_v10_ms": 0, "wave_hs_m": 1.0, "precip_rate_mm_h": 0, "air_temp_2m_c": 31,
                        "visibility_km": 0.5, "cloud_fraction_pct": 80}, 26.5, 56.5, t, "hormuz")
        self.assertEqual(env["game_sea_state"].value, 3)
        self.assertEqual(env["game_ambient_db"].value, 75.0)
        self.assertIsNone(env["convergence_zones"].value)
        self.assertEqual(S.derive({}, -35, 19, t, "cape-of-good-hope")["convergence_zones"].value, (32.0, 64.0))


if __name__ == "__main__":
    unittest.main()
