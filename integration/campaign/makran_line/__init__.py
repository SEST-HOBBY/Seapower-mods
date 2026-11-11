#!/usr/bin/env python3
"""SEST MAKRAN LINE - The Fuel Road.

Four Task Force Mode missions, 24 October to 14 November 2028, in the North
Arabian Sea: inside Southern Watch's six weeks, at the other end of the
Indian Ocean. With America's ready combat power drawn north, insurers are
refusing cover on the tanker road from the Gulf to Karachi, and the
fictional Meridian Maritime Group - the same network of freight companies
and security contractors Southern Watch fights in the Arafura - is offering
the tankers its "escorts". A Pakistan Navy task group, Task Force 88, keeps
the road open: the Karachi approaches, the Gwadar anchorage, a submarine
trail off the Makran coast and the last convoy into Port Qasim.

The opponent is Meridian alone, in armed merchants and trawlers. No Indian
or Iranian state unit is placed, and there is no insurgency ashore: the
campaign is a maritime security operation against a non-state network.

Built on Southern Watch's, Southern Reach's and Sulu Line's rules
(campaign_data.py's docstring, southern_reach/AUTHORING.md), plus three of
its own:

  1. Every unit the player buys registers Pakistan. The roster is the
     Pakistani Pack's and nothing else; what a realistic 2028 task group
     would add that the collection does not have is stated in the bible,
     not stood in by another navy's hull.

  2. Rearm is free at every force allocation. The collection has no
     Pakistani supply ship (no PNS Moawin or Nasr), so the ships turn round
     at Karachi between missions, and every window says so.

  3. "Blue" is the player: Taskforce1 is Pakistan, Taskforce2 is Meridian,
     and every Meridian unit carries an explicit Nation=Meridian so the
     flag remap (integration/common/flags.py) never flies one as Russian.
     The proven-point pool has no point off Gwadar, so every mission is
     proved against the coastline (geo/arabian_theatre_coast.json,
     GEOGRAPHY="coast").

Each mission is its own module (mk01_*.py ... mk04_*.py) exporting MISSION:

    python3 integration/campaign/build_pack.py --dry-run --campaign makran-line --only MK01
"""
import importlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from .lore import EVENTS  # noqa: E402
from .tables import (CALENDAR, MODULES, ROSTER, TASKFORCE,  # noqa: E402
                     DIFFICULTIES, COMMANDER)

# While a mission is being written the others may not exist yet. With
# SR_ALLOW_MISSING set (the builder's own switch for a partial campaign) the
# package skips a missing module; a real build never sets it.
_PARTIAL = bool(os.environ.get("SR_ALLOW_MISSING"))
MISSING = []
MISSIONS = []


def check_fields(mission):
    """A Pakistani field holds only what the player buys or the mission
    places. A field written without a CustomAirGroup gets its unit file's
    [AirGroup] for free - the stock airfield_small_1's F-4D/Es, RA-5Cs,
    EA-6Bs, E-3A, P-3Cs, SH-3Hs and CH-46s, a 1970s U.S. wing on a 2028
    Pakistani field (Sulu Line's lesson of 27 Oct 2026). So every player-side
    field says what it holds - air_group=[] for an empty one - and one that
    does not stops the build. A field is any unit whose type names an
    airfield or an airbase."""
    for u in mission["units"]:
        if (u["side"] == "blue" and u.get("air_group") is None
                and any(w in u["type"] for w in ("airfield", "airbase"))):
            raise SystemExit(f"{mission['code']}: {u['type']} inherits its stock air "
                             "group - give it air_group=[] or its own flights")


def check_opponent(mission):
    """The owner's decision of 11 Nov 2026: Meridian is the only opponent,
    and every Meridian unit says so. A red unit without nation="Meridian"
    would fly whatever its file registers (an armed Okean registers Soviet,
    which flags.py maps to Russia), and the campaign places no state's
    forces against the player."""
    for u in mission["units"]:
        if u["side"] == "red" and u.get("nation") != "Meridian":
            raise SystemExit(f"{mission['code']}: red {u['type']} at {u['station']} flies "
                             f"{u.get('nation')!r} - every opponent here is Meridian's")


for _mod in MODULES:
    try:
        _m = importlib.import_module(f"{__name__}.{_mod}").MISSION
    except ModuleNotFoundError as _exc:
        if _PARTIAL and _exc.name == f"{__name__}.{_mod}":
            MISSING.append(_mod)
            continue
        raise
    _cal = CALENDAR[_m["code"]]
    for _k, _v in zip(("date", "points", "generation", "anchor"), _cal):
        if _k in _m and _m[_k] != _v:
            raise SystemExit(f"{_m['code']}: {_k}={_m[_k]!r} disagrees with the "
                             f"calendar's {_v!r}")
        _m[_k] = _v
    # The campaign's rule, enforced so no window can drift from it: with no
    # Pakistani supply ship in the collection, every force allocation rearms.
    _w = _m.get("window", {})
    if _w.get("buy") and not _w.get("rearm"):
        raise SystemExit(f"{_m['code']}: a force allocation that does not rearm - "
                         "Makran Line has no supply ship, so the turn round at "
                         "Karachi rearms every window")
    check_fields(_m)
    check_opponent(_m)
    MISSIONS.append(_m)

_codes = [m["code"] for m in MISSIONS]
if len(set(_codes)) != len(_codes):
    raise SystemExit("makran_line: duplicate mission code")
# A variable read is a promise an earlier mission wrote it. This campaign is
# its own save, so every variable it reads is its own.
_declared = {v for m in MISSIONS for v in m.get("declares", [])}
for _m in MISSIONS:
    _reads = [r["variable"] for r in _m.get("reveal_if", [])]
    _reads += [u["spawn_if"][0] for u in _m["units"] if u.get("spawn_if")]
    if _m.get("window", {}).get("rearm_if"):
        _reads.append(_m["window"]["rearm_if"][0])
    for _v in _reads:
        if _v not in _declared and not _PARTIAL:
            raise SystemExit(f"{_m['code']}: reads campaign variable {_v!r}, "
                             "which no mission declares")
if MISSING:
    print(f"  (partial build) {len(MISSING)} Makran Line module(s) not written yet: "
          + ", ".join(MISSING))

INFO_DESC = (
    "MAKRAN LINE - The Fuel Road. October 2028. With America's ready combat power drawn "
    "north, insurers are refusing cover on the tanker road from the Gulf to Karachi, and the"
    " Meridian Maritime Group is offering the tankers its own armed escorts. A Pakistan Navy"
    " task group, Task Force 88, is sent to keep the road open: the Karachi approaches, the "
    "Gwadar anchorage, a submarine trail off the Makran coast and the last convoy into Port "
    "Qasim. The opponent is Meridian alone, in armed merchants and trawlers. The task group "
    "is what the collection can field for 2028: the Tughril-class frigates, PNS Alamgir, "
    "their Z-9CE and Sea King flights, and the Air Force's JF-17s and ZDK-03 from the second"
    " week. There is no Pakistani supply ship, so the ships rearm at Karachi between "
    "missions. Meridian, its ships, the merchants and the commander are fiction."
)

BROWSE = {"Makran Line": "Makran Line"}
BROWSE_DESC = {
    "Makran Line": (
        "The Pakistan Navy's side of the 2028 crisis, October to November: tanker convoys, "
        "the Gwadar anchorage and a submarine trail in the North Arabian Sea, against the "
        "Meridian network's armed merchants and trawlers."
    ),
}

ROOT = HERE.parents[2]
CAMPAIGN = dict(
    SLUG="sest-makran-line", TITLE="Makran Line",
    DISPATCHES="Makran Line - Dispatches",
    SUBTITLE="The Fuel Road  ·  October - November 2028",
    ART_PREFIX="makran_line", SERIES_LABEL="MAKRAN LINE",
    MAP_SERIES="SEST MAKRAN LINE", GEOGRAPHY="coast", BROWSE=BROWSE,
    BROWSE_DESC=BROWSE_DESC,
    DOCS_DIR=ROOT / "docs" / "campaigns" / "makran-line",
    COVERAGE_DOC=ROOT / "docs" / "campaigns" / "makran-line" / "coverage.md",
    CAMPAIGN_NAME_EN="Makran Line - The Fuel Road (Pakistan Navy)",
    CAMPAIGN_DIFFICULTY="3", MAP_FOCUS_NM=250, MAP_INSET=(55, 15, 75, 30),
    ROSTER_SOURCE="makran_line/tables.py",
    INFO_DESC=INFO_DESC, DISPATCH_DESC="", TASKFORCE=TASKFORCE,
    DIFFICULTIES=DIFFICULTIES, ROSTER=ROSTER, COMMANDER=COMMANDER,
    EVENTS=EVENTS, MISSIONS=MISSIONS, EXCUSES={},
    REARM_RULES=(
        "- Rearm: free at every force allocation. The ships turn round at Karachi between "
        "missions.",
        "- Rearming is free before every mission with a force allocation. The collection has"
        " no Pakistani supply ship, so the task group does not rearm at sea: the ships take "
        "ammunition back at Karachi between missions, and what they fire in a mission stays "
        "fired until the next force allocation."))
