#!/usr/bin/env python3
"""SEST RED LINE - The Other Watch.

Six Task Force Mode missions, November 2028 to February 2029, played by the
officer on the other side of Southern Watch and Southern Reach: the carrier
group commander whose signal the coalition intercepted on 22 November, "a
commander who would rather withdraw intact", and whose second signal it
intercepted on 25 February. Five missions sail his screen, four in the
Banda approaches and one off Fiordland; one is a detached submarine
operation in the Southern Ocean. Three side operations in the north joined
them on 20 Oct 2026 (campaign-upgrade-plan.md section 4.2, step RL-1): two
optionals flown by the enclave field's own aircraft, of which Datum's result
the next mission reads (The Ships from the North's is held until the test
card's 7.4 is answered, 21 Oct 2026), and a contingency for the screen's
own detachment.

Built to docs/campaigns/red-line/campaign-bible.md. The rules that hold the
data together are Southern Watch's and Southern Reach's (campaign_data.py's
docstring, southern_reach/AUTHORING.md) plus three of this campaign's own:

  1. The coalition's campaigns are canon and this one cannot move them. A
     Task Force defeat is replayed, so the canonical outcome of every mission
     here is its victory, and every victory is consistent with both. Any
     coalition unit either campaign names or depends on is a `spare`
     objective with a fatal entry: the player cannot sink it and keep the
     result. Nothing after 23 November relies on Fujian.

  2. Defence, escort, interception and evasion vary the pace. Declared hostile
     shooters can be engaged; named coalition assets remain protected so the
     coalition's story and reserved hull identities still hold.

  3. "Blue" is the player whatever the flag: Taskforce1 is China, and the
     coalition is Taskforce2. The north has no coastline extract, so RL01-RL04
     use Southern Watch's proven-point geography; RL05 and RL06 are proved
     against the southern coastline, as Southern Reach is.

Each mission is its own module (rl01_*.py ... rl06_*.py, and the side
operations rlo1_*.py, rlo2_*.py and rlc1_*.py) exporting MISSION:

    python3 integration/campaign/build_pack.py --dry-run --campaign red-line --only RL01
"""
import importlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from .lore import EVENTS  # noqa: E402
from .tables import (CALENDAR, MODULES, ROSTER, RESERVE_FLEET, TASKFORCE,  # noqa: E402
                     DIFFICULTIES, COMMANDER)

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
    "RED LINE - The Other Watch. A PLAN commander's campaign across the northern crisis "
    "and southern summer. Defend Fujian against missile craft, escort the Biak fuel run "
    "through torpedo and missile attacks, fight for the reconnaissance aircraft, and stop "
    "a ceasefire spoiler while protecting the withdrawal. A compact submarine passage and "
    "a contested tender rendezvous vary the pace. Two optional air operations and a short "
    "pilot-recovery race sit between the six core missions. Coalition non-belligerents and "
    "civil traffic remain protected; declared hostile shooters can be engaged."
)
BROWSE = {"Red Line": "Red Line"}
BROWSE_DESC = {"Red Line": "Carrier defence, convoy escort, fighter interception, withdrawal, "
               "submarine evasion and a contested rendezvous from the PLAN side of the crisis."}

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
    DIFFICULTIES=DIFFICULTIES, ROSTER=ROSTER, RESERVE_FLEET=RESERVE_FLEET,
    COMMANDER=COMMANDER, EVENTS=EVENTS, MISSIONS=MISSIONS, EXCUSES={})
