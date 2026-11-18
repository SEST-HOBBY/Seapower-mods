import datetime as dt
import math
import statistics
import unittest

from helpers import UTC

from mno_env import procedural as P
from mno_env.clock import MnoEnvState, to_seconds

T = dt.datetime(2028, 9, 14, tzinfo=UTC)


class TestProceduralV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.st = MnoEnvState(P.generate("phys", T, hours=0, res_deg=4.0))
        cls.t = to_seconds(T)

    def zonal(self, name, lat):
        return statistics.mean(self.st.sample(self.t, lat, lon, [name]).values[name] for lon in range(-180, 180, 8))

    def test_wind_belts(self):
        self.assertLess(self.zonal("wind_u10_ms", 0), -3)     # easterly trades
        self.assertGreater(self.zonal("wind_u10_ms", -45), 4)  # Southern Ocean westerlies
        self.assertGreater(self.zonal("wind_u10_ms", 45), 1)   # northern westerlies
        self.assertGreater(self.zonal("msl_pressure_hpa", -30), self.zonal("msl_pressure_hpa", -60) + 20)

    def test_circulation_around_lows(self):
        checked = 0
        for s in P.active_storms("phys", T):
            if s["kind"] != "extratropical" or s["intensity"] < 0.5 or abs(s["lat"]) > 65:
                continue
            r = 0.6 * s["radius"]
            circ = 0.0
            for k in range(8):  # line integral of the wind around the centre
                a = 2 * math.pi * k / 8
                lat = s["lat"] + r * math.sin(a)
                lon = s["lon"] + r * math.cos(a) / math.cos(math.radians(s["lat"]))
                v = self.st.sample(self.t, lat, lon, ["wind_u10_ms", "wind_v10_ms"]).values
                circ += -v["wind_u10_ms"] * math.sin(a) + v["wind_v10_ms"] * math.cos(a)
            self.assertEqual(circ > 0, s["lat"] > 0, s)  # anticlockwise in the north, clockwise in the south
            checked += 1
        self.assertGreater(checked, 3)

    def test_tropical_cyclones_only_in_season(self):
        march = [s for s in P.active_storms("phys", dt.datetime(2029, 3, 10, tzinfo=UTC)) if s.get("basin") == "NATL"]
        self.assertEqual(march, [])

    def test_storms_live_and_die(self):
        ids_seen, counts = set(), []
        for d in range(0, 60, 2):
            now = P.active_storms("phys", T + dt.timedelta(days=d))
            counts.append(len(now))
            ids_seen |= {(s["kind"], s["t0"], round(s["lat0"], 2)) for s in now}
        self.assertTrue(all(8 <= c <= 45 for c in counts), counts)
        self.assertGreater(len(ids_seen), 120)  # many different storms over two months, not the same few
        for s in P.active_storms("phys", T):
            self.assertLessEqual(s["age_d"], s["life_d"])

    def test_deterministic_and_windows_join(self):
        a = P.generate("phys", T, hours=12, res_deg=5.0)
        b = P.generate("phys", T + dt.timedelta(hours=6), hours=6, res_deg=5.0)
        self.assertEqual(a["times"][1]["values"], b["times"][0]["values"])  # the shared frame is identical


if __name__ == "__main__":
    unittest.main()
