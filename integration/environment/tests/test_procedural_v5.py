"""Regression tests for procedural weather v5 (answers to the independent critique of v4)."""
import datetime as dt
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env import procedural as P  # noqa: E402
from mno_env import seaice  # noqa: E402
from mno_env.grid import LatLonGrid  # noqa: E402

UTC = dt.timezone.utc
G4 = LatLonGrid(-180.0, -90.0, 4.0, 4.0, 90, 46)


def frame(seed, t):
    return P._frame(seed, t, G4, seaice.edges_on(t, res=4.0), P._hours(t) / 6.0)


def cell(lat, lon):
    return int(round((lat + 90) / 4)) * G4.nx + int(round((lon + 180) / 4)) % G4.nx


class TestV5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jul = frame("v5", dt.datetime(2029, 7, 16, tzinfo=UTC))
        cls.sep = frame("v5", dt.datetime(2028, 9, 14, tzinfo=UTC))

    def test_pack_ice_damps_waves(self):
        land = P._land_nodes(G4)
        for out in (self.jul, self.sep):
            for ice, hs, l in zip(out["sea_ice_conc_pct"], out["wave_hs_m"], land):
                if ice >= 80 and not l:
                    self.assertLess(hs, 0.05)

    def test_no_ice_on_land_and_single_valued_poles(self):
        land = P._land_nodes(G4)
        plan = P._fill_plan(G4, land)
        for out in (self.jul, self.sep):
            # v6: land nodes carry the neighbouring sea value; interior land (no sea nearby) has none
            self.assertTrue(all(v == 0.0 for v, nb in zip(out["sea_ice_conc_pct"], plan) if nb == ()))
            for j in (0, G4.ny - 1):
                row = slice(j * G4.nx, (j + 1) * G4.nx)
                for f in ("sea_ice_conc_pct", "msl_pressure_hpa"):
                    self.assertEqual(len(set(out[f][row])), 1, f)
                self.assertTrue(all(v == 0.0 for v in out["wind_u10_ms"][row] + out["wind_v10_ms"][row]))

    def test_central_arctic_keeps_its_pack_in_september(self):
        for lon in range(-180, 180, 8):
            self.assertGreater(self.sep["sea_ice_conc_pct"][cell(84, lon)], 75, lon)

    def test_summer_monsoon_is_south_westerly(self):
        u = [self.jul["wind_u10_ms"][cell(la, lo)] for la in (12, 16) for lo in (60, 64, 68)]
        self.assertGreater(sum(u) / len(u), 5.0)  # Arabian Sea in July

    def test_noise_has_no_seam_and_is_not_periodic(self):
        h = P._hours(dt.datetime(2028, 9, 14, tzinfo=UTC))
        for lon in range(-180, 180, 20):
            self.assertLess(abs(P._waves_noise("s", 24.999, lon, h, "c") - P._waves_noise("s", 25.001, lon, h, "c")), 0.01)
        series = [P._waves_noise("s", 45.0, -30.0, h + 6 * k, "p") for k in range(4 * 120)]
        n = len(series)
        mean = sum(series) / n
        x = [v - mean for v in series]
        var = sum(v * v for v in x)
        peak = max((sum(v * math.cos(2 * math.pi * f * k / n) for k, v in enumerate(x)) ** 2
                    + sum(v * math.sin(2 * math.pi * f * k / n) for k, v in enumerate(x)) ** 2) * 2 / n
                   for f in range(1, n // 2))
        self.assertLess(peak / var, 0.35)  # no single period dominates

    def test_cyclone_land_decay_is_cumulative(self):
        flags = (0, 0, 1, 1, 1, 0, 0)
        days = [P._land_days(flags, a / 8) for a in range(0, 14)]
        self.assertEqual(days, sorted(days))  # never decreases, so strength never returns
        self.assertAlmostEqual(P._land_days(flags, 1.75), 0.75)
        seed = "v5-tc"
        t0 = dt.datetime(2029, 10, 1, tzinfo=UTC)
        best = {}
        for k in range(4 * 60):
            for s in P.active_storms(seed, t0 + dt.timedelta(hours=6 * k)):
                if s["kind"] != "tropical":
                    continue
                key = (s["t0"], s["basin"])
                over = P._land().is_land(s["lat"], s["lon"])
                rec = best.setdefault(key, {"pre": 0.0, "landed": False, "after": 0.0})
                if over:
                    rec["landed"] = True
                elif not rec["landed"]:
                    rec["pre"] = max(rec["pre"], s["intensity"])
                elif P._land_days(P._tc_land_flags(seed, s["t0"] // 6, s["basin"], (P.EPOCH + dt.timedelta(hours=s["t0"])).month), s["age_d"]) > 0.5:
                    rec["after"] = max(rec["after"], s["intensity"])
        crossed = [r for r in best.values() if r["landed"] and r["pre"] > 0.3]
        self.assertGreaterEqual(len(crossed), 2)  # the window really contains landfalls
        for r in crossed:
            self.assertLess(r["after"], 0.8 * r["pre"])

    def test_snapshot_id_carries_version_and_step(self):
        t = dt.datetime(2028, 9, 14, 6, tzinfo=UTC)
        a = P.generate("id", t, hours=6, step_hours=6)
        b = P.generate("id", t, hours=6, step_hours=1)
        self.assertNotEqual(a["snapshot_id"], b["snapshot_id"])
        self.assertTrue(a["snapshot_id"].endswith("-v" + P.VERSION.rsplit(".", 1)[-1]))
        self.assertIn("6hstep", a["snapshot_id"])


class TestSeaIceV5(unittest.TestCase):
    def test_extent_matches_nsidc_on_the_sampled_grid(self):
        for m in (3, 9):
            t = dt.datetime(2029, m, 15, tzinfo=UTC)
            e = seaice.edges_on(t, res=4.0)
            for h in ("north", "south"):
                got = seaice.extent_on_grid(h, e[h], 4.0, e["sh_summer"] if h == "south" else 0.0)
                self.assertAlmostEqual(got, seaice.target_extent(h, t), delta=0.1)

    def test_regional_ice_where_it_belongs(self):
        mar = seaice.edges_on(dt.datetime(2029, 3, 15, tzinfo=UTC))
        sep = seaice.edges_on(dt.datetime(2029, 9, 14, tzinfo=UTC))
        feb = seaice.edges_on(dt.datetime(2029, 2, 20, tzinfo=UTC))
        self.assertGreater(seaice.ice_at(60, -85, mar), 80)    # Hudson Bay frozen in March
        self.assertGreater(seaice.ice_at(57, 145, mar), 50)    # northern Sea of Okhotsk (regional calibration, SEA-ICE-MARGINAL-SEAS.md)
        self.assertGreater(seaice.ice_at(65, 23, mar), 50)     # Bothnian Bay
        self.assertLess(seaice.ice_at(62, -35, mar), 15)       # Irminger Sea open
        self.assertLess(seaice.ice_at(58, -85, sep), 15)       # Hudson Bay open in September
        self.assertGreater(seaice.ice_at(86, 16, sep), 80)     # central Arctic keeps its pack
        self.assertLess(seaice.ice_at(-75, -175, feb), 30)     # Ross Sea opens at the minimum
        self.assertGreater(seaice.ice_at(-68, -55, feb), 30)   # western Weddell pack survives
        self.assertGreater(seaice.ice_at(-72, -110, feb), 30)  # Amundsen pack survives


if __name__ == "__main__":
    unittest.main()
