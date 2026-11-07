"""Static regression for concise native Task Force combat-cost debrief rows."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CS = ROOT / "integration/runtime-fixes/CampaignCosts.cs"


class CombatDebriefLayoutTests(unittest.TestCase):
    def test_native_rows_are_concise(self):
        text = CS.read_text(encoding="utf-8")
        source = text.split('static string DebriefPair(', 1)[1].split('target=summaryRows.GetValue', 1)[0]
        expected = ("Cost Weapons", "Cost Units", "Cost Stores", "Cost Mission", "Cost Campaign")
        for name in expected:
            self.assertIn('add("' + name + '"', source)
        self.assertIn('add("Cost Data Gaps","See F11 Combat Costs")', source)
        for obsolete in ("Combat Cost: Basis", "Combat Cost: Incomplete",
                         "Combat Cost: Campaign", "Combat Cost: Lost Stores"):
            self.assertNotIn('add("' + obsolete + '"', source)

    def test_accounting_retained(self):
        text = CS.read_text(encoding="utf-8")
        self.assertIn("campaign.Player.Merge(mission.Player)", text)
        self.assertIn("campaign.Enemy.Merge(mission.Enemy)", text)
        self.assertIn("Pair(current.Player.Total,current.Enemy.Total)", text)


if __name__ == "__main__":
    unittest.main()
