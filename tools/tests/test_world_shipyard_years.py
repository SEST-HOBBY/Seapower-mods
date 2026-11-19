"""The World shipyard's service-year table matches the collection and leaves the campaign alone.

integration/world-sandbox/service_years.py reads each ship catalogue unit's
ServiceDate from its winning *_variants.ini and build_regions.py writes the
result to runtime/WorldShipyardYears.cs, which WorldShipyard.cs uses to order
and label DCM's shipyard. The lift ships stay in ground.lift (the Wasp is
blue's only lift), so they stay on Amphibious and are also listed under Ships.
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "integration/world-sandbox"
CAMPAIGN = HERE / "SEST_World_Campaign/dynamic_campaigns/sest-world-regions-2028/campaign.json"
TABLE = ROOT / "integration/beta-feature-parity/runtime/WorldShipyardYears.cs"
SHIPYARD = ROOT / "integration/beta-feature-parity/runtime/WorldShipyard.cs"
OPERATIONS = ROOT / "integration/beta-feature-parity/runtime/WorldOperations.cs"

# Runs in its own interpreter: service_years puts integration/campaign on
# sys.path and imports build_pack by bare name, as the builders do.
SCRIPT = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import service_years as s
sys.stdout.buffer.write(s.render(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))).encode("ascii"))
"""
ROW = re.compile(r'^        \{ "([^"]+)", \((\d+), (\d+)\) \},$')


def parse(text):
    ships = {}
    for line in text.splitlines():
        m = ROW.match(line)
        if m:
            ships[m[1]] = (int(m[2]), int(m[3]))
    tab = re.search(r"ShipsTabToo = new\(\) \{ (.*) \};", text)
    return ships, set(re.findall(r'"([^"]+)"', tab[1])) if tab else None


class WorldShipyardYearsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
        cls.committed = TABLE.read_bytes()
        cls.ships, cls.tab = parse(cls.committed.decode("ascii"))

    def test_table_rebuilds_byte_identical(self):
        if not (ROOT / "mods-source").is_dir():
            self.skipTest("mods-source not present: the winning variants files cannot be read")
        run = subprocess.run([sys.executable, "-c", SCRIPT, str(HERE), str(CAMPAIGN)],
                             cwd=ROOT, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr.decode(errors="replace"))
        self.assertEqual(run.stdout, self.committed,
                         "WorldShipyardYears.cs is stale: run integration/world-sandbox/build_regions.py")

    def test_table_is_ascii_with_unix_line_endings(self):
        self.committed.decode("ascii")
        self.assertNotIn(b"\r", self.committed)

    def test_known_ships(self):
        self.assertEqual(self.ships["usn_lhd_wasp"], (2015, 0))
        self.assertEqual(self.ships["usn_lhd_wasp_early"], (1989, 2015))
        self.assertEqual(self.ships["usn_bb_iowa"][1], 1992)
        self.assertEqual(self.ships["usn_lha_tripoli"][1], 0)
        self.assertEqual(self.ships["usn_ff_knox"], (1979, 1994))
        self.assertEqual(self.ships["plan_lpd_type_071"], (2007, 0))

    def test_lift_ships_stay_amphibious_and_are_listed_under_ships(self):
        lift = self.campaign["ground"]["lift"]
        self.assertEqual(self.tab, set(lift))
        self.assertEqual(lift, {"usn_lhd_wasp": 3, "plan_lpd_type_071": 2},
                         "ground.lift is unchanged: the Wasp is blue's only lift")

    def test_only_ship_catalogue_units(self):
        ships = {r["unit"] for r in self.campaign["catalogue"] if not r.get("aircraft") and not r.get("ground")}
        self.assertTrue(set(self.ships) <= ships, sorted(set(self.ships) - ships)[:10])
        self.assertTrue(self.tab <= ships)
        self.assertGreater(len(self.ships), 700)
        self.assertEqual(list(self.ships), sorted(self.ships))
        for unit, (first, last) in self.ships.items():
            self.assertTrue(first == 0 or 1850 <= first <= 2100, unit)
            self.assertTrue(last == 0 or (1850 <= last < 2028 and (first == 0 or first <= last)), unit)

    def test_runtime_guards(self):
        shipyard = SHIPYARD.read_text(encoding="ascii")
        operations = OPERATIONS.read_text(encoding="ascii")
        # Bind never throws into WorldOperations.Poll, which would stop all of World Operations.
        bind = shipyard[shipyard.index("internal static void Bind"):shipyard.index("internal static void Install")]
        self.assertIn("catch (Exception ex)", bind)
        self.assertIn("Api.LogFailure(\"World shipyard presentation unavailable; Dynamic Campaign Mod's own shipyard retained\", ex)", bind)
        self.assertEqual(shipyard.count("WorldOpeningBriefing.IsWorldCampaign()"), 1)
        self.assertNotIn("__result = false", shipyard, "lift ships stay on Amphibious")
        self.assertIn("WorldOpeningBriefing.Bind(a);\n        WorldShipyard.Bind(a);", operations)
        self.assertIn("WorldOpeningBriefing.Install();\n            WorldShipyard.Install();", operations)


if __name__ == "__main__":
    unittest.main()
