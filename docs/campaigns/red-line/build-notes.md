# Red Line — build notes

What was built from `campaign-bible.md`, which builder features it relies
on, and what has **not** been demonstrated. Read this with the Southern
Watch and Southern Reach notes (`../southern-watch/build-notes.md`,
`../southern-reach/build-notes.md`): Task Force Mode, the air-tasking rows,
the `IsFalse` spawn form, bases and airframe range, and the coastline proof
are theirs and are not repeated.

## What is in the pack

| | |
|---|---|
| Campaign | `campaigns/sest-red-line/` — 6 missions, 4 story pages, 44 files |
| Browser copies | every mission again under `missions/Red Line/` (31 files) |
| Placed units | 62; RL05 and RL06's 11 positions proved against the coastline extract, RL01–RL04's 23 stations used as authored (below) |
| Mods reached | 35 directly; the pack union with the other two campaigns still reaches all 159 enabled mods and SEST packs |
| Points | 560 across six missions; opening budget 1,000 (Supported 1,250 / Veteran 850), cap 1,500 |
| The pack | `SEST_Campaign` now carries three campaigns, 638 files and 57 missions; the consolidated `SEST_Integration` is 766 files (691 before) |
| The other campaigns | every mission file, story page and `campaign.ini` of Southern Watch and Southern Reach is byte-identical. Nine of their mission cards changed, on purpose (below) |

The code is `integration/campaign/red_line/`: `__init__.py` (the spec, the
calendar check, the variable audit), `tables.py` (modules, calendar, roster,
Task Force settings, commander, air-tasking rows), `lore.py` (four pages) and
`rl01_*.py` … `rl06_*.py`. The builder picks the package up by itself.

## The builder features it uses

Each of these was added to the builder for this campaign, with its own tests,
in the commits before this one.

| Feature | Where |
|---|---|
| A third campaign registers itself; it must name its own `DOCS_DIR` and `COVERAGE_DOC` | the spec; `docs/campaigns/red-line/coverage.md` is generated here |
| **`unseen`** resolver and fatal: stock's `UnitClassified` with `Condition_Taskforce=Taskforce2` on the player's own units | RL05 (Hull 419), RL06 (Hull 334). Each has an `Unseen` objective and a fatal entry, so the coalition classifying the boat fails the objective and ends the mission |
| A victory **`also`** term of kind `destroyed` | RL04: the win is Liaoning and the replenishment ship in the box *and* Meridian Harmony gone. No incident can follow a win |
| A **passive red unit may start in company** (weapons Hold, every role non-combat) | RL04: `ran_ms_super_p`, `Role=Spy`, starts 5 NM from Liaoning, inside the escort role's 6 NM standoff |
| An **armed submarine counts as an escort** in the closure check | RL06: the tender's nearest escort is Hull 334, so the frigate's decoy station is 37 NM east where the story puts it, not within the 32 frame-miles the gate used to demand |
| Story pages **labelled from this side**: `note_label` | every page: COMMANDER'S NOTE, or FILE NOTE on the last. No page says ANALYST NOTE; there is no INTSUM, so no RELEASABLE TO COALITION PARTNERS marking |
| Only the **map tiles the events use** are written | four signals, so `bkg_tile_message.png` only; nothing dangles |
| The roster file **names its own source** | `player_task_force_roster.ini` says "edit red_line/tables.py" |

Two things it uses that were already there:

- **Per-campaign air-tasking rows.** Southern Watch's rows offer RAAF and US
  Navy fits (MurderHornetCAP, ASWPatrol) that no Chinese aircraft defines,
  and the builder's flight check refuses a row that offers a fit nothing in it
  can fly. `tables.py` has its own: `HELO` (ASWKiller/ASWHunter), `RECON`
  (ASW/ASWKiller/ASWHunter/AEW — the Z-9C matches the Recon filter too) and
  `CAP` (AirToAir/AirToAirIntercept).
- **Per-mission geography.** The spec is `pool`; RL05 and RL06 set
  `geography="coast"` and are proved against the southern extract.

## Where the build departs from the design

- **RL04 is on 27 November, 0310, not 28 November, 0510.** The ceasefire moved
  to 0000 on the 27th in both campaigns' current text, and the first convoy
  sails on the 28th. The 22 November page's order now reads CEASEFIRE TAKES
  EFFECT 0000 ON 27 NOVEMBER, acknowledged at 2304 on the 26th. The brief adds
  Southern Watch's own line that not every group has acknowledged: this one
  has.
- **RL04's coaster starts in company** (5 NM from the carrier, not 6.5 NM out),
  and the win requires her sunk through the `also` term instead of the design's
  70-minute timing workaround. Her denied box is 15 NM down her track.
- **RL06's decoy is 37 NM from the tender**, and Invercargill Airport is not
  placed: a red airfield draws on the briefing map as "reported ground forces",
  and Kiwi 05 flies on the engine's unlimited fuel without one. The boat starts
  ten miles north of the holding position.
- **RL01's patrol aircraft and RL03's frigate** were moved a few miles so the
  briefing map's labels do not print over each other.
- **The commander's default name** is *Cao Mingyuan*, not the design's. It is
  built from the game's own `[Names_China]` pool (Cao, Ming, Yuan) and was
  searched for on 26 September 2026 — in English, as 曹明远, and with "navy",
  "PLA", rear admiral, captain and carrier group — with no naval officer of
  that name found; the matches are civilians (a court officer, a county
  official, a patent inventor, academics). The player can change it, and no page or briefing uses it.
- **No Russian prequel dispatch.** Southern Watch's D4 covers that side.
- **RL05's cruise ship** is *MV Southern Light*, not Southern Reach's *Polar
  Horizon*, which that campaign has northbound on the 18th.

## Changes to the shared renderers

Found by looking at every Red Line card and page, and fixed where the fault
was, not only on this campaign's art:

| Change | Effect on the other campaigns |
|---|---|
| A mission card's chart is framed on the whole objective ring, not only its centre (`plot_extent`) | nine shipped cards whose ring ran off the chart are re-framed: Southern Watch 04, O4, C2; Southern Reach SR10, SR11, TS01, TS04, TS06, TS11. Every other card is byte-identical |
| A card title whose widest line would reach the chart is set smaller (`title_size`) | CONVERGENCE crossed the chart's frame; BROKEN WAKE (C2) and HOME WATERS (TS01) touched it. Both cards are in the nine above |
| The campaign backdrop keeps the campaign marks 100 px from the top and 150 px from the bottom, where the title is | only Red Line's chart (the equator to 47 South) is re-framed; both other backdrops are byte-identical |
| Meridians east of 180 are labelled west; a parallel's label that would print over the meridians' row is left off | Red Line only |
| The briefing map keeps a pennant's number (*Hull 419*, not *HULL*); Red Line landmarks (Kai Islands, Manipa Strait, Milford Sound) | no other map changed |

## Checked here

- The build and the six gates on a clean rebuild: 55 builder tests; `build_pack.py`;
  `consolidate_packs.py`; `check_campaign_coverage.py` (106 mission files,
  1,520 placed references, 159/159 mods and packs, nothing dangling);
  `check_load_order.py`; `check_dependencies.py`; `preflight.py` (every unit,
  air group, loadout variant and pylon store resolves).
- Every unit type and mod id in the six missions resolved through the build.
- The northern positions. There is no committed coastline north of 25 South,
  so RL01–RL04 use Southern Watch's pool rule, and the builder lists 23
  stations "used as authored". Every one of them, every route waypoint and
  every trigger area centre in those four missions was also checked against a
  Natural Earth extract of the north made for the purpose (118–145E, 16S–5N)
  and is on water: the closest is RL02's arrival box, 8.8 NM off Biak. That
  extract is not in the repo, so the build does not repeat the check.
- Every card, page, backdrop and briefing map was looked at.

## What has not been demonstrated

Nothing in this campaign has been run in the game. In the order to test
(`test-card.md`):

- **The AI at Hold and Tight.** RL01 and RL04 start the player's ships at
  weapons Hold with a Poseidon overhead; whether a ship left Free fires on it,
  and whether a Hold ship can be ordered to fire on one target, decide both
  missions. RL03's Tight F-35s against a KJ-500 is the other half.
- **The `unseen` trigger.** It is stock's shape (Operation Polar Fury 1985
  Trigger5), never seen fire in a SEST mission. It measures *classification*,
  not detection: a boat detected and never classified passes.
- **RL04's race.** Meridian Harmony runs 15 NM to the edge of her denied box at
  telegraph 4. The file gives her no speed key; if she takes longer than the
  80-minute clock the mission ends on the clock instead of the box.
- **Chinese rank insignia.** The game ships insignia and emblems for the United
  States, Japan and Australia only, so every rank's image field is empty and no
  navy emblem is named. How the commander screen draws that is unknown.
- **The briefing map's own-force label** takes the first hull in a cluster, so
  RL04's reads "TYPE 054A P5 x5" for the frigate, Liaoning and the rest.
- **RL06's card** rings the decoy station, the first area the mission scores,
  as Southern Lifeline's and Cook Strait's cards ring their windows.
- **Names the game will show.** ALPHA is `ran_ssg_collins` Variant6; a full
  identification shows that hull's name, which no text uses. GOLF is
  `usn_ssn_virginia_2027`; her class is what a classification shows, and no
  page says whose she is. Meridian Harmony and Austral Compliance fly Panama.
- **Hai Yang 7 in RL04** is in company and scored by nothing: the group's
  orders are about the carrier, the coaster and the coalition.
