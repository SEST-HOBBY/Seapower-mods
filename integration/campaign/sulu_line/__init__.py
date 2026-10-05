#!/usr/bin/env python3
"""SEST SULU LINE - The Island Road.

Seven Task Force Mode missions, October to November 2028, in the Sulu Sea
and the West Philippine Sea: the same six weeks as Southern Watch, at the
other end of the archipelago. With most of America's ready combat power
drawn north, a Philippine-led task group - with a Royal Thai Navy
detachment and, from the second week, one RAN frigate - keeps the island
supply road open from Puerto Princesa to Jolo and Ayungin while the Meridian
network arms the Sulu coast and Chinese ships push on the shoals.

Built on Southern Watch's and Southern Reach's rules (campaign_data.py's
docstring, southern_reach/AUTHORING.md) plus three of this campaign's own:

  1. There is no free rearm. No window rearms the force; what a ship fires
     stays fired until a supply ship the player bought comes alongside, or
     an escorted convoy holds its service window (SL04). Supply ships are
     sold only in three windows. This is the campaign, not a rule on top
     of it.

  2. Fire missions are real targets. Every naval gunfire mission (SL02,
     SL06) is won by destroying land units ashore, in reach of a 76 mm gun
     from water a frigate can steam; what the gun fires comes back only
     from a supply ship.

  3. "Blue" is the player: Taskforce1 is the Philippines. The north has no
     coastline extract, so every mission uses the proven-point pool.

Each mission is its own module (sl01_*.py ... sl07_*.py) exporting MISSION:

    python3 integration/campaign/build_pack.py --dry-run --campaign sulu-line --only SL01
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
    for _k, _v in zip(("date", "points", "generation", "anchor"), _cal):
        if _k in _m and _m[_k] != _v:
            raise SystemExit(f"{_m['code']}: {_k}={_m[_k]!r} disagrees with the "
                             f"calendar's {_v!r}")
        _m[_k] = _v
    # The campaign's one rule, enforced here so no mission can drift from
    # it: nothing after the first window rearms for free.
    _w = _m.get("window", {})
    if _m["code"] != "SL01" and _w.get("rearm"):
        raise SystemExit(f"{_m['code']}: window rearms for free - Sulu Line's rearm "
                         "is a supply ship or a held service window (rearm_if)")
    MISSIONS.append(_m)

_codes = [m["code"] for m in MISSIONS]
if len(set(_codes)) != len(_codes):
    raise SystemExit("sulu_line: duplicate mission code")
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
    print(f"  (partial build) {len(MISSING)} Sulu Line module(s) not written yet: "
          + ", ".join(MISSING))

INFO_DESC = (
    "SULU LINE - The Island Road. October 2028. With most of America's ready combat power "
    "drawn north, the Philippine Navy holds the island supply road alone: Puerto Princesa "
    "to the Balabac outpost, the gun line off Jolo, the boats to Ayungin Shoal. The Meridian"
    " network is arming the Sulu coast and Chinese ships are pushing on the shoals. A "
    "Philippine-led task group with a Royal Thai Navy detachment, and later one Australian "
    "frigate, escorts the convoys and fires for the Marines ashore. There is no free rearm. "
    "What a ship fires stays fired until a supply ship you bought comes alongside at sea - "
    "BRP Tarlac, the Thai oiler Chula or a chartered barge carrier - or a convoy you "
    "escorted holds its service window. Supply ships are sold at three points in the "
    "campaign. Lose one and what it carried is gone."
)

BROWSE = {"Sulu Line": "Sulu Line"}
BROWSE_DESC = {
    "Sulu Line": (
        "The Philippine Navy's side of the 2028 crisis, October to November: convoys, "
        "naval gunfire support and shoal resupply in the Sulu Sea and the West Philippine "
        "Sea, with no free rearm."
    ),
}

ROOT = HERE.parents[2]
CAMPAIGN = dict(
    SLUG="sest-sulu-line", TITLE="Sulu Line",
    DISPATCHES="Sulu Line - Dispatches",
    SUBTITLE="The Island Road  ·  October - November 2028",
    ART_PREFIX="sulu_line", SERIES_LABEL="SULU LINE",
    MAP_SERIES="SEST SULU LINE", GEOGRAPHY="pool", BROWSE=BROWSE,
    BROWSE_DESC=BROWSE_DESC,
    DOCS_DIR=ROOT / "docs" / "campaigns" / "sulu-line",
    COVERAGE_DOC=ROOT / "docs" / "campaigns" / "sulu-line" / "coverage.md",
    CAMPAIGN_NAME_EN="Sulu Line - The Island Road (Philippine Navy)",
    CAMPAIGN_DIFFICULTY="3", MAP_FOCUS_NM=300, MAP_INSET=(108, -2, 130, 20),
    ROSTER_SOURCE="sulu_line/tables.py",
    INFO_DESC=INFO_DESC, DISPATCH_DESC="", TASKFORCE=TASKFORCE,
    DIFFICULTIES=DIFFICULTIES, ROSTER=ROSTER, COMMANDER=COMMANDER,
    EVENTS=EVENTS, MISSIONS=MISSIONS, EXCUSES={},
    REARM_RULES=(
        "- Rearm: never free. Ships rearm only from a supply ship you own, alongside at "
        "sea, or from the escorted charter in Service at Sea.",
        "- There is no free rearm in this campaign. A ship takes ammunition back by coming "
        "within half a mile of a supply ship at eight knots or less: BRP Tarlac or Davao del"
        " Sur, HTMS Chula, or a chartered C8 barge carrier. Their stocks are finite and are "
        "not refilled. Supply ships are on sale before The Island Road, Service at Sea and "
        "The Aborlan Battery only; one that is sunk is gone until the next sale."))
