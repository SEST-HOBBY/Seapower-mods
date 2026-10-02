"""Regression cases for a game update leaving pack versions behind, proved on a small tree."""
import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_game_version import audit, bump, classify, main, parse_version, read_game_version

CHANGELOG = """Change log
----------

===============================================================================

20-Jul-2026: 0.8.2 Build #358 (23444) Public Release
----------------------------------------------------
[FIX] S-300 battery targeting points

20-Jul-2026: 0.8.1 Build #357 (23440)
-------------------------------------
"""

# Shaped like integration/rafale-f5/build_patch.py: the version is a literal
# inside INFO_INI and the builder writes the pack's _info.ini from it.
ALPHA_BUILDER = '''from pathlib import Path
OUT = Path(__file__).resolve().parent / "SEST_Alpha"
INFO_INI = """[Language_en]
Name=SEST Alpha
Description=One unit.

[Compatibility]
ApproximateVersion=0.8.2
"""
OUT.mkdir(exist_ok=True)
(OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")
'''
ALPHA_LINE = ALPHA_BUILDER.splitlines().index("ApproximateVersion=0.8.2") + 1

# A builder that never touches _info.ini, so the committed one is static.
BETA_BUILDER = '''from pathlib import Path
OUT = Path(__file__).resolve().parent / "SEST_Beta"
(OUT / "aircraft").mkdir(parents=True, exist_ok=True)
(OUT / "aircraft" / "x.ini").write_text("[General]\\n", encoding="utf-8")
'''
BETA_INFO = b"\xef\xbb\xbf[Language_en]\r\nName=SEST Beta\r\n\r\n[Compatibility]\r\nApproximateVersion=0.8.2\r\n"

RANGED_MOD = ("[Language_cn]\r\nName=协调\r\n\r\n[Language_en]\r\nName=Strike Tool\r\n\r\n"
              "[Compatibility]\r\n"
              ";ApproximateVersion is the second check and will override all statements below.\r\n"
              "GreaterThanEqualToVersion=0.8.2\r\nLessThanVersion=0.9.0\r\n")


class GameVersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.live = self.root / "data/install-snapshot/changelog.live.txt"
        self.write(self.live, CHANGELOG)
        self.alpha_builder = self.root / "integration/alpha/build_patch.py"
        self.alpha_info = self.root / "integration/alpha/SEST_Alpha/_info.ini"
        self.write(self.alpha_builder, ALPHA_BUILDER)
        self.write(self.alpha_info, "[Language_en]\nName=SEST Alpha\n\n[Compatibility]\nApproximateVersion=0.8.2\n")
        self.beta_builder = self.root / "integration/beta/build_patch.py"
        self.beta_info = self.root / "integration/beta/SEST_Beta/_info.ini"
        self.write(self.beta_builder, BETA_BUILDER)
        self.beta_info.parent.mkdir(parents=True)
        self.beta_info.write_bytes(BETA_INFO)
        self.write(self.root / "data/load-order.tokens.txt", "# order\nSEST_Integration\n100\n200\n300\n")
        self.mod(100, "[Language_en]\nName=Current\n\n[Compatibility]\nApproximateVersion=0.8.2\n")
        self.mod(200, RANGED_MOD)
        self.mod(300, "[Language_en]\nName=Old\n\n[Compatibility]\nApproximateVersion=0.6.0\n")

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="")

    def mod(self, wid, text):
        self.write(self.root / "mods-source" / str(wid) / "_info.ini", text)

    def test_game_version_is_the_first_build_line(self):
        version, source = read_game_version(self.root)
        self.assertEqual(version, "0.8.2")
        self.assertIn("Build #358 (20-Jul-2026) from data/install-snapshot/changelog.live.txt", source)
        self.assertNotIn("FALLBACK", source)
        self.assertEqual(read_game_version(self.root, "0.9.0"), ("0.9.0", "from --version (changelog says 0.8.2)"))

    def test_vanilla_changelog_is_the_fallback_and_says_so(self):
        self.write(self.root / "mods-source/_vanilla/changelog.txt", CHANGELOG.replace("0.8.2 Build #358", "0.8.3 Build #360"))
        self.live.unlink()
        version, source = read_game_version(self.root)
        self.assertEqual(version, "0.8.3")
        self.assertIn("FALLBACK", source)
        (self.root / "mods-source/_vanilla/changelog.txt").unlink()
        with self.assertRaises(ValueError):
            read_game_version(self.root)

    def test_tree_at_the_game_version_passes_and_lists_the_far_behind_mod(self):
        lines, problems, found = audit(self.root, "0.8.2")
        self.assertEqual(problems, [])
        self.assertEqual(found, {})
        self.assertIn("Static _info.ini (edited by hand, not generated): integration/beta/SEST_Beta/_info.ini", lines)
        self.assertIn("  ApproximateVersion vs 0.8.2: 1 match, 1 more than one minor behind, 1 range only", lines)
        self.assertIn("  Version ranges: 1 declared, 1 admit 0.8.2", lines)
        self.assertIn("INFO: 1 mod(s) declare a minor version below 0.8, which the Mod Manager shows as "
                      "out of date (MAJOR and MINOR must match); the 1 more than one minor behind:", lines)
        self.assertIn("  0.6.0   300  Old", lines)

    def test_game_update_fails_packs_builders_and_the_ranged_mod(self):
        lines, problems, found = audit(self.root, "0.9.0")
        self.assertEqual(problems, [
            "integration/alpha/SEST_Alpha/_info.ini declares 0.8.2, game is 0.9.0",
            "integration/beta/SEST_Beta/_info.ini declares 0.8.2, game is 0.9.0 (static: no builder writes it)",
            f"integration/alpha/build_patch.py:{ALPHA_LINE} writes ApproximateVersion=0.8.2, game is 0.9.0",
            "200 Strike Tool declares 0.8.2 <= v < 0.9.0, which excludes 0.9.0",
        ])
        self.assertEqual(found, {"packs": 2, "builders": 1, "workshop": 1})
        self.assertIn("  ApproximateVersion vs 0.9.0: 1 one minor behind, 1 more than one minor behind, 1 range only", lines)

    def test_a_builder_writing_through_a_helper_is_not_static(self):
        # integration/replenishment/build_patch.py writes via write("_info.ini", INFO_INI).
        self.write(self.alpha_builder, ALPHA_BUILDER.replace(
            '(OUT / "_info.ini").write_text(INFO_INI, encoding="utf-8")',
            'def write(name, text):\n    (OUT / name).write_text(text, encoding="utf-8")\nwrite("_info.ini", INFO_INI)'))
        lines = audit(self.root, "0.8.2")[0]
        self.assertIn("Static _info.ini (edited by hand, not generated): integration/beta/SEST_Beta/_info.ini", lines)
        self.assertEqual([p.relative_to(self.root).as_posix() for p, _ in bump(self.root, "0.9.0")[0]],
                         ["integration/alpha/build_patch.py", "integration/beta/SEST_Beta/_info.ini"])

    def test_undeclared_pack_and_builder_fail(self):
        self.write(self.alpha_builder, ALPHA_BUILDER.replace("\n[Compatibility]\nApproximateVersion=0.8.2\n", ""))
        self.write(self.alpha_info, "[Language_en]\nName=SEST Alpha\n")
        problems = audit(self.root, "0.8.2")[1]
        self.assertIn("integration/alpha/SEST_Alpha/_info.ini declares no [Compatibility] ApproximateVersion", problems)
        self.assertIn("integration/alpha/build_patch.py writes _info.ini with no ApproximateVersion literal", problems)

    def test_lower_bound_excludes_an_older_game(self):
        self.mod(200, "[Language_en]\nName=New Only\n\n[Compatibility]\nGreaterThanEqualToVersion=0.9.0\n")
        problems = audit(self.root, "0.8.2")[1]
        self.assertEqual(problems, ["200 New Only declares 0.9.0 <= v, which excludes 0.8.2"])

    def test_versions_compare_numerically(self):
        self.assertGreater(parse_version("0.10.0"), parse_version("0.9.0"))
        self.assertGreater(parse_version("0.8.10"), parse_version("0.8.2"))
        self.assertIsNone(parse_version("0.8.x"))
        self.assertEqual(classify(parse_version("0.8.10"), parse_version("0.9.0")), "one minor behind")
        self.assertEqual(classify(parse_version("0.8.5"), parse_version("0.8.2")), "newer than the game")
        self.assertEqual(classify(parse_version("0.7.0"), parse_version("0.9.0")), "more than one minor behind")

    def test_bump_rewrites_builders_and_static_files_only(self):
        alpha_info_before = self.alpha_info.read_bytes()
        changed, left = bump(self.root, "0.9.0")
        self.assertEqual([(p.relative_to(self.root).as_posix(), old) for p, old in changed],
                         [("integration/alpha/build_patch.py", ["0.8.2"]), ("integration/beta/SEST_Beta/_info.ini", ["0.8.2"])])
        self.assertEqual(left, [])
        self.assertEqual(self.alpha_builder.read_text(encoding="utf-8"), ALPHA_BUILDER.replace("0.8.2", "0.9.0"))
        self.assertEqual(self.beta_info.read_bytes(), BETA_INFO.replace(b"0.8.2", b"0.9.0"))
        self.assertEqual(self.alpha_info.read_bytes(), alpha_info_before)
        self.assertEqual(self.beta_builder.read_text(encoding="utf-8"), BETA_BUILDER)
        problems = audit(self.root, "0.9.0")[1]
        self.assertEqual([p for p in problems if "build_patch.py" in p or "Beta" in p], [])
        self.assertIn("integration/alpha/SEST_Alpha/_info.ini declares 0.8.2, game is 0.9.0", problems)

    def test_bump_is_idempotent(self):
        bump(self.root, "0.9.0")
        snapshot = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        changed, left = bump(self.root, "0.9.0")
        self.assertEqual((changed, left), ([], []))
        self.assertEqual({p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}, snapshot)

    def test_bump_reports_what_it_cannot_rewrite(self):
        self.write(self.alpha_builder, ALPHA_BUILDER.replace("\n[Compatibility]\nApproximateVersion=0.8.2\n", ""))
        changed, left = bump(self.root, "0.9.0")
        self.assertEqual([p.name for p, _ in changed], ["_info.ini"])
        self.assertEqual(left, [self.alpha_builder])

    def test_a_single_digit_day_is_still_the_newest_line(self):
        self.write(self.live, "2-Oct-2026: 0.9.0 Build #370 (23600) Public Release\n" + CHANGELOG)
        self.assertEqual(read_game_version(self.root), ("0.9.0", "Build #370 (2-Oct-2026) from data/install-snapshot/changelog.live.txt"))

    def test_an_unbuilt_pack_is_a_finding_and_its_builder_is_still_scanned(self):
        # build_all.py --from-scratch deletes integration/*/SEST_* first; a failed build leaves none.
        shutil.rmtree(self.alpha_info.parent)
        lines, problems, found = audit(self.root, "0.9.0")
        self.assertIn("integration/alpha has no built SEST_* folder for build_patch.py to write; "
                      "run python3 tools/build_all.py --from-scratch", problems)
        self.assertIn(f"integration/alpha/build_patch.py:{ALPHA_LINE} writes ApproximateVersion=0.8.2, game is 0.9.0", problems)
        self.assertEqual(found, {"packs": 2, "builders": 1, "workshop": 1})
        self.assertEqual([p.relative_to(self.root).as_posix() for p, _ in bump(self.root, "0.9.0")[0]],
                         ["integration/alpha/build_patch.py", "integration/beta/SEST_Beta/_info.ini"])

    def test_no_pack_at_all_is_not_a_pass(self):
        shutil.rmtree(self.root / "integration")
        lines, problems, found = audit(self.root, "0.8.2")
        self.assertEqual(problems, ["no SEST pack found under integration (wrong --root, or nothing built)"])
        self.assertIn("Builders: 0 scanned for ApproximateVersion= literals", lines)

    def test_an_export_newer_than_the_snapshot_fails(self):
        self.write(self.root / "mods-source/_vanilla/changelog.txt", CHANGELOG.replace("0.8.2 Build #358", "0.8.3 Build #360"))
        self.assertEqual(read_game_version(self.root)[0], "0.8.2")
        lines, problems, found = audit(self.root, "0.8.2")
        self.assertEqual(problems, ["mods-source/_vanilla/changelog.txt is from 0.8.3 Build #360 but "
                                    "data/install-snapshot/changelog.live.txt says 0.8.2: the export is newer than "
                                    "the snapshot; run tools/capture-context.ps1"])
        self.assertEqual(found, {"snapshot": 1})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root)]), 1)
        self.assertEqual(out.getvalue().splitlines()[-1],
                         "Game version check: FAILED (0 pack(s), 0 builder(s), 0 Workshop exclusion(s) against 0.8.2; "
                         "the snapshot lags the export)")

    def test_bump_exit_code_says_whether_a_hand_edit_is_left(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root), "--bump", " 0.9.0 "]), 0)
        text = out.getvalue().splitlines()
        self.assertEqual(text[0], "bump: integration/alpha/build_patch.py  0.8.2 -> 0.9.0")
        self.assertIn("note: the changelog still reads 0.8.2; re-export and run tools/capture-context.ps1 "
                      "once the game has updated", text)
        self.assertEqual(text[-1], "Bump to 0.9.0: 2 file(s) rewritten, 0 left for a hand edit; "
                                   "rebuild (python3 tools/build_all.py --from-scratch), then run this check")
        self.assertEqual(self.alpha_builder.read_text(encoding="utf-8"), ALPHA_BUILDER.replace("0.8.2", "0.9.0"))
        self.write(self.alpha_builder, ALPHA_BUILDER.replace("\n[Compatibility]\nApproximateVersion=0.8.2\n", ""))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root), "--bump", "0.9.0"]), 1)
        text = out.getvalue().splitlines()
        self.assertIn("left alone: integration/alpha/build_patch.py has no ApproximateVersion literal; "
                      "add a [Compatibility] section by hand", text)
        self.assertTrue(text[-1].startswith("Bump to 0.9.0: 0 file(s) rewritten, 1 left for a hand edit;"))

    def test_main_prints_a_verdict_and_returns_the_exit_code(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root)]), 0)
        self.assertEqual(out.getvalue().splitlines()[-1],
                         "Game version check: PASS (0 pack(s), 0 builder(s), 0 Workshop exclusion(s) against 0.8.2)")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root), "--version", "0.9.0"]), 1)
        text = out.getvalue().splitlines()
        self.assertTrue(text[0].startswith("Game version: 0.9.0 from --version (changelog says 0.8.2)"))
        self.assertEqual(text[-1], "Game version check: FAILED (2 pack(s), 1 builder(s), 1 Workshop exclusion(s) against 0.9.0)")


if __name__ == "__main__":
    unittest.main()
