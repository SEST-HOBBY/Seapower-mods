#!/usr/bin/env python3
"""Build SEST Total Force 2026 - a twelve-mission linear campaign whose order
of battle is drawn from the whole collection.

WHY THIS EXISTS

128 Workshop subscriptions and 16 local packs are a lot of content to own and
never see. The Banda vignettes reached for the mods the sandbox left idle, one
family per scenario; this goes the rest of the way: a single campaign in which
EVERY active mod that can put something on the map does, and the ones that
cannot are named, with the reason, in docs/campaign-coverage.md.

"Incorporates all mods" is a claim about the load order, not about the folder
list, so it is computed the way the game resolves files. A mod is credited
only when the campaign places a unit that actually reads one of its files:

  unit      the mod's copy of <unit>.ini WINS the load order
  variant   it wins <unit>_variants.ini for a placed hull
  squadron  it wins <unit>_squadrons.ini for a placed airframe
  store     it wins an ammunition file the placed unit's chosen loadout hangs
  library   it wins no file any mission can name - systems, effects, UI or a
            bare _info.ini dependency marker - and applies install-wide
  shadowed  everything it ships is outranked; it cannot be reached at all

A mod placed in a mission but whose unit file is won by something else is
credited to the winner, never to the loser. That distinction is the whole
point: five mods here are invisible in game precisely because something above
them replaces their files, and the report says so instead of counting them.

WHY THE POSITIONS ARE HARVESTED, NOT INVENTED

Ships belong in water and land units on land, and nothing in this repo can
tell them apart from a coordinate. So every sea and land position is SNAPPED
to a position some already-loading mission put a unit of that kind on - the
repo's own missions plus the stock ones and the two stock campaigns, about
33,000 proven points. An anchor that lands on a coastline snaps to real water
a mile away; an anchor in the desert fails the build. Aircraft are airborne
and need no snapping.

Everything the game reads is derived here: hull variants, squadron references
and loadout names are resolved from the WINNING file at build time, so a mod
update that retires a variant fails this build rather than spawning a default
fit in mission seven.

Usage (repo root):
    python3 integration/campaign/build_pack.py              # build the pack
    python3 integration/campaign/build_pack.py --dry-run    # check only
"""
import argparse
import collections
import functools
import math
import pathlib
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration" / "missions"))
from refine_civ_traffic import load_order  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SEST_Campaign"
SLUG = "sest-southern-watch"
# The campaign's own name, and the only place it is spelled. It drives the
# mission file names, both mission-browser folders, the campaign card and the
# folder _info.ini files - so the pack's developer prefix does not leak into
# anything a player reads. `SLUG` stays as it is: it is a path, not a label.
TITLE = "Southern Watch"
DISPATCHES = "Southern Watch - Dispatches"
# The backdrop's second line. Not a name - the campaign's subject and
# its dates, both of which the twelve missions already agree on.
SUBTITLE = "The Northern Lifeline  ·  October - November 2028"
# Everything below this line is what a SECOND campaign in the same pack has to
# be able to change, and every value here is Southern Watch's own - so a
# campaign that sets none of them builds exactly what shipped before there
# was a second one. set_campaign() swaps the lot per campaign; the functions
# that read them are unchanged.
ART_PREFIX = "southern_watch"           # <prefix>_<code>_sheet.png
SERIES_LABEL = "SOUTHERN WATCH"         # the footer on cards and documents
MAP_SERIES = "SEST SOUTHERN WATCH"      # the briefing map's series line
GEOGRAPHY = "pool"                      # "pool": proven points; "coast": coastline
BROWSE = {}                             # series/group -> mission-browser folder
DOCS_DIR = ROOT / "docs" / "campaigns" / "southern-watch"
COVERAGE_DOC = ROOT / "docs" / "campaign-coverage.md"
CAMPAIGN_NAME_EN = None                 # None -> "<TITLE> (Royal Australian Navy)"
CAMPAIGN_DIFFICULTY = "3"               # [Campaign] Difficulty=
MAP_FOCUS_NM = None                     # briefing map: leave far bases off the chart
MAP_INSET = None                        # briefing map: the locator inset's box


def set_campaign(spec):
    """Point every campaign-scoped global at one campaign's data.

    `spec` is the dict a campaign module exports (see southern_reach/
    __init__.py and campaign_spec() below for Southern Watch's). Keys it does
    not set keep Southern Watch's values, which is why the first campaign's
    output did not move when the second arrived.

    Except the files a campaign WRITES outside its own pack folder. main()
    writes a coverage report and a required-mods list for every campaign, so
    a spec that fell back to Southern Watch's paths would overwrite Southern
    Watch's report with its own and nothing would say so. Only Southern
    Watch may leave them out, and no other campaign may name its paths.
    """
    if spec.get("SLUG") != _DEFAULTS["SLUG"]:
        who = spec.get("TITLE") or spec.get("SLUG") or "a campaign spec"
        for key in _OWN_FILES:
            if not spec.get(key):
                raise SystemExit(
                    f"{who}: the spec sets no {key}, and falling back would "
                    f"write over Southern Watch's {_DEFAULTS[key].relative_to(ROOT)}"
                    " - give the campaign its own")
            if Path(spec[key]).resolve() == _DEFAULTS[key].resolve():
                raise SystemExit(
                    f"{who}: {key} is Southern Watch's "
                    f"{_DEFAULTS[key].relative_to(ROOT)} - give the campaign its own")
    g = globals()
    for key in ("SLUG", "TITLE", "DISPATCHES", "SUBTITLE", "ART_PREFIX",
                "SERIES_LABEL", "MAP_SERIES", "GEOGRAPHY", "BROWSE",
                "DOCS_DIR", "COVERAGE_DOC", "CAMPAIGN_NAME_EN",
                "CAMPAIGN_DIFFICULTY", "MAP_FOCUS_NM", "MAP_INSET",
                "TASKFORCE", "DIFFICULTIES", "ROSTER"):
        # A key the spec leaves out goes back to Southern Watch's value - not
        # to whatever the previous campaign set. The first version of this
        # left the second campaign's map focus in place and redrew every
        # Southern Watch briefing map with the wrong inset.
        g[key] = spec.get(key, _DEFAULTS[key])
    g["CAMPAIGN_BLURB"] = spec["INFO_DESC"]


_DEFAULTS = {k: globals()[k] for k in (
    "SLUG", "TITLE", "DISPATCHES", "SUBTITLE", "ART_PREFIX", "SERIES_LABEL",
    "MAP_SERIES", "GEOGRAPHY", "BROWSE", "DOCS_DIR", "COVERAGE_DOC",
    "CAMPAIGN_NAME_EN", "CAMPAIGN_DIFFICULTY", "MAP_FOCUS_NM", "MAP_INSET")}
_DEFAULTS.update(TASKFORCE=None, DIFFICULTIES=None, ROSTER=None)
# What main() writes into docs/ for each campaign. See set_campaign().
_OWN_FILES = ("DOCS_DIR", "COVERAGE_DOC")


def campaign_specs():
    """The campaigns this pack ships, in the order they are built.

    Southern Watch is assembled from campaign_data's flat module globals;
    Southern Reach exports one dict, and so does Red Line when its package
    is in the tree. All come out the same shape.
    """
    sys.path.insert(0, str(HERE))
    import campaign_data as sw                      # noqa: E402
    import southern_reach as sr                     # noqa: E402
    watch = dict(
        SLUG="sest-southern-watch", TITLE="Southern Watch",
        DISPATCHES="Southern Watch - Dispatches",
        SUBTITLE="The Northern Lifeline  ·  October - November 2028",
        ART_PREFIX="southern_watch", SERIES_LABEL="SOUTHERN WATCH",
        MAP_SERIES="SEST SOUTHERN WATCH", GEOGRAPHY="pool", BROWSE={},
        DOCS_DIR=ROOT / "docs" / "campaigns" / "southern-watch",
        COVERAGE_DOC=ROOT / "docs" / "campaign-coverage.md",
        CAMPAIGN_NAME_EN=None, CAMPAIGN_DIFFICULTY="3",
        INFO_DESC=sw.INFO_DESC, DISPATCH_DESC=sw.DISPATCH_DESC,
        TASKFORCE=sw.TASKFORCE, DIFFICULTIES=sw.DIFFICULTIES,
        ROSTER=sw.ROSTER, COMMANDER=sw.COMMANDER, EVENTS=sw.EVENTS,
        MISSIONS=sw.MISSIONS, EXCUSES=sw.EXCUSES)
    specs = [watch, sr.CAMPAIGN]
    # Red Line is optional: a tree without its package builds the two
    # campaigns it always did. A package that is present and fails to import
    # is a broken campaign, not a missing one, so only the package's OWN
    # absence is caught. A folder left holding nothing but __pycache__ (a
    # checkout from before the package existed) imports as an empty namespace
    # package with no __file__, and counts as absent too.
    try:
        import red_line as rl                       # noqa: E402
    except ModuleNotFoundError as exc:
        if exc.name != "red_line":
            raise
    else:
        if getattr(rl, "__file__", None):
            specs.append(rl.CAMPAIGN)
    # Two campaigns sharing a pack folder or a report overwrite each other in
    # build order, silently. Southern Watch's own paths are set_campaign()'s
    # to guard; this is every other pair.
    for key in ("SLUG",) + _OWN_FILES:
        seen = {}
        for spec in specs:
            if not spec.get(key):
                continue
            value = spec[key] if key == "SLUG" else Path(spec[key]).resolve()
            if value in seen:
                raise SystemExit(f"{seen[value]} and {spec.get('TITLE')} both "
                                 f"set {key}={spec[key]} - each campaign needs its own")
            seen[value] = spec.get("TITLE")
    return specs


def pack_excuses(specs):
    """Every campaign's EXCUSES in one table. The coverage rule is the pack's
    - every enabled mod placed by SOME campaign or excused in writing - so an
    excuse any campaign gives counts for all of them."""
    out = {}
    for spec in specs:
        out.update(spec.get("EXCUSES", {}))
    return out
# The nine languages the game ships (one language_<xx> folder each in the
# vanilla export). Localised keys have NO fallback: pacific-strike's Mission1
# repeats the SAME English PNG under TileImagePath_en, _ru AND _de rather than
# letting _en cover the others, and every localised campaign block spells its
# own MissionImage_/AssetsPath_/FilePath_. A key written only as _en is
# therefore a key a German or Japanese player does not get - no mission card,
# no story page, no campaign tile at all.
#
# The ART is genuinely shared, so it is mirrored. The TEXT is English in every
# block, because it has not been translated and machine-translating a
# campaign's prose would be inventing content and calling it a translation.
# Native ships partially-localised campaigns the same way: the Russian block of
# `missions/Campaign Scenarios/Pacific Strike/_info.ini` carries an English
# Name beside a translated Description.
LANGS = ("en", "cn", "de", "es", "fr", "ja", "ko", "ru", "vn")
MODS = ROOT / "mods-source"
UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units", "biologic")

# Families the mission format counts separately. (side, kind) -> section stem.
FAMILY = {
    ("blue", "vessel"): "Taskforce1Vessel",
    ("blue", "sub"): "Taskforce1Submarine",
    ("blue", "air"): "Taskforce1Aircraft",
    ("blue", "heli"): "Taskforce1Helicopter",
    ("blue", "land"): "Taskforce1LandUnit",
    ("red", "vessel"): "Taskforce2Vessel",
    ("red", "sub"): "Taskforce2Submarine",
    ("red", "air"): "Taskforce2Aircraft",
    ("red", "heli"): "Taskforce2Helicopter",
    ("red", "land"): "Taskforce2LandUnit",
    ("neutral", "vessel"): "NeutralVessel",
    ("neutral", "sub"): "NeutralSubmarine",
    ("neutral", "air"): "NeutralAircraft",
    ("neutral", "heli"): "NeutralHelicopter",
    ("neutral", "land"): "NeutralLandUnit",
    ("neutral", "bio"): "NeutralBiologic",
}
# Order matters: the [Mission] header declares counts in this order, and the
# blocks are written in it, so a mission's file is stable across rebuilds.
COUNT_KEY = {
    "Taskforce1Vessel": "NumberOfTaskforce1Vessels",
    "Taskforce2Vessel": "NumberOfTaskforce2Vessels",
    "NeutralVessel": "NumberOfNeutralVessels",
    "Taskforce1Submarine": "NumberOfTaskforce1Submarines",
    "Taskforce2Submarine": "NumberOfTaskforce2Submarines",
    "NeutralSubmarine": "NumberOfNeutralSubmarines",
    "Taskforce1Aircraft": "NumberOfTaskforce1Aircraft",
    "Taskforce2Aircraft": "NumberOfTaskforce2Aircraft",
    "NeutralAircraft": "NumberOfNeutralAircraft",
    # Helicopters are their own family. Every helicopter placement in the
    # stock and workshop missions (60; 97 with the user-folder copies) sits in
    # a [TaskforceNHelicopterM] or [NeutralHelicopterM] section counted by
    # NumberOf...Helicopters - the
    # format guide lists the family separately, stock names them with
    # Taskforce1Helicopter1NameOverride, and its conditions test
    # Condition_UnitType=Helicopter apart from Aircraft. This builder used to
    # file every helicopter as Aircraft; the first one flown from an authored
    # section (O1's Seahawk) showed the wrong flag and sat doing nothing.
    "Taskforce1Helicopter": "NumberOfTaskforce1Helicopters",
    "Taskforce2Helicopter": "NumberOfTaskforce2Helicopters",
    "NeutralHelicopter": "NumberOfNeutralHelicopters",
    "Taskforce1LandUnit": "NumberOfTaskforce1LandUnits",
    "Taskforce2LandUnit": "NumberOfTaskforce2LandUnits",
    "NeutralLandUnit": "NumberOfNeutralLandUnits",
    "NeutralBiologic": "NumberOfNeutralBiologics",
}
FAMILY_ORDER = list(COUNT_KEY)


# --- the load order, as the game resolves it ---------------------------------

def providers():
    """(token, directory) highest priority first - the game's search order.

    The one SEST token in the canonical order is the consolidated pack, which
    only exists after every other builder has run; resolving through it would
    make this builder depend on its own downstream stage and break a
    --from-scratch build outright. The per-pack sources it is merged from are
    byte-identical by construction (tools/consolidate_packs.py fails the build
    on any disagreement), so they stand in for it here - and they name the
    pack that actually contributed each file, which the consolidated folder
    cannot.
    """
    out = []
    order = load_order()
    for token in order:
        if token.startswith("SEST_"):
            for pack in sorted((ROOT / "integration").glob("*/SEST_*")):
                if pack.parent.name != "dist":
                    out.append((pack.name, pack))
        elif (MODS / token).is_dir():
            out.append((token, MODS / token))
    # Deliberately NOT falling back to exported folders that are absent from
    # the canonical order. refine_civ_traffic.winning_file does fall back, which
    # is right for diagnostics and wrong here: a campaign that resolves a unit
    # through a mod the Mod Manager does not load is a campaign that breaks on
    # the machine it ships to, and a coverage report that credits it is telling
    # a comfortable lie. If a required mod is unsubscribed, this resolver fails
    # and names the unit.
    out.append(("_vanilla", MODS / "_vanilla" / "original"))
    return out


_INDEX = None


def index():
    """Lowercased relative path -> (token, path), resolved once.

    Only paths the game can name are listed: a unit file two directories deep
    (mods-source/3594891803/'PLAN mod test'/vessels/...) is unreachable, so
    crediting it would inflate the coverage report with content that cannot
    load. Keys are lowercased because the game runs on a case-insensitive
    filesystem and resolves them that way.
    """
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for token, base in providers():
            # Sorted, because this is a FIRST-WINS index and a mod can ship two
            # files whose names differ only in case - check_load_order names
            # Shahed_136_white.ini and shahed_136_white.ini. Windows sees one
            # file there and Linux sees two, so an unsorted walk lets the two
            # platforms disagree about which one won.
            for f in sorted(base.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(base).as_posix().lower()
                if rel.split("/")[0] in UNIT_DIRS and rel.count("/") != 1:
                    continue
                _INDEX.setdefault(rel, (token, f))
    return _INDEX


def owner(relpath):
    hit = index().get(relpath.lower())
    return hit[0] if hit else None


def winning(relpath):
    hit = index().get(relpath.lower())
    return hit[1] if hit else None


def unit_file(uid):
    for kind in UNIT_DIRS:
        f = winning(f"{kind}/{uid}.ini")
        if f:
            return kind, f
    return None, None


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def ini_text(value):
    """Mission INI text: paragraph breaks are the two-character escape \\n.

    A real newline inside Description= or a message ends the key and leaves
    bare continuation lines the parser has no home for. Two of the missions
    were authored with real newlines and emitted exactly that, so this is
    applied centrally rather than trusted to whoever writes the next brief.
    """
    return value.replace("\r\n", "\n").replace("\n", "\\n")


def unit_value(uid, key, depth=0):
    """A top-level key of the winning file, following #!alias like unit_type.

    None when the file does not say. Callers must not read None as False:
    a deck with no AircraftSupported list and an airframe with no
    CarrierCapable line are UNDECLARED, and the build reports them as such
    rather than deciding for the mod author either way.
    """
    _kind, f = unit_file(uid)
    if f is None or depth > 4:
        return None
    text = read(f)
    m = re.search(r"^\s*" + re.escape(key) + r"=([^\n/]*)", text, re.M)
    if m:
        return m.group(1).strip()
    a = re.search(r"#!alias\s+(\S+)", text)
    if a:
        return unit_value(Path(a.group(1)).stem, key, depth + 1)
    return None


def unit_spot(keys):
    bits = keys.get("RelativePositionInNM", "").split(",")
    try:
        return float(bits[0]), float(bits[2])
    except (ValueError, IndexError):
        return None


def deck_fit(atype, kind, deck_type, is_ship):
    """Can this airframe recover on that deck, by the two files' own words.

    0 = compatible: a field; a ship whose AircraftSupported names the type;
        or a ship with no list and an airframe that says CarrierCapable=True.
    1 = undeclared: a ship with no list and a fixed-wing airframe with no
        CarrierCapable line. Allowed, reported, and listed on the test card.
    None = incompatible: CarrierCapable=False, or a ship whose list leaves
        the type out. A helicopter on an unlisted escort deck is 0 - vanilla
        escorts declare a capacity and, mostly, no list.
    """
    if not is_ship:
        return 0
    cc = unit_value(atype, "CarrierCapable")
    if cc == "False":
        return None
    listed = unit_value(deck_type, "AircraftSupported")
    if listed:
        names = {x.strip() for x in listed.split(",") if x.strip()}
        return 0 if atype in names else None
    if cc == "True" or kind == "Helicopter":
        return 0
    return 1


RECOVERY_NOTES = []


def unit_type(uid, depth=0):
    """UnitType of the winning file, following #!alias like the game does."""
    kind, f = unit_file(uid)
    if f is None or depth > 4:
        return None
    text = read(f)
    m = re.search(r"^\s*UnitType=(\S+)", text, re.M)
    if m:
        return m.group(1)
    a = re.search(r"#!alias\s+(\S+)", text)
    if a:
        return unit_type(Path(a.group(1)).stem, depth + 1)
    return None


# --- proven positions --------------------------------------------------------

POOL_ROOTS = ("integration/missions",
              "mods-source/_vanilla/original/missions",
              "mods-source/_vanilla/original/campaigns",
              "mods-source/_vanilla/user/missions")


def pool_kind(section):
    if "Submarine" in section:
        return "sea"          # a submarine's position is water like any other
    if "LandUnit" in section:
        return "land"
    if "Vessel" in section or "Biologic" in section:
        return "sea"
    return None               # aircraft need no proven ground


def harvest():
    """Every (lat, lon) a loading mission has already put a unit of that kind on.

    lat = centre + z/60, lon = centre + x/60: RelativePositionInNM is plain
    arcminutes on both axes. Checked against the two RAAF bases NORTHERN
    FRONT II places - Darwin resolves to -12.427,130.884 and Scherger to
    -12.603,142.040, both within a mile of the real airfields.
    """
    pool = {"sea": [], "land": []}
    for rel in POOL_ROOTS:
        for f in sorted((ROOT / rel).rglob("*.ini")):
            if OUT in f.parents:
                continue      # never feed this campaign's own output back in
            text = read(f)
            la = re.search(r"^MapCenterLatitude=(-?[\d.]+)", text, re.M)
            lo = re.search(r"^MapCenterLongitude=(-?[\d.]+)", text, re.M)
            if not (la and lo):
                continue
            clat, clon = float(la.group(1)), float(lo.group(1))
            section = None
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("[") and s.endswith("]"):
                    section = s[1:-1]
                    continue
                m = re.match(r"RelativePositionInNM=(-?[\d.]+),([^,]*),(-?[\d.]+)\s*$", s)
                if not (m and section):
                    continue
                kind = pool_kind(section)
                if kind:
                    pool[kind].append((clat + float(m.group(3)) / 60.0,
                                       clon + float(m.group(1)) / 60.0))
    for kind in pool:
        pool[kind] = sorted(set((round(a, 4), round(b, 4)) for a, b in pool[kind]))
    return pool


# Civil air traffic: a Mach 0.8 airliner at cruise altitude makes about 470
# knots (civ_a330 SpeedAndRange_Cruise=0.82, civ_a320 0.78). An airway's one
# waypoint goes this many times further than that covers in the mission's
# clock, so no airliner ever arrives, turns and orbits.
CIVIL_CRUISE_KN = 470
AIRWAY_MARGIN = 1.5


def civil_reach_nm(mission):
    return CIVIL_CRUISE_KN * mission.get("minutes", 60) / 60.0


def nm_between(a, b):
    dlat = (a[0] - b[0]) * 60.0
    dlon = (a[1] - b[1]) * 60.0 * math.cos(math.radians((a[0] + b[0]) / 2.0))
    return math.hypot(dlat, dlon)


# How far an OFFSHORE station may be moved to reach proven water before the
# build refuses. 8 NM is inside any escort's sensor horizon and a tenth of a
# 50-minute mission's steaming; 43 NM - what SW12 was getting - is neither.
OFFSHORE_SNAP = 8.0
# How far from every harvested LAND point a station has to be before its
# authored position is trusted as open water without a proven sea point.
OPEN_SEA = 25.0
UNPROVEN = []
PLACEMENT_PROBLEMS = []


# The proof a coastline gives instead of a pool. Where no loading mission has
# ever put a ship - Storm Bay, Cook Strait, the Macquarie Ridge - the position
# is checked against the committed Natural Earth extract (coast.py): a land
# unit must be ashore, a ship must be at sea, an offshore station must have
# OFFSHORE_MIN of water around it, and a route's waypoints must not cross a
# headland. It is a different proof, and the coverage report says which one
# each station got.
OFFSHORE_MIN = 2.0
COAST_CHECKED = []


def coast_data():
    from coast import coast
    return coast()


class CoastPlacer:
    """Stands in for Snapper on a mission whose geography is "coast".

    Same take() signature, so place() does not care which it was handed;
    positions are used as authored and refused if the coastline disagrees.
    Hulls sharing a coastal station are spread 0.4 NM abeam, the way the pool
    placer's distinct points spread them, so two ships never spawn on one
    coordinate.
    """

    def __init__(self, coast, mission):
        self.coast, self.mission = coast, mission
        self.used, self.pool = set(), {"sea": [], "land": []}
        self.berths = collections.Counter()

    def _cover(self, at, where):
        if not self.coast.covers(*at):
            PLACEMENT_PROBLEMS.append(
                f"{where}: {at} is outside the coastline extract's box "
                f"{self.coast.box} - extend it with tools/make_coast_extract.py")
            return False
        return True

    def take(self, kind, at, exclude_nm=0.4, limit=None, where=""):
        lat, lon = at
        if kind == "sea":
            n = self.berths[where]
            self.berths[where] += 1
            st = self.mission["stations"].get(where.split(" ", 1)[-1], {})
            side = (n + 1) // 2 * (1 if n % 2 else -1)
            beam = math.radians(st.get("heading", 90) + 90)
            lat = at[0] + side * 0.4 * math.cos(beam) / 60.0
            lon = at[1] + side * 0.4 * math.sin(beam) / (60.0 * math.cos(math.radians(at[0])))
        if self._cover((lat, lon), where):
            land, nm = self.coast.check(lat, lon)
            if kind == "land" and not land:
                PLACEMENT_PROBLEMS.append(
                    f"{where}: a land unit at {at} is at sea ({nm:.1f} NM from the "
                    "nearest coast). Put it on the field's real coordinates")
            elif kind == "sea" and land:
                PLACEMENT_PROBLEMS.append(
                    f"{where}: a sea position at {at} is ashore ({nm:.1f} NM "
                    "inside the coast)")
            else:
                COAST_CHECKED.append((where, (lat, lon),
                                      "ashore" if land else f"{nm:.1f} NM off"))
        return (round(lat, 4), round(lon, 4)), 0.0

    def offshore(self, at, where):
        if self._cover(at, where):
            land, nm = self.coast.check(*at)
            if land or nm < OFFSHORE_MIN:
                PLACEMENT_PROBLEMS.append(
                    f"{where}: station at {at} is "
                    f"{'ashore' if land else f'{nm:.1f} NM off the coast'} - an "
                    f"offshore station needs {OFFSHORE_MIN:.0f} NM of water "
                    "(mark it coastal=True for a port or an anchorage)")
            else:
                COAST_CHECKED.append((where, at, f"{nm:.0f} NM off"))
        return (round(at[0], 4), round(at[1], 4)), 0.0

    def waypoint(self, at, where):
        if self._cover(at, where):
            land, nm = self.coast.check(*at)
            if land or nm < 0.5:
                PLACEMENT_PROBLEMS.append(
                    f"{where}: waypoint {at} is "
                    f"{'ashore' if land else 'in the surf'} ({nm:.1f} NM from the "
                    "coast) - route the track round the headland")

    def point(self, at, where, least=1.0):
        """An authored point a trigger uses - a box centre, a stage area."""
        if self._cover(at, where):
            land, nm = self.coast.check(*at)
            if land or nm < least:
                PLACEMENT_PROBLEMS.append(
                    f"{where}: {at} is {'ashore' if land else f'{nm:.1f} NM off the coast'} "
                    "- a trigger area's centre belongs on water")


def open_water(snapper, at, where):
    """Where an offshore station actually goes.

    The proven-position pool is every spot a loading mission ever put a unit
    on. Ashore that is a real test - an airbase is where the airbase is. At
    sea it is a list of where other people's ships once happened to be, and
    the open Arafura is nearly empty of them, so "snap to proven water" moved
    stations by tens of miles to prove a thing the chart already says.

    Three cases, in order:
      1. Further than OPEN_SEA from every harvested land point: the authored
         point is used exactly. It is open ocean; the designer put a ship on
         it; the encounter is what they drew. Recorded as unproven so the
         coverage report can list it.
      2. Within OFFSHORE_SNAP of a proven sea point: snapped to it. Near a
         coast, a proof is worth 8 NM.
      3. Neither: refused, with the numbers. Move the station, or mark it
         coastal=True and take the per-unit snap that a port or a rig gets.
    """
    if isinstance(snapper, CoastPlacer):
        return snapper.offshore(at, where)
    land = min((nm_between(p, at) for p in snapper.pool["land"]), default=1e9)
    sea_p, sea_d = None, 1e9
    for p in snapper.pool["sea"]:
        if p in snapper.used:
            continue
        d = nm_between(p, at)
        if d < sea_d:
            sea_p, sea_d = p, d
    if land > OPEN_SEA:
        UNPROVEN.append((where, at, land))
        return (round(at[0], 4), round(at[1], 4)), 0.0
    if sea_p is not None and sea_d <= OFFSHORE_SNAP:
        snapper.used.add(sea_p)
        return sea_p, sea_d
    # Collected, not raised: the build should name EVERY station that needs a
    # decision in one run, not the first one and then the next after a fix.
    PLACEMENT_PROBLEMS.append(
        f"{where}: station at {at} is {land:.0f} NM from the nearest known "
        f"land and {sea_d:.0f} NM from the nearest proven water - too close "
        "to a coast to trust and too far from proof to snap. Move it, or "
        "mark the station coastal=True to take a per-unit snap.")
    return (round(at[0], 4), round(at[1], 4)), 0.0


class Snapper:
    """Hands out proven points near an anchor, never the same one twice.

    Two ships on one coordinate is a collision the game resolves by shoving
    them apart, so used points are retired as they are handed out.
    """

    def __init__(self, pool, limit_nm=60.0):
        self.pool = pool
        self.limit = limit_nm
        self.used = set()

    def take(self, kind, anchor, exclude_nm=0.4, limit=None, where=""):
        limit = self.limit if limit is None else limit
        best, best_d = None, None
        for p in self.pool[kind]:
            if p in self.used:
                continue
            d = nm_between(p, anchor)
            if best_d is None or d < best_d:
                best, best_d = p, d
        if best is None or best_d > limit:
            raise SystemExit(
                f"{where}: no proven {kind} position within {limit:.0f} NM of "
                f"{anchor} - nearest is {best_d and round(best_d)} NM away. "
                "Move the station onto water/ground some mission already "
                "uses, or mark it coastal=True if a large move is the truth "
                "of the place (a port, a rig, a beacon).")
        self.used.add(best)
        return best, best_d


# --- what the game reads for one placed unit ---------------------------------

KIND_OF = {"Vessel": "vessel", "Submarine": "sub", "Aircraft": "air",
           "Helicopter": "heli", "VTOL": "air", "LandUnit": "land",
           "Biologic": "bio"}


def variants(uid, kind):
    """Usable [VariantN] names from the WINNING variants file, or []."""
    f = winning(f"{kind}/{uid}_variants.ini")
    if f is None:
        return []
    body = read(f)
    names, seen = [], set()
    for n in re.findall(r"^\[(Variant\d+)\]", body, re.M):
        if n not in seen:
            seen.add(n)
            names.append(n)
    declared = re.search(r"^NumberOfVariants=(\d+)", body, re.M)
    if declared:
        names = names[:min(len(names), int(declared.group(1)))]
    return names


def squadrons(uid):
    f = winning(f"aircraft/{uid}_squadrons.ini")
    if f is None:
        return []
    return re.findall(r"^\[(Squadron\d+)\]", read(f), re.M)


def alias_target(path):
    """The file a `#!alias` unit file inherits from, or None.

    65 unit files in this mod set are aliases - `jp_f-2a_late.ini` is
    `#!alias aircraft/jp_f-2a.ini` carrying only its own weapon systems.
    Anything that reads a unit's properties has to follow that the way
    unit_type() already does, or an aliased hull looks like it declares
    nothing at all.
    """
    m = re.search(r"#!alias\s+(\S+)", read(path))
    return winning(m.group(1)) if m else None


def loadouts(path, depth=0):
    m = re.search(r"^AvailableLoadouts=(.+)$", read(path), re.M)
    if m:
        return [x.strip() for x in m.group(1).split(",") if x.strip()]
    base = alias_target(path) if depth < 4 else None
    return loadouts(base, depth + 1) if base else []


def pick_loadout(uid, path, want):
    """The loadout to write, and why. Never invents a name the file lacks."""
    offered = loadouts(path)
    if not offered:
        return None, "file offers none"
    if want:
        if want not in offered:
            raise SystemExit(f"{uid}: loadout {want!r} is not offered by the "
                             f"winning file (offers: {', '.join(offered)})")
        return want, "declared"
    if "Default" in offered:
        return "Default", "default"
    return offered[0], "first offered"


def stores(uid, kind, path, loadout):
    """Ammunition ids the placed unit hangs with this loadout.

    Sections are either bare (WeaponSystem3, WeaponMagazineVLS_1 - loaded
    whatever the fit) or suffixed with a loadout name (WeaponSystem1Malice424),
    which is how the aircraft files carry one pylon map per fit. Only the
    chosen fit's sections count, so the report credits the stores the mission
    actually flies with rather than every round the airframe can carry.
    """
    text = read(path)
    out, section = set(), ""
    known = set(loadouts(path))
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1]
            continue
        if not section.startswith(("WeaponSystem", "WeaponMagazine")):
            continue
        # Longest-first, because one offered fit's name can be a suffix of
        # another's. And a section that clearly carries a fit name which this
        # unit does NOT offer is skipped rather than treated as bare: the
        # df-26b offers AntiShip/Strike/NukeStrike and still ships a
        # [WeaponSystem1Default] pylon map, and counting that as loaded
        # whatever the fit credited a 2,324 NM anti-ship round to the nuclear
        # loadout. 55 of 210 placed unit/fit pairs sat on that mistake.
        suffix = next((l for l in sorted(known, key=len, reverse=True)
                       if section.endswith(l)), None)
        if suffix:
            if suffix != loadout:
                continue
        elif re.match(r"WeaponSystem\d+[A-Za-z][A-Za-z0-9_-]*$", section):
            continue
        # Three spellings, all in shipped data: `Station7=`, `Ammunition1=`
        # and a bare `Ammunition=` with no index - which is how a launcher
        # section names its one round (2,425 lines across 699 files, among
        # them both of the Peykaap's Nasir launchers). Missing the bare form
        # under-credited stores and made an anti-ship boat read as a rocket
        # boat to the reach check.
        m = re.match(r"(?:Station\d+|Ammunition\d*)=([^\s#/]+)", s)
        if m:
            out.add(m.group(1).split("|")[0])
        m = re.match(r"DateBased_\w+=(\S+)", s)
        if m:
            for part in m.group(1).split("|"):
                bits = part.split(",")
                if len(bits) == 2:
                    out.add(bits[1])
    return sorted(x for x in out if x and not x[0].isdigit())


_TOKENS = None


def mod_token(mod_id):
    """Catalog id (or SEST pack folder) -> the token the load order uses."""
    global _TOKENS
    if _TOKENS is None:
        data = catalog()
        _TOKENS = {m["id"]: str(m["workshop_id"]) for m in data["mods"]}
        _TOKENS.update({p["folder"]: p["folder"] for p in data["local_packs"]})
        # Stock units carry no mod credit, and saying so in the roster is how
        # a unit that SHOULD come from a mod gets caught when something
        # unsubscribes and the game silently falls back to vanilla.
        _TOKENS["_vanilla"] = "_vanilla"
    if mod_id not in _TOKENS:
        raise SystemExit(f"roster names unknown mod {mod_id!r} - it is not in "
                         "data/mod-catalog.json")
    return _TOKENS[mod_id]


def resolve(spec):
    """Fill one authored unit in: winning file, kind, variant, squadron, fit.

    Returns the block keys the mission needs plus the credit set - every mod
    whose files this one unit makes the game read.
    """
    uid = spec["type"]
    kind_dir, path = unit_file(uid)
    if path is None:
        raise SystemExit(f"{spec['mission']}: no enabled mod defines {uid!r}")
    utype = unit_type(uid)
    kind = KIND_OF.get(utype)
    if kind is None:
        raise SystemExit(f"{spec['mission']}: {uid} has UnitType={utype!r}, "
                         "which is not a kind a mission can place")
    if spec.get("kind") and spec["kind"] != kind:
        raise SystemExit(f"{spec['mission']}: {uid} is a {kind}, but the roster "
                         f"files it as a {spec['kind']} - upstream changed it")

    keys, credit = {}, {}

    def note(token, how, detail):
        if token and token not in credit:
            credit[token] = (how, detail)

    note(owner(f"{kind_dir}/{uid}.ini"), "unit", uid)

    pool = variants(uid, kind_dir)
    if pool:
        want = spec.get("variant") or pool[0]
        if want not in pool:
            raise SystemExit(f"{spec['mission']}: {uid} has no {want} "
                             f"(has: {', '.join(pool)})")
        keys["VariantReference"] = want
        note(owner(f"{kind_dir}/{uid}_variants.ini"), "variant", uid)

    if kind in ("air", "heli"):
        sq = squadrons(uid)
        if sq:
            want = spec.get("squadron") or ("Squadron1" if "Squadron1" in sq else sq[0])
            if want not in sq:
                raise SystemExit(f"{spec['mission']}: {uid} has no {want} "
                                 f"(has: {', '.join(sq)})")
            keys["SquadronReference"] = want
            note(owner(f"aircraft/{uid}_squadrons.ini"), "squadron", uid)

    fit, _why = pick_loadout(uid, path, spec.get("loadout"))
    if fit:
        keys["LoadoutVariant"] = fit
    for store in stores(uid, kind_dir, path, fit):
        note(owner(f"ammunition/{store}.ini"), "store", f"{uid} / {store}")
    for folder in sorted(set(ASSET_FOLDER.findall(read(path)))):
        for token in sorted(asset_owners(folder)):
            note(token, "asset", f"{uid} / {folder.rstrip('/')}")

    # The roster says which mod each unit is there to exercise. If the game
    # would read nothing of that mod's, the roster is wrong - either something
    # now outranks it, or the unit was mis-attributed. Either way it must be
    # said out loud rather than quietly counted as coverage.
    want = mod_token(spec["mod"])
    if want not in credit:
        raise SystemExit(
            f"{spec['mission']}: {uid} is rostered for {spec['mod']}, but the game "
            f"reads nothing of its from this unit. What it does read: "
            + ", ".join(f"{tok} ({how})" for tok, (how, _d) in sorted(credit.items())))

    return kind, keys, credit


# --- rendering ---------------------------------------------------------------

BLOCK_ORDER = ("Type", "VariantReference", "SpawnByVariableAND",
               "SquadronReference", "JoinTaskForce", "LoadoutVariant",
               "TaskForceModeAnchor", "TaskForceModeReplacedUnitIndex",
               "Nation", "UnlimitedFuel", "WeaponStatus",
               "RadarsActive", "CrewSkill", "Morale", "CampaignTag",
               "RelativePositionInNM", "Heading", "Telegraph",
               # last, after Waypoints, where the native blocks put it
               "HomeBase")


def block(tag, keys):
    lines = [f"[{tag}]"]
    for k in BLOCK_ORDER:
        if k in keys:
            lines.append(f"{k}={keys[k]}")
    for k, v in keys.items():
        if k not in BLOCK_ORDER:
            lines.append(f"{k}={v}")
    return "\n".join(lines)


# Most direct reason first: a mod that supplies a hull the mission places is
# reported by that hull, not by a round the hull happens to carry.
STRENGTH = {"unit": 0, "variant": 1, "squadron": 2, "roster": 3, "store": 4,
            "asset": 5}


# Model folders a unit file loads from another mod's `assets/` tree. The game
# resolves `ResourcesMeshFolder=assets/models/aircraft/usn_sh-60b/` through the
# load order like any other path, so the mod that ships that folder is as much
# a dependency as the one that ships the unit - and nothing else here sees it:
# ADO Nimitz 2000s' carrier (D2's Carl Vinson) draws its deck Seahawks from
# the MH-60R Seahawk mod, and the only thing that kept that mod on the
# required list was a squadron table it no longer wins. Stock never uses the
# `assets/` prefix, so every such path is a mod's. The export is text-only: a
# folder that ships nothing but meshes and textures has no file here to own
# it, and is skipped rather than reported missing.
ASSET_FOLDER = re.compile(r"^\s*Resources\w*Folder\s*=\s*([A-Za-z0-9_][^\s#/]*(?:/[^\s#/]+)*)/?",
                          re.M | re.I)
_ASSET_OWNERS = None


def asset_owners(folder):
    """Tokens that win at least one exported file under `folder`.

    Any folder a unit file loads from counts, not only `assets/` ones: the
    P-8 mod's airframe lives in aircraft/P8_Poseidon/Upgrade/, and once a
    SEST pack patches both of that aircraft's text files the model folder is
    the only thing left saying the mod is read at all. index() skips files
    nested inside the unit folders (it answers "which unit file wins"), so
    this walks every provider in the same first-wins order. A folder the
    stock game also ships (aircraft/materials/) is shared ground and credits
    nobody.
    """
    global _ASSET_OWNERS
    if _ASSET_OWNERS is None:
        _ASSET_OWNERS = collections.defaultdict(set)
        seen = set()
        for token, base in providers():
            for f in sorted(base.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(base).as_posix().lower()
                if rel in seen:
                    continue
                seen.add(rel)
                parts = rel.split("/")
                for i in range(2, len(parts)):
                    _ASSET_OWNERS["/".join(parts[:i])].add(token)
    key = folder.lower().rstrip("/")
    owners = _ASSET_OWNERS.get(key, set())
    return set() if ("_vanilla" in owners or key in stock_folders()) else owners


_STOCK_FOLDERS = None


def stock_folders():
    """Every folder a stock unit file loads from - shared ground.

    The vanilla export is text-only, so a folder of stock meshes and
    textures (aircraft/materials/) has no exported file to show it is the
    game's; the stock unit files that load from it are the evidence. A mod
    that ships into such a folder is dressing shared ground, not supplying
    this unit's model, and is not credited for it.
    """
    global _STOCK_FOLDERS
    if _STOCK_FOLDERS is None:
        _STOCK_FOLDERS = set()
        base = ROOT / "mods-source" / "_vanilla" / "original"
        for f in base.rglob("*.ini"):
            text = f.read_text(encoding="utf-8-sig", errors="replace")
            _STOCK_FOLDERS |= {m.lower().rstrip("/") for m in ASSET_FOLDER.findall(text)}
    return _STOCK_FOLDERS


def place(mission, snapper):
    """Give every authored unit a section id, a position and its credits."""
    centre = mission["centre"]
    # Where this mission's aircraft can come down. `UnlimitedFuel` is the
    # game's own answer to having nowhere: "Use this option when an airbase is
    # not available for units to prevent aircraft from crashing at bingo fuel"
    # (language_en/ui.ini:1081). Seventeen of these twenty-two missions field
    # aircraft with no base and every one of them used to ship False.
    decks = max([deck_size(u["type"]) for u in mission["units"]
                 if u["side"] == "blue"] or [0])
    placed = collections.defaultdict(list)     # family -> [(tag, keys)]
    members = collections.defaultdict(list)    # station -> [tag]
    credits = {}
    seats = collections.Counter()              # per-station air spacing
    berths = collections.Counter()             # per-station sea spacing
    station_snap = {}                          # station -> ((lat, lon), drift)
    worst = 0.0

    # The generated force forms on Taskforce1Vessel1: every stock Task Force
    # Mode mission puts TaskForceModeAnchor on the FIRST unit of its kind, and
    # the authoring guide says other slots misbehave. So the anchored ship is
    # sorted to the front of the blue vessels before anything is numbered,
    # rather than being anchored wherever the roster happened to list it.
    anchor = mission.get("anchor")
    units = list(mission["units"])
    if anchor:
        station, _, idx = anchor.partition("#")
        want = int(idx) if idx else 1
        seen = 0
        for i, spec in enumerate(units):
            if spec["side"] == "blue" and spec["station"] == station:
                seen += 1
                if seen == want:
                    units.insert(0, units.pop(i))
                    break

    for spec in units:
        spec = dict(spec, mission=mission["key"])
        st = mission["stations"][spec["station"]]
        kind, keys, credit = resolve(spec)
        family = FAMILY[(spec["side"], kind)]
        idx = len(placed[family]) + 1
        tag = f"{family}{idx}"

        if kind in ("air", "heli"):
            n = seats[spec["station"]]
            seats[spec["station"]] += 1
            lat = st["at"][0] - (n // 3) * 0.05
            lon = st["at"][1] + (n % 3) * 0.05
            alt = spec.get("alt", st.get("alt", 25000))
        elif kind == "land" or spec.get("snap") or st.get("coastal"):
            # Where the place IS the point - a port, an airbase, a rig that
            # belongs in water, a drifting hull authored onto a proven spot -
            # each unit is snapped on its own, as far as it takes. An oil rig
            # is a LandUnit that belongs in water; everything else takes the
            # pool its kind implies.
            want = spec.get("snap") or ("land" if kind == "land" else "sea")
            (lat, lon), dist = snapper.take(want, st["at"],
                                            where=f"{mission['key']} {spec['station']}")
            worst = max(worst, dist)
            alt = "low" if kind == "land" else (spec.get("depth", 0)
                                                if kind == "sub" else 0)
        else:
            # Offshore, the STATION is snapped - once - and its ships form on
            # the snapped point. It used to snap every hull on its own to the
            # nearest proven point nobody had used yet, which scattered a
            # four-ship convoy across four unrelated spots and put its escort
            # wherever ITS nearest point happened to be: SW01's authored
            # 34 NM between Warramunga and her convoy shipped as 46-51, in a
            # 50-minute mission an Anzac at flank covers 24 NM of. A point
            # 0.6 NM from proven water is water. The limit is small on
            # purpose: a station that has to move further than OFFSHORE_SNAP
            # is a station that was authored in the wrong place, and the
            # build should say so rather than quietly deform the encounter.
            key = spec["station"]
            if key not in station_snap:
                station_snap[key] = open_water(snapper, st["at"],
                                               f"{mission['key']} {key}")
                worst = max(worst, station_snap[key][1])
            (alat, alon), _d = station_snap[key]
            n = berths[key]
            berths[key] += 1
            # line abreast on the station's heading, 0.6 NM apart, alternating
            # sides of the snapped point so the group centres on it
            side = (n + 1) // 2 * (1 if n % 2 else -1)
            beam = math.radians(st.get("heading", 90) + 90)
            lat = alat + side * 0.6 * math.cos(beam) / 60.0
            lon = alon + side * 0.6 * math.sin(beam) / (60.0 * math.cos(math.radians(alat)))
            # A submarine at 0 is on the surface. That is deliberate for the
            # boat alongside its tender in SW09 and wrong for everything that
            # is meant to be hunting; depth is authored per unit.
            alt = spec.get("depth", 0) if kind == "sub" else 0

        keys = dict(Type=spec["type"], **keys)
        # Native writes UnlimitedFuel on every section kind - vessels,
        # submarines, land units, even biologics - so it is emitted for all of
        # them here too, inert. assign_home_bases() overwrites it for anything
        # that flies once every section has a number, because the answer
        # depends on what else is in the mission.
        keys.update(UnlimitedFuel="False",
                    WeaponStatus=spec.get("weapons", "Free"),
                    RadarsActive=spec.get("radars", "True"),
                    CrewSkill=spec.get("skill", "Trained"), Morale="3")
        keys["RelativePositionInNM"] = (
            f"{(lon - centre[1]) * 60:.2f},{alt},{(lat - centre[0]) * 60:.2f}")
        keys["Heading"] = spec.get("heading", st.get("heading", 90))
        # A civil aircraft flies an airway, never an orbit. With no Waypoints
        # the game holds an aircraft in a circle over its spawn, and one that
        # reaches its last waypoint circles there - White Water's airliner did
        # the first, and every Southern Reach airliner did it all mission.
        # `airway=(lat, lon)` names where the service is going; the one
        # waypoint written lies on that bearing and past anything the clock
        # lets an airliner reach at cruise, so it is still en route when the
        # mission ends. That is the stock pattern: Charlies.ini's DC-10 flies
        # a single waypoint 500 NM out.
        if spec.get("airway") and not spec.get("route"):
            if kind != "air":
                sys.exit(f"{mission['key']}: airway= is for fixed-wing traffic; "
                         f"{spec['type']} is {kind}")
            to_lat, to_lon = spec["airway"]
            dx, dz = (to_lon - lon) * 60, (to_lat - lat) * 60
            dist = math.hypot(dx, dz)
            if dist < 1:
                sys.exit(f"{mission['key']}: {spec['type']}'s airway ends where it starts")
            stretch = max(1.0, AIRWAY_MARGIN * civil_reach_nm(mission) / dist)
            spec = dict(spec, route=[(lat + (to_lat - lat) * stretch,
                                      lon + (to_lon - lon) * stretch, alt)],
                        telegraph=spec.get("telegraph", 3))
            keys["Heading"] = round(math.degrees(math.atan2(dx, dz)) % 360)
        if spec.get("nation"):
            keys["Nation"] = spec["nation"]
        for k, v in spec.get("extra", {}).items():
            keys[k] = v

        # The purchased task force forms on the anchor. The sort above put the
        # anchored ship first, so it is the first blue vessel that gets the
        # flag - every stock Task Force Mode mission anchors Taskforce1Vessel1,
        # and three of these anchored Vessel2 or Vessel3 before that sort.
        if (mission.get("anchor") and spec["side"] == "blue"
                and kind == "vessel" and not mission.get("_anchored")):
            if idx != 1:
                sys.exit(f"{mission['key']}: the anchor landed on {tag}, not "
                         "the first blue vessel")
            # The guide: in a Generated mission the anchor is REPLACED by
            # the player's first ship, which takes its position, heading,
            # telegraph and waypoints; in a Replaced mission the slot with
            # ReplacedUnitIndex=1 is filled the same way. Either way this
            # section is the player's own hull at launch, so it carries no
            # name (the player's ship keeps its own) and no fiction may call
            # it by one. Blank generation launches the file as authored and
            # the anchor key is not emitted at all.
            if spec.get("name") and mission.get("generation"):
                sys.exit(f"{mission['key']}: the anchor {spec['type']} is "
                         f"named {spec['name']!r}, but at launch it is the "
                         "player's first ship - drop the name= and address "
                         "the player's force in the briefing")
            if mission.get("generation"):
                keys["TaskForceModeAnchor"] = "True"
                if mission["generation"] == "Replaced":
                    keys["TaskForceModeReplacedUnitIndex"] = "1"
                mission["_anchor_tag"] = tag
            mission["_anchored"] = True
        # A purchased aircraft reaches a mission through a flight row and a
        # matching slot. Without these the roster sells aircraft that no
        # mission can deploy.
        # SpawnByVariableAND lets an earlier operation change a later order of
        # battle: 08A Pathfinders omits two SA-8 launchers when 07A sank the
        # Palawan reinforcements, and 10 Vengeance at Luzon omits the Slava and
        # its screen when 07A sank the Slava. This is how a consequence is
        # enforced rather than narrated.
        if spec.get("spawn_if"):
            var, state = spec["spawn_if"]
            keys["SpawnByVariableAND"] = f"{var},{state}"
        if spec.get("join"):
            # The native grant of a unit the player did not buy: JoinTaskForce
            # with a CampaignTag naming type, fit and mission - `04 Sunda
            # Strait` line 504, `08A Pathfinders` line 531, four more. It is
            # what a mission uses when an objective depends on the aircraft
            # being THAT aircraft, and it never co-occurs with a tasking slot.
            keys["JoinTaskForce"] = "True"
            fit = keys.get("SquadronReference") or keys.get("VariantReference")
            keys["CampaignTag"] = "_".join(
                x for x in (keys["Type"], fit, mission["num"]) if x)
        if spec.get("slot") and not mission.get("generation"):
            sys.exit(f"{mission['key']}: {spec['type']} is slot-tagged, but a "
                     "blank-generation mission places no persistent aircraft "
                     "- there is nothing to fill it with")
        if spec.get("slot"):
            # A slot is a cockpit the player fills with whatever they own.
            # No slot-tagged section in the shipped campaign carries a
            # NameOverride, and a hard-coded callsign on one promises an
            # airframe the briefing cannot know is there.
            if spec.get("name"):
                sys.exit(f"{mission['key']}: {spec['type']} fills the "
                         f"{spec['slot']!r} slot and is named "
                         f"{spec['name']!r} - slot-tagged aircraft keep the "
                         "player's own names; drop the name=")
            role = spec["slot"]
            keys["TaskForceModeAirTaskingSlot"] = slot_ordinal(
                mission.get("window", {}).get("flights", []), role,
                spec["mission"])
            keys["TaskForceModeAirTaskingRole"] = role
        if spec.get("route"):
            if isinstance(snapper, CoastPlacer) and kind in ("vessel", "sub"):
                for la, lo, _a in spec["route"]:
                    snapper.waypoint((la, lo), f"{mission['key']} {spec['station']} "
                                               f"({spec['type']})")
            keys["Waypoints"] = "|".join(
                f"{(lo - centre[1]) * 60:.2f},{a},{(la - centre[0]) * 60:.2f}"
                for la, lo, a in spec["route"])
            # A route without a speed is a route at whatever the game
            # defaults to. Every one of the 169 waypointed vessel and
            # submarine sections in the Pacific Strike export sets Telegraph=
            # (0-5; 3 is cruise, 2 is the most common), and SW04's whole
            # mission hangs on its passenger arriving before a deadline.
            keys["Telegraph"] = spec.get("telegraph", 3)

        placed[family].append((tag, keys, spec.get("name"),
                               spec.get("no_neutral_penalty", False)))
        members[spec["station"]].append(tag)
        for token, why in credit.items():
            best = credits.get(token)
            if best is None or STRENGTH[why[0]] < STRENGTH[best[0]]:
                credits[token] = (why[0], why[1], mission["key"])

    # Every civil aircraft is still on its airway when the clock runs out:
    # one with no route circles its spawn, one that reaches its last
    # waypoint circles that, and players notice both.
    reach = civil_reach_nm(mission)
    for tag, keys, name, _x in placed.get("NeutralAircraft", []):
        if not str(keys.get("Type", "")).startswith("civ_"):
            continue
        label = f"{tag} ({keys['Type']}{', ' + name if name else ''})"
        if not keys.get("Waypoints"):
            raise SystemExit(f"{mission['key']}: {label} has no route - an aircraft "
                             "with no Waypoints circles its spawn all mission; give "
                             "it airway=(lat, lon), where the service is going")
        x, _a, z = (float(v) for v in keys["RelativePositionInNM"].split(",")[:3])
        path = 0.0
        for wp in keys["Waypoints"].split("|"):
            wx, _wa, wz = (float(v) for v in wp.split("/")[0].split(",")[:3])
            path += math.hypot(wx - x, wz - z)
            x, z = wx, wz
        if path <= reach:
            raise SystemExit(f"{mission['key']}: {label} flies {path:.0f} NM of route "
                             f"and the clock gives it {reach:.0f} at cruise - it "
                             "arrives and circles; use airway= or extend the route")

    stranded = assign_home_bases(placed)
    if stranded:
        raise SystemExit(f"{mission['key']}: " + "; ".join(stranded))
    return placed, members, credits, worst


def assign_home_bases(placed):
    """Give every aircraft somewhere to land, and only then charge it fuel.

    `HomeBase` names the section of the field or the deck an aircraft belongs
    to - 54 native aircraft and helicopters carry one, pointing at a
    `Taskforce1LandUnit` airfield or at a ship, and 59 of them are on the RED
    side. 42 of the 54 also carry `UnlimitedFuel=False`, which is the point:
    an aeroplane with a base can be charged for fuel, and one without cannot
    be, because it will fly until it falls out of the sky.

    Both keys are decided together, per airframe, per SIDE - an aircraft
    recovers on its own side's deck or nobody's. A helicopter takes any deck
    (every escort here declares `AircraftCapacity=1`); a fast jet needs a real
    field or a carrier, ten being the gap between an escort's single spot and
    the smallest flight deck in the collection. Nearest first, so a ship's
    flight is homed on its own ship rather than whichever is numbered first.

    A deck is only a deck for an airframe the two files agree on: a ship's
    `AircraftSupported` list, an airframe's `CarrierCapable`, a VTOL's own
    UnitType. See deck_fit(). Fourteen assignments in the reviewed build put
    helicopters on decks whose lists left them out and F-35As on a carrier
    the airframe file says it cannot use.

    A player aircraft with nowhere in range is returned as a problem and fails
    the build: the answer is to give the mission a field or a deck, not to
    hand the aeroplane infinite fuel. For red and neutral the same search runs
    and the same bases are used where they exist, but nothing fails - their
    order of battle is not the design's to fix, and a red fighter dropping out
    of the sky at bingo would hand the player the mission.
    """
    spot = unit_spot
    stranded = []
    for side in ("Taskforce1", "Taskforce2", "Neutral"):
        decks = []
        for kind_family in ("LandUnit", "Vessel"):
            for tag, keys, _n, _x in placed.get(side + kind_family, []):
                size = deck_size(keys["Type"])
                if size:
                    decks.append((tag, size, spot(keys), keys["Type"],
                                  kind_family == "Vessel"))

        for family in (side + "Aircraft", side + "Helicopter"):
            for tag, keys, _n, _x in placed.get(family, []):
                kind = unit_type(keys["Type"])
                if kind not in ("Aircraft", "Helicopter", "VTOL"):
                    continue
                here = spot(keys)

                def how_far(deck):
                    if not (here and deck[2]):
                        return 9e9
                    return math.hypot(deck[2][0] - here[0],
                                      deck[2][1] - here[1])

                total = airframe_range(keys["Type"])
                radius = (total or 0.0) * SORTIE_FRACTION
                options, refused = [], []
                for d in decks:
                    fit = deck_fit(keys["Type"], kind, d[3], d[4])
                    if fit is None:
                        refused.append(d[3])
                        continue
                    # A helicopter takes any deck; a fast jet needs a field
                    # or a carrier; a VTOL takes a deck that names it and a
                    # field otherwise.
                    needs = 1 if kind == "Helicopter" else 10
                    if kind == "VTOL" and d[4] and fit == 0:
                        needs = 1
                    if d[1] < needs:
                        continue
                    options.append((fit, how_far(d), d))
                # Compatible decks first, nearest first within each class:
                # a jet with no CarrierCapable line lands on a field 40 NM
                # away before it lands on a carrier 10 NM away.
                options.sort(key=lambda o: (o[0], o[1]))
                pick = next((o for o in options if o[1] <= radius), None)
                if pick:
                    fit, dist, d = pick
                    keys["HomeBase"] = d[0]
                    keys["UnlimitedFuel"] = "False"
                    if fit == 1:
                        RECOVERY_NOTES.append(
                            f"{keys['Type']} at {tag} recovers on {d[3]} "
                            f"({d[0]}), which lists no supported aircraft, "
                            "and the airframe declares no CarrierCapable - "
                            "undeclared, untested")
                    continue
                # Nowhere to land. For the player that is a design fault and
                # the build says so; for anyone else it is the tooltip's own
                # case, and infinite fuel beats falling out of the sky.
                keys["UnlimitedFuel"] = "True"
                if side != "Taskforce1":
                    continue
                why = (f" ({', '.join(sorted(set(refused)))} refused it: "
                       "AircraftSupported or CarrierCapable)" if refused else "")
                if total is None:
                    stranded.append(
                        f"{keys['Type']} at {tag} declares no range - no "
                        "MaxRange, no SpeedAndRange_Cruise, no alias with one")
                elif not options:
                    stranded.append(
                        f"{keys['Type']} at {tag} has nowhere to land in this "
                        "mission - no compatible "
                        + ("deck" if kind == "Helicopter" else "field or carrier")
                        + " on its own side" + why)
                else:
                    stranded.append(
                        f"{keys['Type']} at {tag} is {options[0][1]:.0f} "
                        f"NM from the nearest base it can use, and "
                        f"{total:.0f} NM of range gives it a {radius:.0f} NM "
                        "radius. Put something it can land on within reach"
                        + why)
    return stranded

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def date_words(date):
    """(2028, 10, 18) -> '18 October 2028'. No locale, no strftime."""
    y, m, d = date
    return f"{d} {MONTHS[m - 1]} {y}"


def mission_code(mission):
    """The short id that names a mission's files and its mark on the backdrop.

    Southern Watch's numbers are unique on their own ("01", "O1", "D1");
    a campaign with two series numbers each from 01 and sets `code`
    ("SR01", "TS01") so the two first missions do not share a card.
    """
    return mission.get("code", mission["num"])


def sheet_path(mission):
    """Where this mission's card lives, spelled once."""
    return f"campaigns/{SLUG}/art/{ART_PREFIX}_{mission_code(mission).lower()}_sheet.png"


def mission_name(mission):
    """The name the browser and the campaign card both show.

    Prefixed, because a mission browser lists everything flat and "01 White
    Water" beside a stock campaign's "01 Raid on Okinawa" tells nobody who
    owns it. A campaign with more than one series (Southern Reach's two
    chapters) names each mission by its own series rather than the campaign.
    """
    return f"{mission.get('series', TITLE)} {mission['num']} - {mission['key']}"


def browse_folder(mission):
    """Which mission-browser folder a mission's second copy goes in."""
    if mission["group"] == "dispatch":
        return DISPATCHES
    if BROWSE:
        return BROWSE.get(mission.get("series"), BROWSE.get(mission["group"], TITLE))
    return TITLE


def refs(members, ref):
    """"station" -> every tag at it; "station#2" -> just the second."""
    station, _, idx = ref.partition("#")
    if station not in members:
        raise SystemExit(f"objective or condition names station {station!r}, "
                         "which places nothing")
    group = members[station]
    if not idx:
        return list(group)
    if int(idx) > len(group):
        raise SystemExit(f"{ref}: station {station!r} places only "
                         f"{len(group)} unit(s)")
    return [group[int(idx) - 1]]


def area_condition(n, centre, at, radius, units, minimum, side="Blue"):
    return [f"Condition_Condition{n}_Type=UnitsInTheArea",
            f"Condition_Condition{n}_PositionNM="
            f"{(at[1] - centre[1]) * 60:.2f},0,{(at[0] - centre[0]) * 60:.2f}",
            f"Condition_Condition{n}_AreaRadiusNM={radius}",
            f"Condition_Condition{n}_AreaDisplaySide={side}",
            f"Condition_Condition{n}_Units={','.join(units)}",
            f"Condition_Condition{n}_MinimumUnits={minimum}"]


def destroyed_condition(n, units, minimum):
    return [f"Condition_Condition{n}_Type=UnitDestroyed",
            f"Condition_Condition{n}_Units={','.join(units)}",
            f"Condition_Condition{n}_MinimumUnits={minimum}"]


def classified_condition(n, units, minimum, by):
    """`by` has classified at least `minimum` of `units`.

    The numbered form with the minimum spelled out, key for key as stock
    writes it when the ENEMY is the side classifying: Operation Polar Fury
    1985 Trigger5 (Taskforce2 classifying the player's two submarines) and
    Mind the Gap - Original 1988 Trigger2 (the player's five ships). The
    player-side classify resolver keeps its own un-numbered form.
    """
    return [f"Condition_Condition{n}_Type=UnitClassified",
            f"Condition_Condition{n}_Taskforce={by}",
            f"Condition_Condition{n}_Units={','.join(units)}",
            f"Condition_Condition{n}_MinimumUnits={minimum}"]


# A fatal entry's kinds, and the resolvers each may take its units from when
# it names none (see F() in campaign_data.py).
FATAL_SOURCES = {"destroyed": ("protect", "survive"), "unseen": ("unseen",)}


# What a victory `also` term may say, by kind: (keys it needs, keys it reads).
# A term used to be a Time test if it had after_minutes and an area test
# otherwise, whatever else it said - so `also=[dict(kind="destroyed",
# units=["spoiler"])]` came out as "the spoiler is inside the arrival box",
# a mission nobody could win, and the build was clean. A kind or a key this
# table does not know now stops the build instead.
ALSO_TERMS = {
    "time": ({"after_minutes"}, {"kind", "after_minutes"}),
    "area": ({"units"}, {"kind", "units", "at", "radius", "min_units"}),
    "destroyed": ({"units"}, {"kind", "units", "min_units"}),
}


def also_condition(mission, n, extra, members):
    """Condition n of the victory trigger, from one `also` term.

    `time`: the clock has reached after_minutes. `area`: min_units of the
    units are in a box (the victory's own unless `at`/`radius` say
    otherwise). `destroyed`: min_units of them are gone. Without a `kind`
    a term is `time` if it sets after_minutes and `area` if not, which is
    how every term written before the kinds existed reads.
    """
    victory = mission["victory"]
    kind = extra.get("kind") or ("time" if extra.get("after_minutes") else "area")
    if kind not in ALSO_TERMS:
        raise SystemExit(f"{mission['key']}: victory also-term has kind {kind!r}; "
                         f"the builder knows {', '.join(ALSO_TERMS)}")
    needs, reads = ALSO_TERMS[kind]
    stray, missing = sorted(set(extra) - reads), sorted(needs - set(extra))
    if stray or missing:
        raise SystemExit(
            f"{mission['key']}: a {kind!r} also-term "
            + (f"does not read {', '.join(map(repr, stray))}" if stray else "")
            + (" and " if stray and missing else "")
            + (f"needs {', '.join(map(repr, missing))}" if missing else "")
            + f" - {kind} reads {', '.join(sorted(reads))}")
    if kind == "time":
        return [f"Condition_Condition{n}_Type=Time",
                f"Condition_Condition{n}_Time={extra['after_minutes'] * 60}"]
    wanted = [extra["units"]] if isinstance(extra["units"], str) else extra["units"]
    units = [tag for r in wanted for tag in refs(members, r)]
    if kind == "destroyed":
        return destroyed_condition(n, units, extra.get("min_units", len(units)))
    return area_condition(n, mission["centre"], extra.get("at", victory.get("at")),
                          extra.get("radius", victory.get("radius", 20)),
                          units, extra.get("min_units", len(units)))


# Conservative transit speeds for the reachability check, in knots. They are
# deliberately below what the hulls can do: the question is whether an arrival
# objective is possible at all, not whether it is comfortable.
# Keyed on the unit's own UnitType, because an Aircraft family holds both a
# 300-knot jet and a 120-knot helicopter and the slow one is what decides
# whether an objective is reachable.
TRANSIT = {"Vessel": 18.0, "Submarine": 10.0, "LandUnit": 12.0,
           "Aircraft": 300.0, "VTOL": 250.0, "Helicopter": 120.0,
           "Biologic": 6.0}


def transit_of(tag, placed):
    for family, entries in placed.items():
        for t, keys, _n, _x in entries:
            if t == tag:
                return TRANSIT.get(unit_type(keys["Type"]), 18.0)
    return 18.0


def solve_arrival(mission, placed, members):
    """Put the arrival box where the units can actually reach it.

    Hand-written coordinates were the wrong tool: the position snapper spreads
    a convoy by however far the proven-point pool forces it, so a box that is
    reachable in one theatre is 26 NM out of reach in another, and the author
    cannot see which from the data. So the roster authors a BEARING and a
    radius - the direction the operation is going and how big the handover area
    is - and the box is solved against the positions the units actually got.

    The chosen distance is the largest that still leaves the condition
    satisfiable: the units the condition needs can reach it, and fewer than
    that many start inside it.
    """
    victory = mission["victory"]
    if victory["kind"] != "arrive" or "bearing" not in victory:
        return
    centre = mission["centre"]
    wanted = (list(victory["units"]) if victory.get("units")
              else [victory["station"]])
    tags = {t for r in wanted for t in refs(members, r)}
    spots = []
    for family, entries in placed.items():
        for tag, keys, _n, _x in entries:
            if tag in tags:
                x, _alt, z = keys["RelativePositionInNM"].split(",")
                spots.append(((centre[0] + float(z) / 60.0,
                               centre[1] + float(x) / 60.0),
                              TRANSIT.get(unit_type(keys["Type"]), 18.0)))
    if not spots:
        raise SystemExit(f"{mission['key']}: the arrival condition names no unit")
    minimum = victory.get("min_units", len(spots))
    radius = victory.get("radius", 12)
    lat0 = sum(p[0] for p, _f in spots) / len(spots)
    lon0 = sum(p[1] for p, _f in spots) / len(spots)
    brg = math.radians(victory["bearing"])

    # Start from a distance that is a sensible operation rather than the
    # furthest technically-reachable one: the slowest unit spends at most about
    # 60% of the mission's clock getting there, leaving the rest for the fight
    # that is the actual point of the mission.
    # A mission may state its own convoy speed - SW12's Coral Pioneer makes
    # nine knots on one shaft, and a box solved at the class default of 18
    # was a box she could not reach.
    slowest = victory.get("transit") or min(f for _p, f in spots)
    cap = int(radius + mission["minutes"] / 60.0 * slowest * 0.6)
    best = None
    for step in range(max(cap, radius + 4), radius + 2, -1):
        at = (lat0 + step * math.cos(brg) / 60.0,
              lon0 + step * math.sin(brg) / 60.0 / math.cos(math.radians(lat0)))
        d = sorted((nm_between(p, at), f) for p, f in spots)
        if sum(1 for x, _f in d if x < radius) >= minimum:
            continue
        if all(x - radius <= mission["minutes"] / 60.0 * f * 0.75
               for x, f in d[:minimum]):
            best = at
            break
    if best is None:
        raise SystemExit(
            f"{mission['key']}: no arrival distance on bearing "
            f"{victory['bearing']} works - {minimum} unit(s) must both start "
            f"outside a {radius} NM circle and reach it in "
            f"{mission['minutes']} minutes. Slow the objective down or give "
            "the mission more time.")
    victory["at"] = (round(best[0], 3), round(best[1], 3))


# The game classifies its own units in [AI] Role=. Anything here can shoot or
# be shot at as part of the opposition; an AEW aircraft, a transport, an
# airfield, a merchant or a range target cannot, and counting those as
# "enemy strength" is how a mission with one submarine and a KJ-500 overhead
# reads as five red units when it is really one threat.
COMBAT_ROLES = {
    "Fighter", "Bomber", "HeavyBomber", "StrategicBomber", "SEAD", "Attack",
    "ASuW", "ASuW_VLR", "ASuW_Gun", "ASuW_Gun", "AAW", "SAM", "Gun", "SS",
    "SSN", "SSBN", "ASW", "FAC", "Carrier", "CVL", "CVS", "ASM", "LandAttack",
}
NONCOMBAT_HINT = {"Merchant", "Airliner", "Airfield", "Target", "Transport",
                  "Spy", "RAS", "AEW", "Recon", "MaritimePatrol", "Radar",
                  "ESM", "SAR", "EW", "Landing"}


@functools.lru_cache(maxsize=None)
def ai_roles(uid):
    """The unit's own [AI] Role= tokens, following #!alias.

    Two traps live in this one line. The role sits in [AI], not at the top of
    the file, and several of these files carry a trailing `//` comment on it
    (`Role=Fighter                      //...`), so the value is cut at the
    first slash. And an aliased file has no [AI] section of its own: read
    jp_f-2a_late.ini directly and the F-2A declares no role at all, which
    would make a fighter look like a non-combatant to check_pacing and like a
    mismatch to the air-tasking gate.
    """
    _kind, f = unit_file(uid)
    return _roles_of(f)


def _roles_of(path, depth=0):
    if path is None or depth > 4:
        return frozenset()
    m = re.search(r"^\[AI\]\s*$(.*?)(?=^\[)", read(path), re.M | re.S)
    if m:
        r = re.search(r"^Role=([^/\n]+)", m.group(1), re.M)
        if r:
            return frozenset(x.strip() for x in r.group(1).split(",") if x.strip())
    return _roles_of(alias_target(path), depth + 1)


def is_combat(uid):
    roles = ai_roles(uid)
    if not roles:
        return True          # unclassified: assume it fights, and be wrong safe
    return bool(roles & COMBAT_ROLES)


# What each mission role is allowed to weigh, counted in RED units that can
# fight. The campaign's shape is an invariant, not a one-time edit: "smaller
# opening engagements" and "occasional fleet battles" only stay true if the
# build refuses to drift back.
# Hull counts and, since the reach check exists, the two distances that decide
# whether those hulls are opposition or scenery.
#
#   contact   the furthest a red unit's own longest round can be from the
#             nearest blue unit and still mean anything. A mission whose gap
#             exceeds red's reach by this much is a standoff with ships in it,
#             whatever its census says. None = the mission is not about a
#             fight and nothing is required to reach.
#   standoff  the closest red may spawn to blue. An opening that begins with
#             a missile boat already inside the convoy is not an opening; it
#             is an ambush the player cannot have seen coming.
ROLE_BUDGET = {
    "opening":   dict(max_combat=3, standoff=12, contact=0),
    "patrol":    dict(max_combat=4, standoff=8),
    "recon":     dict(max_combat=5, standoff=10, contact=0),
    "escort":    dict(max_combat=6, standoff=6, contact=0),
    "strike":    dict(max_combat=8, standoff=6, contact=0),
    "logistics": dict(max_combat=6, standoff=5, contact=0),
    "fleet":     dict(min_combat=8, standoff=15, contact=0),
    "exercise":  dict(max_combat=99),
}


def all_copies(relpath):
    """Every provider's copy of one file, highest priority first.

    `winning()` answers which file the game reads FIRST, which is the right
    question for a unit and the wrong one for a value. 102 files in this
    collection open with `#!extend`, 18 of them ammunition: the winner is a
    stub that adds a section or two and leaves the rest to the copy below it.
    `ammunition/plaaf_pl-15.ini` is 483 bytes of [Guidance] in mod 3789188689
    and `MaxLaunchRange=108.1` in 3436170138, so reading only the winner said
    a PL-15 reaches nothing.
    """
    key = relpath.lower()
    out = []
    for _token, base in providers():
        f = base / relpath
        if f.is_file():
            out.append(f)
        else:                                   # case-insensitive filesystem
            hit = _INDEX and _INDEX.get(key)
            if hit and hit[1].parent == base / Path(relpath).parent:
                out.append(hit[1])
    return out


def ammo_range(store, depth=0):
    """`MaxLaunchRange` for one round, down the extend/alias chain.

    The highest-priority file that actually DECLARES the value wins, which is
    what overriding means; a stub that declares nothing defers to the copy
    below it rather than answering zero.
    """
    if depth > 4:
        return 0.0
    best = 0.0
    for f in all_copies(f"ammunition/{store}.ini"):
        text = read(f)
        m = re.search(r"^MaxLaunchRange=([\d.]+)", text, re.M)
        if m:
            return float(m.group(1))
        a = re.search(r"#!alias\s+(\S+)", text)
        if a:
            best = max(best, ammo_range(Path(a.group(1)).stem, depth + 1))
    return best


_RANGE = {}

# What fraction of an airframe's total range is usable as a sortie radius.
#
# The RANGE itself is data - see airframe_range() - but turning a range into a
# radius needs one stated assumption, because a sortie has to come back. Half
# of it goes out and half returns, and a real profile spends the rest on
# reserve, join-up, time on task and the fact that nothing cruises the whole
# way. 0.40 is the planning figure that falls out of that, and it is the only
# number here that is not read from a file.
SORTIE_FRACTION = 0.40


def airframe_range(uid, depth=0):
    """Total range in nautical miles, off the unit's own flight model.

    Two spellings, both shipped. A helicopter declares `MaxRange` in
    `[Physics]`, already in nautical miles - MH-60R 520, AH-64E 1035, VH-3D
    542. A fixed-wing declares `SpeedAndRange_Cruise=<mach>,<range>` with a
    `RangeUnits` line whose comment reads "Can be: Km. Any other value = nmi",
    so only the literal Km converts - F-35A 1367 nmi, P-8 5000 km, B-2 9000.
    Aliased files defer to the airframe they extend, as everywhere else.

    Every one of the 100 airframes this campaign places answers.
    """
    if depth > 4:
        return None
    if uid in _RANGE:
        return _RANGE[uid]
    _kind, path = unit_file(uid)
    if path is None:
        return None
    text = read(path)
    out = None
    m = re.search(r"^MaxRange=\s*([\d.]+)", text, re.M)
    if m:
        out = float(m.group(1))
    else:
        c = re.search(r"^SpeedAndRange_Cruise=\s*[\d.]+\s*,\s*([\d.]+)",
                      text, re.M)
        if c:
            out = float(c.group(1))
            u = re.search(r"^RangeUnits=\s*(\S+)", text, re.M)
            if u and u.group(1).strip().lower() == "km":
                out /= 1.852
        else:
            a = re.search(r"#!alias\s+(\S+)", text)
            if a:
                out = airframe_range(Path(a.group(1)).stem, depth + 1)
    _RANGE[uid] = out
    return out


_REACH = {}
REACH_PROBLEMS = []
CLOSURE_PROBLEMS = []
CLOSURE_NOTES = []


def _bearing(fx, fz, tx, tz):
    """Compass bearing from (fx, fz) to (tx, tz) in the mission's NM frame:
    x east, z north."""
    return math.degrees(math.atan2(tx - fx, tz - fz)) % 360.0


def _off_bow(heading, bearing):
    """Degrees between where a unit points and where something is."""
    return abs((bearing - heading + 180.0) % 360.0 - 180.0)


def protected_tags(mission, members):
    """Every placed tag the mission says the player must keep alive or deliver:
    the arrival group, every fatal entry's units, every protect/survive
    resolver's stations."""
    out = set()
    v = mission.get("victory", {})
    if v.get("kind") in ("arrive", "protect", "survive"):
        for r in ([v.get("station")] + list(v.get("stations", []) or [])):
            if r:
                out |= set(refs(members, r))
    for entry in mission.get("fatal", []):
        # An `unseen` fatal is about who the enemy classifies, not what it
        # sinks; the boat slipping through a barrier is not an escorted hull.
        if entry.get("kind", "destroyed") != "destroyed":
            continue
        for r in entry.get("units") or []:
            out |= set(refs(members, r))
    for how in mission.get("resolve", {}).values():
        if isinstance(how, tuple) and how[0] in ("protect", "survive"):
            for r in how[1:]:
                if isinstance(r, str):
                    out |= set(refs(members, r))
    return out


def check_closure(mission, placed, members):
    """Is the encounter actually an encounter?

    check_reach asks whether red can hurt blue. This asks the three things it
    does not: whether the escort can get to what it is escorting before the
    clock runs out, whether the neutrals are anywhere the player will have to
    tell them apart from the threat, and whether a red unit that is supposed
    to press the player is pointed at them or is set dressing.

    SW01 shipped with its escort 50 NM from its convoy in a 50-minute mission,
    its "identification traffic" 130 NM away and sailing off, and its armed
    escort stationary, facing away, with a 17 NM radar 20 NM from the nearest
    merchant. Every one of those passed every gate. The first is a hard
    failure here; the other two are reported, because a background neutral
    or a red picket that never closes can be a legitimate design - but it
    has to be a decision, and a decision is something you can read.
    """
    def rows(prefix):
        out = []
        for family, entries in placed.items():
            if not family.startswith(prefix):
                continue
            kind = ("land" if family.endswith("LandUnit") else
                    "air" if family.endswith(("Aircraft", "Helicopter")) else
                    "sub" if family.endswith("Submarine") else "sea")
            for tag, keys, _n, _x in entries:
                bits = keys.get("RelativePositionInNM", "").split(",")
                try:
                    x, z = float(bits[0]), float(bits[2])
                except (ValueError, IndexError):
                    continue
                out.append(dict(tag=tag, uid=keys["Type"], x=x, z=z, kind=kind,
                                heading=float(keys.get("Heading", 0) or 0),
                                moving=any(k.startswith(("Waypoint", "Telegraph"))
                                           for k in keys),
                                fit=keys.get("LoadoutVariant")))
        return out

    blue, red, neutral = rows("Taskforce1"), rows("Taskforce2"), rows("Neutral")
    guard = protected_tags(mission, members)
    protected = [b for b in blue if b["tag"] in guard and b["kind"] in ("sea", "sub")]
    if not protected:
        return
    steam = mission["minutes"] / 60.0 * 24.0

    def armed_reach(u):
        kind_dir, path = unit_file(u["uid"])
        if path is None:
            return 0.0
        fit = u["fit"]
        if fit is None:
            fit, _why = pick_loadout(u["uid"], path, None)
        return reach(u["uid"], kind_dir, path, fit)

    escorts = [b for b in blue if b["kind"] == "sea" and armed_reach(b) > 0]
    if escorts:
        for pr in protected:
            nearest = min(escorts, key=lambda e: math.hypot(e["x"]-pr["x"], e["z"]-pr["z"]))
            d = math.hypot(nearest["x"]-pr["x"], nearest["z"]-pr["z"])
            if d - 2.0 > steam:
                CLOSURE_PROBLEMS.append(
                    f"{mission['key']}: {pr['tag']} ({pr['uid']}) is protected and "
                    f"the nearest escort ({nearest['tag']}, {nearest['uid']}) is "
                    f"{d:.0f} NM away - {mission['minutes']} minutes at 24 kn is "
                    f"{steam:.0f} NM. The escort cannot reach what it escorts.")

    def nearest_protected(u):
        pr = min(protected, key=lambda p: math.hypot(p["x"]-u["x"], p["z"]-u["z"]))
        return pr, math.hypot(pr["x"]-u["x"], pr["z"]-u["z"])

    if mission.get("neutral_objective"):
        for n in neutral:
            if n["kind"] == "land":
                continue
            pr, d = nearest_protected(n)
            closing = _off_bow(n["heading"], _bearing(n["x"], n["z"], pr["x"], pr["z"])) <= 60
            if d > 35.0 and not closing and not n["moving"]:
                CLOSURE_NOTES.append(
                    f"{mission['key']}: neutral {n['tag']} ({n['uid']}) is {d:.0f} NM "
                    f"from {pr['tag']} and pointed away - it is not part of the "
                    "identification picture")

    for r in red:
        if r["kind"] == "land":
            continue
        pr, d = nearest_protected(r)
        closing = _off_bow(r["heading"], _bearing(r["x"], r["z"], pr["x"], pr["z"])) <= 90
        if not closing and not r["moving"] and d > armed_reach(r):
            CLOSURE_NOTES.append(
                f"{mission['key']}: red {r['tag']} ({r['uid']}) is {d:.0f} NM from "
                f"{pr['tag']}, pointed away, with no waypoints and "
                f"{armed_reach(r):.0f} NM of reach - set dressing unless it moves")


def deck_size(uid):
    """Aircraft this unit can recover, from its own `AircraftCapacity`.

    The number separates every case cleanly and needs no list of names: an
    escort declares 1 (Anzac, Hobart, Arafura, Mogami, Maya), a flight deck 30
    to 90 (Canberra 30, Charles de Gaulle 42, Type 003 85, Ford 90), and an
    airbase 80 to 1000 (airfield_a-10 80, RAAF Darwin 200, the large PVO base
    1000). Matching on "airbase" in the id worked and would have gone on
    working right up to the first base that is not called one.

    Not every hull with a deck writes the line. Five vanilla Soviet hulls
    (Sovremenny, Slava, Kara, both Krestas) and every Euromod Korean hull
    declare their deck through `[AirGroup]` (the embarked flight, e.g.
    `rok_mk99_a=Default,1`) and `AircraftSupported`, with no capacity at all;
    the game flies their helicopters regardless. So a hull with no capacity
    line but an [AirGroup] falls back to the number of airframes that group
    embarks, and one with a [FlightDeck] section but neither falls back to
    its `DeckParkSlots`. A hull with none of these is not a deck.
    """
    _kind_dir, path = unit_file(uid)
    if path is None:
        return 0
    text = read(path)
    m = re.search(r"^AircraftCapacity=\s*(\d+)", text, re.M)
    if m:
        return int(m.group(1))
    group = re.search(r"^\[AirGroup\]\s*\n((?:[^\[\n][^\n]*\n?)*)", text, re.M)
    if group:
        n = sum(int(c) for c in re.findall(
            r"^\s*[^#\s=]+=\w+,(\d+)", group.group(1), re.M))
        if n:
            return n
    if re.search(r"^\[FlightDeck\]", text, re.M):
        m = re.search(r"^DeckParkSlots=\s*(\d+)", text, re.M)
        if m:
            return int(m.group(1))
    return 0


def reach(uid, kind_dir, path, fit):
    """How far this unit can shoot, in NM, from the rounds it actually carries.

    `MaxLaunchRange` off every ammunition file the chosen fit hangs. It is the
    one number that says whether two groups on a map can affect each other,
    and nothing in the campaign data states it - which is how a mission came
    to declare a surface action and place its target 208 NM from a frigate
    whose longest round reaches 28.

    It is a ceiling, not a capability: it ignores what the round is FOR. A
    ship with a 28 NM SAM and a 13 NM gun reads 28, and cannot sink anything
    at 20. So this is used to prove a force CANNOT reach, never to prove it
    can.
    """
    key = (uid, fit)
    if key in _REACH:
        return _REACH[key]
    best = max([ammo_range(s) for s in stores(uid, kind_dir, path, fit)]
               or [0.0])
    _REACH[key] = best
    return best


def check_reach(mission, placed, members):
    """Can the two sides actually affect each other, and can the player win?

    Two questions the unit census cannot answer and that no amount of counting
    hulls will. A mission that declares a fleet action and places its enemy
    135 NM beyond anybody's reach is a standoff with a fleet in it; a mission
    whose victory is `destroy` against a target nothing aboard can reach is
    not a hard mission, it is an unwinnable one.

    Distance is straight-line at spawn plus what the slowest sensible transit
    adds over the mission clock - 24 knots for a surface group, which is the
    figure the campaign's own escorts are written around. Aircraft are not
    given a transit allowance here because their own reach dwarfs it.
    """
    def positions(family_prefix):
        out = []
        for family, entries in placed.items():
            if not family.startswith(family_prefix):
                continue
            ashore = family.endswith("LandUnit")
            flies = family.endswith(("Aircraft", "Helicopter"))
            for tag, keys, _n, _x in entries:
                bits = keys.get("RelativePositionInNM", "").split(",")
                if len(bits) == 3:
                    try:
                        out.append((tag, keys["Type"], float(bits[0]),
                                    float(bits[2]), ashore,
                                    keys.get("LoadoutVariant"), flies,
                                    "Waypoints" in keys))
                    except ValueError:
                        pass
        return out

    def armed(uid, fit=None):
        """Reach with the fit this mission actually placed, not a default.

        `LoadoutVariant` is already on the emitted block; taking the default
        instead would measure a different aeroplane from the one that ships.
        """
        kind_dir, path = unit_file(uid)
        if path is None:
            return 0.0
        if fit is None:
            fit, _why = pick_loadout(uid, path, None)
        return reach(uid, kind_dir, path, fit)

    blue = positions("Taskforce1")
    red = positions("Taskforce2")
    steam = mission["minutes"] / 60.0 * 24.0

    problems = []
    if mission["victory"]["kind"] == "destroy" and blue and red:
        want = {t for r in mission["victory"].get("stations",
                 [mission["victory"].get("station")]) if r
                for t in refs(members, r)}
        targets = [r for r in red if r[0] in want]
        for tag, uid, x, z, _a, _f, _fl, _mv in targets:
            closest = min(
                (math.hypot(x - bx, z - bz) - armed(buid, bfit) - steam, buid)
                for _bt, buid, bx, bz, _ba, bfit, _bfl, _mv in blue)
            if closest[0] > 0:
                problems.append(
                    f"{mission['key']}: victory needs {uid} at {tag} destroyed, "
                    f"and the nearest thing that could do it ({closest[1]}) is "
                    f"{closest[0]:.0f} NM short even after {steam:.0f} NM of "
                    "steaming - this mission cannot be won")
    if problems:
        raise SystemExit("\n  ".join(problems))

    if not (blue and red):
        return None
    gap = min(math.hypot(x - bx, z - bz) for _t, _u, x, z, _a, _f, _fl, _mv in red
              for _bt, _bu, bx, bz, _ba, _bf, _bfl, _mv in blue)
    longest = max([armed(u, f) for _t, u, _x, _z, _a, f, _fl, _mv in red] or [0.0])
    # What red can actually cross: its longest round PLUS what the unit that
    # carries it can move in the mission. An aircraft with an 86 NM missile
    # 93 NM from the convoy is not 7 NM of open water nothing can cross - it
    # is a minute of flight. 300 kn is a conservative cruise; ships get the
    # same 24 kn the rest of the file uses; a land launcher gets nothing.
    def transit(ashore, flies, moves=False):
        if ashore:
            # A land unit with Waypoints drives (eight native sections do);
            # one without stays where it is put.
            return mission["minutes"] / 60.0 * TRANSIT["LandUnit"] if moves else 0.0
        return mission["minutes"] / 60.0 * (300.0 if flies else 24.0)
    short = min([min(math.hypot(x - bx, z - bz) for _bt, _bu, bx, bz, _ba, _bf, _bfl, _bmv in blue)
                 - armed(u, f) - transit(a, fl, mv)
                 for _t, u, x, z, a, f, fl, mv in red] or [0.0])
    # The standoff rule is about an engagement the player is dropped into
    # without a say, which happens at sea and in the air. Two ground forces
    # in contact ashore is not that - it is the scenario - so a land-on-land
    # pair does not count toward it.
    afloat = [math.hypot(x - bx, z - bz)
              for _t, _u, x, z, ashore, _f, _fl, _mv in red
              for _bt, _bu, bx, bz, bashore, _bf, _bfl, _mv in blue
              if not (ashore and bashore)]

    budget = ROLE_BUDGET[mission["role"]]
    if budget.get("contact") is not None and short > budget["contact"]:
        REACH_PROBLEMS.append(
            f"{mission['key']}: a {mission['role']} mission, and the red force "
            f"spawns {gap:.0f} NM from the nearest blue unit; even the unit "
            f"that gets closest, its longest round plus what it can move in "
            f"{mission['minutes']} minutes, is {short:.0f} NM short. Those "
            "hulls are scenery")
    if budget.get("standoff") and afloat and min(afloat) < budget["standoff"]:
        REACH_PROBLEMS.append(
            f"{mission['key']}: a {mission['role']} mission opens with red "
            f"{min(afloat):.0f} NM from blue, inside the "
            f"{budget['standoff']} NM this "
            "role is written around. An engagement the player is already "
            "inside is not one they decided to have")
    return gap, longest


def check_pacing(mission, placed):
    role = mission.get("role")
    if not role:
        raise SystemExit(f"{mission['key']}: no role - every mission declares "
                         "its place in the escalation curve")
    budget = ROLE_BUDGET.get(role)
    if budget is None:
        raise SystemExit(f"{mission['key']}: unknown role {role!r}")
    red = [keys["Type"] for family, entries in placed.items()
           if family.startswith("Taskforce2") for _t, keys, _n, _x in entries]
    fighting = [u for u in red if is_combat(u)]
    n = len(fighting)
    if "max_combat" in budget and n > budget["max_combat"]:
        raise SystemExit(
            f"{mission['key']}: a {role} mission may field at most "
            f"{budget['max_combat']} red combat units and has {n} "
            f"({', '.join(sorted(set(fighting)))}). Either cut the opposition "
            "or change the mission's role.")
    if "min_combat" in budget and n < budget["min_combat"]:
        raise SystemExit(
            f"{mission['key']}: a {role} mission needs at least "
            f"{budget['min_combat']} red combat units and has {n}. A fleet "
            "action that is not one should be re-roled.")
    return n


def check_coast_geometry(mission, placer):
    """On a coastline-proved mission, every trigger area sits on water too.

    solve_arrival() walks a bearing until the box is reachable; on a coast it
    can walk into Tasmania. The authored areas - a stage over a rig, an
    arrival objective's own point - get the same check.
    """
    if not isinstance(placer, CoastPlacer):
        return
    key = mission["key"]
    v = mission.get("victory", {})
    if v.get("kind") == "arrive" and v.get("at"):
        placer.point(v["at"], f"{key} arrival box")
    for extra in v.get("also", []):
        if extra.get("at"):
            placer.point(extra["at"], f"{key} arrival box (also)")
    stage = v.get("after")
    if stage and stage.get("kind") == "area" and stage.get("at"):
        placer.point(stage["at"], f"{key} stage area")
    for oid, how in mission.get("resolve", {}).items():
        if isinstance(how, tuple) and how[0] == "arrive":
            placer.point(how[2], f"{key} {oid} arrival")


def check_geometry(mission, placed, members):
    """An arrival objective must be neither already met nor impossible.

    Both failure modes shipped: O01's search helicopter started 13 NM inside
    its own 20 NM success circle, and SW02 asked 13-knot merchants to cover
    220 NM in 75 minutes. Nothing else in the build could see either.

    The test is on the units the condition actually needs. "Three of four
    arrive" is met by the nearest three, so requiring the fourth to be able to
    reach the box would reject a perfectly sound objective - and, symmetrically,
    the objective is only already-met if min_units of them start inside.
    """
    victory = mission["victory"]
    if victory["kind"] != "arrive":
        return
    at, radius = victory["at"], victory.get("radius", 20)
    centre = mission["centre"]
    wanted = (list(victory["units"]) if victory.get("units")
              else [victory["station"]])
    tags = {t for r in wanted for t in refs(members, r)}
    minimum = victory.get("min_units", len(tags))

    found = []
    for family, entries in placed.items():
        for tag, keys, _n, _x in entries:
            if tag not in tags:
                continue
            x, _alt, z = keys["RelativePositionInNM"].split(",")
            here = (centre[0] + float(z) / 60.0, centre[1] + float(x) / 60.0)
            found.append((nm_between(here, at), tag, family))
    found.sort()

    inside = [t for d, t, _f in found if d < radius]
    if len(inside) >= minimum:
        raise SystemExit(
            f"{mission['key']}: {len(inside)} of the {minimum} units the "
            f"arrival condition needs start inside its {radius} NM circle "
            f"({', '.join(inside)}) - the objective is met at spawn")
    for d, tag, family in found[:minimum]:
        speed = transit_of(tag, placed)
        reach = mission["minutes"] / 60.0 * speed * 0.75
        if d - radius > reach:
            raise SystemExit(
                f"{mission['key']}: {tag} is one of the {minimum} units the "
                f"arrival condition needs and must cover {d - radius:.0f} NM; "
                f"{mission['minutes']} minutes at a conservative {speed:.0f} kn "
                f"buys {reach:.0f} NM. Move the box or lengthen the mission.")


def message_texts(mission):
    """Every in-game message body and intel text this mission writes, as
    (where, text). The builder puts its own 'Title|' in front of a message;
    the text after it must not add another '|'. The game reads a message as
    Title|Body|Button - its own missions end theirs '|Exit mission' and
    '|Start mission' - so a second pipe turns the rest of the sentence into
    the button label. Intel text is shown by Action_Taskforce1_Intel, and
    no mission in the game, the repo or its mods puts a '|' in one."""
    out = [(k, mission[k]) for k in ("brief", "win", "lose", "timeout")
           if mission.get(k)]
    after = mission.get("victory", {}).get("after", {})
    if after.get("lost"):
        out.append(("victory.after.lost (stage lost)", after["lost"]))
    if after.get("intel"):
        out.append(("victory.after.intel (stage intel)", after["intel"]))
    for i, deny in enumerate(mission.get("denied", []), 1):
        out.append((f"denied[{i}].message", deny["message"]))
    for oid, reward in mission.get("reveals", {}).items():
        out.append((f"reveals[{oid}].intel", reward["intel"]))
    for i, loss in enumerate(mission.get("support_loss", []), 1):
        out.append((f"support_loss[{i}].intel", loss["intel"]))
    for reveal in mission.get("reveal_if", []):
        out.append((f"reveal_if[{reveal['variable']}].intel", reveal["intel"]))
    for flag in mission.get("flags", []):
        if flag.get("intel"):
            out.append((f"flags[{flag['name']}].intel", flag["intel"]))
    for find in mission.get("discoveries", []):
        out.append((f"discoveries[{find['objective']}].intel", find["intel"]))
    return out


def check_message_texts(mission):
    # The mission's name is the title of its start message, so a '|' there
    # shifts the brief into the button field just as one in a body would.
    if "|" in mission["key"]:
        raise SystemExit(
            f"{mission.get('code', mission['num'])} {mission['key']}: '|' in the "
            "mission name, which is the start message's title; the game would "
            "read the rest of the name as the body and the brief as the button.")
    for where, text in message_texts(mission):
        if "|" in text:
            raise SystemExit(
                f"{mission.get('code', mission['num'])} {mission['key']}: '|' in "
                f"{where}. The game splits a message on '|' into title, body and "
                "button, and intel text is not known to accept one; write the "
                "sender as 'SENDER: text'.")


def render(mission, placed, members):
    check_message_texts(mission)
    name = mission_name(mission)
    centre = mission["centre"]
    victory = mission["victory"]
    main = victory["objective"]

    L = ["[Language_en]", f"Name={name}",
         f"Description={ini_text(mission['brief'])}"]
    for oid, text, _spec in mission["objectives"]:
        L.append(f"Objective_{oid}={ini_text(text)}")
    L.append(f"Taskforce1StartMessage=<color=yellow>{mission['key']}</color>|"
             f"{ini_text(mission['brief'])}")
    L.append("Taskforce1VictoryMessage=<color=lime>Operation complete.</color>|"
             f"{ini_text(mission['win'])}")
    L.append("Taskforce1DefeatMessage=<color=red>Operation failed.</color>|"
             f"{ini_text(mission['lose'])}")
    L.append("Taskforce2VictoryMessage=<color=lime>Opposing force prevailed.</color>|"
             f"{ini_text(mission['lose'])}")
    L.append("Taskforce2DefeatMessage=<color=red>Opposing force defeated.</color>|"
             f"{ini_text(mission['win'])}")
    L.append("TimeoutMessage=<color=red>Operational window closed.</color>|"
             f"{ini_text(mission['timeout'])}")
    # Authorised range targets are exempt: a gunnery serial's own target is not
    # a civilian casualty.
    neutral_tags = [tag for family in placed if family.startswith("Neutral")
                    for tag, _k, _n, exempt in placed[family] if not exempt]
    for oid, reward in mission.get("reveals", {}).items():
        L.append(f"{oid}Intel={ini_text(reward['intel'])}")
    for i, loss in enumerate(mission.get("support_loss", []), 1):
        L.append(f"SupportLoss{i}Intel={ini_text(loss['intel'])}")
    if mission.get("victory", {}).get("after", {}).get("intel"):
        L.append(f"StageIntel={ini_text(mission['victory']['after']['intel'])}")
    if mission.get("victory", {}).get("after", {}).get("lost"):
        L.append("StageLostMessage=<color=red>Operation failed.</color>|"
                 + ini_text(mission["victory"]["after"]["lost"]))
    for reveal in mission.get("reveal_if", []):
        L.append(f"{reveal['variable']}Intel={ini_text(reveal['intel'])}")
    for i, deny in enumerate(mission.get("denied", []), 1):
        L.append(f"Denied{i}Message=<color=red>Operation failed.</color>|"
                 + ini_text(deny["message"]))
    for flag in mission.get("flags", []):
        if flag.get("intel"):
            L.append(f"{flag['name']}Intel={ini_text(flag['intel'])}")
    for find in mission.get("discoveries", []):
        L.append(f"{find['objective']}Intel={ini_text(find['intel'])}")
    if neutral_tags:
        L.append("NeutralLossMessage=<color=orange>Neutral contact lost.</color>|"
                 "A protected contact has been destroyed. The operation has "
                 "failed. Preserve the contact and engagement records.")
    for family in FAMILY_ORDER:
        for tag, _keys, unit_name, _x in placed.get(family, []):
            if unit_name and tag != mission.get("_anchor_tag"):
                L.append(f"{tag}NameOverride={unit_name}")
    L.append("")

    d, t = mission["date"], mission["time"]
    L += ["[Environment]", f"Date={d[0]},{d[1]},{d[2]}", f"Time={t[0]},{t[1]}",
          "ConvertTimeToLocal=True", f"SeaState={mission['sea']}",
          f"Clouds={mission['clouds']}", f"WindDirection={mission['wind']}",
          f"MapCenterLatitude={centre[0]}", f"MapCenterLongitude={centre[1]}",
          "LoadBackgroundData=False", ""]

    L += ["[Mission]", f"Difficulty={mission.get('difficulty', 1)}",
          "PlayerTaskforce=Taskforce1", "EnemyTaskforce=Taskforce2",
          f"Taskforce1_Nation={mission['blue_nation']}",
          f"Taskforce2_Nation={mission['red_nation']}"]
    for family in FAMILY_ORDER:
        if placed.get(family):
            L.append(f"{COUNT_KEY[family]}={len(placed[family])}")

    # One formation per station, side AND way of moving. Grouping by station
    # alone put SW05's Seahawk slot in a 0.1 NM Vic with two F-35As: a
    # helicopter and a jet are never one formation, nor is anything that
    # flies with anything afloat. A surfaced submarine keeping company with
    # a ship (SW09's Collins and Stalwart) still is.
    def moves(tag):
        return ("rotary" if "Helicopter" in tag else "fixed" if "Aircraft" in tag
                else "land" if "LandUnit" in tag else "afloat")
    forms = collections.defaultdict(list)
    for station, tags in members.items():
        by_side = collections.defaultdict(list)
        for tag in tags:
            side = ("Taskforce1" if tag.startswith("Taskforce1") else
                    "Taskforce2" if tag.startswith("Taskforce2") else "Neutral")
            by_side[(side, moves(tag))].append(tag)
        for (side, _family), group in by_side.items():
            if len(group) > 1:
                forms[side].append((mission["stations"][station].get("label", station),
                                    group))
    for side, groups in sorted(forms.items()):
        L.append(f"{side}_NumberOfFormations={len(groups)}")
        for i, (label, group) in enumerate(groups, 1):
            shape = "Vic" if ("Aircraft" in group[0] or "Helicopter" in group[0]) else "Loose"
            spacing = "0.1" if shape == "Vic" else "1.5"
            L.append(f"{side}_Formation{i}={','.join(group)}|{label}|{shape}|{spacing}")

    # --- triggers -----------------------------------------------------------
    # Build them first so the count in [Mission] is what actually follows.
    T = []

    def trigger(comment, lines):
        T.append((comment, lines))

    # The fourth field of an objective line is what the game does with that
    # objective if it is still In Progress when the mission ends, so on a
    # defeat every unfinished task would quietly resolve to its default and
    # bank its score. The native answer is to cancel them: `03 Lifeline at the
    # Edge of the World` line 517 ends a defeat with
    # `Action_ObjectivesCancel=DestroySSKs,PetropavlovskMustSurvive,
    # DestroyUSSAG,DestroyUSSSN` - every other objective in the mission,
    # hidden ones included. 45 native triggers do this. The list is derived
    # here rather than authored, because the one thing a hand-written cancel
    # list reliably does is go stale when an objective is added.
    all_objectives = [o[0] for o in mission["objectives"]]

    # The shared exit. Twelve native missions end this way: ONE trigger owns
    # Action_EndMission, it ships Disabled=True, and every outcome trigger
    # sets its verdict and then enables it - `missions/NATO/Charlies.ini`
    # Trigger1, and Gauntlet, and ten more. Two things follow that matter
    # here. Only one EndMission exists, so a defeat cannot be followed by a
    # victory ending the same mission again. And the delay is zero in all ten
    # native uses of the key, which closes the window this campaign used to
    # leave open: a loss landing 40 seconds into a victory's countdown.
    trigger("Mission exit", [
        "Disabled=True", "Condition_Type=Time", "Condition_Time=10",
        "Action_EndMission=True", "Action_EndMissionDelay=0"])
    EXIT = "Action_EnableTriggers=Trigger1"

    def terminal(comment, conditions, *, failed=(), message, victor,
                 completed=(), keep=()):
        named, won = list(failed), list(completed)
        cancel = [o for o in all_objectives
                  if o not in named and o not in won and o not in keep]
        lines = list(conditions) + [
            f"Action_Taskforce1_Message={message}", f"Action_Victory={victor}"]
        if won:
            lines.append(f"Action_ObjectivesCompleted={','.join(won)}")
        if named:
            lines.append(f"Action_ObjectivesFailed={','.join(named)}")
        if cancel:
            lines.append(f"Action_ObjectivesCancel={','.join(cancel)}")
        lines.append(EXIT)
        trigger(comment, lines)

    # On a win, the survival objectives the player held are completed
    # explicitly, the way `03 Lifeline` line 487 completes DefendSupplyShips
    # and PetropavlovskMustSurvive. Positive tasks are not: they are earned by
    # their own triggers or they are not earned.
    # ...but only the ones whose loss ENDS the mission. A protected unit the
    # mission survives losing (SW10's Japanese escorts) has already had its
    # objective failed by its own trigger, and the win line would flip it
    # back to complete on the same debrief. StatusAtMissionEnd=Complete
    # resolves the held case on its own.
    ends = {f["objective"] for f in mission.get("fatal", [])}
    held = [oid for oid, how in mission.get("resolve", {}).items()
            if isinstance(how, tuple) and how[0] in ("protect", "survive")
            and oid in ends]

    deadline = mission["minutes"] * 60          # Condition_Time is SECONDS
    # The clock running out fails the main task and leaves the survival
    # objectives to their own end-status: a carrier that survived the window
    # survived it, whether or not the transports made the box. Cancelling
    # them was telling the player the file contradicts its own rule.
    survivals = [oid for oid, how in mission.get("resolve", {}).items()
                 if isinstance(how, tuple) and how[0] in ("protect", "survive")]
    terminal("Deadline",
             ["Condition_Type=Time", f"Condition_Time={deadline}"],
             failed=[main], message="TimeoutMessage", victor="Taskforce2",
             keep=survivals)
    trigger("Start message", [
        "Condition_Type=Time", "Condition_Time=1",
        "Action_Taskforce1_Message=Taskforce1StartMessage"])

    if victory["kind"] == "arrive":
        win_units = ([tag for r in victory["units"] for tag in refs(members, r)]
                     if victory.get("units") else refs(members, victory["station"]))
        cond = area_condition(1, centre, victory["at"], victory.get("radius", 20),
                              win_units, victory.get("min_units", len(win_units)))
    else:
        win_units = [tag for st in victory["stations"] for tag in refs(members, st)]
        cond = destroyed_condition(1, win_units, victory.get("min_units", len(win_units)))
    if not win_units:
        raise SystemExit(f"{mission['key']}: the victory condition names no unit")
    expr, n = "<Condition1>", 1
    for extra in victory.get("also", []):
        n += 1
        cond += also_condition(mission, n, extra, members)
        expr += f" AND <Condition{n}>"
    win_lines = [f"ConditionsCompleted={expr}",
                 "Action_Taskforce1_Message=Taskforce1VictoryMessage",
                 "Action_Taskforce2_Message=Taskforce2DefeatMessage",
                 "Action_Victory=Taskforce1",
                 "Action_ObjectivesCompleted="
                 + ",".join([main] + [o for o in held if o != main])]
    if victory.get("sets"):
        win_lines.append(f"Action_VariableSet={victory['sets']},True")
    win_lines.append(EXIT)

    # A win the player has to EARN. Two missions scored their arrival with
    # nothing asked of the player first: SW03 could be won by flying straight
    # south from spawn and never going near the platform it is about, and
    # SW04's contact drove itself into the box while the player watched. So
    # the arrival trigger can ship Disabled=True behind a stage - the lifters
    # over the rig, the contact classified - and only the stage enables it.
    # Both halves are stock: Disabled=True + Action_EnableTriggers is the
    # shared-exit pattern twelve native missions use, UnitsInTheArea and
    # UnitClassified are the conditions the campaign already leans on. The
    # stage is a trigger, so it can also carry the intel line that tells the
    # player the first half is done.
    stage = victory.get("after")
    per_unit = bool(stage and stage.get("per_unit"))
    if stage:
        s_refs = ([stage["units"]] if isinstance(stage["units"], str)
                  else list(stage["units"]))
        s_units = [tag for r in s_refs for tag in refs(members, r)]
        if not s_units:
            raise SystemExit(f"{mission['key']}: the victory stage names no unit")
        s_at = None
        if stage["kind"] == "area":
            if "at_unit" in stage:
                # the PLACED position of a unit - a snapped rig is where it
                # was snapped to, not where the station was authored
                ref = refs(members, stage["at_unit"])[0]
                for _fam, entries in placed.items():
                    for tag, keys, _n, _x in entries:
                        if tag == ref:
                            bx, _a, bz = keys["RelativePositionInNM"].split(",")
                            s_at = (centre[0] + float(bz) / 60.0,
                                    centre[1] + float(bx) / 60.0)
            else:
                s_at = stage["at"]

        def stage_conditions(units):
            if stage["kind"] == "area":
                c = area_condition(1, centre, s_at, stage.get("radius", 3),
                                   units, stage.get("min_units", 1))
                expr = "<Condition1>"
                if stage.get("after_minutes"):
                    # "Still there when the clock says so." The area test
                    # and a Time condition in one trigger, on units that
                    # START inside the area - the exact shape of `03 Lifeline
                    # at the Edge of the World` Trigger8 (<Condition1> AND
                    # <Condition2>, two vessels 1.6 and 2.4 NM inside a 10 NM
                    # area, Time=120). It is the nearest thing the engine has
                    # to a dwell, and SW09's service window is built on it:
                    # leave the box before the window closes and the stage
                    # never fires.
                    c += ["Condition_Condition2_Type=Time",
                          f"Condition_Condition2_Time={stage['after_minutes'] * 60}"]
                    expr += " AND <Condition2>"
                c.append(f"ConditionsCompleted={expr}")
            elif stage["kind"] == "classify":
                c = ["Condition_Type=UnitClassified",
                     "Condition_Taskforce=Taskforce1",
                     f"Condition_Units={','.join(units)}",
                     f"Condition_MinimumUnits={stage.get('min_units', 1)}"]
            else:
                raise SystemExit(f"{mission['key']}: unknown victory stage "
                                 f"{stage['kind']!r}")
            if stage.get("intel"):
                c.append("Action_Taskforce1_Intel=StageIntel")
            if stage.get("sets"):
                c.append(f"Action_VariableSet={stage['sets']},True")
            return c

        if per_unit:
            # One chain PER AIRCRAFT: the lifter that reached the platform is
            # the lifter that has to reach the withdrawal line, and losing it
            # after the pickup loses the people aboard. Stage_i enables its
            # own Win_i and Lost_i (a comma list, as seven native triggers
            # do); the other aircraft's chain stays armed, so a second lifter
            # can still fly the rescue after the first is lost on the way in.
            for tag in s_units:
                stage_no = len(T) + 1
                s_cond = stage_conditions([tag])
                s_cond.append(f"Action_EnableTriggers=Trigger{stage_no + 1},"
                              f"Trigger{stage_no + 2}")
                trigger(f"Stage {tag}", s_cond)
                w_cond = area_condition(1, centre, victory["at"],
                                        victory.get("radius", 20), [tag], 1)
                w_expr, wn = "<Condition1>", 1
                for extra in victory.get("also", []):
                    wn += 1
                    w_cond += also_condition(mission, wn, extra, members)
                    w_expr += f" AND <Condition{wn}>"
                w_lines = [x for x in win_lines if not x.startswith("ConditionsCompleted=")]
                trigger(f"Objective met by {tag}",
                        ["Disabled=True"] + w_cond
                        + [f"ConditionsCompleted={w_expr}"] + w_lines)
                terminal(f"{tag} lost after the pickup",
                         ["Disabled=True"] + destroyed_condition(1, [tag], 1)
                         + ["ConditionsCompleted=<Condition1>"],
                         failed=[main],
                         message="StageLostMessage" if stage.get("lost") else "Taskforce1DefeatMessage",
                         victor="Taskforce2")
        else:
            met_no = len(T) + 2          # this stage trigger, then the arrival
            s_cond = stage_conditions(s_units)
            s_cond.append(f"Action_EnableTriggers=Trigger{met_no}")
            trigger("Stage", s_cond)
            cond.insert(0, "Disabled=True")
    if not per_unit:
        trigger("Objective met", cond + win_lines)

    # Every objective needs a predicate. "victory" is completed by the trigger
    # above; everything else gets its own, and an objective with no resolver
    # fails the build - twenty of them used to sit there resolving to nothing.
    resolve = mission["resolve"]

    def own_units(what, station_refs):
        """The player's units at these stations, for a predicate on what the
        enemy knows about them. A red or neutral unit here is an authoring
        mistake the engine would accept and never fire on."""
        units = [t for r in station_refs if isinstance(r, str)
                 for t in refs(members, r)]
        foreign = [t for t in units if not t.startswith("Taskforce1")]
        if not units or foreign:
            raise SystemExit(
                f"{mission['key']}: {what} is scored on the enemy classifying "
                f"the player's units, and {list(station_refs)} places "
                f"{', '.join(foreign) if foreign else 'nothing'}")
        return units

    for oid, _text, spec in mission["objectives"]:
        if oid not in resolve:
            raise SystemExit(f"{mission['key']}: objective {oid} has no resolver")
        how = resolve[oid]
        if how in ("victory", "neutral"):
            continue
        kind = how[0]
        if kind == "protect":
            units = [tag for r in how[1:] if isinstance(r, str)
                     for tag in refs(members, r)]
            least = next((x for x in how[1:] if isinstance(x, int)), 1)
            trigger(f"{oid} lost", destroyed_condition(1, units, least)
                    + ["ConditionsCompleted=<Condition1>",
                       f"Action_ObjectivesFailed={oid}"])
        elif kind == "survive":
            units = [tag for r in how[1:] for tag in refs(members, r)]
            trigger(f"{oid} wiped out", destroyed_condition(1, units, len(units))
                    + ["ConditionsCompleted=<Condition1>",
                       f"Action_ObjectivesFailed={oid}"])
        elif kind == "spare":
            # Restraint, scored on the thing the text names: destroy any of
            # these and the objective fails. It completes by its own
            # end-status if the player never did. D4's "restraint" used to
            # be "not all five red fighters shot down".
            units = [tag for r in how[1:] for tag in refs(members, r)]
            trigger(f"{oid} broken", destroyed_condition(1, units, 1)
                    + ["ConditionsCompleted=<Condition1>",
                       f"Action_ObjectivesFailed={oid}"])
        elif kind == "destroy":
            units = [tag for tag in refs(members, how[1])]
            trigger(f"{oid} met", destroyed_condition(1, units, how[2])
                    + ["ConditionsCompleted=<Condition1>",
                       f"Action_ObjectivesCompleted={oid}"])
        elif kind == "arrive":
            units = [tag for tag in refs(members, how[1])]
            trigger(f"{oid} met",
                    area_condition(1, centre, how[2], how[3], units, how[4])
                    + ["ConditionsCompleted=<Condition1>",
                       f"Action_ObjectivesCompleted={oid}"])
        elif kind == "ammo":
            # "Bring the frigate out with rounds left" used to be scored as
            # "the frigate survives" - nothing ever looked at the magazine.
            # UnitsAreOutOfAmmo is stock (03 Lifeline uses it twice, on
            # wp_ss-n-19 and wp_ss-n-12) and names the round it watches. The
            # objective is not in `held`, so on a win it resolves by its own
            # end-status unless this trigger has already failed it.
            units = refs(members, how[1])
            trigger(f"{oid} spent",
                    ["Condition_Condition1_Type=UnitsAreOutOfAmmo",
                     f"Condition_Condition1_Units={','.join(units)}",
                     f"Condition_Condition1_Ammunition={how[2]}",
                     "ConditionsCompleted=<Condition1>",
                     f"Action_ObjectivesFailed={oid}"])
        elif kind == "classify":
            # The reconnaissance decision, in the engine's own vocabulary:
            # Condition_Type=UnitClassified fires when the player's side has
            # classified the named contacts, and the pay-off is a permanent
            # reveal of what they were screening. Both halves are stock -
            # UnitClassified in missions/Warsaw Pact/Breakthrough.ini, the
            # reveal pair in campaigns/linear-campaign-proto-1/missions/
            # 03 Mind the Gap.ini. What it cannot do is model a partial or
            # decaying picture: a contact is classified or it is not.
            # One station ref, or a list of them: Turning North's network
            # objective names the carrier, the replenishment ship and the
            # collector in a formation of six, not any three of the six.
            units = [t for r in ([how[1]] if isinstance(how[1], str) else how[1])
                     for t in refs(members, r)]
            lines = ["Condition_Type=UnitClassified",
                     "Condition_Taskforce=Taskforce1",
                     f"Condition_Units={','.join(units)}",
                     f"Condition_MinimumUnits={how[2]}",
                     f"Action_ObjectivesCompleted={oid}"]
            if how[3] if len(how) > 3 else None:
                lines.append(f"Action_VariableSet={how[3]},True")
            reward = mission.get("reveals", {}).get(oid)
            if reward:
                revealed = [t for r in reward["units"] for t in refs(members, r)]
                lines += [f"Action_Taskforce1_Intel={oid}Intel",
                          "Action_UnitRevealToTaskforce=Taskforce1|"
                          + reward.get("level", "Classify"),
                          f"Action_UnitRevealTime={reward.get('seconds', -1)}",
                          f"Action_Units={','.join(revealed)}"]
            trigger(f"{oid} classified", lines)
        elif kind == "unseen":
            # The same condition turned round: the objective fails the moment
            # the ENEMY classifies any of these player units. It measures
            # classification, not detection - a boat the patrol holds as an
            # unknown contact is still unseen. It only ever fails, so it
            # completes by its own end-status, as `spare` does.
            units = own_units(f"objective {oid}", how[1:])
            trigger(f"{oid} classified by the enemy",
                    classified_condition(1, units, 1, "Taskforce2")
                    + ["ConditionsCompleted=<Condition1>",
                       f"Action_ObjectivesFailed={oid}"])
        else:
            raise SystemExit(f"{mission['key']}: objective {oid} has an unknown "
                             f"resolver {how!r}")

    # Terminal states end the mission and cancel the other side's objective, so
    # a defeat cannot be followed by a victory action. Whether the engine gives
    # one precedence inside a single update is still untested.
    # One terminal trigger per protected objective, naming ONLY the units that
    # objective is about. A single list with a single objective id made every
    # loss fail the same objective: SW09 reported Collins lost when the ship
    # that sank was a freighter with no objective of its own, and SW07 blamed
    # the tanker when a Rhino went down. The units come from the objective's
    # own resolver, so the trigger that ends the mission and the trigger that
    # marks the objective failed can never disagree about what they watch.
    # A fatal entry of kind "unseen" is the same terminal on a different
    # condition: the enemy classifying the named player units, in the shape
    # classified_condition() copies from stock. Its units come from an
    # `unseen` resolver the way a loss's come from `protect`/`survive`.
    for entry in mission.get("fatal", []):
        oid = entry["objective"]
        if oid not in {o[0] for o in mission["objectives"]}:
            raise SystemExit(f"{mission['key']}: {oid} ends the mission but is "
                             "not one of its objectives")
        fkind = entry.get("kind", "destroyed")
        if fkind not in FATAL_SOURCES:
            raise SystemExit(f"{mission['key']}: {oid} ends the mission on kind "
                             f"{fkind!r}; the builder knows "
                             f"{', '.join(FATAL_SOURCES)}")
        watch = entry.get("units")
        least = entry.get("minimum", 1)
        if watch is None:
            how = mission["resolve"].get(oid)
            if not (isinstance(how, tuple) and how[0] in FATAL_SOURCES[fkind]):
                raise SystemExit(
                    f"{mission['key']}: {oid} ends the mission but names no "
                    f"units and its resolver is {how!r}, which supplies none - "
                    "give the fatal entry its own units")
            watch = list(how[1:])
            if how[0] == "survive":
                least = None            # all of them
        # When a fatal entry names its own units AND the objective has a
        # resolver that watches units too, the two must be the same set. They
        # disagreed in O1 - the trigger watched the ship, the objective said
        # helicopter - and nothing noticed because each was internally fine.
        how = mission["resolve"].get(oid)
        if entry.get("units") and isinstance(how, tuple) and how[0] in FATAL_SOURCES[fkind]:
            mine = {t for r in watch for t in refs(members, r)}
            theirs = {t for r in how[1:] if isinstance(r, str)
                      for t in refs(members, r)}
            # A fatal entry may name a SUBSET of the objective's units - the one
            # hull whose loss alone ends the mission while the objective
            # tolerates losing another - but never a ship the objective is
            # not about.
            if not mine <= theirs:
                raise SystemExit(
                    f"{mission['key']}: {oid} ends the mission when "
                    f"{sorted(mine)} is "
                    f"{'classified' if fkind == 'unseen' else 'lost'}, but the objective itself is "
                    f"about {sorted(theirs)}. One of them is reporting the "
                    "wrong ship")
        if fkind == "unseen":
            watched = own_units(f"the fatal entry on {oid}", watch)
            terminal(f"{oid} classified by the enemy - mission over",
                     classified_condition(1, watched, least, "Taskforce2")
                     + ["ConditionsCompleted=<Condition1>"],
                     failed=[oid], message="Taskforce1DefeatMessage",
                     victor="Taskforce2")
            continue
        watched = [tag for r in watch for tag in refs(members, r)]
        if not watched:
            raise SystemExit(f"{mission['key']}: {oid} ends the mission but "
                             f"{watch} matches nothing placed")
        terminal(f"{oid} lost - mission over",
                 destroyed_condition(1, watched, least or len(watched))
                 + ["ConditionsCompleted=<Condition1>"],
                 failed=[oid], message="Taskforce1DefeatMessage",
                 victor="Taskforce2")

    # A race the player can lose: an ENEMY unit reaching a place ends the
    # mission. Stock's own shape - 01 Raid on Okinawa, "Assault unit reaches
    # Kume - player defeat": UnitsInTheArea on a Taskforce2 unit, the area
    # shown to both sides, EndMission and Victory=Taskforce2.
    for i, deny in enumerate(mission.get("denied", []), 1):
        oid = deny["objective"]
        if oid not in {o[0] for o in mission["objectives"]}:
            raise SystemExit(f"{mission['key']}: denied names objective {oid}, "
                             "which the mission does not have")
        units = [t for r in deny["units"] for t in refs(members, r)]
        if not units or not all(u.startswith("Taskforce2") for u in units):
            raise SystemExit(f"{mission['key']}: a denied race is lost to "
                             f"enemy units; {deny['units']} places {units}")
        terminal(f"{oid} denied",
                 area_condition(1, centre, deny["at"], deny["radius"], units,
                                deny.get("min_units", 1), side="Both")
                 + ["ConditionsCompleted=<Condition1>"],
                 failed=[oid], message=f"Denied{i}Message",
                 victor="Taskforce2")

    # Losing a support asset costs something the player can read at the time,
    # and - where `sets` names a campaign flag - something a later mission
    # reads back. Two mechanisms carry that: Task Force Mode's own persistence
    # (a dead ship is gone and must be re-bought at its roster price) and
    # [CampaignVariables], which SW02 writes and SW09 spawns against.
    for i, loss in enumerate(mission.get("support_loss", []), 1):
        units = [t for r in loss["units"] for t in refs(members, r)]
        trigger(f"Support lost: {loss['asset']}",
                destroyed_condition(1, units, 1)
                + ["ConditionsCompleted=<Condition1>",
                   f"Action_Taskforce1_Intel=SupportLoss{i}Intel"]
                + ([f"Action_ObjectivesFailed={loss['objective']}"]
                   if loss.get("objective") else [])
                + ([f"Action_VariableSet={loss['sets']},True"]
                   if loss.get("sets") else []))

    # Campaign flags this mission writes for later ones. Only the IsFalse form
    # of SpawnByVariableAND appears in the native export, so a flag always
    # names something that HAPPENED and later missions spawn the content that
    # exists when it did not. Inventing IsTrue would be inventing a mechanism.
    for flag in mission.get("flags", []):
        units = [t for r in flag["units"] for t in refs(members, r)]
        trigger(f"Flag: {flag['name']}",
                destroyed_condition(1, units, flag.get("minimum", 1))
                + ["ConditionsCompleted=<Condition1>",
                   f"Action_VariableSet={flag['name']},True"]
                + ([f"Action_Taskforce1_Intel={flag['name']}Intel"]
                   if flag.get("intel") else []))

    # Reconnaissance that produces new tasking. The stock shape is a report
    # trigger that ships `Disabled=True`, an earlier detection whose trigger
    # carries `Action_EnableTriggers`, and `Action_ObjectivesUnHide` on an
    # objective flagged `Hidden` in [Taskforce1_Objectives] - Triggers 8 and
    # 10 of strike-group-molniya `03 Lifeline at the Edge of the World`, whose
    # objectives block reads `DestroyUSSAG=20,-20,Complete,Hidden`.
    #
    # The report's own Condition_Time is measured from mission start there,
    # not from the moment it is enabled: stock gives it the same 120 seconds
    # the enabling trigger already required, so it fires as soon as it is
    # switched on. That reading is what `seconds` means here, and it is the
    # one thing in this block that a play test could still overturn.
    for find in mission.get("discoveries", []):
        hidden = find["objective"]
        specs = {o[0]: o[2] for o in mission["objectives"]}
        if hidden not in specs:
            raise SystemExit(f"{mission['key']}: discovery unhides {hidden}, "
                             "which is not one of this mission's objectives")
        if "Hidden" not in specs[hidden].split(","):
            raise SystemExit(
                f"{mission['key']}: {hidden} is unhidden by a discovery but is "
                f"not flagged Hidden ({specs[hidden]!r}), so it is on the "
                "player's list from the start and the reveal means nothing")
        # The task's own completion trigger ships disabled as well, and the
        # report is what switches it on. Otherwise it is live from mission
        # start: identify the shuttle before finding the escorts and the
        # objective completes silently, then a report arrives saying nobody
        # has put a name on it. Native accepts that race - `10 Vengeance at
        # Luzon`'s DestroySlava has one UnHide and one Completed trigger and
        # nothing between them - but it costs nothing to close, and it uses
        # the same Disabled/EnableTriggers pair the discovery already needs.
        earner = [lines for comment, lines in T
                  if comment.startswith(f"{hidden} ")]
        if not earner:
            raise SystemExit(f"{mission['key']}: {hidden} is discovered but "
                             "has no trigger that completes it")
        earner[0].insert(0, "Disabled=True")
        earns = 1 + next(i for i, (_c, lines) in enumerate(T)
                         if lines is earner[0])
        trigger(f"Report unhides {hidden}", [
            "Disabled=True",
            "Condition_Type=Time",
            f"Condition_Time={find.get('seconds', 120)}",
            f"Action_Taskforce1_Intel={hidden}Intel",
            f"Action_ObjectivesUnHide={hidden}",
            f"Action_EnableTriggers=Trigger{earns}"])
        report = len(T)
        wanted = f"{find['after']} classified"
        enabling = [lines for comment, lines in T if comment == wanted]
        if not enabling:
            raise SystemExit(
                f"{mission['key']}: discovery waits on {find['after']!r}, "
                "which is not a classify objective in this mission")
        enabling[0].append(f"Action_EnableTriggers=Trigger{report}")

    # force_loss=False: a mission whose player force is batteries on land
    # (D5) is not lost when its last aircraft is; its own fatal rule says
    # what losing it means.
    # With no ships, the force is whatever flies; stock lists several types
    # in one HasNoUnitsOfType (`Condition_UnitType=Vessel,Submarine,Aircraft`),
    # so a helicopter left in the air is still a force.
    flying = [u for u, fam in (("Aircraft", "Taskforce1Aircraft"),
                               ("Helicopter", "Taskforce1Helicopter"))
              if placed.get(fam)]
    if mission.get("force_loss", True) and (placed.get("Taskforce1Vessel") or flying):
        terminal("Player force gone", [
            "Condition_Type=HasNoUnitsOfType", "Condition_Taskforce=Taskforce1",
            "Condition_UnitType=" + ("Vessel" if placed.get("Taskforce1Vessel")
                                     else ",".join(flying))],
            failed=[main], message="Taskforce1DefeatMessage",
            victor="Taskforce2")
    if neutral_tags:
        # A `spare` objective on a neutral hull (Cook Strait's ferries, the
        # Bass Strait platforms, the withdrawing group under the ceasefire)
        # is scored by its own trigger in the same tick this terminal
        # fires; cancelling it here would take that score back. It keeps
        # its own result, failed by its trigger or Complete at the end.
        spared = [oid for oid, how in mission.get("resolve", {}).items()
                  if isinstance(how, tuple) and how[0] == "spare"
                  and any(t in neutral_tags for r in how[1:] for t in refs(members, r))]
        terminal("Neutral harmed",
                 destroyed_condition(1, neutral_tags,
                                     mission.get("neutral_limit", 1))
                 + ["ConditionsCompleted=<Condition1>"],
                 failed=[mission["neutral_objective"]],
                 message="NeutralLossMessage", victor="Taskforce2",
                 keep=spared)

    # A saved result from an earlier operation, read here. 09 Shadows off
    # Palawan reveals the missile sites this way when 08A's recon completed.
    for reveal in mission.get("reveal_if", []):
        revealed = [t for r in reveal["units"] for t in refs(members, r)]
        trigger(f"Reveal from {reveal['variable']}", [
            "Condition_Condition1_Type=VariableCheck",
            f"Condition_Condition1_Variable={reveal['variable']}",
            "ConditionsCompleted=<Condition1>",
            f"Action_Taskforce1_Intel={reveal['variable']}Intel",
            "Action_UnitRevealToTaskforce=Taskforce1|"
            + reveal.get("level", "Identify"),
            "Action_UnitRevealTime=-1",
            f"Action_Units={','.join(revealed)}"])

    # A unit sitting in an air-tasking slot is a placeholder the player fills
    # from the aircraft they own, so binding a trigger to it is binding an
    # objective to something that may not be there. Across all 20 slot-tagged
    # sections in the native campaign, ZERO are named by any trigger - and the
    # one native mission that does bind Taskforce1Aircraft1 and 2 to triggers
    # (04 Sunda Strait) grants them with JoinTaskForce instead. That invariant
    # is enforced here.
    slotted = {tag for family, entries in placed.items()
               if family.startswith("Taskforce1")
               for tag, keys, _n, _x in entries
               if "TaskForceModeAirTaskingSlot" in keys}
    bound = {u.strip() for _c, lines in T for line in lines
             for key, _, value in [line.partition("=")]
             if key.endswith("_Units") or key == "Action_Units"
             for u in value.split(",")}
    clash = sorted(slotted & bound)
    if clash:
        by_tag = {tag: keys["Type"] for family, entries in placed.items()
                  for tag, keys, _n, _x in entries}
        raise SystemExit(
            f"{mission['key']}: " + "; ".join(
                f"{by_tag[t]} at {t} is an air-tasking placeholder and a "
                "trigger depends on it - grant it with join=True instead"
                for t in clash))

    L.append(f"NumberOfTriggers={len(T)}")
    L.append("")

    for family in FAMILY_ORDER:
        for tag, keys, _n, _x in placed.get(family, []):
            L.append(block(tag, keys))
            L.append("")

    # An objective may end Fail if something can COMPLETE it before the end:
    # the victory trigger, or its own classify/arrive/destroy resolver. Then
    # "still open at the win" means "never done", and the failure score is
    # the price of not doing it - which is what SW06's reconnaissance
    # decision needs to cost anything. A protect/neutral objective only ever
    # fails, so Fail-at-end on one of those would fail it on a clean win.
    resolved = {mission["victory"]["objective"]} | {
        oid for oid, how in mission.get("resolve", {}).items()
        if isinstance(how, tuple) and how[0] in ("classify", "arrive", "destroy")}
    L.append("[Taskforce1_Objectives]")
    L.append("#ID=CompletedScore,FailedScore,StatusAtMissionEnd")
    for oid, _text, spec in mission["objectives"]:
        status = spec.split(",")[2] if len(spec.split(",")) > 2 else ""
        if status == "Fail" and oid not in resolved:
            raise SystemExit(
                f"{mission['key']}: objective {oid} ends Fail but only the "
                "victory objective is completed by a terminal trigger")
        L.append(f"{oid}={spec}")
    L.append("")

    # Variables this mission WRITES are declared here with their default, the
    # way 07A and 08A declare theirs. A mission that only reads one does not
    # declare it.
    declared = sorted(mission.get("declares", []))
    if declared:
        L.append("[CampaignVariables]")
        for var in declared:
            L.append(f"{var}=False")
        L.append("")

    for i, (comment, lines) in enumerate(T, 1):
        L.append(f"[Trigger{i}]  #{comment}")
        L.append(f"Name={comment}")
        L += lines
        L.append("")
    return name, "\n".join(L) + "\n"


# --- the campaign, its events and its briefings ------------------------------

EVENT_XML = """<Page xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  d:DesignWidth="1920" d:DesignHeight="1080"
  xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" mc:Ignorable="d">
  <Viewbox>
    <Border Background="#F2EFE6" Width="1100" Height="760" Padding="60"
            TextElement.FontFamily="Times New Roman" TextElement.Foreground="Black">
      <StackPanel Orientation="Vertical">
        <Rectangle HorizontalAlignment="Stretch" Height="4" Fill="Black"/>
        <TextBlock Text="{dateline}" Margin="0,14,0,14" FontSize="26"/>
        <Rectangle HorizontalAlignment="Stretch" Height="4" Fill="Black"/>
        <TextBlock Text="{headline}" FontWeight="Bold" FontSize="54"
                   TextWrapping="Wrap" TextAlignment="Center" Margin="0,26,0,26"/>
        <Rectangle HorizontalAlignment="Stretch" Height="2" Fill="Black"/>
{paragraphs}
      </StackPanel>
    </Border>
  </Viewbox>
</Page>
"""

BRIEF_XML = """<ScrollViewer xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" \
VerticalScrollBarVisibility="Auto"><StackPanel Margin="24">{body}</StackPanel></ScrollViewer>
"""


def xml_escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;"))


def event_page(event):
    """The story beat, as the shipped campaigns do it: one bound image.

    `19850708_breakingnews_event.xml` in Pacific Strike is a Viewbox holding a
    single `<Image Source="{Binding Assets[...]}"/>`, resolved against the
    entry's `AssetsPath_en`. The dispatch is typeset into that PNG by
    make_art, from the same text this page used to lay out by hand - so the
    words are set properly instead of being stacked TextBlocks, and there is
    one place they come from.
    """
    return (
        '<Viewbox xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n'
        '  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n'
        '  Margin="0" HorizontalAlignment="Center" VerticalAlignment="Center">\n'
        '    <StackPanel>\n'
        f'        <Image Source="{{Binding Assets[{event["file"]}_image]}}"/>\n'
        '    </StackPanel>\n'
        '</Viewbox>\n')


def briefing_page(mission):
    parts = []

    def section(head, text):
        parts.append(f'<TextBlock FontSize="20" Margin="0,14,0,6" '
                     f'Text="{xml_escape(head)}"/>')
        for paragraph in re.split(r"(?:\\n\\n|\n\s*\n)", text):
            if paragraph.strip():
                # a task bullet sits closer to the next one than prose does
                gap = "4" if paragraph.strip().startswith("\u2022") else "10"
                parts.append(f'<TextBlock FontSize="16" TextWrapping="Wrap" '
                             f'Margin="0,0,0,{gap}" '
                             f'Text="{xml_escape(paragraph.strip())}"/>')

    section("SITUATION", mission["brief"])
    # Who is speaking, and what they actually want. The bible wrote seven
    # recurring people and asked for "short radio traffic, log extracts and
    # debriefs"; for a year not one of them reached a briefing. INTENT is
    # where the campaign's thesis - identify first, protect the transports,
    # do not spend what you cannot replace - is said in a voice, before every
    # mission, by the person whose problem it is.
    if mission.get("sender"):
        section("FROM", mission["sender"])
    if mission.get("intent"):
        section("COMMANDER'S INTENT", mission["intent"])
    section("TASK", "\n\n".join(f"• {text}"
                                for _oid, text, _s in mission["objectives"]))
    section("FORCES", mission["forces"])
    section("TIME", f"Complete the assigned task within {mission['minutes']} "
                    "minutes. Command will close the operation at that deadline "
                    "and the main task will be recorded as failed.")
    if any(not u.get("no_neutral_penalty") for u in mission["units"]
           if u["side"] == "neutral"):
        section("RULES OF ENGAGEMENT",
                "All designated neutral contacts are protected. A protected "
                "neutral loss cancels the operation. Identify before you shoot.")
    # Installation and provider details remain in REQUIRED-MODS.txt and the
    # coverage report; the operational briefing contains only the orders.
    return BRIEF_XML.format(body="".join(parts))


ROSTER_SECTION = {"Vessel": "AllowedVessels", "Submarine": "AllowedSubmarines",
                  "Aircraft": "AllowedAircraft", "Helicopter": "AllowedHelicopters",
                  "VTOL": "AllowedAircraft"}


def roster_ini(roster):
    """player_task_force_roster.ini, in the stock file's own syntax.

    Every pick is checked against the file that WINS the load order first: a
    price on a variant the hull no longer offers is a purchase the builder
    would be advertising and the game would refuse. Aircraft go in by squadron,
    ships by variant, and a submarine goes in AllowedSubmarines because its
    UnitType says so - not because of what its filename looks like.
    """
    by_section, problems, credits = collections.defaultdict(list), [], {}
    for entry in roster:
        uid = entry["unit"]
        kind_dir, path = unit_file(uid)
        if path is None:
            problems.append(f"roster: no enabled mod defines {uid}")
            continue
        utype = unit_type(uid)
        section = ROSTER_SECTION.get(utype)
        if section is None:
            problems.append(f"roster: {uid} is a {utype}, which is not a "
                            "purchasable category")
            continue
        pool = (squadrons(uid) if section in ("AllowedAircraft", "AllowedHelicopters")
                else variants(uid, kind_dir))
        for pick in entry["picks"]:
            if pick not in pool:
                problems.append(
                    f"roster: {uid} is priced with {pick}, which its winning "
                    f"file does not offer (has: {', '.join(pool) or 'none'})")
        by_section[section].append(entry)
        token = owner(f"{kind_dir}/{uid}.ini")
        if token:
            credits[token] = ("roster", f"{uid} at {entry['points']} points")
    if problems:
        raise SystemExit("roster failed:\n  " + "\n  ".join(problems))

    L = [f"; SEST {TITLE} requisition roster.",
         "; Generated by integration/campaign/build_pack.py - edit campaign_data.py.",
         ";",
         "; Points are fictional balance values. The variant and squadron lists",
         "; are not: each one is checked against the file that wins the load",
         "; order, so a price can never name a fit the hull does not offer."]
    for section in ("AllowedVessels", "AllowedSubmarines", "AllowedAircraft",
                    "AllowedHelicopters"):
        if not by_section[section]:
            continue
        L += ["", f"[{section}]",
              "; syntax is: <unit_type>=<variant_or_squadron>,...|<points_cost>"]
        for entry in by_section[section]:
            if entry.get("note"):
                L.append(f"; {entry['note']}")
            L.append(f"{entry['unit']}={','.join(entry['picks'])}|{entry['points']}")
    L += ["", "[LoadoutPrices]",
          "; Aircraft loadouts are included in the aircraft purchase cost.",
          "; Naval loadout presets are not advertised until they are authored",
          "; and tested - the inspected RAN hulls declare none."]
    return "\n".join(L) + "\n", credits


def threat_profile(placed):
    """The mission info panel's threat display, read off the red order of battle.

    These are presentation fields, not deployment restrictions - the authoring
    guide is explicit about that - so they are derived rather than hand-set.
    """
    def level(*families):
        n = sum(len(placed.get(f, [])) for f in families)
        return f"True,{min(5, 2 + n // 3)}" if n else "False"
    return [("Ship", level("Taskforce2Vessel")),
            ("Air", level("Taskforce2Aircraft", "Taskforce2Helicopter")),
            ("Sub", level("Taskforce2Submarine")), ("Land", level("Taskforce2LandUnit"))]


def allowed_roster_units(allow, roster, where):
    """TaskForceModeAllowedRosterUnits for one mission, from the roster itself.

    Pacific Strike uses this key eleven times to open the builder on a subset
    of the campaign roster - `usn_bb_iowa,Variant3|usn_cg_belknap,Variant4,...`
    The variants are never re-stated here: they are read back out of the
    roster entry, so a per-mission allowlist cannot advertise a fit the
    roster does not price, and naming a unit the roster does not sell at all
    fails the build rather than shipping a dead entry.
    """
    priced = {e["unit"]: e for e in roster}
    unknown = [u for u in allow if u not in priced]
    if unknown:
        raise SystemExit(f"{where}: purchase allowlist names "
                         f"{', '.join(unknown)}, which the roster does not sell")
    seen = [u for u in allow if allow.count(u) > 1]
    if seen:
        raise SystemExit(f"{where}: purchase allowlist repeats "
                         f"{', '.join(sorted(set(seen)))}")
    return "|".join(f"{u},{','.join(priced[u]['picks'])}" for u in allow)


# The six air-tasking roles the game localises, and the whole vocabulary:
# language_en/ui.ini lines 3032-3037 define AirTaskingRole_SuCAP, _CAP,
# _Recon, _HeloRecon, _Attack and _AEW and nothing else. A label outside this
# set has no display string, so it is not a role - it is a word.
TASKING_ROLES = ("SuCAP", "CAP", "Recon", "HeloRecon", "Attack", "AEW")


def slot_ordinal(rows, role, where):
    """Which slot integer a section filling `role` must carry.

    Not the row's position in the list. `TaskForceModeAirTaskingSlot` is the
    1-based ordinal of the row AMONG THE ROWS SHARING ITS LABEL, and the two
    native cases that tell the hypotheses apart both say so: Pacific Strike
    Mission26's third row is CAP and its sections carry Slot=1 (09 Shadows off
    Palawan.ini:833), while Mission29's third row is its second Recon row and
    carries Slot=2 (10 Vengeance at Luzon.ini:754). Row index would have given
    3 in both.

    Which means a mission with two rows of one label cannot be authored the
    way this campaign authors flights: SLOTS says what ROLE an aircraft fills,
    and a role is not enough to pick between a first and a second Recon row.
    Native does it (Mission29), so the ordinal is real; this builder cannot
    express it, and saying so is better than silently handing every section
    ordinal 1 and leaving the second row with no cockpits - which is what an
    earlier version of this function did, by returning inside the loop.
    """
    same = [r for r in rows if r.split("|")[0] == role]
    if not same:
        raise SystemExit(f"{where}: an aircraft is tagged for a {role!r} "
                         "flight, which this mission does not advertise")
    if len(same) > 1:
        raise SystemExit(
            f"{where}: {len(same)} {role!r} rows, and a slot tag names only a "
            "role - there is no way to say which of them an aircraft fills. "
            "Give the rows distinct labels or author one")
    return 1


def tasking_rows(mission, placed):
    """The mission's air-tasking rows, with SlotCount taken from reality.

    A campaign row and the mission's slot-tagged aircraft sections are the two
    halves of Air Tasking: the row advertises the job, the sections are the
    cockpits a purchased aircraft can fill. Native pairing is exact - all 13
    active Pacific Strike rows have precisely as many sections as their Count,
    none has zero - so the count is derived here rather than authored, and a
    row with no section is not emitted at all.

    Sections bind to a row by (Role, Slot), where Slot is the row's ordinal
    among the rows sharing its label. Three further things are checked, since
    an advertised job with a cockpit its aircraft cannot do is the same defect
    one level down:

      * the tagged aircraft's own [AI] Role must match the row's filter;
      * if it declares loadouts, one must be a fit the row offers;
      * the label must be a role the game has a name for.
    """
    rows, dropped, problems = [], [], []
    tagged = collections.defaultdict(list)
    for family, entries in placed.items():
        if not family.startswith("Taskforce1"):
            continue
        for _tag, keys, _n, _x in entries:
            slot = keys.get("TaskForceModeAirTaskingSlot")
            if slot is not None:
                tagged[(keys["TaskForceModeAirTaskingRole"], int(slot))].append(
                    keys["Type"])
    ordinals = collections.Counter()
    for row in mission.get("window", {}).get("flights", []):
        label, display, roles, _count, fits = row.split("|")
        ordinals[label] += 1
        # Consumed before the label is judged, so a bad label reports itself
        # rather than leaving its sections behind to trip the drift assertion
        # below - which used to answer "slot_ordinal and tasking_rows disagree"
        # to a question that was really "Tanker is not a role".
        crews = tagged.pop((label, ordinals[label]), [])
        if label not in TASKING_ROLES:
            problems.append(
                f"{mission['key']}: {label!r} is not an air-tasking role - "
                f"ui.ini names {', '.join(TASKING_ROLES)} and nothing else")
            continue
        want_roles = frozenset(x for x in roles.split("/") if x)
        want_fits = frozenset(x for x in fits.split("/") if x)
        if not crews:
            dropped.append(label)
            continue
        for uid in crews:
            have = ai_roles(uid)
            if not have & want_roles:
                problems.append(
                    f"{mission['key']}: {uid} fills the {label} flight but its "
                    f"[AI] Role is {'/'.join(sorted(have)) or 'undeclared'}, "
                    f"which the row's filter {roles!r} does not match")
            _kind, path = unit_file(uid)
            has_fits = frozenset(loadouts(path))
            if has_fits and not has_fits & want_fits:
                problems.append(
                    f"{mission['key']}: {uid} fills the {label} flight but "
                    f"defines none of its fits (offers "
                    f"{', '.join(sorted(has_fits))})")
        rows.append(f"{label}|{display}|{roles}|{len(crews)}|{fits}")
    # Nothing should be left: slot_ordinal() has already refused a role with
    # no row and a role with two, so every tagged section is popped above.
    # Kept as an assertion rather than a check, because if it ever fires the
    # two functions have drifted apart.
    if tagged:
        raise SystemExit(
            f"{mission['key']}: {sorted(tagged)} survived flight matching - "
            "slot_ordinal and tasking_rows disagree about what a slot is")
    if problems:
        raise SystemExit("air tasking failed:\n  " + "\n  ".join(problems))
    return rows, dropped


def check_purchased_recovery(mission, placed, roster_types):
    """Every aircraft the roster could put in a tasking slot can recover.

    A slot is filled by whatever the player owns that matches the row, so
    the placeholder's own basing proves nothing about the purchase. For
    each row, every roster airframe whose [AI] Role matches it (and whose
    fits, if it declares any, overlap the row's) must have a compatible
    field or deck - deck_fit() 0, not merely undeclared - within its sortie
    radius of the cockpit. The reviewed build sold four types at the finale
    that no row could take and a tanker no field could receive.
    """
    problems = []
    rows = mission.get("window", {}).get("flights", [])
    if not rows:
        return problems
    decks = []
    for kind_family in ("LandUnit", "Vessel"):
        for tag, keys, _n, _x in placed.get("Taskforce1" + kind_family, []):
            size = deck_size(keys["Type"])
            if size:
                decks.append((tag, size, unit_spot(keys), keys["Type"],
                              kind_family == "Vessel"))
    slots = []
    for family in ("Taskforce1Aircraft", "Taskforce1Helicopter"):
        for tag, keys, _n, _x in placed.get(family, []):
            if "TaskForceModeAirTaskingSlot" in keys:
                slots.append((keys["TaskForceModeAirTaskingRole"], unit_spot(keys)))
    for row in rows:
        label, _display, roles, _count, fits = row.split("|")
        want = frozenset(x for x in roles.split("/") if x)
        want_fits = frozenset(x for x in fits.split("/") if x)
        spots = [sp for r, sp in slots if r == label]
        for uid in roster_types:
            if not (ai_roles(uid) & want):
                continue
            _k, path = unit_file(uid)
            has = frozenset(loadouts(path)) if path else frozenset()
            if has and not has & want_fits:
                continue
            kind = unit_type(uid)
            radius = (airframe_range(uid) or 0.0) * SORTIE_FRACTION
            for sp in spots:
                ok = False
                for d in decks:
                    if deck_fit(uid, kind, d[3], d[4]) != 0:
                        continue
                    needs = 1 if kind == "Helicopter" else 10
                    if kind == "VTOL" and d[4]:
                        needs = 1
                    if d[1] < needs or not (sp and d[2]):
                        continue
                    if math.hypot(d[2][0] - sp[0], d[2][1] - sp[1]) <= radius:
                        ok = True
                        break
                if not ok:
                    problems.append(
                        f"{mission['key']}: a purchased {uid} in the {label} "
                        f"flight has no compatible field or deck within "
                        f"{radius:.0f} NM of its cockpit - the row sells a "
                        "sortie the aircraft cannot recover from")
                    break
    return problems


def check_flights(rows, roster, authored=()):
    """Every air-tasking row must describe aircraft the roster actually sells.

    The contract is read off the stock rows rather than guessed. Pacific
    Strike's `Recon|Recon|MPA/ASW/ESM/AEW|1|ASW/Recon/AntiShip/AEW` offers
    `AEW` to the E-2C (whose only fit is AEW), `ASW/AntiShip/Recon` to the
    P-3C and `ASW/AntiShip` to the S-3A: the row lists the UNION across the
    aircraft its role filter matches, and each aircraft flies the
    intersection. Two things follow, and both are checked:

      * a fit named in a row must be defined by at least one roster aircraft
        the row's roles match - otherwise it is a name from a different
        decade's airframe, which is exactly how `Recon` and `AEW` got into
        this campaign's rows;
      * an aircraft the row matches must define at least one of the row's
        fits - otherwise the row advertises a job it cannot offer.

    An aircraft with no `AvailableLoadouts` line at all (E-7A, MQ-4C) is
    exempt from the second rule: whatever the engine does with it is its own
    default, and inventing a preset to satisfy a checker would be worse than
    leaving the behaviour unestablished.
    """
    # The two rules have different audiences, and conflating them is what made
    # the first attempt at this reject good rows.
    #
    # Rule 1 - no orphan fit name - is about the row's whole cast: an aircraft
    # the roster sells, OR one already authored into some mission's slot for
    # this flight. SW03's CH-53 is the second kind: never purchasable, and the
    # row still has to be able to arm it.
    #
    # Rule 2 - every matched aircraft can fly the job - is about PURCHASES
    # only. An authored aircraft that happens to match this row's filter while
    # being tagged to a different one never enters this flight, so holding the
    # row responsible for arming it is wrong: SW11's EA-18G is tagged Attack
    # and matches Fighter, and no amount of CAP fits would make that a bug.
    def describe(uid):
        kind_dir, path = unit_file(uid)
        if kind_dir not in ("aircraft", "helicopters"):
            return None
        return (uid, ai_roles(uid), frozenset(loadouts(path)))

    sellable = [d for d in (describe(e["unit"]) for e in roster) if d]
    cast = {d[0]: d for d in sellable}
    for uid in authored:
        if uid not in cast:
            d = describe(uid)
            if d:
                cast[uid] = d
    problems = []
    for row in sorted(set(rows)):
        parts = row.split("|")
        if len(parts) != 5:
            problems.append(f"flight row {row!r} is not "
                            "Label|Display|Roles|Count|Fits")
            continue
        label, _display, roles, count, fits = parts
        want_roles = frozenset(x for x in roles.split("/") if x)
        want_fits = [x for x in fits.split("/") if x]
        if not count.isdigit() or int(count) < 1:
            problems.append(f"{label}: flight size {count!r} is not a count")
        buyable = [(u, f) for u, r, f in sellable if r & want_roles]
        if not buyable:
            problems.append(
                f"{label}: role filter {roles!r} matches nothing the roster "
                "sells - " + "; ".join(f"{u} is {'/'.join(sorted(r))}"
                                       for u, r, _ in sellable))
            continue
        whole_cast = [(u, f) for u, r, f in cast.values() if r & want_roles]
        for fit in want_fits:
            if not any(fit in f for _u, f in whole_cast):
                problems.append(
                    f"{label}: offers {fit!r}, which nothing that can fly this "
                    f"flight defines")
        for uid, fit_set in buyable:
            if fit_set and not fit_set & set(want_fits):
                problems.append(
                    f"{label}: sells {uid} into this flight, and it defines "
                    f"none of {'/'.join(want_fits)} "
                    f"(has: {', '.join(sorted(fit_set))})")
    if problems:
        raise SystemExit("air tasking failed:\n  " + "\n  ".join(problems))


def window_of(mission):
    return mission.get("window", {})


def campaign_ini(missions, events, placements):
    """The campaign spine, in native Task Force Mode.

    Every key here was read out of the exported Pacific Strike campaign before
    it was used. What that establishes is the vocabulary, not the balance: the
    numbers are a first pass and the bible's acceptance run is what would
    settle them.
    """
    EVENT_FORMS = {e["file"]: e.get("form", "press") for e in events}
    L = ["[File]", f"Base=campaigns/{SLUG}/campaign.ini", "",
         "[Campaign]", "Type=Linear", f"Difficulty={CAMPAIGN_DIFFICULTY}",
         f"Length={sum(1 for m in missions if m['group'] == 'core')}",
         # Native placement: BackgroundImage sits between Length and
         # DisplayFormat in all three shipped campaigns. MapView is what the
         # one shipped Task Force Mode campaign (Pacific Strike) uses; Legacy
         # is the 1988 linear prototype's, and this campaign shipped Legacy
         # for its first builds - the briefing panel drew no mission image.
         f"BackgroundImage=campaigns/{SLUG}/art/00_campaign_background.png",
         "DisplayFormat=MapView", "",
         "[TaskForceMode]"]
    for key, value in TASKFORCE.items():
        L.append(f"{key}={value}")
    L.append("")
    for name, points, cap, repair in DIFFICULTIES:
        L += [f"[TaskForceModeDifficulty_{name}]", f"Name={name}",
              f"StartingPoints={points}", f"PointCap={cap}",
              "ShipIncludesAirwing=False", "PurchaseLoadouts=True",
              f"RepairCostModifier={repair}",
              f"CrewSkillInitial={TASKFORCE['CrewSkillInitial']}", ""]
    # English only, and deliberately. See LANGS: the evidence for mirroring
    # covers SUFFIX keys, not [Language_xx] SECTIONS. The base game ships
    # `missions/Demo/_info.ini` with ja, en and ko and nothing else, and
    # `missions/Intro/_info.ini` with five of the nine - so a missing section
    # is a case the game already handles in its own content, and nine copies
    # of one English paragraph would be bloat bought with a guess.
    L += ["[Language_en]",
          f"Name={CAMPAIGN_NAME_EN or f'{TITLE} (Royal Australian Navy)'}",
          "Description=" + CAMPAIGN_BLURB, ""]

    entries = _spine(missions, events)
    index_of = {e["mission"]["key"]: i for i, e in enumerate(entries, 1)
                if e["type"] == "Mission"}
    # The last playable entry, derived rather than named: the epilogue that
    # follows SW12 is a story card, and flagging it would tell the game the
    # campaign ends on something the player never flies.
    last_playable = max(index_of.values())
    L += ["[Missions]", f"NumberOfMissions={len(entries)}", ""]
    for i, entry in enumerate(entries, 1):
        L.append(f"[Mission{i}]  #{entry['comment']}")
        L.append(f"Type={entry['type']}")
        mission = entry.get("mission")
        if entry["type"] == "Mission":
            L.append(f"MissionFile=campaigns/{SLUG}/missions/{entry['file']}.ini")
            if mission.get("generation"):
                L.append(f"TaskForceModeMissionGenerationType={mission['generation']}")
            L.append("RequiredResult=CostlyVictory")
        L.append(f"IsUnlocked={'True' if i == 1 else 'False'}")
        L.append("IsComplete=False")
        if i > 1:
            L.append(f"Parents={entry.get('parent', i - 1)}")
        if entry["type"] == "Mission":
            placed = placements[mission["key"]]
            L.append("")
            # A detached operation - a strike flown from a carrier that is
            # not the player's, a relief window - does not sail the owned
            # force. Stock's detached ops set this False; a placed blue hull
            # that is set dressing for the mission is not a reason to say
            # True and sell the player ships that will not appear.
            # Blank generation (the guide: "launch as-is without any
            # persistent task force units") is the detached operation. The
            # Includes flags are display only, and what they display for such
            # a mission is that nothing of the player's deploys - as the three
            # stock detached operations show it.
            blank = not mission.get("generation")
            detached = blank or mission.get("detached")
            L.append(f"TaskForceModeIncludesTaskForce="
                     f"{'False' if detached else 'True' if placed.get('Taskforce1Vessel') else 'False'}")
            L.append(f"TaskForceModeIncludesAirwing="
                     f"{'True' if (placed.get('Taskforce1Aircraft') or placed.get('Taskforce1Helicopter')) and not detached else 'False'}")
            L.append(f"TaskForceModeIncludesSubmarine="
                     f"{'True' if placed.get('Taskforce1Submarine') and not detached else 'False'}")
            if blank and (window_of(mission).get("flights") or window_of(mission).get("airbase_prep")):
                raise SystemExit(f"{mission['key']}: a blank-generation mission "
                                 "places no persistent units - it cannot "
                                 "advertise flight rows or airbase prep")
            L.append("")
            for what, value in threat_profile(placed):
                L.append(f"TaskForceModeThreatProfile{what}={value}")
            L.append("")
            # Builder access, repair and rearm are three separate windows, not
            # one boolean: the design opens purchases at force-assembly points,
            # repair at service windows and a free rearm at some of them.
            window = mission.get("window", {})
            L.append(f"TaskForceModeRepair={'True' if window.get('repair') else 'False'}")
            L.append(f"TaskForceModeRearm="
                     f"{'True' if window.get('rearm') or window.get('rearm_if') else 'False'}")
            L.append("TaskForceModeEnableTaskForceBuilder="
                     f"{'True' if window.get('buy') else 'False'}")
            # An open builder does not have to offer the whole roster. The
            # campaign assembles the force in stages, and SW12 buys aircraft
            # but no hulls - which is a comment in the data until this key
            # makes it a rule the game enforces.
            if window.get("buy") and window.get("allow"):
                L.append("TaskForceModeAllowedRosterUnits="
                         + allowed_roster_units(window["allow"], ROSTER,
                                                mission["key"]))
            flights, empty = tasking_rows(mission, placed)
            bad = check_purchased_recovery(
                mission, placed,
                [e["unit"] for e in ROSTER
                 if unit_type(e["unit"]) in ("Aircraft", "Helicopter", "VTOL")])
            if bad:
                raise SystemExit("purchased aircraft cannot recover:\n  "
                                 + "\n  ".join(bad))
            if empty:
                # An advertised flight with no cockpit is an offer the player
                # can buy into and never deploy. Saying so out loud beats
                # shipping it.
                print(f"  {mission['key']}: no slot for "
                      + ", ".join(empty) + " - row not emitted")
            if flights:
                L.append("TaskForceModeAirTaskingAvailable=True")
                for n, row in enumerate(flights, 1):
                    L.append(f"TaskForceModeAirTaskingFlight{n}={row}")
            # Whether the whole owned force sails or the player picks a
            # detachment. Both keys are stock (pacific-strike campaign.ini);
            # neither is documented in ui.ini, so the pairing is inferred from
            # how the stock campaign uses them and is untested here.
            if blank:
                pass        # nothing of the player's sails: no deployment keys
            elif window.get("detachment"):
                L += ["TaskForceModeDeploymentOptions=True",
                      "TaskForceModeRequireEntireTaskForce=False"]
            else:
                L.append("TaskForceModeRequireEntireTaskForce=True")
            # A one-ship (or n-ship) restricted mission: the guide's own
            # pattern, Replaced generation plus a unit limit.
            if window.get("max_units"):
                if mission.get("generation") != "Replaced":
                    raise SystemExit(f"{mission['key']}: max_units needs "
                                     "Replaced generation (the guide's rule)")
                L += [f"TaskForceModeRequiredUnitType="
                      f"{window.get('unit_type', 'Vessel')}",
                      f"TaskForceModeMaxUnits={window['max_units']}"]
            # Rearm that depends on an earlier result - the guide's
            # TaskForceModeRearmByVariableAND, IsTrue included.
            if window.get("rearm_if"):
                var, state = window["rearm_if"]
                L.append(f"TaskForceModeRearmByVariableAND={var},{state}")
            if window.get("situation"):
                L.append("TaskForceModeBuilderSituation_en="
                         + ini_text(window["situation"]))
            if window.get("notice"):
                title, text = window["notice"]
                L += [f"TaskForceModeDebriefNoticeTitle_en={title}",
                      f"TaskForceModeDebriefNoticeText_en={ini_text(text)}"]
            if window.get("airbase_prep"):
                if not any("airbase" in k["Type"].lower() or "airfield" in k["Type"].lower()
                           for _t, k, _n, _x in placed.get("Taskforce1LandUnit", [])):
                    raise SystemExit(f"{mission['key']}: airbase_prep needs a "
                                     "player land unit whose Type contains "
                                     "airbase or airfield (the guide's rule)")
                L += ["TaskForceModeAirbasePrepAvailable=True",
                      "TaskForceModeAirbasePrepReadySlots=2",
                      "TaskForceModeAirbasePrepInProgressSlots=1"]
            if i == last_playable:
                # Stock marks its final mission so the campaign can be
                # replayed in sandbox afterwards.
                L.append("TaskForceModeFinalMission=True")
            L.append(f"TaskForceModeCompletionPoints={mission.get('points', 0)}")
            # Zero cap increment for this first balance pass: a reward is not a
            # reason to raise the ceiling on unspent points.
            L.append("TaskForceModeCompletionCapPoints=0")
            if mission.get("expires_after"):
                # The stock campaign's value is the campaign ENTRY INDEX whose
                # completion closes the window (03A and 03B both expire after
                # entry 12, the next main mission), not a countdown. Getting
                # that backwards ships an optional operation that expires
                # before it can be flown.
                closer = index_of.get(mission["expires_after"])
                if closer is None:
                    raise SystemExit(
                        f"{mission['key']}: expires_after names "
                        f"{mission['expires_after']!r}, which is not a mission "
                        "in the campaign spine")
                L.append(f"ExpiresAfterMissionComplete={closer}")
            if mission.get("special"):
                L.append("MissionSpecialNoteHighlightColor=Color.SeaPowerBlue")
        # Everything below is per-language, and every language gets all of it.
        # See LANGS: there is no fallback, so an entry that names its art only
        # in English has no art outside English.
        local = [("Name", entry["name"]), ("Description", entry["sub"])]
        if entry["type"] == "Mission":
            local += [("MissionSequenceName", entry["seq"]),
                      ("MapShortName", entry["short"]),
                      ("MissionIntro", entry["intro"]),
                      # The card the campaign map draws for this mission.
                      # Generated by make_art from the mission that was just
                      # written, so it cannot describe a mission that changed
                      # underneath it.
                      ("MissionImage", sheet_path(entry["mission"]))]
            if mission.get("special"):
                local.append(("MissionSpecialNote", mission["special"]))
        else:
            # TileImagePath_ is the 128x128 tile BEHIND the event on the
            # campaign map, not the story image: stock points every event at
            # bkg_tile_message.png or bkg_tile_newspaper.png and reaches the
            # page's own images through the XAML's Assets[] binding. The
            # first builds put the 1920x1080 story image here.
            form = EVENT_FORMS.get(entry["file"], "press")
            tile = "newspaper" if form == "press" else "message"
            local += [("AssetsPath", f"campaigns/{SLUG}/art"),
                      ("FilePath", f"campaigns/{SLUG}/art/{entry['file']}.xml"),
                      ("TileImagePath",
                       f"campaigns/{SLUG}/art/bkg_tile_{tile}.png")]
        for lang in LANGS:
            L.append("")
            for key, value in local:
                L.append(f"{key}_{lang}={value}")
        L.append("")
    return "\n".join(L)


def _spine(missions, events):
    """Campaign entries in calendar order, with the optional branches hung off
    the main chain rather than inside it.

    Pacific Strike does this by giving a side mission and the next main mission
    the SAME Parents value, so the side mission unlocks without gating what
    follows. An optional operation the player skips must not stop the campaign.
    """
    scheduled = sorted((m for m in missions if m["group"] != "dispatch"),
                       key=lambda m: m["date"])
    keys = {m["key"] for m in scheduled}
    import os
    for ev in events[1:-1]:
        if ev.get("before") not in keys:
            msg = (f"event {ev['file']} hangs before {ev.get('before')!r}, which is "
                   "not a mission in this campaign - it would silently never be shown")
            if os.environ.get("SR_ALLOW_MISSING"):
                print(f"  (partial build) {msg}")
                continue
            raise SystemExit(msg)
    out = [dict(type="FreeEvent", comment="Prologue", file=events[0]["file"],
                name=events[0]["title"], sub=events[0]["sub"])]
    for m in scheduled:
        for ev in events[1:-1]:
            if ev.get("before") == m["key"]:
                out.append(dict(type="FreeEvent", comment=ev["title"].replace("\\n", " - "),
                                file=ev["file"], name=ev["title"], sub=ev["sub"]))
        label = m.get("seq") or {"optional": "OPTIONAL", "contingency": "CONTINGENCY"}.get(
            m["group"], f"MISSION {m['num'].lstrip('0')}")
        out.append(dict(type="Mission", comment=f"{mission_code(m)} {m['key']}",
                        file=mission_name(m), name=m["key"].upper(),
                        sub=m["place"], seq=label, short=mission_code(m),
                        intro=m["intro"], mission=m))
    out.append(dict(type="FreeEvent", comment="Epilogue", file=events[-1]["file"],
                    name=events[-1]["title"], sub=events[-1]["sub"]))

    chain = None
    for i, entry in enumerate(out, 1):
        side = entry.get("mission", {}).get("group") in ("optional", "contingency")
        if chain is not None:
            entry["parent"] = chain
        if not side:
            chain = i
    return out


# --- coverage ----------------------------------------------------------------

HOW_TEXT = {
    "unit": "places the unit; this mod wins its file",
    "roster": "the requisition roster prices it, so the player can buy it",
    "variant": "supplies the hull variant the placed unit uses",
    "squadron": "supplies the squadron the placed airframe flies from",
    "store": "supplies a round the placed unit's loadout hangs",
    "asset": "supplies a model folder the placed unit's file draws from",
}


def catalog():
    import json
    return json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8"))


def coverage(credits, excuses):
    """Every ENABLED mod and local pack, with how the campaign reaches it.

    Enabled, not active: data/load-order.tokens.txt is the subscription list
    the game loads, and five of its entries are catalogued deprecated and two
    WIP while still being required donors - the Anzac hull SEST patches and
    the Wedgetail among them. Coverage that skipped them would be measuring
    the catalog instead of the install.
    """
    data = catalog()
    by_workshop = {str(m["workshop_id"]): m for m in data["mods"]
                   if m.get("workshop_id")}
    rows, missing = [], []
    wanted = []
    for token in load_order():
        if token.startswith("SEST_"):
            continue          # the consolidated pack; its sources are below
        mod = by_workshop.get(token)
        if mod is None:
            raise SystemExit(f"load order names {token}, which is not catalogued")
        wanted.append(("mod", mod["id"], token, mod["title"]))
    wanted += [("pack", p["folder"], p["folder"], p["title"])
               for p in data["local_packs"]]
    for what, mid, token, title in sorted(wanted):
        if token in credits:
            how, detail, mission = credits[token]
            rows.append((mid, title, how, detail, mission, token))
        elif mid in excuses:
            rows.append((mid, title, excuses[mid][0], excuses[mid][1], "-", token))
        else:
            missing.append((what, mid, token, title))
    return rows, missing


def report(rows, missions, worst, unused=(), coast=()):
    counts = collections.Counter(r[2] for r in rows)
    L = [f"# {TITLE} — mod coverage", "",
         "Generated by `integration/campaign/build_pack.py`. Do not edit.", "",
         f"The campaign is {len(missions)} missions built from "
         f"{sum(len(m['units']) for m in missions)} placed units. Every mod in "
         "the canonical load order (`data/load-order.tokens.txt`) and every "
         "SEST source pack appears below, with the mechanism that makes the "
         "game read its files. Coverage is measured on the load order rather "
         "than on catalog status, because five enabled entries are catalogued "
         "deprecated and two WIP while still being required donors.", ""]
    if unused:
        L += [f"This campaign reaches {len(rows)} of the enabled mods and packs; "
              f"the {len(unused)} it does not are listed at the end. The pack's "
              "coverage rule - every enabled mod placed or excused - is met by "
              "the pack as a whole, not by each campaign in it.", ""]
    if coast:
        L += [f"{len(coast)} station(s) were proved against the coastline "
              "extract (`integration/campaign/geo/`) rather than a pool of "
              "proven points: nothing in this repo had sailed this water before.", ""]
    L += ["| class | meaning | mods |", "|---|---|---|"]
    meaning = dict(HOW_TEXT)
    meaning["library"] = ("ships no file a mission can name — systems, effects, "
                          "UI or a bare dependency marker — and applies install-wide")
    meaning["shadowed"] = ("every file it ships is outranked by something above "
                           "it; nothing it contains can load")
    meaning["campaign"] = "this pack - the campaign being measured"
    for how in ("unit", "variant", "squadron", "roster", "store", "asset",
                "library", "shadowed", "campaign"):
        if counts.get(how):
            L.append(f"| `{how}` | {meaning[how]} | {counts[how]} |")
    L += ["", f"Sea and land positions are snapped to points already used by a "
          f"loading mission; the furthest any anchor had to move is "
          f"{worst:.1f} NM.", "",
          "| mod / pack | title | class | via | mission |", "|---|---|---|---|---|"]
    for mid, title, how, detail, mission, _token in rows:
        L.append(f"| `{mid}` | {title} | `{how}` | {detail} | {mission} |")
    L.append("")
    if unused:
        L += ["## Enabled, and not reached by this campaign", "",
              "Left in the load order because removing one changes which file "
              "wins for the mods that are. See the campaign's own "
              "REQUIRED-MODS.txt for the four lists a subscriber needs.", "",
              "| mod / pack | title |", "|---|---|"]
        for _what, mid, _token, title in unused:
            L.append(f"| `{mid}` | {title} |")
        L.append("")
    return "\n".join(L)


def campaign_requirements(rows, missing, title):
    """One campaign's dependency closure, in the four lists a release needs:
    hard required, SEST donors, install-wide libraries, not used.

    Computed from the same coverage rows as the pack-level file, so it cannot
    name a mod the campaign's missions do not reach; the pack-level
    REQUIRED-MODS.txt beside it is the union across every campaign shipped.
    """
    need = [r for r in rows if r[2] in NEEDED and r[5].isdigit()]
    packs = [r for r in rows if r[2] in NEEDED and not r[5].isdigit()]
    libs = [r for r in rows if r[2] in ("library",) and r[5].isdigit()]
    shadowed = [r for r in rows if r[2] == "shadowed"]
    promoted, elsewhere = prerequisites(
        need, [r for r in rows if r[2] not in NEEDED and r[5].isdigit()])
    key = lambda r: r[1].lower()
    L = [f"{title.upper()} - what this campaign needs", "",
         "Four lists. The pack-level REQUIRED-MODS.txt one folder up is the",
         "union across every campaign in the pack; this is the closure for",
         "this one, derived from the units its missions place, the squadrons",
         "and hull variants they name, and the rounds their loadouts hang.", "",
         f"1. HARD REQUIRED ({len(need) + len(promoted)}): a mission names a file of "
         "theirs, or a mod above says it cannot run without them.", ""]
    for _mid, t, how, _d, _m, token in sorted(need, key=key):
        L.append(f"  {token:<13} {NEEDED[how]:<32} {t}")
    for row, askers in sorted(promoted.items(), key=lambda kv: kv[0][1].lower()):
        L.append(f"  {row[5]:<13} {'required by another mod':<32} {row[1]}")
        L.append(f"  {'':<13} {'':<32}   asked for by: {', '.join(sorted(set(askers)))}")
    for name, askers in sorted(elsewhere.items()):
        L.append(f"  {'(workshop)':<13} {'manual install':<32} {name} - required by "
                 f"{', '.join(sorted(set(askers)))}; not in this collection")
    L += ["", f"2. SEST INTEGRATION PACKS ({len(packs)}): this project's own patches, "
          "inside the consolidated download.", ""]
    for _mid, t, how, _d, _m, token in sorted(packs, key=key):
        L.append(f"  {'(local)':<13} {NEEDED[how]:<32} {t}")
    L += ["", f"3. INSTALL-WIDE LIBRARIES AND UI ({len(libs)}): ship no file a mission "
          "names. Optional unless a mod in list 1 asks for them (Anchor Chain",
          "is asked for; the map, salvo and rescue tools are conveniences).", ""]
    for _mid, t, how, _d, _m, token in sorted(libs, key=key):
        L.append(f"  {token:<13} {'library':<32} {t}")
    unused = [(mid, token, t) for _w, mid, token, t in missing] + \
             [(r[0], r[5], r[1]) for r in shadowed]
    L += ["", f"4. NOT USED BY THIS CAMPAIGN ({len(unused)}): enabled while it was built, "
          "and left in the order because removing one changes which copy of a",
          "shared file wins for the mods above.", ""]
    for mid, token, t in sorted(unused, key=lambda x: x[2].lower()):
        L.append(f"  {token if token.isdigit() else '(local)':<13} {t}")
    L.append("")
    return "\n".join(L) + "\n"


# A player is not a developer: the coverage report above is a table of catalog
# ids and internal classes, and it lives in the repo, which is not somewhere a
# subscriber can read. This is the same fact set written for the person who
# just downloaded the mod - workshop ids, because that is what a subscription
# is addressed by, and a plain statement of what happens when one is absent.
#
# The honest scope of this list: it is every enabled mod the campaign REACHES,
# derived from the units the missions place. It is not a proof of sufficiency.
# Workshop mods declare dependencies of their own (the catalog records two that
# do), and a unit file may #!extend a base this build resolves without the
# campaign ever naming its mod. So the full order ships beside it.
# Short forms of HOW_TEXT. The report's sentences read well in a table with a
# `via` column beside them and turn to gibberish truncated into a column here.
NEEDED = {"unit": "a unit a mission places",
          "variant": "a hull variant in use",
          "squadron": "a squadron a flight comes from",
          "roster": "a unit the player can buy",
          "store": "a weapon a loadout hangs",
          "asset": "a model a placed unit draws"}


def _squash(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def prerequisites(need, rest):
    """What the REQUIRED mods say they need, read out of their own _info.ini.

    A mod reached by nothing the campaign places is not a mod the player can
    skip if something the campaign DOES place asks for it. Anchor Chain is the
    case that proves it: nothing here names a file of its, so coverage class
    it `library` and the list said "the campaign does not call for them" -
    while B-2 Spirit, which IS required, says "Requires AnchorChain and
    SeaLifter" in its own description. A player who trusted the list would
    have skipped a mod a required mod cannot run without.

    Matched on squashed titles because a mod spells its dependency however it
    likes: "AnchorChain", "Anchor Chain", "the Anchor Chain mod".

    Returns (promoted, elsewhere): rows to move into the required list, and
    names that are required but are in no part of this collection at all.
    """
    index = {}
    for row in need + rest:
        index[_squash(row[1])] = row
    # Spelled out because they are not in the load order to be derived from:
    # a dependency this collection does not carry is exactly the one a player
    # is most likely to be missing.
    OUTSIDE = {"sealifter": "SeaLifter"}
    promoted, elsewhere = {}, {}
    for row in need:
        info = MODS / row[5] / "_info.ini"
        if not info.is_file():
            continue
        text = info.read_text(encoding="utf-8-sig", errors="replace")
        desc = " ".join(m.group(1) for m in
                        re.finditer(r"^Description=(.*)$", text, re.M))
        if not re.search(r"\brequir", desc, re.I):
            continue
        flat = _squash(desc)
        for key, other in index.items():
            if len(key) > 6 and key in flat and other[5] != row[5]:
                if other in rest:
                    promoted.setdefault(other, []).append(row[1])
        for key, name in OUTSIDE.items():
            if key in flat:
                elsewhere.setdefault(name, []).append(row[1])
    return promoted, elsewhere


def requirements(rows):
    need = [r for r in rows if r[2] in NEEDED and r[5].isdigit()]
    rest = [r for r in rows if r[2] not in NEEDED and r[5].isdigit()]
    packs = [r for r in rows if not r[5].isdigit()]
    promoted, elsewhere = prerequisites(need, rest)
    rest = [r for r in rest if r not in promoted]
    key = lambda r: r[1].lower()
    L = [f"{TITLE.upper()} - required Steam Workshop mods", "",
         "TRY THE MOD MANAGER FIRST. Its Sync button asks Steam for this mod's",
         "required items and subscribes you to them - the game reports back",
         "\"Subscribed to N new dependencies. Enabled N installed",
         "dependencies\", and it iterates, so a dependency's own dependencies",
         "come too. If that works you do not need the list below at all, and",
         "it is here to check against rather than to work through by hand.",
         "",
         f"{len(need)} mods. Each supplies a file a mission names directly - by",
         "Type=, SquadronReference=, VariantReference=, a loadout's store,",
         "or a model folder a placed unit's own file draws from.",
         "",
         "What the game does with a reference it cannot resolve has not been",
         "tested here, so this file will not tell you. At best the unit is",
         "simply absent and the mission is a different, easier one; at worst",
         "the mission does not load. Neither is the mission that was built.",
         "",
         "Either way, check the Mod Manager list against LOAD-ORDER.txt in",
         "this folder when you are done: subscribing is not ordering, and",
         "order decides which copy of a shared file the game reads.", "",
         f"{'Workshop id':<13} {'supplies':<32} mod", ""]
    for _mid, title, how, _detail, _mission, token in sorted(need, key=key):
        L.append(f"{token:<13} {NEEDED[how]:<32} {title}")
    if promoted:
        L += ["", "And these, which the campaign never names itself - but a mod",
              "above does, in its own description. Skipping one breaks the mod",
              "that asked for it.", ""]
        for row, askers in sorted(promoted.items(), key=lambda kv: kv[0][1].lower()):
            L.append(f"{row[5]:<13} {'required by another mod':<32} {row[1]}")
            L.append(f"{'':<13} {'':<32}   asked for by: {', '.join(sorted(set(askers)))}")
    if elsewhere:
        L += ["", "NOT IN THIS LIST AND STILL REQUIRED:", ""]
        for name, askers in sorted(elsewhere.items()):
            L.append(f"  {name} - named as a requirement by "
                     f"{', '.join(sorted(set(askers)))}.")
            L.append(f"  It is not one of the mods above and this collection does "
                     f"not carry it.")
            L.append(f"  Find it on the Workshop. It needs a manual install: "
                     f"subscribing alone")
            L.append(f"  is not enough.")
    L += ["", "-" * 74, "",
          f"Also enabled while this was built ({len(rest)}), and left in the order",
          "because removing one changes which file wins: these ship systems,",
          "effects or UI rather than anything a mission names, or are outranked",
          "by something above them. The campaign does not call for them.", ""]
    for _mid, title, how, _detail, _mission, token in sorted(rest, key=key):
        L.append(f"{token:<13} {how:<32} {title}")
    L += ["", "-" * 74, "",
          "Not from the Workshop. These are this project's own packs. If you",
          "have the consolidated download - one mod folder carrying everything",
          "- they are already inside it and there is nothing to subscribe to;",
          "the repository also builds each of them on its own.", ""]
    for _mid, title, how, _detail, _mission, token in sorted(packs, key=key):
        L.append(f"{'(local)':<13} {how:<32} {title}")
    L += ["", "-" * 74, "",
          "Two things this list cannot settle for you:", "",
          "  * A mod can need a further download of its own and say so only in",
          "    its own Workshop description. The ones this build could read out",
          "    of an _info.ini are listed above; a description that is on the",
          "    Workshop page and not in the file is not something it can see.",
          "  * Load ORDER decides which copy of a shared file the game reads.",
          "    Two mods that both ship the same aircraft will not both load it.",
          "    LOAD-ORDER.txt is the order this was built and tested against,",
          "    and this campaign's own folder belongs at the top of it.", ""]
    return "\n".join(L) + "\n"


def required_urls(rows):
    """Every required mod as a Workshop URL, in load-order sequence.

    For setting the published item's Required Items. Steam resolves
    dependencies itself once they are set, and the game's Mod Manager Sync
    walks them - which is the only reason a 133-mod campaign is a reasonable
    thing to publish at all.
    """
    need = [r for r in rows if r[2] in NEEDED and r[5].isdigit()]
    promoted, elsewhere = prerequisites(need, [r for r in rows
                                               if r[2] not in NEEDED
                                               and r[5].isdigit()])
    rank = {t: i for i, t in enumerate(load_order())}
    both = need + list(promoted)
    both.sort(key=lambda r: rank.get(r[5], 10**6))
    L = [f"{TITLE} - Required Items for the Workshop listing", "",
         f"{len(both)} items, in canonical load order. Paste each into the",
         "published item's Required Items box. Generated by build_pack.py from",
         "the same coverage rows REQUIRED-MODS.txt uses, so it cannot name a",
         "mod the campaign does not reach.", ""]
    for row in both:
        L.append(f"https://steamcommunity.com/sharedfiles/filedetails/?id={row[5]}"
                 f"    # {row[1]}")
    if elsewhere:
        L += ["", "NOT IN THE COLLECTION - find the id yourself before "
                  "publishing:"]
        for name, askers in sorted(elsewhere.items()):
            L.append(f"  {name}  (required by {', '.join(sorted(set(askers)))})")
    L.append("")
    return "\n".join(L) + "\n"


def load_order_text():
    """The canonical order, as a player's Mod Manager would read it.

    With TITLES. The order is stored as workshop ids because that is what
    usersettings.ini stores, but the Mod Manager shows a player names - and a
    list of 140 bare numbers is not something a human can check an install
    against, which is the only reason this file ships.
    """
    data = catalog()
    titles = {str(m["workshop_id"]): m.get("title", "?") for m in data["mods"]
              if m.get("workshop_id")}
    order = load_order()
    L = [f"{TITLE.upper()} - the load order this was built against", "",
         f"{len(order)} entries, top of the list first. The Mod Manager's own",
         "order is what the game uses; this is a copy to check yours against,",
         "not something the game reads.", "",
         "The one rule that matters: this pack, and any other folder whose",
         "name starts with SEST_, sits ABOVE every Workshop mod. They are",
         "whole-file replacements - anything that outranks them wins instead,",
         "and the fix they carry is gone.", "",
         "A mod you have subscribed to that is not on this list is not a",
         "problem: put it at the bottom. Nothing in the campaign names it, and",
         "the bottom is where it cannot outrank something that is named.", "",
         f"{'#':>4}  {'workshop id':<13} mod", ""]
    for i, token in enumerate(order, 1):
        if token.startswith("SEST_"):
            L.append(f"{i:>4}. {'(this pack)':<13} {token}")
        else:
            L.append(f"{i:>4}. {token:<13} {titles.get(token, '(not catalogued)')}")
    L.append("")
    return "\n".join(L) + "\n"


# --- main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    # Writing is the default: tools/build_all.py runs every builder with no
    # arguments, and a builder that only reports unless asked produces an
    # empty pack folder and a consolidated dist with no campaign in it.
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve and check everything, emit nothing")
    ap.add_argument("--campaign", metavar="SLUG",
                    help="dry-run one campaign only (its slug or title)")
    ap.add_argument("--only", metavar="CODES",
                    help="dry-run only these missions, by code or number, "
                         "comma-separated (SR03,TS01) - skips the pack coverage gate")
    args = ap.parse_args()
    if (args.campaign or args.only) and not args.dry_run:
        sys.exit("--campaign and --only are dry-run filters: a written pack is "
                 "always the whole pack")

    specs = campaign_specs()
    if args.campaign:
        squash = lambda x: re.sub(r"[^a-z0-9]", "", x.lower()).replace("sest", "", 1)
        want = squash(args.campaign)
        specs = [s for s in specs if want in (squash(s["SLUG"]), squash(s["TITLE"]))]
        if not specs:
            sys.exit(f"no campaign called {args.campaign!r} - "
                     + ", ".join(s["SLUG"] for s in campaign_specs()))

    pool = harvest()
    print(f"proven positions: {len(pool['sea'])} sea, {len(pool['land'])} land")

    excuses, pack_credits, campaigns = pack_excuses(specs), {}, []
    for spec in specs:
        set_campaign(spec)
        missions = spec["MISSIONS"]
        if args.only:
            wanted = {x.strip().upper() for x in args.only.split(",") if x.strip()}
            missions = [m for m in missions
                        if mission_code(m).upper() in wanted or m["num"].upper() in wanted]
            if not missions:
                broken = getattr(sys.modules.get("southern_reach"), "BROKEN", {})
                sys.exit(f"{TITLE}: none of {sorted(wanted)} is here"
                         + (" - modules that failed to import: "
                            + "; ".join(f"{k}: {v}" for k, v in broken.items())
                            if broken else ""))
        for lst in (UNPROVEN, RECOVERY_NOTES, CLOSURE_NOTES, REACH_PROBLEMS,
                    CLOSURE_PROBLEMS, PLACEMENT_PROBLEMS, COAST_CHECKED):
            del lst[:]
        print(f"\n== {TITLE}")

        # The requisition roster is resolved first: a purchasable unit is
        # reached by the campaign as surely as a placed one, and a bad price
        # stops the build before twenty missions are rendered on top of it.
        roster_text, roster_credits = roster_ini(ROSTER)
        # ... and the air-tasking rows against that same roster, before any of
        # them is written into a campaign entry.
        check_flights([r for m in spec["MISSIONS"]
                       for r in m.get("window", {}).get("flights", [])], ROSTER,
                      authored={u["type"] for m in spec["MISSIONS"] for u in m["units"]
                                if u.get("slot")})
        built, credits, worst, placements = [], {}, 0.0, {}
        for token, why in roster_credits.items():
            credits[token] = (why[0], why[1], "requisition roster")
        for mission in missions:
            if (mission.get("geography") or GEOGRAPHY) == "coast":
                placer = CoastPlacer(coast_data(), mission)
            else:
                placer = Snapper(pool, limit_nm=mission.get("snap_limit", 60.0))
            placed, members, mission_credits, far = place(mission, placer)
            # A named anchor that matched nothing is a silent failure: the
            # campaign would generate the purchased force with no starting
            # position.
            if mission.get("anchor") and not mission.get("_anchored"):
                sys.exit(f"{mission['key']}: anchor station "
                         f"{mission['anchor']!r} places no blue vessel")
            worst = max(worst, far)
            weight = check_pacing(mission, placed)
            picture = check_reach(mission, placed, members)
            check_closure(mission, placed, members)
            solve_arrival(mission, placed, members)
            check_coast_geometry(mission, placer)
            check_geometry(mission, placed, members)
            name, text = render(mission, placed, members)
            built.append((name, text, mission))
            placements[mission["key"]] = placed
            for token, why in mission_credits.items():
                best = credits.get(token)
                if best is None or STRENGTH[why[0]] < STRENGTH[best[0]]:
                    credits[token] = why
            units = sum(len(v) for v in placed.values())
            gap = (f" gap{picture[0]:6.0f} reach{picture[1]:6.0f} NM"
                   if picture else "")
            print(f"  {name:<44} {units:>3} units {weight:>3} red combat  "
                  f"{len(mission_credits):>3} mods  snap<={far:4.1f}{gap}")

        if UNPROVEN:
            print(f"\n{len(UNPROVEN)} offshore station(s) used as authored - open water "
                  f"by distance from known land, not by a proven point:")
            for where, at, land in UNPROVEN:
                print(f"  {where:<34} {at[0]:8.3f},{at[1]:8.3f}   nearest land {land:4.0f} NM")
        if COAST_CHECKED:
            print(f"\n{len(COAST_CHECKED)} position(s) proved against the coastline extract:")
            for where, at, how in COAST_CHECKED:
                print(f"  {where:<40} {at[0]:8.3f},{at[1]:8.3f}   {how}")
        if RECOVERY_NOTES:
            print(f"\n{len(RECOVERY_NOTES)} recovery assignment(s) the files leave undeclared:")
            for note in RECOVERY_NOTES:
                print(f"   {note}")
        if CLOSURE_NOTES:
            print(f"\n{len(CLOSURE_NOTES)} unit(s) placed where they cannot take part:")
            for note in CLOSURE_NOTES:
                print(f"  {note}")
        if REACH_PROBLEMS or CLOSURE_PROBLEMS or PLACEMENT_PROBLEMS:
            sys.exit("geometry failed:\n  " + "\n  ".join(
                PLACEMENT_PROBLEMS + REACH_PROBLEMS + CLOSURE_PROBLEMS))

        # Built BEFORE the dry-run exit, because every air-tasking gate lives
        # in here - the row/section pairing, the role and fit checks, the
        # label vocabulary, the purchase allowlists. Returning first made
        # `--dry-run` ("resolve and check everything, emit nothing") the one
        # command that checked none of them: the same mutation passed dry-run
        # and failed the real build. It is pure, so building it early costs
        # nothing.
        campaign_text = campaign_ini([m for _n, _t, m in built], spec["EVENTS"],
                                     placements) + "\n"
        rows, missing = coverage(credits, spec.get("EXCUSES", {}))
        print(f"\n{TITLE}: reaches {len(rows)} mods and packs; "
              f"{len(missing)} enabled and not reached by this campaign")
        campaigns.append(dict(spec=spec, built=built, placements=placements,
                              credits=credits, rows=rows, missing=missing,
                              worst=worst, roster_text=roster_text,
                              campaign_text=campaign_text, missions=missions,
                              coast=list(COAST_CHECKED)))
        for token, why in credits.items():
            best = pack_credits.get(token)
            if best is None or STRENGTH[why[0]] < STRENGTH[best[0]]:
                pack_credits[token] = why

    # The pack's coverage rule: every enabled mod is placed by SOME campaign
    # in the pack, or excused in writing. A second campaign does not have to
    # reach all 135 mods on its own - the spec for Southern Reach says it must
    # not - but nothing in the load order may go unaccounted for.
    rows, missing = coverage(pack_credits, excuses)
    if missing and not (args.only or args.campaign):
        print("\nNOT INCORPORATED — every active mod must be placed or excused:")
        for what, mid, token, title in missing:
            print(f"   {what:<5} {mid:<34} {token:<18} {title}")
        sys.exit(f"{len(missing)} mod(s) uncovered")
    stale = [m for m in excuses if m in pack_credits or
             m in {r[0] for r in rows if r[2] in HOW_TEXT}]
    if stale and not (args.only or args.campaign):
        sys.exit("excuse no longer needed (the pack now reaches it): "
                 + ", ".join(sorted(stale)))
    if not (args.only or args.campaign):
        print(f"\ncoverage: {len(rows)} mods and packs, all accounted for by the pack")

    if args.dry_run:
        print("(dry run — nothing written)")
        return

    import shutil
    # Decide about the art BEFORE the tree is destroyed. This used to rmtree
    # the pack and only then try to import Pillow, so on a machine without it
    # the builder deleted all 24 PNGs and printed "keeping the committed
    # PNGs" - which was false, and which a contributor would only notice as 24
    # deletions in `git status`. If Pillow is missing the art is copied out and
    # put back, so the committed images survive a rebuild on any machine.
    try:
        import make_art
    except ImportError as exc:
        make_art, art_reason = None, str(exc)
    else:
        art_reason = None
    keep_art = {}
    if make_art is None:
        for c in campaigns:
            old_art = OUT / "campaigns" / c["spec"]["SLUG"] / "art"
            if old_art.is_dir():
                tmp = pathlib.Path(tempfile.mkdtemp(prefix="sest-art-"))
                shutil.copytree(old_art, tmp / "art")
                keep_art[c["spec"]["SLUG"]] = tmp
    # The briefing maps the same way: the renderer needs Pillow AND the
    # Natural Earth coastlines (fetched once, cached), and a machine with
    # neither keeps the committed maps rather than shipping a blank pane.
    sys.path.insert(0, str(ROOT / "integration" / "missions"))
    try:
        import briefing_maps
        geo, maps_reason = briefing_maps.available()
    except ImportError as exc:
        briefing_maps, geo, maps_reason = None, None, str(exc)
    keep_maps = {}
    if geo is None and OUT.exists():
        for f in OUT.rglob("*_briefing/*"):
            if f.suffix == ".png" or f.name == "BriefingMap_en.xml":
                keep_maps[f.relative_to(OUT)] = f.read_bytes()
    if OUT.exists():
        shutil.rmtree(OUT)

    def emit(base, name, text, mission, browsed):
        """One mission: its .ini and its briefing folder.

        `browsed` is whether this copy sits under missions/, where the mission
        browser walks the tree and reads every folder's _info.ini. Native draws
        the line in the same place: `missions/NATO/Dong Hoi_briefing/_info.ini`
        exists and carries `Hidden=True` AND `Type=Scenario`, while not one of
        the fifteen briefing folders under
        `campaigns/pacific-strike-task-force/missions/` has an _info.ini at
        all. The campaign loads those by path, so there is nothing to describe.
        """
        base.mkdir(parents=True, exist_ok=True)
        (base / f"{name}.ini").write_text(text, encoding="utf-8")
        brief = base / f"{name}_briefing"
        brief.mkdir(exist_ok=True)
        if browsed:
            (brief / "_info.ini").write_text(
                "[General]\nHidden=True\nType=Scenario\n\n"
                "[Language_en]\nName=Briefing folder\n"
                "Description=Folder with files of mission briefing.\n",
                encoding="utf-8")
        (brief / "BriefingText_en.xml").write_text(briefing_page(mission),
                                                   encoding="utf-8")

    def info(name, desc, general="[General]\nType=Scenario\n\n", tail=""):
        """A folder's _info.ini.

        [General] Type= because all twelve native mission folders declare one -
        ten Scenario, the two tutorial folders Tutorial - and these two
        declared nothing at all. English only for the same reason campaign.ini
        is: the base game's own Demo folder ships three languages of nine.
        """
        return general + f"[Language_en]\nName={name}\nDescription={desc}\n" + tail

    total_files = 0
    for c in campaigns:
        spec = c["spec"]
        set_campaign(spec)
        built, missions = c["built"], c["missions"]
        camp = OUT / "campaigns" / SLUG
        (camp / "missions").mkdir(parents=True)
        (camp / "art").mkdir(parents=True)
        folders = {}          # browser folder -> description

        # The core missions ship twice: once under campaigns/, which is what
        # the linear campaign loads, and once under missions/, so they are
        # also listed in the ordinary mission browser. Same bytes, one builder
        # - and it means the campaign is playable mission by mission even on
        # an install where the Mod Manager does not surface a mod-supplied
        # campaign.
        for name, text, mission in built:
            folder = browse_folder(mission)
            if mission["group"] == "dispatch":
                folders[folder] = spec["DISPATCH_DESC"]
                emit(OUT / "missions" / folder, name, text, mission, browsed=True)
            else:
                folders[folder] = (spec.get("BROWSE_DESC", {}).get(folder)
                                   or spec["INFO_DESC"])
                emit(camp / "missions", name, text, mission, browsed=False)
                emit(OUT / "missions" / folder, name, text, mission, browsed=True)
        for event in spec["EVENTS"]:
            (camp / "art" / f"{event['file']}.xml").write_text(event_page(event),
                                                               encoding="utf-8")

        # The art last, because a card is drawn FROM the mission file that
        # was just written. Pillow is the only thing here that is not stdlib;
        # without it the images set aside above are put back unchanged.
        if make_art is None:
            kept = keep_art.get(SLUG)
            if kept is not None:
                for f in sorted((kept / "art").iterdir()):
                    shutil.copy2(f, camp / "art" / f.name)
                shutil.rmtree(kept, ignore_errors=True)
                print(f"  {TITLE}: art not regenerated ({art_reason}) - restored "
                      f"{len(list((camp / 'art').glob('*.png')))} committed PNG(s). "
                      f"Install Pillow to rebuild them from the missions.")
            else:
                print(f"  {TITLE}: art not regenerated ({art_reason}) and none was "
                      "committed - this campaign has NO images. Install Pillow and rebuild.")
        else:
            cards = [dict(num=m["num"], code=mission_code(m), key=m["key"],
                          place=m["place"], group=m["group"],
                          series=m.get("series"), date=date_words(m["date"]),
                          ini=(camp / "missions" if m["group"] != "dispatch"
                               else OUT / "missions" / browse_folder(m)) / f"{name}.ini")
                     for name, _t, m in built]
            make_art.render_all(camp, cards, spec["EVENTS"], SLUG, TITLE, SUBTITLE,
                                prefix=ART_PREFIX, label=SERIES_LABEL)

        # The briefing map beside every mission - the right-hand pane of the
        # briefing screen, drawn from <mission>_briefing/BriefingMap_en.xml
        # and the image it binds (see integration/missions/briefing_maps.py).
        # Every stock mission ships one; these shipped none, and the pane was
        # blank. Drawn once into the campaign copy and mirrored byte-for-byte
        # into the browser copy, which check_campaign_coverage requires to be
        # identical.
        if geo is None:
            put_back = 0
            for rel, data in keep_maps.items():
                target = OUT / rel
                if target.parent.is_dir() and not target.exists():
                    target.write_bytes(data)
                    put_back += 1
            print(f"  {TITLE}: briefing maps not regenerated ({maps_reason}) - restored "
                  f"{put_back} committed file(s). Install Pillow (and let it fetch "
                  f"the coastlines once) to redraw them from the missions.")
        else:
            for name, _t, m in built:
                if m["group"] == "dispatch":
                    src = OUT / "missions" / browse_folder(m) / f"{name}_briefing"
                else:
                    src = camp / "missions" / f"{name}_briefing"
                ini = src.parent / f"{name}.ini"
                stem = briefing_maps.render(ini, src, m["key"], geo, series=MAP_SERIES,
                                            focus_nm=MAP_FOCUS_NM, inset_box=MAP_INSET)
                if m["group"] != "dispatch":
                    dst = OUT / "missions" / browse_folder(m) / f"{name}_briefing"
                    for fn in (f"{stem}.png", "BriefingMap_en.xml"):
                        shutil.copy2(src / fn, dst / fn)
        (camp / "campaign.ini").write_text(c["campaign_text"], encoding="utf-8")
        (camp / "player_task_force_roster.ini").write_text(c["roster_text"],
                                                           encoding="utf-8")
        (camp / "commander_settings.ini").write_text(spec["COMMANDER"], encoding="utf-8")
        for folder, desc in folders.items():
            (OUT / "missions" / folder / "_info.ini").write_text(info(folder, desc),
                                                                 encoding="utf-8")
        # This campaign's own closure, in the four lists a release needs.
        (camp / "REQUIRED-MODS.txt").write_text(
            campaign_requirements(c["rows"], c["missing"], TITLE), encoding="utf-8")
        COVERAGE_DOC.parent.mkdir(parents=True, exist_ok=True)
        COVERAGE_DOC.write_text(report(c["rows"], spec["MISSIONS"], c["worst"],
                                       unused=c["missing"], coast=c["coast"]),
                                encoding="utf-8")
        # Publisher-facing, so it stays in docs/ rather than in the download:
        # the Workshop's Required Items box takes one item at a time, and 133
        # of them typed by hand is 133 chances to fat-finger an id.
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        (DOCS_DIR / "required-mods-urls.txt").write_text(required_urls(c["rows"]),
                                                         encoding="utf-8")
        files = sum(1 for f in camp.rglob("*") if f.is_file())
        total_files += files
        print(f"  {TITLE}: {len(built)} missions, {len(spec['EVENTS'])} events, "
              f"{files} files under campaigns/{SLUG}; wrote "
              f"{COVERAGE_DOC.relative_to(ROOT)}")

    # The pack's own entry in the Mod Manager. No Type= here: that key
    # classifies a MISSION folder, and native mod roots do not carry one.
    # One entry carries every campaign in the pack, so its name and its
    # description name them all.
    titles = [c["spec"]["TITLE"] for c in campaigns]
    # The campaigns' own descriptions are the in-game bios and stay in the
    # world. What a player needs to install it belongs here, on the pack's
    # Mod Manager entry, once.
    blurb = (" ".join(c["spec"]["INFO_DESC"] for c in campaigns)
             + " Needs the Steam Workshop mods listed in REQUIRED-MODS.txt in "
               "this mod's folder; LOAD-ORDER.txt beside it is the Mod Manager "
               "order it was built and tested against.")
    (OUT / "_info.ini").write_text(
        info(" - ".join(titles), blurb, general="",
             tail="\n[Compatibility]\nApproximateVersion=0.8.2\n"),
        encoding="utf-8")
    # The pack-level lists, from the union of what every campaign reaches.
    set_campaign(dict(campaigns[0]["spec"], TITLE=" / ".join(titles)))
    (OUT / "REQUIRED-MODS.txt").write_text(requirements(rows), encoding="utf-8")
    (OUT / "LOAD-ORDER.txt").write_text(load_order_text(), encoding="utf-8")

    files = sum(1 for f in OUT.rglob("*") if f.is_file())
    print("wrote REQUIRED-MODS.txt and LOAD-ORDER.txt into the pack")
    print(f"\nbuilt {OUT.relative_to(ROOT)}: {files} files, "
          f"{sum(len(c['built']) for c in campaigns)} missions across "
          f"{len(campaigns)} campaign(s)")


CAMPAIGN_BLURB = ""


if __name__ == "__main__":
    main()
