"""Regress the one-choice Growler selector against shipped aircraft and rows."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration/campaign"))
import build_pack as campaign
from campaign_data import CAP, STRIKE, STRIKE_FORD

DIST = ROOT / "integration/dist/SEST_Integration"
PACK = ROOT / "integration/growler-ngj-malice/SEST_Growler_NGJ_MALICE"


def loadouts(text):
    return re.search(r"^AvailableLoadouts=(.*)$", text, re.M)[1].split(",")


def stations(text, key):
    body = re.search(rf"^\[WeaponSystem1{key}\]\n(.*?)(?=^\[)", text, re.M | re.S)[1]
    return {int(n): a for n, a in re.findall(r"^Station(\d+)=(\S+)", body, re.M)}


class GrowlerCampaignLoadouts(unittest.TestCase):
    def test_both_airframes_offer_distinct_conventional_choices(self):
        for uid, third in [("usn_ea-18g", "SEST_SEAD120D"), ("usn_ea-18g_2020", "SEAD")]:
            text = (DIST / "aircraft" / f"{uid}.ini").read_text()
            fits = loadouts(text)
            with self.subTest(uid=uid):
                self.assertEqual(len(fits), len(set(fits)))
                self.assertTrue({third, "SEST_SEAD88C", "SEST_SEAD88E"} <= set(fits))
                for key, arm in [("SEST_SEAD88C", "usn_agm-88c"), ("SEST_SEAD88E", "usn_agm-88e")]:
                    seats = stations(text, key)
                    self.assertEqual(seats, {3: arm, 4: arm, 11: "usn_aim-120d-3",
                                            12: "usn_aim-120d-3", 27: "usn_tank_610_f-18",
                                            28: "usn_tank_610_f-18"})
                    self.assertNotEqual(seats, stations(text, third))

    def test_cap_and_strike_rows_allow_all_three_raaf_fits(self):
        offered = set(loadouts((DIST / "aircraft/usn_ea-18g.ini").read_text()))
        for row in [CAP, STRIKE]:
            self.assertEqual(offered & set(row.split("|")[4].split("/")),
                             {"SEST_SEAD120D", "SEST_SEAD88C", "SEST_SEAD88E"})
        naval = set(loadouts((DIST / "aircraft/usn_ea-18g_2020.ini").read_text()))
        self.assertEqual(naval & set(STRIKE_FORD.split("|")[4].split("/")),
                         {"SEAD", "SEST_SEAD88C", "SEST_SEAD88E"})

    def test_shipped_campaign_selectors_keep_three_choices(self):
        for slug in ["sest-southern-watch", "sest-southern-reach"]:
            text = (DIST / "campaigns" / slug / "campaign.ini").read_text()
            rows = re.findall(r"^TaskForceModeAirTaskingFlight\d+=(.+)$", text, re.M)
            relevant = [r for r in rows if r.startswith(("CAP|", "Attack|"))]
            self.assertTrue(relevant, slug)
            for row in relevant:
                with self.subTest(campaign=slug, row=row.split("|")[0]):
                    self.assertTrue({"SEST_SEAD120D", "SEST_SEAD88C", "SEST_SEAD88E"}
                                    <= set(row.split("|")[4].split("/")))

    def test_new_store_dependencies_resolve_in_collection(self):
        for uid in ["usn_agm-88c", "usn_agm-88e", "usn_aim-120d-3", "usn_tank_610_f-18"]:
            self.assertIsNotNone(campaign.winning(f"ammunition/{uid}.ini"), uid)

    def test_generated_and_consolidated_airframes_match(self):
        for uid in ["usn_ea-18g", "usn_ea-18g_2020"]:
            self.assertEqual((PACK / "aircraft" / f"{uid}.ini").read_bytes(),
                             (DIST / "aircraft" / f"{uid}.ini").read_bytes())

    def test_all_menu_labels_describe_the_weapon_choice(self):
        for language in ["en", "cn"]:
            text = (DIST / f"language_{language}/loadout_names.ini").read_text()
            for key, weapon in [("SEST_SEAD88C", "AGM-88C"), ("SEST_SEAD88E", "AGM-88E")]:
                self.assertEqual(len(re.findall(rf"^{key}=", text, re.M)), 1)
                label = re.search(rf"^{key}=(.*)$", text, re.M)[1]
                self.assertIn(weapon, label)
                self.assertIn("AIM-120D", label)


if __name__ == "__main__":
    unittest.main()
