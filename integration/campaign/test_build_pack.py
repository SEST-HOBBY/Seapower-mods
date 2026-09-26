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
import contextlib
import importlib.abc
import io
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import build_pack as bp  # noqa: E402
import check_campaign_coverage as coverage_check  # noqa: E402
from campaign_data import F, S, U  # noqa: E402
try:
    import make_art  # noqa: E402
except ImportError:          # Pillow missing: the art tests are skipped
    make_art = None

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
                    ("Spoiler", "Stop the coaster", "20,-40,Fail")],
        victory=dict(kind="arrive", station="group", at=(-4.30, 128.60),
                     radius=12, objective="Withdrawal"),
        resolve={"Withdrawal": "victory", "Spoiler": ("destroy", "spoiler", 1)},
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

    def test_a_term_no_win_can_meet_stops_the_build(self):
        for term, why in ((dict(kind="destroyed", units=[]), r"\[\]"),
                          (dict(units=[]), r"\[\]"),
                          (dict(kind="destroyed", units=["spoiler"], min_units=5), "5 of"),
                          (dict(units=["escort"], min_units=0), "0 of"),
                          (dict(after_minutes=80), "minute 80"),
                          (dict(after_minutes=0), "minute 0"),
                          (dict(kind="time", after_minutes=70.5), "minute 70.5"),
                          (("destroyed", "spoiler"), "is a dict")):
            with self.assertRaisesRegex(SystemExit, why, msg=repr(term)):
                self.win([term])

    def test_a_destroyed_term_on_the_players_own_units_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "player's own Taskforce1Vessel1"):
            self.win([dict(kind="destroyed", units=["escort"])])

    def test_the_per_unit_chain_reads_the_same_terms(self):
        stage = dict(kind="area", units="escort", at=(-4.45, 128.85), radius=3,
                     per_unit=True)
        triggers = self.win([dict(kind="destroyed", units=["spoiler"])], after=stage)
        lines = triggers["Objective met by Taskforce1Vessel1"]
        self.assertIn("Condition_Condition2_Type=UnitDestroyed", lines)
        with self.assertRaisesRegex(SystemExit, "kind 'sunk'"):
            self.win([dict(kind="sunk", units=["spoiler"])], after=stage)


STOCK = bp.ROOT / "mods-source" / "_vanilla" / "original" / "missions"


class UnseenObjective(unittest.TestCase):
    """('unseen', station): fails when the ENEMY classifies those player
    units, in stock's own shape; F(..., kind="unseen") ends the mission on it."""

    def mission(self, fatal=(), how=("unseen", "escort"), spec="25,-40,Complete"):
        m = small_mission()
        m["objectives"] = m["objectives"] + [("Unseen", "Stay unclassified", spec)]
        m["resolve"] = dict(m["resolve"], Unseen=how)
        m["fatal"] = list(fatal)
        return m

    def test_the_condition_is_stocks_own(self):
        stock = coverage_check.blocks(
            (STOCK / "Warsaw Pact" / "Operation Polar Fury 1985.ini").read_text(
                encoding="utf-8-sig", errors="replace"))["Trigger5"]
        want = [k for k in stock if k.startswith("Condition")]
        lines = rendered(self.mission())["Unseen classified by the enemy"]
        got = [l.partition("=")[0] for l in lines if l.startswith("Condition")]
        self.assertEqual(got, want)
        self.assertEqual(stock["Condition_Condition1_Taskforce"], "Taskforce2")

    def test_the_resolver_fails_the_objective(self):
        lines = rendered(self.mission())["Unseen classified by the enemy"]
        self.assertEqual(lines, [
            "Condition_Condition1_Type=UnitClassified",
            "Condition_Condition1_Taskforce=Taskforce2",
            "Condition_Condition1_Units=Taskforce1Vessel1",
            "Condition_Condition1_MinimumUnits=1",
            "ConditionsCompleted=<Condition1>",
            "Action_ObjectivesFailed=Unseen"])

    def test_the_fatal_ends_the_mission(self):
        triggers = rendered(self.mission(fatal=[F("Unseen", kind="unseen")]))
        lines = triggers["Unseen classified by the enemy - mission over"]
        for want in ("Condition_Condition1_Type=UnitClassified",
                     "Condition_Condition1_Taskforce=Taskforce2",
                     "Condition_Condition1_Units=Taskforce1Vessel1",
                     "Action_Victory=Taskforce2", "Action_ObjectivesFailed=Unseen",
                     "Action_EnableTriggers=Trigger1"):
            self.assertIn(want, lines)
        self.assertEqual(triggers["Mission exit"][-2:],
                         ["Action_EndMission=True", "Action_EndMissionDelay=0"])

    def test_a_fatal_may_name_a_subset_and_nothing_else(self):
        rendered(self.mission(fatal=[F("Unseen", ["escort"], kind="unseen")]))
        with self.assertRaisesRegex(SystemExit, "reporting the wrong ship"):
            rendered(self.mission(fatal=[F("Unseen", ["group"], kind="unseen")]))

    def test_only_the_players_units_can_be_unseen(self):
        with self.assertRaisesRegex(SystemExit, "Taskforce2Vessel1"):
            rendered(self.mission(how=("unseen", "spoiler")))
        with self.assertRaisesRegex(SystemExit, "Taskforce2Vessel1"):
            rendered(self.mission(fatal=[F("Unseen", ["spoiler"], kind="unseen")],
                                  how=("spare", "spoiler")))

    def test_it_only_fails_so_it_cannot_end_fail(self):
        with self.assertRaisesRegex(SystemExit, "ends Fail"):
            rendered(self.mission(spec="25,-40,Fail"))

    def test_the_resolver_names_stations_only(self):
        # protect reads a trailing count; unseen has none, and used to drop it
        for how in (("unseen", "escort", 2), ("unseen", ["escort", "group"])):
            with self.assertRaisesRegex(SystemExit, "names stations", msg=repr(how)):
                rendered(self.mission(how=how))

    def test_a_fatal_minimum_runs_from_one_to_the_count(self):
        two = ("unseen", "escort", "group")
        lines = rendered(self.mission(how=two, fatal=[F("Unseen", kind="unseen", minimum=2)]))[
            "Unseen classified by the enemy - mission over"]
        self.assertIn("Condition_Condition1_Units=Taskforce1Vessel1,Taskforce1Vessel2", lines)
        self.assertIn("Condition_Condition1_MinimumUnits=2", lines)
        for least in (0, 3):     # 0 ends the mission on its first tick; 3 never
            with self.assertRaisesRegex(SystemExit, "minimum= runs from 1"):
                rendered(self.mission(how=two, fatal=[F("Unseen", kind="unseen",
                                                        minimum=least)]))

    def test_an_unknown_fatal_kind_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "'sighted'"):
            rendered(self.mission(fatal=[F("Unseen", ["escort"], kind="sighted")]))

    def test_unseen_units_are_not_escorted_hulls(self):
        placed, members = small_placement()
        m = self.mission(fatal=[F("Unseen", kind="unseen")])
        self.assertNotIn("Taskforce1Vessel1", bp.protected_tags(m, members))


class StandoffAndClosure(unittest.TestCase):
    """The standoff gate ignores a red unit that will not shoot and is not
    built to; the closure gate counts an armed boat as an escort and leaves
    a hull marked independent=True alone. Real units, placed by the builder
    on the coastline extract, well south of the Bight."""

    STATIONS = {"tender": S(-47.50, 140.50, "Tender"),
                "boat": S(-47.50, 140.70, "Boat"),          # 12 NM east
                "far_boat": S(-47.50, 141.20, "Far boat"),  # 42 NM east
                "decoy": S(-47.50, 142.00, "Decoy"),        # 90 NM east
                "spoiler": S(-47.53, 140.50, "In company")}  # 1.8 NM south

    TENDER = dict(side="blue", mod="_vanilla", type="civ_ms_kommunist",
                  station="tender", weapons="Hold")
    DECOY = dict(side="blue", mod="modern-plan-systems", type="plan_type_054a_p5",
                 station="decoy", weapons="Hold")
    BOAT = dict(side="blue", mod="plan-submarines", type="plan_ss_type_039c",
                station="boat", depth="belowlayer", weapons="Hold")

    def setUp(self):
        for lst in (bp.PLACEMENT_PROBLEMS, bp.COAST_CHECKED, bp.CLOSURE_PROBLEMS,
                    bp.CLOSURE_NOTES, bp.REACH_PROBLEMS):
            del lst[:]

    def placed(self, units):
        m = dict(key="Test Quiet Side", num="06", group="core", centre=(-47.5, 140.5),
                 minutes=80, role="escort", stations=self.STATIONS,
                 units=[dict(u) for u in units],
                 victory=dict(kind="arrive", station="tender", at=(-47.30, 140.20),
                              radius=6, objective="Rendezvous"),
                 objectives=[("Rendezvous", "Meet", "35,-35,Fail,Main")],
                 resolve={"Rendezvous": "victory"}, fatal=[])
        placed, members, _credits, _far = bp.place(m, bp.CoastPlacer(bp.coast_data(), m))
        self.assertEqual(bp.PLACEMENT_PROBLEMS, [])
        return m, placed, members

    def standoff(self, red):
        m, placed, members = self.placed([self.TENDER, self.DECOY, red])
        bp.check_reach(m, placed, members)
        return [p for p in bp.REACH_PROBLEMS if "opens with red" in p]

    def closure(self, units):
        m, placed, members = self.placed(units)
        bp.check_closure(m, placed, members)
        return bp.CLOSURE_PROBLEMS

    def test_a_passive_spoiler_may_start_in_company(self):
        self.assertEqual(self.standoff(dict(
            side="red", mod="auxilliary-merchant-pack", type="ran_ms_super_p",
            station="spoiler", weapons="Hold")), [])

    def test_the_same_hull_weapons_free_may_not(self):
        self.assertEqual(len(self.standoff(dict(
            side="red", mod="auxilliary-merchant-pack", type="ran_ms_super_p",
            station="spoiler", weapons="Free"))), 1)

    def test_a_warship_at_hold_may_not(self):
        self.assertEqual(len(self.standoff(dict(
            side="red", mod="SEST_RAN_Fleet", type="ran_ffh_anzac",
            station="spoiler", weapons="Hold"))), 1)

    def test_a_role_the_builder_does_not_name_is_not_passive(self):
        # Role=SSGN is in neither list, so is_combat() says no; a 1,000 NM
        # Tomahawk boat at Hold must still not start inside the standoff.
        self.assertFalse(bp.is_combat("usn_ssgn_ohio"))
        self.assertFalse(bp.is_passive("usn_ssgn_ohio"))
        self.assertTrue(bp.is_passive("ran_ms_super_p"))
        self.assertEqual(len(self.standoff(dict(
            side="red", mod="us-submarines", type="usn_ssgn_ohio",
            station="spoiler", depth="periscope", weapons="Hold"))), 1)

    def test_the_decoy_alone_is_too_far_to_escort(self):
        problems = self.closure([self.TENDER, self.DECOY])
        self.assertEqual(len(problems), 1)
        self.assertIn("Taskforce1Vessel1 (civ_ms_kommunist) is protected", problems[0])
        self.assertIn("at 24 kn", problems[0])

    def test_an_armed_boat_escorts_her_tender(self):
        self.assertEqual(self.closure([self.TENDER, self.DECOY, self.BOAT]), [])

    def test_a_boat_is_held_to_a_boats_speed(self):
        problems = self.closure([self.TENDER, dict(self.BOAT, station="far_boat")])
        self.assertEqual(len(problems), 1)
        self.assertIn("at 10 kn", problems[0])

    def test_an_independent_hull_is_not_measured(self):
        self.assertEqual(self.closure([dict(self.TENDER, independent=True),
                                       self.DECOY]), [])

    def test_only_the_players_hulls_can_be_independent(self):
        with self.assertRaises(SystemExit):
            self.placed([self.TENDER, dict(
                side="red", mod="auxilliary-merchant-pack", type="ran_ms_super_p",
                station="spoiler", weapons="Hold", independent=True)])


SIGNAL = dict(file="99_test_signal", form="signal",
              header=[("FROM", "FLEET HQ"), ("TO", "COMMANDER CARRIER TASK GROUP")],
              body=["1. THE GROUP IS NOT AT WAR WITH ANY STATE."],
              note="Para 3 is the order.")
LOG = dict(file="99_test_log", form="log", ship="Test Ship", master="A. Test",
           date="28 November 2028", entries=[("0510", "Group turned north-west.")],
           note="Acknowledged.  - A.T.")
INTSUM = dict(file="99_test_intsum", form="intsum", org="Fleet HQ", ref="INTSUM 01",
              date="22 December 2028", subject="Test", body=["The picture."])


@unittest.skipIf(make_art is None, "Pillow is not installed")
class StoryArt(unittest.TestCase):
    """The page labels a campaign played from the other side needs, and only
    the map tiles something stands on."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sest-art-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def png(self, draw, *args, **kw):
        out = self.tmp / "page.png"
        with contextlib.redirect_stdout(io.StringIO()):
            draw(out, *args, **kw)
        return out.read_bytes()

    def render_all(self, events, **kw):
        with contextlib.redirect_stdout(io.StringIO()):
            make_art.render_all(self.tmp / "camp", [], events, "sest-test",
                                "Test", "Subtitle", **kw)
        return self.tmp / "camp" / "art"

    def signal(self, **kw):
        return self.png(make_art.signal, SIGNAL["header"], SIGNAL["body"],
                        note=SIGNAL["note"], **kw)

    def log(self, **kw):
        return self.png(make_art.log, LOG["ship"], LOG["master"], LOG["date"],
                        LOG["entries"], note=LOG["note"], **kw)

    def test_the_defaults_draw_what_they_drew(self):
        self.assertEqual(self.signal(), self.signal(note_label="ANALYST NOTE"))
        self.assertEqual(self.log(), self.log(heading="DECK LOG EXTRACT",
                                              master_label="MASTER",
                                              note_label="MASTER'S NOTE"))

    def test_each_label_changes_the_page(self):
        self.assertNotEqual(self.signal(), self.signal(note_label="SENDER'S NOTE"))
        for key, value in (("heading", "LOG EXTRACT"), ("master_label", "CAPTAIN"),
                           ("note_label", "CAPTAIN'S NOTE")):
            self.assertNotEqual(self.log(), self.log(**{key: value}), key)

    def test_render_all_passes_the_event_keys_through(self):
        art = self.render_all([
            dict(SIGNAL, note_label="SENDER'S NOTE"),
            dict(LOG, log_heading="LOG EXTRACT", master_label="CAPTAIN",
                 note_label="CAPTAIN'S NOTE"),
            dict(INTSUM, marking="SECRET  //  FLEET HQ ONLY")])
        self.assertEqual((art / "99_test_signal_image.png").read_bytes(),
                         self.signal(note_label="SENDER'S NOTE"))
        self.assertEqual((art / "99_test_log_image.png").read_bytes(),
                         self.log(heading="LOG EXTRACT", master_label="CAPTAIN",
                                  note_label="CAPTAIN'S NOTE"))
        self.assertEqual((art / "99_test_intsum_image.png").read_bytes(),
                         self.png(make_art.intsum, INTSUM["org"], INTSUM["ref"],
                                  INTSUM["date"], INTSUM["subject"], INTSUM["body"],
                                  marking="SECRET  //  FLEET HQ ONLY"))

    def test_only_the_tiles_the_events_stand_on_are_written(self):
        events = [SIGNAL, LOG]
        art = self.render_all(events, tiles={bp.event_tile(e) for e in events})
        self.assertEqual(sorted(f.name for f in art.glob("bkg_tile_*.png")),
                         ["bkg_tile_message.png"])

    def test_a_tile_that_is_not_one_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "no map tile called press"):
            self.render_all([SIGNAL], tiles={"press", "message"})
        self.assertFalse((self.tmp / "camp").exists())

    def test_the_tile_rule(self):
        self.assertEqual(bp.event_tile(dict(file="x")), "newspaper")
        self.assertEqual({bp.event_tile(e) for e in (SIGNAL, LOG, INTSUM)}, {"message"})


class RosterAndSeahawk(unittest.TestCase):
    """Generated text that assumed Southern Watch: the roster file's header
    and footer, and a Seahawk's squadron chosen by side instead of flag."""

    GEN = "; Generated by integration/campaign/build_pack.py - edit "

    def tearDown(self):
        bp.set_campaign(bp.campaign_specs()[0])

    def roster(self, spec):
        bp.set_campaign(spec)
        return bp.roster_ini(spec["ROSTER"])[0].splitlines()

    def red(self, *units):
        return dict(CampaignRegistry.fake_red_line().CAMPAIGN,
                    ROSTER=[dict(unit=u, picks=["Variant1"], points=100) for u in units])

    def test_each_roster_names_the_file_to_edit(self):
        watch, reach = bp.campaign_specs()[:2]
        self.assertEqual(self.roster(watch)[1], self.GEN + "campaign_data.py.")
        self.assertEqual(self.roster(reach)[1], self.GEN + "southern_reach/tables.py.")
        red = self.roster(self.red("plan_type_054a_p5"))
        self.assertEqual(red[0], "; SEST Red Line requisition roster.")
        self.assertEqual(red[1], self.GEN + "the Red Line campaign's roster.")
        red = self.roster(dict(self.red("plan_type_054a_p5"),
                               ROSTER_SOURCE="red_line/tables.py"))
        self.assertEqual(red[1], self.GEN + "red_line/tables.py.")

    def test_the_footer_says_what_the_hulls_on_sale_declare(self):
        self.assertEqual(self.roster(self.red("plan_type_054a_p5"))[-1],
                         "; and tested - no hull on this roster declares one.")
        self.assertEqual(self.roster(self.red("plan_type_054a_p5", "plan_type_056a"))[-2:],
                         ["; and tested.",
                          "; plan_type_056a declares Default, AntiShip, ASW; "
                          "none is priced here."])
        self.assertIn("; ran_opv_arafura declares Containers, AntiShip, AntiAir; "
                      "none is priced here.", self.roster(bp.campaign_specs()[0]))

    def squadron(self, side, blue_nation, red_nation, **kw):
        m = dict(key="Test Seahawk", num="01", group="core", centre=(-47.5, 140.5),
                 minutes=60, blue_nation=blue_nation, red_nation=red_nation,
                 stations={"deck": S(-47.50, 140.50, "Deck"),
                           "flight": S(-47.48, 140.50, "Flight", alt=500)},
                 units=[U(side, "SEST_RAN_Fleet", "ran_ffh_anzac", "deck", weapons="Hold"),
                        U(side, "us-navy-2027", "usn_mh-60r", "flight", **kw)])
        placed, _members, _credits, _far = bp.place(m, bp.CoastPlacer(bp.coast_data(), m))
        family = "Taskforce1Helicopter" if side == "blue" else "Taskforce2Helicopter"
        return placed[family][0][1]["SquadronReference"]

    def test_an_australian_seahawk_is_816_squadron_on_either_side(self):
        self.assertEqual(self.squadron("blue", "Australia", "China"), "Squadron20")
        self.assertEqual(self.squadron("red", "China", "Australia"), "Squadron20")

    def test_anybody_elses_keeps_the_files_default(self):
        self.assertEqual(self.squadron("red", "Australia", "USA"), "Squadron1")
        self.assertEqual(self.squadron("blue", "China", "Australia"), "Squadron1")

    def test_the_units_own_flag_and_an_explicit_squadron_win(self):
        self.assertEqual(self.squadron("red", "China", "USA", nation="australia"),
                         "Squadron20")
        self.assertEqual(self.squadron("red", "China", "Australia", squadron="Squadron2"),
                         "Squadron2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
