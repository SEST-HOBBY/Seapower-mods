"""Regression cases for the vanilla-drift report, on a throwaway git repo.

Each test builds a small repository with the real layout - a vanilla export,
SEST packs with and without builders, mission files, a campaign roster and a
changelog - commits it as the baseline, then changes the working tree the way
a game update and a fresh export would. Nothing here reads this repository's
own history.

    python3 -m unittest tools/tests/test_check_vanilla_drift.py
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_vanilla_drift as drift  # noqa: E402

CHANGELOG = """Change log
----------

===============================================================================

20-Jul-2026: 0.8.2 Build #358 (23444) Public Release
----------------------------------------------------
[FIX] S-300 battery targeting points
"""
NEW_ENTRY = """02-Oct-2026: 0.8.3 Build #361 (23600) Public Release
----------------------------------------------------
[NEW] F-47

===============================================================================

"""
VANILLA = "mods-source/_vanilla/original"
FIXES = "integration/collection-fixes/SEST_Collection_Fixes"
CAMPAIGN = "integration/dist/SEST_Integration/campaigns/sest-x"


class VanillaDriftTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        self.env = {**os.environ, "HOME": temp.name, "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
                    "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
        self.write(".gitattributes", "* -text\n")
        self.write("mods-source/_vanilla/changelog.txt", CHANGELOG)
        self.write(f"{VANILLA}/aircraft/usn_f-14a.ini", "[General]\nUnitType=Aircraft\n")
        self.write(f"{VANILLA}/aircraft/usn_f-14a_squadrons.ini", "[Default]\nNation=US\nServiceDate=1975|1991\n")
        self.write(f"{VANILLA}/aircraft/usn_e-2c.ini", "[General]\nUnitType=Aircraft\n")
        self.write(f"{VANILLA}/aircraft/fr_alouette_II.ini", "[General]\nUnitType=Helicopter\n")
        self.write(f"{VANILLA}/ammunition/usn_gbu-24.ini", "[General]\nType=Bomb\nWeight=1000\n")
        self.write(f"{VANILLA}/ammunition/wp_sa-n-1.ini", "[General]\nType=Missile\nAmmoPoints=100\n")
        self.write(f"{VANILLA}/vessels/wp_pb_don.ini", "[General]\nUnitType=Vessel\nLength=100\n")
        self.write(f"{VANILLA}/vessels/wp_ss_kilo.ini", "[General]\nUnitType=Submarine\n")
        self.write(f"{VANILLA}/language_en/loadout_names.ini",
                   "[LoadoutNames]\nAirToAir=Air to Air    // standard\nStrike=Strike\n")
        self.write(f"{VANILLA}/systems/sensors.ini", "[General]\nDataLinkUpdateRate=1\n\n[Start_ECM]\nType=ECM\n")
        self.write(f"{VANILLA}/language_en/nations.ini", "[Nations]\nUS=United States\n")
        self.write(f"{VANILLA}/missions/Warsaw Pact/Northern Passage.ini", "[Unit1]\nType=wp_pb_don\n")
        self.write(f"{VANILLA}/clouds.ini", "[Clouds]\nDensity=1\n")
        self.write(f"{VANILLA}/_info.ini", "[Language_en]\nName=Sea Power\n")
        # A pack whose builder forks the vanilla file, and merge files it adds keys to.
        self.write("integration/collection-fixes/build_patch.py",
                   't = read("_vanilla/original", "ammunition/usn_gbu-24.ini")\n'
                   '(OUT / "_info.ini").write_text(INFO_INI)\n')
        self.write(f"{FIXES}/_info.ini", "[Language_en]\nName=SEST Collection Fixes\n")
        self.write(f"{FIXES}/ammunition/usn_gbu-24.ini", "# SEST Collection Fixes\n[General]\nType=Bomb\nWeight=1000\n")
        self.write(f"{FIXES}/language_en/loadout_names.ini",
                   "[LoadoutNames]\nSIGINT=Signals Intelligence\nAirToAir=Air to Air\n")
        self.write(f"{FIXES}/systems/sensors.ini", "[Side_Globe]\nType=ECM\n")
        # A pack whose builder names its file only in prose - a docstring, a
        # comment, a trailing comment and a description template: still a static copy.
        self.write("integration/static-pack/SEST_Static_Pack/vessels/wp_pb_don.ini",
                   "[General]\nUnitType=Vessel\nLength=100\n")
        self.write("integration/static-pack/build_patch.py",
                   '"""Ships a hand-forked vessels/wp_pb_don.ini."""\n'
                   '# see "wp_pb_don" upstream\n'
                   'OUT = 1  # vessels/wp_pb_don.ini, by hand\n'
                   'INFO = """\\\n'
                   'Description=a copy of vessels/wp_pb_don.ini with one fix\n'
                   '"""\n')
        # A pack whose builder writes a whole folder from data, never naming a file.
        self.write("integration/metered/SEST_Metered/ammunition/wp_sa-n-1.ini",
                   "[General]\nType=Missile\nAmmoPoints=100\nSupplyCategory=SEST_AreaSAM\n")
        self.write("integration/metered/build_patch.py",
                   'for rid in metered_rounds():\n'
                   '    write(f"ammunition/{rid}.ini", tag(read(rid)))\n')
        # A builder that reads a vanilla file it does not ship, one whose
        # mission['clouds'] must not pass for the export's clouds.ini, and one
        # that names a file with spaces in its name and a unit id in another case.
        self.write("integration/allied-fixes/build_patch.py",
                   'nations_ini = ROOT / "mods-source" / "_vanilla" / "original" / "language_en" / "nations.ini"\n'
                   'line = f"Clouds={mission[\'clouds\']}"\n'
                   'src = VANILLA / "missions" / "Warsaw Pact" / "northern passage.ini"\n'
                   'heli = ("FR_ALOUETTE_II", "Squadron1")\n')
        # The campaign's mission modules live a level down; caches and tests do not count.
        self.write("integration/campaign/southern_reach/sr01_departure.py",
                   'U("blue", "_vanilla", "usn_f-14a", "cap")\n')
        self.write("integration/campaign/__pycache__/stale.py", 'U("blue", "_vanilla", "usn_f-14a", "cap")\n')
        self.write("integration/campaign/test_build_pack.py", 'assert "usn_f-14a" in roster\n')
        # The dist copy must not count as a pack.
        self.write("integration/dist/SEST_Integration/vessels/wp_pb_don.ini", "[General]\nUnitType=Vessel\n")
        self.write("integration/missions/01 Threads.ini",
                   "[Unit1]\nType=usn_f-14a\nFlightDeck_ReadyUpTask1=usn_e-2c,Squadron1,AEW,2,0\n")
        self.write(f"{CAMPAIGN}/missions/X 01.ini", "[Unit1]\nType=USN_F-14A\n")
        self.write(f"{CAMPAIGN}/campaign.ini",
                   "[Mission1]\nType=Mission\nTaskForceModeAllowedRosterUnits=WP_SS_KILO,Variant1|ran_ffh_anzac,Variant3\n")
        self.write(f"{CAMPAIGN}/player_task_force_roster.ini",
                   "; roster\n[AllowedSubmarines]\n; syntax is: <unit_type>=<variant>,...|<points>\nwp_ss_kilo=Variant1|300\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "baseline export")
        self.baseline = self.git("rev-parse", "HEAD").strip()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args):
        return subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args],
                              cwd=self.root, env=self.env, check=True, capture_output=True, text=True).stdout

    def run_tool(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = drift.main(["--root", str(self.root), *argv])
        return code, out.getvalue()

    def section(self, text, number):
        """The lines of report section <number>."""
        lines = text.splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith(f"{number}. "))
        end = next(i for i in range(start + 2, len(lines)) if lines[i] == drift.BANNER)
        return "\n".join(lines[start + 2:end])

    def test_an_unchanged_export_passes(self):
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("added 0, removed 0, modified 0, line endings only 0", out)
        self.assertTrue(out.splitlines()[-1].startswith("Vanilla drift: PASS - no drift"))

    def test_default_revision_is_the_last_commit_that_touched_the_export(self):
        self.write("README.md", "unrelated\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "docs only")
        self.assertEqual(drift.export_commits(self.root, 1)[0][0], self.baseline)
        code, out = self.run_tool()
        self.assertEqual(code, 0)
        self.assertIn(f"Vanilla drift since {self.baseline[:8]}\n", out)

    def test_an_unknown_revision_is_refused(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_tool("--since", "no-such-commit")
        self.assertIn("not a commit", str(caught.exception))

    def test_a_revision_without_an_export_is_refused(self):
        self.git("rm", "-r", "-q", "--cached", VANILLA)
        self.git("commit", "-q", "-m", "no export in this commit")
        with self.assertRaises(SystemExit) as caught:
            self.run_tool("--since", "HEAD")
        self.assertIn(f"no {VANILLA} is committed at that revision", str(caught.exception))

    def test_a_modified_file_under_a_static_override_needs_a_human(self):
        self.write(f"{VANILLA}/vessels/wp_pb_don.ini", "[General]\nUnitType=Vessel\nLength=110\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 1)
        self.assertIn("vessels/wp_pb_don.ini  modified\n      SEST_Static_Pack: STATIC COPY", self.section(out, 1))
        self.assertNotIn("SEST_Integration", out)
        read = self.section(out, 4)
        self.assertIn("integration/static-pack/build_patch.py:1  \"\"\"Ships a hand-forked vessels/wp_pb_don.ini.\"\"\"  (comment)", read)
        self.assertIn("integration/static-pack/build_patch.py:2  # see \"wp_pb_don\" upstream  (comment)", read)
        self.assertIn("integration/static-pack/build_patch.py:3  OUT = 1  # vessels/wp_pb_don.ini, by hand  (comment)", read,
                      "a trailing comment is not code")
        self.assertIn("integration/static-pack/build_patch.py:5  Description=a copy of vessels/wp_pb_don.ini with one fix  (text)", read,
                      "a description template is not code")
        self.assertIn("NEEDS A HUMAN: vessels/wp_pb_don.ini (modified): SEST_Static_Pack ships a static copy", out)

    def test_the_vanilla_manifest_is_nobody_s_override(self):
        self.write(f"{VANILLA}/_info.ini", "[Language_en]\nName=Sea Power 0.8.3\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertEqual(self.section(out, 1).strip(), "none")
        self.assertEqual(self.section(out, 4).strip(), "none", "a pack writing its own _info.ini does not read vanilla's")
        self.assertIn(".: 1\n      _info.ini  modified", self.section(out, 7))

    def test_a_modified_file_under_a_builder_derived_override_is_only_noted(self):
        self.write(f"{VANILLA}/ammunition/usn_gbu-24.ini", "[General]\nType=Bomb\nWeight=1050\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("SEST_Collection_Fixes: builder-derived, a rebuild rebases it "
                      "(integration/collection-fixes/build_patch.py:1  t = read(", self.section(out, 1))
        self.assertIn("ammunition/usn_gbu-24.ini  modified\n      integration/collection-fixes/build_patch.py:1",
                      self.section(out, 4))
        self.assertTrue(out.splitlines()[-1].startswith("Vanilla drift: PASS - 1 file(s) changed"))

    def test_a_folder_written_from_data_is_derived_by_pattern(self):
        self.write(f"{VANILLA}/ammunition/wp_sa-n-1.ini", "[General]\nType=Missile\nAmmoPoints=120\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("ammunition/wp_sa-n-1.ini  modified\n"
                      "      SEST_Metered: builder-derived by pattern - the builder writes the folder from data "
                      "(integration/metered/build_patch.py:2  write(f\"ammunition/{rid}.ini\"", self.section(out, 1))
        self.assertEqual(self.section(out, 4).strip(), "none", "a pattern is not a name")
        self.assertNotIn("NEEDS A HUMAN", out)

    def test_a_vanilla_key_a_pack_also_defines_is_a_clash(self):
        self.write(f"{VANILLA}/language_en/loadout_names.ini",
                   "[LoadoutNames]\nAirToAir=Air-to-Air    // renamed\nStrike=Strike\nSIGINT=Signals Intelligence\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 1)
        merged = self.section(out, 2)
        self.assertIn("language_en/loadout_names.ini  modified  (also shipped by 1 pack(s))\n"
                      "      SEST_Collection_Fixes:\n"
                      "         CLASH [LoadoutNames] SIGINT is new in vanilla; the next build stops on it\n"
                      "         [LoadoutNames] AirToAir: vanilla value 'Air to Air' -> 'Air-to-Air'; the pack's copy masks it",
                      merged)
        self.assertEqual(self.section(out, 1).strip(), "none", "a merge file is not an override")
        self.assertEqual(out.count("NEEDS A HUMAN:"), 1, "a changed value under a shared key is not a finding")
        self.assertIn("NEEDS A HUMAN: language_en/loadout_names.ini: vanilla now defines [LoadoutNames] SIGINT, "
                      "which SEST_Collection_Fixes also defines", out)

    def test_a_merge_file_change_sharing_no_keys_is_only_listed(self):
        self.write(f"{VANILLA}/systems/sensors.ini", "[General]\nDataLinkUpdateRate=2\n\n[Start_ECM]\nType=ECM\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("systems/sensors.ini  modified  (also shipped by 1 pack(s))\n"
                      "      no shared keys: SEST_Collection_Fixes", self.section(out, 2))

    def test_a_removed_merge_file_leaves_the_pack_s_copy_standing(self):
        (self.root / VANILLA / "systems/sensors.ini").unlink()
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("systems/sensors.ini  removed  (also shipped by 1 pack(s))\n"
                      "      vanilla no longer ships it; the packs' copies stand alone: SEST_Collection_Fixes",
                      self.section(out, 2))

    def test_a_vanilla_sensor_section_a_pack_also_defines_is_a_clash(self):
        self.write(f"{VANILLA}/systems/sensors.ini",
                   "[General]\nDataLinkUpdateRate=1\n\n[Start_ECM]\nType=ECM\n\n[Side_Globe]\nType=ECM\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 1)
        self.assertIn("CLASH [Side_Globe] is new in vanilla", self.section(out, 2))
        self.assertIn("NEEDS A HUMAN: systems/sensors.ini: vanilla now defines [Side_Globe], "
                      "which SEST_Collection_Fixes also defines", out)

    def test_a_removed_unit_a_mission_fields_needs_a_human(self):
        (self.root / VANILLA / "aircraft/usn_f-14a.ini").unlink()
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 1)
        placed = self.section(out, 3)
        self.assertIn("aircraft/usn_f-14a.ini  REMOVED - usn_f-14a fielded by 2 file(s): "
                      "dist/SEST_Integration/campaigns/sest-x/missions/X 01.ini, missions/01 Threads.ini", placed)
        self.assertIn("NEEDS A HUMAN: aircraft/usn_f-14a.ini: removed, but 2 file(s) field usn_f-14a", out)

    def test_a_removed_unit_a_workshop_mod_still_ships_is_not_a_finding(self):
        # 0.8.3 dropped the game's Tu-16N stub; the Tu-16N mod's copy is what
        # Southern Watch D7 fields, so the unit stands.
        self.write("mods-source/3673908868/aircraft/usn_f-14a.ini", "[General]\nUnitType=Aircraft\n")
        (self.root / VANILLA / "aircraft/usn_f-14a.ini").unlink()
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0, out)
        placed = self.section(out, 3)
        self.assertIn("aircraft/usn_f-14a.ini  removed - usn_f-14a fielded by 2 file(s): ", placed)
        self.assertIn("; still shipped by 3673908868", placed)
        self.assertNotIn("NEEDS A HUMAN", out)

    def test_a_roster_or_flight_deck_unit_is_fielded_too(self):
        (self.root / VANILLA / "vessels/wp_ss_kilo.ini").unlink()
        (self.root / VANILLA / "aircraft/usn_e-2c.ini").unlink()
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 1)
        placed = self.section(out, 3)
        self.assertIn("aircraft/usn_e-2c.ini  REMOVED - usn_e-2c fielded by 1 file(s): missions/01 Threads.ini", placed)
        self.assertIn("vessels/wp_ss_kilo.ini  REMOVED - wp_ss_kilo fielded by 2 file(s): "
                      "dist/SEST_Integration/campaigns/sest-x/campaign.ini, "
                      "dist/SEST_Integration/campaigns/sest-x/player_task_force_roster.ini", placed)
        self.assertEqual(out.count("NEEDS A HUMAN:"), 2)

    def test_a_changed_squadrons_file_of_a_fielded_unit_is_only_listed(self):
        self.write(f"{VANILLA}/aircraft/usn_f-14a_squadrons.ini", "[Default]\nNation=US\nServiceDate=1974|1991\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("aircraft/usn_f-14a_squadrons.ini  modified (via its squadrons file) - usn_f-14a fielded by 2",
                      self.section(out, 3))

    def test_an_added_unit_is_a_candidate_with_its_facts(self):
        self.write(f"{VANILLA}/aircraft/usn_f-47.ini", "[General]\nUnitType=Aircraft\nCarrierCapable=True\n")
        self.write(f"{VANILLA}/aircraft/usn_f-47_squadrons.ini", "[Default]\nNation=US\nServiceDate=2029\n")
        self.write(f"{VANILLA}/ammunition/usn_aim-260.ini", "[General]\nType=Missile\nTargetType=AAW\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        new = self.section(out, 5)
        self.assertIn("aircraft/usn_f-47.ini  UnitType=Aircraft  Nation=US  ServiceDate=2029  (from usn_f-47_squadrons.ini)", new)
        self.assertIn("ammunition/usn_aim-260.ini  UnitType=Missile AAW  (no squadrons/variants file)", new)
        self.assertNotIn("aircraft/usn_f-47_squadrons.ini", new)
        self.assertEqual(self.section(out, 7).strip(), "none", "the squadrons file rides with its unit")
        self.assertIn("added 3, removed 0, modified 0", out)

    def test_a_line_endings_only_change_is_set_aside(self):
        (self.root / VANILLA / "clouds.ini").write_bytes(b"[Clouds]\r\nDensity=1\r\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("added 0, removed 0, modified 0, line endings only 1", out)
        self.assertIn("clouds.ini", self.section(out, 6))
        self.assertEqual(self.section(out, 7).strip(), "none")
        self.assertIn("Vanilla drift: PASS - 0 file(s) changed, 1 line endings only", out.splitlines()[-1])

    def test_a_file_a_builder_reads_is_reported_under_builder_read(self):
        self.write(f"{VANILLA}/language_en/nations.ini", "[Nations]\nUS=United States\nAU=Australia\n")
        self.write(f"{VANILLA}/clouds.ini", "[Clouds]\nDensity=2\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("language_en/nations.ini  modified\n      integration/allied-fixes/build_patch.py:1",
                      self.section(out, 4))
        self.assertNotIn("clouds.ini", self.section(out, 4), "mission['clouds'] is not the export's clouds.ini")
        self.assertIn(".: 1\n      clouds.ini  modified", self.section(out, 7))

    def test_a_name_is_found_with_spaces_in_it_and_in_any_case(self):
        self.write(f"{VANILLA}/missions/Warsaw Pact/Northern Passage.ini", "[Unit1]\nType=wp_pb_don\nHeading=90\n")
        self.write(f"{VANILLA}/aircraft/fr_alouette_II.ini", "[General]\nUnitType=Helicopter\nCrew=2\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        read = self.section(out, 4)
        self.assertIn("missions/Warsaw Pact/Northern Passage.ini  modified\n      integration/allied-fixes/build_patch.py:3", read)
        self.assertIn("aircraft/fr_alouette_II.ini  modified\n      integration/allied-fixes/build_patch.py:4", read)
        self.assertEqual(self.section(out, 7).strip(), "none")

    def test_a_nested_mission_module_is_a_builder_but_caches_and_tests_are_not(self):
        self.write(f"{VANILLA}/aircraft/usn_f-14a.ini", "[General]\nUnitType=Aircraft\nCrew=2\n")
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        read = self.section(out, 4)
        self.assertIn("integration/campaign/southern_reach/sr01_departure.py:1", read)
        self.assertNotIn("__pycache__", read)
        self.assertNotIn("test_build_pack.py", read)

    def test_the_game_version_is_read_at_both_ends(self):
        self.assertEqual(drift.game_version(CHANGELOG),
                         dict(date="20-Jul-2026", version="0.8.2", build="358", number="23444", note="Public Release"))
        self.assertEqual(drift.game_version(CHANGELOG.replace("\n", "\r\n"))["note"], "Public Release")
        self.assertIsNone(drift.game_version("Change log\n----------\n"))
        self.assertIsNone(drift.game_version(""))
        self.write("mods-source/_vanilla/changelog.txt", CHANGELOG.replace("=\n\n", "=\n\n" + NEW_ENTRY, 1))
        code, out = self.run_tool("--since", self.baseline)
        self.assertEqual(code, 0)
        self.assertIn("Game version: 0.8.2 Build #358 (20-Jul-2026) -> 0.8.3 Build #361 (02-Oct-2026)\n", out)
        self.assertNotIn("[unchanged]", out)

    def test_the_changelog_shape_since_september_2026_is_read(self):
        # The game dropped the "#" and the "(N)" on 28 Sep 2026 and suffixes
        # a letter to a same-day build: these are the real 0.8.3 lines.
        self.assertEqual(drift.game_version("01-Oct-2026: 0.8.3 Build 261001 Public Release\n"),
                         dict(date="01-Oct-2026", version="0.8.3", build="261001", number=None,
                              note="Public Release"))
        self.assertEqual(drift.game_version("28-Sep-2026: 0.8.2 Build 260928b\n")["build"], "260928b")


if __name__ == "__main__":
    unittest.main()
