"""Regression cases for the merged-section report of check_mod_conflicts, on small files."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_mod_conflicts import contested, describe, merge_unit, parse_sections, position

SENSORS_A = """# a mod's sensors
[Type2031]
PassiveRange=23000   // metres
Gain=50
HasDataLink=False

[Type968]
Gain=40
MaxRange=100

[OnlyHere]
Gain=1
"""
SENSORS_B = """﻿[Type2031]
PassiveRange=90000
Gain=56
HasDataLink=False
SonarFrequency=1000

[Type968]
Gain=40
MaxRange=100

[OnlyThere]
Gain=2
"""
NAMES_A = """[****************************** All nations ******************************]

[wp_buk-m3]
Type=Buk-M3 Complex
Default=Buk-M3,Buk-M3

[AmmunitionNames]
wp_9m317ma=9M317MA
wp_9m317=9M317
"""
NAMES_B = """[wp_buk-m3]
Type=Buk-M3 Complex
Default=Buk-M3 (late),Buk-M3

[AmmunitionNames]
wp_9m317ma=9M317MA
wp_9m317=9M317 Buk-M2
other=Other
"""


class MergeUnitTests(unittest.TestCase):
    def test_systems_merge_by_section_and_language_by_key(self):
        self.assertEqual(merge_unit("systems/weapons.ini"), "section")
        self.assertEqual(merge_unit("systems\\weapons\\extra.ini"), "section")
        self.assertEqual(merge_unit("language_en/ammunition_names.ini"), "key")
        self.assertIsNone(merge_unit("aircraft/usn_f-14a.ini"))
        self.assertIsNone(merge_unit("ammunition/wp_9m317ma.ini"))


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, text):
        p = self.root / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_sections_keys_and_comments(self):
        s = parse_sections(self.write("a.ini", SENSORS_A))
        self.assertEqual(sorted(s), ["OnlyHere", "Type2031", "Type968"])
        self.assertEqual(s["Type2031"], {"PassiveRange": "23000", "Gain": "50", "HasDataLink": "False"})

    def test_bom_and_decorative_headers(self):
        self.assertIn("Type2031", parse_sections(self.write("b.ini", SENSORS_B)))
        names = parse_sections(self.write("n.ini", NAMES_A))
        self.assertEqual(sorted(names), ["AmmunitionNames", "wp_buk-m3"])

    def test_sections_contested_section_by_section(self):
        a = parse_sections(self.write("a.ini", SENSORS_A))
        b = parse_sections(self.write("b.ini", SENSORS_B))
        items = contested(a, b, "section")
        self.assertEqual([i["section"] for i in items], ["Type2031"])
        self.assertEqual(items[0]["differ"], ["Gain", "PassiveRange"])
        self.assertEqual(items[0]["only_mine"], [])
        self.assertEqual(items[0]["only_theirs"], ["SonarFrequency"])
        self.assertEqual(describe(items[0], "section"),
                         "[Type2031]: 2 key(s) differ (Gain, PassiveRange); 1 only there")
        self.assertEqual(contested(a, a, "section"), [])

    def test_language_contested_key_by_key(self):
        a = parse_sections(self.write("a.ini", NAMES_A))
        b = parse_sections(self.write("b.ini", NAMES_B))
        items = contested(a, b, "key")
        self.assertEqual([(i["section"], i["key"]) for i in items],
                         [("wp_buk-m3", "Default"), ("AmmunitionNames", "wp_9m317")])
        self.assertEqual(describe(items[1], "key"),
                         "[AmmunitionNames] wp_9m317: here '9M317', there '9M317 Buk-M2'")


class PositionTests(unittest.TestCase):
    ORDER = ["SEST_Integration", "100", "200"]

    def test_positions_are_one_based_and_sest_packs_take_the_dist_slot(self):
        self.assertEqual(position("100", self.ORDER), 2)
        self.assertEqual(position("SEST_Collection_Fixes", self.ORDER), 1)
        self.assertEqual(position("SEST_Integration", self.ORDER), 1)
        self.assertIsNone(position("300", self.ORDER))


if __name__ == "__main__":
    unittest.main()
