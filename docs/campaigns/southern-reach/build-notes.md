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
| Campaign | `campaigns/sest-southern-reach/` — 26 missions, 20 story pages, 178 files |
| Chapters | Southern Reach SR01–SR12 (6 Dec 2028 – 14 Jan 2029); Tasman Shield TS01–TS12 with the optional pair TS10A/TS10B and the optional TS11A (22 Jan – 2 Mar 2029) |
| Browser copies | every mission again under `missions/Southern Reach/` and `missions/Tasman Shield/` |
| Placed units | 413, of which 209 stations were proved against the coastline extract |
| Mods reached | 49 directly (`coverage.md`); the pack as a whole places or excuses every one of the 164 enabled mods and SEST packs (`tools/check_campaign_coverage.py`) |
| Points | 2,800 across the 23 mainline missions, +180 for the three optionals; opening budget 1,000 (Supported 1,250 / Veteran 850), cap 1,500 |
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

Every one of the 209 stations passed, and each mission's coverage note says
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

## After the first install: flags, circling airliners, the story pages

**No New Zealand flag.** The game's nation key is `NewZealand`, with no space
(`language_en/nations.ini`; `Settings_UI_General.ini` maps that key to the
flag art). This build wrote `New Zealand` on the two RNZAF bases and the two
New Zealand civil airfields, and the P-8 mod itself writes `New Zealand` for
its No. 5 Squadron RNZAF livery (and `South Korea` for its ROKN one). All
now use the game's keys: the bases and airfields in their own files, the
Poseidon through a patched copy of the P-8 mod's squadron table in SEST
Allied Fixes that changes only those two `Nation=` lines and refuses to
build if any other name in it is not a game key. The coverage checker now
fails any placed unit whose nation the game cannot resolve; across both
campaigns the only ones were these.

Shipping that squadron table meant SEST now supplies both text files the
game reads for the P-8, and the builder concluded the P-8 mod was no longer
used. It is: the aircraft file loads its airframe from
`aircraft/P8_Poseidon/Upgrade/`, which only that mod ships. Model folders
now count wherever they sit, not only under `assets/`, unless a stock unit
loads from the same folder (shared ground like `aircraft/materials/` credits
nobody).

**Airliners circling.** An aircraft with no route orbits its spawn, and one
that reaches its last waypoint orbits there. Every Southern Reach airliner
had no route. Each now names its destination (`airway=` in the module:
Sydney, Auckland, Hobart, Perth, Wilkins...) and the builder writes one
waypoint on that bearing, half again beyond what an airliner at cruise
covers in the mission's clock. A new build gate refuses any neutral civil
aircraft without a route that outlasts the clock. In the loose missions, 30
civil aircraft in 10 files ran out of route inside two hours;
`integration/missions/extend_civil_airways.py` appends one waypoint along
each one's last leg (nothing else in the file changes, and it is idempotent),
and `sync-sest.ps1 -RefreshMissions` now runs it after an import.

**The story pages.** The FICTION footer and INTSUM banner are gone; the
INTSUM carries a security marking instead. The deck log was rebuilt: the
heading sits clear of the margin rule, entries hang in a time column, the
type steps down until every entry fits (the old page silently dropped any
that did not), and the master's note is boxed with the signature set right.
The front page splits its two columns at a paragraph break where it can and
never strands a single line; a page whose text will not fit now fails the
build instead of losing its last paragraph. Both campaigns' opening pages
and in-game descriptions were rewritten; the Automatic SAR instructions and
the install notes left the campaign descriptions for the pack's own Mod
Manager entry.

## Notes the builder still prints

One closure note survives, on purpose:

> Search Datum: red Taskforce2Vessel1 (civ_fv_okean) is 21 NM from
> Taskforce1Vessel1, pointed away, with no waypoints and 0 NM of reach - set
> dressing unless it moves

That hull is *Nan Hai 24*, hove to with the airlink's crew aboard. She is the
datum: the victory box is drawn on her (`at_unit`, 3 NM), and the mission
fails if she is sunk. She is not meant to move.

## The group's replenishment ships are the real classes

SEST Replenishment ships the Chinese classes the campaign had been standing
in for, so the stand-ins are gone:

- **Empty Horizon.** The protection group's command element sailed with
  RE-power's Soviet-named *Boris Chilikin*, briefed as "a Russian oiler that
  visits" the fleet. It is the group's own Type 903A now, **Taihu**
  (`plan_aor_type903a` Variant1), and the brief, the forces line and the
  station say so. She is unarmed and at Hold; the Picture objective still
  reads only the frigate and the corvette.
- **Turning North** and **Southern Cross.** The Liaoning group's
  replenishment ship was a vanilla `plan_ap_qiongsha`, a troop transport the
  bible called "the Qiongsha replenishment stand-in". It is a Type 901,
  **Hulunhu** (`plan_aor_type901` Variant1) - the class built to keep station
  with the carriers - in both: `network#4`, which the Network objective
  classifies, and the neutral withdrawing hull under the ceasefire. The
  intel line, the win text, the brief and the forces line name her.
- **Great Australian Bight** keeps its *Boris Chilikin*: she sails with a
  Russian Udaloy, which is the class's own navy, and she was already credited
  to SEST Replenishment.

Red Line's Order to Withdraw puts the same Hulunhu with Liaoning in the Banda
in November, so the ship the player shadows north in January is the one the
other side took south.

## Tasman Crossing's window

The window before Tasman Crossing released the Super Hornet and the Growler
"because Williamtown's aircraft reach the mid-Tasman". 1 and 6 Squadrons are
Amberley's (the squadron files say "fwd Townsville", Southern Watch's
northern arrangement), and no SEST RAAF Bases air group holds either type. A
bought one flies from the only field the mission places, Williamtown, so the
note now says what is true in both senses: Amberley's squadrons, staged
through Williamtown.

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
| `integration/campaign/southern_reach/` | the campaign package: `__init__.py` (spec, calendar enforcement, variable audit), `tables.py` (modules, calendar, roster, task force, difficulties, commander), `lore.py` (20 events), 26 mission modules, `AUTHORING.md` |
| `integration/campaign/coast.py`, `geo/southern_theatre_coast.json`, `tools/make_coast_extract.py` | the coastline proof |
| `integration/campaign/build_pack.py`, `make_art.py`, `integration/missions/briefing_maps.py` | multi-campaign builder, art prefix/label, map focus and inset |
| `integration/raaf-bases/` | the two RNZAF bases |
| `docs/campaigns/southern-reach/` | this file, `campaign-bible.md`, `test-card.md`, `coverage.md` (generated), `required-mods-urls.txt` (generated) |

## Open Allocation (27 September)

The campaign is also listed as "Southern Reach - Tasman Shield - Open
Allocation", which offers the whole roster at every open force-allocation
window (the P-8, Triton, Wedgetail, F-35A, Super Hornet and Growler are on
sale at SR01) and is otherwise this campaign, line for line, loading these
missions by path. Why a twin and what it changes: Southern Watch build notes,
"Open Allocation"; test card 6G there.

## Same-nation discount (28 September)

The campaign now carries Pacific Strike's 20% same-nation discount
(`SameNationUnitDiscount=0.2`), in its Open Allocation twin too. Every unit on
its roster is registered to Australia by its squadron or hull variant, so the
discount covers all of it. Southern Watch build notes, "Same-nation discount";
test card G.6 there.

## Wider forces (28 September)

Asked for broad use of the collection without convoluting the missions, the
campaign now draws on more of the enabled mods and packs (the count is in
`coverage.md`; 41 before). Eight missions gained one or two units each, every
one at a station of its own; no victory, fatal entry or existing station
changed. Two objective texts widened to cover what was added: SR04's
Restraint now spares the Bear's tanker, and TS10A's Traffic names the French frigate.
The forces paragraph and brief of each mission say what is new. Every choice
had to be something the real navies and air forces would put in that water in
early 2029, and had to fit the bible; what failed either test is listed after
the table.

| Mission | Added | Why it is there |
|---|---|---|
| SR04 Macquarie Passage | Il-78 Midas 41 (`il-78`), red, Hold, 75 NM behind the Bear | the bible has always said the Bears come south "with a tanker behind them"; now one is. Restraint spares it with the Bear |
| SR07 Beneath the South | Il-78 Midas 42, red, Hold, 200 NM behind the Bear | the same; beyond every anti-air round the player can buy, since no objective covers it |
| SR08 The Gateway | Skier 95, an LC-130 of Operation Deep Freeze climbing out of Christchurch for McMurdo at 9,000 ft (neutral `usmc_kc-130j`, `us-naval-aviation`) | Christchurch is the US Antarctic Program's gateway and late December is its season |
| TS07 Southern Air Bridge, TS09 The Southern Convoy, TS11 Approaches | Texaco 61 and Texaco 71, USAF KC-46As (`kc-46a`) | tankers for the F-35As, on the Enhanced Air Cooperation rotation; in TS09 and TS11 the track stays outside the Type 052D's HHQ-9C (260 NM) for the whole clock, even with the 052D closing at 24 kn |
| TS08 Great Australian Bight | the Pacific Fleet corvette Aldar Tsydenzhapov (`rfn_cvt_20380_7-12` Variant3, `russian-navy-21`), with the Udaloy and the oiler, holding fire | Pacific Fleet Project 20380s deploy with the Udaloys. Hold, because her Uran-U reaches 140 NM and the bible keeps the Bight's surface escort to the Udaloy's 27 NM on purpose (section 3, now noting her) |
| TS09, TS11 | the Type 052D's Z-20F (`plan_z-20f`) | the destroyer's own anti-submarine helicopter; the 052D's file lists it for its deck |
| TS10A Northern Priority | FS Courbet, a French La Fayette-class frigate outbound from Devonport for Noumea, and her Panther (`cdg-modern-french-navy`, `french-helicopter-package`), both neutral | a warship that is not a threat: one more identification problem in the Gulf |

Stand-in, which player-facing text never names: a USMC KC-130J for the
ski-equipped LC-130 of the 109th Airlift Wing. The Il-78, the Project 20380,
the Z-20F, the KC-46A and FS Courbet are the real types.

Tried and taken out again:

- HMNZS Otago in TS01 (a River Batch 2 standing in for a Protector-class OPV)
  and an RNZAF NH90 on search-and-rescue in TS02 (a French NH90 TTH). The
  chapter card before TS01 gives New Zealand's contribution as No. 5
  Squadron, the airfields and "Commander Brand's plain signals about where
  its ships are not", and section 5 places no New Zealand helicopter. That is
  the story's point and it matches the RNZN's real crew shortages, so both
  came out;
- a reconnaissance drone over SR01's convoy and SR10's ice edge
  (`usn_ForpostR705`). A Type 054A has no way to launch or recover a
  fixed-wing drone of that size, and the one in the collection is a Russian
  Forpost that shows a Soviet flag;
- a Tu-214R electronic-intelligence aircraft over the Bight. It has no
  refuelling probe and no base within its range of that water;
- a KC-135 tanker in TS04 and TS11. The collection's KC-135 (`kc-135`) is a
  1957 KC-135A, a variant the USAF retired in the 1990s; TS11's tanker is a
  KC-46A, and TS04 has none, because the sitrep before it says Williamtown's
  fighters reach the middle of the crossing "and no further";
- an A380 for TS07's Sydney-Auckland airliner. The only livery that fits the
  Tasman is the UAE one, and the game has no UAE nation key, so it would fly
  with no flag (`check_campaign_coverage.py` refuses that); the A330 stays;
- the Z-20J (`planaf_z-20j`, `type-071-lpd`) as the 052D's helicopter. Its
  file hangs no stores and carries no radar or sonar, and the 052D's deck
  does not list it; the Z-20F has both and is listed.

The tankers are American because the RAAF's own, the KC-30A, is an A330 MRTT
and nothing in the collection models one; a USAF tanker in Australia is the
real Enhanced Air Cooperation arrangement.

The briefing charts name an unarmed aircraft more than 120 NM from the ships
in the corner ("OFF CHART: TEXACO 249 NM NNE" on TS09's chart) the way they
already named a far airfield, rather than drawing it: charted, TS09's tanker
made the convoy action a third of the size it had been (`integration/missions/briefing_maps.py`,
`off_chart`; tested in `test_build_pack.py`, BriefingChartSupport).

What it costs: every mod a mission places is one the campaign needs, so the
campaign's `REQUIRED-MODS.txt` lists more than it did (40 hard-required,
32 before). The pack as a whole needed all of them already.

## The Twelve-Mile Line (28 September)

Asked for "a defector escort from red to blue", the player chose a Southern
Reach optional mission and a warship's crew, and asked that it be realistic.
Three independent designs (realism first, mechanics first, story first) were
scored by three judges (a naval officer and maritime lawyer, the builder's
owner, the story editor); all three chose the mechanics design, "The
Twelve-Mile Line", with grafts from the other two. It is built to that card
(bible section 7, TS11A) with the judges' must-fix list applied.

**The story.** The night after Approaches, a Type 056A on picket leaves the
screen and runs for Eden; her captain and political officer hold the bridge
and engine room, the rest hold the operations room, and her weapons are made
safe. Canberra accepts her ship's company's request for protection. A Type
054A of her screen follows with Fleet headquarters' order that she "is not to
reach a foreign port". The player's detachment, on passage to Sydney, meets
her, does not fire first, defends her once the frigate shows hostile intent,
and brings her inside twelve miles, where the frigate will not follow. The
model is the Storozhevoy, November 1975: a split crew, a pursuer ordered to
stop her own ship short of foreign waters, force as the last resort near the
line. The ship goes back after the talks; the people are heard.

**Where it sits.** 27 February, between Approaches and Southern Cross, and
closed by Southern Cross. Earlier would contradict the group commander's 25
February signal, printed as sent in both campaigns, which accounts for his
ships and mentions no defection. Winning sets `TS11ADefectorSafe`, and
Southern Cross then opens with the spoiler identified from the defectors'
debrief; it changes no order of battle. The story page before it
(`07c_channel_sixteen`, Bluefin 31's relay of the call) sits in the main
chain, so it reports the request and nothing after it.

**Three builder features**, each emitting only stock keys, each tested
(`test_build_pack.py`, DefectorEscortFeatures) and documented in AUTHORING:

- *Waypoint orders.* A route point may carry orders; `AttackAtWaypoint` is a
  single scripted strike at one named unit (stock: 06 Raid on Lombok's Osa,
  at `OverrideWeaponStatus=Tight`). The frigate stays Tight - "self-defence
  only", the game's own tooltip - so she never opens on the RAN, and fires two
  and then four YJ-83A at the corvette and at nothing else. The builder
  checks the round is in her fit and the target is exactly one unit on the
  other side; the pack checker checks the target is a section of the mission.
- *`disable=`.* The corvette's weapons are off from the first second (stock:
  08 Defense of North Borneo, Trigger4, key for key). A hull disarmed this
  way is not counted as an escort by the closure gate.
- *`lift=`.* When the frigate reaches her firing position - the
  fire-control lock - Restraint's trigger is switched off and Bluefin 31
  says so: firing first costs Restraint; defending her after the lock does
  not.

**Where it departs from the winning card.** Restraint is scored, not fatal:
whether a Generated force inherits the anchor's weapons Tight is unproven,
and a Free escort killing the Z-9 in the first minute must not end the
mission before the player has decided anything (test card 6.3). No text
states an Approaches outcome, names a Chinese person, or gives the corvette a
name or pennant (Red Line bible, section 2). The airliner the card had is
left out: no livery in the collection flies Sydney-Hobart. The chart names
East Sale in its corner (`map_focus_nm=100`).

**Not merged: TS08A "The Defector".** A different defector mission was built
in another session, on `feature/tasman-shield-defector` (a Russian support
vessel off the Bight, between TS08 and TS09). It is not on this branch: the
request was a Chinese warship's crew, and one defector mission is enough. The
branch is left as it was.

**For a campaign in progress.** The mission and its story page add two
campaign entries after Approaches, which renumbers the three after them. A
Southern Reach campaign already past Approaches should be started again; one
before it is unaffected.

## Rivet Joint (30 September)

The RC-135V/W Rivet Joint mod joined the collection on 30 September, and
TS11 Approaches places one: Rivet 21, a USAF 55th Wing RC-135V/W
(`boeing-rc135`, Squadron2) on the same Enhanced Air Cooperation rotation as
Texaco 71, weapons Hold, homed on Williamtown (110 NM), on an east-west
track off Sydney at 31,000 ft. That is 348 NM from the Type 052D, outside
her HHQ-9C for the whole clock, and more than 120 NM from the ships, so the
briefing chart names it in the corner ("OFF CHART: RIVET 21") rather than
drawing it. It carries nothing - one hardpoint with no stations - and three
ESM suites, so there is no radar to switch off. The brief and the forces
list name it; no objective changed. Its one fit, SIGINT, is that empty
hardpoint; the mod ships no name string for it (the picker would show
MISSING TEXT, and `check_campaign_coverage` reported it as dangling), so
SEST Collection Fixes supplies one, as it did for the MH-60R's
Anti-shipLate. The campaign now reaches 50 mods and packs (49 before) and
its REQUIRED-MODS lists 41 hard-required (40).

Coordinated Strike Tool, subscribed the same day, is a code mod with one
`_info.ini` and no data files: a time-on-target planner on F8. It is excused
in `campaign_data.py` as Auto Time-on-Target was; Approaches' briefing
already says time-on-target is an advantage, never a requirement, and that
still holds.

The same export brought Russian Navy 21's update. TS08 places its Project
20380 corvette (`rfn_cvt_20380_7-12`); the file changed in its launcher
settings, not in what she carries, and every gate passes on the rebuilt pack.

## Sea Power 0.8.3 (2 October)

The game updated to 0.8.3 (Southern Watch build notes, "Sea Power 0.8.3",
has the whole record). For this campaign: the rules page's Survived
Missions column is now filled by the game from `CrewSkillThresholds`
(1/4/9/16 as before, from the game rather than written in by the build);
the 198 stock units the pack fields that the update changed are all still
there, none renamed or removed; and nothing new is placed, since every unit
0.8.3 added is a 1960s-90s type. The Side Globe jammer Varyag mounts is now
cloned from the game's own Side Globe. The pack is 1203 files and declares
0.8.3.

## Combat systems and the CIWS model (3 October)

Southern Watch's build notes, *Combat systems and the CIWS model*, have the
whole record; what it means here. The player's hulls now name the systems
the real ships carry - Anzac Saab 9LV with CEAFAR (`SEST_9LV_MLU`, VeryFast,
96 contacts), Hobart Aegis Baseline 9, Canberra, Arafura and Supply 9LV -
where the Anzac declared none and Supply declared None; the Anzac's Phalanx
is now vanilla's Block 1 definition. The PLAN hulls these missions field
get theirs by `#!extend`: the 054A `SEST_PLAN_Multirole`, the 056A
`SEST_PLAN_Compact`, the 052D `SEST_PLAN_AAW`, the 055 `SEST_PLAN_Cruiser`,
Liaoning, Shandong and Fujian `SEST_PLAN_Carrier`, the Type 071
`SEST_PLAN_Amphibious`, the Luda and Sovremenny vanilla's own; the
submarines (Kilo, Song, Yuan, 093B) none, like every vanilla boat. The
Type 730 and 1130 the PLAN ships defend themselves with are on the 0.8.3
burst model at anchors 55 and 60 (were 85 and 102), and the vanilla AK-630
and Phalanx the game retuned are read again on every hull that mounts them.
The pack is 1265 files. Test card, section 7.

*The same afternoon* (Southern Watch build notes, *Seven mod updates and
0.8.4*): the PLAN Pack's own update gave its hulls their own combat systems
(the 054A reads ZKJ-5A, the 052D ZBJ-1A, the 056A ZKJ-5B) and moved its
Type 730 and 1130 onto the 0.8.3 keys itself, at anchors 65 and 90, so the
SEST assignments and retunes for that pack were retired by their guards. The
Liaoning (TS09), the Type 071 and the Luda and Sovremenny keep theirs. The
game is 0.8.4; the pack declares it and is 1257 files. Test card 7.3a, 7.3c
and 7.6 are reworded for it.

*Evening* (Southern Watch build notes, *The first play test*): both
campaigns here ship `enemy_theater_roster.ini`, so the Situation button
shows the PLAN and Russian forces the missions place; every cable's
date-time group carries a four-digit year; the Rafale is retired from the
collection (nothing here placed it). 1260 files.
