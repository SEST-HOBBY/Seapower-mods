"""Regression cases for check_load_order's reading of the live order, on small lists."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_load_order as clo  # noqa: E402

TOKENS = ["SEST_Integration", "100", "200", "300"]
RULES = [("SEST_Growler", "200", {"aircraft/usn_ea-18g.ini"}),
         ("SEST_Fixes", "300", {"vessels/x.ini", "vessels/y.ini", "vessels/z.ini", "vessels/w.ini"})]
LIVE_TEXT = """# The [LoadOrder] Sea Power is actually using, captured 2026-10-14T16:58:11.
# Compare against data\\load-order.tokens.txt - the canonical order.

NumberOfModFiles=4   entries parsed: 4

   1. 3812461539   on     SEST Integration Pack
   2. 100          on     Anchor Chain
   3. 300          on     Something
   4. ACConfigs    OFF
"""


def problems(live):
    return clo.live_check(TOKENS, live, RULES)[1]


class LiveOrderTests(unittest.TestCase):
    def test_read_live_parses_tokens_flags_and_the_capture_time(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "load-order.live.txt"
            p.write_text(LIVE_TEXT, encoding="utf-8")
            live, when = clo.read_live(p)
        self.assertEqual(live, [("3812461539", True), ("100", True), ("300", True), ("ACConfigs", False)])
        self.assertEqual(when, "2026-10-14T16:58:11")
        self.assertEqual(clo.read_live(Path("/nonexistent/load-order.live.txt")), (None, None))

    def test_workshop_item_stands_in_for_the_local_folder(self):
        live = [("3812461539", True), ("100", True), ("200", True), ("300", True)]
        lines, broken = clo.live_check(TOKENS, live, RULES)
        self.assertEqual(broken, [])
        self.assertIn("canonical but not live (1): SEST_Integration", lines)
        self.assertIn("live but not canonical (1): 3812461539", lines)
        self.assertTrue(any("3812461539 at #1" in l and "stands in" in l for l in lines))

    def test_identical_orders_report_no_drift(self):
        live = [(t, True) for t in TOKENS]
        lines, broken = clo.live_check(TOKENS, live, RULES)
        self.assertEqual(broken, [])
        self.assertIn("order of shared entries: same as canonical", lines)
        self.assertIn("disabled in game (0): -", lines)

    def test_a_mod_above_sest_loses_its_override(self):
        live = [("100", True), ("200", True), ("SEST_Integration", True), ("300", True)]
        broken = problems(live)
        self.assertEqual(len(broken), 2)
        self.assertIn("SEST_Growler (live #3, as SEST_Integration) is BELOW 200 (live #2)", broken[0])
        self.assertIn("contested: aircraft/usn_ea-18g.ini", broken[0])
        self.assertIn("100 (live #1) sits above SEST (live #3)", broken[1])

    def test_a_disabled_mod_above_sest_cannot_outrank_it(self):
        live = [("200", False), ("SEST_Integration", True), ("100", True), ("300", True)]
        lines, broken = clo.live_check(TOKENS, live, RULES)
        self.assertEqual(broken, [])
        self.assertIn("disabled in game (1): 200", lines)

    def test_sest_disabled_or_missing_loses_everything(self):
        self.assertEqual(len(problems([("SEST_Integration", False), ("100", True)])), 1)
        self.assertIn("SEST_Integration listed but disabled", problems([("SEST_Integration", False), ("100", True)])[0])
        self.assertIn("neither SEST_Integration nor 3812461539 is listed", problems([("100", True), ("200", True)])[0])

    def test_reordered_shared_entries_are_drift_not_breakage(self):
        live = [("SEST_Integration", True), ("300", True), ("100", True), ("200", True)]
        lines, broken = clo.live_check(TOKENS, live, RULES)
        self.assertEqual(broken, [])
        self.assertIn("order of shared entries: DIFFERENT - the game has reordered them", lines)


if __name__ == "__main__":
    unittest.main()
