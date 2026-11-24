import json
import unittest

import helpers  # noqa: F401  (sets sys.path and the land mask)

from mno_env import geo, ice, iceshelves as S
from mno_env.geo import great_circle_nm, intermediate

CONF = {"high", "medium", "low", "estimate"}


def _values(node, path=()):
    """Every {'value': ...} object in the attribute file, with its path."""
    if isinstance(node, dict):
        if "value" in node:
            yield path, node
        for k, v in node.items():
            if k != "value":
                yield from _values(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _values(v, path + (i,))


class TestAttributeFile(unittest.TestCase):
    def test_every_number_has_source_and_confidence_or_a_gap(self):
        doc = S.attributes()
        self.assertEqual(doc["status"], "ESTIMATE")
        self.assertFalse(doc["enabled_by_default"])
        n = 0
        for path, v in _values(doc):
            if v["value"] is None:
                self.assertTrue(v.get("gap"), path)
                continue
            n += 1
            self.assertTrue(v.get("source"), path)
            self.assertIn(v.get("confidence"), CONF, path)
            if v.get("basis", "").startswith("derived") or str(v.get("source", "")).startswith("derived"):
                self.assertEqual(v["confidence"], "estimate", path)
        self.assertGreater(n, 60)

    def test_events_are_dated_and_sourced(self):
        doc = S.attributes()
        for e in doc["shelves"] + doc["point_features"]:
            for ev in e.get("events", []):
                self.assertRegex(str(ev["date"]), r"^\d{4}(-\d{2}(-\d{2})?)?$", ev["name"])
                self.assertTrue(ev.get("source") or ev["area_km2"].get("source"), ev["name"])
                if ev.get("ne_shows"):
                    self.assertTrue(ev.get("evidence"), ev["name"])

    def test_entries_match_natural_earth(self):
        names = {s.name for s in ice.load_shelves()}
        idx = S._attribute_index()  # raises on a bad name or an ambiguous match_point
        for e in S.attributes()["shelves"]:
            self.assertIn(e["ne_name"], names)
        self.assertEqual(len(idx), len(S.attributes()["shelves"]) + 1)  # Ross is two features

    def test_unattributed_list(self):
        u = S.unattributed_shelves()
        self.assertIn("Cook Ice Shelf", u["named"])
        self.assertNotIn("Ross Ice Shelf", u["named"])
        self.assertGreater(u["unnamed_polygons"], 100)

    def test_derived_freeboard_and_draft_follow_hydrostatics(self):
        f0, f1 = S.attributes()["hydrostatics"]["freeboard_fraction"]["value"]
        self.assertAlmostEqual(1 - 917 / 1027, f0, places=3)
        items = [(e, "thickness_front_m", "freeboard_front_m", "draft_front_m") for e in S.attributes()["shelves"]]
        items += [(e, "thickness_m", "freeboard_m", "draft_m") for e in S.attributes()["point_features"]]
        items += [(S.attributes(), None, None, None)]
        checked = 0
        for e, tk, fk, dk in items:
            if tk is None:
                g = e["generic_front"]
                h, fb, dr = g["thickness_m"]["value"], g["freeboard_m"]["value"], g["draft_m"]["value"]
            else:
                if not str(e.get(fk, {}).get("basis", "")).startswith("derived from thickness"):
                    continue
                h, fb, dr = e[tk]["value"], e[fk]["value"], e[dk]["value"]
            h = h if isinstance(h, list) else [h, h]
            for (lo, hi), (want_lo, want_hi) in ((fb, (h[0] and f0 * h[0], f1 * h[1])),
                                                 (dr, (h[0] and (1 - f1) * h[0], (1 - f0) * h[1]))):
                if lo is not None:
                    self.assertTrue(want_lo - 5 <= lo <= want_lo + 1e-9, (e.get("label", e.get("name")), lo, want_lo))
                self.assertTrue(want_hi - 1e-9 <= hi <= want_hi + 5, (e.get("label", e.get("name")), hi, want_hi))
            checked += 1
        self.assertGreaterEqual(checked, 7)


class TestFronts(unittest.TestCase):
    def test_front_file_provenance(self):
        doc = json.loads(S.FRONTS.read_text(encoding="utf-8"))
        self.assertEqual(doc["status"], "PUBLISHED")
        self.assertTrue(doc["source_url"] and doc["licence"] and len(doc["source_sha256"]) == 64)
        feats = json.loads((ice.DATA / doc["polygons_file"]).read_text(encoding="utf-8"))["shelves"]
        for f in doc["fronts"]:
            self.assertEqual(feats[f["feature"]]["name"], f["name"])

    def test_ross_front_is_the_seaward_edge(self):
        doc = json.loads(S.FRONTS.read_text(encoding="utf-8"))
        lats = [p[1] for f in doc["fronts"] if f["name"] == "Ross Ice Shelf" for p in f["line"]]
        self.assertGreater(len(lats), 100)
        self.assertTrue(all(-79.0 < la < -77.0 for la in lats))  # not the grounding line at 82-85 S
        amery = [p[1] for f in doc["fronts"] if f["name"] == "Amery Ice Shelf" for p in f["line"]]
        self.assertTrue(all(la > -70.6 for la in amery))  # front in Prydz Bay, grounding line near 73 S

    def test_distance_matches_dense_sampling(self):
        segs = S.front_segments()
        for p in ((-77.5, -175.0), (-69.0, 73.5), (-66.0, -58.0)):
            got = S.distance_to_front_nm(*p)
            brute = min(great_circle_nm(p, intermediate(a, b, k / 8)) for _, _, _, _, a, b in segs for k in range(5))
            self.assertLessEqual(got, brute + 1e-6, p)
            self.assertGreater(got, brute - 0.5, p)  # segments are short, so 4 steps is close

    def test_distance_examples(self):
        self.assertLess(S.distance_to_front_nm(-78.0, -175.0), 30)
        self.assertGreater(S.distance_to_front_nm(-81.0, -175.0), 120)  # deep inside Ross
        self.assertGreater(S.distance_to_front_nm(-50.0, 0.0), 1000)
        seg = S.front_segments()[100]
        on = intermediate(seg[4], seg[5], 0.5)
        self.assertLess(S.distance_to_front_nm(*on), 0.05)


class TestShelfAt(unittest.TestCase):
    def test_lookup(self):
        r = S.shelf_at(-81, -175)
        self.assertEqual(r["name"], "Ross Ice Shelf")
        self.assertEqual(r["attributes"]["freeboard_front_m"]["value"], [15, 50])
        self.assertIs(ice.shelf_at, S.shelf_at)
        self.assertIsNone(S.shelf_at(-75, -175))          # Ross Sea
        self.assertIsNone(S.shelf_at(-79.5, -47.5))       # Berkner Island hole
        self.assertIsNone(S.shelf_at(10, 10))
        self.assertEqual(S.shelf_at(-65.72, 103.49)["name"].split(" (")[0], "Conger(-Glenzer) Ice Shelf")

    def test_dated_events_against_the_outline(self):
        st = {e["name"]: e["ne_status"] for p in ((-81, -175), (-65.0, -60.4), (-65.72, 103.49), (-69, -62), (-79, -60))
              for e in S.shelf_events(*p)}
        self.assertEqual(st["B-15"], "after")              # 2000, before the 2003-2012 epoch
        self.assertEqual(st["Larsen B collapse"], "after")  # polygon is the remnant
        self.assertEqual(st["Conger collapse"], "before")   # 2022: polygon still shows it
        self.assertEqual(st["A-76"], "before")
        self.assertEqual(st["A68"], "unknown")
        self.assertEqual(S.event_ne_status({"date": "2008-02-28"}), "unknown")


class TestCliffNavigationSensors(unittest.TestCase):
    def test_front_cliff(self):
        c = S.front_cliff(-77.5, -175)
        self.assertEqual(c["shelf"], "Ross Ice Shelf")
        self.assertEqual(c["freeboard_m"]["range"], [15, 50])
        self.assertEqual(c["freeboard_m"]["confidence"], "high")
        self.assertEqual(c["draft_m"]["confidence"], "estimate")
        self.assertIsNone(c["water_depth_m"]["range"])
        self.assertEqual(c["water_depth_m"]["lower_bound"], c["draft_m"]["range"][0])
        g = S.front_cliff(-67.0, 152.5)  # Cook Ice Shelf: no attributes
        self.assertEqual(g["freeboard_m"]["basis"], "generic front (no value for this shelf)")
        self.assertEqual(g["draft_m"]["typical"], 220)
        a = S.front_cliff(-69.0, 73.0)   # Amery: upper bound only
        self.assertTrue(a["draft_m"]["partly_generic"])
        self.assertLessEqual(a["draft_m"]["typical"], 270)
        self.assertIs(ice.front_cliff, S.front_cliff)

    def test_navigation(self):
        for plat in S.PLATFORMS:
            r = S.shelf_navigation(-81, -175, plat)
            self.assertEqual(r["status"], "blocked")
            self.assertFalse(r["enter"])
        seg = S.front_segments()[100]
        near = intermediate(seg[4], seg[5], 0.5)
        # a point about 1 nm off a front, on the open-water side
        for brg in range(0, 360, 30):
            q = geo.destination(near, brg, 1.0)
            if S.shelf_at(*q) is None and S.distance_to_front_nm(*q) < 1.5:
                break
        self.assertEqual(S.shelf_navigation(*q, "submarine")["status"], "blocked")
        self.assertEqual(S.shelf_navigation(*q, "surface")["status"], "caution")
        self.assertEqual(S.shelf_navigation(-74.0, -175, "submarine")["status"], "open")
        self.assertEqual(S.shelf_navigation(-74.0, -175, "surface")["status"], "open")
        with self.assertRaises(ValueError):
            S.shelf_navigation(-74, -175, "aircraft")

    def test_point_features(self):
        names = [f["name"] for f in S.point_features_near(82.6, -80.0, 120)]
        self.assertIn("Milne Ice Shelf", names)
        self.assertEqual(S.point_features_near(0, 0, 500), [])
        self.assertIsNone(S.shelf_at(81.0, -61.5))  # point features never block

    def test_sensor_notes(self):
        r = S.face_reflection()
        self.assertAlmostEqual(r["db"], -8, delta=0.5)   # research: about 0.4, about -8 dB
        n = S.front_sensor_notes(-77.5, -175, antenna_m=25)
        self.assertAlmostEqual(n["radar"]["horizon_nm"], 23, delta=0.5)  # 25 m antenna, 30 m cliff
        self.assertIn("land-like", n["radar"]["return"])
        self.assertIn("katabatic", n["weather"])

    def test_routes_unchanged(self):
        from helpers import state, t0
        from mno_env import routes
        st = state()
        r = routes.evaluate([(-75, -178), (-82, -170)], st, t0(), speed_kn=15, capability="icebreaker",
                            shelves=ice.load_shelves())
        self.assertTrue(r.blocked.startswith("ice shelf"))
        r = routes.evaluate([(-74.0, -175.0), (-77.2, -175.0)], st, t0(), speed_kn=15, capability="icebreaker")
        self.assertIsNone(r.blocked)  # no shelves passed: no shelf rule, as before


if __name__ == "__main__":
    unittest.main()
