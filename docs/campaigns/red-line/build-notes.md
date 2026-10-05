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
| Campaign | `campaigns/sest-red-line/` — 6 missions, 4 story pages, 46 files |
| Browser copies | every mission again under `missions/Red Line/` (31 files) |
| Placed units | 69; RL05 and RL06's 12 positions proved against the coastline extract, RL01–RL04's 22 stations used as authored (below) |
| Mods reached | 44 directly (`coverage.md`); the pack union with the other two campaigns reaches all 168 enabled mods and SEST packs (the 148 Workshop mods in the load order plus the 20 SEST source packs) |
| Points | 560 across six missions; opening budget 1,000 (Supported 1,250 / Veteran 850), cap 1,500 (1,250 on Veteran) |
| The pack | `SEST_Campaign` now carries three campaigns and their Open Allocation twins, 676 files and 58 missions; the consolidated `SEST_Integration` was 766 files with Red Line (691 before), 1189 with the ported work (`../southern-reach/install-alignment.md`, §6), 1201 with The Twelve-Mile Line, 1203 on the 0.8.3 game files, 1265 with the combat systems (60 extend files, two systems files), 1257 once the PLAN Pack's own update took over its eight hulls, 1260 with the three campaigns' enemy rosters and their twins' copies, less the briefly retired Rafale F5 pack, 1264 with the Rafale F5 pack back (rebuilt on the French Air Force mod, 3758943352) and the four new mods, and 1266 with SETUP in the pack: the 4 October build, published as Workshop item 3812461539 |
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
- **Liaoning sails on 17 December, not 22 December.** Southern Reach's
  25 February signal has an air wing that "has flown seventy days", which is
  17 December to the day, and its 17 December intercept already has "the
  carrier" transiting. The 22 December page is the southern tasking received
  at sea, five days out; the 23 December sitrep's carrier movement from the
  Java Sea is a dated observation of the same passage.

## Canon review

Every text leaf here was read against the current Southern Watch and
Southern Reach text after the first build. What changed, and why:

| Where | Was | Now, and the text it answers to |
|---|---|---|
| RL04 brief, intent, objective, lose | "an allied submarine may be astern"; "any boat astern are the coalition's"; "Fire on nothing of the coalition's" | "a submarine may be astern"; "nobody has said whose the boat astern is"; "Fire on nothing but Meridian Harmony". RL02 and the bible leave GOLF unclaimed, and *Return Passage* names no shooter |
| RL04 brief | "your frigate on the southern flank" | "on the starboard quarter": the anchor is 9 NM east-north-east of Liaoning on a course of 300, and north-east of the coaster |
| RL04 lose | "the carrier is hurt" | "LIAONING is lost": the fatal is her loss, not damage |
| RL04 docstring, bible | "nothing here says which of the groups that was" | *The First Ship Through* places both: a Luda and a Type 071 withdrawing, an unacknowledged 054A. This group is neither, 370 NM from that box |
| 22 December page | Liaoning and her escorts "sail from the Java Sea today"; the protection group's "frigate, corvettes and research trawler" | received five days out (above); its destroyer is the flagship, "not to be lost", as the 25 February signal has it and as *Approaches* has the Type 052D commanding the group since October |
| RL05 docstring, bible | Southern Reach meets Hull 419 "for the first time" in *Cold Route*; the boat "the coalition will call ROMEO" | *Fujian's Shadow* already calls the Type 093B in the northern screen ROMEO, and may sink her. Hull 419 is the boat Southern Reach calls ROMEO; nothing says whether she is the northern one |
| RL05 lose | the boat classified or sunk | or a patrol aircraft down, which the fatal also ends it for |
| RL02 docstring, bible | the 12 November INTSUM sees "the enclave's supply routes" | it sees the Russian detachment's; the Chinese detachment on the same field is supplied the same way |
| RL02 intro, brief, win | the relief window opens "at dawn"; the Poseidon has "four hours" of the escort | before dawn (*The Open Door* is at 0450, "before dawn"); the Poseidon has flown the route since dusk, so "a night's recording" |
| RL01 brief, objective, win | "the Banda station", 22 NM down the track in the northern Molucca Sea | "her morning station, twenty-two miles down the track"; the Banda station is days south |
| RL03 brief, forces, lose | "Kai fishing boats"; the enclave field "380 miles"; "has fired on the convoy" | a Kai fishing boat and a stern trawler, as placed; 400 miles, as placed; "has sunk a ship of the convoy", the fatal |
| RL06 | "your frigate" throughout; "thirty-odd miles"; "fired on their aircraft" | the screen, since the window offers a frigate or a corvette; "some thirty miles" (29 NM); "their aircraft is down", the fatal |
| Bible, names | "the only person named is Rewi"; "no real unit is named" | no person is named in any page or briefing; real ships appear only where the coalition campaigns put them |

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

## Playability review

Each generated mission file was read against the builder's dry run and its
own brief. Distances are true nautical miles from the positions the files
write. Speeds are the files' own: `TelegraphVelocities` where a hull has one
(every submarine here), and for a surface hull without one, 5, 10, 15 and 20
knots at telegraph 1 to 4, capped at its `MaxForwardVelocity` - the game's
default ladder is not in any file, so that is an assumption the test card
checks. A Poseidon cruises at about 400 knots, a Triton at 310, a KJ-500 at
about 265.

| Mission | The main task | Distance, and time | Clock |
|---|---|---|---|
| RL01 | Classify ALPHA, then Fujian into her station box | 11.9 NM to the box edge: 48 min at telegraph 3, 22 at her 32 kn. ALPHA starts 12.4 NM astern of Fujian and 10.8 NM from Dipper 21 | 70 |
| RL02 | Hai Yang 7 into the northern roads | 13.4 NM: 54 min at telegraph 3, 67 at the brief's twelve knots. GOLF starts 24.7 NM from her, closing at 10 kn | 95 |
| RL03 | Three classifications, then the frigate into the north-west box | 13.0 NM after the stage: 26 min at 30 kn. The convoy is 64 NM from the frigate; the names come from the air | 75 |
| RL04 | Liaoning and the replenishment ship in the box, Meridian Harmony sunk | The group 8.9 NM: 33-36 min. The coaster 15.3 NM to her denied box: 46 min at telegraph 4, 40 at her 23 kn, 61 at 15. The frigate starts 8.5 NM from her | 80 |
| RL05 | Hull 419 through the barrier into the forward box | 9.7 NM, the box's near edge a mile past the racetrack line: 58 min at 10 kn, 97 at 6, 116 at 5 | 120 (was 80) |
| RL06 | The decoy on station at T+30, then the tender and Hull 334 in the holding box | The decoy starts at its circle's centre. The tender 9.1 NM: 36 min at telegraph 3. Hull 334 3.7 NM: 22 min at 10 kn, 44 at 5. Earliest win about T+36 | 80 |

**What changed, and why.**

| Where | Was | Now |
|---|---|---|
| Every red racetrack (RL01, RL02, RL04, RL05's Poseidon and Triton, RL06's Kiwi 05, RL03's F-35s) and RL03's KJ-500 | Two to five waypoints over the same two ends. An aircraft that reaches its last waypoint circles there, so each ran out in 16-42 minutes: RL05's barrier became an orbit 19 NM north of the boat's crossing at about T+29, and Kiwi 05 was circling 39 NM from the rendezvous at about T+23, before the rendezvous could count | The two ends and `\|Loop`, stock's own form (Senkaku Run's Tu-95RT): every patrol is flown until the clock runs out. The builder's `loop=True` refuses a ship, an unrouted aircraft and civil traffic, with its own tests |
| RL05's clock | 80 minutes: only ten knots reached the box in time, and a boat keeping off the plot at five timed out under the barrier | 120 minutes (timeout 0630) |
| Hull 419, Hull 334, the tender; ALPHA and GOLF | `RadarsActive=True`: a mast raised at periscope depth radiates, and ESM classifies an emitter | `False`, as every submarine in the stock missions starts. The screen is the one that radiates |
| RL04's GOLF | In the Restraint fatal. She spawns only if RL02 left her afloat, and whether the engine counts a unit that never spawned as destroyed is unproven: if it does, every player who sank her lost RL04 at its first second on every replay | Her own objective, *Boat*, scored 0/-40 and never fatal - the shape Southern Reach's *Last Ship South* gives its tanker "if she sailed". Restraint and its fatal are the Poseidon's |
| RL02's escort | 12.5 NM astern of the tanker with the threat ahead: a tanker at cruise running at GOLF opens that gap faster than a frigate at 30 knots closes it, and the brief has the tanker "in company" | 3.5 NM on the tanker's port bow, between her and GOLF, 21 NM from the boat (28 NM since October 2026) |
| RL03's air tasking | The Y-9 and the KJ-500 were on sale and no row in RL03 or after could fly them | A Recon row and cockpit: a Y-9 bought in RL02 or RL03, or a KJ-500, flies it. The brief, forces and builder text say so |
| RL01's brief | "A RAAF Poseidon and a Triton are over the group" | The Triton circles 44 NM south-west; the brief puts it there |
| The roster note on the Sovremenny | "north only; the windows enforce it" | "on sale in the north only; one already owned still sails": `TaskForceModeRequireEntireTaskForce` takes every owned hull south |

**Checked and sound.**

- *Stage order.* RL01's arrival trigger is disabled until ALPHA is classified;
  RL03's until all three hulls are; RL06's until the decoy is inside its circle
  with 1,800 seconds run. RL04's win is one trigger, box AND kill. RL02 and RL05
  have no stage.
- *The unseen fatals* name `Taskforce1Submarine1` and nothing else, and the
  classifying side is Taskforce2: the patrol aircraft (RL05's Poseidon and
  Triton, RL06's Kiwi 05) and, in RL05, HOTEL, the Virginia added under
  "Wider forces", whose sonar can classify the boat at any depth. The tender,
  the screen and the ship's flight cannot fail them.
- *RL04's race.* The win needs Meridian Harmony destroyed, so she reaches her
  denied box only if nobody stopped her, and a player who ignores her loses to
  the box (about T+46), not the clock.
- *Hold and Tight.* The game's own tooltip (`language_en/ui.ini` 1049): Hold
  disables weapon use, Tight allows self-defence only, Free engages any
  hostile. RL02's Tight frigate and RL03's Tight F-35s will not open fire
  unprovoked; every brief that says "set them free and..." is about Free.
- *Positions.* A Natural Earth extract of the north was cut again for this
  review and every unit, route leg (sampled every quarter mile) and trigger
  centre in RL01-RL04 is on water: the nearest are RL02's tanker leg 7.6 NM
  off Biak, RL04's ferry 8.9 NM off Ambon, RL01's tuna boats 10 NM off Mayu.
  RL05 and RL06 are proved by the build; RL06's cray boat is the nearest,
  10.3 NM off.
- *Rosters and rows.* `check_flights` passes, and every airframe on sale in a
  window has a row in that window it can fly: the Z-9C everywhere, the Y-9 in
  RL02 and RL03, the KJ-500 in RL03, the J-15 and J-15D in RL03.
- *Art.* Every path `campaign.ini` and the page and briefing XML name exists;
  `check_campaign_coverage.py` reports nothing dangling.

## Liaoning's replenishment ship

The Order to Withdraw sailed a vanilla `plan_ap_qiongsha` as "the
replenishment ship" - a troop transport standing in. SEST Replenishment now
ships the real class, so she is the Type 901 **Hulunhu**
(`plan_aor_type901` Variant1), the same hull Southern Reach names in Turning
North and Southern Cross, and the brief names her. She is a working supplier:
the screen could take stores from her at sea, at thirteen knots or less, at
the cost of time the withdrawal does not have. The window's "no rearming" is
the service between operations, which stays shut, and the next operation the
screen sails, The Quiet Side, rearms anyway; nothing downstream reads a
magazine this could fill. The victory's transit is authored at twelve knots
and did not change, and the builder's arrival solve passes with her in the
group.

## Checked here

- The build and the six gates on a clean rebuild: 58 builder tests; `build_pack.py`;
  `consolidate_packs.py`; `check_campaign_coverage.py` (106 mission files,
  1,520 placed references, 159/159 mods and packs, nothing dangling; after
  the ported work, 1,524 and 162/162);
  `check_load_order.py`; `check_dependencies.py`; `preflight.py` (every unit,
  air group, loadout variant and pylon store resolves).
- Every unit type and mod id in the six missions resolved through the build.
- The northern positions. There is no committed coastline north of 25 South,
  so RL01–RL04 use Southern Watch's pool rule, and the builder lists 22
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
- **RL04's race.** Meridian Harmony runs 15.3 NM to the edge of her denied box
  at telegraph 4: about 46 minutes if telegraph 4 is 20 knots. Her file has a
  23-knot maximum and no telegraph ladder; if she takes longer than the
  120-minute deadline (1.5 times the 80-minute window, since 4 October) the
  mission ends on the clock instead of the box.
- **Chinese rank insignia.** The game ships insignia and emblems for the United
  States, Japan and Australia only, so every rank's image field is empty and no
  navy emblem is named. How the commander screen draws that is unknown.
- **The briefing map's own-force label** takes the first hull in a cluster, so
  RL04's reads "TYPE 054A P5 x5" for the frigate, Liaoning and the rest, and
  RL02's "TYPE 054A P5 x4" for the frigate, the tanker and the flight.
- **RL06's card** rings the decoy station, the first area the mission scores,
  as Southern Lifeline's and Cook Strait's cards ring their windows.
- **Names the game will show.** ALPHA is `ran_ssg_collins` Variant6; a full
  identification shows that hull's name, which no text uses. GOLF is
  `usn_ssn_virginia_2027`; her class is what a classification shows, and no
  page says whose she is. Meridian Harmony and Austral Compliance fly Panama.
- **Hai Yang 7 in RL04** is in company and scored by nothing: the group's
  orders are about the carrier, the coaster and the coalition.

## Open Allocation (27 September)

The campaign is also listed as "Red Line - The Other Watch - Open Allocation",
which offers the whole roster at every open force-allocation window (the Y-9,
KJ-500, J-15 and J-15D are on sale at RL01) and is otherwise this campaign,
line for line, loading these missions by path. Why a twin and what it changes:
Southern Watch build notes, "Open Allocation"; test card 6G there.

## Same-nation discount (28 September)

The campaign now carries Pacific Strike's 20% same-nation discount
(`SameNationUnitDiscount=0.2`), in its Open Allocation twin too. Every unit on
its roster is registered to China by its squadron or hull variant, so the
discount covers all of it. Southern Watch build notes, "Same-nation discount";
test card G.6 there.

## Wider forces (28 September)

The campaign now draws on more of the enabled mods and packs (the count is in
`coverage.md`; 36 before). Three missions gained units, at stations of their
own; no victory or existing unit changed. Every coalition unit added is spared
(added to the mission's Restraint objective and its fatal entry), as the
campaign's first rule requires. RL03's Restraint text names the Growler; RL01's
Wedgetail is covered by its "not the aircraft", and RL05's HOTEL by its "Fire on
nothing" (her name is in the Unseen objective).

| Mission | Added | Why it is there |
|---|---|---|
| RL01 Trailing Contact | a RAAF E-7A Wedgetail (`e-7a-wedgetail`, its squadron from SEST RAAF Wedgetail), coalition, Hold, 114 NM south of the carrier; the Manado-Ambon airliner (`civ_a330` in Lion Air's livery), neutral | the coalition's air picture, which the brief says is watching; one more contact to identify before acting. Indonesia keeps domestic routes for its own airlines, and the A320 file has no Indonesian livery |
| RL03 The Other Picture | a RAAF No. 6 Squadron EA-18G with the F-35As (`SEST_Growler_NGJ_MALICE`), coalition, Hold, emitters off; the Sydney-Hong Kong A330 (Qantas), neutral | the escort the F-35As would have, listening rather than jamming (Hold does not switch a jammer off; `radars="False"` does); the daily service whose great circle crosses the box. Red combat is at the recon cap, 5. The brief now warns that fighters left free will find the Growler, and the lose text covers "an aircraft that never fired" |
| RL05 Under the Convergence | HOTEL, the US Navy Virginia-class boat of Submarine Rotational Force-West (`usn_ssn_virginia`, `us-submarines`), coalition, Hold, dived, crossing the passage line about 5 NM astern of the boat's start at about minute 90 | Southern Reach's TS08 already has her on the Western Australia rotation. Closest approach is about 12 NM to a boat making the planned 5 knots: heard coming, a hazard to a boat that lingers, not a wall. The Unseen objective names her |

Not done, and why:

- RL03's J-15s stay J-15s. They are the cockpits the player's purchased CAP
  flight takes; the roster sells J-15 and J-15D, so a J-20 there would never
  reach the game.
- A J-16 pair from the enclave field in RL02, and a YY-20A tanker in RL03,
  were built and taken out. RL02 is about the field being down to two days
  of fuel: launching two fighters to orbit is the opposite of the mission.
  Nothing in RL03 can take fuel from a tanker (no receiver in the J-15,
  J-15D, KJ-500 or Y-9 files).
- A Type 071 carrying the enclave detachment home in RL04 was built and
  taken out: this bible gives the Type 071 to the northern element, not to
  this commander's group.
- A New Zealand offshore patrol vessel on the Fiordland fisheries patrol in
  RL06 was built and taken out, for the reason Southern Reach took HMNZS
  Otago out of TS01: that campaign's story is that New Zealand's ships are
  not there, and this bible's rule is that real ships appear only where the
  coalition campaigns put them.

All the added units are the real types.

## Rivet Joint (30 September)

The RC-135V/W Rivet Joint mod joined the collection on 30 September, and
RL03 places one: a USAF 55th Wing RC-135V/W out of Tindal (`boeing-rc135`,
Squadron2), coalition, weapons Hold, on an east-west track 60 NM south of the
convoy and 100 NM from the frigate at 31,000 ft. It carries nothing - one
hardpoint with no stations - and three ESM suites (ELINT, COMINT, a radar
warning receiver), so there is no radar to switch off; its role is EW and
Recon, which the builder counts as passive, and red combat stays at the recon
cap. It is spared with the Growler: the Restraint objective names it, the
fatal entry covers it, and the intro, the brief and the forces list say it is
not a target. Its one fit, SIGINT, is that empty hardpoint; the mod ships no
name string for it (the picker would show MISSING TEXT, and
`check_campaign_coverage` reported it as dangling), so SEST Collection Fixes
supplies one, as it did for the MH-60R's Anti-shipLate. The campaign now
reaches 44 mods and packs (43 before) and its REQUIRED-MODS lists 35
hard-required (34).

Coordinated Strike Tool, subscribed the same day, is a code mod with one
`_info.ini` and no data files: a time-on-target planner on F8. It is excused
in `campaign_data.py` as Auto Time-on-Target was, and no mission may depend
on it. The 30 Sep snapshot still showed Auto Time-on-Target subscribed,
enabled and loaded beside it.

The same export brought Russian Navy 21's update (sensors, the 40N6/48N6
rounds, the 20380/20385/21956/11356/22350/11780 hulls). Nothing this
campaign places comes from it; the SEST Replenishment copies of its hulls
were rebuilt on the new files and `check_pack_fidelity` passes.

## Sea Power 0.8.3 (2 October)

The game updated to 0.8.3 (Southern Watch build notes, "Sea Power 0.8.3",
has the whole record). For this campaign: the rules page's Survived
Missions column is now filled by the game from `CrewSkillThresholds`
(1/4/9/16 as before, from the game rather than written in by the build);
the 198 stock units the pack fields that the update changed are all still
there, none renamed or removed; and nothing new is placed, since every unit
0.8.3 added is a 1960s-90s type. The pack is 1203 files and declares
0.8.3.

## Combat systems and the CIWS model (3 October)

Southern Watch's build notes, *Combat systems and the CIWS model*, have the
whole record; what it means for the red side. Every PLAN surface hull Red
Line puts the player in or against now names a combat system where it
declared none: the 054A `SEST_PLAN_Multirole` (Fast, 48 contacts, 3
worked), the 056A `SEST_PLAN_Compact`, the 052D `SEST_PLAN_AAW` (VeryFast,
120, 5), the 055 `SEST_PLAN_Cruiser`, the carriers `SEST_PLAN_Carrier`, the
Type 071 `SEST_PLAN_Amphibious` - clones of Euromod profiles under SEST
names, assigned by `#!extend` from the top of the order. The coalition
hulls facing them get theirs the same way (Ford, the 2027 Ticonderoga, the
Daegu and KDX-III, the French and the old Type 23), and the Hobart, Anzac
and Mogami name theirs on the hull. Submarines on both sides take none,
like every vanilla boat. The Type 730 and Type 1130 are on the 0.8.3 burst
model (anchors 55 and 60, were 85 and 102; the 1130 keeps its eleven
barrels' 11,000 rounds a minute), and the vanilla AK-630 the Luda and
Sovremenny mount reads the game's own retune again instead of a stale copy
four aircraft mods carried. The pack is 1265 files. Test card, 8A.

*The same afternoon* (Southern Watch build notes, *Seven mod updates and
0.8.4*): the PLAN Pack's own update gave every one of its hulls its own
combat system - the player's 054A reads ZKJ-5A (Fast, 64 contacts), the
052D ZBJ-1A, the 055 ZBJ-1B, the 056A ZKJ-5B - and retuned its Type 730 and
1130 itself (anchors 65 and 90, the 1130 with 2800-round volleys), so the
SEST profiles and retunes for that pack were retired by their guards; the
Type 071 (RL04) and the coalition hulls keep theirs. The Fujian in RL01 is
now the PLAN Pack's own hull, with the same air wing, and the roster credits
it so. The game is 0.8.4; the pack declares it and is 1257 files. Test card
8A.3, 8A.3a and 8A.4 are reworded for it.

*Evening* (Southern Watch build notes, *The first play test*): Red Line
ships `enemy_theater_roster.ini`, so the Situation button shows the
coalition the player faces - RAN, USN, JMSDF and RNZN blocks, the Maya as a
flagship, the Collins and Virginias as persistent boats. 1260 files.

*Late evening* (Southern Watch build notes, *Four new mods, the Chinese
loading tips, and the Rafale back*): nothing placed here from the four new
mods; the loading-screen tips are English again for every campaign. 1264
files.

## The Quiet Side at 95 minutes (4 October)

The tender is a surfaced merchant in a sea state 5, and with ships priced
for the sea (Southern Watch build notes, 4 October) the holding position
thirty miles west of the decoy station sat a mile past what 80 minutes
bought. The window is 95 minutes; the position, the half-hour decoy hold
and the boat's rules are as they were. Every Red Line mission now closes
its window with a message and is lost at 1.5 times the plan, as the other
two campaigns do.

## Routes They Can See: GOLF moved out (October 2026)

GOLF started 21 NM from the escort with her Mk 48s (27 NM) free. The
campaign-wide opening gate (`check_opening`, see the Southern Watch build
notes) missed her because her torpedoes sit only in `[TorpedoRoom]`; with
that read, she was the one boat in all three campaigns inside 25 NM. She now
starts 28 NM east of the frigate and still closes across Hai Yang 7's track.

