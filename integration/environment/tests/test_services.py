import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from helpers import START, UTC, procedural_snapshot, state, t0

from mno_env import RULES_VERSION, ice, routes
from mno_env.cache import CacheError, MnoEnvDataProvider
from mno_env.forecast import Asset, MnoEnvForecast
from mno_env.persistence import EnvSaveState, MnoEnvPersistence, default_state


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = MnoEnvPersistence(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_two_saves_do_not_leak(self):
        a = default_state("gco-2028", "slotA", 100)
        b = default_state("gco-2028", "slotB", 100)
        self.assertNotEqual(a.seed, b.seed)
        a.events.append("storm-1-resolved")
        a.forecast["blue"] = {"satellite": True}
        self.p.save(a)
        self.p.save(b)
        la, wa = self.p.load("gco-2028", "slotA")
        lb, wb = self.p.load("gco-2028", "slotB")
        self.assertIsNone(wa)
        self.assertEqual(la.events, ["storm-1-resolved"])
        self.assertEqual(lb.events, [])
        self.assertEqual(lb.forecast, {})

    def test_same_seed_different_slot(self):
        a = default_state("gco-2028", "slotA")
        a.seed = "shared"
        self.p.save(a)
        c = self.p.save_as(a, "slotC")
        self.assertEqual(c.seed, "shared")
        lc, _ = self.p.load("gco-2028", "slotC")
        self.assertEqual((lc.save_id, lc.seed), ("slotC", "shared"))
        self.assertTrue(self.p.delete("gco-2028", "slotA"))
        self.assertFalse(self.p.delete("gco-2028", "slotA"))
        self.assertIsNone(self.p.load("gco-2028", "slotC")[1])

    def test_missing_and_corrupt(self):
        s, w = self.p.load("gco-2028", "old-save", 55)
        self.assertIn("no environment sidecar", w)
        self.assertEqual(s, default_state("gco-2028", "old-save", 55))
        a = default_state("gco-2028", "slotA")
        path = self.p.save(a)
        path.write_text(path.read_text().replace('"campaign_seconds": 0', '"campaign_seconds": 999'))
        s, w = self.p.load("gco-2028", "slotA")
        self.assertIn("checksum", w)
        self.assertEqual(s.seed, a.seed)  # deterministic fallback == default for this save
        self.assertIn("999", path.read_text())  # the corrupt file is kept for inspection
        path.write_bytes(b"\x00\xff garbage")
        self.assertIn("unreadable", self.p.load("gco-2028", "slotA")[1])

    def test_sidecar_of_another_save_rejected(self):
        a = default_state("gco-2028", "slotA")
        src = self.p.save(a)
        dst = self.p.path("gco-2028", "slotB")
        dst.write_bytes(src.read_bytes())
        self.assertIn("another save", self.p.load("gco-2028", "slotB")[1])

    def test_unsafe_ids(self):
        for bad in ("../x", "a/b", "", "x" * 200):
            with self.assertRaises(ValueError):
                self.p.path("gco", bad)

    def test_rules_version_warning(self):
        a = default_state("gco-2028", "slotA")
        a.rules_version = "old"
        self.p.save(a)
        self.assertIn(RULES_VERSION, self.p.load("gco-2028", "slotA")[1])


class TestCache(unittest.TestCase):
    def test_roundtrip_corruption_and_offline_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            prov = MnoEnvDataProvider(Path(d))
            snap = procedural_snapshot()
            m = prov.add(snap)
            entry = m["snapshots"][0]
            self.assertEqual(prov.load(snap["snapshot_id"])["integrity"], snap["integrity"])
            r = prov.resolve(snap["snapshot_id"], entry["sha256"], "seed", START)
            self.assertEqual((r.source, r.reason), ("cache", None))
            r = prov.resolve(snap["snapshot_id"], "0" * 64, "seed", START)
            self.assertEqual(r.source, "procedural-fallback")
            self.assertIn("not the version", r.reason)
            f = Path(d) / entry["file"]
            f.write_bytes(f.read_bytes()[:-10])
            r = prov.resolve(snap["snapshot_id"], None, "seed", START + dt.timedelta(hours=3, minutes=7))
            self.assertIn("corrupt", r.reason)
            self.assertEqual(r.snapshot["times"][0]["valid_utc"], "2028-09-14T06:00:00Z")
            f.unlink()
            self.assertIn("missing", prov.resolve(snap["snapshot_id"], None, "seed", START).reason)
            self.assertIn("not in the cache", prov.resolve("nope", None, "seed", START).reason)
            self.assertIn("no dataset", prov.resolve(None, None, "seed", START).reason)
            (Path(d) / "manifest.json").write_text("{broken")
            self.assertIn("manifest", prov.resolve(snap["snapshot_id"], None, "seed", START).reason)

    def test_refuses_invalid_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            bad = json.loads(json.dumps(procedural_snapshot()))
            bad["integrity"]["payload_sha256"] = "x"
            with self.assertRaises(CacheError):
                MnoEnvDataProvider(Path(d)).add(bad)


class TestForecast(unittest.TestCase):
    def setUp(self):
        self.st = state()
        self.f = MnoEnvForecast(self.st, "save-seed")

    def test_deterministic_and_grows_with_lead(self):
        a = self.f.report("blue", t0(), t0() + 24 * 3600, -55, -50)
        b = MnoEnvForecast(state(), "save-seed").report("blue", t0(), t0() + 24 * 3600, -55, -50)
        self.assertEqual(a, b)
        near = self.f.report("blue", t0(), t0() + 6 * 3600, -55, -50)
        far = self.f.report("blue", t0(), t0() + 66 * 3600, -55, -50)
        self.assertLess(near.sigma["msl_pressure_hpa"], far.sigma["msl_pressure_hpa"])
        self.assertEqual(a.status, "FORECAST")
        red = self.f.report("red", t0(), t0() + 24 * 3600, -55, -50)
        self.assertNotEqual(a.values, red.values)  # each side's errors are its own

    def test_observation_and_recon(self):
        ship = Asset("ship", -55, -50, 60, t0())
        obs = self.f.report("blue", t0(), t0(), -55, -50, [ship])
        self.assertEqual(obs.status, "OBSERVED")
        truth = self.st.sample(t0(), -55, -50).values
        self.assertEqual(obs.values["wave_hs_m"], truth["wave_hs_m"])
        with_recon = self.f.report("blue", t0(), t0() + 12 * 3600, -55, -50, [ship])
        without = self.f.report("blue", t0(), t0() + 12 * 3600, -55, -50)
        self.assertLess(with_recon.sigma["wave_hs_m"], without.sigma["wave_hs_m"])
        old_ship = Asset("ship", -55, -50, 60, t0() - 7 * 3600)
        self.assertEqual(self.f.report("blue", t0(), t0(), -55, -50, [old_ship]).status, "FORECAST")
        far_ship = Asset("ship", -20, -50, 60, t0())
        self.assertEqual(self.f.report("blue", t0(), t0(), -55, -50, [far_ship]).status, "FORECAST")

    def test_truth_untouched_stale_estimated(self):
        before = self.st.sample(t0() + 3600, -55, -50).values
        self.f.report("blue", t0(), t0() + 3600, -55, -50, [Asset("aircraft", -55, -50, 100, t0())])
        self.assertEqual(self.st.sample(t0() + 3600, -55, -50).values, before)
        self.assertEqual(self.f.report("blue", t0(), t0() + 300 * 3600, 0, 0).status, "STALE")
        self.assertEqual(self.f.report("blue", t0(), t0(), 0, 0, estimate={"wave_hs_m": 3}).status, "ESTIMATED")
        with self.assertRaises(ValueError):
            self.f.report("blue", t0(), t0() - 1, 0, 0)


class TestIceRoutes(unittest.TestCase):
    def test_access_thresholds(self):
        self.assertEqual([ice.access(c) for c in (5, 20, 40, 70)], ["open", "caution", "restricted", "blocked"])
        self.assertEqual(ice.access(70, "polar_class"), "caution")
        self.assertEqual(ice.access(99, "icebreaker"), "caution")
        self.assertEqual(ice.access(None), "caution")
        with self.assertRaises(ValueError):
            ice.access(5, "PC3")

    def test_capability_table_needs_sources(self):
        self.assertEqual(ice.load_capabilities(), {})
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.json"
            p.write_text(json.dumps({"units": {"x": {"capability": "polar_class"}}}))
            with self.assertRaises(ValueError):
                ice.load_capabilities(p)
            p.write_text(json.dumps({"units": {"x": {"capability": "polar_class", "source": "class society register"}}}))
            self.assertEqual(ice.load_capabilities(p), {"x": "polar_class"})

    def test_shelves_schematic(self):
        shelves = ice.load_shelves()
        self.assertTrue(shelves)
        self.assertFalse(any(s.authoritative for s in shelves))
        self.assertTrue(any(s.contains(-81, -175) for s in shelves))   # Ross, east of 180
        self.assertTrue(any(s.contains(-81, 175) for s in shelves))    # Ross, west of 180
        self.assertTrue(any(s.contains(-79, -60) for s in shelves))    # Ronne
        self.assertFalse(any(s.contains(-75, -175) for s in shelves))  # Ross Sea, open

    def test_open_ocean_route_matches_great_circle(self):
        st = state()
        pts = [(-35.0, 20.0), (-40.0, 60.0), (-35.0, 100.0)]
        r = routes.evaluate(pts, st, t0(), speed_kn=15)
        from mno_env.geo import great_circle_nm
        gc = great_circle_nm(pts[0], pts[1]) + great_circle_nm(pts[1], pts[2])
        self.assertIsNone(r.blocked)
        self.assertAlmostEqual(r.distance_nm, gc, delta=0.5)
        self.assertGreaterEqual(r.hours, gc / 15 - 0.01)
        self.assertLessEqual(r.fuel, 1.25 * r.distance_nm + 0.1)  # bounded penalty
        self.assertEqual(r, routes.evaluate(pts, st, t0(), speed_kn=15))  # deterministic

    def test_blocks(self):
        st = state()
        self.assertEqual(routes.evaluate([(0, 5), (0, 40)], st, t0(), speed_kn=15).blocked, "land")
        r = routes.evaluate([(-75, -178), (-82, -170)], st, t0(), speed_kn=15, capability="icebreaker",
                            shelves=ice.load_shelves())
        self.assertTrue(r.blocked and r.blocked.startswith("ice shelf"))
        r = routes.evaluate([(-50, 0), (-68, 0)], st, t0(), speed_kn=15)
        self.assertTrue(r.blocked and r.blocked.startswith("sea ice"))
        r2 = routes.evaluate([(-50, 0), (-68, 0)], st, t0(), speed_kn=15, capability="icebreaker")
        self.assertIsNone(r2.blocked)
        self.assertGreater(r2.hours, r2.distance_nm / 15)  # ice slows even an icebreaker

    def test_icebergs(self):
        st = state()
        b = ice.Iceberg("FIX-1", "large", -58.0, -40.0, t0())
        p1 = b.predict(st, t0() + 48 * 3600)
        self.assertEqual(p1, b.predict(st, t0() + 48 * 3600))
        self.assertGreater(p1["hazard_radius_nm"], b.predict(st, t0() + 6 * 3600)["hazard_radius_nm"])
        self.assertIsNone(ice.Iceberg("G", "growler", -58, -40, t0() - 30 * 86400).predict(st, t0()))
        with self.assertRaises(ValueError):
            b.predict(st, t0() - 1)
        r = routes.evaluate([(-58.0, -45.0), (-58.0, -35.0)], st, t0(), speed_kn=12, bergs=[b])
        self.assertEqual([h["berg_id"] for h in r.hazards], ["FIX-1"])


if __name__ == "__main__":
    unittest.main()
