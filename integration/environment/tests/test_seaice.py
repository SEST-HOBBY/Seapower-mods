import datetime as dt
import statistics
import sys
import unittest

from helpers import ENV_ROOT, HERE, UTC

from mno_env import seaice

sys.path.insert(0, str(ENV_ROOT / "tools"))
import refresh_seaice_climatology  # noqa: E402


class TestClimatology(unittest.TestCase):
    def test_table_matches_official_csv(self):
        # Two of NSIDC's own files are kept as fixtures; the stored table must agree with them.
        for name, hemi, month in (("N_03.csv", "north", 3), ("S_09.csv", "south", 9)):
            vals = refresh_seaice_climatology.parse(HERE / "fixtures" / "nsidc" / name)
            for period, (y0, y1) in refresh_seaice_climatology.PERIODS.items():
                med = round(statistics.median(v for y, v in vals.items() if y0 <= y <= y1), 2)
                self.assertEqual(seaice.table(hemi, period)[month - 1], med, (name, period))

    def test_season_shape(self):
        n, s = seaice.table("north"), seaice.table("south")
        self.assertEqual(n.index(max(n)) + 1, 3)   # Arctic maximum in March
        self.assertEqual(n.index(min(n)) + 1, 9)   # minimum in September
        self.assertEqual(s.index(max(s)) + 1, 9)   # Antarctic maximum in September
        self.assertEqual(s.index(min(s)) + 1, 2)   # minimum in February
        self.assertLess(seaice.table("north")[8], seaice.table("north", "1981_2010")[8])  # recent Arctic summers are lower

    def test_interpolation_between_mid_months(self):
        a = seaice.target_extent("north", dt.datetime(2028, 3, 15, tzinfo=UTC))
        b = seaice.target_extent("north", dt.datetime(2028, 4, 15, tzinfo=UTC))
        mid = seaice.target_extent("north", dt.datetime(2028, 3, 30, 12, tzinfo=UTC))
        self.assertAlmostEqual(mid, (a + b) / 2, delta=0.01)
        self.assertAlmostEqual(seaice.target_extent("south", dt.datetime(2028, 12, 31, 23, tzinfo=UTC)),
                               seaice.target_extent("south", dt.datetime(2029, 1, 1, 0, tzinfo=UTC)), delta=0.01)  # continuous across the year

    def test_calibrated_extent_and_edge_shift(self):
        mar = dt.datetime(2028, 3, 15, tzinfo=UTC)
        sep = dt.datetime(2028, 9, 15, tzinfo=UTC)
        em, es = seaice.edges_on(mar), seaice.edges_on(sep)
        for h, w, e in (("north", mar, em), ("south", sep, es), ("north", sep, es), ("south", mar, em)):
            self.assertAlmostEqual(seaice.extent(h, e[h]), seaice.target_extent(h, w), delta=0.1)
        self.assertLess(em["north"], es["north"])   # Arctic edge further from the pole in March
        self.assertLess(es["south"], em["south"])   # Antarctic edge further north in September
        self.assertGreater(seaice.ice_at(-62, -40, es), 50)   # Weddell outflow iced in September
        self.assertLess(seaice.ice_at(-62, -40, em), 15)      # open in March
        self.assertLess(seaice.ice_at(72, 20, es), 15)        # Barents Sea open in September
        self.assertEqual(seaice.ice_at(10, 0, es), 0.0)


if __name__ == "__main__":
    unittest.main()
