import datetime as dt
import json
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


class TestMarginalSeas(unittest.TestCase):
    """Sea of Okhotsk, Bering Sea and Chukchi Sea regional calibration (docs/environment/SEA-ICE-MARGINAL-SEAS.md).
    Reference: NSIDC G02135 v4.0 regional monthly extent (medians stored in seaice.py)."""

    @staticmethod
    def on(month, day=15, baseline=seaice.DEFAULT_BASELINE):
        return seaice.edges_on(dt.datetime(2028, month, day, 12, tzinfo=UTC), baseline)

    def test_regional_extent_matches_nsidc(self):
        for baseline, months in (("2016_2025", range(1, 13)), ("1981_2010", (1, 3, 5, 6, 12))):
            for m in months:
                e = self.on(m, baseline=baseline)
                for name in seaice.MARGINAL_SEAS:
                    target = seaice.MARGINAL_SEAS[name]["targets"][baseline][m - 1]
                    got = seaice.marginal_extent(name, e["marginal"][name])
                    self.assertAlmostEqual(got, target, delta=15.0, msg=(baseline, m, name))

    def test_okhotsk_season_shape(self):
        t = seaice.MARGINAL_SEAS["okhotsk"]["targets"]["2016_2025"]
        self.assertIn(t.index(max(t)) + 1, (2, 3))   # NSIDC maximum late Feb to early March
        self.assertLess(t[5], 100.0)                 # below 100 thousand km2 by mid-June (NSIDC: about 1 June)
        self.assertEqual(t[6:10], (0.0, 0.0, 0.0, 0.0))
        cells = seaice._marginal_cells("okhotsk")
        for m in (7, 8, 9, 10):                      # ice-free from July to October
            e = self.on(m)
            self.assertEqual(max(seaice.ice_at(la, lo, e) for la, lo, _a in cells), 0.0, m)
        # the old constant shift kept 59N 145E at 92 % in July and 67 % in October
        self.assertLess(seaice.ice_at(59, 145, self.on(7)), 1.0)
        self.assertLess(seaice.ice_at(59, 145, self.on(10)), 1.0)
        self.assertGreater(seaice.ice_at(59, 145, self.on(3)), 85)

    def test_okhotsk_last_ice_is_in_the_shantar_corner(self):
        # NSIDC G02135 monthly extent polygons 2016-2025: June ice at Shantar / Sakhalin Gulf (5-9 of
        # 10 years) and Shelikhov Gulf (8-10 of 10); none on the north coast off Okhotsk town.
        # Britannica (Sea of Okhotsk): floes stay "in the Sakhalin gulfs and around Shantar Island".
        cells = seaice._marginal_cells("okhotsk")
        _s, lat, lon = max((seaice.ice_order("okhotsk", la, lo), la, lo) for la, lo, _a in cells)
        self.assertTrue(53 <= lat <= 56 and 136 <= lon <= 142, (lat, lon))
        late_june = self.on(6, 25)
        iced = [(la, lo) for la, lo, _a in cells if seaice.ice_at(la, lo, late_june) >= 15]
        self.assertTrue(iced)
        for la, lo in iced:
            self.assertTrue((53 <= la <= 57 and 135 <= lo <= 142) or (60 <= la <= 63 and 158 <= lo <= 166), (la, lo))
        self.assertLess(seaice.ice_at(59, 143.5, self.on(6, 20)), 15)   # was 63 % before the fix
        self.assertLess(seaice.ice_at(59, 143.5, self.on(7, 1)), 1)

    def test_okhotsk_march_edge_matches_the_nsidc_median_line(self):
        # NSIDC G02135 v4.0 median_extent_N_03_1981-2010_polyline: the edge crosses 150E at 54.8N,
        # 152E at 55.8N and 154.5E at 57.5N (so 52N 150E is open in the median March).
        e = self.on(3, baseline="1981_2010")
        for lon, median_lat in ((150.0, 54.77), (152.0, 55.82), (154.5, 57.49)):
            lat = next(la / 100 for la in range(5000, 6000, 5) if seaice.ice_at(la / 100, lon, e) >= 15)
            self.assertLess(abs(lat - median_lat), 1.5, (lon, lat, median_lat))
        self.assertLess(seaice.ice_at(52, 150, e), 15)

    def test_okhotsk_melt_order(self):
        # North-west shelf and Shantar corner keep ice longest (residual ice in June); south-east first.
        jun, mar = self.on(6), self.on(3)
        self.assertGreater(seaice.ice_at(55, 137.5, jun), 15)   # Shantar / Sakhalin Gulf residual ice
        self.assertLess(seaice.ice_at(51, 152, jun), 1)         # central basin open
        self.assertLess(seaice.ice_at(47, 152, mar), 15)        # Kuril Basin open even at the maximum
        self.assertGreater(seaice.ice_at(55, 138, mar), 85)     # NW shelf close pack in March
        self.assertGreater(seaice.ice_at(51, 141, mar), 50)     # northern Tatar Strait frozen
        self.assertLess(seaice.ice_at(45, 139, mar), 1)         # Sea of Japan open (Tsushima Current)

    def test_hokkaido_drift_ice_season(self):
        # JMA Abashiri normals: first drift ice 22 January (1991-2020), last ice 11 April (1981-2010).
        for baseline in ("1981_2010", "2016_2025"):
            self.assertLess(seaice.ice_at(44.5, 144.5, self.on(1, 1, baseline)), 15, baseline)
            self.assertGreater(seaice.ice_at(44.5, 144.5, self.on(2, 15, baseline)), 15, baseline)
            self.assertLess(seaice.ice_at(44.5, 144.5, self.on(4, 20, baseline)), 15, baseline)

    def test_bering_winter_ice_and_open_summer(self):
        self.assertGreater(seaice.ice_at(62, -168, self.on(3)), 85)   # northern shelf iced in March
        self.assertLess(seaice.ice_at(55, -178, self.on(3)), 1)       # Aleutian Basin open
        cells = seaice._marginal_cells("bering")
        for m in (7, 8, 9, 10):
            e = self.on(m)
            self.assertEqual(max(seaice.ice_at(la, lo, e) for la, lo, _a in cells), 0.0, m)

    def test_bering_strait_has_no_seam_in_winter(self):
        # NSIDC G02135 regional series: the Chukchi Sea is fully ice-covered December to April.
        from mno_env.geo import LandMask
        land = LandMask.from_file()
        for m in (1, 2, 3, 4):
            e = self.on(m)
            for lon in (-172.0, -170.0, -168.0):
                vals = [seaice.ice_at(la / 4, lon, e) for la in range(262, 271) if not land.is_land(la / 4, lon)]
                self.assertTrue(vals, lon)
                self.assertLess(max(vals) - min(vals), 20.0, (m, lon, vals))
                self.assertGreater(min(vals), 80.0, (m, lon, vals))

    def test_bering_strait_rim_stays_iced_near_full_targets(self):
        # Early January (interpolating from the December median) and early May the Chukchi target is
        # a few percent below the full region. The southern rim (Bering Strait, Kotzebue Sound) must
        # not open first: Kotzebue Sound stays shorefast until about the end of May or early June
        # (NWS Alaska break-up outlooks), and the Bering cells next to it read 95 %.
        from mno_env.geo import LandMask
        land = LandMask.from_file()
        rim = [(la / 4, lo / 4) for la in range(260, 268) for lo in range(-700, -640)
               if seaice.marginal_sea(la / 4, lo / 4) == "chukchi" and not land.is_land(la / 4, lo / 4)]
        self.assertGreater(len(rim), 100)
        # water neighbours 0.25 degrees apart with one point in each sea (the Bering Strait border)
        pairs = []
        for la in range(256, 272):
            for lo in range(-704, -640):
                a = (la / 4, lo / 4)
                for b in ((a[0] + 0.25, a[1]), (a[0], a[1] + 0.25)):
                    if {seaice.marginal_sea(*a), seaice.marginal_sea(*b)} == {"bering", "chukchi"} and not land.is_land(*a) and not land.is_land(*b):
                        pairs.append((a, b))
        self.assertGreater(len(pairs), 10)
        for baseline in ("2016_2025", "1981_2010"):
            for m, d in [(1, d) for d in range(1, 11)] + [(5, 1), (5, 8)]:
                e = self.on(m, d, baseline)
                low = [(p, round(seaice.ice_at(p[0], p[1], e))) for p in rim if seaice.ice_at(p[0], p[1], e) < 15.0]
                self.assertFalse(low, (baseline, m, d, low[:5]))
                self.assertGreater(seaice.ice_at(66.25, -163.0, e), 50.0, (baseline, m, d))  # Kotzebue Sound
                step = max(abs(seaice.ice_at(*a, e) - seaice.ice_at(*b, e)) for a, b in pairs)
                self.assertLess(step, 25.0, (baseline, m, d))

    def test_chukchi_north_border_step_is_bounded(self):
        # Known limit (docs/environment/SEA-ICE-MARGINAL-SEAS.md, "New seams"): north of 80N (and of
        # row 79's two cells) the Central Arctic uses the hemispheric model, which is lighter there in
        # late summer than the Chukchi calibration. This pins the size of that step so it cannot grow.
        worst = {}
        for baseline, bound in (("2016_2025", 70.0), ("1981_2010", 20.0)):
            for m in (7, 8, 9, 10):
                for d in (1, 15):
                    e = self.on(m, d, baseline)
                    for lo in range(-688, -624):
                        lon = lo / 4 + 0.125
                        for la in range(78 * 4 + 3, 80 * 4):
                            lat = la / 4
                            if seaice.marginal_sea(lat, lon) == "chukchi" and seaice.marginal_sea(lat + 0.25, lon) is None:
                                step = abs(seaice.ice_at(lat, lon, e) - seaice.ice_at(lat + 0.25, lon, e))
                                worst[baseline] = max(worst.get(baseline, 0.0), step)
            self.assertLess(worst[baseline], bound, (baseline, worst))

    def test_chukchi_opens_from_the_south_in_summer(self):
        self.assertLess(seaice.ice_at(68, -168, self.on(9)), 15)
        self.assertGreater(seaice.ice_at(68, -168, self.on(3)), 90)
        cells = seaice._marginal_cells("chukchi")
        sep = self.on(9)
        iced = [la for la, lo, _a in cells if seaice.ice_at(la, lo, sep) >= 15]
        self.assertTrue(iced and min(iced) >= 74, iced)   # the last summer ice is in the north

    def test_other_regions_use_the_unchanged_hemispheric_model(self):
        # Golden values from seaice.py BEFORE the regional calibration (fixture note says how they
        # were made): the hemispheric edges and every concentration outside the regional seas must be
        # exactly as before, whatever changes inside the seas.
        doc = json.loads((HERE / "fixtures" / "seaice-hemispheric-golden.json").read_text(encoding="utf-8"))
        for row in doc["dates"]:
            e = seaice.edges_on(dt.datetime.strptime(row["date"], "%Y-%m-%d").replace(hour=12, tzinfo=UTC))
            self.assertEqual((e["north"], e["south"], e["sh_summer"]), (row["north"], row["south"], row["sh_summer"]), row["date"])
            for (lat, lon), want in zip(doc["points"], row["ice_at"]):
                self.assertIsNone(seaice.marginal_sea(lat, lon))
                self.assertEqual(seaice.ice_at(lat, lon, e), want, (row["date"], lat, lon))

    def test_edges_without_marginal_entry_refused_only_inside_the_seas(self):
        e = self.on(3)
        bare = {"north": e["north"], "south": e["south"], "sh_summer": e["sh_summer"]}
        with self.assertRaises(ValueError):
            seaice.ice_at(55, 140, bare)
        self.assertEqual(seaice.ice_at(70, 0, bare), seaice.ice_at(70, 0, e))
