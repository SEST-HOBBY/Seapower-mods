"""Runtime mission ribbons, read the way SEST Runtime 1.6.5 reads them.

The beta runtime R13 (MissionAwards.cs, integration/beta-feature-parity/
runtime/ on feature/runtime-mission-awards-20261110 at 77abfbfe) grants the
ribbons a campaign names in [Mission<N>] SestRuntimeRibbonAwards. The game,
Runtime 1.6.4 and the standard build ignore the key. This file ports the
runtime's reader to Python, line for line:

- MissionAwardsTests.cs:397-402 (AsRead): how IniHandler hands the value
  over: cut at ';', '//' or '#', split on '=', each piece trimmed and the
  pieces after the key rejoined with '='. ReadValues (MissionAwards.cs:
  253-266) then trims it.
- ParseSpecs (MissionAwards.cs:329-348): at most 4096 characters (:47,
  :336), split on '|', blanks skipped, one bad spec rejects the key, at most
  32 specs (:47, :344).
- ParseSpec (:350-366): the part before '?' goes to the native
  TryParseMissionRibbonAwardSpec, which splits on ',' and cuts the id before
  ':' (MissionAwardsTests.cs:186-187); its NormalizeRibbonId is not ported,
  so every id here is held to [a-z0-9_]+, which a trim or a case fold leaves
  as it is. The conditions after '?' split on '&'.
- ParseTerm (:368-406): nolaunch; objective:<id>=completed|failed|cancelled|
  notfailed; result>=<MissionDebriefViewModel.Result name>; rescued>=1-999
  (digits only, NumberStyles.None). Case is ignored, and spaces may stand
  before ':' and '>='.

The port is held to the runtime's own grammar cases (MissionAwardsTests.cs:
520-556), and then every value build_pack.py wrote into the five campaigns
under integration/campaign/SEST_Campaign is parsed with it. Each awarded id
must have its [Ribbon_<id>] definition, which the runtime reads
(ReadRibbonDefinition, MissionAwards.cs:287), must not be listed in
[TaskForceRibbons] RibbonIds (the developer catalogue and its grant), must
not be a native award, and may name only the mission's own objectives.
"""
import importlib.util
import json
from datetime import date
from pathlib import Path
import re
import unittest
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "integration/campaign/service_awards.py"
spec = importlib.util.spec_from_file_location("service_awards", SOURCE)
awards = importlib.util.module_from_spec(spec)
spec.loader.exec_module(awards)
PACK = ROOT / "integration/campaign/SEST_Campaign"
UI = ROOT / "mods-source/_vanilla/original/language_en/ui.ini"
KEY = "SestRuntimeRibbonAwards"                         # MissionAwards.cs:45
MAX_SPECS, MAX_VALUE = 32, 4096                         # MissionAwards.cs:47

# MissionDebriefViewModel.Result: ui.ini names its 18 values best first
# (Result_Incomplete, then DecisiveVictory down to CompleteDefeat); the enum
# runs Incomplete (0), CompleteDefeat (1) ... DecisiveVictory (17), which
# MissionAwardsTests.cs:237-240 pins on the beta (PyrrhicVictory 9, Draw 10,
# CostlyVictory 11, MajorVictory 16).
_NAMES = re.findall(r"^Result_(\w+)=", UI.read_text(encoding="utf-8-sig"), re.M)
RESULTS = (_NAMES[0],) + tuple(reversed(_NAMES[1:]))

# The owner's two awards (11 Nov 2026), as the runtime normalises them:
# (campaign, [MissionN], code) -> [(id, nations, terms)].
EXPECTED = {
    ("sest-red-line", "Mission15", "RL05"): [
        ("sest_silent_passage", [], ["objective:Passage=completed", "nolaunch"])],
    ("sest-red-line", "Mission11", "RLC1"): [
        ("sest_personnel_recovery", [], ["objective:Pilot=completed", "rescued>=1"])],
}


class Term(NamedTuple):
    kind: str
    id: str
    text: str
    number: int


class Spec(NamedTuple):
    raw: str
    ribbon_id: str
    nations: list
    terms: list


def as_read(line):
    """MissionAwardsTests.cs:397-402: the value IniHandler returns for a
    'Key=value' line."""
    text = re.split(r";|//|#", line)[0].strip()
    return "=".join(part.strip() for part in text.split("=")[1:])


OBJECTIVE_PREFIX = re.compile(r"^objective\s*:", re.I)                    # MissionAwards.cs:369
AT_LEAST_PREFIX = re.compile(r"^(?P<name>result|rescued)\s*>=", re.I)     # MissionAwards.cs:370


def parse_term(text):
    """MissionAwards.cs:372-406 (ParseTerm). None for an invalid term."""
    if text.lower() == "nolaunch":                                         # :374
        return Term("nolaunch", "", "nolaunch", 0)
    objective = OBJECTIVE_PREFIX.match(text)                               # :375-394
    if objective:
        rest = text[objective.end():]
        eq = rest.find("=")
        if eq <= 0:
            return None
        oid, want = rest[:eq].strip(), rest[eq + 1:].strip().lower()
        if not oid or want not in ("completed", "failed", "cancelled", "notfailed"):
            return None
        return Term("objective", oid, f"objective:{oid}={want}", 0)
    at_least = AT_LEAST_PREFIX.match(text)                                 # :395-397
    if not at_least:
        return None
    value = text[at_least.end():].strip()
    if at_least["name"].lower() == "result":                               # :398-403
        match = next((n for n in RESULTS if n.lower() == value.lower()), None)
        if match is None:
            return None
        return Term("result", match, "result>=" + match, RESULTS.index(match))
    if not re.fullmatch(r"[0-9]+", value) or not 1 <= int(value) <= 999:   # :404, NumberStyles.None
        return None
    return Term("rescued", "", f"rescued>={int(value)}", int(value))


def parse_spec(raw):
    """MissionAwards.cs:350-366 (ParseSpec): (Spec, None) or (None, error)."""
    split = raw.find("?")
    if split < 0:
        return None, "has no '?' conditions"
    fields = raw[:split].strip().split(",")                                # TryParseMissionRibbonAwardSpec
    rid = fields[0].split(":")[0].strip()
    if not rid:
        return None, "has no ribbon id"
    terms = []
    for piece in raw[split + 1:].split("&"):
        term = parse_term(piece.strip())
        if term is None:
            return None, f"has an unknown or invalid condition '{piece.strip()}'"
        terms.append(term)
    return Spec(raw, rid, [f.strip() for f in fields[1:] if f.strip()], terms), None


def parse_specs(values):
    """MissionAwards.cs:329-348 (ParseSpecs): (specs, error). Fail closed."""
    specs = []
    for value in values:
        if len(value) > MAX_VALUE:
            return specs, f"value longer than {MAX_VALUE} characters"
        for piece in value.split("|"):
            raw = piece.strip()
            if not raw:
                continue
            parsed, error = parse_spec(raw)
            if parsed is None:
                return [], f"spec '{raw}' {error}"
            specs.append(parsed)
            if len(specs) > MAX_SPECS:
                return [], f"more than {MAX_SPECS} specs"
    return specs, None


def section(text, name):
    m = re.search(r"(?ms)^\[" + re.escape(name) + r"\][^\n]*\n(.*?)(?=^\[|\Z)", text)
    return dict((k.strip(), v) for k, v in re.findall(r"^([^=\n;#]+)=(.*)$", m[1], re.M)) if m else {}


class RuntimeGrammarPort(unittest.TestCase):
    """The port accepts and rejects what the runtime's own tests say it does."""

    def test_result_names_are_the_beta_enum(self):
        self.assertEqual(len(RESULTS), 18)
        for name, value in (("Incomplete", 0), ("PyrrhicVictory", 9), ("Draw", 10), ("CostlyVictory", 11),
                            ("MajorVictory", 16), ("DecisiveVictory", 17)):
            self.assertEqual(RESULTS.index(name), value, name)
        self.assertEqual(awards.RESULTS, RESULTS)

    def test_the_runtime_grammar_cases(self):
        # MissionAwardsTests.cs:521-522
        one, error = parse_specs(["sest_rl05_passage?objective:Passage=completed&objective:Unseen=completed&nolaunch"])
        self.assertIsNone(error)
        self.assertEqual([(s.ribbon_id, len(s.terms)) for s in one], [("sest_rl05_passage", 3)])
        # :523-524
        two, error = parse_specs([" a?nolaunch | | b,China?rescued>=1 ", "c?result>=MajorVictory"])
        self.assertIsNone(error)
        self.assertEqual([s.ribbon_id for s in two], ["a", "b", "c"])
        self.assertEqual(two[1].nations, ["China"])
        # :525-528
        mixed, error = parse_specs(["A:3,US?NoLaunch&Objective:Pilot=COMPLETED&Result>=majorvictory&RESCUED>=2"
                                    "&objective: Boat = notfailed"])
        self.assertIsNone(error)
        terms = mixed[0].terms
        self.assertEqual((mixed[0].ribbon_id, len(terms)), ("A", 5))
        self.assertEqual((terms[2].id, terms[2].number, terms[3].number, terms[4].id, terms[4].text),
                         ("MajorVictory", 16, 2, "Boat", "objective:Boat=notfailed"))
        # :531-536
        spaced, error = parse_specs(["s ? objective :Passage=completed & Objective : Boat = NotFailed & result >= "
                                     "CostlyVictory & RESCUED >=2 & rescued>= 3 & Result\t>=\tdraw"])
        self.assertIsNone(error)
        self.assertEqual([t.text for t in spaced[0].terms],
                         ["objective:Passage=completed", "objective:Boat=notfailed", "result>=CostlyVictory",
                          "rescued>=2", "rescued>=3", "result>=Draw"])
        self.assertEqual([t.number for t in spaced[0].terms[2:]], [11, 2, 3, 10])
        # :537-543: one bad spec rejects the whole key.
        for bad in ("a", "a?", "a?nofire", "a?nolaunch&", "?nolaunch", " ,?nolaunch", "a?rescued>=0",
                    "a?rescued>=1000", "a?rescued>=x", "a?rescued>=-1", "a?rescued>=+1", "a?objective:x=done",
                    "a?objective:=completed", "a?objective:x", "a?result>=Win", "a?result>=11",
                    "a?launched<=0", "a?result> =Draw", "a?result > = Draw", "a?rescued> =1",
                    "a?objectives:x=completed", "a?objective x=completed", "a?results>=Draw", "a?no launch"):
            with self.subTest(bad=bad):
                specs, error = parse_specs(["ok?nolaunch|" + bad])
                self.assertEqual(specs, [])
                self.assertIsNotNone(error)
        # :544-545
        self.assertIsNotNone(parse_specs(["x" * 4097 + "?nolaunch"])[1])
        self.assertIsNotNone(parse_specs(["|".join(f"r{n}?nolaunch" for n in range(33))])[1])
        self.assertIsNone(parse_specs(["|".join(f"r{n}?nolaunch" for n in range(32))])[1])

    def test_the_ini_reader_cases(self):
        # MissionAwardsTests.cs:548-556
        line = ("SestRuntimeRibbonAwards = sest_rl05_passage?objective:Passage = completed&objective:Unseen=completed"
                "&nolaunch|sest_rlc1_recovery,US?objective:Pilot=completed&rescued>=1")
        specs, error = parse_specs([as_read(line)])
        self.assertIsNone(error)
        self.assertEqual([s.ribbon_id for s in specs], ["sest_rl05_passage", "sest_rlc1_recovery"])
        spaced = ("SestRuntimeRibbonAwards = sest_rlc1_recovery ? objective : Pilot = completed & rescued >= 1 & "
                  "result >= CostlyVictory")
        self.assertEqual(as_read(spaced),
                         "sest_rlc1_recovery ? objective : Pilot=completed & rescued >=1 & result >=CostlyVictory")
        self.assertEqual(len(parse_specs([as_read(spaced)])[0][0].terms), 3)
        cut = "SestRuntimeRibbonAwards=sest_x;objective:Passage=completed"
        self.assertEqual(as_read(cut), "sest_x")
        self.assertEqual(parse_specs([as_read(cut)]), ([], "spec 'sest_x' has no '?' conditions"))


class RuntimeAwardData(unittest.TestCase):
    """service_awards' runtime table and the checks the build makes."""

    def setUp(self):
        saved = awards.RUNTIME
        self.addCleanup(setattr, awards, "RUNTIME", saved)

    def mission(self, code="RL05", **extra):
        rows = {"RL05": ("Under the Convergence", (2028, 12, 27),
                         [("Passage",), ("Unseen",), ("Restraint",), ("Boat",), ("Traffic",)]),
                "RLC1": ("Pilot in the Water", (2028, 11, 24),
                         [("Pilot",), ("Restraint",), ("Watchers",), ("Traffic",)])}
        key, when, objectives = rows[code]
        return dict(dict(code=code, key=key, date=when, objectives=objectives), **extra)

    def table(self, **row):
        base = dict(id="sest_test_award", name="Test Ribbon", why="For testing Under the Convergence",
                    stripes=(("#000000", 1),), terms=(("nolaunch",),))
        awards.RUNTIME = {"sest-red-line": {"RL05": (dict(base, **row),)}}

    def test_the_red_line_specs(self):
        self.assertEqual(awards.runtime_mission_awards("sest-red-line", self.mission("RL05")),
                         ["sest_silent_passage?objective:Passage=completed&nolaunch"])
        self.assertEqual(awards.runtime_mission_awards("sest-red-line", self.mission("RLC1")),
                         ["sest_personnel_recovery?objective:Pilot=completed&rescued>=1"])
        self.assertEqual(awards.runtime_grants("sest-red-line"),
                         {"sest_silent_passage": "RL05", "sest_personnel_recovery": "RLC1"})
        for slug in ("sest-southern-watch", "sest-southern-reach", "sest-sulu-line", "third-party-campaign"):
            self.assertEqual(awards.runtime_grants(slug), {})
        self.assertEqual(awards.runtime_mission_awards("third-party-campaign", {"code": "RL05"}), [])

    def test_every_grammar_term_is_written_as_the_runtime_reads_it(self):
        self.table(terms=(("objective", "Boat", "notfailed"), ("objective", "Unseen", "cancelled"),
                          ("result", "MajorVictory"), ("rescued", 999), ("nolaunch",)), nations=("China",))
        written = awards.runtime_mission_awards("sest-red-line", self.mission())
        specs, error = parse_specs(["|".join(written)])
        self.assertIsNone(error)
        self.assertEqual(specs[0].nations, ["China"])
        self.assertEqual([t.text for t in specs[0].terms],
                         ["objective:Boat=notfailed", "objective:Unseen=cancelled", "result>=MajorVictory",
                          "rescued>=999", "nolaunch"])

    def test_bad_data_stops_the_build(self):
        for terms, message in (((("objective", "Pilot", "completed"),), "no objective 'Pilot'"),
                               ((("objective", "passage", "completed"),), "no objective 'passage'"),
                               ((("objective", "Passage", "done"),), "not 'done'"),
                               ((("result", "Win"),), "not a runtime award condition"),
                               ((("rescued", 0),), "not a runtime award condition"),
                               ((("rescued", 1000),), "not a runtime award condition"),
                               ((("rescued", True),), "not a runtime award condition"),
                               ((("nofire",),), "not a runtime award condition"),
                               ((), "needs a condition")):
            with self.subTest(terms=terms):
                self.table(terms=terms)
                with self.assertRaisesRegex(ValueError, re.escape(message)):
                    awards.runtime_mission_awards("sest-red-line", self.mission())
        self.table(nations=("US",))
        with self.assertRaisesRegex(ValueError, "not a nation the campaign offers"):
            awards.runtime_mission_awards("sest-red-line", self.mission())
        self.table(id="sest_undersea_operations")
        with self.assertRaisesRegex(ValueError, "is a native award"):
            awards.runtime_mission_awards("sest-red-line", self.mission())
        self.table(id="Sest Test")
        with self.assertRaisesRegex(ValueError, "not a runtime ribbon"):
            awards.runtime_mission_awards("sest-red-line", self.mission())
        awards.RUNTIME = {"sest-red-line": {"RL05": (dict(id="a", terms=(("nolaunch",),)),),
                                            "RLC1": (dict(id="a", terms=(("nolaunch",),)),)}}
        with self.assertRaisesRegex(ValueError, "granted twice"):
            awards.runtime_grants("sest-red-line")
        awards.RUNTIME = {"sest-red-line": {"RL99": (dict(id="a", terms=(("nolaunch",),)),)}}
        with self.assertRaisesRegex(ValueError, "no mission table entry"):
            awards.runtime_grants("sest-red-line")

    def test_a_value_the_ini_reader_would_cut_stops_the_build(self):
        self.table(terms=(("objective", "Pass;age", "completed"),))
        objectives = [("Pass;age",)]
        with self.assertRaisesRegex(ValueError, "would not reach the runtime whole"):
            awards.runtime_mission_awards("sest-red-line", self.mission(objectives=objectives))
        for oid in ("Pass#age", "Pass//age"):
            self.table(terms=(("objective", oid, "completed"),))
            with self.assertRaisesRegex(ValueError, "would not reach the runtime whole"):
                awards.runtime_mission_awards("sest-red-line", self.mission(objectives=[(oid,)]))

    def test_runtime_ribbons_are_defined_but_never_listed(self):
        from_source = awards.commander_settings("[CommanderSettings]\nCommanderNations=China\n", "sest-red-line")
        listed = section(from_source, "TaskForceRibbons")["RibbonIds"].split("|")
        for rid in awards.runtime_grants("sest-red-line"):
            self.assertIn(f"[Ribbon_{rid}]", from_source)
            self.assertNotIn(rid, listed)
        self.assertEqual(listed, ["sest_red_line_service", "sest_contact_intelligence", "sest_undersea_operations"])
        self.assertEqual(from_source, awards.commander_settings(from_source, "sest-red-line"))
        with self.assertRaisesRegex(ValueError, "RibbonIds lists the runtime ribbon sest_silent_passage"):
            awards.commander_settings("[TaskForceRibbons]\nRibbonIds=sest_silent_passage\n", "sest-red-line")

    def test_runtime_citations_say_only_what_the_runtime_checks(self):
        rows = awards.catalogue("sest-red-line")
        passage, recovery = rows["sest_silent_passage"], rows["sest_personnel_recovery"]
        self.assertTrue(passage["runtime"] and recovery["runtime"])
        self.assertIn("without launching a weapon", passage["citation"])
        self.assertIn("Under the Convergence", passage["citation"])
        # The game counts anyone the task force lifts from a raft.
        self.assertIn("survivors recovered", recovery["citation"])
        named = recovery["citation"].replace("Pilot in the Water", "")
        for word in ("pilot", "Flying Shark", "J-15", "his ", "airman"):
            self.assertNotIn(word.lower(), named.lower())
        for row in (passage, recovery):
            self.assertEqual((row["type"], row["reference"], row["recipient"], row["precedence"]),
                             ("CampaignAward", "Fictional", "commander", 125))
            self.assertTrue(row["citation"].endswith(". " + awards.FICTIONAL))


class BuiltRuntimeAwards(unittest.TestCase):
    """Every SestRuntimeRibbonAwards value build_pack.py wrote, parsed with
    the port, against the campaign it ships in."""

    @classmethod
    def setUpClass(cls):
        cls.campaigns, cls.found = {}, {}
        for slug in awards.CAMPAIGNS:
            folder = PACK / "campaigns" / slug
            text = (folder / "campaign.ini").read_text(encoding="utf-8")
            commander = (folder / "commander_settings.ini").read_text(encoding="utf-8")
            sections = list(re.finditer(r"(?ms)^\[([^\]\n]+)\]([^\n]*)\n(.*?)(?=^\[|\Z)", text))
            missions = {}
            for m in sections:
                if re.fullmatch(r"Mission\d+", m[1]):
                    comment = re.match(r"\s*#(\S+) ?(.*)$", m[2])
                    missions[m[1]] = dict(code=comment[1] if comment else "",
                                          title=comment[2].strip() if comment else "", body=m[3])
            cls.campaigns[slug] = dict(folder=folder, text=text, commander=commander, missions=missions,
                                       sections=sections)
            for name, mission in missions.items():
                lines = re.findall(r"^[ \t]*" + KEY + r"[ \t]*=.*$", mission["body"], re.M)
                if lines:
                    cls.found[(slug, name, mission["code"])] = lines

    def native_ids(self, slug):
        """Every id the game itself grants in this campaign (its parse:
        '|' between specs, ',' before nations, the id cut before ':')."""
        out = set()
        for mission in self.campaigns[slug]["missions"].values():
            m = re.search(r"^TaskForceModeRibbonAwards=(.*)$", mission["body"], re.M)
            for spec in (m[1].split("|") if m else []):
                if spec.strip():
                    out.add(spec.split(",")[0].split(":")[0].strip())
        return out

    def parsed(self, slug, name, lines):
        self.assertEqual(len(lines), 1, f"{slug} [{name}]: one {KEY} line")
        value = lines[0].split("=", 1)[1]
        for mark in (";", "#", "//"):
            self.assertNotIn(mark, value, f"{slug} [{name}]: IniHandler would cut the value at {mark!r}")
        specs, error = parse_specs([as_read(lines[0]).strip()])
        self.assertIsNone(error, f"{slug} [{name}]")
        return specs

    def test_the_key_is_written_only_where_the_owner_decided(self):
        got = {where: [(s.ribbon_id, s.nations, [t.text for t in s.terms]) for s in self.parsed(*where[:2], lines)]
               for where, lines in self.found.items()}
        self.assertEqual(got, EXPECTED)
        for slug, campaign in self.campaigns.items():
            # Only a [Mission<N>] section carries the key.
            for m in campaign["sections"]:
                if not re.fullmatch(r"Mission\d+", m[1]):
                    self.assertNotIn(KEY, m[3], f"{slug} [{m[1]}]")
            emitted = {s.ribbon_id for (s_slug, name, _c), lines in self.found.items() if s_slug == slug
                       for s in self.parsed(slug, name, lines)}
            self.assertEqual(emitted, set(awards.runtime_grants(slug)), slug)

    def test_each_runtime_ribbon_is_defined_unlisted_and_not_native(self):
        for (slug, name, code), lines in self.found.items():
            campaign = self.campaigns[slug]
            commander = campaign["commander"]
            listed = section(commander, "TaskForceRibbons")["RibbonIds"].split("|")
            offered = section(commander, "CommanderSettings")["CommanderNations"].split("|")
            native = self.native_ids(slug)
            for spec_ in self.parsed(slug, name, lines):
                rid = spec_.ribbon_id
                with self.subTest(campaign=slug, award=rid):
                    self.assertRegex(rid, r"^[a-z0-9_]+$")
                    row = section(commander, "Ribbon_" + rid)
                    self.assertTrue(row, "no [Ribbon_] definition: the runtime would log 'not awarded'")
                    self.assertNotIn(rid, listed, "listed in RibbonIds: the developer grant would hand it out")
                    self.assertNotIn(rid, native, "the game grants it already")
                    for nation in spec_.nations:
                        self.assertIn(nation, offered)
                    self.assertEqual(row["Name_en"], awards.catalogue(slug)[rid]["name"])
                    self.assertEqual(row["ReferenceSource"], "Fictional")
                    self.assertTrue((PACK / row["ImagePath"]).is_file(), row["ImagePath"])

    def test_objectives_are_the_missions_own(self):
        for (slug, name, code), lines in self.found.items():
            mission = self.campaigns[slug]["missions"][name]
            path = re.search(r"^MissionFile=(.*)$", mission["body"], re.M)[1].strip()
            text = (PACK / path).read_text(encoding="utf-8", errors="replace")
            side = re.search(r"^PlayerTaskforce=(\w+)", text, re.M)[1]
            objectives = list(section(text, side + "_Objectives"))
            self.assertTrue(objectives, path)
            for spec_ in self.parsed(slug, name, lines):
                for term in spec_.terms:
                    if term.kind == "objective":
                        # The runtime matches ignoring case; the data is
                        # held to the mission's own spelling.
                        self.assertIn(term.id, objectives, f"{slug} {code} {spec_.ribbon_id}")
                    if term.kind == "result":
                        required = re.search(r"^RequiredResult=(\w+)", mission["body"], re.M)[1]
                        self.assertGreater(term.number, RESULTS.index(required),
                                           "the native gate already requires this result")

    def test_citations_name_the_mission_and_its_date(self):
        for (slug, name, code), lines in self.found.items():
            mission = self.campaigns[slug]["missions"][name]
            self.assertEqual(mission["code"], code)
            path = re.search(r"^MissionFile=(.*)$", mission["body"], re.M)[1].strip()
            y, mo, d = (int(x) for x in re.search(r"^Date=(\d+),(\d+),(\d+)", (PACK / path).read_text(
                encoding="utf-8", errors="replace"), re.M).groups())
            when = date(y, mo, d)
            title, table_date, _context = awards.MISSIONS[slug][code]
            self.assertEqual((mission["title"], tuple(table_date)), (title, (y, mo, d)))
            for spec_ in self.parsed(slug, name, lines):
                row = section(self.campaigns[slug]["commander"], "Ribbon_" + spec_.ribbon_id)
                with self.subTest(campaign=slug, award=spec_.ribbon_id):
                    text = row["CitationText_en"]
                    self.assertIn(title, text)
                    self.assertEqual(row["CitationDate_en"], f"{when.day} {when.strftime('%B')} {when.year}")
                    self.assertTrue(text.endswith(". " + awards.FICTIONAL), text)
                    first = text[:-len(awards.FICTIONAL) - 1]
                    self.assertTrue(first.startswith("For ") and first.endswith("."), first)
                    self.assertEqual(first.count(". "), 0, first)

    def test_rl05_keeps_its_completion_ribbon_beside_the_stricter_one(self):
        body = self.campaigns["sest-red-line"]["missions"]["Mission15"]["body"]
        self.assertRegex(body, r"(?m)^TaskForceModeRibbonAwards=sest_undersea_operations$")
        self.assertRegex(body, r"(?m)^RequiredResult=CostlyVictory$")
        self.assertRegex(self.campaigns["sest-red-line"]["missions"]["Mission11"]["body"],
                         r"(?m)^RequiredResult=CostlyVictory$")

    def test_strips_are_drawn_listed_and_unlike_any_other(self):
        # No two fictional SEST ribbons alike, in any campaign: neither the
        # whole strip nor its centre colour.
        from PIL import Image
        centres, strips = {}, {}
        for slug, campaign in self.campaigns.items():
            commander = campaign["commander"]
            sources = (campaign["folder"] / "art/ribbons/SOURCES.txt").read_text(encoding="utf-8")
            for rid in re.findall(r"^\[Ribbon_(\w+)\]", commander, re.M):
                row = section(commander, "Ribbon_" + rid)
                if row["ReferenceSource"] != "Fictional":
                    continue
                strip = (row["StripeColors"], row["StripeWidths"])
                self.assertNotIn(strip, strips, f"{rid} is drawn as {strips.get(strip)}")
                strips[strip] = rid
                colours = row["StripeColors"].split("|")
                centre = colours[len(colours) // 2]
                self.assertNotIn(centre, centres, f"{rid} shares its centre with {centres.get(centre)}")
                centres[centre] = rid
            for rid in awards.runtime_grants(slug):
                row = awards.catalogue(slug)[rid]
                self.assertIn(f"  {rid}.png - {row['name']}: fictional SEST design", sources)
                with Image.open(campaign["folder"] / "art/ribbons" / (rid + ".png")) as image:
                    self.assertEqual(image.size, (140, 36), rid)
                    self.assertEqual(image.getpixel((70, 18))[:3],
                                     tuple(int(c, 16) for c in re.findall(r"..", centre_of(row)[1:])), rid)


def centre_of(row):
    return row["stripes"][len(row["stripes"]) // 2][0]


class RuntimeAwardDocs(unittest.TestCase):
    """RIBBONS.txt and the Red Line cards say the two ribbons need R13, what
    R13 will log, which checks run now, and the release notes name the tree
    whose manifest they count."""

    def test_ribbons_txt_says_r13_only(self):
        text = (ROOT / "integration/campaign/setup/RIBBONS.txt").read_text(encoding="utf-8")
        self.assertEqual((PACK / "RIBBONS.txt").read_bytes(),
                         (ROOT / "integration/campaign/setup/RIBBONS.txt").read_bytes())
        flat = " ".join(text.split())
        for phrase in ("RL05 Silent Passage", "RLC1 Personnel Recovery", "beta runtime R13 (Runtime 1.6.5)",
                       "R12 (Runtime 1.6.4) and the standard build never grant them", "MissionAwards=0"):
            self.assertTrue(phrase in flat, f"RIBBONS.txt does not say {phrase!r}")

    def test_the_red_line_cards_carry_the_pc_checks(self):
        card = " ".join((ROOT / "docs/campaigns/red-line/test-card.md").read_text(encoding="utf-8").split())
        guide = " ".join((ROOT / "docs/play-test-guide.md").read_text(encoding="utf-8").split())
        for rid in awards.runtime_grants("sest-red-line"):
            self.assertTrue(rid in card, f"the test card does not name {rid}")
        for name, text in (("test card", card), ("play-test guide", guide)):
            for phrase in ("Silent Passage", "Personnel Recovery", "R13"):
                self.assertTrue(phrase in text, f"the {name} does not say {phrase!r}")

    def test_the_cards_expect_as_many_log_lines_as_the_runtime_reads_values(self):
        # The game's EnumerateCampaignRuleSources (beta 499675cd
        # Seapower-Scripts.dll, <EnumerateCampaignRuleSources>d__33) yields
        # the open campaign ini, its #!alias files, then
        # OpenCampaignDefinitionIni([File] Base), and does not skip a file
        # it has already yielded. ReadValues (MissionAwards.cs:253-266) adds
        # one value per source, ParseSpecs (:329-348) keeps every spec, and
        # Evaluate logs one line per spec (:320); a repeat after an award
        # says "already awarded" (:306). Red Line names itself as its base.
        ini = PACK / "campaigns/sest-red-line/campaign.ini"
        text = ini.read_text(encoding="utf-8")
        self.assertNotIn("#!alias", text)
        base = section(text, "File").get("Base", "").strip()
        sources = [ini] + ([PACK / base] if base else [])
        lines = set()
        for (slug, name, _code), rows in EXPECTED.items():
            values = [as_read(KEY + "=" + v).strip() for src in sources
                      for v in [section(src.read_text(encoding="utf-8"), name).get(KEY, "")] if v.strip()]
            specs, error = parse_specs(values)
            self.assertIsNone(error, name)
            per_ribbon = {rid: [s.ribbon_id for s in specs].count(rid) for rid, _n, _t in rows}
            lines.update(per_ribbon.values())
        self.assertEqual(len(lines), 1, lines)
        count = {1: "one", 2: "two"}[lines.pop()]
        docs = {
            "test card": ROOT / "docs/campaigns/red-line/test-card.md",
            "play-test guide": ROOT / "docs/play-test-guide.md",
            "RIBBONS.txt": ROOT / "integration/campaign/setup/RIBBONS.txt",
        }
        for name, path in docs.items():
            flat = " ".join(path.read_text(encoding="utf-8").replace("`", "").split())
            with self.subTest(doc=name):
                said = re.compile(r"(\w+) (?:Player\.log )?lines? (?:for each|per) (?:runtime )?ribbon")
                self.assertEqual(set(said.findall(flat)), {count}, f"the {name} must expect {count} lines per ribbon")
                self.assertFalse("runtime ribbon's line in" in flat, name)
                if count == "two":
                    self.assertTrue("already awarded" in flat, f"the {name} does not say what the second line says")
                    self.assertTrue(re.search(r"\[File\] Base|its own base", flat),
                                    f"the {name} does not say why there are two lines")

    def test_r5_and_r6_are_run_now_and_r1_to_r4_wait_for_r13(self):
        # R5 is the game's own developer catalogue (ReadCampaignRibbonCatalog
        # reads only [TaskForceRibbons] RibbonIds), and R6 is R12's silence:
        # both run on this build. R1 to R4 need R13 to grant anything.
        def flat(path):
            return " ".join((ROOT / path).read_text(encoding="utf-8").split())
        card = flat("docs/campaigns/red-line/test-card.md")
        guide = flat("docs/play-test-guide.md")
        readme = flat("docs/releases/20261107/README-FIRST.txt")
        ribbons = flat("integration/campaign/setup/RIBBONS.txt")
        for name, text, phrase in (("test card", card, "R5 and R6 can be run now"),
                                   ("test card", card, "R1 to R4 need R13"),
                                   ("play-test guide", guide, "R1-R4 need beta runtime R13"),
                                   ("README-FIRST", readme, "R5 and R6; R1 to R4 need R13"),
                                   ("README-FIRST", readme, "Red Line step 4: checks R5 and R6"),
                                   ("RIBBONS.txt", ribbons, "checks R5 and R6"),
                                   ("RIBBONS.txt", ribbons, "(checks R1 to R4)")):
            self.assertTrue(phrase in text, f"the {name} does not say {phrase!r}")
        pc_checks = json.loads((ROOT / "docs/releases/20261107/validation.json").read_text(
            encoding="utf-8"))["red_line_runtime_awards"]["pc_checks"]
        self.assertTrue(pc_checks.startswith("docs/campaigns/red-line/test-card.md R5-R6 now, R1-R4 once R13"),
                        pc_checks)
        for name, text in (("test card", card), ("play-test guide", guide), ("README-FIRST", readme),
                           ("RIBBONS.txt", ribbons)):
            for stale in ("run R6 only", "R1 to R5", "R1-R5", "checks R1 to R6"):
                self.assertFalse(stale in text, f"the {name} still says {stale!r}")

    def test_the_release_notes_name_the_tree_whose_manifest_they_count(self):
        # The toolkit README-FIRST names is built from one branch; the file
        # count it promises must be that branch's, as validation.json
        # records it, and the manifest in this tree.
        release = ROOT / "docs/releases/20261107"
        manifest = json.loads((release / "upload-manifest.json").read_text(encoding="utf-8"))
        validation = json.loads((release / "validation.json").read_text(encoding="utf-8"))
        readme = " ".join((release / "README-FIRST.txt").read_text(encoding="utf-8").split())
        count = len(manifest["files"])
        self.assertEqual(manifest["file_count"], count)
        self.assertTrue(f"VERIFIED: all {count} canonical upload files match the release manifest." in readme,
                        f"README-FIRST step 1 does not promise the manifest's {count} files")
        branch = re.search(r"This toolkit's branch, ([\w./-]+)", readme)[1]
        self.assertEqual(validation["release_branch"].split()[0], branch)
        entries = [v for v in validation.values() if isinstance(v, dict) and v.get("branch") == branch]
        self.assertEqual(len(entries), 1, branch)
        self.assertIn(f": {count} files match the manifest", entries[0]["canonical_upload"])


if __name__ == "__main__":
    unittest.main()
