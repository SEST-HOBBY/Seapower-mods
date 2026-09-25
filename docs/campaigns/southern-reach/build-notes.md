# Southern Reach — build notes

What was built from `campaign-bible.md`, where it departs from the bible, and
what has **not** been demonstrated. Read this with the Southern Watch notes
(`../southern-watch/build-notes.md`): everything established there — Task
Force Mode keys, the `IsFalse` spawn form, the `VariableCheck` reveal, depth
tokens, the air-tasking row filters, bases and airframe range — is inherited
unchanged. This file covers only what is new.

## What is in the pack

| | |
|---|---|
| Campaign | `campaigns/sest-southern-reach/` — 25 missions, 19 story pages, 170 files |
| Chapters | Southern Reach SR01–SR12 (6 Dec 2028 – 14 Jan 2029); Tasman Shield TS01–TS12 with the optional pair TS10A/TS10B (22 Jan – 2 Mar 2029) |
| Browser copies | every mission again under `missions/Southern Reach/` and `missions/Tasman Shield/` |
| Placed units | 392, of which 200 stations were proved against the coastline extract |
| Mods reached | 34 directly; the pack union with Southern Watch reaches all 159 enabled mods and SEST packs (`tools/check_campaign_coverage.py`) |
| Points | 2,800 across the 23 mainline missions, +120 for the optionals; opening budget 1,000 (Supported 1,250 / Veteran 850), cap 1,500 |
| Southern Watch | unchanged: every mission file, card, story page and `campaign.ini` under `sest-southern-watch/` is byte-identical. Three of its briefing maps (The Open Door, The First Ship Through, D8 The Long Perimeter) re-rendered because the map renderer now keeps two overlapping "REPORTED …" labels apart; nothing else on them moved |

Both campaigns ship in the one `SEST_Campaign` pack (and in the consolidated
`SEST_Integration` download). The pack `_info.ini` now names both; the pack
`REQUIRED-MODS.txt` and `LOAD-ORDER.txt` are the union, and each campaign
carries its own closure in `campaigns/<slug>/REQUIRED-MODS.txt`.

## Four things the builder learned to do

**1. Two campaigns from one builder.** `build_pack.py` used to be Southern
Watch: its title, art prefix, docs folder and browse folders were module
constants. They are now a campaign spec (`campaign_specs()`), and
`set_campaign()` swaps every campaign-scoped global in and out, restoring the
module defaults for any key a spec leaves unset. That last clause matters: the
first version left Southern Reach's map focus active while re-emitting
Southern Watch and silently redrew all 44 of its briefing maps. They were
restored from git and the defaults table was added; a rebuild now leaves
Southern Watch's tree clean, which is the check.

**2. A coastline where no mission had sailed.** Southern Watch places every
ship on a point some loading mission has already used. Nothing in this repo
had sailed the Southern Ocean, Fiordland, Cook Strait, the Hauraki Gulf or
the Bight, so there was no pool to snap to. `tools/make_coast_extract.py`
clips Natural Earth's 1:10m land and minor-islands polygons to the theatre
(100–180°E, 25–72°S), simplifies them at 0.006° (about a third of a mile),
and writes `integration/campaign/geo/southern_theatre_coast.json`: 111 rings,
12,167 points, 235 KB. `coast.py` answers "is this on land" and "how far to
the nearest coast", and `CoastPlacer` in the builder enforces:

| what | rule |
|---|---|
| an offshore station | on water, 2 NM or more from any coast |
| a `coastal=True` station (Buckles Bay) and a `snap="sea"` land unit (the Bass Strait rigs) | on water, any distance, each hull on its own check |
| a land unit (every RAAF/RNZAF base, the civil airports, the Macquarie station) | ashore at its authored coordinates |
| every route waypoint of a ship or boat | on water, 0.5 NM or more off |
| every trigger area centre (arrival boxes, stage areas, `arrive` resolvers) | on water, 1 NM or more off |

Every one of the 200 stations passed, and each mission's coverage note says
so. What this does **not** prove is that the game's own coastline agrees with
Natural Earth to within those margins; see the risks below.

**3. New Zealand.** No RNZN hull exists in the load order and none was
invented. New Zealand is represented by `usn_p8` Squadron6 flying as
**Kiwi 05**, two new land units in `SEST_RAAF_Bases` — `airbase_rnzaf_ohakea`
and `airbase_rnzaf_auckland` (Whenuapai), both `nation="New Zealand"` — and
the vanilla `airfield_small_1` standing in for Christchurch, Invercargill and
Hobart airports. The RAAF bases pack now writes `Nation=` from each base's
own record instead of hard-coding Australia.

**4. Maps that fit the theatre.** The Southern Watch briefing maps show
everything the mission places. In the south that put Hobart Airport on the
same chart as a station at 60°S, so `briefing_maps.render()` gained
`focus_nm` (a land unit more than that far from the force centroid is left
off the chart and reported as `OFF CHART`) and `inset_box` (the locator
inset's extent). Southern Reach draws at 350 NM focus with a southern inset;
Southern Watch keeps its defaults. The campaign backdrop places its compass
rose in the first corner with no mission mark under it, which for Southern
Watch is still the top right.

## Where the build departs from the bible

The bible's cards were written before a single position had been proved. The
builder's gates (standoff by role, reach, arrival reachability, escort
closure, the coastline) moved several of them. Each departure is commented in
the module; this is the list.

| Mission | Bible said | Built | Why |
|---|---|---|---|
| SR03 Search Datum | role `recon` | role `patrol` | the recon budget demands a red unit that can reach blue; the only red hulls are an unarmed trawler and the collector |
| SR09 Cold Route | Kiwi 05 at −48.6, 136.4 | −48.2, 136.3 | 7 NM from ROMEO; a fleet mission opens with nothing red inside 15 NM |
| SR10 / SR12 | Ka-31 "up" | Ka-31 on a two-leg AEW orbit | an aircraft with no route pointed away is set dressing to the closure check |
| TS02 Cook Strait | Kiwi 05 fixed from Ohakea | as designed, station moved to −41.70, 174.20 | 6 NM from TANGO |
| TS03 Chatham Watch | tender "alongside" | alongside, with a one-knot westward leg | a stopped red hull 85 NM from the force reads as set dressing; she casts off as the force closes |
| TS04 Tasman Crossing | two groups 40 NM apart in line ahead, bearing 60; `detachment=True` | two groups 30 NM apart *abeam* of the track, one authored box 20 NM ahead of the escort; whole force sails | a trailing group can never reach a box the leading group can; abeam, each is 25 NM from the box, which 12 knots covers. §4's table has no detachment for this mission and the card's flag was dropped in its favour |
| TS07 Southern Air Bridge | two airliners on the route | both re-pointed through the box | pointed away they were set dressing |
| TS08 Great Australian Bight | Collins "working the western sector" 45 NM off | Collins 25 NM west of the escorts | a protected hull must be within what its escort can steam in the clock (32 NM at 24 kn) |
| TS09 The Southern Convoy | bearing 20 | bearing 60, "the split point off Portland" | bearing 20 from the convoy runs into the Coorong coast at the solved distance |
| TS10B Southern Priority | centre −35.4, 137.3; tanker in Investigator Strait | centre −35.15, 137.9; tanker 14 NM from the Outer Harbor box; frigate 40 NM south-west | 60 minutes at the solver's 18 kn buys 13.5 NM; the box is where the bible put it |
| TS11 Approaches | Flagship objective `20,-10,Complete` | `20,-10,Fail` | a destroy objective that ends Complete pays its 20 points for nothing |
| TS02, TS06, TS12 | objective lists as on the card | a `Traffic`/`Neutrals` objective added beside `Ferries`/`Platforms`/`Ceasefire` | every mission needs one objective the neutral-loss rule fails; the `spare` objectives score the specific hulls |
| SR01 Southern Departure | Southern Endeavour's loss fatal | any convoy hull's loss fatal | the win needs all three; losing one left the player running out a clock they could not win |
| SR04 Macquarie Passage | `spare` the Bear and the tender | `spare` VICTOR too | "fire on nothing that has not fired" now scores a shot at the boat; she has to be alive for SR06 and SR07 |
| SR05 Empty Horizon | the collector at the command element's station | the collector on her own station | the Picture objective and `SR05GroupClassified` are the two warships, not any two of three |
| SR08 The Gateway | Lyttelton approach box −43.62, 173.05, "round Banks Peninsula" | −43.55, 172.90, 4 NM off Godley Head, "south-west across Pegasus Bay" | the first box was off the peninsula's north-east bays, 10 NM from the Heads |
| SR10 Southern Line | `spare` the trawlers and the research vessel | `spare` *Nan Hai 27*; a `Neutrals` objective | the neutral-loss rule already covers the neutral hulls; Restraint scores the collector the briefing names |
| SR12 Turning North | classify "the network", min 3 | classify the carrier, the replenishment ship and the collector (a list of refs) | any three of six would have written `SR12NetworkNamed` |
| TS09 The Southern Convoy | F-35A from East Sale | the fighters recover at Edinburgh; East Sale not placed | the builder homes a cockpit on the nearest field, and Edinburgh is 60 NM nearer |

None of these changes what a mission is about. The one that changes what it
feels like is TS04: "two groups thirty miles apart abeam of the track" instead
of "forty miles apart in line ahead"; the briefing was rewritten to match.

## The review pass

Before this was committed, five reviewers read every module against its
bible card, the authoring contract and the emitted files (one per six
missions, one for the cross-cutting chains: variables, calendar, roster,
names), and every finding went to a separate verifier told to refute it.
79 findings, 71 confirmed, 8 refuted. All 71 were applied. Two were the
builder's:

- A `classify` resolver now takes a list of station refs, so Turning
  North's Network objective and the variable it writes are the three named
  hulls of a six-hull formation, not any three.
- The neutral-loss terminal no longer cancels a `spare` objective whose
  hulls are neutral (Cook Strait's ferries, the Bass Strait platforms, the
  withdrawing group under the ceasefire): it was cancelling the objective
  in the same tick its own trigger scored it. Southern Watch has no such
  objective, so its files do not change.

The rest were the fiction against the data: a signal dated the day before
the attack it reports, a "sixty miles" that measured thirty, a New Zealand
officer who existed in neither the cast nor the lore (the Poseidon voice is
Squadron Leader Tane Rewi, RNZAF; the Navy's is Commander Tessa Brand), the
contractor's name (Austral Meridian Services, not Australian Maritime),
Search Datum's trawler (*Nan Hai 24*) confused with the collector (*Nan Hai
27*), the relief convoy bound for Wellington in one file and Auckland in
the next, a Yasen "last held" in a mission that never placed one, and a
destroy objective whose end-status paid its points unearned. The refuted
eight were reviewers' misreadings or the bible's own disclaimers; none was
left standing without a reason recorded in the workflow journal.

## Merged with the deploy branch

The deploy branch (`sest-dev/loving-bell-3cnvvw`) moved on while this was
built: helicopters now sit in their own `Helicopter` sections, the RAN's
Seahawks fly 816 Squadron's colours from a composed squadron table, the
Anzac fires Euromod's ESSM Block II, loadouts no longer show MISSING TEXT, and
the coverage checker learned three new checks. It was merged in, and the
three conflicts resolved: the coverage checker keeps both sides (the new
helicopter and loadout-name checks, run once per campaign), and two
Southern Watch briefing charts take this branch's label fix. Southern Reach
follows the deploy branch's conventions: every Seahawk is now attributed to
U.S. Navy 2027, which wins the unit file, and flies Squadron20 (816 Squadron
RAN) in the missions and the roster. Every pack was rebuilt from scratch on
the merged tree and the four gates pass. The catalog generator, which had
stopped running on the deploy branch (a hand-kept count one registration
behind, and a Korean faction it did not know), is fixed with another
session's one-line port and its count.

## Notes the builder still prints

One closure note survives, on purpose:

> Search Datum: red Taskforce2Vessel1 (civ_fv_okean) is 21 NM from
> Taskforce1Vessel1, pointed away, with no waypoints and 0 NM of reach - set
> dressing unless it moves

That hull is *Nan Hai 24*, hove to with the airlink's crew aboard. She is the
datum: the victory box is drawn on her (`at_unit`, 3 NM), and the mission
fails if she is sunk. She is not meant to move.

## What has not been demonstrated

Nothing in this campaign has been run in the game. Beyond everything the
Southern Watch notes list as unproven, these are new to this build and are
the order to test in (`test-card.md`):

- **The coastline is Natural Earth's, not the game's.** A 2 NM offshore
  margin at 0.006° simplification is comfortable in open water and thin in
  Cook Strait (12 NM wide), Backstairs Passage and the Colville Channel. A
  ship that spawns ashore, or a route that crosses a headland the extract
  rounds off, is the first thing to look for.
- **Authored approach boxes** at Lyttelton (SR08), Wellington (TS02), Sydney
  Heads (TS07), the Rangitoto Channel (TS10A) and Outer Harbor (TS10B) are
  1–6 NM from the coast by the extract. Whether the arrival trigger fires
  before the pilot station is a question for the game.
- **RNZAF fields as the player's fields.** A RAAF Poseidon is told it can
  recover at Ohakea and Whenuapai because the builder's range check accepts
  any blue field of the right kind. Whether the game's SAR and recovery
  logic agrees with a `nation="New Zealand"` land unit has never been seen.
- **`TaskForceModeDeploymentOptions`** (TS02, TS10A, TS10B) and
  **`TaskForceModeAirbasePrep*`** (TS07) are stock keys copied from the
  Pacific Strike campaign and are documented nowhere else. Their pairing with
  `RequireEntireTaskForce=False` is inferred.
- **A blue airliner as the objective** (TS07's Relief 21, `civ_a330` on the
  player's side with a route and an arrival box) has no precedent in either
  campaign.
- **A neutral warship** (TS12's withdrawing Type 054A, `Hold`, neutral side)
  is there so the neutral-loss rule punishes a shot at the ceasefire. Whether
  the player's own weapons-free escorts leave a neutral frigate alone is the
  game's call, not the file's; the briefing tells the player to keep them
  tight until the spoiler fires.
- **Surfaced-and-stopped** (TS03's TANGO at depth 0, telegraph 1, no route)
  relies on the AI diving when it detects the force. If it sits there, the
  first kill of the chapter is a gunnery exercise.
- **The service-window stages** (SR04 at 30 minutes, TS02 at 25 minutes)
  are the Southern Watch `03 Lifeline` trigger shape and were verified there
  only as files.

## Files

| | |
|---|---|
| `integration/campaign/southern_reach/` | the campaign package: `__init__.py` (spec, calendar enforcement, variable audit), `tables.py` (modules, calendar, roster, task force, difficulties, commander), `lore.py` (19 events), 25 mission modules, `AUTHORING.md` |
| `integration/campaign/coast.py`, `geo/southern_theatre_coast.json`, `tools/make_coast_extract.py` | the coastline proof |
| `integration/campaign/build_pack.py`, `make_art.py`, `integration/missions/briefing_maps.py` | multi-campaign builder, art prefix/label, map focus and inset |
| `integration/raaf-bases/` | the two RNZAF bases |
| `docs/campaigns/southern-reach/` | this file, `campaign-bible.md`, `test-card.md`, `coverage.md` (generated), `required-mods-urls.txt` (generated) |
