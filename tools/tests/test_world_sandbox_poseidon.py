"""The 2028 World Sandbox must not stage the P-3-bodied imitation P-8."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORLD = ROOT / "integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns"
DIST = ROOT / "integration/dist/SEST_Integration/dynamic_campaigns"
OLD = "usn_p_8a"
CURRENT = "usn_p8_2027"
WORLD_VARIANTS = ("sest-world-sandbox", "sest-world-regions-2028")


class WorldPoseidonModelTests(unittest.TestCase):
    def test_current_model_is_a_poseidon_with_us_navy_squadron(self):
        model = (ROOT / "mods-source/3606774881/aircraft/usn_p8_2027.ini").read_text(encoding="utf-8-sig")
        squadrons = (ROOT / "mods-source/3606774881/aircraft/usn_p8_2027_squadrons.ini").read_text(encoding="utf-8-sig")
        self.assertRegex(model, r"(?m)^ResourcesRoot=P8_Poseidon\.obj\s*$")
        self.assertRegex(squadrons, r"(?m)^Nation=US\s*$")

    def test_both_worlds_keep_twelve_real_poseidons_and_no_fake_buyable(self):
        for variant in WORLD_VARIANTS:
            with self.subTest(campaign=variant):
                source = json.loads((WORLD / variant / "campaign.json").read_text(encoding="utf-8"))
                shipped = json.loads((DIST / variant / "campaign.json").read_text(encoding="utf-8"))
                self.assertEqual(source, shipped)
                self.assertNotIn(OLD, source["values"])
                self.assertIn(CURRENT, source["values"])
                self.assertEqual(sum(x["unit"] == CURRENT for x in source["catalogue"]), 1)
                self.assertFalse(any(x["unit"] == OLD for x in source["catalogue"]))
                p8_forces = [
                    f for f in source["forces"]
                    if any(x.split()[0] == CURRENT for x in f["units"])
                ]
                self.assertEqual(len(p8_forces), 6)
                self.assertEqual(
                    sum(int(re.search(r"\bx(\d+)", x).group(1)) if re.search(r"\bx(\d+)", x) else 1
                        for f in p8_forces for x in f["units"] if x.split()[0] == CURRENT),
                    12,
                )
                self.assertFalse(any(
                    x.split()[0] == OLD for f in source["forces"] for x in f["units"]
                ))
                self.assertEqual(source["values"][CURRENT], 89)

    def test_register_remains_research_provenance(self):
        report = json.loads((ROOT / "integration/world-sandbox/draft/conversion.json").read_text(encoding="utf-8"))
        rows = [r for r in report["rows"] if r.get("unit") == CURRENT
                and "P-3 geometry" in r.get("resolved", "")]
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(OLD in r.get("units", []) for r in rows))
        self.assertEqual(report["counts"]["catalogue"], 1560)
        self.assertEqual(report["counts"]["values"], 1560)


if __name__ == "__main__":
    unittest.main()
