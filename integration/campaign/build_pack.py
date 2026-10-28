#!/usr/bin/env python3
"""Build the SEST campaign pack: Southern Watch, Southern Reach, Red Line
and Sulu Line.

Southern Reach carries Tasman Shield as its second chapter. Their orders of
battle are drawn from the whole collection. An Open Allocation twin is a
campaign's opt-in (spec OPEN_ALLOCATION), and no campaign in the pack takes
one since 21 Oct 2026 (see "open allocation" below).

WHY THIS EXISTS

190 Workshop mods and 20 local packs are a lot of content to own and
never see. The Banda vignettes reached for the mods the sandbox left idle, one
family per scenario; this goes the rest of the way: campaigns that between them
place something from EVERY active mod that can put something on the map, and
name the ones that cannot, with the reason, in their coverage reports
(docs/campaign-coverage.md and docs/campaigns/*/coverage.md).

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
point: some mods here are invisible in game precisely because something above
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
sys.path.insert(0, str(ROOT / "integration" / "mission-seeds"))
from refine_civ_traffic import load_order  # noqa: E402
import fix_land_positions  # noqa: E402  (firm ground for land units; needs global-land-mask)
sys.path.insert(0, str(ROOT / "integration"))
from common import quotes  # noqa: E402
from common import flags  # noqa: E402

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
ROSTER_SOURCE = "campaign_data.py"      # the roster file's "edit ..." line


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
    # Where a reader goes to change the roster. Southern Watch's is
    # campaign_data.py; another campaign names its own module, and one that
    # does not is named by its title rather than sent to Southern Watch's.
    g["ROSTER_SOURCE"] = spec.get("ROSTER_SOURCE") or (
        _DEFAULTS["ROSTER_SOURCE"] if spec.get("SLUG") == _DEFAULTS["SLUG"]
        else f"the {g['TITLE']} campaign's roster")


_DEFAULTS = {k: globals()[k] for k in (
    "SLUG", "TITLE", "DISPATCHES", "SUBTITLE", "ART_PREFIX", "SERIES_LABEL",
    "MAP_SERIES", "GEOGRAPHY", "BROWSE", "DOCS_DIR", "COVERAGE_DOC",
    "CAMPAIGN_NAME_EN", "CAMPAIGN_DIFFICULTY", "MAP_FOCUS_NM", "MAP_INSET",
    "ROSTER_SOURCE")}
_DEFAULTS.update(TASKFORCE=None, DIFFICULTIES=None, ROSTER=None)
# What main() writes into docs/ for each campaign. See set_campaign().
_OWN_FILES = ("DOCS_DIR", "COVERAGE_DOC")


# ---------------------------------------------------------------- rules page
# The Campaign Rules button on the campaign map opens campaign_rules_<lang>.xml
# from the campaign's own folder. The stock task-force campaign ships one (a
# Noesis page: overview, commander, unit prices, campaign rules); these
# campaigns did not, so the button opened nothing (user report, 27 Sep). Each
# page is the stock one with only its campaign-specific passages replaced -
# the prices table, refund percentages and the survivor reward are Bindings the
# game fills from this campaign's own campaign.ini and roster. A template the
# game has changed stops the build rather than shipping a half-edited page.
RULES_TEMPLATE = (ROOT / "mods-source" / "_vanilla" / "original" / "campaigns"
                  / "pacific-strike-task-force" / "campaign_rules_en.xml")
RULES_WELCOME = {
    "sest-southern-watch": (
        "October 2028. With most of America's ready combat power drawn north, the sea "
        "lanes above Australia are closing. You command the Royal Australian Navy task "
        "force sent to keep them open."),
    "sest-southern-reach": (
        "December 2028. Nine days after the northern ceasefire, the network that tried to "
        "close the Arafura has come south. You command the Royal Australian Navy task "
        "force on the Southern Ocean and Tasman routes."),
    "sest-red-line": (
        "November 2028, from the other bridge. You command a People's Liberation Army Navy "
        "carrier group in the Banda approaches, under an order that says it will not fire "
        "first."),
    "sest-sulu-line": (
        "October 2028. With the Seventh Fleet drawn north, the Philippine Navy holds the "
        "island supply road alone. You command its Sulu Sea task group, and nothing it "
        "fires is replaced except by the supply ships you buy and keep afloat."),
}


def _xml_text(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def campaign_rules(spec, open_allocation=False, allied=0):
    """This campaign's campaign_rules_en.xml, built from the stock page.

    `open_allocation` is the Open Allocation twin's page: the same rules, with
    the availability lines saying the whole roster - its allied fleet included
    - is on sale from the first force allocation. `allied` is how many
    allied-fleet units the roster adds."""
    t = RULES_TEMPLATE.read_text(encoding="utf-8")
    navy = re.search(r"^NavyName\w+=(.+)$", spec["COMMANDER"], re.M).group(1).strip()

    def swap(old, new, what):
        nonlocal t
        if t.count(old) != 1:
            raise SystemExit(f"campaign rules: the stock page's {what} has changed "
                             f"({t.count(old)} matches) - rebase campaign_rules()")
        t = t.replace(old, new)

    line = ('<TextBlock Text="{}" FontSize="15" Foreground="#D8DDE8" '
            'TextWrapping="Wrap" Margin="0,0,0,{}"/>')
    title = spec["TITLE"] + (" - Open Allocation" if open_allocation else "")
    swap('Text="Pacific Strike \'85 - Task Force Mode"',
         f'Text="{_xml_text(title)} - Task Force Mode"', "title")
    swap('Text="War has broken out in Europe and the Pacific. You are the Allies\' first '
         'line of defense, stationed in Japan at the outbreak of hostilities."',
         f'Text="{_xml_text(RULES_WELCOME[spec["SLUG"]])}"', "welcome")
    # A campaign with its own rearm rule (Sulu Line: no free rearm at all)
    # says so where the stock page says rearming is free.
    if spec.get("REARM_RULES"):
        short, long = spec["REARM_RULES"]
        swap('Text="- Rearm: available before certain missions, for free."',
             f'Text="{_xml_text(short)}"', "rearm line")
        swap('Text="- Rearming is only available between certain missions. Task Force '
             'Manager will show a green \'Rearmed\' icon when your ships have been rearmed '
             'before the mission."', f'Text="{_xml_text(long)}"', "rearming paragraph")
    start = t.find('<TextBlock Text="Coalition Command"')
    end_marker = ('<TextBlock Text="- Japanese or Australian commanders increase the '
                  'challenge without changing the missions themselves."')
    end = t.find(end_marker)
    if start < 0 or end < 0:
        raise SystemExit("campaign rules: the stock commander section has changed - "
                         "rebase campaign_rules()")
    end = t.index("/>", end) + 2
    indent = "\n            "
    # The stock discount line, verbatim: the percentage is the game's own
    # Binding, so the page shows whatever SameNationUnitDiscount it applies.
    stock_discount = re.search(r'<TextBlock FontSize="15"[^>]*>\s*<Run Text="- Commanders '
                               r'receive a "/>.*?</TextBlock>', t[start:end], re.S)
    separator = ('<Border Height="1" Background="{StaticResource Brush.Glyph.Normal}" '
                 'Opacity="0.45" Margin="0,0,0,14"/>')
    if not stock_discount or separator not in t[start:end]:
        raise SystemExit("campaign rules: the stock discount section has changed - "
                         "rebase campaign_rules()")
    discount = same_nation_discount(spec["COMMANDER"])
    nation = re.search(r"^CommanderNations=(.+)$", spec["COMMANDER"], re.M).group(1).strip()
    lines = [
        '<TextBlock Text="Command" FontSize="17" FontWeight="Bold" Foreground="White" '
        'TextWrapping="Wrap" Margin="0,0,0,6"/>',
        line.format(_xml_text(f"You command the {navy} task force for the whole "
                              "campaign. The commander's nation is fixed."), 14),
        line.format("Commander nationality does not change mission rules, ship "
                    "performance, aircraft performance, or combat capability.", 14),
    ]
    if discount:
        nations = roster_nations(spec["ROSTER"])
        own = sum(1 for n in nations.values() if n.lower() == nation.lower())
        foreign = collections.Counter(nation_name(n) for n in nations.values()
                                      if n.lower() != nation.lower())
        lines += [separator + "\n",
                  '<TextBlock Text="National Purchase Discount" FontSize="17" '
                  'FontWeight="Bold" Foreground="White" TextWrapping="Wrap" '
                  'Margin="0,0,0,6"/>',
                  stock_discount.group(0),
                  line.format(_xml_text(
                      f"- Every unit on this campaign's roster is registered to {nation} "
                      "by its squadron or hull variant, so the discount applies to all "
                      "of it." if not foreign else
                      f"- The discount covers the {own} class{'es' if own != 1 else ''} "
                      f"registered to {nation}. The {sum(foreign.values())} "
                      f"class{'es' if sum(foreign.values()) != 1 else ''} registered to "
                      "other nations - from "
                      + ", ".join(f"{n} ({c})" for n, c in sorted(
                          foreign.items(), key=lambda x: (-x[1], x[0])))
                      + (" - cost their listed price." if sum(foreign.values()) != 1
                         else " - costs its listed price.")), 14)]
    else:
        lines.append(line.format("- No national purchase discount applies: every unit "
                                 "costs its listed price.", 14))
    t = t[:start] + indent.join(lines) + t[end:]
    held = (", except what the story sells only at its own windows"
            if spec.get("OPEN_HOLD") else "")
    import mission_depth
    nation = re.search(r"^CommanderNations=(.+)$", spec["COMMANDER"], re.M).group(1).strip()
    priced = {e["unit"]: e for e in spec["ROSTER"]}
    buying = sorted((m for m in spec.get("MISSIONS", []) if m.get("window", {}).get("buy")),
                    key=mission_depth._when)
    first = buying[0] if buying else None
    # The campaign's own opening (mission_depth.open_from; 21 Oct 2026, step
    # 2 of "Build open allocation into standard campaign"): from that window
    # every force allocation offers the whole roster and the fleet the
    # reserve admits, as the twin did from the first, and the availability
    # line says so in place of "only what the window allows".
    opening = None if open_allocation else mission_depth.open_from(spec)
    reserve = (mission_depth.reserve_offer(spec)
               if spec.get("RESERVE_OPENS") and not open_allocation else [])

    def reserve_notes(units):
        """What the availability and reserve lines say of `units`: their
        prices, carriers' and amphibious ships' empty decks, and where an
        allied aircraft is sold."""
        notes = []
        if any(mission_depth._navy(priced[u]) != nation for u in units):
            notes.append("Allied classes cost their own navies' listed prices, without "
                         "the same-nation discount.")
        # A deck of more than four is a carrier's or an amphibious ship's
        # (Galicia 6 to Ford 90); an escort's flight is one to three.
        if any(unit_type(u) == "Vessel" and deck_size(u) > 4 for u in units):
            notes.append("Carriers and amphibious ships come without aircraft, as "
                         "every ship bought here does.")
        if spec.get("RESERVE_AIR"):
            notes.append("An allied aircraft is sold only where some mission here "
                         "can launch and recover it.")
        return notes

    if open_allocation:
        availability = (f'- Open Allocation: every force allocation offers the whole campaign '
                        f'roster{", the allied fleet included," if allied else ","} from the '
                        f'first{held}. Some operations still limit what sails.')
    elif opening is not None:
        units = next((u for m, u in reserve if m is opening), [])
        whole = ("- Every force allocation offers the whole roster" if opening is first else
                 f"- Force allocations before {opening['key']} offer what the story releases. "
                 f"From the force allocation before {opening['key']}, every force allocation "
                 "offers the whole roster")
        said = [whole + (" and " + mission_depth.reserve_phrase(spec, units) if units else "")
                + "."]
        said += [n for n in reserve_notes(units) if not n.startswith("Allied classes")]
        said.append("Some operations still limit what sails.")
        availability = " ".join(said)
    else:
        availability = ("- Unit availability changes between missions: Task Force Builder "
                        "offers only what the current force-allocation window allows.")
    swap('Text="- Unit availability can change between missions. Japanese units, for '
         'example, may not be available after leaving Japanese waters."',
         f'Text="{_xml_text(availability)}"', "availability line")
    # The allied reserve (mission_depth.apply_reserve), said once on the
    # story page: the Unit Catalog lists the whole roster file from the first
    # window, reserve classes included, and this is what says when they are
    # really on sale. The twin sells them from the first anyway. Until 21 Oct
    # 2026 it named eleven escort classes and said no allied aircraft,
    # carrier, amphibious ship or tanker was sold; the whole fleet is now,
    # counted by navy (mission_depth.reserve_phrase), and Red Line's line
    # names the PLAN's own two supply ships without calling them allied.
    # The fleet the campaign's opening sells is said in the availability
    # line above (step 2, the same day), and only its prices, the catalogue
    # and the named hulls here; a class RESERVE opens elsewhere keeps the
    # line of its own.
    if reserve:
        at = t.index("/>", t.index(f'Text="{_xml_text(availability)}"')) + 2
        for m, units in reversed(reserve):
            if m is opening:
                said = (["The Unit Catalog lists all of it from the start."]
                        if m is not first else [])
                said += [n for n in reserve_notes(units) if n.startswith("Allied classes")]
            else:
                said = [("Every force allocation also sells " if m is first else
                         f"Every force allocation from the one before {m['key']} also sells ")
                        + mission_depth.reserve_phrase(spec, units) + "."]
                if m is not first:
                    said.append("The Unit Catalog lists them from the start.")
                said += reserve_notes(units)
            said.append("No hull a mission names is sold.")
            t = t[:at] + indent + line.format(_xml_text("- " + " ".join(said)), 5) + t[at:]
    swap('Text="- Ships purchased in Task Force Builder include their airwing for free, and '
         'those aircraft are assigned to the ship automatically. Replacement aircraft must '
         'be purchased separately if aircraft are lost."',
         'Text="- Ships purchased in Task Force Builder come without aircraft. Helicopters '
         'and aircraft are bought separately, and replacements must be bought if aircraft '
         'are lost."', "airwing line")
    # All four campaigns sell a helicopter in their first window and added
    # fixed-wing types from the second (checked 27 Sep), so the stock
    # helicopter and fixed-wing lines stood as written. Red Line's first
    # window offers the whole roster since 21 Oct 2026, the Y-9, KJ-500,
    # J-15 and J-15D with it, so the fixed-wing line is read off the first
    # window's list now (a window with none sells the whole roster).
    first_sale = ((first["window"].get("allow") or list(priced)) if first else [])
    fixed_first = any(unit_type(u) in ("Aircraft", "VTOL") for u in first_sale)
    swap('Text="- Helicopters are available immediately at campaign start. Each ship will '
         'show its supported aircraft in Task Force Builder."',
         ('Text="- Helicopters and fixed-wing aircraft are on sale from the first force '
          'allocation. Each ship shows its supported aircraft in Task Force Builder."'
          if open_allocation else
          'Text="- Helicopters are available from the first force allocation. Each ship '
          'shows its supported aircraft in Task Force Builder."'), "helicopter line")
    if open_allocation:
        swap('Text="- Fixed-wing aircraft are not available for purchase at the start of '
             'the campaign, but become available later on."',
             'Text="- Fixed-wing aircraft are on sale from the first force allocation, '
             'before any mission can use them.'
             + (' Allied aircraft are sold only where some mission here can launch and '
                'recover them.' if allied else '') + '"', "fixed-wing line")
    elif fixed_first:
        swap('Text="- Fixed-wing aircraft are not available for purchase at the start of '
             'the campaign, but become available later on."',
             'Text="- Fixed-wing aircraft are on sale from the first force allocation. Each '
             'flies only in a mission whose air tasking takes it."',
             "fixed-wing line")
    # No roster sells a submarine: the game's task force cannot take a bought
    # one (in-game check, 13 Oct - allied_fleet.py), and roster_ini() refuses
    # it. The Open Allocation twins sold thirteen until then, and this line
    # said where they sailed.
    subs = [e["unit"] for e in spec["ROSTER"] if unit_type(e["unit"]) == "Submarine"]
    if subs:
        raise SystemExit(f"{spec['TITLE']}: the roster sells submarines "
                         f"({', '.join(subs)}) - a bought boat cannot join the task force")
    swap('Text="- Submarines operate independently of your task force. They appear in '
         'separate (but connected) optional side missions, which offer benefits to '
         'complete, but do not advance the main campaign."',
         'Text="- Submarines cannot be bought in this campaign. A mission that gives you '
         'one provides it with the mission; it does not join your task force."',
         "submarine line")
    # The table's Survived Missions column is the game's own since 0.8.3
    # (28 Sep 2026 build): each cell binds <Level>CrewSkillSurvivalRequirement,
    # which the game fills from this campaign's CrewSkillThresholds. The stock
    # page carried Pacific Strike's numbers as text before, and this swapped
    # ours in; now it only proves the bindings are still there, since a page
    # that lost them would show the stock campaign's numbers again. Brush
    # names give the level each row shows: Green = Novice, Trained = Regular,
    # Seasoned, Veterans = Veteran, Ultra = Elite.
    for level in ("Green", "Trained", "Seasoned", "Veterans", "Ultra"):
        if (f'Text="{{Binding {level}CrewSkillSurvivalRequirement}}"' not in t
                or f"Brush.CrewSkill.{level}" not in t):
            raise SystemExit(f"campaign rules: the stock proficiency table's {level} row "
                             "has changed - rebase campaign_rules()")
    return t


# ---------------------------------------------------------- open allocation
# An Open Allocation twin (user request, 27 Sep 2026) is a campaign's second
# entry in the campaign list: the same missions, points and prices, but every
# force-allocation window sells the whole roster instead of what the story
# has released so far. The game has no switch for that. A difficulty preset
# carries points, airwing, loadout, repair, refund and crew keys and nothing
# else (the Difficulty* strings under ui.ini [TaskForceMode]); its own
# Unrestricted start option sells every unit of every nation, ignoring the
# roster. So the switch is a second entry, chosen at the start the way the
# game's own start options are, with its own save. The twin is the base
# campaign.ini with four kinds of line changed, and it loads the base
# campaign's missions and art by path - MissionFile and every art key are
# StreamingAssets-relative in every stock campaign - so nothing but the spine
# is duplicated.
#
# Kept for a world-wide Task Force Mode campaign, or for the SEST World
# Campaign (integration/world-sandbox, a Dynamic Campaign Mod campaign with
# its own buy list) should it want allied_fleet.py's priced lists. Every
# campaign shipped a twin from 27 Sep to 21 Oct 2026; the owner retired them
# from the pack on 21 Oct and put what they sold in the standard campaigns
# instead: from Weapons Free, Tasman Crossing and Red Line's first window
# every force allocation offers the whole roster (mission_depth.open_from),
# and the allied reserve (mission_depth.apply_reserve) adds the allied
# fleet, or in Red Line the PLAN's supply ships. The windows before those
# keep the story's lists. Only this twin path is dormant. A spec opts in with OPEN_ALLOCATION=True:
# open_allocation_twin() and write_open_twin() then build and write
# campaigns/<slug>-open, and tools/check_campaign_coverage.py holds it to
# open_twin(). No spec in the pack sets it, and the tests build a twin into
# a temporary folder so the code and OPEN_HOLD stay checked against the
# shipped campaigns. A spec that also sets RESERVE_FLEET is refused
# (mission_depth.apply_reserve, review of 21 Oct 2026): its twin would be
# built from windows already open and quote their sentence as the story's.
OPEN_SUFFIX = "-open"
# The window's own situation follows the note unchanged: it still says what
# sails, what is rearmed and where the next window is, and what it says is on
# offer is read as the story's allocation, which the note sets aside.
OPEN_NOTE = ("Open Allocation: the whole roster is on offer at this window. The "
             "story's allocation for it reads:")
OPEN_BLURB = ("OPEN ALLOCATION - every unit this campaign sells is on offer from the "
              "first force allocation, whatever the story has released. Same missions, "
              "points and prices. ")
# OPEN_HOLD (20 Oct 2026): units a twin sells only at the windows where the
# story's own allowlist sells them. Sulu Line's twin sold its C8 charter at
# The Island Road and every supply ship at Fire Mission Jolo, where the story
# sells none: in a campaign with no free rearm, a supply ship on sale is the
# rearm. A window that holds one back says so, and so does the description.
OPEN_NOTE_HELD = ("Open Allocation: the whole roster is on offer at this window, except "
                  "what the story sells only at its own windows. The story's allocation "
                  "for it reads:")
OPEN_BLURB_HELD = ("OPEN ALLOCATION - every unit this campaign sells is on offer from the "
                   "first force allocation, whatever the story has released, except the "
                   "few the story sells only at its own windows. Same missions, points "
                   "and prices. ")


def open_slug(slug):
    return slug + OPEN_SUFFIX


def allied_line(roster, commander):
    """The campaign-list sentence naming the allied fleet on a twin's roster,
    or "" when its roster is the commander's own navy alone."""
    nation = re.search(r"^CommanderNations=(.+)$", commander, re.M).group(1).strip()
    foreign = collections.Counter(nation_name(n) for n in roster_nations(roster).values()
                                  if n.lower() != nation.lower())
    if not foreign:
        return ""
    names = [n for n, _c in sorted(foreign.items(), key=lambda x: (-x[1], x[0]))]
    count = sum(foreign.values())
    where = names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"
    return (f"The allied fleet is on sale beside it at full price: {count} "
            f"class{'es' if count != 1 else ''} from {where}. ")


def open_allocation_ini(text, slug, roster, allied="", hold=()):
    """The Open Allocation twin's campaign.ini, from the base campaign's text.

    Changed: `[File] Base` (the file's own location, which stock says every
    system needs), the campaign's `[Language_en]` Name and Description, and in
    every window whose builder is open, the allowlist (the whole roster, every
    priced variant) and the situation (OPEN_NOTE first). A unit in `hold`
    (spec OPEN_HOLD) is in a window's allowlist only where the base window's
    has it, and a window that leaves one out opens with OPEN_NOTE_HELD. A
    repair-only stop keeps its situation: nothing is on offer there.
    Everything else - every MissionFile, every art path, every gate and
    reward - is the base campaign's, byte for byte.
    """
    units = [e["unit"] for e in roster]
    unknown = sorted(set(hold) - set(units))
    if unknown:
        raise SystemExit(f"{slug}: OPEN_HOLD names {', '.join(unknown)}, which the roster "
                         "does not sell")
    counts = collections.Counter()
    out = []
    for sec in re.split(r"\n(?=\[)", text):
        head = sec.split("\n", 1)[0].strip()
        if head.startswith("[File]"):
            old = f"Base=campaigns/{slug}/campaign.ini"
            counts["base"] += sec.count(old)
            sec = sec.replace(old, f"Base=campaigns/{open_slug(slug)}/campaign.ini")
        elif head == "[Language_en]":
            sec, n = re.subn(r"^Name=(.*?)( \([^)]*\))?$",
                             lambda m: f"Name={m.group(1)} - Open Allocation{m.group(2) or ''}",
                             sec, count=1, flags=re.M)
            counts["name"] += n
            blurb = OPEN_BLURB_HELD if hold else OPEN_BLURB
            sec, n = re.subn(r"^Description=", lambda m: "Description=" + blurb + allied,
                             sec, count=1, flags=re.M)
            counts["description"] += n
        elif re.search(r"^TaskForceModeEnableTaskForceBuilder=True$", sec, re.M):
            counts["windows"] += 1
            # A window with no allowlist sells the whole roster in the base
            # campaign too, held units included.
            base = re.search(r"^TaskForceModeAllowedRosterUnits=(.*)$", sec, re.M)
            sold = {e.split(",")[0] for e in base.group(1).split("|")} if base else set(units)
            offered = [u for u in units if u not in hold or u in sold]
            note = OPEN_NOTE if len(offered) == len(units) else OPEN_NOTE_HELD
            full = allowed_roster_units(offered, roster, f"{slug}: open allocation")
            sec, n = re.subn(r"^TaskForceModeAllowedRosterUnits=.*$",
                             lambda m: "TaskForceModeAllowedRosterUnits=" + full,
                             sec, flags=re.M)
            counts["allow"] += n
            sec, n = re.subn(r"^TaskForceModeBuilderSituation_en=",
                             lambda m: "TaskForceModeBuilderSituation_en=" + note + " ",
                             sec, flags=re.M)
            counts["situation"] += n
        out.append(sec)
    if (counts["base"], counts["name"], counts["description"]) != (1, 1, 1) \
            or not counts["windows"]:
        raise SystemExit(f"{slug}: open allocation could not find the campaign's "
                         f"Base, Name, Description or a purchase window ({dict(counts)})")
    return "\n".join(out)


def open_allocation_twin(spec, campaign_text, missions, placements, flight_rows,
                         authored=(), play_credits=None):
    """Everything an Open Allocation twin is, for the campaign set_campaign()
    last chose: a dict of its roster, roster file, rules page, spine and
    coverage rows, plus the allied entries it sells and those it leaves out.

    Its roster is this campaign's own, then the allied fleet its commander
    can call on (spec ALLIED_FLEET), aircraft only where a row here launches
    and recovers them (usable_allied). `campaign_text` is the base spine as
    written; `missions` and `placements` are the built missions and what
    they placed; `play_credits` is what the campaign itself loads, Dispatches
    left out, which the twin's REQUIRED-MODS adds its roster to. Everything
    that can stop the build happens here, so main() calls it before the dry
    run returns and before the pack folder is cleared. Only a spec with
    OPEN_ALLOCATION is built this way (21 Oct 2026); the tests call it
    directly.
    """
    allied, allied_dropped = usable_allied(spec.get("ALLIED_FLEET", []), missions,
                                           placements, flight_rows, ROSTER, authored)
    twin_roster = list(ROSTER) + allied
    # The twin's rows against the twin's roster, as the base build checks
    # its own; usable_allied has already kept only what passes.
    check_flights(flight_rows, twin_roster, authored=authored)
    # The allied-fleet sentence names what the twin adds, not the twin's
    # whole roster: called with twin_roster until 20 Oct 2026, it counted
    # Sulu Line's own Thai, Australian and MSC units as an allied fleet
    # ("5 classes from Thailand, Australia and USA"), and a campaign's
    # allied reserve, on its base roster already, would count twice.
    foreign = allied_line(allied, spec["COMMANDER"])
    rules_text = campaign_rules(dict(spec, ROSTER=twin_roster), open_allocation=True,
                                allied=bool(foreign))
    spine = open_allocation_ini(campaign_text, SLUG, twin_roster, foreign,
                                spec.get("OPEN_HOLD", ()))
    roster_text, roster_credits = roster_ini(
        twin_roster, heading=f"; SEST {TITLE} - Open Allocation requisition roster: "
                             "the campaign's own units, then the allied fleet.")
    credits = dict(play_credits or {})
    for token, why in roster_credits.items():
        credits.setdefault(token, (why[0], why[1], ROSTER_ORIGIN))
    rows, missing = coverage(credits, spec.get("EXCUSES", {}))
    return dict(roster=twin_roster, roster_text=roster_text, rules_text=rules_text,
                campaign_text=spine, rows=rows, missing=missing,
                allied=allied, allied_dropped=allied_dropped)


def write_open_twin(out, spec, twin, all_rows=()):
    """Write `twin` (open_allocation_twin()) as campaigns/<slug>-open under
    `out`, beside the base campaign already written there, and return the
    folder. It holds its own spine, rules page, roster and REQUIRED-MODS
    (the campaign's units and the allied fleet), and copies of the base's
    commander settings and enemy roster; the missions and art stay in the
    base folder (see open_allocation_ini()). `all_rows` is the base
    campaign's full coverage, Dispatches included, for the list of mods only
    the Dispatches need.
    """
    import shutil
    camp = out / "campaigns" / SLUG
    folder = out / "campaigns" / open_slug(SLUG)
    folder.mkdir(parents=True)
    (folder / "campaign.ini").write_text(twin["campaign_text"], encoding="utf-8")
    (folder / "campaign_rules_en.xml").write_text(twin["rules_text"], encoding="utf-8")
    (folder / "player_task_force_roster.ini").write_text(twin["roster_text"],
                                                         encoding="utf-8")
    (folder / "REQUIRED-MODS.txt").write_text(
        campaign_requirements(twin["rows"], twin["missing"], f"{TITLE} - Open Allocation",
                              dispatch_only(all_rows, twin["rows"]),
                              spec["DISPATCHES"]), encoding="utf-8")
    shutil.copy2(camp / "commander_settings.ini", folder / "commander_settings.ini")
    shutil.copy2(camp / "enemy_theater_roster.ini", folder / "enemy_theater_roster.ini")
    return folder


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
        ROSTER_SOURCE="campaign_data.py",
        INFO_DESC=sw.INFO_DESC, DISPATCH_DESC=sw.DISPATCH_DESC,
        TASKFORCE=sw.TASKFORCE, DIFFICULTIES=sw.DIFFICULTIES,
        ROSTER=sw.ROSTER, RESERVE_FLEET=sw.RESERVE_FLEET, COMMANDER=sw.COMMANDER,
        EVENTS=sw.EVENTS, MISSIONS=sw.MISSIONS, EXCUSES=sw.EXCUSES)
    specs = [watch, sr.CAMPAIGN]
    import allied_fleet                              # noqa: E402
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
    # Sulu Line, the same way: optional, appended after Red Line.
    try:
        import sulu_line as sl                      # noqa: E402
    except ModuleNotFoundError as exc:
        if exc.name != "sulu_line":
            raise
    else:
        if getattr(sl, "__file__", None):
            specs.append(sl.CAMPAIGN)
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
    # The allied fleet their commander's navy can call on (allied_fleet.py),
    # chosen by the commander's nation. The allied reserve sells it in the
    # standard campaigns, from the window each names (mission_depth.
    # apply_reserve; the whole fleet since 21 Oct 2026), and a campaign that
    # opts in to OPEN_ALLOCATION sells on its twin whatever the reserve
    # leaves in it.
    for spec in specs:
        nation = re.search(r"^CommanderNations=(.+)$", spec.get("COMMANDER", ""), re.M)
        spec.setdefault("ALLIED_FLEET",
                        allied_fleet.FOR_NATION.get(nation.group(1).strip(), [])
                        if nation else [])
    import mission_depth
    mission_depth.apply(specs)
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


# SEST Cross-Deck (integration/cross-deck) extends allied decks with the
# allied members of the airframe families they already fly, through an
# Anchor Chain #!extend stub per hull. The game reads the stub on top of the
# winning file, so the deck list the campaign measures has to be the same
# union, or an MH-60R the game lands on an Iver Huitfeldt would be refused here.
CROSS_DECK = ROOT / "integration" / "cross-deck" / "SEST_Cross_Deck" / "vessels_overwrite"


def deck_types(deck_type):
    """The deck's AircraftSupported as the game reads it: the winning file's
    list, replaced by SEST Cross-Deck's extended list where one is built.
    None when the hull declares no list at all."""
    stub = CROSS_DECK / f"{deck_type}_CrossDeck_SEST.ini"
    if stub.is_file():
        m = re.search(r"^AircraftSupported=([^\n/]*)", read(stub), re.M)
        if m:
            return m.group(1).strip()
    return unit_value(deck_type, "AircraftSupported")


def deck_fit(atype, kind, deck_type, is_ship):
    """Can this airframe recover on that deck, by the two files' own words.

    0 = compatible: a field; a ship whose AircraftSupported names the type
        (or names the game's own `Helicopters` token and the type is one);
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
    listed = deck_types(deck_type)
    if listed:
        names = {x.strip() for x in listed.split(",") if x.strip()}
        if atype in names:
            return 0
        # Vanilla's own wildcard (29 hulls, the Ticonderogas and Burkes
        # among them): every helicopter, whatever its name.
        return 0 if ("Helicopters" in names and kind == "Helicopter") else None
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

POOL_ROOTS = ("integration/mission-seeds",
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


def coast_data(mission=None):
    """The coastline a "coast" mission is proved on: the extract in geo/ whose
    box holds the mission's centre (Southern Reach's southern theatre, Sulu
    Line's Sulu and Celebes Seas, Southern Watch's Banda and Arafura). No
    mission, or no extract holding it: the southern theatre's, whose box
    check then names every position outside it."""
    from coast import coast, covering
    if mission and mission.get("centre"):
        return covering(*mission["centre"]) or coast()
    return coast()


class CoastPlacer:
    """Stands in for Snapper on a mission whose geography is "coast".

    Same take() signature, so place() does not care which it was handed;
    positions are used as authored and refused if the coastline disagrees.
    Hulls sharing a coastal station are spread 0.4 NM abeam, the way the pool
    placer's distinct points spread them, so two ships never spawn on one
    coordinate; land units sharing a station stand 0.15 NM apart.
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
        elif kind == "land":
            # Land units sharing a station (a launcher and its radar, a
            # battery's guns) stand 0.15 NM apart on an east-west line, each
            # proved ashore on its own: one coordinate for all of them is a
            # pile-up the game shoves apart wherever it likes.
            n = self.berths[where]
            self.berths[where] += 1
            side = (n + 1) // 2 * (1 if n % 2 else -1)
            lon = at[1] + side * 0.15 / (60.0 * math.cos(math.radians(at[0])))
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

    def route(self, start, waypoints, where, least=0.5):
        """Check each sailed leg, including spawn to the first waypoint.

        Two wet endpoints do not prove a wet passage: Weather Alternate's
        raiders crossed Kai Kecil between them. Quarter-NM samples with a
        half-NM default shore margin also reject near misses between sample
        points. A mission may demand more room where game terrain differs.
        """
        if not math.isfinite(least) or least <= 0:
            raise SystemExit(f"{where}: route clearance must be finite and positive")
        for leg, end in enumerate(waypoints, 1):
            steps = max(1, math.ceil(nm_between(start, end) / 0.25))
            dlon = (end[1] - start[1] + 180) % 360 - 180
            for i in range(steps + 1):
                fraction = i / steps
                at = (start[0] + (end[0] - start[0]) * fraction,
                      (start[1] + dlon * fraction + 180) % 360 - 180)
                if not self._cover(at, f"{where} leg {leg}"):
                    break
                land, nm = self.coast.check(*at)
                if land or nm < least:
                    PLACEMENT_PROBLEMS.append(
                        f"{where}: leg {leg} crosses "
                        f"{'land' if land else f'the {least:g} NM shore margin'} near "
                        f"({at[0]:.4f}, {at[1]:.4f}); "
                        "route round the island or headland")
                    break
            start = end

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


def pick_nation(uid, pick):
    """The nation a roster pick is registered to, or None.

    No unit file on these rosters declares a Nation; the squadron (for an
    aircraft) or the hull variant (for a ship) does, else that file's
    [Default] - the same place the game takes a unit's flag from, and the
    place check_campaign_coverage reads it. The Super Hornet, Growler, P-8
    and Seahawk on sale are US-built airframes flying Australian squadrons,
    and this is what says so. Stock does the same: Pacific Strike sells
    `usn_fa-18a=Squadron7,Squadron8` to an Australian commander, and its
    squadrons file registers both to Australia. An empty or comment-only
    Nation= is undeclared, and falls through to [Default].
    """
    kind, _path = unit_file(uid)
    f = winning(f"{kind}/{uid}_{'squadrons' if kind == 'aircraft' else 'variants'}.ini")
    if f is None:
        return None
    text = read(f)
    for section in (pick, "Default"):
        m = re.search(rf"^\[{re.escape(section)}\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S)
        n = m and re.search(r"^[ \t]*Nation[ \t]*=[ \t]*(.*?)[ \t]*\r?$", m.group(1), re.M)
        value = n and re.split(r"\s*(?://|#|;)", n.group(1), 1)[0].strip()
        if value:
            return value
    return None


def roster_nations(roster):
    """{unit: nation} for a roster, every pick of a unit agreeing.

    The game decides the discount per purchase; this builder describes it per
    unit, so it needs one nation per unit - a limit of this builder, not the
    game's rule (stock sells usn_p-3c squadrons of three nations under one
    entry). A pick with no declared nation, picks that disagree, or a unit
    file that declares a nation of its own different from its picks' would
    put the decision somewhere this build cannot see, so any of them stops
    it.
    """
    out = {}
    for e in roster:
        found = {pick_nation(e["unit"], p) for p in e["picks"]}
        if None in found or len(found) != 1:
            raise SystemExit(f"roster: {e['unit']} {e['picks']} - no single declared "
                             f"nation across its picks ({sorted(map(str, found))}); the "
                             "same-nation discount would be decided somewhere this "
                             "build cannot see")
        nation = found.pop()
        own = unit_value(e["unit"], "Nation")
        if own and own.lower() != nation.lower():
            raise SystemExit(f"roster: {e['unit']} declares Nation={own} in its unit "
                             f"file but its picks are registered to {nation}; which one "
                             "the discount follows is not something this build can see")
        out[e["unit"]] = nation
    return out


def nation_name(key):
    """The game's display name for a nation key (language_en/nations.ini)."""
    global _NATION_NAMES
    if _NATION_NAMES is None:
        f = ROOT / "mods-source" / "_vanilla" / "original" / "language_en" / "nations.ini"
        _NATION_NAMES = {}
        for raw in f.read_text(encoding="utf-8-sig").splitlines():
            k, sep, v = raw.partition("=")
            if sep:
                _NATION_NAMES[k.strip().lower()] = v.strip()
    return _NATION_NAMES.get(key.lower(), key)


_NATION_NAMES = None


def same_nation_discount(commander):
    """SameNationUnitDiscount from a commander_settings text, as a fraction.

    0 when the key is absent. Pacific Strike writes a fraction (0.2); a
    value that does not read as one stops the build rather than ship a
    discount nobody chose.
    """
    m = re.search(r"^SameNationUnitDiscount=(.*)$", commander, re.M)
    if not m:
        return 0.0
    try:
        value = float(m.group(1).strip())
    except ValueError:
        value = -1.0
    if not 0 <= value < 1:
        raise SystemExit(f"commander settings: SameNationUnitDiscount={m.group(1).strip()} "
                         "is not a fraction between 0 and 1 (Pacific Strike's is 0.2)")
    return value


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


def loadout_dates(path, depth=0):
    """{fit: year} from the file's LoadoutDate_<fit>= keys, alias base included."""
    found = {m.group(1).strip(): int(m.group(2)) for m in
             re.finditer(r"^LoadoutDate_([^=\n]+)=(\d{4})", read(path), re.M)}
    if found:
        return found
    base = alias_target(path) if depth < 4 else None
    return loadout_dates(base, depth + 1) if base else {}


def pick_loadout(uid, path, want, year=None):
    """The loadout to write, and why. Never invents a name the file lacks.

    A file that dates its fits (LoadoutDate_<fit>=year, the stock mechanism the
    game uses to fit a ship to the mission's date) gets the latest fit in
    service by the mission's year; ties go to the first offered. Writing
    Default there forced the oldest fit: Euromod's Anzac and Hobart sailed a
    2028 campaign without NSM (17 Oct 2026). An undated fit counts as in
    service from the start."""
    offered = loadouts(path)
    if not offered:
        return None, "file offers none"
    if want:
        if want not in offered:
            raise SystemExit(f"{uid}: loadout {want!r} is not offered by the "
                             f"winning file (offers: {', '.join(offered)})")
        return want, "declared"
    dates = loadout_dates(path) if year else {}
    if dates:
        live = [f for f in offered if dates.get(f, 0) <= year]
        if live:
            best = max(dates.get(f, 0) for f in live)
            return next(f for f in live if dates.get(f, 0) == best), f"in service by {year}"
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


@functools.lru_cache(maxsize=None)
def chain_owners(relpath, depth=0):
    """Every mod whose copy of one file the game reads, highest first.

    The winner, and while the copy just taken is an Anchor Chain `#!extend`
    stub, the copy below it as well: the J-35's PL-15S is a stub in the PLA
    AEP layered on the PLAAF Aircraft Pack's full file, and crediting only
    the stub said the PLAAF pack was unused. A copy that is `#!alias` of
    another file credits that file's chain and stops.
    """
    pairs = providers()
    out = []
    for f in all_copies(relpath):
        token = next((t for t, base in pairs if f.is_relative_to(base)), None)
        if token and token not in out:
            out.append(token)
        text = read(f)
        a = re.search(r"#!alias\s+(\S+)", text)
        if a and depth < 4:
            out += [t for t in chain_owners(a.group(1), depth + 1) if t not in out]
            break
        if not re.search(r"^\s*#!extend\s", text, re.M):
            break
    return tuple(out)


def store_credit(uid, kind_dir, path, fit):
    """(token, "store", detail) for every round a unit hangs with one fit:
    each mod whose copy of that ammunition file the game reads
    (chain_owners). resolve() credits a placed unit's fit with it,
    aircraft_credit() every fit of an embarked or sold airframe, and
    roster_ini() every fit of a sold hull."""
    return [(token, "store", f"{uid} / {store}")
            for store in stores(uid, kind_dir, path, fit)
            for token in chain_owners(f"ammunition/{store}.ini")]


@functools.lru_cache(maxsize=None)
def aircraft_credit(atype):
    """(token, how, detail) for one embarked or sold aircraft type: its
    unit and squadron files, and every round any of its fits hangs."""
    akind, apath = unit_file(atype)
    if apath is None:
        return ()
    out = [(owner(f"{akind}/{atype}.ini"), "unit", atype),
           (owner(f"{akind}/{atype}_squadrons.ini"), "squadron", atype)]
    for afit in loadouts(apath) or [None]:
        out += store_credit(atype, akind, apath, afit)
    return tuple(out)


def deck_aircraft(uid, kind_dir, path, variant, spec):
    """Aircraft ids a placed deck embarks: the mission's own air_group when it
    writes one (CustomAirGroup=True on the unit), else the variant's
    CustomAirGroup, else the unit's [AirGroup], following #!alias."""
    if spec.get("air_group") is not None:
        return [atype for atype, _sq, _n in spec["air_group"]]
    entry = re.compile(r"^\s*([^#\s=]+)\s*=\s*\w+,\d+", re.M)
    vf = winning(f"{kind_dir}/{uid}_variants.ini")
    if vf and variant:
        sec = re.search(rf"^\[{re.escape(variant)}\][^\n]*\n((?:[^\[\n][^\n]*\n?)*)",
                        read(vf), re.M)
        if sec and re.search(r"^CustomAirGroup\s*=\s*True", sec.group(1), re.M | re.I):
            return entry.findall(sec.group(1))
    p = path
    for _ in range(4):
        group = re.search(r"^\[AirGroup\][^\n]*\n((?:[^\[\n][^\n]*\n?)*)", read(p), re.M)
        if group:
            return entry.findall(group.group(1))
        p = alias_target(p)
        if not p:
            break
    return []


def resolve(spec, year=None):
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

    fit, _why = pick_loadout(uid, path, spec.get("loadout"), year)
    if fit:
        keys["LoadoutVariant"] = fit
    for token, how, detail in store_credit(uid, kind_dir, path, fit):
        note(token, how, detail)
    # A deck's aircraft fly from it whether or not the mission names them,
    # and every fit they offer can be armed on deck. Until 20 Oct 2026 none
    # of it was credited: Red Line and Southern Reach listed the PLAAF
    # Aircraft Pack as not used while the Fujian's and Liaoning's J-35s and
    # J-15Ts hang rounds only it ships.
    for atype in deck_aircraft(uid, kind_dir, path, keys.get("VariantReference"), spec):
        for token, how, detail in aircraft_credit(atype):
            note(token, how, f"{uid} deck / {detail}")
    for token, how, detail in asset_credit(uid, path):
        note(token, how, detail)

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
               "SquadronReference", "Disabled", "JoinTaskForce", "LoadoutVariant",
               "TaskForceModeAnchor", "TaskForceModeReplacedUnitIndex",
               "TaskForceModeIgnoreUnit", "Nation", "UnlimitedFuel", "WeaponStatus",
               "RadarsActive", "CrewSkill", "Morale", "CampaignTag",
               "RelativePositionInNM", "RandomSpawnCenter", "RandomSpawnRange",
               "RandomSpawnDirection", "Heading", "Telegraph",
               # last, after Waypoints, where the native blocks put it
               "HomeBase")


def block(tag, keys):
    lines = [f"[{tag}]"]
    for k in BLOCK_ORDER:
        # A random spawn replaces the fixed position, as in the stock Sub
        # Duel JMSDF 1985; the builder's own checks still read the centre
        # as RelativePositionInNM.
        if k == "RelativePositionInNM" and "RandomSpawnCenter" in keys:
            continue
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
# Where a credit the requisition roster gives is said to come from.
ROSTER_ORIGIN = "requisition roster"


def stronger_credit(why, best):
    """Whether credit `why` (how, detail, mission) replaces `best` as the
    one a coverage row shows: a stronger kind, or one as strong from a
    mission where `best` came from the roster. The roster's credits are
    merged first, and since 28 Oct 2026 they credit the variants and rounds
    of the units on sale as well; with only a stronger kind replacing them,
    about a dozen rows went from a unit a mission places to a roster
    example (Sulu Line's Euromod Main Pack: ran_mh-60r / usn_mk54_air
    instead of pn_ffg-150 / fr_cal_76mm in The Island Road). The kind is
    the same either way, so no mod changes list."""
    if best is None or STRENGTH[why[0]] < STRENGTH[best[0]]:
        return True
    return (STRENGTH[why[0]] == STRENGTH[best[0]] and best[2] == ROSTER_ORIGIN
            and why[2] != ROSTER_ORIGIN)


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


def asset_credit(uid, path):
    """(token, "asset", detail) for every model folder a unit's winning file
    loads (ASSET_FOLDER): each mod that wins a file under it (asset_owners).
    resolve() credits a placed unit with it, and roster_ini() a sold one."""
    return [(token, "asset", f"{uid} / {folder.rstrip('/')}")
            for folder in sorted(set(ASSET_FOLDER.findall(read(path))))
            for token in sorted(asset_owners(folder))]


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


# Orders a route may carry at a waypoint, as stock writes them after the
# waypoint's coordinates with "/" (06 Raid on Lombok l.279, Operation Polar
# Fury 1985 l.315): `x,alt,z/SetTelegraph,2/AttackAtWaypoint,ammo,Target,2`.
# AttackAtWaypoint is a single scripted strike at a named unit, fired whatever
# the shooter's weapon status - the Osa in Raid on Lombok does it at
# OverrideWeaponStatus=Tight - which is how a unit can be made to fire at one
# ship and at nothing else.
WAYPOINT_ORDERS = ("SetTelegraph", "SetWeaponStatus", "AttackAtWaypoint")
TARGET_MARK = "\x00target:{}\x00"

# U(..., disable=(...)): a unit's systems switched off at mission start, the
# way 08 Defense of North Borneo's Trigger4 does it, key for key.
DISABLE_ACTIONS = {"weapons": "WeaponSystems", "sensors": "SensorSystems",
                   "propulsion": "PropulsionSystems"}


def scripted_stores(uid, keys):
    """Loaded rounds, including a tube's associated magazine such as TorpedoRoom."""
    kind, path = unit_file(uid)
    held = set(stores(uid, kind, path, keys.get("LoadoutVariant")))
    body = read(path)
    for magazine in set(re.findall(r"^AssociatedMagazine=\s*([\w-]+)", body, re.M)):
        section = re.search(r"^\[" + re.escape(magazine) + r"\]\s*$(.*?)(?=^\[|\Z)", body, re.M | re.S)
        if section:
            held.update(re.findall(r"^Ammunition\d*=([^\s#/|]+)", section.group(1), re.M))
    return held


def timed_attacks(mission, spec, keys, pending, tag):
    """Native Attack=target,seconds,ammunition,shots; no runtime plugin.

    Attacks are deliberately limited to named opposing units, with real loaded
    stores and a preparation period. MissionFileInformation.ini documents this
    as an unconditional attack, including the seconds-from-mission-start clock.
    Actual launch/target handling is still a PC acceptance check.
    """
    out = []
    for number, attack in enumerate(spec.get("attacks", []), 1):
        where = f"{mission['key']}: {spec['type']} at {spec['station']}, attack {number}"
        if not isinstance(attack, (tuple, list)) or len(attack) != 4:
            raise SystemExit(f"{where}: attacks takes (minute, ammunition, target station ref, shots)")
        minute, ammo, target, shots = attack
        if (isinstance(minute, bool) or not isinstance(minute, (int, float)) or
                not math.isfinite(minute) or not OPENING_QUIET_MIN <= minute < mission["minutes"]):
            raise SystemExit(f"{where}: attack must follow the {OPENING_QUIET_MIN}-minute preparation period and precede the window")
        if spec.get("enter") is not None and minute <= spec["enter"]:
            raise SystemExit(f"{where}: attack must be after the shooter's join time")
        if not isinstance(shots, int) or isinstance(shots, bool) or shots < 1:
            raise SystemExit(f"{where}: shots must be a positive integer")
        if not isinstance(target, str) or not target:
            raise SystemExit(f"{where}: target must name one station ref")
        if ammo not in scripted_stores(spec["type"], keys):
            raise SystemExit(f"{where}: {ammo!r} is not carried in this fit")
        pending.append((tag, target, spec["side"], where))
        out.append(f"{TARGET_MARK.format(target)},{round(minute * 60)},{ammo},{shots}")
    if out:
        keys["Attack"] = "|".join(out)
        keys["OverrideWeaponStatus"] = keys["WeaponStatus"]


def waypoint_orders(mission, spec, kind, keys, orders, pending, tag, n):
    """The "/Order,..." suffix of one waypoint, validated against the files.

    An AttackAtWaypoint target is a station ref; it is written as a mark and
    resolved to the target's section once every unit has one (place())."""
    where = f"{mission['key']}: {spec['type']} at {spec['station']}, waypoint {n}"
    if not orders:
        return ""
    if kind == "land":
        raise SystemExit(f"{where}: waypoint orders on a land unit")
    out = []
    for order in orders:
        order = tuple(order)
        verb = order[0] if order else None
        if verb not in WAYPOINT_ORDERS:
            raise SystemExit(f"{where}: unknown waypoint order {verb!r} "
                             f"(known: {', '.join(WAYPOINT_ORDERS)})")
        if verb == "SetTelegraph":
            if (len(order) != 2 or not isinstance(order[1], int)
                    or isinstance(order[1], bool) or not 0 <= order[1] <= 5):
                raise SystemExit(f"{where}: SetTelegraph takes one telegraph 0-5")
            out.append(f"SetTelegraph,{order[1]}")
        elif verb == "SetWeaponStatus":
            if len(order) != 2 or order[1] not in ("Hold", "Tight", "Free"):
                raise SystemExit(f"{where}: SetWeaponStatus takes Hold, Tight or Free")
            out.append(f"SetWeaponStatus,{order[1]}")
        else:
            if len(order) != 4:
                raise SystemExit(f"{where}: AttackAtWaypoint takes (ammunition, "
                                 "target station ref, rounds)")
            _v, ammo, target, rounds = order
            if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 1:
                raise SystemExit(f"{where}: AttackAtWaypoint rounds must be 1 or more")
            carried = scripted_stores(spec["type"], keys)
            if ammo not in carried:
                raise SystemExit(f"{where}: AttackAtWaypoint fires {ammo!r}, which "
                                 f"{spec['type']} does not carry in this fit "
                                 f"(carries: {', '.join(sorted(carried)) or 'nothing'})")
            pending.append((tag, target, spec["side"], where))
            out.append(f"AttackAtWaypoint,{ammo},{TARGET_MARK.format(target)},{rounds}")
            # Raid on Lombok's Osa: the status the unit holds everywhere
            # except where it is told to fire.
            keys["OverrideWeaponStatus"] = keys["WeaponStatus"]
    return "".join("/" + o for o in out)


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
    ashore = []                                # land units put on firm ground so far
    worst = 0.0
    alone = set()                              # independent=True, by tag
    contact = set()                            # contact="why", by tag
    unlisted = set()                           # orbat=False, by tag
    pending = []                               # AttackAtWaypoint targets
    disabled = []                              # (tag, systems) off at start
    entering = []                              # (tag, minute) held back

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
        # A squadron that follows the flag (U() gives the Seahawk one: 816
        # Squadron under Australia's). The flag is the unit's own nation= or
        # its side's, compared without case, as the game compares nation keys.
        by_flag = spec.get("squadron_by_nation")
        if by_flag and not spec.get("squadron"):
            flag = spec.get("nation") or mission.get(f"{spec['side']}_nation") or ""
            pick = {k.lower(): v for k, v in by_flag.items()}.get(flag.lower())
            if pick:
                spec["squadron"] = pick
        kind, keys, credit = resolve(spec, (mission.get("date") or (None,))[0])
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
            sub = fix_land_positions.land_unit(spec["type"])[0] if want == "land" else ""
            if want == "land" and sub not in ("OilRig", "Port"):
                # A proven point is where some mission put a land unit, not
                # proof of ground: the game floats a land unit wherever its
                # 1 km grid has none (fix_land_positions.py), and the game's
                # own mission copies from before 10 Oct 2026 still hold such
                # spots. A unit needs land all round it - an airbase, which
                # brings its own ground, only under its anchor - and one that
                # has none takes the station's own coordinate if that is firm
                # ground, else the nearest firm ground to where it snapped.
                g = fix_land_positions.ground(lat, lon)
                if g < (0 if sub == "Airbase" else fix_land_positions.FIRM_KM):
                    firm = fix_land_positions.firm_ground(*st["at"], avoid=ashore)
                    if firm is None or nm_between(firm, st["at"]) > 1.0:
                        firm = fix_land_positions.firm_ground(lat, lon, avoid=ashore)
                    if firm is None:
                        PLACEMENT_PROBLEMS.append(
                            f"{mission['key']} {spec['station']}: {spec['type']} at {(lat, lon)} "
                            f"has no firm ground within {fix_land_positions.SEARCH_NM:.0f} NM")
                    else:
                        lat, lon = firm
                        dist = nm_between(firm, st["at"])
                ashore.append((lat, lon))
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
            berth = float(st.get("spawn_spacing", 0.6))
            if not math.isfinite(berth) or berth <= 0:
                raise SystemExit(f"{mission['key']}: {key} has invalid spawn spacing")
            lat = alat + side * berth * math.cos(beam) / 60.0
            lon = alon + side * berth * math.sin(beam) / (60.0 * math.cos(math.radians(alat)))
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
        # `random_spawn=dict(range=(min, max), bearing=(a, b))`: the game
        # places the unit at a random range (NM) and absolute bearing
        # (degrees, a to b clockwise, a may be negative) from this point -
        # the stock keys RandomSpawnCenter, RandomSpawnRange and
        # RandomSpawnDirection (Sub Duel JMSDF 1985).
        rs = spec.get("random_spawn")
        if rs:
            lo, hi = rs["range"]
            a, b = rs.get("bearing", (0, 360))
            if not (0 <= lo < hi) or not (-360 <= a < b <= 360) or b - a > 360:
                raise SystemExit(f"{mission['key']}: {spec['type']} has an invalid random_spawn {rs}")
            keys["RandomSpawnCenter"] = keys["RelativePositionInNM"]
            keys["RandomSpawnRange"] = f"{lo},{hi}"
            keys["RandomSpawnDirection"] = f"{a},{b}"
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
        else:
            # The flag the story flies it under where the unit file registers
            # a nation this war does not have (integration/common/flags.py):
            # Soviet-registered Russian hulls and aircraft fly the Russian
            # Federation's, Iran-registered Meridian hulls the company's.
            pick = next((keys[k] for k in ("VariantReference", "Squadron") if k in keys), "Default")
            remapped = flags.flag_for(pick_nation(spec["type"], pick), spec["type"])
            if remapped:
                keys["Nation"] = remapped
        # air_group=[(type, squadron, count)]: the deck's own aircraft, the way
        # every stock Task Force Mode mission writes them - CustomAirGroup=True
        # and one `type=SquadronN,count` line each, on the anchor and on every
        # player ship with a flight (Pacific Strike 01-10). This builder never
        # wrote one, and HMAS Canberra sailed Rig Seventeen with no helicopter
        # the player could launch (play test, 18 Oct 2026). ready=[(type,
        # squadron, fit, count, seconds)] are the FlightDeck_ReadyUpTask lines
        # that have some of them prepared at the start (Molniya 01's roro).
        # Each type is checked against the deck and credited to its mod.
        if spec.get("air_group") is not None:
            keys["CustomAirGroup"] = "True"
            group = {}
            for atype, squadron, count in spec["air_group"]:
                akind, apath = unit_file(atype)
                if apath is None:
                    sys.exit(f"{mission['key']}: air_group names {atype!r}, which "
                             "no enabled mod defines")
                if deck_fit(atype, unit_type(atype), spec["type"],
                            kind == "vessel") is None:
                    sys.exit(f"{mission['key']}: {spec['type']}'s deck does not "
                             f"take {atype}")
                if not any(re.search(rf"^\[{squadron}\]", read(f), re.M)
                           for f in all_copies(f"{akind}/{atype}_squadrons.ini")):
                    sys.exit(f"{mission['key']}: {atype} has no {squadron}")
                keys[atype] = f"{squadron},{count}"
                group[(atype, squadron)] = (apath, count)
                token = owner(f"{akind}/{atype}.ini")
                if token and token not in credit:
                    credit[token] = ("unit", atype)
            ready = spec.get("ready", [])
            if ready:
                keys["FlightDeck_ReadyUpTasks"] = str(len(ready))
            for i, (atype, squadron, fit, count, seconds) in enumerate(ready, 1):
                if (atype, squadron) not in group:
                    sys.exit(f"{mission['key']}: ready names {atype} {squadron}, "
                             "which the air_group does not carry")
                apath, carried = group[(atype, squadron)]
                if fit not in loadouts(apath) or count > carried:
                    sys.exit(f"{mission['key']}: ready {atype} {fit} x{count} - "
                             f"the file offers {', '.join(loadouts(apath))} and "
                             f"the group carries {carried}")
                keys[f"FlightDeck_ReadyUpTask{i}"] = (
                    f"{atype},{squadron},{fit},{count},{seconds}")
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
            mission["_anchor_section"] = tag
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
            # A waypoint is (lat, lon, alt) or (lat, lon, alt, orders): the
            # orders are carried out on reaching it (WAYPOINT_ORDERS).
            route = [(p[0], p[1], p[2], list(p[3]) if len(p) > 3 else [])
                     for p in spec["route"]]
            if isinstance(snapper, CoastPlacer) and kind in ("vessel", "sub"):
                snapper.route((lat, lon), [(la, lo) for la, lo, _a, _o in route],
                              f"{mission['key']} {spec['station']} ({spec['type']})",
                              least=mission.get("route_clearance_nm", 0.5))
            keys["Waypoints"] = "|".join(
                f"{(lo - centre[1]) * 60:.2f},{a},{(la - centre[0]) * 60:.2f}"
                + waypoint_orders(mission, spec, kind, keys, orders, pending, tag, n)
                for n, (la, lo, a, orders) in enumerate(route, 1))
            # A route without a speed is a route at whatever the game
            # defaults to. Every one of the 169 waypointed vessel and
            # submarine sections in the Pacific Strike export sets Telegraph=
            # (0-5; 3 is cruise, 2 is the most common), and SW04's whole
            # mission hangs on its passenger arriving before a deadline.
            keys["Telegraph"] = spec.get("telegraph", 3)
        # A patrol flown until the clock runs out. An aircraft that reaches
        # its last waypoint circles there, so a racetrack written as its two
        # ends three or four times over is half an hour of a Poseidon's
        # cruise: in Red Line's eighty-minute missions every barrier became
        # an orbit off to one side of the water it was barring. `|Loop` after
        # the last waypoint is stock's own form (Senkaku Run's Tu-95RT,
        # 01A line 654) and is attested on aircraft only, so it is refused on
        # anything else - and on civil traffic, which flies an airway.
        if spec.get("loop"):
            if kind not in ("air", "heli") or not spec.get("route"):
                sys.exit(f"{mission['key']}: {spec['type']} has loop=True - a "
                         "looped route is for an aircraft with a route= "
                         "(stock loops aircraft patrols and nothing else)")
            if spec["side"] == "neutral" and spec["type"].startswith("civ_"):
                sys.exit(f"{mission['key']}: {spec['type']} is civil traffic and "
                         "flies an airway; it does not loop")
            keys["Waypoints"] += "|Loop"

        timed_attacks(mission, spec, keys, pending, tag)

        placed[family].append((tag, keys, spec.get("name"),
                               spec.get("no_neutral_penalty", False)))
        members[spec["station"]].append(tag)
        # A player hull that sails unescorted on purpose - the tender slipping
        # in while the frigate draws the patrol off - is exempt from the
        # closure gate's escort distance. It is not a key the game reads, so
        # it rides on the mission, the way the anchor's tag does.
        # A red unit authored to open in contact - a shadower already on the
        # player, a boat the briefing puts inside the search box - says why
        # in contact="...", and check_opening() reads the reason instead of
        # refusing the range. Like independent=, not a key the game reads.
        if spec.get("contact"):
            if spec["side"] != "red" or not isinstance(spec["contact"], str):
                sys.exit(f"{mission['key']}: contact= is a reason, on a red unit; "
                         f"{spec['type']} is {spec['side']}")
            contact.add(tag)
        if spec.get("independent"):
            if spec["side"] != "blue":
                sys.exit(f"{mission['key']}: independent=True is for the "
                         f"player's own hulls; {spec['type']} is {spec['side']}")
            alone.add(tag)
        # orbat=False keeps an opposing unit out of the campaign's Situation
        # window (enemy_roster_ini), and recognise=False keeps it out of the
        # briefing's photographs (recognition): Red Line's ALPHA and GOLF,
        # whose class and navy are the puzzle the player is there to solve.
        # Neither is a key the game reads.
        if spec.get("orbat") is False:
            if spec["side"] != "red":
                sys.exit(f"{mission['key']}: orbat=False is for an opposing unit - the "
                         f"Situation window lists no other; {spec['type']} is {spec['side']}")
            unlisted.add(tag)
        # Systems off from the first second: TS11A's corvette, whose plot
        # holds her bridge and engines but not her operations room. The
        # player's own hull at launch cannot be the one - in a Generated
        # mission it is whatever they bought - nor can an air-tasking
        # placeholder.
        if spec.get("disable"):
            systems = tuple(spec["disable"])
            unknown = [s for s in systems if s not in DISABLE_ACTIONS]
            if not systems or unknown:
                sys.exit(f"{mission['key']}: {spec['type']} disable={systems!r} - "
                         f"name one or more of {', '.join(DISABLE_ACTIONS)}")
            if tag == mission.get("_anchor_section"):
                sys.exit(f"{mission['key']}: {spec['type']} is the anchor, the "
                         "player's own hull at launch; disable= cannot apply to it")
            if spec.get("slot"):
                sys.exit(f"{mission['key']}: {spec['type']} fills an air-tasking "
                         "slot; disable= cannot apply to a placeholder")
            disabled.append((tag, systems))
        # A red unit held back: it is in the file from the start but switched
        # off, and a timed trigger switches it on - stock's own way of
        # launching a raid later (Pacific Strike 02's H-6Ds and 01A's
        # bombers: Disabled=True on the unit, then "15min timer to enable
        # bombers", Action_SetEnabledStatus=True). Until then it is not in
        # the mission: it neither shoots nor sees, and check_opening() counts
        # it only from the minute it enters.
        if spec.get("enter") is not None:
            minute = spec["enter"]
            if spec["side"] not in ("red", "blue") or isinstance(minute, bool) \
                    or not isinstance(minute, (int, float)) \
                    or not 0 < minute < mission["minutes"]:
                sys.exit(f"{mission['key']}: enter= is the minute a combat-side unit joins, "
                         f"inside the {mission['minutes']}-minute plan; {spec['type']} "
                         f"({spec['side']}) has {minute!r}")
            if spec.get("slot") or spec.get("join") or tag == mission.get("_anchor_section"):
                sys.exit(f"{mission['key']}: enter= cannot defer a purchased or granted unit")
            if spec["side"] == "blue" and spec["type"] not in SMALL_UAV_TYPES:
                sys.exit(f"{mission['key']}: delayed blue support is restricted to small reconnaissance UAVs")
            keys["Disabled"] = "True"
            entering.append((tag, minute))
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

    # Every section has its number now: point each scripted attack at its
    # target's. A target must be exactly one unit on the other side - never
    # a neutral, never a slot the player fills with whatever they own.
    if pending:
        sections = {tag: keys for entries in placed.values()
                    for tag, keys, _n, _x in entries}
        for tag, ref, side, where in pending:
            hits = refs(members, ref)
            if len(hits) != 1:
                raise SystemExit(f"{where}: AttackAtWaypoint target {ref!r} is "
                                 f"{len(hits)} units; name exactly one")
            target = hits[0]
            other = "Taskforce1" if side == "red" else "Taskforce2"
            if side == "neutral" or not target.startswith(other):
                raise SystemExit(f"{where}: AttackAtWaypoint target {ref!r} is "
                                 f"{target}, not on the other side")
            if "TaskForceModeAirTaskingSlot" in sections[target]:
                raise SystemExit(f"{where}: AttackAtWaypoint target {ref!r} is an "
                                 "air-tasking placeholder")
            keys = sections[tag]
            for field in ("Waypoints", "Attack"):
                if field in keys:
                    keys[field] = keys[field].replace(TARGET_MARK.format(ref), target)
    stranded = assign_home_bases(placed, generated=bool(mission.get("generation")))
    if stranded:
        raise SystemExit(f"{mission['key']}: " + "; ".join(stranded))
    mission["_independent"] = alone
    mission["_contact"] = contact
    mission["_unlisted"] = unlisted
    mission["_disabled"] = disabled
    mission["_enter"] = dict(entering)
    return placed, members, credits, worst


SMALL_UAV_TYPES = {"usn_rq7705", "usn_ForpostR705", "usn_orlan10705", "usn_Mugin5705"}


def deck_places_needed(uid, kind):
    # Small UAVs need one place; a ship must still explicitly support the type.
    return 1 if kind == "Helicopter" or uid in SMALL_UAV_TYPES else 10


def assign_home_bases(placed, generated=False):
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

    Where the player's force is generated into the mission (Generated or
    Replaced), a player-side aircraft is still checked against the decks in
    reach but is never written a `HomeBase` naming a Taskforce1 ship. The
    stock task-force campaign never writes one - its Taskforce1 aircraft name
    a Taskforce1 airfield or nothing, helicopters included - and Rig
    Seventeen, the one mission to name an authored ship past the anchor for
    authored aircraft, died in ResolvePlacedCampaignAircraft twice
    ("NullReferenceException ... | 1 vs 3": one player ship against
    `Taskforce1Vessel3`), both times with a force carried through earlier
    missions. The slot MH-60R homed on `Taskforce1Vessel1` loaded, but its
    SAR reported "no home base" all the same (Player.log, snapshot 9208d39e).
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
                    needs = deck_places_needed(keys["Type"], kind)
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
                    if not (generated and side == "Taskforce1" and d[4]):
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
    "no_incoming": (set(), {"kind"}),
}


def also_condition(mission, n, extra, members):
    """Condition n of the victory trigger, from one `also` term.

    `time`: the clock has reached after_minutes. `area`: min_units of the
    units are in a box (the victory's own unless `at`/`radius` say
    otherwise). `destroyed`: min_units of them are gone. Without a `kind`
    a term is `time` if it sets after_minutes and `area` if not, which is
    how every term written before the kinds existed reads.

    A term the engine would accept and the player could never meet stops
    the build as well: one that names no unit (`Units=` with
    `MinimumUnits=0`), a min_units above what it names, a minute the
    Deadline trigger reaches first, or a `destroyed` term on the player's
    own units - a win that waits for the player to lose them.
    """
    victory = mission["victory"]
    if not isinstance(extra, dict):
        raise SystemExit(f"{mission['key']}: a victory also-term is a dict, "
                         f"not {extra!r}")
    kind = extra.get("kind") or ("time" if "after_minutes" in extra else "area")
    if kind not in ALSO_TERMS:
        raise SystemExit(f"{mission['key']}: victory also-term has kind {kind!r}; "
                         f"the builder knows {', '.join(ALSO_TERMS)}")
    needs, reads = ALSO_TERMS[kind]
    stray, missing = sorted(set(extra) - reads), sorted(needs - set(extra))
    if stray or missing:
        raise SystemExit(
            f"{mission['key']}: a victory also-term of kind {kind!r} "
            + (f"does not read {', '.join(map(repr, stray))}" if stray else "")
            + (" and " if stray and missing else "")
            + (f"needs {', '.join(map(repr, missing))}" if missing else "")
            + f" - {kind} reads {', '.join(sorted(reads))}")
    if kind == "time":
        after = extra["after_minutes"]
        if (not isinstance(after, int) or isinstance(after, bool)
                or not 0 < after < mission["minutes"]):
            raise SystemExit(
                f"{mission['key']}: a victory also-term waits for minute "
                f"{after!r}, and the planned window closes at minute "
                f"{mission['minutes']} - a time term is whole minutes inside "
                "the window")
        return [f"Condition_Condition{n}_Type=Time",
                f"Condition_Condition{n}_Time={after * 60}"]
    if kind == "no_incoming":
        # Task-force-wide, as native NoIncomingWeapons reads it. This is
        # combined with an earned win/elapsed-attack gate, never used alone.
        return [f"Condition_Condition{n}_Type=NoIncomingWeapons",
                f"Condition_Condition{n}_Taskforce=Taskforce1"]
    wanted = [extra["units"]] if isinstance(extra["units"], str) else extra["units"]
    units = [tag for r in wanted for tag in refs(members, r)]
    least = extra.get("min_units", len(units))
    if (not units or not isinstance(least, int) or isinstance(least, bool)
            or not 1 <= least <= len(units)):
        raise SystemExit(
            f"{mission['key']}: a victory also-term of kind {kind!r} asks for "
            f"{least!r} of {units} - it needs at least one unit, and a "
            "min_units from 1 to the number it names")
    if kind == "destroyed":
        own = [t for t in units if t.startswith("Taskforce1")]
        if own:
            raise SystemExit(
                f"{mission['key']}: a victory also-term of kind 'destroyed' "
                f"names the player's own {', '.join(own)} - the win would wait "
                "for the player to lose them")
        return destroyed_condition(n, units, least)
    return area_condition(n, mission["centre"], extra.get("at", victory.get("at")),
                          extra.get("radius", victory.get("radius", 20)),
                          units, least)


# Conservative transit speeds for the reachability check, in knots. They are
# deliberately below what the hulls can do: the question is whether an arrival
# objective is possible at all, not whether it is comfortable.
# Keyed on the unit's own UnitType, because an Aircraft family holds both a
# 300-knot jet and a 120-knot helicopter and the slow one is what decides
# whether an objective is reachable.
TRANSIT = {"Vessel": 18.0, "Submarine": 10.0, "LandUnit": 12.0,
           "Aircraft": 300.0, "VTOL": 250.0, "Helicopter": 120.0,
           "Biologic": 6.0}

# A surface ship in a seaway does not make her class speed. The game's own
# penalty is not in any file this repo can read, so this is calibrated on
# the one measurement in hand - HMAS Supply at flank in Macquarie Passage's
# sea state 5 made about 7 knots, 0.4 of the 18 the table assumes - and
# shaded conservative on either side of it. Submarines dive under it and
# aircraft fly over it; only Vessel speeds are scaled.
SEA_SPEED = {0: 1.0, 1: 1.0, 2: 1.0, 3: 0.9, 4: 0.7, 5: 0.45, 6: 0.35,
             7: 0.3, 8: 0.25}

# `minutes` is the planned window: it sizes every placement and reach check,
# and at that minute the player is told the window has closed. The mission
# itself is lost half as long again later. Stock's own campaigns run no
# clock at all; the first play tests lost missions a quarter-mile short of
# the box, and a plan that was right on paper is still a plan.
DEADLINE_FACTOR = 1.5


def sea_factor(mission):
    return SEA_SPEED.get(int(mission.get("sea", 0)), 0.25)


def ship_speed(kind, mission, calm=None):
    """The planning speed of a unit of UnitType `kind` in this mission's sea."""
    base = TRANSIT.get(kind, 18.0) if calm is None else calm
    return base * sea_factor(mission) if kind == "Vessel" else base


def deadline_minutes(mission):
    return int(round(mission["minutes"] * DEADLINE_FACTOR))


def hold_minutes(victory):
    """Minutes an arrival's units spend held before they may move: a stage
    that keeps them inside an area around one of their own starts until a
    minute (Macquarie Passage's service check, Southern Lifeline's
    rendezvous) is time at anchor, not time on the way."""
    stage = victory.get("after") or {}
    if isinstance(stage, dict) and stage.get("at_unit") and stage.get("after_minutes"):
        return int(stage["after_minutes"])
    return 0


def transit_of(tag, placed, mission):
    for family, entries in placed.items():
        for t, keys, _n, _x in entries:
            if t == tag:
                return ship_speed(unit_type(keys["Type"]), mission)
    return ship_speed("Vessel", mission)


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
                              ship_speed(unit_type(keys["Type"]), mission)))
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
    # An authored convoy speed is a calm-water figure too, and takes the
    # same sea.
    slowest = (ship_speed("Vessel", mission, calm=victory["transit"])
               if victory.get("transit") else min(f for _p, f in spots))
    window = mission["minutes"] - hold_minutes(victory)
    cap = int(radius + window / 60.0 * slowest * 0.6)
    best = None
    for step in range(max(cap, radius + 4), radius + 2, -1):
        at = (lat0 + step * math.cos(brg) / 60.0,
              lon0 + step * math.sin(brg) / 60.0 / math.cos(math.radians(lat0)))
        d = sorted((nm_between(p, at), f) for p, f in spots)
        if sum(1 for x, _f in d if x < radius) >= minimum:
            continue
        if all(x - radius <= window / 60.0 * f * 0.75
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


def is_passive(uid):
    """Every one of the unit's roles is a known non-combat one.

    Not the same as `not is_combat()`, which is true of any role missing from
    COMBAT_ROLES. usn_ssgn_ohio declares Role=SSGN and nothing else and
    carries a 1,000 NM Tomahawk; sea_mine declares SeaMine; neither is in
    either list. The census may miss them, but a gate that lets a unit start
    alongside the player because it is "not combat" has to be sure: a role
    NONCOMBAT_HINT does not name counts as one that fights.
    """
    roles = ai_roles(uid)
    return bool(roles) and roles <= NONCOMBAT_HINT


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

    def armed_reach(u):
        kind_dir, path = unit_file(u["uid"])
        if path is None:
            return 0.0
        fit = u["fit"]
        if fit is None:
            fit, _why = pick_loadout(u["uid"], path, None)
        return reach(u["uid"], kind_dir, path, fit)

    # An escort is anything armed that sails: a surface ship at the 24 kn
    # this file uses everywhere, or a boat at the reach check's 10 kn dived.
    # Only surface ships counted once, so a tender meeting her submarine
    # with the frigate drawing a patrol off thirty miles east was refused
    # as unescorted. The one that gets closest in the clock is the escort.
    # A hull marked independent=True sails alone on purpose (place() records
    # it) and is not measured at all.
    knots = {"sea": ship_speed("Vessel", mission, calm=24.0),
             "sub": TRANSIT["Submarine"]}
    # A hull whose weapons are switched off at the start (disable=) carries
    # them and cannot fire them: TS11A's corvette is not her own escort.
    disarmed = {tag for tag, systems in mission.get("_disabled", [])
                if "weapons" in systems}
    escorts = [b for b in blue if b["kind"] in knots and armed_reach(b) > 0
               and b["tag"] not in disarmed]
    alone = mission.get("_independent", set())

    def short_of(e, pr):
        return (math.hypot(e["x"]-pr["x"], e["z"]-pr["z"]) - 2.0
                - mission["minutes"] / 60.0 * knots[e["kind"]])

    if escorts:
        for pr in protected:
            if pr["tag"] in alone:
                continue
            nearest = min(escorts, key=lambda e: short_of(e, pr))
            d = math.hypot(nearest["x"]-pr["x"], nearest["z"]-pr["z"])
            if short_of(nearest, pr) > 0:
                kn = knots[nearest["kind"]]
                CLOSURE_PROBLEMS.append(
                    f"{mission['key']}: {pr['tag']} ({pr['uid']}) is protected and "
                    f"the nearest escort ({nearest['tag']}, {nearest['uid']}) is "
                    f"{d:.0f} NM away - {mission['minutes']} minutes at {kn:.0f} kn is "
                    f"{mission['minutes'] / 60.0 * kn:.0f} NM. The escort cannot "
                    "reach what it escorts.")

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


# The opening, in nautical miles. Two surface ships' radars see each other's
# hulls out to about twenty miles (a Peykaap's set reads 17); a boat dived
# inside twenty-five is inside her own torpedo reach of the first ship she
# hears. Inside those, the first minute of the mission is the engagement.
OPENING_SURFACE_NM = 25.0
OPENING_SUB_NM = 25.0
# An armed aircraft needs this much flying between its spawn and its own
# launch range, so a raid is something the player sees coming. A standoff
# round (a YJ-12 at 270, a Kh-22 in four figures) is launched from far out
# in life too; past OPENING_AIR_STANDOFF_NM the question is only whether
# the bomber starts on the player's plot, which is where the AEW will see it.
OPENING_AIR_LEAD_NM = 20.0
OPENING_AIR_STANDOFF_NM = 100.0
# A spotter this close to a ship already has her track.
OPENING_SPOTTER_NM = 25.0
# A red radar aircraft gives every red shooter a track as far as its line of
# sight reaches, to this many miles at most (a KJ-600 at 26,000 ft sees about
# 200 NM): the role tokens are the game's own [AI] Role= values.
OPENING_RADAR_ROLES = frozenset({"AEW", "MaritimePatrol", "Recon", "ESM"})
OPENING_RADAR_NM = 220.0
# The height a SAM's radar is taken to sit at, for its line of sight to a
# player aircraft: about a destroyer's mast or a battery's tower.
OPENING_SAM_MAST_FT = 100.0
# The quiet opening: no red unit can fire in these first minutes. A raid
# that joins at this minute or later (enter=) is held to the raid rule
# instead (13 October, Fujian's Shadow).
OPENING_QUIET_MIN = 5
OPENING_PROBLEMS = []

_SHIP_REACH = {}


def ship_reach(uid, fit):
    """How far this unit can hit a SHIP, in NM: its anti-ship missiles and
    its torpedoes, not its SAMs, its air-to-air rounds or its sonobuoys -
    the three that made reach() read a Ka-28 as a 100 NM threat."""
    key = (uid, fit)
    if key in _SHIP_REACH:
        return _SHIP_REACH[key]
    kind_dir, path = unit_file(uid)
    best = 0.0
    if path is not None:
        if fit is None:
            fit, _why = pick_loadout(uid, path, None)
        # A tube fed from a magazine names no round itself: the Virginia's
        # four Mk63s say AssociatedMagazine=TorpedoRoom and her 22 Mk 48s
        # are listed only there, so stores() alone read her as unarmed and
        # RL02's boat passed this gate 21 NM from the escort.
        held = set(stores(uid, kind_dir, path, fit))
        body = read(path)
        for mag in set(re.findall(r"^AssociatedMagazine=\s*([\w-]+)", body, re.M)):
            sec = re.search(r"^\[" + re.escape(mag) + r"\]\s*$(.*?)(?=^\[|\Z)", body, re.M | re.S)
            if sec:
                held |= set(re.findall(r"^Ammunition\d*=([^\s#/|]+)", sec.group(1), re.M))
        for store in sorted(held):
            text = "".join(read(f) for f in all_copies(f"ammunition/{store}.ini"))
            kind = re.search(r"^Type=(\w+)", text, re.M)
            aim = re.search(r"^TargetType=(\w+)", text, re.M)
            if kind and (kind.group(1) == "Torpedo" or
                         (kind.group(1) == "Missile" and aim
                          and aim.group(1) == "ASuW")):
                best = max(best, ammo_range(store))
    _SHIP_REACH[key] = best
    return best


def air_reach(uid, fit):
    """How far this unit can hit an AIRCRAFT, in NM: its missiles whose
    TargetType is AAW - a fighter's air-to-air rounds, a ship's or a
    battery's SAMs - read the way ship_reach() reads anti-ship rounds,
    magazines included."""
    key = (uid, fit)
    if key in _AIR_REACH:
        return _AIR_REACH[key]
    kind_dir, path = unit_file(uid)
    best = 0.0
    if path is not None:
        if fit is None:
            fit, _why = pick_loadout(uid, path, None)
        held = set(stores(uid, kind_dir, path, fit))
        body = read(path)
        for mag in set(re.findall(r"^AssociatedMagazine=\s*([\w-]+)", body, re.M)):
            sec = re.search(r"^\[" + re.escape(mag) + r"\]\s*$(.*?)(?=^\[|\Z)", body, re.M | re.S)
            if sec:
                held |= set(re.findall(r"^Ammunition\d*=([^\s#/|]+)", sec.group(1), re.M))
        for store in sorted(held):
            text = "".join(read(f) for f in all_copies(f"ammunition/{store}.ini"))
            kind = re.search(r"^Type=(\w+)", text, re.M)
            aim = re.search(r"^TargetType=(\w+)", text, re.M)
            if kind and kind.group(1) == "Missile" and aim and aim.group(1) == "AAW":
                best = max(best, ammo_range(store))
    _AIR_REACH[key] = best
    return best


_AIR_REACH = {}


def radar_horizon(alt_ft, mast_ft=60.0):
    """Radar line of sight in NM between two heights: 1.23 x (sqrt h1 +
    sqrt h2), the standard 4/3-earth figure."""
    return 1.23 * (math.sqrt(max(alt_ft, 0.0)) + math.sqrt(max(mast_ft, 0.0)))


def check_opening(mission, placed):
    """Does the mission open with a fight already in progress?

    The first public report (October 2026) said it of White Water, Steel
    Highway and Southern Cross, and the files agreed: a Peykaap inside its
    own radar of the merchants, a 039C thirteen miles from the escorts with
    its weapons free, a boat with a drone over the patrol ship and Nasir in
    reach of her from the first second. A player cannot classify, position
    or decide anything in a mission whose opening is the attack.

    The in-game check of 13 October said it again of Fujian's Shadow, which
    this gate had passed: the H-6K's YJ-12s (270 NM) reached Ford at 126 NM
    because an aircraft's reach was counted to 100 NM at most; the 093B's
    YJ-18s reached everything from 54 NM with the KJ-600 giving the track,
    and neither a boat's missiles nor a radar aircraft's picture was
    counted; the J-35 and J-20A were half a minute from PL-15 range of the
    F-35Cs and nothing measured air against air.

    So the opening is now OPENING_QUIET_MIN minutes in which nothing red can
    fire. A red unit in the mission then - from the start, or joining
    before that minute (enter=) - whose weapons are FREE (Tight and Hold do
    not fire first) is refused when:

      - it is a surface ship inside OPENING_SURFACE_NM, or a boat inside
        OPENING_SUB_NM, of the player's nearest hull;
      - it is an armed aircraft with less than OPENING_AIR_LEAD_NM of flying
        before its own anti-ship launch range - the whole range, however
        long: a standoff bomber that can fire at the first second is the
        fight in progress;
      - it is a ship, a boat or a battery holding a player hull inside its
        anti-ship reach with a track on her: its own radar inside
        OPENING_SURFACE_NM, a red aircraft within OPENING_SPOTTER_NM of her,
        or a red radar aircraft (AEW, maritime patrol, reconnaissance) whose
        line of sight reaches her;
      - it is an aircraft with less than OPENING_AIR_LEAD_NM of flying before
        its air-to-air reach of a player aircraft in the air; or
      - it is a ship or a battery holding a player aircraft inside its SAM
        reach and its radar's line of sight.

    A unit that joins at OPENING_QUIET_MIN or later is a raid the player has
    had the quiet minutes to prepare for: it is held to the rule a raid was
    always held to - an armed aircraft with OPENING_AIR_LEAD_NM of flying
    before its launch range, that range counted to OPENING_AIR_STANDOFF_NM
    at most, and a ship or boat outside the 25 NM rings - measured from
    where it joins.

    A unit the story puts in contact on purpose says so with contact="why".
    The player's own units are not measured: the player sets their weapons
    before the clock starts.
    """
    joins = mission.get("_enter", {})

    def rows(prefix):
        out = []
        for family, entries in placed.items():
            if not family.startswith(prefix):
                continue
            kind = ("air" if family.endswith(("Aircraft", "Helicopter")) else
                    "sub" if family.endswith("Submarine") else
                    "land" if family.endswith("LandUnit") else "sea")
            for tag, keys, name, _x in entries:
                bits = keys.get("RelativePositionInNM", "").split(",")
                try:
                    x, z = float(bits[0]), float(bits[2])
                except (ValueError, IndexError):
                    continue
                try:
                    alt = float(bits[1])
                except ValueError:
                    alt = 0.0
                out.append(dict(tag=tag, uid=keys["Type"], x=x, z=z, kind=kind,
                                alt=alt, depth=bits[1].lower(), name=name,
                                free=keys.get("WeaponStatus") == "Free",
                                fit=keys.get("LoadoutVariant"),
                                joins=joins.get(tag)))
        return out

    player, red = rows("Taskforce1"), rows("Taskforce2")
    hulls = [b for b in player if b["kind"] in ("sea", "sub")]
    flying = [b for b in player if b["kind"] == "air" and b["alt"] > 0
              and (b["joins"] is None or b["joins"] < OPENING_QUIET_MIN)]
    excused = mission.get("_contact", set())

    def gap(a, b):
        return math.hypot(a["x"] - b["x"], a["z"] - b["z"])

    def nearest(u, among):
        h = min(among, key=lambda b: gap(b, u))
        return h, gap(h, u)

    def who(u):
        return f"{u['tag']} ({u['uid']}{', ' + u['name'] if u['name'] else ''})"

    def opening(u):
        return u["joins"] is None or u["joins"] < OPENING_QUIET_MIN

    def flag(u, text):
        when = ("starts" if u["joins"] is None
                else f"joins at minute {u['joins']:g} and")
        OPENING_PROBLEMS.append(f"{mission['key']}: {who(u)} {when} weapons free {text}")

    # Who gives a red shooter its track at the start: anything red flying
    # within OPENING_SPOTTER_NM of the target, or a red radar aircraft whose
    # line of sight reaches it.
    eyes = [r for r in red if r["kind"] == "air" and opening(r)]

    def track(hull):
        # A radar aircraft cannot provide an anti-ship track on a boat below
        # the layer. The separate close-submarine gate still applies. Numeric
        # positive values are depths here; 0 and periscope stay conservative.
        if hull["kind"] == "sub" and hull["depth"] not in ("0", "0.0", "periscope", "surface"):
            return None
        for s in eyes:
            d = gap(s, hull)
            if d < OPENING_SPOTTER_NM:
                return f"{who(s)} {d:.0f} NM from her"
            if (ai_roles(s["uid"]) & OPENING_RADAR_ROLES
                    and d <= min(radar_horizon(s["alt"]), OPENING_RADAR_NM)):
                return f"{who(s)}'s radar on her from {d:.0f} NM"
        return None

    for r in red:
        if not r["free"] or r["tag"] in excused:
            continue
        hits = ship_reach(r["uid"], r["fit"])
        start = opening(r)
        if hulls and hits:
            hull, d = nearest(r, hulls)
            to = f"{d:.0f} NM from {hull['tag']} ({hull['uid']})"
            if r["kind"] == "sea" and d < OPENING_SURFACE_NM:
                flag(r, f"{to} - inside {OPENING_SURFACE_NM:.0f} NM, each on the "
                        "other's radar from the first second")
            elif r["kind"] == "sub" and d < OPENING_SUB_NM:
                flag(r, f"{to} - inside {OPENING_SUB_NM:.0f} NM, with {hits:.0f} NM "
                        "of torpedo or missile")
            elif r["kind"] == "air":
                need = (hits if start else min(hits, OPENING_AIR_STANDOFF_NM)) \
                    + OPENING_AIR_LEAD_NM
                if d < need:
                    flag(r, f"{to} - its anti-ship reach is {hits:.0f} NM; it needs "
                            f"{need:.0f} NM so the raid is seen coming"
                            + ("" if not start else
                               f" (or enter= at minute {OPENING_QUIET_MIN} or later)"))
            elif start and d <= hits:
                eye = ("its own radar" if r["kind"] != "sub" and d < OPENING_SURFACE_NM
                       else track(hull))
                if eye:
                    flag(r, f"{to} - inside its {hits:.0f} NM anti-ship reach, with "
                            f"{eye} giving the track from the first second")
        if not (start and flying):
            continue
        aa = air_reach(r["uid"], r["fit"])
        if not aa:
            continue
        plane, d = nearest(r, flying)
        to = f"{d:.0f} NM from {plane['tag']} ({plane['uid']})"
        if r["kind"] == "air" and d < aa + OPENING_AIR_LEAD_NM:
            flag(r, f"{to} - its air-to-air reach is {aa:.0f} NM; it needs "
                    f"{aa + OPENING_AIR_LEAD_NM:.0f} NM (or enter= at minute "
                    f"{OPENING_QUIET_MIN} or later)")
        elif (r["kind"] in ("sea", "land")
              and d <= min(aa, radar_horizon(plane["alt"], OPENING_SAM_MAST_FT))):
            flag(r, f"{to} - inside its {aa:.0f} NM SAM reach and its radar's "
                    "line of sight from the first second")


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
    steam = mission["minutes"] / 60.0 * ship_speed("Vessel", mission, calm=24.0)

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
    # pair does not count toward it. Nor does a red unit at weapons Hold
    # whose every [AI] Role is a known non-combat one: an armed coaster
    # sailing in company with the player's group (Role=Spy) will not open
    # fire and is not built to, so it is the situation the player is briefed
    # on, not an ambush. Free, Tight or any role is_passive() does not know
    # and the gate applies as before.
    passive = {tag for family, entries in placed.items()
               if family.startswith("Taskforce2")
               for tag, keys, _n, _x in entries
               if keys.get("WeaponStatus") == "Hold" and is_passive(keys["Type"])}
    afloat = [math.hypot(x - bx, z - bz)
              for t, _u, x, z, ashore, _f, _fl, _mv in red if t not in passive
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
    for lift in mission.get("lift", []):
        placer.point(lift["at"], f"{key} {lift['objective']} lift area")


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
    # A stage that holds the units inside an area until a minute (Macquarie
    # Passage's service check: both ships within five miles of Supply's
    # start at minute 30) is time they spend at anchor, not on the way.
    hold = hold_minutes(victory)
    window = mission["minutes"] - hold
    for d, tag, family in found[:minimum]:
        speed = transit_of(tag, placed, mission)
        reach = window / 60.0 * speed * 0.75
        if d - radius > reach:
            # Reported, not raised: one build names every short box, so a
            # pass over the sea-state table does not take a rebuild per
            # mission to read.
            REACH_PROBLEMS.append(
                f"{mission['key']}: {tag} is one of the {minimum} units the "
                f"arrival condition needs and must cover {d - radius:.1f} NM; "
                f"{window} minutes under way"
                + (f" (the {hold}-minute hold taken off)" if hold else "")
                + f" at a conservative {speed:.1f} kn in sea state "
                f"{mission.get('sea', 0)} buys {reach:.1f} NM. Move the box "
                "or lengthen the mission.")


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
    if mission.get("victory", {}).get("or_destroyed"):
        out.append(("victory.or_destroyed", mission["victory"]["or_destroyed"]))
    after = mission.get("victory", {}).get("after", {})
    if after.get("lost"):
        out.append(("victory.after.lost (stage lost)", after["lost"]))
    if after.get("intel"):
        out.append(("victory.after.intel (stage intel)", after["intel"]))
    if after.get("held"):
        out.append(("victory.after.held (stage held)", after["held"]))
    for i, deny in enumerate(mission.get("denied", []), 1):
        out.append((f"denied[{i}].message", deny["message"]))
    for oid, reward in mission.get("reveals", {}).items():
        out.append((f"reveals[{oid}].intel", reward["intel"]))
    for i, loss in enumerate(mission.get("support_loss", []), 1):
        out.append((f"support_loss[{i}].intel", loss["intel"]))
    for i, report in enumerate(mission.get("reports", []), 1):
        if not 0 < report["minute"] < mission["minutes"]:
            raise SystemExit(f"{mission['key']}: report {i} falls outside the mission")
        out.append((f"reports[{i}].intel", report["intel"]))
    for reveal in mission.get("reveal_if", []):
        out.append((f"reveal_if[{reveal['variable']}].intel", reveal["intel"]))
    for flag in mission.get("flags", []):
        if flag.get("intel"):
            out.append((f"flags[{flag['name']}].intel", flag["intel"]))
    for i, cutoff in enumerate(mission.get("reinforcement_cutoffs", []), 1):
        out.append((f"reinforcement_cutoffs[{i}].intel", cutoff["intel"]))
    for find in mission.get("discoveries", []):
        out.append((f"discoveries[{find['objective']}].intel", find["intel"]))
    for lift in mission.get("lift", []):
        out.append((f"lift[{lift['objective']}].intel", lift["intel"]))
    return out


_ONES = ("", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
         "sixteen", "seventeen", "eighteen", "nineteen")
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
         "eighty", "ninety")


def number_words(n):
    """1..999 in the texts' own style: 'seventy-five', 'one hundred and twelve'."""
    n = int(n)
    if n < 20:
        return _ONES[n] or "zero"
    if n < 100:
        return _TENS[n // 10] + ("-" + _ONES[n % 10] if n % 10 else "")
    rest = n % 100
    return (_ONES[n // 100] + " hundred"
            + (" and " + number_words(rest) if rest else ""))


def clock_text(mission, text):
    """Fill a message's clock placeholders from the mission, so a text that
    names the minute it is shown at cannot drift from the trigger that shows
    it: {deadline} / {Deadline} is the deadline in minutes, spelled out, and
    {deadline_clock} the HHMM it falls on (the mission's start plus the
    deadline, modulo a day)."""
    dl = deadline_minutes(mission)
    h, m = mission.get("time", (0, 0))
    clock = (h * 60 + m + dl) % (24 * 60)
    words = number_words(dl)
    return (text.replace("{Deadline}", words[:1].upper() + words[1:])
                .replace("{deadline}", words)
                .replace("{deadline_clock}", f"{clock // 60:02d}{clock % 60:02d}"))


# A timeout body that names its own minute - "Seventy-five minutes and...",
# "within ninety minutes", "0820, and..." - was right when the Deadline was
# the planned window and wrong the day the Deadline moved. The figure is the
# builder's to write (clock_text); an authored one stops the build.
_TIMEOUT_FIGURE = re.compile(
    r"\b(?:\d{2,3}|(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"one hundred(?: and)?)(?:[- ](?:one|two|three|four|five|six|seven|eight|"
    r"nine))?)\s+minutes\b"
    r"|(?<![\d{\w])[0-2]\d[0-5]\d(?![\d}])", re.I)


def check_message_texts(mission):
    hit = _TIMEOUT_FIGURE.search(mission.get("timeout", ""))
    if hit:
        raise SystemExit(
            f"{mission.get('code', mission['num'])} {mission['key']}: the timeout "
            f"text names a time ({hit.group(0)!r}), and the Deadline that shows it "
            "is not the planned window. Write {Deadline} / {deadline} for the "
            "deadline in minutes or {deadline_clock} for its HHMM; the builder "
            "fills them from the mission.")
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


# --- deployment zones: where the player may place the force ------------------
# The game lets a player move units before a mission only inside a [Zones]
# entry of Type=Deployment for their side (ui.ini: "Defines a gameplay
# deployment area where eligible units for the selected side can be placed").
# No SEST mission wrote one, so every force started exactly where the file put
# it and could not be moved (user report, 13 Oct: "when starting campaign, i
# cant move my task force around at all"). Stock Pacific Strike draws a blue
# rectangle round its anchor (02, 06, 07, 10: 20 x 30 to 90 x 215 NM) that
# opens away from the enemy - 06's anchor sits 3.4 NM inside the edge facing
# Lombok - and a submarine-only box ("Sub Patrol Box", 09 and 10) for a boat
# that starts away from the surface force.
#
# The same shapes here, with the rule the stock boxes keep by eye written
# down: a zone opens away from the enemy, never toward it. The box starts as
# the hulls' own extent plus DEPLOY_PAD_NM all round - room for the formation
# - and each side then opens up to DEPLOY_OPEN_NM further, a mile at a time.
# A side stops where the next mile would bring an enemy in play nearer than
# the padded box already is (by more than DEPLOY_SLACK_NM), or would put the
# edge on land. "In play" is an enemy whose anti-ship reach - DEPLOY_SEEN_NM
# for one with none - comes within DEPLOY_OPEN_NM of the padded box. The
# mission's goals hold the box back the same way, wherever they are: an
# arrival or lift point, a stage area, and any contact an objective names
# (the merchant to classify, the ship to sink). So the player can pull back
# and spread out, and no opening - or transit - gets shorter than the
# mission's own by more than the pad.
#
# Every playable unit gets a box (the player's decision of 14 Oct 2026: "for
# all missions give every playable unit a movable zone, i.e. the Global Hawk
# or Seahawks flying included in the mission plan etc"). The main group - the
# hulls chained within DEPLOY_CLUSTER_NM of the anchor - keeps its all-types
# box as above. Every other player unit with a position that this box does
# not already cover is clustered the same way, aircraft, helicopters and
# mobile land units included, and each cluster gets a box admitting only the
# types in it: a boat alone a submarine box, a flight an aircraft box, a
# convoy a vessel box, a battery a land box. A base - an airbase, a port, a
# rig, an installation, a bridge (DEPLOY_FIXED_LAND, by LandUnitSubType) - is
# a place, not a unit the player moves, and gets none. The far boxes open by
# the same rules as the first; the land test applies only to a box a hull
# could be dragged ashore from, so an aircraft box may lie over land. A far
# box that admits Vessel can take the formation as the first box can; the
# player accepted that with the decision.
#
# What an aircraft is at the start: a Taskforce1Aircraft or
# Taskforce1Helicopter section with RelativePositionInNM and an altitude,
# airborne. Stock writes no other kind: the 182 player aircraft and
# helicopter sections in the 153 shipped mission and campaign files all
# carry RelativePositionInNM with an altitude (one P-3C at 0, in the
# prototype campaign's 04B), and no key among the 25 they use parks one at
# a field. The campaign's owned aircraft enter a mission only through an
# air-tasking slot, which is such a section with the player's airframe in
# it. So every such section is a candidate, slot placeholders included; an
# owned aircraft with no slot is not in the mission at all.
#
# Positions are plain arcminutes on both axes (lat = centre + z/60, lon =
# centre + x/60), as the game reads RelativePositionInNM: stock 10's map
# symbols sit 0.05-0.4 NM from their units that way and 13-28 NM off with a
# cos(lat) correction. GeoPoint is the rectangle's centre - every stock
# anchor is inside its box only on that reading - and WidthNm (east-west)
# and HeightNm (north-south) are in the same units.
DEPLOY_PAD_NM = 3.0
DEPLOY_OPEN_NM = 25.0
DEPLOY_SLACK_NM = 0.5
DEPLOY_SEEN_NM = 50.0
DEPLOY_CLUSTER_NM = 25.0
DEPLOY_LAND_DEG = 0.03          # about 2 NM of sea beyond the edge
DEPLOY_ALL = "Vessel,Submarine,Helicopter,Aircraft,Land"
# The AllowedUnitTypes word for each player section family.
DEPLOY_TYPE = {"Vessel": "Vessel", "Submarine": "Submarine", "Aircraft": "Aircraft",
               "Helicopter": "Helicopter", "LandUnit": "Land"}
# Land units that are places, not units, by LandUnitSubType
# (fix_land_positions.land_unit): the builder's own STAYS set - an airbase,
# a port or a rig brings its own ground and is never moved to find it - plus
# the structures, Installation (a FOB, a bunker, a plant) and Bridge. The
# other subtypes in the collection (SAM, MissileSite, Radar, AAA, MobileUnit)
# are batteries, launchers, radars, guns and vehicles: mobile, and boxed. A
# subtype the builder cannot read is treated as mobile, so it gets a box.
DEPLOY_FIXED_LAND = frozenset(fix_land_positions.STAYS) | {"Installation", "Bridge"}
# A unit is held by a box when it is this far inside the edge or more. The
# pad keeps every unit DEPLOY_PAD_NM in; this only absorbs the rounding of
# the written GeoPoint (six decimals) and WidthNm/HeightNm (one).
DEPLOY_HOLD_NM = 0.1
# No box that admits a kind of unit a circle counts reaches within this of
# the circle while units it counts have still to arrive (14 Oct 2026: with
# the boxes opened 25 NM, a force moved forward in Southern Watch 10 or
# Tasman Shield 04 could be placed inside its own arrival circle and win
# before the clock started; twelve missions' boxes overlapped one). The
# game lets a unit be placed in ANY box that admits its type - stock's 10
# Vengeance at Luzon gives its one submarine a second, empty patrol box -
# so the rule is on what a box admits, not on what it holds: an escort of
# the convoy's kind waiting within the clearance gets no box at all. Where
# a counted unit itself starts nearer, boxes of its kind may reach its own
# distance less DEPLOY_START_ALLOW_NM - the designer's start, no nearer. A
# circle every counted unit starts inside (a service window the force
# keeps, Southern Watch 09's) is a station, not a limit.
DEPLOY_CLEAR_NM = 5.0
# The pad a side keeps when it is pulled in to face a circle: enough to hold
# the unit on that edge (DEPLOY_HOLD_NM in), no more; the smaller pads are
# tried when that one still comes too near (a box's corner lies a pad's
# diagonal beyond the unit, and a cluster's corner nearer than any ship).
DEPLOY_NEAR_PAD_NM = 0.5
DEPLOY_PULL_PADS = (DEPLOY_NEAR_PAD_NM, 0.3, 0.15)
# How much nearer a circle than the nearest unit it counts starts a box of
# that unit's kind may reach: the pad and the corner beyond it.
DEPLOY_START_ALLOW_NM = 1.0
DEPLOY_EDGE_NM = 0.5            # a counted unit this near a circle's edge gets no box
DEPLOY_KEEP_OUT_NM = 0.3        # how far outside a generated mission's box its other units stay


def rect_nm(rect, x, z):
    """Distance from (x, z) to the rectangle (x0, x1, z0, z1), 0 inside."""
    x0, x1, z0, z1 = rect
    return math.hypot(max(x0 - x, 0.0, x - x1), max(z0 - z, 0.0, z - z1))


def deployment_goals(mission, members):
    """(lat, lon) points and unit tags the player is sent to reach.

    Read before the triggers are built, so a malformed term is left for the
    trigger builder to refuse with its own message rather than tripped on.
    """
    points, tags = [], set()
    v = mission.get("victory", {})
    if v.get("kind") == "arrive" and v.get("at"):
        points.append(v["at"])
    points += [extra["at"] for extra in v.get("also", [])
               if isinstance(extra, dict) and extra.get("at")]
    if isinstance(v.get("after"), dict) and v["after"].get("at"):
        points.append(v["after"]["at"])
    points += [lift["at"] for lift in mission.get("lift", [])
               if isinstance(lift, dict) and lift.get("at")]
    for how in mission.get("resolve", {}).values():
        if not isinstance(how, tuple) or len(how) < 2:
            continue
        if how[0] == "arrive" and len(how) > 2:
            points.append(how[2])
        if how[0] in ("classify", "destroy"):
            for r in ([how[1]] if isinstance(how[1], str) else how[1]):
                tags.update(refs(members, r))
    if v.get("kind") == "destroy":
        for r in v.get("stations", [v.get("station")]):
            if r:
                tags.update(refs(members, r))
    return points, tags


def deployment_areas(mission, placed, members):
    """Every circle a player unit's presence completes a stage or the
    mission in, or lifts a restraint in: dicts of x, z, r in the mission's
    NM frame and counted, the tags the condition names, read from the spec
    with the keys and defaults the trigger builder uses. check_zone_areas()
    reads the written file back, so a circle this misses stops the build
    there rather than shipping."""
    centre = mission["centre"]

    def nm(at):
        return (at[1] - centre[1]) * 60.0, (at[0] - centre[0]) * 60.0

    def tags(ref_or_list):
        wanted = [ref_or_list] if isinstance(ref_or_list, str) else list(ref_or_list or [])
        return {tag for r in wanted for tag in refs(members, r)}

    def area(at, r, counted):
        x, z = nm(at)
        return dict(x=x, z=z, r=float(r), counted=set(counted))

    out = []
    v = mission.get("victory", {})
    stage = v.get("after")
    if v.get("kind") == "arrive" and v.get("at"):
        if isinstance(stage, dict) and stage.get("per_unit"):
            counted = tags(stage.get("units"))      # one chain per unit of the stage's
        else:
            counted = tags(v["units"]) if v.get("units") else tags(v.get("station"))
        out.append(area(v["at"], v.get("radius", 20), counted))
    for extra in v.get("also", []):
        if not isinstance(extra, dict):
            continue
        kind = extra.get("kind") or ("time" if "after_minutes" in extra else "area")
        at = extra.get("at") or v.get("at")
        if kind == "area" and at:
            out.append(area(at, extra.get("radius", v.get("radius", 20)), tags(extra.get("units"))))
    if isinstance(stage, dict) and stage.get("kind") == "area":
        at = stage.get("at")
        if stage.get("at_unit"):
            ref = refs(members, stage["at_unit"])[0]
            for _fam, entries in placed.items():
                for tag, keys, _n, _x in entries:
                    if tag == ref and unit_spot(keys):
                        x, z = unit_spot(keys)
                        at = (centre[0] + z / 60.0, centre[1] + x / 60.0)
        if at:
            out.append(area(at, stage.get("radius", 3), tags(stage.get("units"))))
    for how in mission.get("resolve", {}).values():
        if isinstance(how, tuple) and len(how) > 3 and how[0] == "arrive":
            out.append(area(how[2], how[3], tags(how[1])))
    for lift in mission.get("lift", []):
        if isinstance(lift, dict) and lift.get("at") and lift.get("radius") is not None:
            out.append(area(lift["at"], lift["radius"], tags(lift.get("units"))))
    # one circle, however many conditions name it: the units any of them counts
    merged = {}
    for a in out:
        key = (round(a["x"], 3), round(a["z"], 3), a["r"])
        merged.setdefault(key, a)["counted"] |= a["counted"]
    return list(merged.values())


PARKED_NOTES = []


def deploy_type(tag, keys):
    """The AllowedUnitTypes word a box must carry to hold this player
    section, or None for one the player does not move: a base
    (DEPLOY_FIXED_LAND), or a section of no boxed family."""
    m = re.match(r"Taskforce1(Vessel|Submarine|Aircraft|Helicopter|LandUnit)\d+$", tag)
    if not m:
        return None
    if m.group(1) == "LandUnit":
        sub = fix_land_positions.land_unit(keys["Type"])[0]
        return None if sub in DEPLOY_FIXED_LAND else "Land"
    return DEPLOY_TYPE[m.group(1)]


def deploy_units(placed):
    """(tag, keys, x, z, type word) for every player unit a box must hold,
    in the file's own order."""
    out = []
    for family in FAMILY_ORDER:
        if not family.startswith("Taskforce1"):
            continue
        for tag, keys, _n, _x in placed.get(family, []):
            ty = deploy_type(tag, keys)
            xz = unit_spot(keys)
            if ty and xz:
                out.append((tag, keys, xz[0], xz[1], ty))
    return out


def zone_box(zone, centre):
    """A zone dict's (x0, x1, z0, z1) in the mission's NM frame, read back
    from the GeoPoint, WidthNm and HeightNm the file will carry."""
    cx = (zone["at"][1] - centre[1]) * 60.0
    cz = (zone["at"][0] - centre[0]) * 60.0
    return (cx - zone["width"] / 2.0, cx + zone["width"] / 2.0,
            cz - zone["height"] / 2.0, cz + zone["height"] / 2.0)


def zone_holds(zone, centre, x, z, ty):
    """Does this zone admit the type and hold the point, DEPLOY_HOLD_NM in?"""
    if ty not in zone["types"].split(","):
        return False
    x0, x1, z0, z1 = zone_box(zone, centre)
    return (x0 + DEPLOY_HOLD_NM <= x <= x1 - DEPLOY_HOLD_NM
            and z0 + DEPLOY_HOLD_NM <= z <= z1 - DEPLOY_HOLD_NM)


def zone_label(types):
    """The label for a box past the first: stock's own kind of name for a
    boat's box, and the two this pack adds."""
    kinds = set(types.split(","))
    if kinds == {"Submarine"}:
        return "Submarine Patrol Box"
    if kinds <= {"Aircraft", "Helicopter"}:
        return "Air Station"
    return "Detachment Zone"


def deployment_zones(mission, placed, members):
    """The blue Deployment zones for one mission, as dicts.

    One zone for the group of hulls the force forms on (the anchor's, else
    the first ship's), taking every unit type as stock's do; then one for
    each cluster of the player's other units that this box does not already
    hold - a boat on her own, a flight on station, a convoy far off, a
    battery ashore - admitting only the types in the cluster. A cluster is
    units chained within DEPLOY_CLUSTER_NM of each other. Bases get none
    (deploy_type). Labels past the first are numbered where one repeats, as
    stock numbers its "Sub Patrol Box 1" and "2" (10 Vengeance at Luzon).
    """
    centre = mission["centre"]
    units = deploy_units(placed)
    areas = deployment_areas(mission, placed, members)
    keys_of = {tag: keys for entries in placed.values() for tag, keys, _n, _x in entries}
    spot = {tag: unit_spot(keys) for tag, keys in keys_of.items() if unit_spot(keys)}

    def counted_types(a):
        return {deploy_type(t, keys_of[t]) for t in a["counted"] if t in keys_of} - {None}

    def clearance(tag, a):
        x, z = spot[tag]
        return math.hypot(x - a["x"], z - a["z"]) - a["r"]

    # Task Force Mode, the stock pattern (15 Oct 2026). In a Generated or
    # Replaced mission the game builds the player's force from what they
    # own, and a Deployment zone is where that force goes: stock's 10
    # Vengeance at Luzon boxes the anchor (the hull it replaces with the
    # player's first ship) and its four air-tasking slots, and nothing else.
    # The 13 and 14 Oct builds boxed the convoys, escorts and recon aircraft
    # the mission supplies, and the player reported them missing in game.
    # So here only the anchor and the slot-tagged aircraft get a box, and no
    # box may hold any other Taskforce1 unit: every other one keeps its
    # authored place, unmovable, as before 13 Oct. A mission that launches
    # as authored (blank generation) keeps the boxes below.
    generated = bool(mission.get("generation"))
    keep_out = []
    if generated:
        holders = {mission.get("_anchor_section")} | {
            tag for tag, keys in keys_of.items()
            if tag.startswith("Taskforce1") and "TaskForceModeAirTaskingSlot" in keys}
        holders.discard(None)
        keep_out = [spot[tag] for tag in spot if tag.startswith("Taskforce1") and tag not in holders]
        units = [u for u in units if u[0] in holders]
        areas = [a for a in areas if a["counted"] & holders]
        mission["_holders"] = holders

    # The game lets a unit be placed in ANY box that admits its type (stock's
    # 10 Vengeance at Luzon offers its one submarine a second, empty patrol
    # box), so what a box holds at the start does not limit what can be put
    # in it. A circle is LIVE while a unit it counts has still to arrive;
    # one that every counted unit starts inside (a service window)
    # constrains nothing.
    live = [a for a in areas
            if any(t in spot and clearance(t, a) >= 0 for t in a["counted"])]

    # No box: a unit of a kind a live circle counts, not counted by it,
    # within the clearance - an escort waiting near where its convoy must
    # arrive: any box round it admits the convoy's kind, and the convoy
    # could be placed there. Nor a counted unit inside the circle or at its
    # edge, where no box round it stays out. Each stays where the mission
    # puts it.
    parked = {}
    for u in ([] if generated else units):
        for a in live:
            if u[4] not in counted_types(a):
                continue
            c = clearance(u[0], a)
            where = f"{-c:.1f} NM inside" if c < 0 else f"{c:.1f} NM off the edge of"
            circle = f"the {a['r']:g} NM circle at {a['x']:.1f},{a['z']:.1f} NM"
            if u[0] in a["counted"]:
                if c < DEPLOY_EDGE_NM:
                    parked[u[0]] = (f"starts {where} {circle} it must reach, which others "
                                    "have still to reach - no box round it stays out of it")
                    break
            elif c < DEPLOY_CLEAR_NM:
                parked[u[0]] = (f"starts {where} {circle} that counts other units of its "
                                "kind - a box round it would let them be placed there")
                break
    mission["_parked"] = parked
    PARKED_NOTES.extend(f"{mission['key']}: {keys_of[tag]['Type']} at {tag} has no box - {why}"
                        for tag, why in parked.items())
    units = [u for u in units if u[0] not in parked]
    if not units:
        return []
    order = {u[0]: i for i, u in enumerate(units)}

    def chain(items):
        """Single-linkage groups, each in file order, in order of first member.
        In a generated mission each unit is a group of its own: a box round
        two slots far apart could take in a supplied ship between them."""
        if generated:
            return [[h] for h in sorted(items, key=lambda u: order[u[0]])]
        groups = []
        for h in items:
            joined = [g for g in groups
                      if any(math.hypot(h[2] - o[2], h[3] - o[3]) <= DEPLOY_CLUSTER_NM for o in g)]
            merged = [h] + [o for g in joined for o in g]
            groups = [g for g in groups if g not in joined] + [merged]
        return sorted((sorted(g, key=lambda u: order[u[0]]) for g in groups),
                      key=lambda g: order[g[0][0]])

    def spots(prefix):
        out = []
        for family, entries in placed.items():
            if family.startswith(prefix):
                for tag, keys, _n, _x in entries:
                    xz = unit_spot(keys)
                    if xz:
                        out.append((tag, keys, xz[0], xz[1]))
        return out

    red = []
    for tag, keys, x, z in spots("Taskforce2"):
        reach = 0.0 if "LandUnit" in tag else ship_reach(keys["Type"], keys.get("LoadoutVariant"))
        red.append((tag, x, z, max(reach, DEPLOY_SEEN_NM)))
    points, targets = deployment_goals(mission, members)
    goals = [((lon - centre[1]) * 60.0, (lat - centre[0]) * 60.0)
             for lat, lon in points]
    goals += [(x, z) for tag, _k, x, z in spots("") if tag in targets]

    def water(x, z):
        return fix_land_positions.water(centre[0] + z / 60.0, centre[1] + x / 60.0,
                                        clearance=DEPLOY_LAND_DEG)

    def cut_out(box, extent):
        """box with each other Taskforce1 unit of a generated mission cut
        out of it: for each one inside (or within DEPLOY_KEEP_OUT_NM), the
        side between it and the group moves in to leave it outside, the cut
        that keeps the most area. A unit inside the group's own extent on
        both axes cannot be cut out; the gate names it."""
        b = list(box)
        for x, z in keep_out:
            if rect_nm(b, x, z) >= DEPLOY_KEEP_OUT_NM:
                continue
            room = 2 * DEPLOY_HOLD_NM          # the group stays this far inside
            options = []
            if x > extent[1]:
                options.append((1, max(extent[1] + room, x - DEPLOY_KEEP_OUT_NM)))
            if x < extent[0]:
                options.append((0, min(extent[0] - room, x + DEPLOY_KEEP_OUT_NM)))
            if z > extent[3]:
                options.append((3, max(extent[3] + room, z - DEPLOY_KEEP_OUT_NM)))
            if z < extent[2]:
                options.append((2, min(extent[2] - room, z + DEPLOY_KEEP_OUT_NM)))
            best = None
            for i, v in options:
                trial = list(b)
                trial[i] = v
                area = (trial[1] - trial[0]) * (trial[3] - trial[2])
                # the cut must leave the unit clearly outside
                if rect_nm(trial, x, z) >= DEPLOY_KEEP_OUT_NM / 2 and (best is None or area > best[0]):
                    best = (area, trial)
            if best:
                b = best[1]
        return b

    def need(a, kind):
        """How far outside live circle a a box admitting kind must stay:
        the clearance, or - where a unit of that kind the circle counts
        already starts nearer - that unit's own distance less the start
        allowance (the designer's start, no nearer), never inside."""
        own = [clearance(tag, a) for tag in a["counted"]
               if tag in spot and tag not in parked and deploy_type(tag, keys_of[tag]) == kind]
        return min(DEPLOY_CLEAR_NM, max(0.0, min(own) - DEPLOY_START_ALLOW_NM) if own
                   else DEPLOY_CLEAR_NM)

    def pulled(box, ext, a, pad):
        """box with each side that faces circle a pulled in to the extent
        ext of the units it is kept for, plus pad."""
        b = list(box)
        if a["x"] < ext[0]:
            b[0] = max(b[0], ext[0] - pad)
        if a["x"] > ext[1]:
            b[1] = min(b[1], ext[1] + pad)
        if a["z"] < ext[2]:
            b[2] = max(b[2], ext[2] - pad)
        if a["z"] > ext[3]:
            b[3] = min(b[3], ext[3] + pad)
        return b

    def keeps(box, a, want):
        """Does box stay want outside circle a, and out of it by a hold?"""
        return rect_nm(box, a["x"], a["z"]) - a["r"] >= max(want, DEPLOY_HOLD_NM)

    def open_box(group, afloat, types):
        """The padded box, each side opened as far as the enemy, the goals,
        the live circles and - for a box a hull can be moved in (afloat) -
        the land allow. Returns the box and the type words the box must not
        admit: the kinds a live circle counts that the group has none of,
        where the box reaches within that kind's need of the circle."""
        xs, zs = [h[2] for h in group], [h[3] for h in group]
        extent = [min(xs), max(xs), min(zs), max(zs)]
        box = [extent[0] - DEPLOY_PAD_NM, extent[1] + DEPLOY_PAD_NM,
               extent[2] - DEPLOY_PAD_NM, extent[3] + DEPLOY_PAD_NM]
        box = cut_out(box, extent)
        # For each live circle and each kind it counts that the group has,
        # the box keeps the need: its sides that face the circle are pulled
        # in to the group's units OF THAT KIND, with a shrinking pad. A
        # helicopter 7 NM nearer the circle than the ships it rides with
        # (Borrowed Shield) must not hold the ships' box open that far; a
        # unit a pull leaves outside gets its own box.
        own_types = {h[4] for h in group}
        limits = []
        for a in live:
            for kind in sorted(counted_types(a) & own_types):   # pulls compound: fixed order
                want = need(a, kind)
                limits.append((a["x"], a["z"], a["r"] + want))
                if keeps(box, a, want):
                    continue
                cx_ = [h[2] for h in group if h[4] == kind]
                cz_ = [h[3] for h in group if h[4] == kind]
                ext = [min(cx_), max(cx_), min(cz_), max(cz_)]
                for pad in DEPLOY_PULL_PADS:
                    box = pulled(box, ext, a, pad)
                    if keeps(box, a, want):
                        break
        base = tuple(box)
        in_play = [(x, z, rect_nm(base, x, z)) for _t, x, z, reach in red
                   if rect_nm(base, x, z) <= reach + DEPLOY_OPEN_NM]
        in_play += [(x, z, rect_nm(base, x, z)) for x, z in goals]
        # (index into box, outward sign, edge runs along x?)
        for i, sign, along_x in ((0, -1, False), (1, 1, False),
                                 (2, -1, True), (3, 1, True)):
            for _mile in range(int(DEPLOY_OPEN_NM)):
                trial = list(box)
                trial[i] += sign
                if any(rect_nm(trial, x, z) < d - DEPLOY_SLACK_NM for x, z, d in in_play):
                    break
                if any(rect_nm(trial, x, z) < DEPLOY_KEEP_OUT_NM for x, z in keep_out):
                    break
                # no nearer to a circle than its need, or than the box
                # already is where the start itself is nearer
                if any(rect_nm(trial, ax, az) < min(limit, rect_nm(box, ax, az))
                       for ax, az, limit in limits):
                    break
                if afloat:
                    lo, hi = (trial[0], trial[1]) if along_x else (trial[2], trial[3])
                    n = max(2, int((hi - lo) / 2.0) + 1)
                    edge = [lo + (hi - lo) * k / (n - 1) for k in range(n)]
                    if not all(water(v, trial[i]) if along_x else water(trial[i], v)
                               for v in edge):
                        break
                box = trial
        drop = set()
        for a in live:
            for kind in counted_types(a) - own_types:
                if rect_nm(box, a["x"], a["z"]) - a["r"] < need(a, kind):
                    drop.add(kind)
        return box, drop

    def split(group):
        """The pieces of a group whose box could not keep a live circle's
        need even pulled in to its units: two ships 14 NM from a circle on
        different bearings have a bounding box that passes 10 NM from it
        (Western Passage's convoy and the escorts round the circle it must
        reach). Such a group is halved along its wider axis, and the halves
        again, until each piece's tightest box keeps the need."""
        pieces, todo = [], [list(group)]
        while todo:
            g = todo.pop()
            halve = None
            for a in live:
                # sorted: a set's order follows string hashing, which Python
                # seeds afresh each run, and the first kind found decides the
                # axis - D8's detachment box came out one or two boxes from
                # one build to the next (20 Oct 2026).
                for kind in sorted(counted_types(a) & {h[4] for h in g}):
                    mem = [h for h in g if h[4] == kind]
                    if len(mem) < 2:
                        continue
                    ext = (min(h[2] for h in mem), max(h[2] for h in mem),
                           min(h[3] for h in mem), max(h[3] for h in mem))
                    tight = pulled([ext[0] - DEPLOY_PAD_NM, ext[1] + DEPLOY_PAD_NM,
                                    ext[2] - DEPLOY_PAD_NM, ext[3] + DEPLOY_PAD_NM],
                                   ext, a, DEPLOY_PULL_PADS[-1])
                    if not keeps(tight, a, need(a, kind)):
                        halve = 2 if ext[1] - ext[0] >= ext[3] - ext[2] else 3
                        break
                if halve:
                    break
            if halve:
                ranked = sorted(g, key=lambda h: h[halve])
                todo += [ranked[:len(ranked) // 2], ranked[len(ranked) // 2:]]
            else:
                pieces.append(g)
        return sorted((sorted(g, key=lambda u: order[u[0]]) for g in pieces),
                      key=lambda g: order[g[0][0]])

    def zone(group, types, label):
        kinds = set(types.split(","))
        (x0, x1, z0, z1), drop = open_box(group, afloat=bool(kinds & {"Vessel", "Submarine"}),
                                          types=types)
        types = ",".join(ty for ty in types.split(",") if ty not in drop)
        z = dict(label=label, types=types,
                 at=(round(centre[0] + (z0 + z1) / 120.0, 6),
                     round(centre[1] + (x0 + x1) / 120.0, 6)),
                 width=round(x1 - x0, 1), height=round(z1 - z0, 1))
        # the units the written box holds: one a circle pulled the box off
        # is boxed again on its own below
        z["tags"] = sorted(h[0] for h in group if zone_holds(z, centre, h[2], h[3], h[4]))
        return z

    out, main_tags = [], set()
    hulls = [u for u in units if u[4] in ("Vessel", "Submarine")]
    if hulls:
        groups = chain(hulls)
        anchor = mission.get("_anchor_section")
        first_ship = next((h[0] for h in hulls if h[4] == "Vessel"), hulls[0][0])
        lead = anchor if any(h[0] == anchor for h in hulls) else first_ship
        main = next(g for g in groups if any(h[0] == lead for h in g))
        pieces = split(main)
        main = next(g for g in pieces if any(h[0] == lead for h in g))
        main_tags = {h[0] for h in main}
        out.append(zone(main, DEPLOY_ALL if any(h[4] == "Vessel" for h in main)
                        else "Submarine", "Deployment Zone"))
        for group in pieces:
            if group is not main:
                types = ",".join(t for t in DEPLOY_ALL.split(",") if any(u[4] == t for u in group))
                out.append(zone(group, types, zone_label(types)))
    rest = [u for u in units if u[0] not in main_tags
            and not any(zone_holds(z, centre, u[2], u[3], u[4]) for z in out)]
    for group in chain(rest):
        for piece in split(group):
            types = ",".join(t for t in DEPLOY_ALL.split(",") if any(u[4] == t for u in piece))
            out.append(zone(piece, types, zone_label(types)))
    # A unit a box was pulled off (the helicopter beside the circle its
    # ships must keep clear of) is boxed on its own, until every unit is
    # held or a box cannot be made (check_deployment_cover says which).
    for _round in range(4):
        unheld = [u for u in units
                  if not any(zone_holds(z, centre, u[2], u[3], u[4]) for z in out)]
        if not unheld:
            break
        before = len(out)
        for group in chain(unheld):
            for piece in split(group):
                types = ",".join(t for t in DEPLOY_ALL.split(",") if any(u[4] == t for u in piece))
                out.append(zone(piece, types, zone_label(types)))
        if len(out) == before:
            break
    counts = collections.Counter(z["label"] for z in out)
    seen = collections.Counter()
    for z in out:
        base = z["label"]
        if counts[base] > 1:
            seen[base] += 1
            z["label"] = f"{base} {seen[base]}"
    return out


def check_deployment_cover(mission, placed, zones):
    """The build stops if any player unit a box should hold is outside every
    zone that admits its type. Read from the zone dicts as the file will
    carry them, not from the grouping that made them."""
    centre = mission["centre"]
    parked = mission.get("_parked", {})
    boxed = mission.get("_holders")          # a generated mission boxes these only
    out = [f"{keys['Type']} at {tag} ({ty}, {x:.1f},{z:.1f} NM)"
           for tag, keys, x, z, ty in deploy_units(placed)
           if tag not in parked and (boxed is None or tag in boxed)
           and not any(zone_holds(z_, centre, x, z, ty) for z_ in zones)]
    if out:
        raise SystemExit(f"{mission['key']}: outside every Deployment zone that "
                         "admits it - the player could not move it: " + "; ".join(out))
    # A generated mission's boxes hold the anchor and the air-tasking slots
    # and nothing else of the player's (deployment_zones, the stock pattern).
    holders = mission.get("_holders")
    if holders is not None:
        inside = []
        for entries in placed.values():
            for tag, keys, _n, _x in entries:
                xz = unit_spot(keys)
                if not tag.startswith("Taskforce1") or tag in holders or not xz:
                    continue
                for i, z_ in enumerate(zones, 1):
                    x0, x1, z0, z1 = zone_box(z_, centre)
                    if x0 <= xz[0] <= x1 and z0 <= xz[1] <= z1:
                        inside.append(f"{keys['Type']} at {tag} in Zone{i} ({z_['label']})")
        if inside:
            raise SystemExit(f"{mission['key']}: a generated mission's box holds a unit the mission "
                             "supplies - the game may take it for a slot of the player's force and "
                             "leave it out: " + "; ".join(inside))


def check_zone_areas(mission, placed, zones, text):
    """The build stops if a Deployment zone that admits a kind of unit a
    live circle counts reaches nearer the circle than that kind's need:
    DEPLOY_CLEAR_NM, or the start of the nearest unit of the kind the circle
    counts (less DEPLOY_START_ALLOW_NM) where that is nearer, never inside. Read
    back from the triggers and zones the file carries, not from the spec,
    so a circle deployment_areas() does not know cannot ship. A circle is
    live while fewer of the units it counts start inside it than it needs;
    one its counted units all start inside (a service window) is skipped.
    The game lets a unit be placed in any box that admits its type, so what
    a box holds at the start does not matter: only how near it reaches."""
    centre = mission["centre"]
    parked = mission.get("_parked", {})
    spots, family = {}, {}
    for entries in placed.values():
        for tag, keys, _n, _x in entries:
            m = re.match(r"Taskforce1(Vessel|Submarine|Aircraft|Helicopter|LandUnit)\d+$", tag)
            if m and unit_spot(keys):
                spots[tag], family[tag] = unit_spot(keys), DEPLOY_TYPE[m.group(1)]
    # one circle, whichever conditions and triggers name it (the per-unit
    # chain writes one "Objective met by" trigger per unit on one circle):
    # the units any of them counts
    circles = {}
    for block in re.findall(r"^\[Trigger\d+\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.S | re.M):
        name = re.search(r"^Name=(.*)$", block, re.M)
        for n in re.findall(r"^Condition_Condition(\d)_Type=UnitsInTheArea", block, re.M):
            pos = re.search(rf"^Condition_Condition{n}_PositionNM=([-\d.]+),[-\d.]+,([-\d.]+)", block, re.M)
            rad = re.search(rf"^Condition_Condition{n}_AreaRadiusNM=([\d.]+)", block, re.M)
            units = re.search(rf"^Condition_Condition{n}_Units=(.*)$", block, re.M)
            if not (pos and rad and units):
                continue
            tags = [u.strip() for u in units.group(1).split(",") if u.strip() in family]
            # A generated mission boxes only the anchor and the slots: a
            # circle that counts none of them cannot be reached from a box.
            if mission.get("_holders") is not None:
                tags = [u for u in tags if u in mission["_holders"]]
            if not tags:
                continue
            key = (float(pos.group(1)), float(pos.group(2)), float(rad.group(1)))
            circles.setdefault(key, [set(), []])[0].update(tags)
            if name and name.group(1) not in circles[key][1]:
                circles[key][1].append(name.group(1))
    problems = []
    for (ax, az, r), (tags, names) in circles.items():
        clear = {u: math.hypot(spots[u][0] - ax, spots[u][1] - az) - r for u in tags}
        if all(c < 0 for c in clear.values()):
            continue                    # complete, or a dwell, as the clock starts
        for kind in sorted({family[u] for u in tags}):
            own = [clear[u] for u in tags if family[u] == kind and u not in parked and clear[u] >= 0]
            allowed = min(DEPLOY_CLEAR_NM, max(0.0, min(own) - DEPLOY_START_ALLOW_NM) if own
                          else DEPLOY_CLEAR_NM)
            for i, zone in enumerate(zones, 1):
                if kind not in zone["types"].split(","):
                    continue
                have = rect_nm(zone_box(zone, centre), ax, az) - r
                # 0.1: the written box is rounded to 0.1 NM a side
                if have < max(allowed - DEPLOY_HOLD_NM, -DEPLOY_HOLD_NM):
                    problems.append(f"Zone{i} ({zone['label']}) admits {kind} and comes "
                                    f"{have:.1f} NM from the {r:g} NM circle of "
                                    f"'{', '.join(names)}' at {ax:.1f},{az:.1f} NM "
                                    f"- it must keep {allowed:.1f}")
    if problems:
        raise SystemExit(f"{mission['key']}: a player could be placed into an objective before "
                         "the clock starts - " + "; ".join(problems))


def zones_ini(zones):
    """The [Zones] block, in the stock campaign's own key order (06 Raid on
    Lombok, Zone1)."""
    L = ["[Zones]", f"NumberOfZones={len(zones)}"]
    L += [f"Zone{i}=Zone{i}" for i in range(1, len(zones) + 1)]
    for i, z in enumerate(zones, 1):
        L += [f"[Zone{i}]", "Type=Deployment", "Shape=Rectangle",
              f"LabelKey=Zone{i}Label", "Side=Blue", "Color=Blue",
              f"GeoPoint={z['at'][0]},{z['at'][1]}",
              f"WidthNm={z['width']:g}", f"HeightNm={z['height']:g}", "Bearing=0",
              "BorderColor=Blue", "BorderWidth=1.5", "FillOpacity=0.16",
              "BorderOpacity=0.5", "FillStyle=Fill",
              f"AllowedUnitTypes={z['types']}",
              "VisibleIn=CampaignMap,BriefingMap", "LockPosition=False"]
    return L


def deployment_panel(mission, placed):
    """Whether campaign.ini turns the deployment panel on for this mission
    (TaskForceModeDeploymentOptions=True): wherever the owned force sails,
    and for a detachment. Blank generation sails nothing of the player's."""
    if not mission.get("generation"):
        return False
    sails = not mission.get("detached") and bool(placed.get("Taskforce1Vessel"))
    return bool(sails or mission.get("window", {}).get("detachment"))


# The families a deployment-panel mission flags when the mission supplies them.
SUPPLIED_FAMILIES = ("Taskforce1Vessel", "Taskforce1Submarine", "Taskforce1Aircraft", "Taskforce1Helicopter")


def mark_supplied(mission, placed):
    """Flag every unit the mission supplies to the player TaskForceModeIgnoreUnit.

    With the deployment panel on, the game seats the player's own force and
    drops the other Taskforce1 units it does not recognise: the 13 Oct build
    turned the panel on wherever the force sails, and the escorted convoys and
    the authored recon aircraft stopped appearing (Southern Departure's three
    merchantmen, its P-8 and Triton). Stock shows the rule. In the five
    pacific-strike missions with the panel, every Taskforce1 ship and aircraft
    is the anchor, a numbered Replaced slot, an air-tasking slot, or carries
    TaskForceModeIgnoreUnit=True. 09 Shadows off Palawan supplies a Charleston,
    a Newport and two LSMs, and flags all four. The missions without the panel
    (01, 02, 04) supply a sealift ship, an E-3A, P-3Cs and F-15Cs unflagged.
    Explicitly retain supplied submarines too: SW09's Collins was reported
    absent in the deployed build, and had no retention flag beside the panel.
    Land units remain the stock pattern. A granted unit
    (JoinTaskForce) joins the force and is never ignored."""
    if not deployment_panel(mission, placed):
        return []
    marked = []
    for family in SUPPLIED_FAMILIES:
        for tag, keys, _n, _x in placed.get(family, []):
            if any(k in keys for k in ("TaskForceModeAnchor", "TaskForceModeReplacedUnitIndex",
                                       "TaskForceModeAirTaskingSlot", "JoinTaskForce")):
                continue
            keys["TaskForceModeIgnoreUnit"] = "True"
            marked.append(tag)
    return marked


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
    prep_decks = [tag for family in ("Taskforce1Vessel", "Taskforce1LandUnit")
                  for tag, keys, _name, _x in placed.get(family, [])
                  if keys.get("Disabled") != "True" and deck_size(keys["Type"]) > 0]
    prepare = mission.get("initial_deck_prep") and bool(prep_decks)
    if prepare:
        L.append("FlightDeckPrepMessage=AIRCRAFT AND UNIT PREPARATION|"
                 "Choose Start preparation to close this message. Keep the simulation paused; "
                 "select your ships and ground teams on the map or in Formation Manager. "
                 "Open each Flight Deck window and assign aircraft and loadouts. "
                 "Set weapon status and individual sensor switches using the normal unit controls. "
                 "When flight-deck timings are enabled, the native preparation phase finishes "
                 "queued aircraft preparation at the first unpause. Review air-defence orders "
                 "before unpausing; the operation clock and enemy action then begin.|Start preparation")
    L.append("Taskforce1VictoryMessage=<color=lime>Operation complete.</color>|"
             f"{ini_text(mission['win'])}")
    if mission.get("victory", {}).get("or_destroyed"):
        L.append("SunkVictoryMessage=<color=lime>Operation complete.</color>|"
                 + ini_text(mission["victory"]["or_destroyed"]))
    L.append("Taskforce1DefeatMessage=<color=red>Operation failed.</color>|"
             f"{ini_text(mission['lose'])}")
    L.append("Taskforce2VictoryMessage=<color=lime>Opposing force prevailed.</color>|"
             f"{ini_text(mission['lose'])}")
    L.append("Taskforce2DefeatMessage=<color=red>Opposing force defeated.</color>|"
             f"{ini_text(mission['win'])}")
    L.append("TimeoutMessage=<color=red>Operational window closed.</color>|"
             f"{ini_text(clock_text(mission, mission['timeout']))}")
    L.append("BehindScheduleMessage=<color=yellow>Behind schedule.</color>|"
             f"The planned {mission['minutes']}-minute window has closed. Command "
             f"will hold the line for about {deadline_minutes(mission) - mission['minutes']}"
             " minutes more. Finish the task now.")
    # Authorised range targets are exempt: a gunnery serial's own target is not
    # a civilian casualty.
    neutral_tags = [tag for family in placed if family.startswith("Neutral")
                    for tag, _k, _n, exempt in placed[family] if not exempt]
    for oid, reward in mission.get("reveals", {}).items():
        L.append(f"{oid}Intel={ini_text(reward['intel'])}")
    for i, loss in enumerate(mission.get("support_loss", []), 1):
        L.append(f"SupportLoss{i}Intel={ini_text(loss['intel'])}")
    for i, report in enumerate(mission.get("reports", []), 1):
        L.append(f"SituationReport{i}Intel={ini_text(report['intel'])}")
    for i, cutoff in enumerate(mission.get("reinforcement_cutoffs", []), 1):
        L.append(f"ReinforcementCancelled{i}Intel={ini_text(cutoff['intel'])}")
    if mission.get("victory", {}).get("after", {}).get("intel"):
        L.append(f"StageIntel={ini_text(mission['victory']['after']['intel'])}")
    if mission.get("victory", {}).get("after", {}).get("lost"):
        L.append("StageLostMessage=<color=red>Operation failed.</color>|"
                 + ini_text(mission["victory"]["after"]["lost"]))
    if mission.get("victory", {}).get("after", {}).get("held"):
        title, text = mission["victory"]["after"]["held"]
        L.append(f"StageHeldMessage=<color=yellow>{title}</color>|{ini_text(text)}")
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
    for lift in mission.get("lift", []):
        L.append(f"{lift['objective']}LiftIntel={ini_text(lift['intel'])}")
    if neutral_tags:
        L.append("NeutralLossMessage=<color=orange>Neutral contact lost.</color>|"
                 "A protected contact has been destroyed. The operation has "
                 "failed. Preserve the contact and engagement records.")
    for family in FAMILY_ORDER:
        for tag, _keys, unit_name, _x in placed.get(family, []):
            if unit_name and tag != mission.get("_anchor_tag"):
                L.append(f"{tag}NameOverride={unit_name}")
    zones = mission["_zones"] = deployment_zones(mission, placed, members)
    check_deployment_cover(mission, placed, zones)
    for i, z in enumerate(zones, 1):
        L.append(f"Zone{i}Label_en={z['label']}")
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
    # A formation is one group in the game: half of it switched off would
    # leave the other half flying a formation with no one in it.
    joins = mission.get("_enter", {})
    for side, groups in forms.items():
        for label, group in groups:
            minutes = {joins.get(tag) for tag in group}
            if len(minutes) > 1:
                raise SystemExit(f"{mission['key']}: {label} is one formation "
                                 f"({', '.join(group)}) but its units join at "
                                 "different minutes - give them one enter=")
    for side, groups in sorted(forms.items()):
        L.append(f"{side}_NumberOfFormations={len(groups)}")
        for i, (label, group) in enumerate(groups, 1):
            shape = "Vic" if ("Aircraft" in group[0] or "Helicopter" in group[0]) else "Loose"
            spacing = "0.1" if shape == "Vic" else "1.5"
            # Coastal traffic must fit the passage as a formation as well as
            # along its leader's route. Weather Alternate's eastern channel
            # cannot safely take the default 1.5 NM spread.
            station = next((mission["stations"][st] for st, tags in members.items()
                            if group[0] in tags), {})
            if "formation_spacing" in station:
                value = float(station["formation_spacing"])
                if not math.isfinite(value) or value <= 0:
                    raise SystemExit(f"{mission['key']}: {label} has invalid formation spacing")
                spacing = f"{value:g}"
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

    # Condition_Time is SECONDS. The planned window closes at `minutes` with
    # a message and nothing else; the mission is lost at DEADLINE_FACTOR
    # times that. The clock running out fails the main task and leaves the
    # survival objectives to their own end-status: a carrier that survived
    # the window survived it, whether or not the transports made the box.
    # Cancelling them was telling the player the file contradicts its own
    # rule.
    deadline = deadline_minutes(mission) * 60
    survivals = [oid for oid, how in mission.get("resolve", {}).items()
                 if isinstance(how, tuple) and how[0] in ("protect", "survive")]
    terminal("Deadline",
             ["Condition_Type=Time", f"Condition_Time={deadline}"],
             failed=[main], message="TimeoutMessage", victor="Taskforce2",
             keep=survivals)
    trigger("Window closed", [
        "Condition_Type=Time", f"Condition_Time={mission['minutes'] * 60}",
        "Action_Taskforce1_Message=BehindScheduleMessage"])
    trigger("Start message", [
        "Condition_Type=Time", "Condition_Time=1",
        "Action_Taskforce1_Message=Taskforce1StartMessage"])
    for i, report in enumerate(mission.get("reports", []), 1):
        trigger(f"Situation report {i}", ["Condition_Type=Time",
                f"Condition_Time={round(report['minute'] * 60)}",
                f"Action_Taskforce1_Intel=SituationReport{i}Intel"])
    # Native OnMissionStart preparation queues the player's actual decks,
    # including generated hulls. The first prompt must be dismissed before
    # selecting another unit. A Time=1 trigger would merely complete existing
    # jobs and would not register the initial preparation phase.
    if prepare:
        trigger("Allow initial flight deck prep", [
            "Condition_Condition1_Type=OnMissionStart",
            "ConditionsCompleted=<Condition1>",
            "Action_PrepareFlightDeck=True",
            "Action_Taskforce1_Message=FlightDeckPrepMessage"])
    # disable=: systems off from the first second, one trigger per set of
    # systems - 08 Defense of North Borneo Trigger4, key for key.
    groups = collections.defaultdict(list)
    for tag, systems in mission.get("_disabled", []):
        groups[systems].append(tag)
    for systems, tags in groups.items():
        trigger("Systems disabled at start", [
            "Condition_Condition1_Type=OnMissionStart",
            "ConditionsCompleted=<Condition1>",
            f"Action_Units={','.join(tags)}"]
            + [f"Action_EnableDisable{DISABLE_ACTIONS[s]}=Disable" for s in systems])
    # enter=: a held-back unit joins at its minute - 01A Senkaku Run Trigger4,
    # key for key.
    joining = collections.defaultdict(list)
    for tag, minute in mission.get("_enter", {}).items():
        joining[minute].append(tag)
    join_triggers = {}
    for minute, tags in sorted(joining.items()):
        trigger(f"Joins at minute {minute:g}", [
            "Condition_Condition1_Type=Time",
            f"Condition_Condition1_Time={round(minute * 60)}",
            "ConditionsCompleted=<Condition1>",
            "Action_SetEnabledStatus=True",
            f"Action_Units={','.join(tags)}"])
        join_triggers[minute] = len(T)

    # Broken Wake's relay must be stopped before it releases a follow-on
    # attack. Stock supports AND NOT time and disabling a trigger. A shared
    # timed join cannot be cancelled if it would also remove unrelated units.
    for i, cutoff in enumerate(mission.get("reinforcement_cutoffs", []), 1):
        minute = cutoff["minute"]
        sources = [t for r in cutoff["source"] for t in refs(members, r)]
        targets = [t for r in cutoff["reinforcements"] for t in refs(members, r)]
        if (minute <= 0 or not sources or not targets or
                any(not t.startswith("Taskforce2") for t in sources + targets) or
                set(targets) != set(joining.get(minute, []))):
            raise SystemExit(f"{mission['key']}: reinforcement cutoff must name an entire opposing join at its exact minute")
        trigger(f"Reinforcements cancelled before minute {minute:g}",
                destroyed_condition(1, sources, len(sources)) + [
                    "Condition_Condition2_Type=Time",
                    f"Condition_Condition2_Time={round(minute * 60)}",
                    "ConditionsCompleted=<Condition1> AND NOT <Condition2>",
                    f"Action_DisableTriggers=Trigger{join_triggers[minute]}",
                    f"Action_Taskforce1_Intel=ReinforcementCancelled{i}Intel"])

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
                 + ",".join([main] + [o for o in held if o != main]
                            + victory.get("bonus", []))]
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
            # hold_minutes: the stage is not done on arrival but after the
            # units have been there that long - SW03's lifters loading thirty
            # people. A Time condition counts from when its trigger is
            # enabled, which is what 04 Chagos Gambit's rain loop (Trigger3
            # and Trigger4, each Time= and each re-enabling the other) only
            # works by; so the arrival enables a held trigger whose clock
            # starts then, and that trigger shows the pop-up and arms the
            # win. Its area test is the arrival's again.
            hold = stage.get("hold_minutes")
            # Trigger numbers, in the order they are written: the stage, the
            # held trigger, then the arrival that wins.
            stage_no = len(T) + 1
            held_no = stage_no + 1 if hold else None
            met_no = (held_no or stage_no) + 1
            s_cond = stage_conditions(s_units)
            # or_destroyed: the arrival's units destroyed after the stage is a
            # win too, written right after the arrival's trigger and armed by
            # the stage - SW04's craft, sunk once classified because she
            # would not stop (play test, 18 Oct 2026).
            sunk = f",Trigger{met_no + 1}" if victory.get("or_destroyed") else ""
            s_cond.append(f"Action_EnableTriggers=Trigger{held_no or met_no}{sunk}")
            trigger("Stage", s_cond)
            if hold:
                if stage["kind"] != "area" or not stage.get("held") or stage.get("lost"):
                    raise SystemExit(f"{mission['key']}: hold_minutes needs an "
                                     "area stage and a `held` message, and no "
                                     "`lost` (make the units fatal instead)")
                h_cond = area_condition(1, centre, s_at, stage.get("radius", 3),
                                        s_units, stage.get("min_units", 1))
                trigger("Stage held", ["Disabled=True"] + h_cond + [
                    "Condition_Condition2_Type=Time",
                    f"Condition_Condition2_Time={round(hold * 60)}",
                    "ConditionsCompleted=<Condition1> AND <Condition2>",
                    "Action_Taskforce1_Message=StageHeldMessage",
                    f"Action_EnableTriggers=Trigger{met_no}"])
            cond.insert(0, "Disabled=True")
    if not per_unit:
        trigger("Objective met", cond + win_lines)
    if victory.get("or_destroyed"):
        if not stage or per_unit or hold:
            raise SystemExit(f"{mission['key']}: or_destroyed needs a victory "
                             "stage (not per_unit, not held) to arm it")
        trigger("Objective met by sinking",
                ["Disabled=True"] + destroyed_condition(1, win_units, 1)
                + ["ConditionsCompleted=<Condition1>",
                   "Action_Taskforce1_Message=SunkVictoryMessage",
                   # the bonus (taken intact) is the arrival's alone
                   "Action_ObjectivesCompleted="
                   + ",".join([main] + [o for o in held if o != main])]
                + [l for l in win_lines if not l.startswith(
                    ("ConditionsCompleted=", "Action_Taskforce1_Message=",
                     "Action_ObjectivesCompleted="))])

    # Every objective needs a predicate. "victory" is completed by the trigger
    # above; everything else gets its own, and an objective with no resolver
    # fails the build - twenty of them used to sit there resolving to nothing.
    resolve = mission["resolve"]

    def own_units(what, station_refs):
        """The player's units at these stations, for a predicate on what the
        enemy knows about them. A red or neutral unit here is an authoring
        mistake the engine would accept and never fire on. So is anything
        that is not a station ref: `("unseen", "boats", 2)` reads like
        protect's count and would be dropped without a word."""
        odd = [r for r in station_refs if not isinstance(r, str)]
        if odd:
            raise SystemExit(
                f"{mission['key']}: {what} names stations, and {odd!r} is not "
                "one - the objective fails on the first unit classified; a "
                "fatal entry's minimum= is its count")
        units = [t for r in station_refs for t in refs(members, r)]
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
            wanted = [how[1]] if isinstance(how[1], str) else how[1]
            units = [tag for ref in wanted for tag in refs(members, ref)]
            if not units or not 1 <= how[2] <= len(units):
                raise SystemExit(f"{mission['key']}: objective {oid} has an impossible destroyed-unit count")
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
            # MinimumUnits=0 is met at spawn and ends the mission on its first
            # tick; one above the count is never met. A loss's minimum falls
            # back to "all of them" on 0; nothing sensible does here.
            if (not isinstance(least, int) or isinstance(least, bool)
                    or not 1 <= least <= len(watched)):
                raise SystemExit(
                    f"{mission['key']}: the fatal entry on {oid} ends the "
                    f"mission when {least!r} of {watched} are classified - "
                    "minimum= runs from 1 to the number it watches")
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

    # lift=: a restraint that stops binding when the other side shows hostile
    # intent. TS11A's frigate reaching her firing position is the fire-control
    # lock; from then, defending the corvette - the frigate or her helicopter
    # included - no longer breaks Restraint. The area test is stock
    # UnitsInTheArea with the circle not shown (AreaDisplaySide=None, 22
    # native uses); the switch-off is Action_DisableTriggers with a comma
    # list (Caron at Grenada 1983 and seven more).
    for lift in mission.get("lift", []):
        oid = lift["objective"]
        how = mission.get("resolve", {}).get(oid)
        if not (isinstance(how, tuple) and how[0] == "spare"):
            raise SystemExit(f"{mission['key']}: lift names {oid!r}, which is not a "
                             "spare objective; only a restraint can be lifted")
        units = [tag for r in lift["units"] for tag in refs(members, r)]
        if not units or any(not u.startswith("Taskforce2") for u in units):
            raise SystemExit(f"{mission['key']}: lift on {oid} must watch opposing "
                             "units - it is their move that lifts the restraint")
        numbers = [i for i, (comment, _l) in enumerate(T, 1)
                   if comment in (f"{oid} broken", f"{oid} lost - mission over")]
        if not numbers:
            raise SystemExit(f"{mission['key']}: lift on {oid} has no trigger to "
                             "switch off")
        at, radius = lift["at"], lift["radius"]
        # A circle nothing it watches ever reaches is a restraint that never
        # lifts, and a mission that says it will.
        sections = {tag: keys for entries in placed.values()
                    for tag, keys, _n, _x in entries}
        cx, cz = (at[1] - centre[1]) * 60, (at[0] - centre[0]) * 60
        reached = False
        for u in units:
            keys = sections[u]
            spots = [keys["RelativePositionInNM"]] + [
                w.split("/")[0] for w in keys.get("Waypoints", "").split("|") if w]
            for s in spots:
                bits = s.split(",")
                try:
                    x, z = float(bits[0]), float(bits[2])
                except (ValueError, IndexError):
                    continue
                reached |= math.hypot(x - cx, z - cz) <= radius
        if not reached:
            raise SystemExit(f"{mission['key']}: lift on {oid}: no spawn or "
                             "waypoint of the watched units is inside the circle, "
                             "so the restraint would never lift")
        trigger(f"{oid} lifted",
                area_condition(1, centre, at, radius, units, 1, side="None")
                + ["ConditionsCompleted=<Condition1>",
                   f"Action_Taskforce1_Intel={oid}LiftIntel",
                   "Action_DisableTriggers=" + ",".join(f"Trigger{i}" for i in numbers)])

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
    # `level` is Identify or Classify, or "" for the bare reveal the stock
    # Sub Duel uses for its "Initial contact" - a detection, no class. `time`
    # is how long the reveal holds (seconds; -1 for the whole mission): the
    # stock initial contact holds 60 s, a datum rather than a gift.
    for reveal in mission.get("reveal_if", []):
        revealed = [t for r in reveal["units"] for t in refs(members, r)]
        level = reveal.get("level", "Identify")
        trigger(f"Reveal from {reveal['variable']}", [
            "Condition_Condition1_Type=VariableCheck",
            f"Condition_Condition1_Variable={reveal['variable']}",
            "ConditionsCompleted=<Condition1>",
            f"Action_Taskforce1_Intel={reveal['variable']}Intel",
            "Action_UnitRevealToTaskforce=Taskforce1" + (f"|{level}" if level else ""),
            f"Action_UnitRevealTime={reveal.get('time', -1)}",
            f"Action_Units={','.join(revealed)}"])

    # Units taken out at a mission time, with no score: the stock
    # Action_DespawnUnits (05A Operation Blockbuster's "Bomber cleanup").
    # SW02 parks a stand-in at the reported datum for the one-minute record
    # and removes it here once the reveal has run.
    for gone in mission.get("despawn_at", []):
        units = [t for r in gone["units"] for t in refs(members, r)]
        trigger(gone["name"], [
            "Condition_Condition1_Type=Time",
            f"Condition_Condition1_Time={int(gone['time'])}",
            "ConditionsCompleted=<Condition1>",
            "Action_DespawnUnits=True",
            f"Action_Units={','.join(units)}"])

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

    mark_supplied(mission, placed)
    for family in FAMILY_ORDER:
        for tag, keys, _n, _x in placed.get(family, []):
            L.append(block(tag, keys))
            L.append("")
    if zones:
        L += zones_ini(zones) + [""]

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
    check_zone_areas(mission, placed, zones, "\n".join(L))
    return name, "\n".join(L).rstrip() + "\n"


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


# --- recognition photos in the briefing ------------------------------------
# The briefing screen already shows images: BriefingMap_en.xml binds the map
# PNG in the mission's _briefing folder by its file stem
# (Source="{Binding Assets[<stem>]}"), and the stock Sub Duel briefing puts an
# <Image> inside BriefingText_en.xml the same way. So the real photographs in
# the SEST gallery (integration/gallery/source) can reach the game here, and
# only here: no unit file has an image key, and the encyclopedia is a 3D
# model viewer.
#
# Each mission lists the classes it places on the player's side and the enemy
# side, one photo per class, from the gallery's load-order-aligned catalogue.
# Only photos the gallery maps to the class itself or its family are used
# (not context or concept stand-ins, not the ones graded P1), and units that
# appear only on a condition (spawn_if) are left out so a carried-over choice
# is not given away. Neutral traffic is mostly stock hulls with no photo.
GALLERY = ROOT / "integration" / "gallery" / "source"
REC_STATUSES = {"exact", "family_reference", "family_or_component_reference",
                "upgrade_base_reference"}
REC_MAX = 8
REC_WIDTH = 400


@functools.lru_cache(maxsize=None)
def gallery_catalogue():
    """{unit id (lower case): (entry, asset)} for the copy the game loads."""
    js = GALLERY / "catalogue.js"
    if not js.is_file():
        return {}
    import json
    cat = json.loads(re.match(r"window\.CATALOGUE=(.*);\s*$",
                              js.read_text(encoding="utf-8"), re.S).group(1))
    assets = {a["asset_id"]: a for a in cat["assets"]}
    out, other = {}, {}
    for e in cat["entries"]:
        a = assets.get(e.get("asset_id") or "")
        if (not a or e.get("mapping_status") not in REC_STATUSES
                or (a.get("quality_review") or {}).get("priority") == "P1"):
            continue
        if e.get("is_winning_copy"):
            out[e["unit_id"].lower()] = (e, a)
        else:
            other.setdefault(e["unit_id"].lower(), (e, a))
    # A unit SEST now forks (a fix, a reload flag, a wing) is won by the
    # pack's own record, which the index carries without the photo the
    # original mod's record has - so 54 placed units, the P-8A in 35
    # missions among them, showed no picture (20 Oct 2026). The same id is
    # the same class: the photo from another record of it stands in.
    for uid, hit in other.items():
        out.setdefault(uid, hit)
    return out


# English names for creators the gallery records in another script: the
# game's font (and make_art's) has no CJK glyphs, so 海上自衛隊 would draw as
# boxes. PHOTO_CREDITS.txt keeps the original.
CREDIT_NAMES = {"hobart": "Japan Maritime Self-Defense Force",
                "type003": "China News Service"}


def photo_credit(asset):
    if asset.get("asset_id") in CREDIT_NAMES:
        return (f"Photo: {CREDIT_NAMES[asset['asset_id']]} · "
                f"{(asset.get('license') or '').strip()} · resized")
    # photos the SEST author supplied before writing their credit
    if asset.get("origin") == "sest_author_supplied" and asset.get("creator") == "Credit to be added":
        return "Photo supplied by the SEST author"
    who = re.sub(r"https?://\S+", "", asset.get("creator") or "")
    who = re.sub(r"[\u2e80-\u9fff\uac00-\ud7af\uff00-\uffef]+", "", who)   # no CJK glyphs in game
    who = re.sub(r"\s+", " ", who).strip(" ,;") or "see PHOTO_CREDITS.txt"
    if len(who) > 70:
        who = who[:67].rstrip() + "..."
    lic = (asset.get("license") or "").strip()
    return f"Photo: {who}" + (f" · {lic}" if lic and lic != "Not recorded" else "") + " · resized"


@functools.lru_cache(maxsize=None)
def profile_pictures():
    """{unit id (lower case): (entry, asset)} from the gallery's encyclopedia
    profile table (integration/gallery/profiles.tsv), for units the catalogue
    has no winning entry for: a photo two reviewers passed as the same type
    or the same family. The briefing takes the catalogue first and this
    second, so a unit whose profile picture is in the encyclopedia can be on
    its briefing too."""
    tsv = GALLERY.parent / "profiles.tsv"
    if not tsv.is_file():
        return {}
    assets = gallery_assets()
    out = {}
    for line in tsv.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 3 or cols[2] not in ("same_type", "same_family"):
            continue
        a = assets.get(cols[1])
        if not a or (a.get("quality_review") or {}).get("priority") == "P1":
            continue
        out[cols[0].lower()] = ({"unit_id": cols[0], "label": a["label"],
                                 "mapping_status": "exact" if cols[2] == "same_type"
                                 else "family_reference"}, a)
    return out


def recognition(mission):
    """[(stem, entry, asset)] for the briefing, the player's side first.

    Each side has half the slots, and a side that cannot fill its half
    leaves the rest to the other. Until 20 Oct 2026 the player's side took
    every slot it could, and once 54 more classes had photos (the P-8A, the
    Type 054A) it crowded the opposition out - Red Line 03 lost the RAAF
    F-35A it exists to recognise."""
    cat, prof = gallery_catalogue(), profile_pictures()
    sides, seen = {"blue": [], "red": []}, set()
    # Military classes before civilian traffic (civ_*) within a side: a
    # merchant on a side's roster is background the briefing can drop when
    # the slots run out; a warship or an aircraft is what it is for.
    units = sorted(mission["units"], key=lambda u: u["type"].lower().startswith("civ_"))
    for side in ("blue", "red"):
        for u in units:
            # recognise=False: a unit whose class is the puzzle (Red Line's
            # ALPHA and GOLF). A photo of her under "Expected opposition"
            # answered it before the first contact.
            if u["side"] != side or u.get("spawn_if") or u.get("recognise") is False:
                continue
            hit = cat.get(u["type"].lower()) or prof.get(u["type"].lower())
            if not hit or hit[1]["asset_id"] in seen:
                continue
            seen.add(hit[1]["asset_id"])
            sides[side].append((f"sest_rec_{hit[1]['asset_id']}", hit[0], hit[1], side))
    blue = sides["blue"][:max(REC_MAX // 2, REC_MAX - len(sides["red"]))]
    return blue + sides["red"][:REC_MAX - len(blue)]


@functools.lru_cache(maxsize=None)
def recognition_png(asset_file):
    """The gallery photo scaled to the briefing column, as PNG bytes."""
    import io
    from PIL import Image
    im = Image.open(GALLERY / asset_file).convert("RGB")
    h = round(im.height * REC_WIDTH / im.width)
    im = im.resize((REC_WIDTH, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


# The briefing's banner: one photograph across the top of the briefing text,
# with the mission's theatre, date, side and time window under it. Until
# 6 Oct 2026 every mission of a campaign carried the campaign's cover photo;
# the player asked for a different photo on each briefing. So each campaign
# mission now takes, in calendar order, the first photo of its own forces
# (then of the opposition) that no earlier mission of the campaign has used,
# then one from the campaign's own pool below, and only when both are spent
# the photo used least so far (plan_banners). A Dispatch, whose side and
# year change from one to the next, takes the first photo of its own forces.
# The strip is cropped to the busiest part of the photo rather than its
# centre (banner_png), so a hull or an airframe is not cut in half by a
# fixed centre crop.
CAMPAIGN_BANNER = {"sest-southern-watch": "hobart", "sest-southern-reach": "canberra",
                   "sest-red-line": "type054a", "sest-sulu-line": "tarlac"}
# Photos of each campaign's own forces and theatre to draw on once the units
# a mission places have all been used on an earlier briefing. Every id must
# be in the gallery; the build stops on one that is not.
BANNER_POOL = {
    "sest-southern-watch": ["hobart", "anzac", "supply_au", "choules", "collins", "e7_raaf",
                            "f35a_raaf", "p8a", "mq4c", "canberra", "arleigh_burke"],
    "sest-southern-reach": ["canberra", "hobart", "anzac", "collins", "supply_au", "choules",
                            "p8a", "mh60r", "e7_raaf", "akula", "type054a", "type056a"],
    "sest-red-line": ["type054a", "type003", "type056a", "sovremenny", "type051", "type901",
                      "kj500", "jh7a"],
    "sest-sulu-line": ["miguel_malvar", "tarlac", "jacinto", "naresuan", "chakri", "rizal_old",
                       "type056a", "type054a", "type052c", "kj500", "jh7a"],
}
# Photos that are fine at encyclopedia size but not as a strip across the
# top of a briefing: a hull behind a roof, a helicopter in a museum hall.
BANNER_SKIP = {"choules", "lynx"}
BANNER_PLAN = {}      # mission key -> asset id, for the campaign set_campaign() chose
# The campaign screen's backdrop, where it should not repeat the banner: the
# Steam page shows both side by side (the banner photo large, the campaign
# map beside it), so Southern Watch's map carries its MH-60R and Red Line's
# the Fujian its commander sails with. Others fall back to the banner photo.
CAMPAIGN_BACKDROP = {"sest-southern-watch": "mh60r", "sest-red-line": "type003"}
BANNER_SIZE = (900, 320)
SERVICE = {"Australia": "Royal Australian Navy", "China": "People's Liberation Army Navy",
           "Philippines": "Philippine Navy"}


@functools.lru_cache(maxsize=None)
def gallery_assets():
    js = GALLERY / "catalogue.js"
    if not js.is_file():
        return {}
    import json
    cat = json.loads(re.match(r"window\.CATALOGUE=(.*);\s*$",
                              js.read_text(encoding="utf-8"), re.S).group(1))
    return {a["asset_id"]: a for a in cat["assets"]}


# The line under each briefing banner: one quote per mission, chosen by the
# mission's role (campaign_data role=) from integration/common/quotes.py and
# different from every earlier mission's in the campaign while the set lasts.
# Planned beside the banners so a rebuild on any machine sets the same line.
EPIGRAPH_PLAN = {}    # mission key -> quote


def plan_banners(missions):
    """Fill BANNER_PLAN for this campaign: one photo per scheduled mission,
    different from every earlier mission's where the gallery allows it. The
    epigraphs (EPIGRAPH_PLAN) are planned here too, by the same rule."""
    EPIGRAPH_PLAN.clear()
    for m, q in zip(missions, quotes.plan_epigraphs([m.get("role", "escort") for m in missions])):
        EPIGRAPH_PLAN[m["key"]] = q
    BANNER_PLAN.clear()
    assets = gallery_assets()
    if not assets:
        return
    slug = SLUG.removesuffix("-open")
    pool = BANNER_POOL.get(slug, [])
    bad = [a for a in pool if a not in assets]
    if bad:
        raise SystemExit(f"{slug}: BANNER_POOL names photos the gallery has not got: {bad}")
    used = collections.Counter()

    def rank(entry, asset, side):
        """Lower is better: the player's warships, then its aircraft, the
        opposition's warships and aircraft, the pool, and civil hulls and
        land units only when nothing else is left."""
        civil = (entry["unit_id"].startswith("civ_") or "civilian" in asset.get("label", "").lower()
                 or asset["asset_id"] in ("narcosub",))
        if asset.get("category") not in ("Ships", "Submarines", "Aircraft & helicopters"):
            return 7
        if civil:
            return 6
        flying = asset.get("category") == "Aircraft & helicopters"
        return {("blue", False): 0, ("blue", True): 1, ("red", False): 2, ("red", True): 3}[(side, flying)]

    order = sorted((m for m in missions if m.get("group") != "dispatch"),
                   key=lambda m: m["date"])
    owned = [[(rank(e, a, s), i, a["asset_id"]) for i, (_st, e, a, s) in enumerate(recognition(m))
              if a["asset_id"] not in BANNER_SKIP]
             for m in order]
    for k, m in enumerate(order):
        cands = list(owned[k])
        seen = {c[2] for c in cands}
        # A pool photo a later mission owns is kept for that mission: the
        # later a photo is next wanted, the sooner the pool may spend it.
        later = {}
        for j in range(k + 1, len(order)):
            for c in owned[j]:
                later.setdefault(c[2], j)
        cands += [(4, len(cands) + later.get(a, 10 ** 6) * -1 + 10 ** 6, a)
                  for a in pool if a not in seen]
        good = [c for c in cands if c[0] <= 4]
        fresh = [c for c in good if c[2] not in used]
        if fresh:
            pick = min(fresh)[2]
        elif good:
            pick = min(good, key=lambda c: (used[c[2]], c[0], c[1]))[2]
        elif cands:
            pick = min(cands, key=lambda c: (used[c[2]], c[0], c[1]))[2]
        else:
            pick = CAMPAIGN_BANNER.get(slug)
        if pick:
            used[pick] += 1
            BANNER_PLAN[m["key"]] = pick


def banner(mission):
    """(stem, asset) for the mission's banner photo, or None."""
    assets = gallery_assets()
    aid = None
    if mission.get("group") != "dispatch":
        aid = BANNER_PLAN.get(mission["key"]) or CAMPAIGN_BANNER.get(SLUG.removesuffix("-open"))
    if aid is None:
        own = [p for p in recognition(mission) if p[3] == "blue"]
        aid = own[0][2]["asset_id"] if own else None
    a = assets.get(aid or "")
    return (f"sest_banner_{aid}", a) if a else None


def _subject_box(im):
    """(x0, y0, x1, y1) of the photo's subject, or None. The frame is cut to
    eight colours; the largest clusters, taken until they cover 55% of the
    pixels, are the background (sky, sea, tarmac), the rest is the subject,
    with the speckle of sun on water removed by a small morphological
    opening. None when nothing solid stands out, which means a centre crop."""
    from PIL import Image, ImageFilter
    W, colors = 200, 8
    small = im.resize((W, max(8, round(im.height * W / im.width))), Image.BOX)
    w, h = small.size
    q = small.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    hist = q.histogram()[:colors]
    bg, acc = set(), 0
    for i in sorted(range(colors), key=lambda i: -hist[i]):
        bg.add(i)
        acc += hist[i]
        if acc >= 0.55 * w * h:
            break
    mask = q.point(lambda v: 0 if v in bg else 255, "L")
    mask = mask.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(7))
    px = mask.load()
    cols = [sum(1 for y in range(h) if px[x, y]) for x in range(w)]
    rows = [sum(1 for x in range(w) if px[x, y]) for y in range(h)]
    if sum(cols) < 0.015 * w * h:
        return None

    def span(prof):
        """The middle 94% of the mass: a stray fleck at the frame's edge does
        not drag the box."""
        total = sum(prof)
        lo, acc = 0, 0
        while lo < len(prof) and acc + prof[lo] < 0.03 * total:
            acc += prof[lo]; lo += 1
        hi, acc = len(prof) - 1, 0
        while hi > lo and acc + prof[hi] < 0.03 * total:
            acc += prof[hi]; hi -= 1
        return lo, hi + 1
    x0, x1 = span(cols)
    y0, y1 = span(rows)
    sx, sy = im.width / w, im.height / h
    return (x0 * sx, y0 * sy, x1 * sx, y1 * sy)


def _window(span, length, lo, hi):
    """Offset of a `length` window within [0, span] centred on the subject's
    [lo, hi) where that fits, else holding the subject's edge that would
    otherwise be cut, else centred."""
    if length >= span:
        return 0
    mid = (lo + hi) / 2.0
    at = mid - length / 2.0
    if hi - lo > length:            # subject larger than the strip: keep its centre
        at = mid - length / 2.0
    return int(max(0, min(span - length, round(at))))


@functools.lru_cache(maxsize=None)
def banner_png(asset_file):
    import io
    from PIL import Image
    im = Image.open(GALLERY / asset_file).convert("RGB")
    w, h = BANNER_SIZE
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * scale)), max(h, round(im.height * scale))), Image.LANCZOS)
    box = _subject_box(im)
    if box:
        x = _window(im.width, w, box[0], box[2])
        y = _window(im.height, h, box[1], box[3])
    else:
        x, y = (im.width - w) // 2, (im.height - h) // 2
    buf = io.BytesIO()
    im.crop((x, y, x + w, y + h)).save(buf, "PNG", optimize=True)
    return buf.getvalue()


def banner_xml(mission):
    b = banner(mission)
    facts = [("THEATRE", mission.get("place", "")),
             ("DATE", date_words(mission["date"]) + (
                 " · {:02d}{:02d} local".format(*mission["time"]) if mission.get("time") else "")),
             ("SIDE", SERVICE.get(mission.get("blue_nation"), mission.get("blue_nation", ""))),
             ("WINDOW", f"{mission['minutes']} min, closes at {deadline_minutes(mission)}")]
    row = "".join(f'<TextBlock FontSize="14" Margin="0,0,24,4" Text="{xml_escape(k + "  " + v)}"/>'
                  for k, v in facts if v)
    img = credit = ""
    if b:
        stem, asset = b
        img = (f'<Image Source="{{Binding Assets[{stem}]}}" Width="{BANNER_SIZE[0]}" '
               'HorizontalAlignment="Left"/>')
        credit = (f'<TextBlock FontSize="12" Opacity="0.7" TextWrapping="Wrap" '
                  f'Text="{xml_escape(asset["label"] + ". " + photo_credit(asset).replace(" · resized", " · cropped"))}"/>')
    return ('<Border BorderBrush="#3D8FC9" BorderThickness="0,0,0,2" Margin="0,0,0,12" Padding="0,0,0,8">'
            f'<StackPanel>{img}<WrapPanel Margin="0,8,0,0">{row}</WrapPanel>{credit}</StackPanel></Border>')


def epigraph_xml(mission):
    """The quotation under the banner, and who said it. The text is the
    campaign's one piece of borrowed voice, so the attribution is honest:
    a maxim is labelled a maxim (quotes.py), never dressed as a signal."""
    q = EPIGRAPH_PLAN.get(mission["key"])
    if not q:
        return ""
    return ('<StackPanel Margin="0,0,0,14">'
            f'<TextBlock FontSize="17" FontStyle="Italic" TextWrapping="Wrap" '
            f'Text="{xml_escape(chr(34) + q["text"] + chr(34))}"/>'
            f'<TextBlock FontSize="13" Opacity="0.7" Margin="0,4,0,0" TextWrapping="Wrap" '
            f'Text="{xml_escape("- " + quotes.attribution(q))}"/>'
            '</StackPanel>')


# Under the photo of a red class the orders protect (protected_classes).
PROTECTED_LABEL = "Protected - do not engage"
NOT_FIRST_LABEL = "Opposition - do not fire first"


def protected_classes(mission):
    """{red class: label} for the red classes the player must not fire on:
    every placed red unit of the type is named by a `spare` resolver. The
    briefing labels their photos so (20 Oct 2026); "Expected opposition" on
    a Poseidon the orders protect read as permission. A restraint that a
    `lift` ends reads "do not fire first", not "do not engage": TS11A's
    frigate and her Z-9 were first labelled protected, and the same
    mission's BLUEFIN 31 then clears the player to engage them once the
    frigate locks the corvette. A hull an unlifted restraint also names
    stays protected. A class with one spared hull among others, or with
    hulls under both rules, keeps the plain label - the photo cannot say
    which one."""
    by_station = collections.defaultdict(list)
    for u in mission["units"]:
        by_station[u["station"]].append(u)
    lifted = {lift["objective"] for lift in mission.get("lift", [])}
    rule = {}
    for oid, how in mission.get("resolve", {}).items():
        if isinstance(how, tuple) and how[0] == "spare":
            label = NOT_FIRST_LABEL if oid in lifted else PROTECTED_LABEL
            for ref in how[1:]:
                station, _, idx = ref.partition("#")
                group = by_station.get(station, [])
                for u in (group[int(idx) - 1:int(idx)] if idx else group):
                    if rule.get(id(u)) != PROTECTED_LABEL:
                        rule[id(u)] = label
    red = collections.defaultdict(list)
    for u in mission["units"]:
        if u["side"] == "red" and not u.get("spawn_if"):
            red[u["type"].lower()].append(rule.get(id(u)))
    return {uid: marks[0] for uid, marks in red.items()
            if marks[0] and len(set(marks)) == 1}


def recognition_xml(picked, protected=None):
    """The RECOGNITION section. A red class in `protected` (protected_classes,
    class -> label) carries its label there, not "Expected opposition"."""
    if not picked:
        return ""
    cells = []
    for stem, entry, asset, side in picked:
        note = "" if entry["mapping_status"] == "exact" else " (class photo)"
        # some units carry their file id as their name; the photo's subject reads better
        label = entry["label"]
        if "_" in label or label.lower() == entry["unit_id"].lower():
            label = asset["label"]
        # full-width brackets and commas have no glyph in the game's font
        for fw, ascii_ in ((" （", " ("), ("（", " ("), ("）", ")"), ("，", ", ")):
            label = label.replace(fw, ascii_)
        who = ("Your forces" if side == "blue" else
               (protected or {}).get(entry["unit_id"].lower(), "Expected opposition"))
        cells.append(
            '<StackPanel Width="420" Margin="0,0,16,16">'
            f'<Image Source="{{Binding Assets[{stem}]}}" Width="{REC_WIDTH}" HorizontalAlignment="Left"/>'
            f'<TextBlock FontSize="15" Margin="0,6,0,0" TextWrapping="Wrap" '
            f'Text="{xml_escape(label + note)}"/>'
            f'<TextBlock FontSize="12" TextWrapping="Wrap" Opacity="0.7" '
            f'Text="{xml_escape(who + ". " + photo_credit(asset))}"/>'
            '</StackPanel>')
    return ('<TextBlock FontSize="20" Margin="0,14,0,6" Text="RECOGNITION"/>'
            '<TextBlock FontSize="14" TextWrapping="Wrap" Margin="0,0,0,10" Opacity="0.8" '
            'Text="Real photographs of the classes in this operation. Full credits: '
            'Gallery\\PHOTO_CREDITS.txt in the SEST Integration Pack folder."/>'
            '<WrapPanel>' + "".join(cells) + '</WrapPanel>')


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

    parts.append(banner_xml(mission))
    parts.append(epigraph_xml(mission))
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
    section("TIME", f"The planned window is {mission['minutes']} minutes. At that "
                    "minute Command signals that you are behind schedule and holds "
                    f"the line for about {deadline_minutes(mission) - mission['minutes']} "
                    f"minutes more; the operation is closed at {deadline_minutes(mission)} "
                    "minutes and the main task will be recorded as failed.")
    if any(not u.get("no_neutral_penalty") for u in mission["units"]
           if u["side"] == "neutral"):
        section("RULES OF ENGAGEMENT",
                "All designated neutral contacts are protected. A protected "
                "neutral loss cancels the operation. Identify before you shoot.")
    parts.append(recognition_xml(recognition(mission), protected_classes(mission)))
    # Installation and provider details remain in REQUIRED-MODS.txt and the
    # coverage report; the operational briefing contains only the orders.
    return BRIEF_XML.format(body="".join(parts))


ROSTER_SECTION = {"Vessel": "AllowedVessels", "Submarine": "AllowedSubmarines",
                  "Aircraft": "AllowedAircraft", "Helicopter": "AllowedHelicopters",
                  "VTOL": "AllowedAircraft"}


# --- the enemy theatre roster: the Situation button -------------------------
# Since 0.8.3 a linear campaign may name a Taskforce2 roster file
# ([DynamicUnitGeneration] Taskforce2RosterFile=), and the Situation button at
# the bottom right of the campaign screen then shows the enemy theatre ORBAT
# and tracks it as units are encountered or destroyed. In the stock Pacific
# Strike the same file also feeds the dynamic unit generator, which rolls
# escorts and coastal forces from it; these campaigns generate nothing (every
# unit is authored and placed), so the file here is the ORBAT alone - every
# enemy unit the campaign's missions place, in the stock file's own sections.
# The split follows the stock comments: flagships are the big hulls with a
# flight deck (9,000 t and up: the carriers, the Type 071 and 055, a Kirov,
# a Slava; an armed merchant stays a persistent unit), persistent units carry
# exactly the variants the missions use, reusable units the Default, aircraft
# their squadron and the largest flight a mission flies. A hull with no weapon
# system - the merchants and fishing boats a mission places on the enemy side
# as traffic or as a decoy's cover - is not order of battle and is left out.
# Each unit files under the nation its own variant or squadron registers it to
# (pick_nation), the mission's enemy nation only when it registers none, so
# Red Line's coalition sorts into RAN, USN, JMSDF and RNZN rather than one
# label. Nothing is hidden: what intelligence knows is in theatre is what the
# player sees.
ROSTER_NATION = {"china": "PLAN", "russia": "Russia", "ussr": "Russia", "soviet": "Russia", "iran": "Iran",
                 "meridian": "Meridian Maritime Group",
                 "australia": "RAN", "newzealand": "RNZN", "new zealand": "RNZN",
                 "usa": "USN", "us": "USN", "united states": "USN", "japan": "JMSDF",
                 "korea": "ROKN", "south korea": "ROKN", "france": "France",
                 "panama": "Panama", "philippines": "Philippine Navy",
                 "thailand": "Royal Thai Navy",
                 # The narco-submarine mod (3413868677) registers Nation=pirates in
                 # lower case; the Situation window shows the label raw, and the
                 # 16 Oct 2026 test read a "pirates" tab. Vanilla's own key is Pirates.
                 "pirates": "Pirates"}
FLAGSHIP_TONS = 9000
ROSTER_ORDER = ("SurfaceMajorFlagships", "SurfacePersistent", "SurfaceReusable",
                "SubmarinesPersistent", "AircraftReusable", "HelicoptersReusable")


def displacement(uid):
    """Displacement= of the winning hull file, tons; 0 when it declares none."""
    kind, f = unit_file(uid)
    if f is None:
        return 0
    m = re.search(r"^\s*Displacement=(\d+)", read(f), re.M)
    return int(m.group(1)) if m else 0


def armed(uid):
    """Does the winning unit file mount any weapon system at all?"""
    kind, f = unit_file(uid)
    return bool(f) and bool(re.search(r"^\[WeaponSystem\d+", read(f), re.M))


def flagship(uid):
    """A big hull with a flight deck: the carriers, the Type 071 and 055, a
    Kirov or a Slava - not an armed merchant that happens to be large."""
    kind, f = unit_file(uid)
    return (displacement(uid) >= FLAGSHIP_TONS and bool(f)
            and bool(re.search(r"^\[FlightDeck\]", read(f), re.M)))


# Navy emblems the base game does not ship, drawn from the gallery's flag set
# (integration/gallery/source/visuals/flags, credited in its
# VISUAL_CREDITS.txt). A commander_settings.ini path under
# ui/campaign/navy_emblems/sest_* must have an entry here.
SEST_EMBLEMS = {"sest_plan_emblem.png": "china_naval.png",
                "sest_pn_emblem.png": "philippines.png"}


def write_emblems(commander):
    from PIL import Image
    for path in re.findall(r"^NavyEmblem\w+=(ui/campaign/navy_emblems/sest_[^\s]+)$", commander, re.M):
        name = path.rsplit("/", 1)[1]
        if name not in SEST_EMBLEMS:
            raise SystemExit(f"commander settings name {path}, which SEST_EMBLEMS cannot draw")
        src = ROOT / "integration" / "gallery" / "source" / "visuals" / "flags" / "png" / SEST_EMBLEMS[name]
        with Image.open(src) as im:
            im = im.convert("RGBA")
            im.thumbnail((256, 256), Image.LANCZOS)
            canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            canvas.paste(im, ((256 - im.width) // 2, (256 - im.height) // 2), im)
        out = OUT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out, "PNG", optimize=True)


def enemy_roster_ini(missions, placements):
    """enemy_theater_roster.ini: every Taskforce2 unit the campaign places."""
    picks = collections.defaultdict(lambda: collections.defaultdict(set))
    flights = collections.defaultdict(dict)   # (nation, section) -> uid -> squadron -> flight
    order, problems = [], []
    # How often the campaign places each hull and variant. The Situation
    # window tracks a SurfacePersistent entry as one named ship: sunk once, it
    # reads Destroyed for the rest of the campaign. A hull and variant the
    # missions place more than once - three Peykaaps in one mission, a Type
    # 054A in two dozen - is a class, not a ship, and the 16 Oct 2026 test
    # read "Destroyed" against a Peykaap the next missions still sail. The
    # missions are authored and carry no generator slots, so this changes
    # what the window shows and nothing that sails.
    placed_times = collections.Counter()
    for m in missions:
        if m["group"] == "dispatch":
            continue
        for family, rows in placements[m["key"]].items():
            if family == "Taskforce2Vessel":
                for tag, keys, _name, _flag in rows:
                    if tag not in m.get("_unlisted", ()):
                        placed_times[(keys["Type"], keys.get("VariantReference"))] += 1
    for m in missions:
        if m["group"] == "dispatch":          # browser missions the campaign never loads
            continue
        counts = collections.Counter()
        for family, rows in placements[m["key"]].items():
            if not family.startswith("Taskforce2"):
                continue
            for tag, keys, _name, _flag in rows:
                # orbat=False (place()): the Situation window lists the
                # campaign's whole order of battle from the first mission, so
                # a boat whose navy is a mission's question is left out of it
                # - Red Line's showed a Collins and a USN submarine section.
                if tag in m.get("_unlisted", ()):
                    continue
                uid = keys["Type"]
                utype = unit_type(uid)
                if utype is None:
                    problems.append(f"{m['key']}: {uid} resolves to no unit file")
                    continue
                if utype == "Vessel" and not armed(uid):
                    continue                      # traffic, not order of battle
                pick = keys.get("VariantReference") or keys.get("SquadronReference") or "Default"
                nation = keys.get("Nation") or pick_nation(uid, pick) or m.get("red_nation") or ""
                nation = flags.flag_for(nation, uid) or nation
                label = ROSTER_NATION.get(nation.lower(), nation.replace(" ", "") or "Enemy")
                if label not in order:
                    order.append(label)
                if utype == "Vessel":
                    variant = keys.get("VariantReference")
                    if flagship(uid):
                        section = "SurfaceMajorFlagships"
                    elif variant and placed_times[(uid, variant)] == 1:
                        section = "SurfacePersistent"
                    else:
                        section, variant = "SurfaceReusable", None
                    picks[(label, section)][uid].add(variant or "Default")
                elif utype == "Submarine":
                    picks[(label, "SubmarinesPersistent")][uid].add(
                        keys.get("VariantReference") or "Default")
                elif utype in ("Aircraft", "VTOL", "Helicopter"):
                    section = "HelicoptersReusable" if utype == "Helicopter" else "AircraftReusable"
                    squadron = keys.get("SquadronReference") or "Squadron1"
                    # The Situation window takes a row's flag from the squadron it
                    # names: one its winning squadrons file does not define showed
                    # the unknown flag (the JH-7A, 16 Oct 2026 test).
                    if squadron not in squadrons(uid):
                        problems.append(f"{m['key']}: {uid} is rostered as {squadron}, which its "
                                        "winning squadrons file does not define - the Situation "
                                        "window would show no flag")
                        continue
                    counts[(label, section, uid, squadron)] += 1
                # land units: the stock roster carries none
        for (label, section, uid, squadron), n in counts.items():
            group = flights[(label, section)].setdefault(uid, {})
            group[squadron] = max(group.get(squadron, 0), n)
    if problems:
        raise SystemExit("enemy roster failed:\n  " + "\n  ".join(problems))

    def variant_key(v):
        m = re.match(r"(\D*)(\d+)$", v)
        return (0, int(m.group(2))) if m else (1, v)

    L = [f"; SEST {TITLE} - enemy theatre roster, the order of battle the campaign's",
         "; Situation button shows and tracks. Generated by integration/campaign/build_pack.py",
         "; from the units the missions place: every section, variant and flight size here",
         "; is one a mission uses. The campaign generates no units from this file - its",
         "; missions are authored - so it carries no formations and hides nothing.", ""]
    for label in order:
        L.append(f"; {label}")
        if label == "PLAN":
            # As the stock roster does for the PLAN: class and hull number in the
            # Situation display rather than individual ship names.
            L += [f"[NationalForces_{label}]", "ShowOnlyClassName=True", ""]
        for section in ROSTER_ORDER:
            if section.endswith("Reusable") and not section.startswith("Surface"):
                rows = flights.get((label, section), {})
                if not rows:
                    continue
                L.append(f"[{section}_{label}]")
                for uid in sorted(rows):
                    L.append(uid + "=" + "|".join(f"{sq},{n}" for sq, n in
                                                  sorted(rows[uid].items(), key=lambda kv: variant_key(kv[0]))))
                L.append("")
                continue
            rows = picks.get((label, section), {})
            if not rows:
                continue
            L.append(f"[{section}_{label}]")
            for uid in sorted(rows):
                L.append(uid + "=" + ",".join(sorted(rows[uid], key=variant_key)))
            L.append("")
    return "\n".join(L)


def roster_ini(roster, heading=None):
    """player_task_force_roster.ini, in the stock file's own syntax.

    Every pick is checked against the file that WINS the load order first: a
    price on a variant the hull no longer offers is a purchase the builder
    would be advertising and the game would refuse. Aircraft go in by squadron,
    ships by variant. A submarine - known by its UnitType, not by what its
    filename looks like - is refused: the game's task force cannot take one.
    """
    by_section, problems, credits = collections.defaultdict(list), [], {}
    for entry in roster:
        uid = entry["unit"]
        kind_dir, path = unit_file(uid)
        if path is None:
            problems.append(f"roster: no enabled mod defines {uid}")
            continue
        if Path(path).stem != uid:
            # The lookup here is case-blind; the game's match of a roster key
            # to a unit and its language section may not be.
            problems.append(f"roster: {uid} is spelled {Path(path).stem} by its file - "
                            "use the file's spelling")
            continue
        utype = unit_type(uid)
        section = ROSTER_SECTION.get(utype)
        if section is None:
            problems.append(f"roster: {uid} is a {utype}, which is not a "
                            "purchasable category")
            continue
        if section == "AllowedSubmarines":
            # In-game check, 13 Oct: a bought boat never showed in the
            # formation editor, and dismissing it did not take it out of the
            # force - it sailed in the next mission and stayed. Stock sells
            # none ("subs are currently not available for purchase in Pacific
            # Strike campaign"); a boat belongs in a mission, authored.
            problems.append(f"roster: {uid} is a submarine - the game's task "
                            "force cannot take a bought one (allied_fleet.py)")
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
    # A unit on sale makes the game read more than its own file. A bought
    # aircraft arms from every fit it offers, as resolve() credits a placed
    # one. Until 28 Oct 2026 only the unit file's owner was credited, and
    # Sulu Line's REQUIRED-MODS listed Modern US Navy and United States Naval
    # Aviation as not used while the Thai Seahawk's ASW fit hangs their
    # usn_ssq-62 and the RAN MH-60R's fits hang USNA's Hellfires and tanks.
    # Added after the units' own credits, and only for a mod not already
    # credited, so a mod that sells a unit stays a `roster` one.
    #
    # A bought hull's deck is not credited: it carries only the roster
    # aircraft the player puts aboard, which are credited as sold airframes.
    # LinearCampaignTaskForceMissionGenerator.WriteVesselSection calls
    # WriteCustomAirGroup for every ship (IL_0131-IL_014a), which clears the
    # authored group and writes CustomAirGroup=True with only the aircraft
    # assigned to that hull, and SceneCreator.SetAdditionalParameters
    # (IL_098c-IL_09b2) then loads that list in place of the variant's or the
    # unit's [AirGroup]. A free air wing comes only with ShipIncludesAirwing,
    # which every SEST campaign turns off, and even then from the roster's own
    # aircraft. Crediting the default group, as this did for a few hours on
    # 28 Oct 2026, put a Rafale pack, French Air Force and a Tu-95 mod on
    # hard-required lists for aircraft no player could fly.
    #
    # A bought hull also reads its own variants file and sails armed, and
    # neither was credited until later the same day. resolve() credits a
    # placed hull with the owner of <unit>_variants.ini and the rounds of its
    # fit; this does the same for every hull on sale, in resolve()'s order,
    # and for every fit the hull offers, as aircraft_credit() does for an
    # airframe. The buyer may pick any of them: IsShipLoadoutTypeRewardUnlocked
    # unlocks every fit LockedShipLoadoutVariants does not name, and no SEST
    # campaign names one; with PurchaseLoadouts=True a fit [LoadoutPrices]
    # leaves out costs what the unit file says (ReadLoadoutBasePurchaseCost).
    # EnsureSelectedLoadoutOption only sets the starting choice. The fit
    # pick_loadout() gives with no mission (Default where the file offers
    # one) is read first, so a round it hangs is the example shown. Until
    # later on 28 Oct 2026 only that fit was credited, and the SM-6 that
    # three of the Hobart's Late fits hang (SEST Collection Fixes) went
    # unseen. A fit dated after the campaign's loadout year is refused in
    # game (ResolveDateLockedLoadouts) and is credited here all the same: a
    # superset, as for an airframe.
    #
    # Last, as resolve() orders them, the model folders a sold unit's file
    # loads from another mod (asset_credit). The Mistral, on sale in Southern
    # Watch and Southern Reach, draws eight vehicle models from French Army
    # Vehicles. Until later on 28 Oct 2026 Southern Reach listed that mod as
    # not used, and Southern Watch as needed only for the Dispatches.
    for entry in roster:
        uid = entry["unit"]
        kind_dir, path = unit_file(uid)
        if ROSTER_SECTION.get(unit_type(uid)) in ("AllowedAircraft", "AllowedHelicopters"):
            # The airframe itself is bought, not placed by a mission.
            found = [(token, "roster" if how == "unit" else how, detail)
                     for token, how, detail in aircraft_credit(uid)]
        else:
            first, _why = pick_loadout(uid, path, None)
            found = [(owner(f"{kind_dir}/{uid}_variants.ini"), "variant", f"{uid} {pick}")
                     for pick in entry["picks"]]
            for fit in [first] + [f for f in loadouts(path) if f != first]:
                found += store_credit(uid, kind_dir, path, fit)
        found += asset_credit(uid, path)
        for token, how, detail in found:
            if token and token not in credits:
                credits[token] = (how, detail)

    L = [heading or f"; SEST {TITLE} requisition roster.",
         f"; Generated by integration/campaign/build_pack.py - edit {ROSTER_SOURCE}.",
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
    # Said of the hulls actually on sale, not assumed: "the inspected RAN
    # hulls declare none" was written before the Arafura, whose file offers
    # three fits, went on both rosters.
    fitted = [(e["unit"], loadouts(unit_file(e["unit"])[1]))
              for e in roster if unit_type(e["unit"]) in ("Vessel", "Submarine")]
    fitted = [(uid, fits) for uid, fits in fitted if fits]
    L += ["", "[LoadoutPrices]",
          "; Aircraft loadouts are included in the aircraft purchase cost.",
          "; Naval loadout presets are not advertised until they are authored",
          "; and tested" + ("." if fitted else " - no hull on this roster declares one.")]
    for uid, fits in fitted:
        L.append(f"; {uid} declares {', '.join(fits)}; none is priced here.")
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


def check_roster_on_sale(roster, missions, title):
    """The reverse of allowed_roster_units(): every roster entry must be on
    sale in at least one purchase window.

    allowed_roster_units() refuses an allowlist that names something the
    roster does not sell. Nothing refused a roster entry no allowlist names,
    and Southern Watch shipped one: a KC-46 priced at 75 points that no
    window ever offered - a line in the player's roster file that reads as a
    purchase and can never be one. An open builder with no allowlist sells
    the whole roster, so one such window satisfies every entry. `missions`
    is the whole campaign, never a --only subset: a window outside the
    filter still sells.
    """
    buying = [m.get("window", {}) for m in missions if m.get("window", {}).get("buy")]
    if any(not w.get("allow") for w in buying):
        return
    on_sale = {u for w in buying for u in w["allow"]}
    dead = [e["unit"] for e in roster if e["unit"] not in on_sale]
    if dead:
        raise SystemExit(f"{title}: the roster prices {', '.join(dead)}, which no "
                         "purchase window's allowlist names - a price nobody can "
                         "pay. Put it on sale in a window or take it off the roster")


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


def _tasking_decks_and_slots(placed):
    """(decks, slots) of one placed mission, as the recovery checks read them."""
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
    return decks, slots


def airframe_rows(uid, mission, placed):
    """[(row label, radius, recovers, slots)] for every air-tasking row of
    `mission` that a purchased `uid` could fill.

    A row takes the airframe when its [AI] Role meets the row's roles and its
    fits, if it declares any, overlap the row's. It recovers when every slot
    of that row has a compatible field or deck - deck_fit() 0, not merely
    undeclared - within its sortie radius of the cockpit.
    """
    rows = mission.get("window", {}).get("flights", [])
    if not rows:
        return []
    decks, slots = _tasking_decks_and_slots(placed)
    out = []
    for row in rows:
        label, _display, roles, _count, fits = row.split("|")
        want = frozenset(x for x in roles.split("/") if x)
        want_fits = frozenset(x for x in fits.split("/") if x)
        if not (ai_roles(uid) & want):
            continue
        _k, path = unit_file(uid)
        has = frozenset(loadouts(path)) if path else frozenset()
        if has and not has & want_fits:
            continue
        kind = unit_type(uid)
        radius = (airframe_range(uid) or 0.0) * SORTIE_FRACTION
        recovers = True
        spots = [sp for r, sp in slots if r == label]
        for sp in spots:
            ok = False
            for d in decks:
                if deck_fit(uid, kind, d[3], d[4]) != 0:
                    continue
                needs = deck_places_needed(uid, kind)
                if kind == "VTOL" and d[4]:
                    needs = 1
                if d[1] < needs or not (sp and d[2]):
                    continue
                if math.hypot(d[2][0] - sp[0], d[2][1] - sp[1]) <= radius:
                    ok = True
                    break
            if not ok:
                recovers = False
                break
        out.append((label, radius, recovers, len(spots)))
    return out


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
    for uid in roster_types:
        for label, radius, recovers, _slots in airframe_rows(uid, mission, placed):
            if not recovers:
                problems.append(
                    f"{mission['key']}: a purchased {uid} in the {label} "
                    f"flight has no compatible field or deck within "
                    f"{radius:.0f} NM of its cockpit - the row sells a "
                    "sortie the aircraft cannot recover from")
    return problems


def usable_allied(entries, missions, placements, rows=(), roster=(), authored=()):
    """(kept, dropped) - the allied entries a campaign may sell: the allied
    reserve's aircraft in the standard campaign (admit_reserve_aircraft) and
    the allied fleet on an Open Allocation twin.

    Ships are always kept: a ship sails in every mission that includes the
    task force. (No submarine is on the list: see allied_fleet.py.)
    An aircraft is kept only if at least one row in the campaign would take
    it and it recovers in every row that would: the builder will not sell a
    sortie it cannot fly, and would refuse the build if it did (see
    check_purchased_recovery). With `rows` it must also pass check_flights
    beside `roster`: a row whose roles match it has to offer one of its fits,
    or the row advertises a job the aircraft cannot fly (review of 2e845dc9:
    the F-16CM matched the Weapons Free strike row and had none of its fits).
    `dropped` says why for each one left out.
    """
    kept, dropped = [], []
    for e in entries:
        uid = e["unit"]
        if unit_type(uid) not in ("Aircraft", "Helicopter", "VTOL"):
            kept.append(e)
            continue
        if rows:
            try:
                check_flights(rows, list(roster) + [e], authored=authored)
            except SystemExit as exc:
                why = next((l.strip() for l in str(exc).splitlines() if uid in l),
                           str(exc).splitlines()[-1].strip())
                dropped.append((e, "a row takes its role but offers none of its fits: " + why))
                continue
        # A row with no cockpit is never written into the campaign (see
        # tasking_rows), so it takes nothing.
        takes = [(m["key"], r) for m in missions if m["key"] in placements
                 for r in airframe_rows(uid, m, placements[m["key"]]) if r[3]]
        if not takes:
            dropped.append((e, "no air-tasking row in this campaign takes it"))
        elif not all(r[2] for _k, r in takes):
            bad = sorted({f"{k} {r[0]}" for k, r in takes if not r[2]})
            dropped.append((e, "no field or deck in reach in " + ", ".join(bad)))
        else:
            kept.append(e)
    return kept, dropped


def admit_reserve_aircraft(spec, missions, placements, rows=(), authored=()):
    """(kept, dropped) - the allied reserve's held aircraft (spec RESERVE_AIR,
    mission_depth.apply_reserve) judged on the built missions, as the Open
    Allocation twins judged theirs (usable_allied), and handed back to
    mission_depth.admit_aircraft(): what is kept goes on the roster and on
    sale from its opening, and what is dropped is recorded with the reason.

    Judged on every mission of the campaign, not only those from the
    opening, though no aircraft can be bought earlier: check_flights and
    check_purchased_recovery hold every roster aircraft to every row, and
    a narrower judgment could sell an aircraft those gates then refuse. On
    21 Oct 2026 both judgments kept the same aircraft (Southern Watch 19 of
    38, Southern Reach 10 of 38). `rows` are the campaign's flight rows as
    widened by its own roster (widen_flights), as the twins' were: an allied
    aircraft flies the fits a row already offers, so the rows of the windows
    before the opening do not change.
    """
    import mission_depth
    held = spec.get("RESERVE_AIR", [])
    wrong = [f"{e['unit']} ({unit_type(e['unit'])})" for e in held
             if unit_type(e["unit"]) not in ("Aircraft", "Helicopter", "VTOL")]
    if wrong:
        raise SystemExit(f"{spec['TITLE']}: the allied reserve holds {', '.join(wrong)} "
                         "as aircraft (priced by squadron), and the unit file says otherwise")
    kept, dropped = usable_allied(held, missions, placements, rows, ROSTER, authored)
    mission_depth.admit_aircraft(spec, kept, dropped)
    return kept, dropped


def print_reserve(spec):
    """The reserve as the build settled it, into the build log: what each
    opening sells, and what was left out and why (spec RESERVE_LEFT_OUT)."""
    import mission_depth
    for m, units in mission_depth.reserve_offer(spec):
        air = sum(1 for u in units if unit_type(u) in ("Aircraft", "Helicopter", "VTOL"))
        print(f"{TITLE}: the reserve sells {len(units)} unit(s) from "
              f"{mission_depth.code_of(m)} {m['key']}: {len(units) - air} ship(s), "
              f"{air} aircraft")
    opening = mission_depth.open_from(spec)
    if opening is not None:
        print(f"{TITLE}: every force allocation from {mission_depth.code_of(opening)} "
              f"{opening['key']} offers the whole roster, {len(spec['ROSTER'])} unit(s)")
    left = spec.get("RESERVE_LEFT_OUT", [])
    if left:
        print(f"{TITLE}: {len(left)} reserve unit(s) left out:")
        for e, why in left:
            print(f"   {e['unit']:<30} {why}")


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


# Rounds a tasking row never offers, whatever the airframe carries: the
# AIM-260 and AIM-424 seats belong to Future Front (rule 3, the conventional
# fit), and the hand-written rows already kept every fit hanging them out.
TASKING_BARRED = frozenset({"dts_aim-260", "dts_aim-260_w", "usn_aim-424",
                            "sest_aim-424"})

# Which fits each row's job takes, by what the fit hangs rather than by name:
# a CAP fit carries air-to-air missiles and nothing for the surface; an
# Attack or SuCAP fit carries something for the surface; a patrol fit hunts
# submarines or ships. AEW is fitless (E-7A, KJ-500) and gains nothing.
_ROW_JOBS = {"CAP": "air", "Attack": "surface", "SuCAP": "surface",
             "Recon": "patrol", "HeloRecon": "patrol"}

# Rounds whose SecondaryTargetType=ASuW also makes a fit a surface fit. The
# AGR-30 Redback is air first, ships and land second - the counter-drone
# APKWS it is built from - and SEST_REDBACK is a strike fit: read off its
# primary alone it would leave the strike rows for the CAP rows. Other AAW
# rounds with an ASuW secondary (AIM-174B, AIM-54C, MICA, Mistral) are not
# here, so their fits stay air-to-air.
SURFACE_SECONDARY = frozenset({"sest_agr-30"})


@functools.lru_cache(maxsize=None)
def store_kind(store, depth=0):
    """(Type, TargetType, SecondaryTargetType, round) of one store, through
    `#!alias` and through a pod to the round it holds: the LRASM-ER is an
    alias of the LRASM, and the H-76's rocket fit hangs a LAU-68 Container
    whose round is the Hydra."""
    text = "".join(read(f) for f in all_copies(f"ammunition/{store}.ini"))
    kind = re.search(r"^Type=(\w+)", text, re.M)
    aim = re.search(r"^TargetType=(\w+)", text, re.M)
    second = re.search(r"^SecondaryTargetType=(\w+)", text, re.M)
    if depth < 4:
        if kind and kind.group(1) == "Container":
            inner = re.search(r"^Ammunition\d*=([^\s#/|]+)", text, re.M)
            if inner:
                return store_kind(inner.group(1), depth + 1)
        if not kind:
            base = re.search(r"#!alias\s+ammunition/(\S+?)\.ini", text)
            if base:
                return store_kind(base.group(1), depth + 1)
    return kind and kind.group(1), aim and aim.group(1), second and second.group(1), store


@functools.lru_cache(maxsize=None)
def fit_jobs(uid, fit):
    """(air, surface, asw, barred) for one aircraft fit, read off its stores."""
    kind_dir, path = unit_file(uid)
    air = surface = asw = False
    held = {s for s in stores(uid, kind_dir, path, fit) if s[0].isalpha()}
    for store in held:
        kind, aim, second, round_ = store_kind(store)
        if kind == "Missile" and aim == "AAW":
            air = True
        if kind in ("Missile", "Bomb", "AerialRocket") and (
                aim == "ASuW" or (second == "ASuW" and round_ in SURFACE_SECONDARY)):
            surface = True
        elif aim == "ASW":
            asw = True
    return air, surface, asw, bool(held & TASKING_BARRED)


def widen_flights(missions, roster):
    """Every air-tasking row also offers each fit its roster aircraft can fly.

    Play test of 18 Oct 2026: the Air Tasking screen showed only a few
    loadouts. A row's fit field is the whole menu - each aircraft flies the
    intersection - and the hand-written rows named two or three fits per
    airframe: the Super Hornet's strike row offered two of its thirty.
    The authored fits stay first and in their order; to them is added every
    fit a roster aircraft matching the row's roles defines whose stores suit
    the row's job (see _ROW_JOBS). Left out: fits with a barred round, fits
    that carry nothing for the job (Ferry, Empty, Transport, Passengers),
    nuclear fits, and names a campaign file cannot write (a space or `#`).
    Only the base roster widens a row, so every added fit passes
    check_flights' first rule by construction.
    """
    sellable = []
    for e in roster:
        kind_dir, path = unit_file(e["unit"])
        if kind_dir in ("aircraft", "helicopters"):
            sellable.append((e["unit"], ai_roles(e["unit"]), loadouts(path)))
    done = {}

    def widen(row):
        label, display, roles, count, fits = row.split("|")
        job = _ROW_JOBS.get(label)
        if not job:
            return row
        want_roles = frozenset(x for x in roles.split("/") if x)
        out = [x for x in fits.split("/") if x]
        for uid, have, offered in sellable:
            if not have & want_roles:
                continue
            for fit in offered:
                if (fit in out or re.search(r"[\s#]", fit)
                        or re.search(r"nuke|nuclear", fit, re.I)):
                    continue
                air, surface, asw, barred = fit_jobs(uid, fit)
                if barred:
                    continue
                if ((job == "air" and air and not surface and not asw)
                        or (job == "surface" and surface)
                        or (job == "patrol" and (asw or surface))):
                    out.append(fit)
        return f"{label}|{display}|{roles}|{count}|{'/'.join(out)}"

    for m in missions:
        rows = m.get("window", {}).get("flights")
        if rows:
            m["window"]["flights"] = [done.setdefault(r, widen(r)) for r in rows]


def window_of(mission):
    return mission.get("window", {})


def event_tile(event):
    """The map tile a story event stands on: the newspaper for a press page,
    the message tile for every other form. campaign.ini points at it and
    make_art writes only the tiles something stands on; both ask here, so
    the two cannot disagree about which file is referenced."""
    return "newspaper" if event.get("form", "press") == "press" else "message"


def campaign_ini(missions, events, placements):
    """The campaign spine, in native Task Force Mode.

    Every key here was read out of the exported Pacific Strike campaign before
    it was used. What that establishes is the vocabulary, not the balance: the
    numbers are a first pass and the bible's acceptance run is what would
    settle them.
    """
    EVENT_TILES = {e["file"]: event_tile(e) for e in events}
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
    # The Situation button's order of battle (enemy_roster_ini); the section
    # and key are the stock campaign's, campaign.ini lines 89-90.
    L += ["[DynamicUnitGeneration]", "Taskforce2RosterFile=enemy_theater_roster.ini", ""]
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
            # persistent task force units") is the detached operation, and
            # what the Includes flags say for such a mission is that nothing
            # of the player's deploys - as the three stock detached operations
            # show it. (IncludesAirwing is not display only: see below.)
            blank = not mission.get("generation")
            detached = blank or mission.get("detached")
            L.append(f"TaskForceModeIncludesTaskForce="
                     f"{'False' if detached else 'True' if placed.get('Taskforce1Vessel') else 'False'}")
            # The airwing sails only into a mission with air-tasking slots to
            # put it in. Every stock mission with IncludesAirwing=True has at
            # least one row, and every stock one whose Taskforce1 aircraft are
            # authored set dressing (01, 02, 03B, 04) says False. Rig Seventeen
            # said True over an authored Osprey and CH-53 and no row, and the
            # game died loading it: NullReferenceException in
            # SceneCreator.ResolvePlacedCampaignAircraft (Player.log, install
            # snapshot 9208d39e). So the flag is not display only.
            flights, empty = tasking_rows(mission, placed)
            L.append(f"TaskForceModeIncludesAirwing="
                     f"{'True' if flights and not detached else 'False'}")
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
            # Wherever the owned force sails it also gets the deployment
            # panel: stock pairs DeploymentOptions with a default disposition
            # every time (06, 07, 09, 10 Formation on Generated; 05 Dispersed
            # on Replaced), and its ui.ini carries "All Task Force ships must
            # deploy for this mission!" for the panel when the whole force is
            # required, so the panel is not only for detachments. The
            # mission's Deployment zones (deployment_zones) hold every unit of
            # the mission's own, sailing or not; render() stops the build
            # where one is outside every box that admits it, which covers
            # the force sailing into a mission with no zone.
            # deployment_panel() is the one rule: render() flagged the
            # mission's supplied units TaskForceModeIgnoreUnit by it.
            if blank:
                pass        # nothing of the player's sails: no deployment keys
            else:
                if deployment_panel(mission, placed):
                    L += ["TaskForceModeDeploymentOptions=True",
                          "TaskForceModeDefaultDisposition="
                          + ("Dispersed" if mission["generation"] == "Replaced"
                             else "Formation")]
                L.append("TaskForceModeRequireEntireTaskForce="
                         + ("False" if window.get("detachment") else "True"))
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
            # Prepare Airbase: the briefing's own planner for the airwing at a
            # player airfield. Stock offers it in five Pacific Strike missions
            # (1-4 ready flights, 1-4 half-prepared). Play test of 18 Oct
            # 2026: no airfield could be planned before the start, because
            # only three missions asked for it. Now every mission whose
            # airwing sails (it has tasking rows) and that has a player
            # airfield offers it; `airbase_prep=True` still insists.
            base = any("airbase" in k["Type"].lower() or "airfield" in k["Type"].lower()
                       for _t, k, _n, _x in placed.get("Taskforce1LandUnit", []))
            if window.get("airbase_prep") and not base:
                raise SystemExit(f"{mission['key']}: airbase_prep needs a "
                                 "player land unit whose Type contains "
                                 "airbase or airfield (the guide's rule)")
            if base and (window.get("airbase_prep") or (flights and not detached)):
                L += ["TaskForceModeAirbasePrepAvailable=True",
                      "TaskForceModeAirbasePrepReadySlots=4",
                      "TaskForceModeAirbasePrepInProgressSlots=2"]
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
            tile = EVENT_TILES.get(entry["file"], "newspaper")
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

# Since 28 Oct 2026 the roster credits what a unit on sale makes the game
# read, as resolve() credits a placed one: a variant, squadron, store or
# asset row may be a sold unit's.
HOW_TEXT = {
    "unit": "places the unit; this mod wins its file",
    "roster": "the requisition roster prices it, so the player can buy it",
    "variant": "supplies the hull variant a placed or sold unit uses",
    "squadron": "supplies the squadron a placed or sold airframe flies from",
    "store": "supplies a round a placed or sold unit's loadout hangs",
    "asset": "supplies a model folder a placed or sold unit's file draws from",
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


def reserve_report(spec):
    """The coverage report's record of the reserve (21 Oct 2026): what each
    opening sells beside the campaign's own roster, and every class of the
    fleet it draws on that is not sold, with the reason - a hull a mission
    places (mission_depth.apply_reserve) or an aircraft no row here can fly
    and recover (admit_reserve_aircraft). The build log says the same."""
    import mission_depth
    if not spec or not spec.get("RESERVE_OPENS"):
        return []
    air = ("Aircraft", "Helicopter", "VTOL")
    L = ["## The reserve", "",
         "What this campaign sells beside its own roster from a window its story "
         "names (`mission_depth.apply_reserve`): on sale at every force allocation "
         "from the one before the mission named, at the unit's own navy's price. A "
         "hull a mission places is never sold, and an aircraft only where a row here "
         "launches and recovers it (`admit_reserve_aircraft`).", "",
         "| from the window before | ships | aircraft |", "|---|---|---|"]
    for m, units in mission_depth.reserve_offer(spec):
        planes = sum(1 for u in units if unit_type(u) in air)
        L.append(f"| {mission_code(m)} {m['key']} | {len(units) - planes} | {planes} |")
    # Step 2 (21 Oct 2026): from the campaign's opening each force
    # allocation offers the whole roster, not the story's list with the
    # reserve after it. Every buy window is counted, so the record shows
    # where the story's lists end.
    opening = mission_depth.open_from(spec)
    if opening is not None:
        buying = [m for m in sorted(spec["MISSIONS"], key=mission_depth._when)
                  if m.get("window", {}).get("buy")]
        # Red Line opens at its first force allocation, so no window comes
        # before it to keep the story's list (review of 21 Oct 2026; the
        # rules page's availability line already said so).
        before = ("" if buying and opening is buying[0] else
                  "; the ones before it offer what the story releases")
        L += ["", f"From the force allocation before {mission_code(opening)} "
              f"{opening['key']}, every force allocation offers the whole roster - the "
              "campaign's own units with the reserve - as the Open Allocation version "
              f"did from the first (`mission_depth.open_offer`){before}. Units each "
              "force allocation offers:", "",
              "| window before | units | whole roster |", "|---|---|---|"]
        for m in buying:
            n = len(m["window"].get("allow") or spec["ROSTER"])
            whole = "yes" if mission_depth.open_offer(spec, m) is not None else "no"
            L.append(f"| {mission_code(m)} {m['key']} | {n} | {whole} |")
    left = spec.get("RESERVE_LEFT_OUT", [])
    if left:
        L += ["", f"Not sold ({len(left)}):", "", "| unit | why |", "|---|---|"]
        for e, why in left:
            L.append(f"| `{e['unit']}` | {why.replace('|', '/')} |")
    L.append("")
    return L


def report(rows, missions, worst, unused=(), coast=(), pooled=None, spec=None):
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
    meaning["external"] = ("in the collection for a third-party campaign or "
                           "scenario, or as content none of these campaigns places; "
                           "required all the same (SETUP checks every mod in the order)")
    for how in ("unit", "variant", "squadron", "roster", "store", "asset",
                "library", "shadowed", "external", "campaign"):
        if counts.get(how):
            L.append(f"| `{how}` | {meaning[how]} | {counts[how]} |")
    # Only a "pool" mission snaps to proven points; a "coast" one keeps its
    # positions as authored and CoastPlacer refuses any the extract contradicts.
    pooled = len(missions) if pooled is None else pooled
    if pooled == len(missions):
        snap = (f"Sea and land positions are snapped to points already used by a "
                f"loading mission; the furthest any anchor had to move is "
                f"{worst:.1f} NM.")
    elif pooled:
        snap = (f"Sea and land positions in {pooled} of the {len(missions)} "
                f"missions are snapped to points already used by a loading "
                f"mission (the furthest any anchor had to move is {worst:.1f} NM); "
                f"the other {len(missions) - pooled} use them as authored, "
                f"checked against the coastline extract.")
    else:
        snap = ("Sea and land positions are used as authored and checked against "
                "the coastline extract, not snapped to points from a loading "
                "mission; no anchor was moved.")
    L += ["", snap, "",
          "| mod / pack | title | class | via | mission |", "|---|---|---|---|---|"]
    for mid, title, how, detail, mission, _token in rows:
        L.append(f"| `{mid}` | {title} | `{how}` | {detail} | {mission} |")
    L.append("")
    L += reserve_report(spec)
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


def dispatch_only(all_rows, play_rows):
    """The rows of mods only the Dispatches need: required by the campaign's
    full build, not by what the campaign itself plays."""
    playing = {r[5] for r in play_rows if r[2] in NEEDED}
    return [r for r in all_rows if r[2] in NEEDED and r[5] not in playing]


def campaign_requirements(rows, missing, title, dispatches=(), dispatch_folder=None):
    """One campaign's dependency closure, in the lists a release needs: hard
    required, the Dispatches' extras, SEST donors, install-wide libraries,
    not used.

    `rows` and `missing` are what the campaign itself plays - its missions
    and its roster; `dispatches` are the rows only its browser Dispatches
    need (dispatch_only), listed apart so a player can see which mods only
    the Dispatches use. They stay installed all the same: every one is in
    LOAD-ORDER.txt, and SETUP stops if any mod there is missing.

    Computed from the same coverage rows as the pack-level file, so it cannot
    name a mod the campaign's missions do not reach; the pack-level
    REQUIRED-MODS.txt beside it is the union across every campaign shipped.
    """
    need = [r for r in rows if r[2] in NEEDED and r[5].isdigit()]
    packs = [r for r in rows if r[2] in NEEDED and not r[5].isdigit()]
    libs = [r for r in rows if r[2] in ("library",) and r[5].isdigit()]
    shadowed = [r for r in rows if r[2] == "shadowed"]
    external = [r for r in rows if r[2] == "external" and r[5].isdigit()]
    promoted, elsewhere = prerequisites(
        need, [r for r in rows if r[2] not in NEEDED and r[5].isdigit()])
    key = lambda r: r[1].lower()
    L = [f"{title.upper()} - what this campaign needs", "",
         "Derived from the units its missions place, the squadrons and hull",
         "variants they name and the rounds their loadouts hang, and from the",
         "units its roster sells with their variants and rounds. The pack-level",
         "REQUIRED-MODS.txt two folders up, at the pack's root, is the union",
         "across every campaign in the pack.", "",
         f"1. HARD REQUIRED ({len(need) + len(promoted)}): a mission or the roster "
         "names a file of theirs, or a mod above says it cannot run without them.", ""]
    for _mid, t, how, _d, _m, token in sorted(need, key=key):
        L.append(f"  {token:<13} {NEEDED[how]:<32} {t}")
    for row, askers in sorted(promoted.items(), key=lambda kv: kv[0][1].lower()):
        L.append(f"  {row[5]:<13} {'required by another mod':<32} {row[1]}")
        L.append(f"  {'':<13} {'':<32}   asked for by: {', '.join(sorted(set(askers)))}")
    for name, askers in sorted(elsewhere.items()):
        L.append(f"  {'(workshop)':<13} {'manual install':<32} {name} - required by "
                 f"{', '.join(sorted(set(askers)))}; not in this collection")
    disp = [r for r in dispatches if r[5].isdigit()]
    if disp:
        L += ["", f"1b. ONLY FOR THE DISPATCHES ({len(disp)}): the optional browser "
              f"missions in missions/{dispatch_folder} place these; the campaign",
              "itself never loads them. Keep them installed anyway: SETUP checks every",
              "mod in LOAD-ORDER.txt and stops if one is missing.", ""]
        for _mid, t, how, _d, _m, token in sorted(disp, key=key):
            L.append(f"  {token:<13} {NEEDED[how]:<32} {t}")
    L += ["", f"2. SEST INTEGRATION PACKS ({len(packs)}): this project's own patches, "
          "already inside this pack (SEST Integration Pack, Workshop 3812461539);",
          "there is nothing more to subscribe to.", ""]
    for _mid, t, how, _d, _m, token in sorted(packs, key=key):
        L.append(f"  {'(local)':<13} {NEEDED[how]:<32} {t}")
    L += ["", f"3. INSTALL-WIDE LIBRARIES AND UI ({len(libs)}): ship no file a mission "
          "names. Keep them installed anyway: SETUP stops if any mod in",
          "LOAD-ORDER.txt is missing. (Anchor Chain is one a mod in list 1 asks",
          "for; the map, salvo and rescue tools are conveniences.)", ""]
    for _mid, t, how, _d, _m, token in sorted(libs, key=key):
        L.append(f"  {token:<13} {'library':<32} {t}")
    if external:
        L += ["", f"3b. THIRD-PARTY CAMPAIGNS AND OTHER COLLECTION CONTENT ({len(external)}): "
              "in the collection for", "campaigns and scenarios this one does not "
              "include. Keep them installed anyway: SETUP", "stops if any mod in "
              "LOAD-ORDER.txt is missing.", ""]
        for _mid, t, how, _d, _m, token in sorted(external, key=key):
            L.append(f"  {token:<13} {'other campaigns':<32} {t}")
    dispatch_tokens = {r[5] for r in dispatches}
    unused = [(mid, token, t) for _w, mid, token, t in missing
              if token not in dispatch_tokens] + \
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
          "asset": "a model a unit draws"}


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
    # is most likely to be missing. Empty since 19 Oct 2026: SeaLifter, the
    # one entry, is no longer needed. The B-2's "Requires AnchorChain and
    # SeaLifter" dates from its game 0.4.0 _info.ini; the PC has never had
    # SeaLifter, and the B-2, A-10A, Su-25, Mi-8 and Type 003 all show their
    # models in the encyclopedia without it. Anchor Chain's preloader, which
    # was the manual part of the old install, SETUP installs.
    OUTSIDE = {}
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
    external = [r for r in rest if r[2] == "external"]
    rest = [r for r in rest if r[2] != "external"]
    key = lambda r: r[1].lower()
    L = [f"{TITLE.upper()} - required Steam Workshop mods", "",
         "TRY SETUP FIRST. \"SETUP - double-click me.cmd\" in this folder checks",
         "that every mod below is downloaded (and names the ones that are",
         "not, with links), installs the Anchor Chain preloader, and writes",
         "the whole Mod Manager order. The Steam collection this pack is",
         "listed in subscribes you to all of them in one press. If that",
         "works you do not need the list below at all, and it is here to",
         "check against rather than to work through by hand.",
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
    if external:
        L += ["", "-" * 74, "",
              f"In the collection for other campaigns and scenarios ({len(external)}):",
              "the third-party campaigns the collection carries, the mods they",
              "place, and content none of these four campaigns uses. They are in",
              "LOAD-ORDER.txt, so SETUP still requires them.", ""]
        for _mid, title, how, _detail, _mission, token in sorted(external, key=key):
            L.append(f"{token:<13} {'other campaigns':<32} {title}")
    L += ["", "-" * 74, "",
          "Not separate Workshop items. These are this project's own packs, and",
          "every one of them is already inside this folder (the SEST Integration",
          "Pack, Workshop item 3812461539) - there is nothing more to subscribe",
          "to; the repository also builds each of them on its own.", ""]
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
    """Every mod one campaign reaches (its Dispatches included), as a Workshop
    URL, in load-order sequence: the ones its missions reach, plus any a
    reached mod says it cannot run without.

    A reference list for the publisher - NOT the Workshop item's Required
    Items. The pack is published as ONE item (SEST Integration Pack -
    Modernised Campaigns, 3812461539) whose Required Items hold every
    Workshop mod in data/load-order.tokens.txt - more than any one campaign
    reaches - as does the collection 'SEST - Modernised Campaign Collection'
    (3812390790), which also holds the pack. The Mod Manager may offer 'Move
    dependencies above this mod' on the pack, which would undo every fix in
    it; SETUP sets the order, not Sync.
    """
    need = [r for r in rows if r[2] in NEEDED and r[5].isdigit()]
    promoted, elsewhere = prerequisites(need, [r for r in rows
                                               if r[2] not in NEEDED
                                               and r[5].isdigit()])
    rank = {t: i for i, t in enumerate(load_order())}
    both = need + list(promoted)
    both.sort(key=lambda r: rank.get(r[5], 10**6))
    L = [f"{TITLE} - Workshop mods this campaign reaches (reference only)", "",
         f"{len(both)} items, in canonical load order. NOT the Workshop item's",
         "Required Items list. All four campaigns ship in one item, the SEST",
         "Integration Pack (3812461539), whose Required Items - like the",
         "collection 'SEST - Modernised Campaign Collection' (3812390790) -",
         "hold every Workshop mod in the load order, more than any one",
         "campaign reaches. If the Mod Manager offers 'Move dependencies",
         "above this mod' on the pack, do not take it (not yet seen in game);",
         "if it was taken, run SETUP again, which puts the pack back on top.",
         "Generated by build_pack.py from the same coverage rows",
         "REQUIRED-MODS.txt uses, so it cannot name a mod the campaign does",
         "not reach.", ""]
    for row in both:
        L.append(f"https://steamcommunity.com/sharedfiles/filedetails/?id={row[5]}"
                 f"    # {row[1]}")
    if elsewhere:
        L += ["", "NOT IN THE COLLECTION - players install these by hand, as the",
              "pack-level REQUIRED-MODS.txt tells them; not in the Required Items:"]
        for name, askers in sorted(elsewhere.items()):
            L.append(f"  {name}  (required by {', '.join(sorted(set(askers)))})")
    L.append("")
    return "\n".join(L) + "\n"


def load_order_text():
    """The canonical order, as a player's Mod Manager would read it.

    With TITLES. The order is stored as workshop ids because that is what
    usersettings.ini stores, but the Mod Manager shows a player names - and a
    list of 190 bare numbers is not something a human can check an install
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
         "You do not have to do this by hand: with the game closed, double-",
         "click \"SETUP - double-click me.cmd\" in this folder and it writes",
         "exactly this order into the game's settings, your other mods at the",
         "bottom as you had them.", "",
         f"{'#':>4}  {'workshop id':<13} mod", ""]
    for i, token in enumerate(order, 1):
        if token.startswith("SEST_"):
            L.append(f"{i:>4}. {'(this pack)':<13} {token}")
        else:
            L.append(f"{i:>4}. {token:<13} {titles.get(token, '(not catalogued)')}")
    L.append("")
    return "\n".join(L) + "\n"


# --- main --------------------------------------------------------------------

# The SEST film behind the game's main menu. The menu's own film is a clip in
# the game's Unity data, not a file a mod can stand in for, so the pack ships
# a small Anchor Chain plugin (integration/menu-background/, built by its
# build_plugin.py) that points the menu's looping VideoPlayer at
# plugins/sest_menu.mp4 - cut from eleven SEST Gallery photographs by
# tools/make_menu_film.py. Anchor Chain, which SETUP installs, loads every DLL
# in a mod folder it knows, so the folder's name is free; a player without it
# simply keeps the stock menu. The DLL and the film are committed (compiler
# and ffmpeg output are not byte-stable); no DLL committed, no folder. Only
# the plugin itself ships: stubs/ is compile-time only, and a second
# AnchorChain.dll in a mod folder would be loaded beside the real one.
MENU_BACKGROUND = ROOT / "integration" / "menu-background"
MENU_INI = """; SEST Menu Background - the film behind Sea Power's main menu.
; Anchor Chain starts SEST.MenuBackground.dll from this folder; it finds the
; menu's background film (ClipName below) and plays the file named below instead.
; Enabled=0 turns it off and the game's own menu film plays.
[Menu]
Enabled=1
Film=sest_menu.mp4
; The game's menu clip: main_menu (Player.log, 10 Oct 2026, game 0.8.5). Empty:
; the first looping clip the game plays is taken as the menu's. Player.log
; lists every film the plugin saw, on lines starting [SEST Menu].
ClipName=main_menu
; Pictures=1 (on unless 0) writes the stock-pictures log: every loaded picture
; and every UI element showing one, on lines starting [SEST Pictures] - at
; start, after each scene load, every two minutes for ten, and when the Mod
; Manager is on screen. Pictures=0 turns the log off. Nothing on screen
; changes either way; the film plays the same. Where SEST UI Follow-up
; (SEST.ContactsFix.dll, README.txt) is active, the log is off whatever
; this says.
Pictures=1
; Backdrops=1 (on unless 0) puts SEST photographs in place of every other
; backdrop the game draws: the loading screens, the picture behind the
; scenario, campaign and Mod Manager pages, from the base game or another
; mod. The game mixes every mod's backdrops into one pool, so a file cannot
; replace them; the plugin paints a SEST photograph into each as it loads.
; Lines starting [SEST Backdrops] in Player.log say which. Backdrops=0 puts
; the game's own pictures back.
Backdrops=1
; Scenario, campaign and briefing pictures, maps, unit photos, flags and the
; game's logos are never touched. (CampaignArt, which also painted over
; pictures in other campaigns' and missions' folders, is retired: from
; 24 Oct 2026 the plugin ignores it.)
; TileGuard=1 (on unless 0) stops the error box that can come up on the
; campaign map after a mission: drawing a map tile while the mission is still
; unloading fails, and the plugin skips that tile instead. Lines starting
; [SEST TileGuard] in Player.log say when it did. TileGuard=0 lets the error
; through as before.
TileGuard=1
"""
MENU_README = """SEST MENU BACKGROUND

What this folder does: it plays the SEST film behind Sea Power's main menu
in place of the game's own, and shows SEST photographs in place of every
other backdrop picture: loading screens and the backdrops behind the
scenario, campaign and Mod Manager pages. Scenario, campaign and briefing
pictures and maps stay as their authors made them.

  SEST.MenuBackground.dll  the plugin. Anchor Chain (installed by SETUP)
                           starts it when the game starts.
  sest_menu.mp4            the film: eleven SEST Gallery photographs,
                           no text, darkened, looping, no sound.
  sest_menu.ini            Enabled=0 turns it all off; Backdrops=0 puts
                           the game's backdrops back;
                           Pictures=0 turns off the [SEST Pictures] lines
                           it writes to Player.log (SEST UI Follow-up,
                           below, turns them off anyway); TileGuard=0
                           turns off the campaign map's tile guard (below).
  MENU_CREDITS.txt         who took each photograph, and the licence.

It also guards the campaign map: after a mission, drawing a map tile while
the mission is still unloading can fail and bring up the game's error box.
The plugin skips that one tile instead.

Without Anchor Chain the plugin never runs and the menu is the game's own.
If the film cannot be played, the plugin puts the game's own film back.
Source: integration/menu-background/ in github.com/SEST-HOBBY/Seapower-mods

SEST's two other plugins share this folder:

  SEST.RuntimeFixes.dll    SEST Runtime Fixes 1.5.0. SEST_RUNTIME_README.txt
  SEST_RUNTIME_README.txt  says what it does; sest_runtime.ini turns its
  sest_runtime.ini         corrections off one at a time.
  SEST.ContactsFix.dll     SEST UI Follow-up 1.4.2, for players of Contact
                           Log: its window no longer opens or closes on the
                           time-control keys; the live F11 cost report
                           reuses each mission's price lists instead of
                           rereading them twice a second; Quick Load moves
                           (below). It turns off the [SEST Pictures] log
                           whatever sest_menu.ini says. It rewrites the
                           AIRCRAFT AND UNIT PREPARATION popup as four
                           numbered steps with a Start preparation button.
                           Three parts need Pop-Out Windows 1.0.1 and stay
                           off without it: the corrected Contacts pop-out;
                           Group Manager 0.2.17's Stock UI / Enhanced UI
                           switch; and the camera compass, which it moves
                           with the 3D view - to the unit camera on another
                           monitor when that view is detached, or into the
                           3D picture-in-picture over the full-screen map.
                           Popping Contacts or Group Manager out to a
                           second screen needs Pop-Out Windows 1.0.1 and a
                           second monitor. It writes timing lines to
                           Player.log every 30 seconds. It works only
                           beside this exact SEST.RuntimeFixes.dll, Contact
                           Log 1.0.1 and Sea Power 0.8.7 (Build 261021);
                           with anything else it writes one "inactive" line
                           to Player.log and changes nothing.

Quick Load moves to Ctrl+F9 where SEST UI Follow-up is on. Each time the
game loads its key bindings, a Quick Load key of F9 alone (the game's
default) becomes Ctrl+F9; any other Quick Load key is kept. F9 alone then
no longer quick-loads. It opens Contacts only if you set Contact Log's key
to F9 yourself (ToggleWindow under [Input] in
BepInEx\\config\\com.seapower.contactlog.cfg); SETUP does not. Pressing
Accept in the game's Options saves Ctrl+F9 in the game's controls.ini, and
it stays there after the pack or Contact Log is removed: then set Quick Load
back to F9 in Options if you want it.
Source: integration/runtime-fixes/ and integration/ui-followup/
"""


def write_menu_background(out):
    dll = MENU_BACKGROUND / "SEST.MenuBackground.dll"
    film = MENU_BACKGROUND / "sest_menu.mp4"
    if not (dll.is_file() and film.is_file()):
        print("  menu background: no plugin or film committed under integration/menu-background/ "
              "- folder not written; run build_plugin.py and tools/make_menu_film.py")
        return
    folder = out / "plugins"
    folder.mkdir(parents=True, exist_ok=True)
    for src in (dll, film, MENU_BACKGROUND / "MENU_CREDITS.txt"):
        (folder / src.name).write_bytes(src.read_bytes())
    (folder / "sest_menu.ini").write_text(MENU_INI, encoding="utf-8")
    (folder / "README.txt").write_text(MENU_README, encoding="utf-8")
    print(f"  menu background: {dll.name} ({dll.stat().st_size // 1024} KB) and "
          f"{film.name} ({film.stat().st_size // 1024} KB) in plugins/")


# SEST Runtime Fixes. Since 27 Oct 2026 the committed DLL is Runtime 1.5.0
# captured byte for byte from the owner's PC; its source is not in the
# repository and build_plugin.py refuses to overwrite it
# (integration/runtime-fixes/README.md, plugin-build.json).
def write_runtime_fixes(out):
    source = ROOT / "integration/runtime-fixes"
    dll = source / "SEST.RuntimeFixes.dll"
    if not dll.is_file():
        raise SystemExit("SEST runtime plugin missing: integration/runtime-fixes/SEST.RuntimeFixes.dll "
                         "(see integration/runtime-fixes/README.md)")
    folder = out / "plugins"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / dll.name).write_bytes(dll.read_bytes())
    for name in ("sest_runtime.ini", "SEST_RUNTIME_README.txt"):
        (folder / name).write_bytes((source / name).read_bytes())
    print(f"  runtime fixes: {dll.name} ({dll.stat().st_size} bytes); own code only")


# SEST UI Follow-up 1.4.2 (SEST.ContactsFix.dll), SEST's third plugin: built
# outside the repository from integration/ui-followup/source/ (it compiles
# against the game's own NoesisGUI, which cannot be committed) and committed
# as built. It patches Runtime 1.5.0's own Contacts and cost code, so it
# accepts only that exact SEST.RuntimeFixes.dll, Contact Log 1.0.1, the
# game's 0.8.7 Seapower-Scripts.dll and NoesisGUI, each by SHA-256; with any
# other it logs "inactive; original behavior retained" and patches nothing.
# Only the DLL ships: source/, including AnchorChain.Reference.cs, never does
# (a second AnchorChain assembly in a mod folder would be loaded beside the
# real one).
UI_FOLLOWUP = ROOT / "integration" / "ui-followup"


def write_contacts_fix(out):
    dll = UI_FOLLOWUP / "SEST.ContactsFix.dll"
    if not dll.is_file():
        raise SystemExit("SEST UI follow-up plugin missing: integration/ui-followup/SEST.ContactsFix.dll "
                         "(see integration/ui-followup/README.md)")
    folder = out / "plugins"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / dll.name).write_bytes(dll.read_bytes())
    print(f"  UI follow-up: {dll.name} ({dll.stat().st_size} bytes); own code only")


# The game's loading-screen backgrounds: ui/backgrounds/loading_screen_1.png ..
# _80.png (data/install-snapshot/streaming-media.txt, 10 Oct 2026, game
# 0.8.5). The 15 Oct 2026 log showed the game pools every mod's and its own
# backdrops rather than letting the first in the load order stand in, so
# these only join the pool; the menu plugin's backdrop swap
# (SestMenuBackground.cs, PictureSwap) paints them over the others. The SEST set
# (tools/make_loading_screens.py: the media report's photographs and the
# gallery's loading backgrounds, credits beside them) fills every slot in
# turn, so no original loading screen is left. The files are JPEG data under
# the game's .png names; the game loads both formats, and 80 PNG photographs
# would add 176 MB. A game update that adds slots shows its own there until
# LOADING_SLOTS is raised.
LOADING = ROOT / "integration" / "media-pack" / "loading"
LOADING_SLOTS = 80


def write_loading_screens(out):
    photos = sorted(LOADING.glob("sest_loading_*.jpg"))
    if not photos:
        print("  loading screens: none committed under integration/media-pack/loading/ "
              "- run tools/make_loading_screens.py")
        return
    folder = out / "ui" / "backgrounds"
    folder.mkdir(parents=True, exist_ok=True)
    for n in range(1, LOADING_SLOTS + 1):
        (folder / f"loading_screen_{n}.png").write_bytes(photos[(n - 1) % len(photos)].read_bytes())
    credits = LOADING / "LOADING_CREDITS.txt"
    if credits.is_file():
        (out / "LOADING-SCREEN-CREDITS.txt").write_bytes(credits.read_bytes())
    print(f"  loading screens: {len(photos)} photographs in the game's {LOADING_SLOTS} slots")


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
        plan_banners(spec["MISSIONS"])
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
                    CLOSURE_PROBLEMS, PLACEMENT_PROBLEMS, COAST_CHECKED,
                    OPENING_PROBLEMS, PARKED_NOTES):
            del lst[:]
        print(f"\n== {TITLE}")

        # The requisition roster is resolved first: a purchasable unit is
        # reached by the campaign as surely as a placed one, and a bad price
        # stops the build before twenty missions are rendered on top of it.
        roster_text, roster_credits = roster_ini(ROSTER)
        # ... every entry on sale somewhere, against the whole campaign ...
        check_roster_on_sale(ROSTER, spec["MISSIONS"], TITLE)
        # ... and the air-tasking rows against that same roster, before any of
        # them is written into a campaign entry.
        # Read once, here: rendering rewrites a mission's rows in place, and
        # an Open Allocation twin (spec OPEN_ALLOCATION) checks its own
        # roster against these same rows after the missions are built.
        widen_flights(spec["MISSIONS"], ROSTER)
        flight_rows = [r for m in spec["MISSIONS"] for r in m.get("window", {}).get("flights", [])]
        authored = {u["type"] for m in spec["MISSIONS"] for u in m["units"] if u.get("slot")}
        check_flights(flight_rows, ROSTER, authored=authored)
        built, worst, placements, reached = [], 0.0, {}, []
        for mission in missions:
            if (mission.get("geography") or GEOGRAPHY) == "coast":
                placer = CoastPlacer(coast_data(mission), mission)
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
            check_opening(mission, placed)
            solve_arrival(mission, placed, members)
            check_coast_geometry(mission, placer)
            check_geometry(mission, placed, members)
            name, text = render(mission, placed, members)
            built.append((name, text, mission))
            placements[mission["key"]] = placed
            reached.append((mission, mission_credits))
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
        if PARKED_NOTES:
            print(f"\n{len(PARKED_NOTES)} unit(s) with no Deployment box - each starts within "
                  f"{DEPLOY_CLEAR_NM:g} NM of a circle that other units of its kind have still to "
                  "reach, and the game lets any unit of a kind a box admits be placed in it:")
            for note in PARKED_NOTES:
                print(f"  {note}")
        if REACH_PROBLEMS or CLOSURE_PROBLEMS or PLACEMENT_PROBLEMS or OPENING_PROBLEMS:
            sys.exit("geometry failed:\n  " + "\n  ".join(
                PLACEMENT_PROBLEMS + REACH_PROBLEMS + CLOSURE_PROBLEMS
                + OPENING_PROBLEMS))

        # The allied reserve's aircraft (mission_depth.apply_reserve held them
        # back): only the built missions say whether a row launches and
        # recovers one. What passes goes on the roster and on sale from its
        # opening, and then every window from an opening says what the
        # reserve sells there. The roster and the flight rows are checked
        # again as they were above, now with the aircraft on sale.
        import mission_depth
        kept, _dropped = admit_reserve_aircraft(spec, [m for _n, _t, m in built],
                                                placements, flight_rows, authored)
        mission_depth.say_reserve(spec)
        if kept:
            roster_text, roster_credits = roster_ini(ROSTER)
            check_roster_on_sale(ROSTER, spec["MISSIONS"], TITLE)
            check_flights(flight_rows, ROSTER, authored=authored)
        if spec.get("RESERVE_OPENS"):
            print_reserve(spec)
        # The roster's credits first, then each mission's in build order, a
        # stronger kind replacing a weaker one: merged here rather than as
        # each mission was built, so that the roster is the one the reserve
        # has settled (21 Oct 2026). What the campaign itself loads - its own
        # missions and its roster - is apart from the Dispatches, which are
        # browser missions the campaign never loads. Southern Watch's
        # Dispatches place a unit from nearly every mod in the collection
        # (they are the pack's coverage), and a REQUIRED-MODS built from both
        # told a player of the campaign to install 137 mods it does not use
        # (user report, 28 Sep).
        credits = {token: (why[0], why[1], ROSTER_ORIGIN)
                   for token, why in roster_credits.items()}
        play_credits = dict(credits)
        for mission, mission_credits in reached:
            for token, why in mission_credits.items():
                if stronger_credit(why, credits.get(token)):
                    credits[token] = why
                if mission["group"] != "dispatch":
                    if stronger_credit(why, play_credits.get(token)):
                        play_credits[token] = why

        # Built BEFORE the dry-run exit, because every air-tasking gate lives
        # in here - the row/section pairing, the role and fit checks, the
        # label vocabulary, the purchase allowlists. Returning first made
        # `--dry-run` ("resolve and check everything, emit nothing") the one
        # command that checked none of them: the same mutation passed dry-run
        # and failed the real build. It is pure, so building it early costs
        # nothing.
        campaign_text = campaign_ini([m for _n, _t, m in built], spec["EVENTS"],
                                     placements) + "\n"
        enemy_text = enemy_roster_ini([m for _n, _t, m in built], placements) + "\n"
        rows, missing = coverage(credits, spec.get("EXCUSES", {}))
        print(f"\n{TITLE}: reaches {len(rows)} mods and packs; "
              f"{len(missing)} enabled and not reached by this campaign")
        # The allied fleet may not repeat the roster, twin or no twin: the
        # allied reserve moves its classes from one to the other.
        repeat = sorted({e["unit"] for e in spec.get("ALLIED_FLEET", [])}
                        & {e["unit"] for e in ROSTER})
        if repeat:
            sys.exit(f"{TITLE}: the allied fleet repeats roster units {repeat}")
        # Everything that can stop the build is decided here, before the dry
        # run returns and before the pack folder is cleared: the rules page
        # (roster nations, no submarine on sale) and, for a campaign that
        # opts in to OPEN_ALLOCATION, the twin and its spine. No campaign in
        # the pack does since 21 Oct 2026 (see "open allocation" above).
        rules_text = campaign_rules(spec)
        play_rows, play_missing = coverage(play_credits, spec.get("EXCUSES", {}))
        twin = None
        if spec.get("OPEN_ALLOCATION"):
            twin = open_allocation_twin(spec, campaign_text, [m for _n, _t, m in built],
                                        placements, flight_rows, authored, play_credits)
            if spec.get("ALLIED_FLEET"):
                print(f"{TITLE} - Open Allocation: {len(twin['allied'])} allied unit(s) on "
                      f"sale, {len(twin['allied_dropped'])} aircraft left out:")
                for e, why in twin["allied_dropped"]:
                    print(f"   {e['unit']:<28} {why}")
        campaigns.append(dict(spec=spec, built=built, placements=placements,
                              rules_text=rules_text, twin=twin,
                              play_rows=play_rows, play_missing=play_missing,
                              credits=credits, rows=rows, missing=missing,
                              worst=worst, roster_text=roster_text,
                              enemy_text=enemy_text,
                              campaign_text=campaign_text, missions=missions,
                              coast=list(COAST_CHECKED),
                              pooled=sum((m.get("geography") or GEOGRAPHY) != "coast"
                                         for m in missions)))
        for token, why in credits.items():
            if stronger_credit(why, pack_credits.get(token)):
                pack_credits[token] = why

    # The pack's coverage rule: every enabled mod is placed by SOME campaign
    # in the pack, or excused in writing. A second campaign does not have to
    # reach every mod in the load order on its own - the spec for Southern
    # Reach says it must not - but nothing in the load order may go
    # unaccounted for.
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
    sys.path.insert(0, str(ROOT / "integration" / "mission-seeds"))
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
        for stem, _entry, asset, _side in recognition(mission):
            (brief / f"{stem}.png").write_bytes(recognition_png(asset["file"]))
        if banner(mission):
            stem, asset = banner(mission)
            (brief / f"{stem}.png").write_bytes(banner_png(asset["file"]))

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
        plan_banners(spec["MISSIONS"])
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
            # The campaign's photograph on its opening front page (the page
            # the campaign opens on), credited on the page.
            base = SLUG.removesuffix("-open")
            ca = gallery_assets().get(CAMPAIGN_BACKDROP.get(base, CAMPAIGN_BANNER.get(base, "")))
            cover = ((GALLERY / ca["file"], f"{ca['label']}. "
                      + photo_credit(ca).replace(" · resized", " · cropped")) if ca else None)
            make_art.render_all(camp, cards, spec["EVENTS"], SLUG, TITLE, SUBTITLE,
                                prefix=ART_PREFIX, label=SERIES_LABEL,
                                tiles={event_tile(e) for e in spec["EVENTS"]}, cover=cover)

        # The briefing map beside every mission - the right-hand pane of the
        # briefing screen, drawn from <mission>_briefing/BriefingMap_en.xml
        # and the image it binds (see integration/mission-seeds/briefing_maps.py).
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
                                            focus_nm=m.get("map_focus_nm", MAP_FOCUS_NM),
                                            inset_box=MAP_INSET)
                if m["group"] != "dispatch":
                    dst = OUT / "missions" / browse_folder(m) / f"{name}_briefing"
                    for fn in (f"{stem}.png", "BriefingMap_en.xml"):
                        shutil.copy2(src / fn, dst / fn)
        (camp / "campaign.ini").write_text(c["campaign_text"], encoding="utf-8")
        (camp / "player_task_force_roster.ini").write_text(c["roster_text"],
                                                           encoding="utf-8")
        (camp / "enemy_theater_roster.ini").write_text(c["enemy_text"], encoding="utf-8")
        (camp / "commander_settings.ini").write_text(spec["COMMANDER"], encoding="utf-8")
        write_emblems(spec["COMMANDER"])
        (camp / "campaign_rules_en.xml").write_text(c["rules_text"], encoding="utf-8")
        for folder, desc in folders.items():
            (OUT / "missions" / folder / "_info.ini").write_text(info(folder, desc),
                                                                 encoding="utf-8")
        # This campaign's own closure, in the four lists a release needs.
        (camp / "REQUIRED-MODS.txt").write_text(
            campaign_requirements(c["play_rows"], c["play_missing"], TITLE,
                                  dispatch_only(c["rows"], c["play_rows"]),
                                  spec["DISPATCHES"]), encoding="utf-8")
        # The Open Allocation twin, for a campaign that opts in to one.
        twin = write_open_twin(OUT, spec, c["twin"], c["rows"]) if c["twin"] else None
        COVERAGE_DOC.parent.mkdir(parents=True, exist_ok=True)
        COVERAGE_DOC.write_text(report(c["rows"], spec["MISSIONS"], c["worst"],
                                       unused=c["missing"], coast=c["coast"],
                                       pooled=c["pooled"], spec=spec),
                                encoding="utf-8")
        # A reference list for the publisher, kept in docs/ rather than the
        # download. It is NOT the Workshop item's Required Items, which (like
        # the collection 3812390790) hold every Workshop mod in the load
        # order; SETUP, not the Mod Manager's dependency fix, sets the order.
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        (DOCS_DIR / "required-mods-urls.txt").write_text(required_urls(c["rows"]),
                                                         encoding="utf-8")
        files = sum(1 for f in camp.rglob("*") if f.is_file())
        total_files += files
        twin_files = sum(1 for f in twin.rglob("*") if f.is_file()) if twin else 0
        total_files += twin_files
        print(f"  {TITLE}: {len(built)} missions, {len(spec['EVENTS'])} events, "
              f"{files} files under campaigns/{SLUG}"
              + (f", {twin_files} under campaigns/{open_slug(SLUG)}" if twin else "")
              + f"; wrote {COVERAGE_DOC.relative_to(ROOT)}")

    # The pack's own entry in the Mod Manager. No Type= here: that key
    # classifies a MISSION folder, and native mod roots do not carry one.
    # One entry carries every campaign in the pack, so its name and its
    # description name them all.
    titles = [c["spec"]["TITLE"] for c in campaigns]
    # The campaigns' own descriptions are the in-game bios and stay in the
    # world. What a player needs to install it belongs here, on the pack's
    # Mod Manager entry, once.
    # The Open Allocation sentence only while some campaign ships a twin,
    # naming those that do: none has since 21 Oct 2026.
    opened = [c["spec"]["TITLE"] for c in campaigns if c["twin"]]
    if opened and len(opened) == len(campaigns):
        twins = (" Each campaign is also listed as an Open Allocation version, which "
                 "offers its whole roster from the first force allocation instead of "
                 "as the story releases it.")
    elif opened:
        names = (opened[0] if len(opened) == 1
                 else ", ".join(opened[:-1]) + " and " + opened[-1])
        twins = (f" {names} " + ("is also listed as an Open Allocation version, which "
                                 "offers its whole roster from the first force allocation "
                                 "instead of as the story releases it." if len(opened) == 1 else
                                 "are also listed as Open Allocation versions, which "
                                 "offer their whole rosters from the first force allocation "
                                 "instead of as the story releases them."))
    else:
        twins = ""
    blurb = (" ".join(c["spec"]["INFO_DESC"] for c in campaigns)
             + twins
             + " Needs the Steam Workshop mods listed in REQUIRED-MODS.txt in "
               "this mod's folder; LOAD-ORDER.txt beside it is the Mod Manager "
               "order it was built and tested against. SETUP: Open Folder on "
               "this entry, quit the game, double-click \"SETUP - double-click "
               "me.cmd\" - it checks the subscriptions, installs the Anchor "
               "Chain preloader and sets the whole order for you.")
    (OUT / "_info.ini").write_text(
        info(" - ".join(titles), blurb, general="",
             tail="\n[Compatibility]\nApproximateVersion=0.8.7\n"),
        encoding="utf-8")
    # The pack-level lists, from the union of what every campaign reaches.
    set_campaign(dict(campaigns[0]["spec"], TITLE=" / ".join(titles)))
    (OUT / "REQUIRED-MODS.txt").write_text(requirements(rows), encoding="utf-8")
    (OUT / "LOAD-ORDER.txt").write_text(load_order_text(), encoding="utf-8")
    # The setup script and its double-click launcher ship at the pack root,
    # byte for byte from integration/campaign/setup/ (CRLF, as Windows
    # expects a .cmd to be; .gitattributes marks both ends -text).
    for src in sorted((HERE / "setup").iterdir()):
        if src.is_file() and not src.name.startswith("."):
            (OUT / src.name).write_bytes(src.read_bytes())
    write_menu_background(OUT)
    write_runtime_fixes(OUT)
    write_contacts_fix(OUT)
    write_loading_screens(OUT)

    files = sum(1 for f in OUT.rglob("*") if f.is_file())
    print("wrote REQUIRED-MODS.txt and LOAD-ORDER.txt into the pack")
    print(f"\nbuilt {OUT.relative_to(ROOT)}: {files} files, "
          f"{sum(len(c['built']) for c in campaigns)} missions across "
          f"{len(campaigns)} campaign(s)")


CAMPAIGN_BLURB = ""


if __name__ == "__main__":
    main()
