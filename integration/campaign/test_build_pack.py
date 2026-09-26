#!/usr/bin/env python3
"""Tests for the builder rules no shipped mission exercises.

The pack build and tools/check_campaign_coverage.py prove Southern Watch and
Southern Reach as built. They cannot prove a rule neither campaign uses, and
every case here is one of those: a spec key a third campaign must set, a
victory term that used to compile silently into a different condition, a
predicate or a gate a mission played from the other side needs. Each test
builds the smallest mission that shows the rule and reads the lines the
builder emits. Nothing is written into the tree.

    python3 integration/campaign/test_build_pack.py
"""
import importlib.abc
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import build_pack as bp  # noqa: E402
import check_campaign_coverage as coverage_check  # noqa: E402
from campaign_data import S  # noqa: E402

_ABSENT = object()


# --- a small mission, rendered ----------------------------------------------
# The ceasefire-morning shape from the Red Line design: a frigate, a carrier
# withdrawing, an armed coaster in company that has turned for the convoy
# lane, a Poseidon overhead. Positions are in the mission's NM frame and are
# written straight into `placed`, so render() runs without the proven-point
# pool or the coastline.

def _keys(uid, x, z, **extra):
    return dict(Type=uid, RelativePositionInNM=f"{x},0,{z}", **extra)


def small_mission(**over):
    m = dict(
        key="Test Withdrawal", code="T01", num="01", group="core",
        brief="Brief.", win="Won.", lose="Lost.", timeout="Out of time.",
        date=(2028, 11, 28), time=(5, 10), sea=2, clouds="Clear", wind="E",
        centre=(-4.6, 128.9), blue_nation="China", red_nation="Australia",
        minutes=80, role="escort",
        stations={"escort": S(-4.45, 128.85, "Escort"),
                  "group": S(-4.50, 128.70, "Carrier group"),
                  "spoiler": S(-4.62, 128.90, "Armed coaster"),
                  "red_air": S(-4.00, 129.40, "Poseidon", alt=14000)},
        objectives=[("Withdrawal", "Withdraw north-west", "35,-35,Fail,Main"),
                    ("Spoiler", "Stop the coaster", "20,-40,Complete")],
        victory=dict(kind="arrive", station="group", at=(-4.30, 128.60),
                     radius=12, objective="Withdrawal"),
        resolve={"Withdrawal": "victory", "Spoiler": ("protect", "escort")},
        units=[])
    m.update(over)
    return m


def small_placement():
    placed = {
        "Taskforce1Vessel": [
            ("Taskforce1Vessel1", _keys("plan_type_054a_p5", 0, 9), None, False),
            ("Taskforce1Vessel2", _keys("plan_type_001", -12, 6), "Liaoning", False)],
        "Taskforce2Vessel": [
            ("Taskforce2Vessel1", _keys("ran_ms_super_p", 0, -1), "MV Meridian Harmony", False)],
        "Taskforce2Aircraft": [
            ("Taskforce2Aircraft1", _keys("usn_p8", 30, 36), None, False)],
    }
    members = {"escort": ["Taskforce1Vessel1"], "group": ["Taskforce1Vessel2"],
               "spoiler": ["Taskforce2Vessel1"], "red_air": ["Taskforce2Aircraft1"]}
    return placed, members


def rendered(mission, placed=None, members=None):
    """render() -> {trigger name: [lines]}, after the pack checker's own
    trigger-integrity pass has read the whole file."""
    if placed is None:
        placed, members = small_placement()
    _name, text = bp.render(mission, placed, members)
    parsed = coverage_check.blocks(text)
    problems = coverage_check.trigger_integrity(HERE / "test.ini", text, parsed)
    if problems:
        raise AssertionError("\n".join(problems))
    triggers = {}
    for line in text.split("\n\n"):
        rows = line.strip().splitlines()
        if rows and rows[0].startswith("[Trigger"):
            triggers[rows[1].partition("=")[2]] = rows[2:]
    return triggers


class _BrokenRedLine(importlib.abc.MetaPathFinder):
    """A red_line package whose own import fails on a missing dependency."""

    def find_spec(self, name, path, target=None):
        if name == "red_line":
            raise ModuleNotFoundError("No module named 'red_line_dependency'",
                                      name="red_line_dependency")
        return None


class CampaignRegistry(unittest.TestCase):
    """A third campaign is registered by its package being in the tree."""

    def setUp(self):
        self.saved = sys.modules.get("red_line", _ABSENT)

    def tearDown(self):
        if self.saved is _ABSENT:
            sys.modules.pop("red_line", None)
        else:
            sys.modules["red_line"] = self.saved

    @staticmethod
    def fake_red_line(**spec):
        mod = types.ModuleType("red_line")
        mod.__file__ = str(HERE / "red_line" / "__init__.py")
        mod.CAMPAIGN = dict(dict(
            SLUG="sest-red-line", TITLE="Red Line",
            DOCS_DIR=bp.ROOT / "docs" / "campaigns" / "red-line",
            COVERAGE_DOC=bp.ROOT / "docs" / "campaigns" / "red-line" / "coverage.md",
            INFO_DESC="", EXCUSES={}), **spec)
        return mod

    def test_absent_package_builds_the_two_campaigns(self):
        sys.modules["red_line"] = None          # import raises, named red_line
        self.assertEqual([s["SLUG"] for s in bp.campaign_specs()],
                         ["sest-southern-watch", "sest-southern-reach"])

    def test_present_package_is_appended_last(self):
        sys.modules["red_line"] = self.fake_red_line()
        self.assertEqual([s["SLUG"] for s in bp.campaign_specs()],
                         ["sest-southern-watch", "sest-southern-reach", "sest-red-line"])

    def test_a_folder_holding_only_pycache_counts_as_absent(self):
        sys.modules["red_line"] = types.ModuleType("red_line")   # no __file__
        self.assertEqual(len(bp.campaign_specs()), 2)

    def test_a_package_that_fails_to_import_stops_the_build(self):
        sys.modules.pop("red_line", None)
        finder = _BrokenRedLine()
        sys.meta_path.insert(0, finder)
        try:
            with self.assertRaises(ModuleNotFoundError) as caught:
                bp.campaign_specs()
            self.assertEqual(caught.exception.name, "red_line_dependency")
        finally:
            sys.meta_path.remove(finder)

    def test_every_campaigns_excuses_count_for_the_pack(self):
        sys.modules["red_line"] = self.fake_red_line(
            EXCUSES={"red-line-only-mod": ("library", "a reason")})
        merged = bp.pack_excuses(bp.campaign_specs())
        self.assertIn("red-line-only-mod", merged)
        self.assertIn("anchor-chain", merged)     # Southern Watch's own

    def test_two_campaigns_may_not_share_a_report(self):
        reach = bp.ROOT / "docs" / "campaigns" / "southern-reach" / "coverage.md"
        sys.modules["red_line"] = self.fake_red_line(COVERAGE_DOC=reach)
        with self.assertRaisesRegex(SystemExit, "Southern Reach and Red Line both set COVERAGE_DOC"):
            bp.campaign_specs()


class CampaignFiles(unittest.TestCase):
    """Only Southern Watch may leave out the paths main() writes into docs/."""

    def tearDown(self):
        bp.set_campaign(bp.campaign_specs()[0])

    def test_southern_watch_may_rely_on_its_defaults(self):
        bp.set_campaign(dict(SLUG="sest-southern-watch", INFO_DESC=""))
        self.assertEqual(bp.COVERAGE_DOC, bp.ROOT / "docs" / "campaign-coverage.md")

    def test_the_shipped_specs_pass(self):
        for spec in bp.campaign_specs():
            bp.set_campaign(spec)
            self.assertEqual(bp.COVERAGE_DOC, spec["COVERAGE_DOC"])

    def test_a_new_campaign_must_name_its_own(self):
        for key in ("DOCS_DIR", "COVERAGE_DOC"):
            spec = dict(CampaignRegistry.fake_red_line().CAMPAIGN)
            del spec[key]
            with self.assertRaisesRegex(SystemExit, f"Red Line: the spec sets no {key}"):
                bp.set_campaign(spec)

    def test_a_new_campaign_may_not_borrow_southern_watchs(self):
        spec = dict(CampaignRegistry.fake_red_line().CAMPAIGN,
                    COVERAGE_DOC=bp.ROOT / "docs" / "campaign-coverage.md")
        with self.assertRaisesRegex(SystemExit, "COVERAGE_DOC is Southern Watch's"):
            bp.set_campaign(spec)


class VictoryAlsoTerms(unittest.TestCase):
    """An `also` term compiles to the condition its kind names, or stops the
    build. kind='destroyed' used to come out as an area test on the same
    units - the spoiler inside the arrival box - and the mission it was
    written for could not be won."""

    def win(self, also, **victory):
        v = dict(small_mission()["victory"], also=also, **victory)
        return rendered(small_mission(victory=v))

    def test_destroyed_term_is_a_kill(self):
        lines = self.win([dict(kind="destroyed", units=["spoiler"])])["Objective met"]
        self.assertIn("Condition_Condition2_Type=UnitDestroyed", lines)
        self.assertIn("Condition_Condition2_Units=Taskforce2Vessel1", lines)
        self.assertIn("Condition_Condition2_MinimumUnits=1", lines)
        self.assertIn("ConditionsCompleted=<Condition1> AND <Condition2>", lines)
        self.assertNotIn("Condition_Condition2_Type=UnitsInTheArea", lines)

    def test_area_and_time_terms_read_as_before(self):
        lines = self.win([dict(units=["escort"], min_units=1),
                          dict(after_minutes=70)])["Objective met"]
        self.assertIn("Condition_Condition2_Type=UnitsInTheArea", lines)
        self.assertIn("Condition_Condition2_AreaRadiusNM=12", lines)
        self.assertIn("Condition_Condition3_Type=Time", lines)
        self.assertIn("Condition_Condition3_Time=4200", lines)
        self.assertIn("ConditionsCompleted=<Condition1> AND <Condition2> AND <Condition3>",
                      lines)

    def test_unknown_kind_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "kind 'sunk'"):
            self.win([dict(kind="sunk", units=["spoiler"])])

    def test_unknown_key_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "'minimum'"):
            self.win([dict(units=["spoiler"], minimum=1)])

    def test_a_key_the_kind_does_not_read_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "'radius'"):
            self.win([dict(kind="destroyed", units=["spoiler"], radius=5)])

    def test_the_per_unit_chain_reads_the_same_terms(self):
        stage = dict(kind="area", units="escort", at=(-4.45, 128.85), radius=3,
                     per_unit=True)
        triggers = self.win([dict(kind="destroyed", units=["spoiler"])], after=stage)
        lines = triggers["Objective met by Taskforce1Vessel1"]
        self.assertIn("Condition_Condition2_Type=UnitDestroyed", lines)
        with self.assertRaisesRegex(SystemExit, "kind 'sunk'"):
            self.win([dict(kind="sunk", units=["spoiler"])], after=stage)


if __name__ == "__main__":
    unittest.main(verbosity=2)
