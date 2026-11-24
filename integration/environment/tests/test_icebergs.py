import datetime as dt
import unittest

from helpers import UTC

from mno_env import geo, ice, icebergs as I

GRAND_BANKS = (44.0, 49.0, -56.0, -45.0)
MAY = dt.date(2028, 5, 15)


class TestTable(unittest.TestCase):
    def test_every_number_has_a_source_and_confidence(self):
        doc = I.climatology()
        for r in doc["regions"]:
            self.assertTrue(r["source"] and r["confidence"], r["id"])
            self.assertIn(r["mix"], doc["counting"]["mix"])
            if r.get("density_from") != "iip":
                self.assertEqual(len(r["monthly"]), 12, r["id"])
        for c in I.CATEGORIES:
            self.assertTrue(doc["categories"][c]["source"] and doc["categories"][c]["confidence"], c)
        for block in ("geometry", "melt", "counting", "iip", "sensors"):
            for k, v in doc[block].items():
                if isinstance(v, dict) and k != "mix":
                    self.assertIn("confidence", v, (block, k))
        self.assertEqual(doc["status"], "ESTIMATE")

    def test_bands_map_to_ice_py(self):
        for c in I.CATEGORIES:
            self.assertIn(I.climatology()["bands_map"][c], ice.BERG_BANDS)
        self.assertNotIn("giant", I.climatology()["bands_map"].values())  # giants are tracked, never generated

    def test_zero_where_no_bergs(self):
        for lat, lon in ((0, -30), (35, 18), (25, -90), (58, 20), (56, 3), (-30, 80), (10, 140), (-40, 170), (49.5, -63.0)):  # last: Gulf of St Lawrence
            for m in range(1, 13):
                self.assertEqual(sum(I.density(lat, lon, m).values()), 0.0, (lat, lon, m))
        self.assertEqual(I.generate((33, 40, 10, 25), MAY, "s"), [])  # Mediterranean

    def test_grand_banks_season(self):
        d = [I.density(45.0, -49.0, m)["small"] for m in range(1, 13)]
        self.assertEqual(d.index(max(d)) + 1, 5)              # IIP peak: May (209), then April (191)
        self.assertGreater(d[3], d[2])
        self.assertGreater(d[3], 10 * d[8])                  # spring far above autumn
        self.assertLess(d[0], d[3] / 10)
        self.assertAlmostEqual(I.density(45.0, -49.0, 4.5)["small"], (d[3] + d[4]) / 2)

    def test_iip_derived_peak_is_order_one_per_10000_km2(self):
        total = sum(I.density(45.0, -49.0, 5)[c] for c in I.BERG_CLASSES)
        self.assertTrue(1.0 <= total <= 10.0, total)

    def test_antarctic_has_tabular_arctic_does_not(self):
        self.assertGreater(I.density(-63, -50, 1)["tabular"], 0)
        self.assertEqual(I.density(70, -60, 7)["tabular"], 0)

    def test_dateline_box(self):
        self.assertEqual(I.region_at(-70, 175)["id"], "ross")
        self.assertEqual(I.region_at(-70, -160)["id"], "ross")


class TestGenerate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bergs = I.generate(GRAND_BANKS, MAY, "seed-1", sst_c=2.0, wind_ms=(8.0, 0.0))

    def test_deterministic(self):
        again = I.generate(GRAND_BANKS, MAY, "seed-1", sst_c=2.0, wind_ms=(8.0, 0.0))
        self.assertEqual([b.to_dict() for b in self.bergs], [b.to_dict() for b in again])
        other = I.generate(GRAND_BANKS, MAY, "seed-2")
        self.assertNotEqual([(b.lat, b.lon) for b in self.bergs], [(b.lat, b.lon) for b in other])
        self.assertGreater(len(self.bergs), 50)

    def test_sub_box_is_a_subset(self):
        small = I.generate((45.0, 47.0, -52.0, -48.0), MAY, "seed-1", sst_c=2.0, wind_ms=(8.0, 0.0))
        ids = {b.berg_id: b for b in self.bergs}
        self.assertTrue(small)
        for b in small:
            self.assertEqual(ids[b.berg_id], b)

    def test_inside_bbox_and_not_on_land(self):
        land = geo.default_land_mask()
        for b in self.bergs:
            self.assertTrue(GRAND_BANKS[0] <= b.lat <= GRAND_BANKS[1] and GRAND_BANKS[2] <= b.lon <= GRAND_BANKS[3])
            self.assertFalse(land.is_land(b.lat, b.lon), b)

    def test_no_bergs_on_ice_shelves(self):
        bergs = I.generate((-79.0, -74.0, 160.0, -150.0), dt.date(2028, 2, 15), "ross")
        shelves = ice.load_shelves()
        self.assertTrue(bergs)
        for b in bergs:
            self.assertFalse(any(s.contains(b.lat, b.lon) for s in shelves), b)
        self.assertTrue(all(b.region == "ross" for b in bergs))

    def test_size_ranges_per_wmo_class(self):
        sample = self.bergs + I.generate((-62.0, -56.0, -55.0, -40.0), dt.date(2028, 1, 15), "south")
        cats = I.climatology()["categories"]
        seen = set()
        for b in sample:
            seen.add(b.category)
            lo, hi = cats[b.category]["length_m"]
            self.assertTrue(lo - 0.05 <= b.length_m <= hi + 0.05, b)
            lo, hi = cats[b.category]["height_m"]
            self.assertTrue(lo - 0.005 <= b.height_m <= hi + 0.005, b)
            self.assertGreater(b.draft_m, b.height_m)        # most of a berg is under water
            self.assertLessEqual(b.draft_m, 600.0)
        self.assertEqual(seen, set(I.CATEGORIES))
        med = {}
        for c in ("growler", "bergy_bit", "small", "medium", "large", "very_large"):
            ms = sorted(b.mass_t for b in sample if b.category == c)
            med[c] = ms[len(ms) // 2]
        self.assertEqual(sorted(med.values()), [med[c] for c in ("growler", "bergy_bit", "small", "medium", "large", "very_large")])

    def test_drift_is_current_plus_wind_fraction(self):
        for b in self.bergs[:50]:
            cur = I.region_at(b.lat, b.lon)["current_ms"]
            wf = I.climatology()["drift"]["wind_factor"][b.category]
            self.assertAlmostEqual(b.drift_u_ms, round(cur[0] + wf * 8.0, 3))
            self.assertAlmostEqual(b.drift_v_ms, round(cur[1], 3))

    def test_grounding_needs_depth(self):
        self.assertTrue(all(b.grounded is None for b in self.bergs))
        g = I.generate(GRAND_BANKS, MAY, "seed-1", water_depth_m=80.0)
        deep = [b for b in g if b.draft_m >= 80.0]
        self.assertTrue(deep)
        for b in deep:
            self.assertTrue(b.grounded)
            self.assertEqual((b.drift_u_ms, b.drift_v_ms), (0.0, 0.0))

    def test_embedded_in_sea_ice(self):
        from mno_env import seaice
        when = dt.datetime(2028, 3, 15, tzinfo=UTC)
        bergs = I.generate((70.0, 75.0, -70.0, -58.0), when, "baffin", edges=seaice.edges_on(when))
        self.assertTrue(bergs)
        self.assertTrue(any(b.embedded_in_sea_ice for b in bergs))

    def test_cap(self):
        with self.assertRaises(ValueError):
            I.generate(GRAND_BANKS, MAY, "seed-1", max_bergs=10)


class TestLifeAndSensors(unittest.TestCase):
    def test_grand_banks_small_berg_melts_in_days(self):
        # Small bergs on the Grand Banks can lose up to a third of their mass in a day (field study).
        r = I.remaining_life_days(40, 30, 10, 26, sst_c=5.0, sea_state=4)
        self.assertLess(r["days"], 15)
        self.assertFalse(r["capped"])

    def test_cold_calm_water_lasts_and_is_capped(self):
        r = I.remaining_life_days(100, 80, 30, 65, sst_c=-1.8, sea_state=0)
        self.assertTrue(r["capped"])
        self.assertEqual(r["days"], 1825)
        warm = I.remaining_life_days(100, 80, 30, 65, sst_c=8.0, sea_state=3)["days"]
        cold = I.remaining_life_days(100, 80, 30, 65, sst_c=0.0, sea_state=3)["days"]
        self.assertLess(warm, cold)

    def test_sea_ice_damps_wave_erosion(self):
        free = I.melt_rates(0.0, 100, 4, 0.0)["wave"]
        packed = I.melt_rates(0.0, 100, 4, 1.0)["wave"]
        self.assertLess(packed, free * 0.05)

    def test_radar_small_ice_lost_in_clutter(self):
        self.assertEqual(I.radar_detection_nm("growler", 2), 0.4)
        self.assertEqual(I.radar_detection_nm("growler", 4), 0.0)
        self.assertEqual(I.radar_detection_nm("bergy_bit", 5), 0.0)
        self.assertGreater(I.radar_detection_nm("large", 7), 0.0)
        self.assertGreater(I.radar_detection_nm("growler", 2, enhanced=True), I.radar_detection_nm("growler", 2))
        from mno_env.sensors import radar_horizon_km
        self.assertLessEqual(I.radar_detection_nm("tabular", 0, antenna_m=5.0),
                             round(radar_horizon_km(5.0, 35.0) / 1.852, 2))

    def test_visual_limited_by_visibility_and_night(self):
        self.assertAlmostEqual(I.visual_detection_nm("large", 1.852), 1.0)
        self.assertEqual(I.visual_detection_nm("growler", 30.0), 1.0)
        self.assertLess(I.visual_detection_nm("medium", 30.0, night=True), I.visual_detection_nm("medium", 30.0))

    def test_sonar_index_rises_with_size(self):
        vals = [I.sonar_false_contact_index(c) for c in I.CATEGORIES]
        self.assertEqual(vals, sorted(vals))
        self.assertLess(I.sonar_false_contact_index("large", draft_m=50, sonar_depth_m=300),
                        I.sonar_false_contact_index("large"))


if __name__ == "__main__":
    unittest.main()
