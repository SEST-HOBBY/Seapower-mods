"""The World Sandbox values the RAAF KC-30A as a tanker whichever copy wins.

Since the 28 Oct 2026 Workshop refresh two mods ship aircraft/aus_a330_mrtt.ini:
Euromod Modern RAN (3820759806), whose copy says Role=Airliner and wins in the
SEST load order, and French Air Force (3758943352), whose copy says Role=AEW.
build_dynamic_campaign values an aircraft by its first Role, so the KC-30A
would have fallen from an AEW's 242 to an airliner's 2; AIR_ROLE_OVERRIDE
values it as a Tanker instead. These checks pin the override to that one
unit, so every other value in the committed campaigns is still what its own
Role gives. That the committed campaign is the builder's output is
tools/tests/test_world_sandbox_rebuild.py.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "integration/world-sandbox"
WORLD = HERE / "SEST_World_Campaign/dynamic_campaigns"
DIST = ROOT / "integration/dist/SEST_Integration/dynamic_campaigns"
REPORT = HERE / "draft/conversion.json"
UNIT = "aus_a330_mrtt"
WORLD_VARIANTS = ("../legacy_campaigns/sest-world-sandbox", "sest-world-regions-2028")

# Facts only the builder can answer (its resolver and value rule), from a
# separate interpreter: it imports build_pack, home_bases and submarines by
# bare name.
SCRIPT = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
import build_dynamic_campaign as b
units = {}
for uid in sys.argv[2:]:
    f = b.bp.unit_file(uid)[1]
    units[uid] = {"file": str(f) if f else None, "role": b.role(uid) if f else None,
                  "value": b.value_of(uid) if f else None,
                  "shipped_by": [token for token, base in b.bp.providers()
                                 if (base / "aircraft" / f"{uid}.ini").is_file()]}
json.dump({"override": b.AIR_ROLE_OVERRIDE, "role_values": b.AIR_ROLE_VALUE, "units": units},
          sys.stdout)
"""


class WorldKc30aValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run = subprocess.run([sys.executable, "-c", SCRIPT, str(HERE), UNIT, "uk_a330_mrtt",
                              "usaf_stratotanker"], cwd=ROOT, capture_output=True, text=True)
        if run.returncode:
            raise AssertionError(f"builder facts failed:\n{run.stdout}{run.stderr}")
        cls.facts = json.loads(run.stdout)
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.campaigns = {}
        for variant in WORLD_VARIANTS:
            source = json.loads((WORLD / variant / "campaign.json").read_text(encoding="utf-8"))
            shipped = json.loads((DIST / variant / "campaign.json").read_text(encoding="utf-8"))
            cls.campaigns[variant] = (source, shipped)

    def test_the_override_is_this_one_unit_valued_as_a_tanker(self):
        self.assertEqual(self.facts["override"], {UNIT: "Tanker"})
        unit = self.facts["units"][UNIT]
        self.assertIsNotNone(unit["file"], f"no installed mod defines {UNIT}")
        value, basis = unit["value"]
        self.assertEqual(value, self.facts["role_values"]["Tanker"])
        self.assertEqual(value, 60)
        self.assertTrue(basis.startswith("Role Tanker, SEST choice"), basis)
        self.assertIn(f"Role {unit['role']}", basis)

    def test_the_cause_still_holds(self):
        # The winning copy does not call the aircraft a tanker; if an author
        # ever does, the override is redundant and AIR_ROLE_OVERRIDE should
        # lose the unit so that its file's own role is what values it.
        unit = self.facts["units"][UNIT]
        self.assertNotEqual(unit["role"], "Tanker",
                            f"the winning {UNIT}.ini now says Role=Tanker: retire the override")
        self.assertIn("3820759806", unit["shipped_by"])
        self.assertEqual(unit["shipped_by"][0], "3820759806",
                         "another mod now outranks Euromod Modern RAN's copy: re-read its Role")

    def test_other_aircraft_are_still_valued_by_their_own_role(self):
        for uid in ("uk_a330_mrtt", "usaf_stratotanker"):
            unit = self.facts["units"][uid]
            if unit["file"] is None:
                continue
            with self.subTest(unit=uid):
                value, basis = unit["value"]
                self.assertEqual(basis, f"Role {unit['role']}")
                self.assertEqual(value, self.facts["role_values"][unit["role"]])

    def test_both_worlds_sell_the_kc30a_once_at_the_tanker_value(self):
        for variant, (source, shipped) in self.campaigns.items():
            with self.subTest(campaign=variant):
                self.assertEqual(source, shipped)
                self.assertEqual(source["values"][UNIT], 60)
                entries = [e for e in source["catalogue"] if e["unit"] == UNIT]
                self.assertEqual(len(entries), 1)
                entry = entries[0]
                # The builder's price bands: 60 is in the first (up to 120).
                self.assertEqual((entry["side"], entry["nation"], entry["tier"], entry.get("aircraft")),
                                 ("blue", "Australia", 0, True))

    def test_the_conversion_report_records_the_choice(self):
        basis = self.report["values_basis"][UNIT]
        self.assertTrue(basis.startswith("Role Tanker, SEST choice"), basis)


if __name__ == "__main__":
    unittest.main()
