"""Regional variant regression tests. Requires built pack and its dependencies."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns"
DIST = ROOT / "integration/dist/SEST_Integration/dynamic_campaigns"
ORIGINAL = "sest-world-sandbox/campaign.json"
VARIANT = "sest-world-regions-2028/campaign.json"


class RegionalExpansionTest(unittest.TestCase):
    def test_original_and_variant_remain_independent(self):
        original = json.loads((PACK / ORIGINAL).read_text(encoding="utf-8"))
        variant = json.loads((PACK / VARIANT).read_text(encoding="utf-8"))
        shipped = json.loads((DIST / VARIANT).read_text(encoding="utf-8"))
        self.assertEqual(variant, shipped)
        self.assertNotEqual(original["id"], variant["id"])
        self.assertEqual(original["id"], "sest.world_sandbox_2028")
        self.assertEqual(variant["id"], "sest.world_sandbox_2028.regional")
        self.assertEqual(len(variant["bases"]), len(original["bases"]) + 15)
        self.assertEqual(len(variant["forces"]), len(original["forces"]) + 25)
        self.assertEqual(len(variant["patrols"]), len(original["patrols"]) + 5)
        self.assertEqual(len(variant["catalogue"]), len(original["catalogue"]))
        self.assertEqual(len(variant["values"]), len(original["values"]))
        self.assertNotIn("ch_ffg_jvh", variant["values"])
        self.assertEqual(sum(f["side"] == "red" for f in variant["forces"]), 122)

    def test_region_specs_resolve(self):
        cfg = json.loads((ROOT / "integration/world-sandbox/regions-2028.json").read_text(encoding="utf-8"))
        base = json.loads((PACK / ORIGINAL).read_text(encoding="utf-8"))
        names = {b["id"] for b in base["bases"]}
        depots = {b["id"] for b in base["bases"] if b.get("depot")}
        prices = set(base["values"])
        for site in cfg["sites"]:
            self.assertNotIn(site["base"]["id"], names)
            self.assertIn(site["base"]["supplyFrom"], depots)
            for f in site["forces"]:
                for unit in f["units"]:
                    self.assertIn(unit.split()[0], prices)
        for f in cfg.get("otherForces", []):
            for unit in f["units"]:
                self.assertIn(unit.split()[0], prices)


if __name__ == "__main__":
    unittest.main()
