#!/usr/bin/env python3
"""SEST SOUTHERN REACH - and its second chapter, TASMAN SHIELD.

One continuous Task Force Mode campaign, December 2028 to March 2029, that
follows Southern Watch south: the Antarctic resupply season through the
Southern Ocean (chapter A, Southern Reach, SR01-SR12), then the homeland
approaches - New Zealand, the Tasman, Bass Strait and the Bight (chapter B,
Tasman Shield, TS01-TS12). One save carries the force from the first mission
to the last, which is why it is one campaign and not two.

Built to docs/campaigns/southern-reach/campaign-bible.md and the corrected
build specification it was written from. The rules that hold the data
together are Southern Watch's (see campaign_data.py's docstring) plus three
of this campaign's own:

  1. Geography is proved against the coastline, not a pool. Nothing in this
     repo had sailed Storm Bay, Cook Strait or the Macquarie Ridge, so every
     mission here declares geography="coast" and the builder checks each
     position against the committed Natural Earth extract (coast.py).

  2. No mechanic the engine has not been seen to have. Replenishment is a
     service window (position when the clock runs, as SW09), ice and weather
     are briefing text and force allocation, "undetected" is never scored,
     and the Antarctic coast itself is not a map anything sails to.

  3. New Zealand is a partner with its own aircraft and its own voice, not a
     stand-in fleet. The RNZAF P-8A (Squadron6 of the winning P-8 squadrons
     file, Nation=New Zealand) is the one NZ unit that resolves; RNZN hulls
     are not invented, and the story says where they are.

Each mission is its own module (sr01_*.py ... ts12_*.py) exporting MISSION,
fully populated - resolvers, window, role, generation, calendar - so a
mission can be read, reviewed and dry-run on its own:

    python3 integration/campaign/build_pack.py --dry-run --campaign southern-reach --only SR01
"""
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
# The unit/station helpers and the air-tasking rows are Southern Watch's, on
# purpose: one definition of a flight row, checked against the same roster
# files, cannot drift between the two campaigns.
from campaign_data import U, F, S, CAP, RECON, HELO, STRIKE  # noqa: E402,F401

from .lore import EVENTS  # noqa: E402
from .tables import CALENDAR, MODULES, ROSTER, TASKFORCE, DIFFICULTIES, COMMANDER  # noqa: E402

# While the campaign is being authored a module may not exist yet. With
# SR_ALLOW_MISSING set the package skips it (and the cross-mission checks
# below become notices), so one mission can be dry-run on its own; a real
# build never sets it, and a missing module fails the import as it should.
import os
_PARTIAL = bool(os.environ.get("SR_ALLOW_MISSING"))
MISSING, BROKEN = [], {}
MISSIONS = []
for _mod in MODULES:
    try:
        _m = importlib.import_module(f"{__name__}.{_mod}").MISSION
    except ModuleNotFoundError as _exc:
        if _PARTIAL and _exc.name == f"{__name__}.{_mod}":
            MISSING.append(_mod)
            continue
        raise
    except Exception as _exc:              # a module mid-edit must not stop the others
        if _PARTIAL:
            BROKEN[_mod] = f"{type(_exc).__name__}: {_exc}"
            continue
        raise
    _m.setdefault("geography", "coast")
    _cal = CALENDAR[_m["code"]]
    # The calendar is the schedule the bible publishes; a mission that
    # disagrees with it is a mission that drifted, and the build says so.
    for _k, _v in zip(("date", "points", "generation", "anchor"), _cal):
        if _k in _m and _m[_k] != _v:
            raise SystemExit(f"{_m['code']}: {_k}={_m[_k]!r} disagrees with the "
                             f"calendar's {_v!r}")
        _m[_k] = _v
    MISSIONS.append(_m)

_codes = [m["code"] for m in MISSIONS]
if len(set(_codes)) != len(_codes):
    raise SystemExit("southern_reach: duplicate mission code")
# A variable read is a promise an earlier mission wrote it.
_declared = {v for m in MISSIONS for v in m.get("declares", [])}
for _m in MISSIONS:
    _reads = [r["variable"] for r in _m.get("reveal_if", [])]
    _reads += [u["spawn_if"][0] for u in _m["units"] if u.get("spawn_if")]
    if _m.get("window", {}).get("rearm_if"):
        _reads.append(_m["window"]["rearm_if"][0])
    for _v in _reads:
        if _v not in _declared:
            if _PARTIAL:
                print(f"  (partial build) {_m['code']} reads {_v!r}, not declared "
                      "by any mission present")
                continue
            raise SystemExit(f"{_m['code']}: reads campaign variable {_v!r}, "
                             "which no mission declares")
if MISSING:
    print(f"  (partial build) {len(MISSING)} Southern Reach module(s) not written yet: "
          + ", ".join(MISSING))
for _mod, _err in BROKEN.items():
    print(f"  (partial build) {_mod} failed to import and was skipped: {_err}")

INFO_DESC = (
    "SOUTHERN REACH - Tasman Shield. December 2028. Nine days after the northern ceasefire,"
    " the network that tried to close the Arafura has come south under a new flag. A "
    "fisheries and research protection group - a frigate, two corvettes, an intelligence "
    "trawler and, in the new year, the carrier Liaoning - is stopping Antarctic-bound ships"
    " off Tasmania. Its contractor, Austral Meridian Services, sells compliance corridors "
    "while a Russian submarine works the Macquarie Ridge. The Australian task group that "
    "held the north escorts the resupply season from Storm Bay to the ice edge at 60 South."
    " As the "
    "formation turns north, the escort task follows it through Fiordland, Cook Strait, the "
    "Tasman, Bass Strait and the Bight. New Zealand's Poseidons support the search among "
    "ferries, tankers, gas platforms and undersea cables. Operations near Auckland and "
    "Adelaide decide which opposing detachments rejoin the carrier group for the fleet "
    "action in the western Tasman."
)

BROWSE = {"Southern Reach": "Southern Reach", "Tasman Shield": "Tasman Shield"}
BROWSE_DESC = {
    "Southern Reach": (
        "The Antarctic resupply season, December 2028 to January 2029. Escort fuel, "
        "stores and people from Storm Bay across the Macquarie Ridge and Southern Ocean "
        "to the ice edge, while identifying the naval force behind the declared fisheries"
        " protection zone."
    ),
    "Tasman Shield": (
        "The homeland approaches, January to March 2029. Protect shipping through "
        "Fiordland, Cook Strait, the Tasman, Bass Strait and the Great Australian Bight "
        "as the protection group turns north and the rules of engagement change."
    ),
}

ROOT = HERE.parents[2]
CAMPAIGN = dict(
    SLUG="sest-southern-reach", TITLE="Southern Reach",
    DISPATCHES="Southern Reach - Dispatches",
    SUBTITLE="Tasman Shield  ·  December 2028 - March 2029",
    ART_PREFIX="southern_reach", SERIES_LABEL="SOUTHERN REACH",
    MAP_SERIES="SEST SOUTHERN REACH", GEOGRAPHY="coast", BROWSE=BROWSE,
    BROWSE_DESC=BROWSE_DESC,
    DOCS_DIR=ROOT / "docs" / "campaigns" / "southern-reach",
    COVERAGE_DOC=ROOT / "docs" / "campaigns" / "southern-reach" / "coverage.md",
    CAMPAIGN_NAME_EN="Southern Reach - Tasman Shield (Royal Australian Navy)",
    CAMPAIGN_DIFFICULTY="3", MAP_FOCUS_NM=350, MAP_INSET=(100, -70, 180, -25),
    INFO_DESC=INFO_DESC, DISPATCH_DESC="", TASKFORCE=TASKFORCE,
    DIFFICULTIES=DIFFICULTIES, ROSTER=ROSTER, COMMANDER=COMMANDER,
    EVENTS=EVENTS, MISSIONS=MISSIONS, EXCUSES={})
