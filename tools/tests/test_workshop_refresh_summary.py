"""Regression cases for the summary's reading of workshop-subscriptions.txt, in both of its formats."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop_refresh_summary import folders, moved

OLD = """# Every subscribed Workshop item on disk, with its in-game name.

3373356293   Westland Lynx HAS.3                                  updated 2026-08-24
3408662804   伊斯坎德尔                                                updated 2026-08-24
3602046770                                                        updated 2026-08-16

subscribed but UNPLACED (2): 3812461539, 3819522350
"""
NEW = """# Every subscribed Workshop item on disk, with its in-game name.
# updated = Steam's timeupdated for the installed version (appworkshop_1286220.acf, local time);
# folder = the folder's last-write time, which an update inside existing subfolders does not move.

3373356293   Westland Lynx HAS.3                                  updated 2026-08-23 21:10  folder 2026-08-24 09:02
3408662804   伊斯坎德尔                                                updated 2026-10-01 07:30  folder 2026-08-24 09:05
3602046770                                                        updated unknown  folder 2026-08-16 12:00

subscribed but UNPLACED (2): 3812461539, 3819522350
"""


class FoldersTests(unittest.TestCase):
    def test_old_format_has_the_folder_date_only(self):
        b = folders(OLD)
        self.assertEqual(b["3373356293"], ("Westland Lynx HAS.3", "2026-08-24", None))
        self.assertEqual(b["3408662804"][0], "伊斯坎德尔")
        self.assertEqual(b["3602046770"], ("", "2026-08-16", None))
        self.assertEqual(len(b), 3)

    def test_new_format_has_steam_time_and_the_folder_column(self):
        b = folders(NEW)
        self.assertEqual(b["3373356293"], ("Westland Lynx HAS.3", "2026-08-23 21:10", "2026-08-24 09:02"))
        self.assertEqual(b["3408662804"][1:], ("2026-10-01 07:30", "2026-08-24 09:05"))
        self.assertEqual(b["3602046770"], ("", "unknown", "2026-08-16 12:00"))

    def test_moved_compares_like_with_like(self):
        old, new = folders(OLD), folders(NEW)
        # old capture against new: the folder dates, which did not move
        self.assertEqual(moved(old["3373356293"], new["3373356293"]), (False, "2026-08-24", "2026-08-24"))
        # Steam's time says the Iskander mod was updated, but the folder date does not: not listed
        self.assertFalse(moved(old["3408662804"], new["3408662804"])[0])
        # two new-format captures: Steam's time decides
        later = folders(NEW.replace("updated 2026-10-01 07:30", "updated 2026-10-14 06:52"))
        self.assertEqual(moved(new["3408662804"], later["3408662804"]), (True, "2026-10-01 07:30", "2026-10-14 06:52"))
        self.assertFalse(moved(new["3373356293"], later["3373356293"])[0])
        # two old-format captures: the folder date
        self.assertTrue(moved(old["3373356293"], folders(OLD.replace("updated 2026-08-24\n", "updated 2026-09-01\n", 1))["3373356293"])[0])


if __name__ == "__main__":
    unittest.main()
