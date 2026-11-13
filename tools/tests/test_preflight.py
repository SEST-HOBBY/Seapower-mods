#!/usr/bin/env python3
"""tools/preflight.py: which Type= lines of a mission name a unit.

    python3 -m unittest discover -s tools/tests -p 'test_preflight.py' -v
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def tool():
    spec = importlib.util.spec_from_file_location("preflight_tool", ROOT / "tools/preflight.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TypeLines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preflight = tool()

    def check(self, text):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "mission.ini"
            path.write_text(text, encoding="utf-8")
            return self.preflight.check_mission(path)

    def test_a_zone_a_station_and_an_anchor_are_not_units(self):
        # The forms of the game's own 0.9.0 missions and of every campaign mission built here.
        problems, crashes, checked = self.check(
            "[General]\nType=Scenario\n[Mission]\nCampaignMission=True\n"
            "[Zone1]\nType=Deployment\n[Zone2_RedSpawn]\nType=Spawn\n"
            "[RecoveryPoint_Taskforce1_1]\nType=GameplayAnchor\n[PatrolZone1]\nType=CAP\n"
            "[AirTaskingStation]\nType=Deployment\n")
        self.assertEqual((problems, crashes, checked), ([], [], 0))

    def test_a_unit_no_mod_defines_is_still_reported_in_every_unit_section(self):
        for section in ("Taskforce1Vessel1", "Taskforce2Submarine3", "Taskforce1Aircraft2",
                        "Taskforce2Helicopter1", "Taskforce1LandUnit12", "NeutralVessel4",
                        "NeutralAircraft1", "NeutralBiologic2", "NeutralLandUnit1", "NeutralSubmarine1",
                        "NeutralHelicopter1"):
            with self.subTest(section=section):
                problems, _crashes, checked = self.check(f"[{section}]\nType=sest_no_such_unit\n")
                self.assertEqual(len(problems), 1)
                self.assertIn("Type=sest_no_such_unit - no enabled mod defines it", problems[0])
                self.assertGreaterEqual(checked, 1)

    def test_a_real_unit_resolves_and_a_campaign_mission_is_clean_of_zone_alarms(self):
        problems, _crashes, checked = self.check("[Taskforce1Vessel1]\nType=usn_cg_ticonderoga\n")
        self.assertEqual((problems, checked), ([], 1))
        built = ROOT / "integration/campaign/SEST_Campaign/campaigns/sest-southern-watch/missions"
        mission = built / "Southern Watch 03 - Rig Seventeen.ini"
        if not mission.is_file():
            self.skipTest("pack not built")
        self.assertIn("Type=Deployment", mission.read_text(encoding="utf-8"))
        problems, _crashes, checked = self.preflight.check_mission(mission)
        self.assertEqual([p for p in problems if "Deployment" in p], [])
        self.assertGreater(checked, 10)


if __name__ == "__main__":
    unittest.main()
