"""Regression cases for the summary's reading of workshop-subscriptions.txt, in both of its
formats, and for what its header says of the installed game and the game's code."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop_refresh_summary import build_of, dropped_files, folders, installed_game, moved

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


RELEASE = """Change log
----------

===============================================================================

11-Nov-2026: 0.9.0 Build 261111 Public Release
----------------------------------------------
[FIX] Campaign: damaged units from dynamic generation were sometimes reported as kills

07-Nov-2026: 0.8.7 Build 261107
"""
NEXT_RELEASE = "20-Nov-2026: 0.9.1 Build 261120 Public Release\n" + RELEASE
BETA = "20-Nov-2026: 0.9.1 Build 261120\n[FIX] x\n" + RELEASE
BUILD = """# Installed Sea Power build - what the packs' ApproximateVersion should track.

exe            : C:\\Sea Power\\Sea Power.exe
product version: 6000.0.85f2 (b028303d8e7d)
game code      : Sea Power_Data\\Managed\\Seapower-Scripts.dll
code sha256    : """ + "ab" * 32 + """
code size      : 5123456
steam buildid     : 26599367
"""


class InstalledGameTests(unittest.TestCase):
    def test_the_first_dated_build_line_is_the_build(self):
        self.assertEqual(build_of(RELEASE), ("11-Nov-2026: 0.9.0 Build 261111 Public Release", "0.9.0", "261111"))
        self.assertEqual(build_of(BETA)[1:], ("0.9.1", "261120"))
        self.assertEqual(build_of("26-Sep-2026: 0.8.1 Build #260926 (7)\n")[1:], ("0.8.1", "260926"))
        self.assertIsNone(build_of("Change log\n----------\n"))
        self.assertIsNone(build_of(None))

    def test_the_same_build_installed_is_named_and_nothing_more(self):
        lines = installed_game(RELEASE, RELEASE, BUILD)
        self.assertEqual(lines, ["  installed            : 11-Nov-2026: 0.9.0 Build 261111 Public Release",
                                 "  game code            : Seapower-Scripts.dll SHA-256 " + "ab" * 32])

    def test_a_newer_release_installed_says_the_export_is_due(self):
        text = "\n".join(installed_game(RELEASE, NEXT_RELEASE, BUILD))
        self.assertIn("installed            : 20-Nov-2026: 0.9.1 Build 261120 Public Release", text)
        self.assertIn("THE INSTALLED GAME IS NOT THE EXPORTED ONE", text)
        self.assertIn("the game export is due", text)
        self.assertNotIn("beta", text)

    def test_a_beta_installed_says_the_export_stays(self):
        text = "\n".join(installed_game(RELEASE, BETA, BUILD))
        self.assertIn("THE INSTALLED GAME IS NOT THE EXPORTED ONE", text)
        self.assertIn("it is a beta, and the export stays", text)
        self.assertNotIn("is due", text)

    def test_a_capture_that_recorded_neither_says_so(self):
        # A capture written by a capture-context.ps1 older than 13 Nov 2026 has no
        # code sha256 line, and one that found no install copied no changelog.
        old_build = "\n".join(l for l in BUILD.splitlines() if not l.startswith(("game code", "code ")))
        self.assertEqual(installed_game(RELEASE, None, old_build),
                         ["  installed            : not captured",
                          "  game code            : not captured (the capture's game-build.txt has no code sha256 line)"])

    def test_the_files_the_install_no_longer_ships_are_counted(self):
        listed = ("# Files in mods-source\\_vanilla\\original that the installed game no longer ships.\n"
                  "# export   : 11-Nov-2026: 0.9.0 Build 261111 Public Release\n\n"
                  "compared: 4505 file(s) of the export\nno longer shipped (2):\n  missions/a.ini\n  missions/b.ini\n")
        self.assertEqual(dropped_files(listed), "  export files the install no longer ships: 2 "
                                                "(data/install-snapshot/game-files-dropped.txt lists them)")
        self.assertEqual(dropped_files(listed.replace("(2):\n  missions/a.ini\n  missions/b.ini", "(0):")),
                         "  export files the install no longer ships: 0")
        self.assertEqual(dropped_files("# header\n\nnot compared: the install's original\\ folder was not found\n"),
                         "  export files the install no longer ships: not compared "
                         "(the install's original\\ folder was not found)")
        self.assertEqual(dropped_files(None), "  export files the install no longer ships: not compared "
                                              "(no game-files-dropped.txt in this capture)")


if __name__ == "__main__":
    unittest.main()
