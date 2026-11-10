"""Native completion ribbons retain other definitions and resolve real artwork."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "integration/campaign/service_awards.py"
spec = importlib.util.spec_from_file_location("service_awards", SOURCE)
awards = importlib.util.module_from_spec(spec)
spec.loader.exec_module(awards)


class CampaignServiceAwards(unittest.TestCase):
    def test_existing_ribbon_ids_and_definitions_are_preserved(self):
        before = "[TaskForceRibbons]\nRibbonIds=baltic_approaches\n\n[Ribbon_baltic_approaches]\nType=CampaignAward\nName_en=Existing\n"
        text = awards.commander_settings(before, "sest-southern-watch")
        self.assertIn("RibbonIds=baltic_approaches|sest_southern_watch_service", text)
        self.assertIn("[Ribbon_baltic_approaches]\nType=CampaignAward\nName_en=Existing", text)
        self.assertEqual(text, awards.commander_settings(text, "sest-southern-watch"))

    def test_all_native_completion_awards_resolve_art_and_definitions(self):
        from PIL import Image
        pack = ROOT / "integration/campaign/SEST_Campaign"
        for slug in awards.CAMPAIGNS:
            for suffix in (s for s in ("", "-open") if (pack / "campaigns" / (slug + s)).exists()):
                with self.subTest(campaign=slug + suffix):
                    directory = pack / "campaigns" / (slug + suffix)
                    text = (directory / "commander_settings.ini").read_text()
                    rid = awards.award_id(slug)
                    self.assertIn("[Ribbon_" + rid + "]", text)
                    self.assertIn("ReferenceSource=Fictional", text)
                    image_path = re.search(r"^ImagePath=(.*)$", text, re.M).group(1)
                    with Image.open(pack / image_path) as image:
                        self.assertEqual(image.size, (140, 36))
                        self.assertEqual(image.getpixel((20, 5))[3], 255)
                    campaign = (directory / "campaign_data.ini").read_text() if (directory / "campaign_data.ini").exists() else (directory / "campaign.ini").read_text()
                    sections = re.findall(r"(?ms)^\[Mission\d+\][^\n]*\n(.*?)(?=^\[|\Z)", campaign)
                    granted = [s for s in sections if "TaskForceModeRibbonAwards=" + rid in s]
                    self.assertEqual(len(granted), 1)
                    self.assertIn("TaskForceModeFinalMission=True", granted[0])

    def test_unknown_campaign_remains_unchanged(self):
        self.assertIsNone(awards.award_id("third-party-campaign"))
        self.assertEqual(awards.commander_settings("existing\n", "third-party-campaign"), "existing\n")

    def test_catalogue_preserves_pipe_and_comma_lists_without_duplicate_ids(self):
        for separators in ["|", ","]:
            text = awards.commander_settings("[TaskForceRibbons]\nRibbonIds=legacy_a" + separators + "legacy_b\n", "sest-southern-watch")
            ids = re.search(r"^RibbonIds=(.*)$", text, re.M)[1].split("|")
            self.assertEqual(ids[:2], ["legacy_a", "legacy_b"])
            self.assertEqual(len(ids), len(set(ids)))

    def test_new_national_options_keep_australian_defaults_and_other_campaigns(self):
        source = "[CommanderSettings]\nCommanderNations=Australia\nCommanderDefaultNation=Australia\nCommanderStartingRankLevel=5\n\n[OfficerRanks]\nAustralia=unchanged\n"
        text = awards.commander_settings(source, "sest-southern-watch")
        self.assertIn("CommanderNations=Australia|US", text)
        self.assertIn("CommanderDefaultNation=Australia", text)
        self.assertIn("CommanderStartingRankLevel=5", text)
        self.assertIn("Australia=unchanged", text)
        self.assertIn("US=Ensign", text)
        red = awards.commander_settings("[CommanderSettings]\nCommanderNations=China\n", "sest-red-line")
        self.assertNotIn("CommanderNations=China|US", red)

    def test_national_grants_use_native_id_nation_grammar(self):
        specs = awards.mission_awards("sest-southern-watch", {"num": "12"}, True)
        self.assertEqual(specs[0], "sest_southern_watch_service")
        self.assertIn("australian_distinguished_service_cross,Australia", specs)
        self.assertIn("navy_unit_commendation,US", specs)
        self.assertNotIn("navy_marine_corps_commendation_medal", "|".join(specs))

    def test_aosm_scenario_milestone_requires_thirty_calendar_days(self):
        mission = {"code": "SR10", "date": (2029, 1, 6)}
        self.assertIn("sest_aosm_indo_pacific,Australia", awards.mission_awards("sest-southern-reach", mission))
        with self.assertRaisesRegex(ValueError, "30 campaign days"):
            awards.mission_awards("sest-southern-reach", {"code": "SR10", "date": (2028, 12, 20)})

    def test_preserved_final_mission_keeps_nation_qualified_specs(self):
        text = "[Mission1]\nTaskForceModeFinalMission=True\nTaskForceModeRibbonAwards=legacy_real,US|legacy_other,Australia\n"
        out = awards.final_mission_awards(text, "sest-southern-watch")
        self.assertIn("legacy_real,US|legacy_other,Australia|sest_southern_watch_service", out)
        self.assertEqual(out, awards.final_mission_awards(out, "sest-southern-watch"))

    def test_real_definitions_have_modern_scenario_citations_and_correct_recipients(self):
        rows = awards.catalogue("sest-southern-reach")
        self.assertEqual(len(awards.REAL), 6)
        for rid, row in rows.items():
            if row["reference"] == "Fictional":
                continue
            self.assertIn("Scenario qualification", row["citation"])
            self.assertIn("fictional", row["citation"])
            self.assertNotIn("1985", row["citation"])
            self.assertNotIn("John Lehman", row["citation"])
            self.assertTrue(row["source"].startswith("https://"))
        text = awards.commander_settings("[CommanderSettings]\nCommanderNations=Australia\n", "sest-southern-reach")
        self.assertIn("CitationRecipient_en={TaskForceName}", text)
        self.assertEqual(rows["navy_unit_commendation"]["recipient"], "unit")
        self.assertIsNone(rows["navy_commendation_medal"]["medal"])

    def test_all_milestones_and_national_specs_resolve_in_own_catalogue(self):
        for slug in awards.CAMPAIGNS:
            catalogue = awards.catalogue(slug)
            for code in set(awards.MILESTONES[slug]) | set(awards.NATIONAL_MISSIONS.get(slug, {})):
                mission = {"code": code, "date": (2029, 1, 6)}
                for spec in awards.mission_awards(slug, mission):
                    self.assertIn(spec.split(",")[0], catalogue)


if __name__ == "__main__":
    unittest.main()
