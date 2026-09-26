#!/usr/bin/env python3
"""SEST RED LINE - The Other Watch.

Six Task Force Mode missions, November 2028 to January 2029, played by the
officer on the other side of Southern Watch and Southern Reach: the carrier
group commander whose signal the coalition intercepted on 22 November, "a
commander who would rather withdraw intact", and whose second signal it
intercepted on 25 February. Five missions sail his screen, four in the
Banda approaches and one off Fiordland; one is a detached submarine
operation in the Southern Ocean.

Built to docs/campaigns/red-line/campaign-bible.md. The rules that hold the
data together are Southern Watch's and Southern Reach's (campaign_data.py's
docstring, southern_reach/AUTHORING.md) plus three of this campaign's own:

  1. The coalition's campaigns are canon and this one cannot move them. A
     Task Force defeat is replayed, so the canonical outcome of every mission
     here is its victory, and every victory is consistent with both. Any
     coalition unit either campaign names or depends on is a `spare`
     objective with a fatal entry: the player cannot sink it and keep the
     result. Nothing after 23 November relies on Fujian.

  2. Winning is restraint, deception, escort or evasion. Nothing here is won
     by a kill the coalition's story would have to account for; the one ship
     the player must sink (RL04) is a Meridian coaster that no coalition page
     names, on the night the ceasefire began.

  3. "Blue" is the player whatever the flag: Taskforce1 is China, and the
     coalition is Taskforce2. The north has no coastline extract, so RL01-RL04
     use Southern Watch's proven-point geography; RL05 and RL06 are proved
     against the southern coastline, as Southern Reach is.

Each mission is its own module (rl01_*.py ... rl06_*.py) exporting MISSION:

    python3 integration/campaign/build_pack.py --dry-run --campaign red-line --only RL01
"""
import importlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from .lore import EVENTS  # noqa: E402
from .tables import CALENDAR, MODULES, ROSTER, TASKFORCE, DIFFICULTIES, COMMANDER  # noqa: E402

# While a mission is being written the others may not exist yet. With
# SR_ALLOW_MISSING set (the builder's own switch for a partial campaign) the
# package skips a missing module; a real build never sets it.
_PARTIAL = bool(os.environ.get("SR_ALLOW_MISSING"))
MISSING = []
MISSIONS = []
for _mod in MODULES:
    try:
        _m = importlib.import_module(f"{__name__}.{_mod}").MISSION
    except ModuleNotFoundError as _exc:
        if _PARTIAL and _exc.name == f"{__name__}.{_mod}":
            MISSING.append(_mod)
            continue
        raise
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
    raise SystemExit("red_line: duplicate mission code")
# A variable read is a promise an earlier mission wrote it. A third campaign
# is a separate save: it cannot read Southern Watch's or Southern Reach's
# variables, so every one it reads is its own.
_declared = {v for m in MISSIONS for v in m.get("declares", [])}
for _m in MISSIONS:
    _reads = [r["variable"] for r in _m.get("reveal_if", [])]
    _reads += [u["spawn_if"][0] for u in _m["units"] if u.get("spawn_if")]
    for _v in _reads:
        if _v not in _declared and not _PARTIAL:
            raise SystemExit(f"{_m['code']}: reads campaign variable {_v!r}, "
                             "which no mission declares")
if MISSING:
    print(f"  (partial build) {len(MISSING)} Red Line module(s) not written yet: "
          + ", ".join(MISSING))

INFO_DESC = (
    "RED LINE - The Other Watch. November 2028 to January 2029, from the other bridge. "
    "A Chinese carrier group commander is sent into the Banda approaches under a "
    "protection-and-evacuation mandate and an order that says the group will not fire first."
    " He puts a class on the Australian submarine trailing his carrier, gets fuel into the "
    "Biak enclave ahead of the coalition's relief window, builds the picture of a convoy that"
    " other people will attack, and in the first hours of the ceasefire stops the one ship in"
    " his own company that wants the war back. In December he is sent south with Liaoning "
    "to take over the fisheries protection group, and its submarines have to pass the "
    "coalition's patrol aircraft without being classified. Every operation is won by "
    "restraint, escort or evasion, and there is nearly always a coalition aircraft "
    "overhead, recording."
)

BROWSE = {"Red Line": "Red Line"}
BROWSE_DESC = {
    "Red Line": (
        "The carrier group commander's side of the northern crisis and the southern summer, "
        "November 2028 to January 2029. Escort, identification and evasion under orders "
        "that say the group does not fire first."
    ),
}

ROOT = HERE.parents[2]
CAMPAIGN = dict(
    SLUG="sest-red-line", TITLE="Red Line",
    DISPATCHES="Red Line - Dispatches",
    SUBTITLE="The Other Watch  ·  November 2028 - February 2029",
    ART_PREFIX="red_line", SERIES_LABEL="RED LINE",
    MAP_SERIES="SEST RED LINE", GEOGRAPHY="pool", BROWSE=BROWSE,
    BROWSE_DESC=BROWSE_DESC,
    DOCS_DIR=ROOT / "docs" / "campaigns" / "red-line",
    COVERAGE_DOC=ROOT / "docs" / "campaigns" / "red-line" / "coverage.md",
    CAMPAIGN_NAME_EN="Red Line - The Other Watch (People's Liberation Army Navy)",
    CAMPAIGN_DIFFICULTY="3", MAP_FOCUS_NM=350, MAP_INSET=(100, -50, 172, 8),
    ROSTER_SOURCE="red_line/tables.py",
    INFO_DESC=INFO_DESC, DISPATCH_DESC="", TASKFORCE=TASKFORCE,
    DIFFICULTIES=DIFFICULTIES, ROSTER=ROSTER, COMMANDER=COMMANDER,
    EVENTS=EVENTS, MISSIONS=MISSIONS, EXCUSES={})
