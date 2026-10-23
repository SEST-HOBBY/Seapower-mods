#!/usr/bin/env python3
"""Fail on retired claims that must not come back into shipped text.

Some sentences in this repo stopped being true on a known day, and each one
was written into several places at once - a builder's Mod Manager blurb, a
README, a comment block that the builder copies verbatim into every pack that
carries the weapon. Correcting one copy has repeatedly left its siblings
behind. The AIM-424 respec fixed the missile definition and the F-15EX blurb,
and three sibling packs went on calling it an AARGM-ER derivative; the same
respec left the old reasoning in a comment block that was emitted into all
seven copies of sest_aim-424.ini.

Each entry below is a phrase (a case-insensitive regex), the files it must be
absent from, and why it is retired. Both the SOURCE (builders, the shared
definition, pack READMEs) and the OUTPUT (every emitted _info.ini, ammunition
file and language file, the consolidated dist included) are held, so a stale
sentence cannot survive in either.

    python3 tools/check_stale_phrases.py

Exits non-zero on any hit. Standard library only; reads nothing but the tree.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEC = dict(encoding="utf-8", errors="surrogateescape")

# Every place the AIM-424 is described. integration/*/SEST_*/ also matches the
# consolidated integration/dist/SEST_Integration/.
AIM424_SOURCES = [
    "integration/*/build_*.py",
    "integration/common/aim424.py",
    "integration/*/README.md",
]
AIM424_OUTPUT = [
    "integration/*/SEST_*/_info.ini",
    "integration/*/SEST_*/ammunition/sest_aim-424.ini",
    "integration/*/SEST_*/language_en/ammunition_names.ini",
]
AIM424_ROUND = [
    "integration/common/aim424.py",
    "integration/*/SEST_*/ammunition/sest_aim-424.ini",
]

REVEAL = "retired by the U.S. Navy's AIM-424 reveal, 22 Aug 2026"

# SEST Collection Fixes' #!extend stubs over the collection's other AIM-424s
# (build_aim424 in integration/collection-fixes/build_patch.py), and the docs
# that tell a player which AIM-424 flies how. The decision log,
# docs/conflicts-and-load-order.md, keeps the dated record of each retired
# decision, so the patterns below match the claims as present-tense
# statements only; the log words its history so that it does not.
AIM424_STUBS = ["integration/*/SEST_*/ammunition_overwrite/*.ini"]
AIM424_DOCS = [
    "README.md",
    "docs/FEATURES.md",
    "docs/conflicts-and-load-order.md",
    "data/mod-catalog.json",
    "docs/mod-catalog.md",
]
ONE_AIM424 = ("retired by the player's decision of 14 Oct 2026: every AIM-424 in the "
              "collection flies SEST's own flight model on SEST's model block "
              "(build_aim424 in integration/collection-fixes/build_patch.py)")
# A fourth element WRAPPED also matches a phrase that a Markdown paragraph
# breaks over two lines. Both claims below were first written that way.
WRAPPED = "wrapped"

# Red Line's text, source and built: the reports mission_depth adds, the
# missions, every copy of them the pack and the consolidated dist ship, and
# the campaign's own documents.
RED_LINE_TEXT = [
    "integration/campaign/mission_depth.py",
    "integration/campaign/red_line/*.py",
    "integration/*/SEST_*/campaigns/sest-red-line*/missions/*.ini",
    "integration/*/SEST_*/campaigns/sest-red-line*/missions/*_briefing/*.xml",
    "integration/*/SEST_*/missions/Red Line/*.ini",
    "integration/*/SEST_*/missions/Red Line/*_briefing/*.xml",
    "docs/campaigns/red-line/*.md",
]
RED_LINE_B1 = ("retired by the campaign upgrade's first batch, 20 Oct 2026 "
               "(docs/campaigns/campaign-upgrade-plan.md, section 8)")

# The player-facing text that describes the campaigns: what a player reads
# before or while playing them.
PLAYER_TEXT = [
    "README.md",
    "docs/FEATURES.md",
    "docs/play-test-guide.md",
    "docs/campaigns/side-operations.md",
    "docs/campaigns/southern-watch/workshop-listing.md",
    "integration/gallery/steam_art/cards.json",
]
# The owner's decisions of 21 Oct 2026, for the pending 20 Oct update. The
# builder can still write an Open Allocation twin for a spec that opts in
# (OPEN_ALLOCATION), so its own Mod Manager sentence is not held here: a
# campaign that opts in again rewords these docs and this entry with it.
TWINS_RETIRED = ("retired by the owner on 21 Oct 2026: no campaign in the pack ships an "
                 "Open Allocation version (Southern Watch build notes, 'Open Allocation "
                 "retired from the pack')")
RL03_HELD = ("held by the owner on 21 Oct 2026: The Other Picture reads nothing from The "
             "Ships from the North until a reveal at Classify is shown to satisfy a "
             "UnitClassified stage (Red Line test card 7.4; restorable from 9035f291)")
# The rules page every campaign ships, built and consolidated.
RULES_PAGES = ["integration/*/SEST_*/campaigns/*/campaign_rules_en.xml"]
FLEET_ON_SALE = ("retired by the owner on 21 Oct 2026: the standard campaigns sell what the "
                 "Open Allocation versions sold beyond the story's lists - the allied fleet "
                 "from Weapons Free and Tasman Crossing, its aircraft where a row can fly "
                 "them, and Red Line's Type 901 and 903A from its first force allocation "
                 "(Southern Watch build notes, '21 October: the allied fleet in the standard "
                 "campaigns')")
# Step 2 of the same decision, later that day: from those windows every force
# allocation offers the whole roster, as the versions did, not the story's
# list with the fleet after it. Held in the player's text, the rules pages,
# the built spines and rosters (window words and roster notes), the test
# cards and Red Line's tables, where step 1's words said the story still
# released the campaign's own units after the opening.
WHOLE_ROSTER = ("retired by the owner on 21 Oct 2026 (step 2): from Weapons Free, Tasman "
                "Crossing and Red Line's first force allocation every force allocation offers "
                "the whole roster with the fleet, as the Open Allocation versions did; only the "
                "windows before keep the story's lists (Southern Watch build notes, 'Step 2: "
                "the whole roster from the opening')")
# The pending 20 Oct change log said, from 22 to 23 Oct 2026, that Sea Power
# 0.8.7 had switched off parts of other mods' code until their authors
# updated. The authors did on 23 Oct, before the log was uploaded.
OTHER_MODS_BACK = ("retired by the authors' 23 Oct 2026 updates: the Fury's, EC-2's, K5 "
                   "KRAKEN's, Saronic Corsair's, MV-75's and YF-23's plugins stay on under "
                   "Sea Power 0.8.7 (docs/workshop-refresh-20261023-review.md)")
# The AGR-30 Redback's descriptions: its builder, the shared fit recipe, the
# pack READMEs and every emitted copy of the round, its pods, its name and
# the packs' Mod Manager blurbs.
REDBACK_TEXT = [
    "integration/allied-fixes/build_patch.py",
    "integration/common/redback.py",
    "integration/*/README.md",
    "integration/*/SEST_*/_info.ini",
    "integration/*/SEST_*/ammunition/sest_agr-30*.ini",
    "integration/*/SEST_*/language_en/ammunition_names.ini",
]
REDBACK_FF = ("retired on 23 Oct 2026: the AGR-30 is fire and forget (MidCourseCorrection=0) - "
              "radio command needed a guidance channel the Seahawks and A-10s do not link, and "
              "the RAN MH-60R never fired it (docs/playtest-20261023-redback.md)")
REDBACK_SEAHAWK = ("retired on 23 Oct 2026: on the Hellfire launcher's lower rail points the "
                   "MH-60R's 19-tube pods sat in the bottom of the quad rack; its fit now hangs a "
                   "7-tube pod in each Hellfire's place on the drawn launcher "
                   "(docs/playtest-20261023-redback.md)")
# The same day's second report, on 57375598: the AGR-30 fired from the
# MH-60R, whose 19-tube pods had taken its auxiliary tanks' Stations 1/2 on a
# SEST seat (RedbackH60). Its climb was gone because the 8 NM
# TerminalApproachDist put every shot inside 8 NM into terminal approach, which
# holds the height. The speed keys were then set from the game's own rules, as
# the builder's comment above the round's swaps records. History docs (the
# build notes, the play-test reports) keep the old figures as history; these
# entries hold the text that describes the round and the fit as they are.
REDBACK_LAUNCHER = ("retired by the owner's second report of 23 Oct 2026: tanks back on the "
                    "MH-60R's Stations 1/2, and a 7-tube pod in each Hellfire's place on the M299 "
                    "launcher, on the RedbackM299 seat (docs/playtest-20261023-redback.md)")
REDBACK_SWITCH_ON = ("retired by the owner's second report of 23 Oct 2026: TerminalApproachDist is "
                     "2 NM again - at 8 NM every shot from inside 8 NM began in terminal approach, "
                     "which holds the height, and never climbed (docs/playtest-20261023-redback.md)")
REDBACK_SPEEDS = ("retired by the owner's second report of 23 Oct 2026: read from the game's code, "
                  "MaxLoftVelocity (150 kt) is the target for the climb and the whole cruise and "
                  "MaxVelocity (450 kt) the launch run-up's, and Deceleration=0.25 is a straight-line "
                  "bleed of Deceleration x 19.05 kt/s, neither g nor a fraction per second "
                  "(docs/playtest-20261023-redback.md)")
WHOLE_ROSTER_TEXT = PLAYER_TEXT + RULES_PAGES + [
    "integration/*/SEST_*/campaigns/*/campaign.ini",
    "integration/*/SEST_*/campaigns/*/player_task_force_roster.ini",
    "docs/campaigns/*/test-card.md",
    "integration/campaign/red_line/tables.py",
]

# (regex, globs, why[, WRAPPED])
STALE = [
    (r"AARGM-ER airframe", AIM424_SOURCES + AIM424_OUTPUT,
     f"the AIM-424 is a Raytheon LRAAM, not an AARGM-ER derivative ({REVEAL})"),
    (r"AIM-174-class reach", AIM424_SOURCES + AIM424_OUTPUT,
     f"the AIM-424's own figure is 'in excess of 250 nm' ({REVEAL})"),
    (r"has to fit (inside )?an F-35|fit an F-35 weapons bay", AIM424_SOURCES + AIM424_OUTPUT,
     f"bay fit is not why the AIM-424 reaches 290 nm - it fits the bay and "
     f"makes 250+ anyway ({REVEAL})"),
    (r"no AIM-424 mesh exists", AIM424_SOURCES + AIM424_OUTPUT,
     "false: US Naval Aviation ships aim-424.obj (usn_aim-424) and the YF-23 "
     "mod ships yf23_aim424; the AGM-88G stand-in is kept by choice"),
    (r"what-if[^.\n]*(AIM-424|MALICE)", AIM424_SOURCES + AIM424_OUTPUT,
     f"the AIM-424 is a real weapon now ({REVEAL})"),
    (r"dual-pulse|2030s seeker|Mass[^.\n]*NOT disclosed", AIM424_ROUND,
     "pre-reveal guesses: the motor is reported two-stage and the weight is "
     "published (1,500 lb / 680 kg, U.S. Navy fact file)"),
    (r"U\.S\. Navy 2027'?s flight model for every AIM-424"
     r"|every AIM-424[^.\n]*\bflies U\.S\. Navy 2027"
     r"|flies U\.S\. Navy 2027'?s AIM-424 flight model",
     AIM424_SOURCES + AIM424_OUTPUT + AIM424_STUBS + AIM424_DOCS,
     "the 13 Oct plan (feature/aim424-usn2027-flight-model) was never merged; " + ONE_AIM424,
     WRAPPED),
    (r"YF-23 (still )?(keeps|fires) its author's (own )?round"
     r"|yf23_aim424_internal is not SEST's"
     r"|yf23_aim424_internal on its own mesh"
     r"|author's own round \(the current state",
     AIM424_SOURCES + AIM424_OUTPUT + AIM424_STUBS + AIM424_DOCS,
     "the YF-23's round flies SEST's figures on SEST's model block now; " + ONE_AIM424,
     WRAPPED),
    (r"\bCAPTAIN LI\b|\bPOLITICAL OFFICER CHEN\b", RED_LINE_TEXT,
     "Red Line names no person on the Chinese side - its bible's Names rule - and its "
     "command-net reports speak as roles; " + RED_LINE_B1),
    (r"neither (coalition )?campaign places", RED_LINE_TEXT,
     "ALPHA is Collins Variant3 (Waller), the one hull no other mission places; Variant6 is "
     "Southern Reach's Rankin attachment; " + RED_LINE_B1, WRAPPED),
    (r"(each|every) campaign (is )?also (listed |comes |ships )?as an Open Allocation"
     r"|also as an Open Allocation version|each (also )?(listed )?(as|with) an Open Allocation"
     r"|Open Allocation sells everything|Open Allocation\"? versions? sells? ",
     PLAYER_TEXT + ["integration/campaign/setup/sest-setup.ps1"], TWINS_RETIRED, WRAPPED),
    (r"both (Japanese )?escorts (start|begin)s? (on (the|its|your) plot )?classified"
     r"|starts \*?The Other Picture\*? with both",
     RED_LINE_TEXT + PLAYER_TEXT, RL03_HELD, WRAPPED),
    (r"(carriers|allied aircraft|Type 901 and 903A)[^.\n]*\bno longer on sale"
     r"|No allied aircraft, carrier, amphibious ship or tanker is sold"
     r"|No carriers, amphibious ships, tankers or allied aircraft"
     r"|Allied escorts are on sale from the force allocation",
     PLAYER_TEXT + RULES_PAGES, FLEET_ON_SALE, WRAPPED),
    (r"Only ships, fighters and strike aircraft are offered"
     r"|the Wedgetail and the Triton are offered again"
     r"|replacement aircraft and escorts, with repairs"
     r"|there is \**no Seahawk, Wedgetail or Triton"
     r"|the Sovremenny and Luda are not\b"
     r"|on sale in the (north|south) only|; north only\b"
     r"|stay on sale where the story sells them"
     r"|Also on sale here|also sells the (allied fleet|People's Liberation)"
     # The Steam Installing card's step 4, written 21 Oct 2026 when the
     # versions were retired and true until step 2 (review of that day).
     r"|the story releases your forces as it goes",
     WHOLE_ROSTER_TEXT, WHOLE_ROSTER, WRAPPED),
    (r"switched off parts of other mods' code|until their authors update"
     r"|falls back to its original order handling",
     PLAYER_TEXT, OTHER_MODS_BACK, WRAPPED),
    (r"radio (midcourse |command )?retargeting|radio midcourse",
     REDBACK_TEXT + PLAYER_TEXT, REDBACK_FF, WRAPPED),
    (r"MH-60R supports remain visible|use the lower (Hellfire|missile) seats",
     REDBACK_TEXT + PLAYER_TEXT + ["docs/campaigns/*/test-card.md"], REDBACK_SEAHAWK, WRAPPED),
    (r"RedbackH60|\btank points?\b|\bin the tanks' place\b"
     r"|MH-60R[^.\n]*\b(pods?|LAU-3s?|19-tubes?)\b(, which)?[^.,;:\n]{0,30}\b(on|from|in) "
     r"(the|each|its) (inboard|inner) pylons?\b",
     REDBACK_TEXT + PLAYER_TEXT + ["docs/campaigns/*/test-card.md"], REDBACK_LAUNCHER, WRAPPED),
    (r"seeker[^.\n]{0,30}\b(switch\w*|turns?|turning|searching)\b[^.\n]{0,12}\b[38] (NM|nautical miles?)\b"
     r"|TerminalApproachDist=[38]\b",
     REDBACK_TEXT + PLAYER_TEXT + ["docs/campaigns/*/test-card.md"], REDBACK_SWITCH_ON, WRAPPED),
    (r"Deceleration\W{0,2}[^.\n]{0,12}?\b0\.[28]\b|\bg per second\b|\bfraction per second\b"
     r"|450[ -](kt|knots?)\b[^.\n/]{0,12}\b(climb|loft)|\b(climb\w*|loft\w*)[^.\n]{0,12}\bat 450[ -](kt|knots?)"
     r"|450-knot phase ceiling|\bloft cap\b|MaxLoftVelocity=450\b",
     REDBACK_TEXT + PLAYER_TEXT + ["docs/campaigns/*/test-card.md"], REDBACK_SPEEDS, WRAPPED),
]


def main():
    hits, files = [], set()
    for pattern, globs, why, *opt in STALE:
        rx = re.compile(pattern, re.I)
        wrapped = WRAPPED in opt
        seen = set()
        for g in globs:
            for path in sorted(ROOT.glob(g)):
                if path in seen or not path.is_file():
                    continue
                seen.add(path)
                files.add(path)
                lines = path.read_text(**CODEC).splitlines()
                for n, line in enumerate(lines, 1):
                    m = rx.search(line)
                    if not m and wrapped and n < len(lines):
                        # A Markdown paragraph wraps, so the phrase may run on
                        # to the next line. Only a match that crosses the
                        # break counts here; one wholly on the next line is
                        # reported there.
                        head = line.rstrip()
                        m = next((x for x in rx.finditer(head + " " + lines[n].strip())
                                  if x.start() < len(head) < x.end()), None)
                    if m:
                        hits.append(f"   {path.relative_to(ROOT)}:{n}: '{m.group(0)}' - {why}")

    print(f"checked {len(STALE)} retired phrase(s) across {len(files)} file(s)")
    if hits:
        print(f"\n{len(hits)} retired claim(s) back in shipped text:\n")
        print("\n".join(hits))
        sys.exit(1)
    print("no retired claim appears in any builder, README or emitted file")


if __name__ == "__main__":
    main()
