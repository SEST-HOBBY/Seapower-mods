import hashlib
import re
import unittest

from helpers import BREAKTHROUGH, HORMUZ, REPO

from mno_env.mission_ini import (PatchRefused, WeatherState, is_weather_only, patch, read_mission_bytes,
                                 references, sections)

STAGES = [WeatherState("Broken", 3), WeatherState("Overcast", 5, rain=True),
          WeatherState("Overcast", 7, rain=True, thunderstorm=True), WeatherState("Clear", 2)]

MINI = """[Language_en]
Name=Mini
Description=Test

[Language_de]
Name=Mini DE

[Environment]
Date=1990,1,1
Time=12,0
SeaState=2
Clouds=Broken
Clouds=Overcast
Weather=Fog

[Mission]
NumberOfTriggers={n}

[Trigger1]  #weather
Condition_Type=Time
Condition_Time=600
Action_SetClouds=Clear

[Trigger2]  #mixed
Condition_Type=Time
Condition_Time=900
Action_SetRain=False   // inline comment
Action_Units=Taskforce1Vessel1
Action_SetEnabledStatus=False

[Trigger3]  #logic
Condition_Type=Time
Condition_Time=5
Action_DisableTriggers=Trigger1
{extra}"""


def mini(n=3, extra=""):
    return MINI.format(n=n, extra=extra)


class TestPatchRules(unittest.TestCase):
    def test_weather_only_disabled_and_counter(self):
        out, r = patch(mini(), STAGES)
        self.assertEqual(r.disabled_weather_only, [1])
        self.assertEqual(r.number_of_triggers_after, 6)
        self.assertIn("NumberOfTriggers=6", out)
        self.assertEqual([int(x) for x in re.findall(r"(?m)^\[Trigger(\d+)\]", out)], [1, 2, 3, 4, 5, 6])
        t1 = out[out.index("[Trigger1]"):out.index("[Trigger2]")]
        self.assertIn("Disabled=True", t1)
        self.assertIn("Action_SetClouds=Clear", t1)  # disabled, not deleted

    def test_mixed_trigger_keeps_other_lines(self):
        out, r = patch(mini(), STAGES)
        t2 = out[out.index("[Trigger2]"):out.index("[Trigger3]")]
        self.assertNotIn("Action_SetRain", t2)
        self.assertIn("Action_Units=Taskforce1Vessel1", t2)
        self.assertIn("Action_SetEnabledStatus=False", t2)
        self.assertNotIn("Disabled=True", t2)
        self.assertEqual(r.stripped_mixed, {2: ["Action_SetRain=False   // inline comment"]})

    def test_environment_duplicates_resolved(self):
        out, r = patch(mini(), STAGES)
        env = out[out.index("[Environment]"):out.index("[Mission]")]
        self.assertEqual(re.findall(r"(?m)^Clouds=.*", env), ["Clouds=Broken"])
        self.assertEqual(re.findall(r"(?m)^SeaState=.*", env), ["SeaState=3"])
        self.assertEqual(re.findall(r"(?m)^Weather=.*", env), [])
        self.assertEqual(sorted(r.environment_removed_lines), sorted(["SeaState=2", "Clouds=Broken", "Clouds=Overcast", "Weather=Fog"]))

    def test_every_language_renamed_en_description_replaced(self):
        out, r = patch(mini(), STAGES, en_description="LAB")
        self.assertIn("Name=MNO Weather Lab: Mini\n", out)
        self.assertIn("Name=MNO Weather Lab: Mini DE\n", out)
        self.assertIn("Description=LAB\n", out)
        self.assertEqual(sorted(r.renamed_languages), ["de", "en"])

    def test_enable_reference_refuses_then_strips(self):
        src = mini(n=4, extra="\n[Trigger4]\nCondition_Type=Time\nCondition_Time=50\nAction_EnableTriggers=Trigger1\n")
        with self.assertRaises(PatchRefused):
            patch(src, STAGES)
        out, r = patch(src, STAGES, referenced_weather="strip")
        t1 = out[out.index("[Trigger1]"):out.index("[Trigger2]")]
        self.assertNotIn("Action_SetClouds", t1)
        self.assertNotIn("Disabled=True", t1)
        self.assertEqual(r.stripped_referenced, [1])
        self.assertTrue(r.warnings)

    def test_reactivate_and_timer_references_refuse(self):
        for line in ("Action_ReactivateTriggers=Trigger1", "Action_MissionTimerSourceTrigger=Trigger1"):
            src = mini(n=4, extra=f"\n[Trigger4]\nCondition_Type=Time\nCondition_Time=50\n{line}\n")
            with self.assertRaises(PatchRefused, msg=line):
                patch(src, STAGES)

    def test_existing_disabled_false_is_replaced_not_duplicated(self):
        src = mini().replace("[Trigger1]  #weather\n", "[Trigger1]  #weather\nDisabled=False\n")
        out, r = patch(src, STAGES)
        t1 = out[out.index("[Trigger1]"):out.index("[Trigger2]")]
        self.assertEqual(re.findall(r"(?m)^Disabled=.*", t1), ["Disabled=True"])

    def test_disable_reference_still_disabled(self):
        out, r = patch(mini(), STAGES)  # Trigger3 disables Trigger1: harmless, so Trigger1 is disabled
        self.assertEqual(r.disabled_weather_only, [1])

    def test_commented_reference_is_not_a_reference(self):
        src = mini(n=4, extra="\n[Trigger4]\nCondition_Type=Time\nCondition_Time=50\n#Action_EnableTriggers=Trigger1\nAction_Units=X\n")
        self.assertNotIn(1, {k for k, v in references(src).items() if "Enable" in v})
        patch(src, STAGES)

    def test_refusals(self):
        with self.assertRaises(PatchRefused):  # duplicate ids
            patch(mini(n=3, extra="\n[Trigger3]\nCondition_Type=Time\nCondition_Time=1\nAction_Units=X\n"), STAGES)
        with self.assertRaises(PatchRefused):  # N below highest id
            patch(mini(n=2), STAGES)
        with self.assertRaises(PatchRefused):  # no NumberOfTriggers
            patch(mini().replace("NumberOfTriggers=3\n", ""), STAGES)
        with self.assertRaises(PatchRefused):
            patch(mini().replace("[Environment]", "[Environment]\n[Environment]"), STAGES)
        with self.assertRaises(PatchRefused):
            read_mission_bytes("Name=\xe9".encode("latin-1"))

    def test_counter_above_highest_id_appends_after_counter(self):
        out, r = patch(mini(n=7), STAGES)
        self.assertEqual([int(x) for x in re.findall(r"(?m)^\[Trigger(\d+)\]", out)], [1, 2, 3, 8, 9, 10])
        self.assertEqual(r.number_of_triggers_after, 10)

    def test_state_validation(self):
        with self.assertRaises(ValueError):
            patch(mini(), [WeatherState("Broken", 3), WeatherState("Broken", 6, thunderstorm=True)])
        with self.assertRaises(ValueError):
            patch(mini(), [WeatherState("Broken", 3), WeatherState("Overcast", 6, snow=True)])
        with self.assertRaises(ValueError):
            patch(mini(), [WeatherState("Cumulus", 3)])
        with self.assertRaises(ValueError):
            patch(mini(), [WeatherState("Broken", 13)])
        out, _ = patch(mini(), [WeatherState("Overcast", 4, snow=True)])
        self.assertIn("Weather=Snow", out)
        self.assertNotIn("Action_SetSnow", out)

    def test_crlf_and_bom_preserved(self):
        src = "﻿" + mini().replace("\n", "\r\n")
        out, r = patch(src, STAGES)
        self.assertTrue(out.startswith("﻿"))
        self.assertNotIn("\n", out.replace("\r\n", ""))
        self.assertEqual(r.newline, "\r\n")

    def test_explicit_times_and_conditions_style(self):
        src = mini().replace("Condition_Type=Time\nCondition_Time=5", "Condition_Condition1_Type=Time\nCondition_Condition1_Time=5\nConditionsCompleted=<Condition1>")
        src = src.replace("Condition_Type=Time\nCondition_Time=600", "Condition_Condition1_Type=Time\nCondition_Condition1_Time=600\nConditionsCompleted=<Condition1>")
        src = src.replace("Condition_Type=Time\nCondition_Time=900", "Condition_Condition1_Type=Time\nCondition_Condition1_Time=900\nConditionsCompleted=<Condition1>")
        out, r = patch(src, STAGES, times=[100, 1000, 5000])
        self.assertEqual(r.trigger_style, "conditions")
        self.assertEqual([a["time_s"] for a in r.appended], [100, 1000, 5000])
        self.assertIn("Condition_Condition1_Time=5000", out)
        with self.assertRaises(ValueError):
            patch(src, STAGES, times=[100, 50, 5000])

    def test_mission_time(self):
        out, _ = patch(mini(), STAGES, mission_time=(10, 0))
        self.assertIn("Time=10,0\n", out)


@unittest.skipUnless(HORMUZ.exists() and BREAKTHROUGH.exists(), "vanilla export not present")
class TestVanilla(unittest.TestCase):
    def test_hormuz(self):
        raw = HORMUZ.read_bytes()
        before = hashlib.sha256(raw).hexdigest()
        out, r = patch(read_mission_bytes(raw), STAGES)
        self.assertEqual(hashlib.sha256(HORMUZ.read_bytes()).hexdigest(), before)
        # Hormuz's own weather triggers 7-10 are not referenced by any other trigger.
        self.assertEqual(r.disabled_weather_only, [7, 8, 9, 10])
        self.assertEqual((r.number_of_triggers_before, r.number_of_triggers_after), (10, 13))
        self.assertEqual(r.newline, "\r\n")
        refs = references(read_mission_bytes(raw))
        self.assertEqual(refs, {1: {"Enable", "Reactivate"}})  # the commented lines 391-392 do not count

    def test_breakthrough_duplicate_clouds(self):
        out, r = patch(read_mission_bytes(BREAKTHROUGH.read_bytes()), STAGES)
        self.assertIn("Clouds=Overcast", r.environment_removed_lines)
        self.assertIn("Clouds=Scattered_2", r.environment_removed_lines)
        self.assertIn("Weather=Rain,Thunderstorm", r.environment_removed_lines)
        self.assertEqual(r.disabled_weather_only, list(range(7, 16)))


class TestCorpus(unittest.TestCase):
    """Every mission INI in the repository either patches cleanly (and passes verify()) or is
    refused with a reason. Nothing else may happen."""

    def test_all_repository_missions(self):
        roots = [REPO / "mods-source", REPO / "integration"]
        ok = refused = 0
        for root in roots:
            for path in root.rglob("*.ini"):
                if "MNO-Environmental-Playtest" in str(path):
                    continue
                raw = path.read_bytes()
                if b"NumberOfTriggers" not in raw:
                    continue
                try:
                    patch(read_mission_bytes(raw), STAGES)
                    ok += 1
                except PatchRefused:
                    refused += 1
        self.assertGreater(ok, 250)
        self.assertLess(refused, ok / 10)

    def test_weather_only_detection(self):
        self.assertTrue(is_weather_only("[Trigger1]\nAction_SetClouds=Clear\nAction_Forecast=X\n"))
        self.assertFalse(is_weather_only("[Trigger1]\nAction_Forecast=X\n"))
        self.assertFalse(is_weather_only("[Trigger1]\nAction_SetClouds=Clear\nAction_Units=X\n"))
        self.assertEqual([s.name for s in sections("[ ==== Triggers ==== ]\n[Trigger1] #c\nA=1\n")], ["==== Triggers ====", "Trigger1"])


if __name__ == "__main__":
    unittest.main()
