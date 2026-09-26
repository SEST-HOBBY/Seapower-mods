#!/usr/bin/env python3
"""Regression checks for mission removal and the Banda Front Lean handover.

Run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_trim_land_sites.py' -v
"""
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MISSIONS = ROOT / "integration" / "missions"
sys.path.insert(0, str(MISSIONS))
import trim_land_sites as trim  # noqa: E402
from build_land_defence import Mission  # noqa: E402


class RemovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / "fixture.ini"
        text = (
            "[Mission]\nNumberOfTaskforce1LandUnits=12\nNumberOfTaskforce2LandUnits=1\n"
            "Taskforce1_NumberOfFormations=1\n"
            "Taskforce1_Formation1=Taskforce1LandUnit1, Taskforce1LandUnit10|Base|Circle|1.5\n"
            "[Environment]\nMapCenterLatitude=-10\nMapCenterLongitude=125\n"
        )
        for side, count in (("Taskforce1", 12), ("Taskforce2", 1)):
            for n in range(1, count + 1):
                text += (f"[{side}LandUnit{n}]\nType=airfield_small_1\n"
                         f"RelativePositionInNM={n},low,0\n")
        for language in ("en", "fr"):
            text += (f"[Language_{language}]\nName=Fixture\n"
                     "Taskforce1LandUnit1NameOverride=Remove me\n"
                     "Taskforce1LandUnit10NameOverride=Keep ten\n"
                     "Taskforce1LandUnit10ShortNameOverride=Ten\n")
        path.write_text(text, encoding="utf-8")
        self.mission = Mission(path)
        self.assertEqual([], self.mission.verify())

    def test_renumbers_spaced_formations_and_language_keys_without_prefix_collision(self):
        self.mission.remove_land_units("Taskforce1", {"Taskforce1LandUnit1"})
        self.assertEqual([], self.mission.verify())
        self.assertEqual(["Taskforce1LandUnit9"],
                         self.mission.formation_specs("Taskforce1")[0][2])
        for language in ("en", "fr"):
            body = self.mission.body(f"[Language_{language}]")
            self.assertNotIn("Remove me", body)
            self.assertIn("Taskforce1LandUnit9NameOverride=Keep ten", body)
            self.assertIn("Taskforce1LandUnit9ShortNameOverride=Ten", body)

    def test_mixed_side_additions_survive_one_side_being_renumbered(self):
        blue = self.mission.add_land_unit("Taskforce1", "airfield_small_1", "Default", 0, 0, 0)
        red = self.mission.add_land_unit("Taskforce2", "airfield_small_1", "Default", 1, 1, 0)
        mapping = self.mission.remove_land_units("Taskforce1", {"Taskforce1LandUnit1"})
        self.assertEqual([mapping[blue], red], self.mission.added)
        self.assertEqual([], self.mission.verify())

    def test_empty_formation_is_refused(self):
        with self.assertRaisesRegex(SystemExit, "would empty"):
            self.mission.remove_land_units("Taskforce1", {"Taskforce1LandUnit1", "Taskforce1LandUnit10"})

    def test_reference_to_deleted_unit_outside_a_formation_is_refused(self):
        self.mission.sections.append(("[Trigger1]", "Target=Taskforce1LandUnit1\n"))
        with self.assertRaisesRegex(SystemExit, "still names deleted unit"):
            self.mission.remove_land_units("Taskforce1", {"Taskforce1LandUnit1"})

    def test_grounding_removes_aircraft_ids_with_spaces(self):
        for i, (header, body) in enumerate(self.mission.sections):
            if header == "[Taskforce1LandUnit1]":
                self.mission.sections[i] = (header, body +
                    "CustomAirGroup=True\nplaf_j16a block3=Squadron1,2|Default,1\n")
        self.mission.set_custom_air_group("Taskforce1LandUnit1")
        self.assertEqual((True, []), self.mission.air_group("Taskforce1LandUnit1"))
        self.assertNotIn("plaf_j16a", self.mission.body("[Taskforce1LandUnit1]"))


class StrayBatteryTests(unittest.TestCase):
    def setUp(self):
        self.mission = Mission(MISSIONS / "SEST Banda Front EDITED.ini")
        self.args = SimpleNamespace(tels=3, coastal=2, tbm=2, drones=2,
                                    technicals=2, keep_bmd=True)

    def detach(self, names):
        index, lines = self.mission._mission_lines()
        for n, key, members, tail in self.mission.formation_specs("Taskforce1"):
            kept = [m for m in members if m not in names]
            self.assertTrue(kept, "fixture must not empty a formation")
            lines[n] = f"{key}={','.join(kept)}{tail}"
        self.mission._set_mission_lines(index, lines)

    def decide_and_check(self):
        side = trim.Side(self.mission, "Taskforce1")
        trimmer = trim.Trimmer(side, self.args)
        trimmer.decide()
        removed = set(trimmer.removals())
        kept = set(side.units) - removed
        for unit in side.strays:
            self.assertIn(unit["name"], kept)
        for name in kept:
            radar = side.units[name]["fcr"]
            if radar:
                self.assertIn(radar, kept, f"{name} lost its radar")
        for form in side.forms:
            self.assertTrue(set(form["keep"]) <= set(form["members"]),
                            "a keep decision must belong to the unit's actual formation")
        self.mission.remove_land_units("Taskforce1", removed)
        self.assertEqual([], self.mission.verify())
        return side, kept

    def test_unformed_guidance_radar_keeps_its_formed_battery(self):
        side = trim.Side(self.mission, "Taskforce1")
        radar = next(u for u in side.units.values() if u["kind"] == "radar" and u["tels"]
                     and any(side.units[t]["kind"] == "tel" for t in u["tels"]))
        self.detach({radar["name"]})
        _, kept = self.decide_and_check()
        self.assertIn(radar["name"], kept)
        self.assertTrue(set(radar["tels"]) & kept)

    def test_unformed_launcher_preserves_its_guidance_radar(self):
        side = trim.Side(self.mission, "Taskforce1")
        launcher = next(u for u in side.units.values() if u["kind"] == "tel" and u["fcr"])
        self.detach({launcher["name"]})
        _, kept = self.decide_and_check()
        self.assertIn(launcher["name"], kept)
        self.assertIn(launcher["fcr"], kept)

    def test_wholly_unformed_bmd_battery_is_preserved(self):
        side = trim.Side(self.mission, "Taskforce1")
        launcher = next(u for u in side.units.values() if u["kind"] == "bmd_tel" and u["fcr"])
        radar = side.units[launcher["fcr"]]
        names = {radar["name"], *radar["tels"]}
        self.detach(names)
        _, kept = self.decide_and_check()
        self.assertTrue(names <= kept)


class BandaFrontHandoverTests(unittest.TestCase):
    def test_source_preservation_reference_integrity_and_repeatable_output(self):
        source = MISSIONS / "SEST Banda Front EDITED.ini"
        expected = (MISSIONS / "SEST Banda Front Lean.ini").read_bytes()
        before = source.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            shutil.copyfile(source, temp / source.name)
            with patch.object(trim, "MISSIONS", temp), patch.object(sys, "argv", ["trim_land_sites.py"]):
                with contextlib.redirect_stdout(io.StringIO()):
                    trim.main()
                    first = (temp / "SEST Banda Front Lean.ini").read_bytes()
                    trim.main()
                self.assertEqual(first, (temp / "SEST Banda Front Lean.ini").read_bytes())
            self.assertEqual(expected, first)
            self.assertEqual(before, (temp / source.name).read_bytes())
            original = Mission(source)
            lean = Mission(temp / "SEST Banda Front Lean.ini")
            self.assertEqual([], lean.verify())
            self.assertEqual(414, sum(len(lean.units(side, "LandUnit")) for side in trim.SIDES))
            for side in trim.SIDES:
                original_forms = [(key, tail) for _, key, _, tail in original.formation_specs(side)]
                lean_forms = [(key, tail) for _, key, _, tail in lean.formation_specs(side)]
                self.assertEqual(original_forms, lean_forms)
                for cls in ("Vessel", "Submarine", "Aircraft", "Biologic"):
                    self.assertEqual(original.units(side, cls), lean.units(side, cls))
                # All surviving blue/red blocks, including their air groups, are verbatim.
                if side != "Neutral":
                    old_bodies = Counter(body for *_, body in original.units(side, "LandUnit"))
                    new_bodies = Counter(body for *_, body in lean.units(side, "LandUnit"))
                    self.assertFalse(new_bodies - old_bodies)
            grounded = [name for name, *_ in lean.units("Neutral", "LandUnit")
                        if lean.air_group(name)[0]]
            self.assertEqual(15, len(grounded))
            for name in grounded:
                self.assertEqual((True, []), lean.air_group(name))
        self.assertEqual(before, source.read_bytes())


if __name__ == "__main__":
    unittest.main()
