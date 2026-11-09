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
        self.assertIn("RibbonIds=baltic_approaches,sest_southern_watch_service", text)
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


if __name__ == "__main__":
    unittest.main()
