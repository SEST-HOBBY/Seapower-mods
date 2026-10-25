"""Regression checks for the World Sandbox renames: the Chilean hull (24 Oct
2026) and US Naval Aviation's HH-60H (25 Oct 2026)."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORLD = Path("integration/world-sandbox/SEST_World_Campaign")
DIST = Path("integration/dist/SEST_Integration")
CAMPAIGN = Path("dynamic_campaigns/sest-world-sandbox/campaign.json")
LEGACY = "ch_ffg_jvh"
CURRENT = "ch_ffg_jacob_van_heemskerck"
HISTORICAL = "197000000"
PRESENT = "800000000"


class WorldHullCompatibilityTests(unittest.TestCase):
    def test_new_campaign_uses_only_current_id(self):
        for pack in (WORLD, DIST):
            data = json.loads((ROOT / pack / CAMPAIGN).read_text(encoding="utf-8"))
            values = data["values"]
            catalogue = [entry["unit"] for entry in data["catalogue"]]
            self.assertNotIn(LEGACY, values)
            self.assertIn(CURRENT, values)
            self.assertNotIn(LEGACY, catalogue)
            self.assertEqual(catalogue.count(CURRENT), 1)

    def test_saved_hull_and_two_named_variants(self):
        for pack in (WORLD, DIST):
            vessel = (ROOT / pack / "vessels" / f"{LEGACY}.ini").read_text(encoding="utf-8")
            variant = (ROOT / pack / "vessels" / f"{LEGACY}_variants.ini").read_text(encoding="utf-8")
            names = (ROOT / pack / "language_en/vessel_names.ini").read_text(encoding="utf-8")
            self.assertEqual(vessel.strip(), f"#!alias vessels/{CURRENT}.ini")  # resolved from the mod root
            self.assertIn("NumberOfVariants=2", variant)
            self.assertIn("[Variant1]", variant)
            self.assertIn("[Variant2]", variant)
            match = re.search(rf"(?ms)^\[{LEGACY}\]\n(.*?)(?=^\[|\Z)", names)
            self.assertIsNotNone(match)
            self.assertIn("Variant1=", match.group(1))
            self.assertIn("Variant2=", match.group(1))

    def test_costs_preserved_for_both_ids(self):
        for pack in (Path("integration/combat-costs/SEST_Combat_Costs"), DIST):
            cfg = (ROOT / pack / "systems/sest_vessel_costs.ini").read_text(encoding="utf-8")
            for uid in (LEGACY, CURRENT):
                block = re.search(rf"(?ms)^\[{uid}\]\n(.*?)(?=^\[|\Z)", cfg)
                self.assertIsNotNone(block, uid)
                self.assertIn(f"VesselCosts={HISTORICAL}", block.group(1))
                self.assertIn(f"CurrentYearCost={PRESENT}", block.group(1))

    def test_renamed_hh60_in_new_campaigns_and_saves(self):
        # US Naval Aviation, 25 Oct 2026: usn_hh-60 -> usn_hh-60h.
        regional = Path("dynamic_campaigns/sest-world-regions-2028/campaign.json")
        for pack in (WORLD, DIST):
            for campaign in (CAMPAIGN, regional):
                data = json.loads((ROOT / pack / campaign).read_text(encoding="utf-8"))
                placed = [u for f in data["forces"] for u in f["units"]]
                self.assertFalse([u for u in placed if u.split(" x")[0] == "usn_hh-60"], campaign)
                self.assertTrue([u for u in placed if u.split(" x")[0] == "usn_hh-60h"], campaign)
                self.assertNotIn("usn_hh-60", data["values"])
                self.assertNotIn("usn_hh-60", [e["unit"] for e in data["catalogue"]])
            unit = (ROOT / pack / "aircraft/usn_hh-60.ini").read_text(encoding="utf-8")
            self.assertEqual(unit.strip(), "#!alias aircraft/usn_hh-60h.ini")
            squadrons = (ROOT / pack / "aircraft/usn_hh-60_squadrons.ini").read_text(encoding="utf-8")
            self.assertIn("[Squadron1]", squadrons)
            names = (ROOT / pack / "language_en/aircraft_names.ini").read_text(encoding="utf-8")
            self.assertRegex(names, r"(?m)^\[usn_hh-60\]$")

    def test_build_order_declared(self):
        entries = json.loads((ROOT / "data/mod-catalog.json").read_text(encoding="utf-8"))["local_packs"]
        prices = next(p for p in entries if p["folder"] == "SEST_Combat_Costs")
        self.assertIn("SEST_World_Campaign", prices["build_after"])


if __name__ == "__main__":
    unittest.main()
