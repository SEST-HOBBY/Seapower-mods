"""Regional variant regression tests. Requires built pack and its dependencies."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns"
DIST = ROOT / "integration/dist/SEST_Integration/dynamic_campaigns"
SPEC = ROOT / "integration/world-sandbox/regions-2028.json"
ORIGINAL = "sest-world-sandbox/campaign.json"
VARIANT = "sest-world-regions-2028/campaign.json"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_regions", ROOT / "integration/world-sandbox/build_regions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegionalExpansionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((PACK / ORIGINAL).read_text(encoding="utf-8"))
        cls.variant = json.loads((PACK / VARIANT).read_text(encoding="utf-8"))
        cls.cfg = json.loads(SPEC.read_text(encoding="utf-8"))

    def test_original_and_variant_remain_independent(self):
        shipped = json.loads((DIST / VARIANT).read_text(encoding="utf-8"))
        self.assertEqual(self.variant, shipped)
        self.assertEqual(json.loads((DIST / ORIGINAL).read_text(encoding="utf-8")), self.original)
        self.assertNotEqual(self.original["id"], self.variant["id"])
        self.assertEqual(self.original["id"], "sest.world_sandbox_2028")
        self.assertEqual(self.variant["id"], "sest.world_sandbox_2028.regional")
        self.assertEqual(len(self.variant["bases"]), len(self.original["bases"]) + 15)
        self.assertEqual(len(self.variant["forces"]), len(self.original["forces"]) + 26)
        self.assertEqual(len(self.variant["patrols"]), len(self.original["patrols"]) + 5)
        self.assertEqual(len(self.variant["catalogue"]), len(self.original["catalogue"]))
        self.assertEqual(len(self.variant["values"]), len(self.original["values"]))
        self.assertNotIn("ch_ffg_jvh", self.variant["values"])
        self.assertEqual(sum(f["side"] == "red" for f in self.variant["forces"]), 123)

    def test_shipped_variant_is_exactly_the_spec_rebuilt(self):
        # The JSON is generated, never hand-patched: the same builder and
        # serialisation on the same inputs give the same bytes.
        builder = load_builder()
        text = builder.render(builder.build(self.original, self.cfg))
        self.assertEqual(text, (PACK / VARIANT).read_text(encoding="utf-8"))

    def test_regional_supply_ships_replenish_without_changing_the_original(self):
        added = self.cfg["replenishment"]
        self.assertEqual(set(added), {"rfn_aor_pashin", "ir_aor_delvar"})
        for unit, load in self.original["replenishment"].items():
            self.assertEqual(self.variant["replenishment"][unit], load)
        for unit, load in added.items():
            self.assertEqual(self.variant["replenishment"][unit], load)
            self.assertNotIn(unit, self.original["replenishment"])
        cargo = [f for f in self.variant["forces"] if f.get("cargo")]
        self.assertEqual(len(cargo), sum(bool(f.get("cargo")) for f in self.original["forces"]) + 4)
        for f in cargo:
            self.assertEqual(f["type"], "Surface")
            self.assertTrue(any(u.split()[0] in self.variant["replenishment"] for u in f["units"]), f["name"])

    def test_regional_patrols_stay_at_sea(self):
        try:
            from global_land_mask import globe
        except ImportError:
            self.skipTest("global_land_mask not installed")
        for patrol in self.cfg["patrols"]:
            points = patrol["points"]
            for a, b in zip(points, points[1:] + points[:1]):
                for i in range(41):
                    lat = a[0] + (b[0] - a[0]) * i / 40
                    lon = a[1] + (b[1] - a[1]) * i / 40
                    self.assertFalse(globe.is_land(lat, ((lon + 180) % 360) - 180),
                                     f"{patrol['force']}: land at {lat:.2f}, {lon:.2f}")

    def test_region_specs_resolve(self):
        names = {b["id"] for b in self.original["bases"]}
        depots = {b["id"] for b in self.original["bases"] if b.get("depot")}
        prices = set(self.original["values"])
        for site in self.cfg["sites"]:
            self.assertNotIn(site["base"]["id"], names)
            self.assertIn(site["base"]["supplyFrom"], depots)
            for f in site["forces"]:
                for unit in f["units"]:
                    self.assertIn(unit.split()[0], prices)
        for f in self.cfg.get("otherForces", []):
            for unit in f["units"]:
                self.assertIn(unit.split()[0], prices)


if __name__ == "__main__":
    unittest.main()
