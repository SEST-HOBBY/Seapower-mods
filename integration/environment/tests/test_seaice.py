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


class TestReviewFixes(unittest.TestCase):
    def test_edge_is_the_15_percent_line(self):
        for h, lat in (("north", 70.0), ("south", -65.0)):
            shape = seaice.edge_shape(h, 30.0, 0.0, lat)
            self.assertAlmostEqual(seaice.concentration(h, lat, 30.0, abs(lat) + shape), 15.0, places=6)

    def test_ice_shelves_are_not_sea_ice_area(self):
        from mno_env import ice
        shelves = ice.load_shelves()
        cells = seaice._ocean_cells()
        self.assertFalse(any(lat < -60 and any(s.contains(lat, lon) for s in shelves) for lat, lon, _ in cells[:4000]))
        self.assertFalse(any(abs(lat + 81.5) < 0.01 and abs(lon + 175.5) < 0.01 for lat, lon, _ in cells))  # Ross Ice Shelf cell

    def test_unreachable_target_refused(self):
        with self.assertRaises(ValueError):
            seaice.base_edge_for("north", 80.0)

    def test_refresh_requires_every_recent_year(self):
        import shutil
        import tempfile
        from pathlib import Path
        src = HERE / "fixtures" / "nsidc" / "N_03.csv"
        with tempfile.TemporaryDirectory() as d:
            lines = src.read_text().splitlines()
            for m in range(1, 13):
                for pre in ("N", "S"):
                    keep = [ln for ln in lines if not ln.startswith("2025")] if (pre, m) == ("N", 12) else lines
                    Path(d, f"{pre}_{m:02d}.csv").write_text("\n".join(keep) + "\n")
            with self.assertRaises(SystemExit):
                refresh_seaice_climatology.main(["--cache", d, "--out", str(Path(d) / "out.json")])
            shutil.copy(src, Path(d) / "N_12.csv")
            refresh_seaice_climatology.main(["--cache", d, "--out", str(Path(d) / "out.json")])
