# Southern Watch — disposition of the review of 057405fe

The independent review (`SEST_Southern_Watch_Full_Review_057405fe.md`, 22
September 2026) and the second-pass reader findings that preceded it were
taken finding by finding against the branch as it now stands. Every row below
was checked on the **built files at `809d153a`** (branch
`sest-dev/loving-bell-3cnvvw`), not on the source that produces them, using
the commands in "How this was checked" at the end.

Vocabulary, as the brief asked for it:

| Disposition | Meaning |
|---|---|
| **fixed** | the defect is gone from the built files, and the row says which file and trigger to look at |
| **partly correct** | the finding was right about some of what it said; the row says which part and what was done |
| **not reproduced** | the built files at the reviewed commit or now do not show what the finding describes |
| **accepted** | the behaviour is real and is kept on purpose, with the reason |
| **engine test** | the files are consistent and the mechanism is native syntax, but nothing here has watched the game do it; the test card names the run |

A note on what "fixed" is worth here. Nothing in this repository has been run
in Sea Power. "Fixed" means the emitted predicate now says what the briefing
says and a counterexample that used to satisfy both no longer does. Whether
the engine evaluates it the way the stock missions imply is the engine test
column, and every one of those is on the test card.

Commits since the reviewed snapshot, oldest first:

```
7759da5e  recovery is checked against the files, anchors are the player's ships
c1216c87  the campaign's civilian thread cannot die and sail on
ee5fff66  SW11 and SW12 contested, O1's promise kept, allied aircraft are allied
0297095a  the service window pays for the rearm, and the schedule is told
87fbd9a4  the eight dispatches keep their contracts
7454dc5b  Euromod-South Korea Navy in the load order; a deck is what a hull embarks
52703d9a  Southern Cross, Borrowed Shield, Weather Alternate, Broken Wake
809d153a  The Missing Beacon's helicopter comes home to the ship
```

## 1. The review's priority findings

### P1 — aircraft recovery validated against the wrong contract

**Fixed, with the landings themselves an engine test.**

`build_pack.py` now resolves the two files' own words before it homes an
aircraft. `deck_fit()` reads the deck's `AircraftSupported` list and the
airframe's `CarrierCapable` line through `#!alias`, returns *compatible*,
*undeclared* (a fixed-wing type with no `CarrierCapable` line on a deck with
no list — allowed, reported, and on the test card) or *incompatible*
(`CarrierCapable=False`, or a deck whose list leaves the type out).
`assign_home_bases()` prefers compatible decks, then fields over undeclared
carriers, treats `UnitType=VTOL` as fixed-wing that may use a deck naming it,
and fails the build for a player aircraft with nowhere to go rather than
handing it `UnlimitedFuel`. `check_purchased_recovery()` runs the same test
for every roster type a mission's flight rows admit, against that mission's
decks within the type's radius, so a purchased replacement is covered as well
as the authored placeholder. `deck_size()` falls back to the airframes an
`[AirGroup]` embarks when a hull writes no `AircraftCapacity` (the five vanilla
Soviet hulls and every Korean hull declare their decks that way).

Census of the built files: **102 player aircraft in 26 missions, 102
compatible, 0 undeclared, 0 incompatible, 0 without a home, 0 on
`UnlimitedFuel`**. The fourteen conflicts the review listed:

| Review row | Now | Where to look |
|---|---|---|
| SW03 two CH-53s → Choules | Both home on **Canberra**, whose deck list names `usmc_ch53_standalone` (the RAN Fleet pack's own hull; `build_fleet.py` `deck` key) | `Southern Watch 03` Aircraft1/2 `HomeBase=Taskforce1Vessel3` |
| SW04, O1 MH-60R → Arafura | Arafura's list now names the RAN helicopter family (same pack, same key); SW04 and O1 home the Seahawk on her | SW04 Aircraft1, O1 Aircraft1 |
| SW05 red Z-21 → Type 071 | Z-20J and Z-21 removed from SW05 | SW05 has no Taskforce2 helicopter |
| SW08 F-35As → Nimitz (`CarrierCapable=False`) | Both home on **Langgur strip** (`airfield_small_1`, a blue land unit) | SW08 Aircraft2/3 `HomeBase=Taskforce1LandUnit1` |
| D1 four helicopters → Italian FREMM | Merlin on the Type 45, Wildcat on the Type 23, Sea Lynx Mk88 on the F124, NH90 on the Karel Doorman; the two orphan types were replaced by types the rotation's decks list | D1 Aircraft1–4 |
| D3 Panther, Cougar, AB212 → Horizon | All on Charles de Gaulle, which declares no list (helicopter on an unlisted deck is compatible by the vanilla convention) | D3 Aircraft4/5/7 |
| D3 Harrier: VTOL skipped, finite fuel, no home | VTOL handled; Harrier homes on Charles de Gaulle | D3 Aircraft6 |
| D2 E-3G, KC-10 → carrier | Both home on **RAAF Scherger** (land unit) | D2 Aircraft1/2 |
| D4 land bombers → carrier | Tu-160, both Tu-95, Su-30SM2 and J-16D home on the dispersal field (`wp_airbase_modern`); Su-57, MiG-29K and Su-33 stay on Kuznetsov, whose files admit them | D4 Aircraft1–8 |
| D6 land types → carrier | F-15EX, F-16CM and the three bombers home on the forward strip; YF-23s, Rafale M and RQ-180 on Ford | D6 Aircraft1–9 |
| D7 F-117, Tornado, B-52G → carrier | All three home on the exercise field (`airfield_a-10`); the U-2 stays on Kitty Hawk because its file says `CarrierCapable=True` | D7 Aircraft3–6 |

Engine test: the landings named on the test card (Lynx on Sejong the Great,
Harrier on Charles de Gaulle, U-2 on Kitty Hawk, VH-3D on Nimitz, F-35A on
Langgur). A resolving `HomeBase` is the file's claim, not the engine's.

### P1 — SW08 mixes incompatible deployment assumptions

**Fixed by choosing the model the guide describes for a supplied package,
and proving it statically; the launch is an engine test.**

The Open Door is a *blank-generation* mission: the guide says a campaign entry
with no `TaskForceModeMissionGenerationType` launches the authored mission
with no persistent units. The campaign entry (`campaign.ini` `[Mission24]`)
now carries no generation type, `IncludesTaskForce=False`,
`IncludesAirwing=False`, no builder, **no tasking rows and no airbase
preparation**, and a `MissionSpecialNote_en` that says nothing of the player's
force sails. The F-35 pair keeps `StrikeLongRangeStealth` and carries no slot
tag, so no row can replace its fit; the Growler flies from Nimitz with
`MurderHornetSEADHeavy`; the F-35As, both KC-130Js and the conditional KC-46
home on Langgur strip, the blue land unit the review found missing. The
builder now refuses a blank mission that declares flights or airbase prep,
and refuses a slot tag on one.

The three facts the review asked to resolve together: (1) the CAP row that
excluded the strike fit no longer exists; (2) a blue airfield exists and is
the recovery base; (3) the entry's omitted generation type is now the
deliberate model and the display flags agree with it.

Engine test: launch The Open Door from the campaign map and confirm there is
no deployment screen, the authored aircraft are present with their authored
stores, and the F-35As recover to Langgur. The "populated owned airwing"
case the review asked for does not arise under this model, which is the
point of choosing it.

### P1 — SW03 does not tie pickup and extraction to the same helicopter

**Fixed; the enable timing is an engine test.**

Rig Seventeen now builds one chain per lifter (`per_unit` stage): Trigger4
(Aircraft1 within 3 NM of the platform) enables Trigger5 (Aircraft1 in the
withdrawal box → victory) and Trigger6 (Aircraft1 destroyed → defeat, with
its own `StageLostMessage`); Trigger7/8/9 are the same chain for Aircraft2.
The review's counterexample — A at the platform, B in the box — no longer
satisfies anything: B's victory trigger is disabled until B has visited the
platform. Losing the aircraft that made the pickup is a defeat, not a
continuing mission. Neither CH-53 carries `JoinTaskForce` or a `CampaignTag`
any more (no mission in the pack does): they are Canberra's allocated lift,
and the shared-tag question is moot.

Engine test: the split case as written, and whether a trigger that ships
`Disabled=True` is enabled by `Action_EnableTriggers` promptly.

### P1 — three dispatches award the wrong arrival

**Fixed.**

| Mission | Now |
|---|---|
| D2 Flight Deck Day | The box *is* the carriers: Trigger4 is the VH-3D within 5 NM of `Taskforce1Vessel1`'s position (`PositionNM=30,0,-54`, the carriers' own coordinate) |
| D3 The Relief Ship | "Get both vehicles of the relief column to the distribution point": Trigger4 watches `Taskforce1LandUnit1,Taskforce1LandUnit2` with `MinimumUnits=2`; the helicopters are a separate Lift objective (Trigger5); the column drives the road on `Waypoints` |
| D8 The Long Perimeter | "Get the relief truck to the airstrip": Trigger4 watches the HEMTT (`Taskforce1LandUnit2`) alone, in a 3 NM box drawn on the strip; the civilian pickup has its own station and is in no arrival list |

`solve_arrival()` is now used only where the destination is genuinely a
bearing (convoy handovers); D2, D3, D8, O1 and C1 author their boxes.

### P1 — Coral Pioneer can die and still receive the living epilogue

**Fixed in every placement, and the other recurring hulls audited.**

Every core mission that places her requires her in the victory condition
(`Condition2` of Trigger4 names her section with `MinimumUnits=1`, ANDed) and,
where a win does not depend on arrival, ends the mission on her loss:

| Mission | Her section | Required by the win | Loss ends the mission |
|---|---|---|---|
| SW01 | Vessel2 | yes (Condition2) | no single-hull trigger: with her sunk the win cannot fire and the deadline ends it in defeat |
| SW02 | Vessel7 | yes (Condition3, with Kokoda Star as Condition2) | Trigger7 |
| SW05 | Vessel2 | not an arrival mission | Trigger8 |
| SW06 | Vessel4 | yes | Trigger9 |
| SW10 | Vessel5 | yes | Trigger8 |
| SW11 | Vessel6 | yes | Trigger9 |
| SW12 | Vessel3 | yes | Trigger7 |

The other merchants are unique per mission (Weipa Trader, Gove Provider, Kai
Trader, Milne Trader, Arnhem Trader, Kerema Trader…) so no other named hull
can be sunk and sail on; D2 no longer places her as a neutral. The two
allied warships that recur — Sejong the Great (O3 → SW06) and Stuart (C2) —
are handled by the campaign variable (a destroyed Sejong never sets
`O3ShieldJoined`, so SW06 never spawns her) and by a hull nothing else places.

Engine test: the paired saves (lose her in SW06 → the mission ends; keep her →
the next cast agrees).

### P1 — purchases with no deployment path

**Fixed.** The KC-46 is no longer sold (roster and every window); it appears
as allocated theatre support in SW02 and SW08 (SW08 conditionally, on
`O4LanggurStocked`). The finale window (`[Mission34]`) offers `usn_p8,
raaf_f-35a, usn_fa-18f_blk3, E7A_Wedgetail, raaf_mq-4c_triton, usn_mh-60r,
ran_opv_arafura, ran_ffh_anzac` against three rows — Ship's Flight (SAR),
Maritime Patrol (MPA/ASW/ESM/AEW) and **Combat Air Patrol (Fighter, 2
slots)** — with `TaskForceModeAirbasePrepAvailable=True` and RAAF Darwin
placed as the field. Every offered aircraft type matches a row, and
`check_purchased_recovery()` proves each has a deck or field within radius.
The Growler moved to the SW05 window so it exists before the mission whose
brief describes it; Collins, Supply, Choules, Canberra and Mogami left the
roster (no mission could deploy an owned one). Replacement hulls (Arafura,
Anzac) are sold at the finale so a costly SW11 is not a dead end.

Engine test: assign a bought F-35A to the SW12 CAP row and watch it appear,
fly and recover at Darwin.

### P2 — generated-force customisation versus named-hull scripting

**Fixed by adopting the guide's one-ship pattern.** Weapons Free (SW05,
renamed) is `TaskForceModeMissionGenerationType=Replaced` with
`TaskForceModeRequiredUnitType=Vessel` and `TaskForceModeMaxUnits=1`, and the
builder situation line says one ship of the player's choosing sails it. The
anchor carries no name (the builder now refuses a name on a generated anchor,
because the guide says the player's first ship replaces it), and the fiction
addresses "your flagship" / "you send one ship, alone". The magazine
objective still reads `UnitsAreOutOfAmmo` on `knm_nsm_1a` for
`Taskforce1Vessel1`; every hull the roster sells (Anzac, Hobart, Arafura)
carries NSM in its winning file, so no legal selection is a non-NSM ship.

Engine test: deploy an Arafura alone into SW05 and confirm the magazine
predicate reads her NSM cells. The same audit removed every anchor name in
SW01/02/04/06/09/10/11/12.

### P2 — SW09 proves a timed rendezvous, not continuous service

**Partly correct; the wording was made true rather than the mechanism
invented.** The stage is `UnitsInTheArea(Stalwart, Collins) AND Time=2100`
(Trigger4), which is what the native Lifeline trigger does and is not a dwell
counter. The briefing now says exactly that: "thirty-five minutes and it runs
on the clock, not on how much crossed the hose", and the withdrawal follows.
Staying surfaced remains a stated house rule. What the stage does buy is
real: it writes `SW09ServiceHeld`, and Common Sea's rearm is
`TaskForceModeRearmByVariableAND=SW09ServiceHeld,IsTrue` (the guide's own
key), with the consequence told to the player before SW09.

Engine test: leave and re-enter around 34/35/36 minutes, and whether a
disabled trigger's `Condition_Time` is absolute or restarts on enable.

### P2 — narrative consequences overstate the implemented state

| Item | Disposition | Evidence |
|---|---|---|
| SW06 success text promises the Triton back with the picture | **fixed** | `Taskforce1VictoryMessage`: "Whatever Sentry 06 brought back or did not, the convoy is where it is supposed to be" |
| O1 promises a better SW02 briefing with nothing wired | **fixed** | O1 Trigger4 (classify Torres Light) sets `O1BeaconFound`; SW02 Trigger12 `VariableCheck` reveals `Taskforce2Submarine1` as Classify with `O1BeaconFoundIntel` |
| C1 declares Lae Provider sunk whatever SW02 did | **fixed** | C1 names MV Kerema Trader, a hull that sailed independent and appears nowhere else; the card says plainly it is offered whatever happened |
| SW12 "do not fire" represented by destruction only | **fixed by narrowing** | `Objective_Ceasefire=Do not sink a withdrawing ship`; the trigger is `UnitDestroyed` on the two withdrawing hulls |
| Sitrep says Saturday, SW11 says Friday | **fixed** | the built texts contain "Friday" only (SW11 ×5) and no "Saturday" |
| Nine knots in the log, eleven in SW12 | **fixed** | SW12 says nine knots throughout; the box is solved with `transit=9` |
| Mercer at rank 5 while called Commodore | **fixed** | `commander_settings.ini`: the player is Commander **Morgan Reid** (`CommanderStartingRankLevel=5`); Commodore Alex Mercer is the supervising commander in every signal |
| D4 "restraint" is a fighter-survival threshold | **fixed** | `Objective_Restraint=…harm nothing of the coalition's`; Trigger6 fails it on any coalition unit destroyed (`spare` resolver) |
| D5 scores pads, not intercepts | **fixed by making the brief honest** | `Objective_Serial` is a `Fail`-status task, the ARRW sentence is gone, and the brief says what is scored |
| D7 "recover the exercise aircraft" protects only the U-2 | **fixed** | `Objective_Recovery=Bring Dragon 41 home`; `Objective_Umpire` names the rule (the tanker is out of play, Trigger6) |
| D1 "escorts intact" tolerated five losses | **fixed** | Trigger5 fails Escorts on the first loss (`MinimumUnits=1`) |

### Every mission, reviewed — the per-mission column

| Mission | Review's next action | Now |
|---|---|---|
| SW01 | victory text should not assert the optional classification | **fixed**: "The escort has been identified, and so has everything you did not shoot" states what the win requires (Identify is scored separately) |
| SW02 | playtest the loss branch | engine test; `SW02SupplyLost` write and SW09 read unchanged |
| SW03 | per-aircraft rescue, CH-53 recovery | **fixed** (above) |
| SW04 | Seahawk/Arafura mismatch; passenger route | **fixed** (deck list); the passenger is routed; O2's picture now reveals the submarine |
| SW05 | named frigate vs generated force | **fixed** (Replaced + MaxUnits=1) |
| SW06 | Pioneer continuity, unconditional success text | **fixed**; Sejong the Great spawns on `O3ShieldJoined` |
| SW07 | blank generation + airbase prep | **fixed**: blank generation with no prep keys; the Wedgetail the memo promised is placed; "enclave field" is the one name |
| SW08 | deployment contract | **fixed** (above) |
| SW09 | dwell wording, purchased support | **fixed** (above); the P-8 homes on Scherger |
| SW10 | two-of-three passage | required Pioneer added; the Japanese helicopters are named allied assets, not player slots; rearm gated on SW09 |
| SW11 | Pioneer, CAP recovery, Strike counted AEW | **fixed**: Strike is the J-15D shooter alone (Trigger6 `Taskforce2Aircraft2`); transports lost ends the mission (Trigger8/9); Ford completes on the deadline she survived (Trigger2 no longer cancels Ford); Fujian at 130 NM in the text as on the plot; escorts are Luda/Sovremenny/054A without hypersonic ASMs |
| SW12 | Pioneer, unusable purchases | **fixed** (above); the spoiler frigate and Kilo are routed onto the track; two blue F-35A CAP slots and the Wedgetail give the finale a fight in both branches |
| O1 | helicopter compatibility, SW02 promise | **fixed**; the wreck exists and must be classified; the win is the helicopter back within 5 NM of the ship (809d153a: the solver had been overriding the authored box) |
| C1 | unconditional recovery vignette | **accepted**, and the text now says so; assisting hulls are on the helicopter's track, the boat is routed, the win is a 30-minute search stage then the helicopter back on Hobart |
| D1 | oiler arrival, incompatible helicopters, escorts threshold | **fixed**: one shadower carries an anti-ship fit and both are routed onto the group; 85 minutes; Karel Doorman named as what she is |
| D2 | carrier destination, support recovery | **fixed**; the "no opposition" reading is **accepted** — it is an exercise day, and the outcome texts no longer claim a package or a broken cycle |
| D3 | column objective, three mismatches, VTOL | **fixed**; the roadblock is routed onto the road, a pickup and a trawler give the ROE an object, the coaster carries containers |
| D4 | bomber recovery, restraint | **fixed**; three neutral merchants on the lane, red replies with JSM/Harpoon, "middle watch" |
| D5 | pad-strike vs interception | **fixed** (brief tells the truth); the loss of both aircraft no longer ends the trial (`force_loss=False`) |
| D6 | recovery vs mod properties, escort threshold | **fixed**: win is the launcher complex destroyed; YF-23s fly the intercept fit; headings match the run; Escort fails on the first loss |
| D7 | two aggressors need not stop the Bear | **fixed**: win is the Bear destroyed; Umpire is the tanker; strike detachment homes on the field |
| D8 | escort-only arrival; J-16D vs `plaf_j16a` | **fixed**: HEMTT alone wins; the brief says J-16; ridge detachment sits on the road; the J-16 starts outside PL-15 reach |

### Money and customisation

The review's economy table was accurate for the snapshot. As built now:

| Rule | Now |
|---|---|
| Starting points / cap | unchanged (1,250/1,000/850; cap 1,500/1,500/1,250) |
| Core completion | 1,580 (SW12 pays 0) — unchanged |
| Side operations | O1 50, O2 50, O3 60, O4 50; C1 0, C2 30 |
| Purchase windows | SW01, SW02, SW03, SW05, SW09, SW11, SW12 — and each window's `TaskForceModeBuilderSituation_en` tells the player when the next one is |
| Roster | Anzac 240, Hobart 480, Arafura 100; F-35A 45, F/A-18F 35, Growler 55, P-8 45, Wedgetail 80, Triton 60, MH-60R 20. Collins, Supply, Choules, Canberra, Mogami and the KC-46 are no longer sold |
| Persistent grants | none — no `JoinTaskForce` anywhere in the pack. Allied and support aircraft are allocations |
| Deployment | SW05 one ship; SW03, SW04 and the optional operations O3/O4/C2 let the player choose a detachment; SW07, SW08, O1, O2 and C1 sail nothing of the player's |

The playthrough estimates the review asked for (lean force, larger force,
loss-heavy) are **not done**: they need the game. The static floor holds at
every window (an Arafura at 100 never costs more than the smallest core
allocation).

### Runtime checks that remain necessary

All nine rows of the review's table are still owed, and are on the test card
under section 7 together with the new mechanisms this batch introduced.

## 2. The second-pass reader findings

The pass-2 dump (`pass2-findings.txt`, 47 findings across continuity,
economy, SW11, SW12, C1, D1–D8 and O1) was the internal input the review
built on. Each is dispositioned below; where a finding duplicates a review
row above, the row is referenced rather than repeated.

### Continuity

| Finding | Disposition |
|---|---|
| Coral Pioneer sunk with a win then sails on | **fixed** — §1 above |
| Steel Highway placed on the Coral Sea route while the pages say Arafura → Moresby | **fixed**: SW02 moved to the Gulf of Papua (`centre -10.3,145.0`); C1 the same; O1's traffic no longer walks her east |
| After the Wake hard-codes Lae Provider sunk | **fixed** — Kerema Trader |
| The intercept page stages Escort Seven at SW05, the mission delivers a Sovremenny | **fixed**: Meridian Escort 7 is placed at the inspection point in SW05 |
| Ward's memo promises a Wedgetail in SW07 | **fixed**: Wedgetail 02 on a long orbit; "enclave field" throughout |
| O1's promise to SW02 unwired | **fixed** — §1 |

### Economy

| Finding | Disposition |
|---|---|
| Growler first sold after the mission that describes it | **fixed**: in the SW05 window |
| Collins sold with no mission to deploy it | **fixed**: removed from the roster; SW09's boat is authored |
| No hull for sale before SW12 after an all-sail SW11 | **fixed**: Arafura and Anzac in the finale window |
| The purchase schedule never told to the player | **fixed**: `TaskForceModeBuilderSituation_en` on every builder window and a `MissionSpecialNote_en` on every no-builder mission |
| 1,100 points of hulls with no role; recon aircraft granted free | **fixed**: Canberra, Choules, Supply out of the roster; no grants |
| SW10's "Japanese ASW pair" are player slots | **fixed**: named allied assets on Mogami; the player's row is Maritime Patrol only |

### Fujian's Shadow

| Finding | Disposition |
|---|---|
| No trigger ends the mission on transports lost | **fixed** (Trigger8 two lost, Trigger9 Coral Pioneer) |
| Hypersonic ASMs on the escorts; the briefed strike is two YJ-91s | **fixed**: escorts are Luda, Sovremenny, 054A; the J-15D flies AntiShip toward the transports |
| Strike scored on any two of four, including AEW | **fixed** (the shooter alone) |
| Deadline cancels Ford though she survived | **fixed** (Trigger2 fails Transports, cancels Strike only; Ford resolves Complete) |
| 300 miles in the text, 134 on the plot; strike aimed at Ford | **fixed** (130 NM, "aimed at the transports and at you both", heading 205) |
| SW06 intel names two recurring hulls | **fixed**: a Luda is in SW11's screen as it was in SW06's |

### The First Ship Through

| Finding | Disposition |
|---|---|
| Nine knots cannot reach the box | **fixed**: box solved with `transit=9` |
| The spoiler group never moves | **fixed**: routed 054A, Kilo on its own station ahead of the track |
| Coral Pioneer not required | **fixed** |
| Four aircraft types sold with no row | **fixed** (CAP row, airbase prep, Darwin) |
| "Maritime strike flight" carries only AAMs | **fixed**: JH-7A `AntiShip` |
| Withdrawing group stationary | **fixed**: routed north |

### After the Wake

| Finding | Disposition |
|---|---|
| Assisting merchants 200 NM away, one armed and free | **fixed**: both on the helicopter's track, unarmed hulls, Hold |
| The boat cannot touch the helicopter but can kill Hobart from spawn | **fixed by telling the truth**: the brief says the boat is inside torpedo range of the ship; the boat is routed |
| Victory is one waypoint; "home" never scored | **fixed**: 30-minute stage in the box, then the helicopter within 5 NM of Hobart |
| Lae Provider sunk regardless | **fixed** |
| Entry advertises deployment for a blank mission | **fixed**: `IncludesTaskForce=False`, no deployment keys, note says nothing of your force sails |
| Snapshot names a losable hull as a neutral | **fixed** (was already in source; rebuilt) |

### Dispatches D1–D8

| Finding | Disposition |
|---|---|
| D1 red cannot do what the brief says | **fixed** (AntiShip MiG-35, routes onto the group) |
| D1 Shadow can never fail and rewards the opposite of intent | **fixed**: "Splash the shadowers before they find the oiler" is what is scored |
| D1 escorts fail only when all six die | **fixed** |
| D1 four helicopters on the FREMM | **fixed** |
| D1 clock tighter than the solver thinks | **fixed**: 85 minutes, box solved at the tankers' speed (`transit=14`) |
| D1 De Zeven Provinciën in text, Karel Doorman in file | **fixed** (text) |
| D2 no opposition; Cycle and Tanker free | **accepted**: an exercise day. Cycle (20) and Tanker (10) stay as protect objectives; nothing threatens them, and the brief no longer telegraphs a twist |
| D2 texts describe a package and a broken cycle | **fixed** |
| D2 "MV drifting contact"; Neutrals text names aircraft | **fixed** |
| D2 KC-10 and E-3G homed on a carrier | **fixed** (Scherger) |
| D2 box 104 NM from the carriers | **fixed** |
| D3 no opposition can reach anything | **partly fixed**: the roadblock APC is routed onto the road the column drives, so the column can be shot at; the amphibious group is still out of reach, and Group remains a protect objective |
| D3 roadblock and column spawn 839 m apart, column unscored | **fixed**: the column is the win (both vehicles); the roadblock sits on the road between; column weapons Tight |
| D3 identification has no object | **fixed** (pickup beside the roadblock, trawler under the lift) |
| D3 Harrier no HomeBase | **fixed** |
| D3 title ship carries munitions and does nothing | **fixed** (Containers; the Juan Carlos carries the lift) |
| D3 scored objective is the helicopters | **fixed** |
| D4 Restraint scored as fighter survival | **fixed** |
| D4 nothing red can reach the auxiliary | **fixed**: P-8 `AntiShip` and F-35A strike fit; Hobart and Anzac within Harpoon reach of the lane |
| D4 no neutral shipping | **fixed** (three merchants on the lane) |
| D4 force description vs file | **fixed** (Kuznetsov named, dispersal field placed, bombers "already airborne") |
| D4 first watch at 03:10; daylight at 04:25 | **fixed** (middle watch; timeout reworded) |
| D4 six-knot auxiliary cannot reach the box | **fixed** (`transit=6`) |
| D5 Serial auto-completes | **fixed** (`Fail` status) |
| D5 Sejjil inside minimum range | **accepted**: it is one of four pads, three must die; the brief no longer sells a "mixed raid" from all four |
| D5 losing both aircraft is an unstated defeat | **fixed** (`force_loss=False`) |
| D5 airliner in a formation with a trawler | **fixed** (own "airway" station) |
| D5 "score the intercepts", ARRW that does not exist | **fixed** (text) |
| D5 geography wording | **fixed** ("all four defence units"; the A-10 is named as the counter-launcher shot) |
| D6 red opens inside PL-17 range with no answer; one bomber hit ends it | **fixed**: YF-23 intercept fit; fatal on two bombers, matching the win |
| D6 stream pointed at the fighters, text says north-west | **fixed** (headings 28) |
| D6 complex cannot be scored | **fixed** (win = complex destroyed) |
| D6 survival-only secondaries | **partly fixed**: Escort fails on the first loss; Sensor is still "RQ-180 not lost" — accepted as the honest minimum |
| D6 Viper 31 and Meteorit 90 unarmed | **fixed** (`AirToAirVLongRange`, `AntiShip`) |
| D7 win never touches the serial | **fixed** (the Bear) |
| D7 U-2 is an unstated instant defeat | **fixed** (Recovery is -15, not fatal; `fatal=[]`) |
| D7 Umpire objective dead | **fixed** (the tanker) |
| D7 land aircraft homed on the carrier | **fixed** |
| D7 red has no counterplay | **partly fixed**: the aggressors sweep from their own station; the Tomcats keep Phoenix — accepted, it is 1988 and the text calls it a hot exercise |
| D7 "nobody is shooting anything real" | **fixed** (text) |
| D8 losing the gunship is an unstated defeat | **fixed** (stated in the brief) |
| D8 gunship inside PL-15 reach at start | **fixed** (J-16 moved east) |
| D8 airhead is an empty circle | **fixed** (box on the strip) |
| D8 civilian pickup counts toward the win | **fixed** |
| D8 ridge cannot reach the column | **fixed** (detachment on the road) |
| D8 Viper unarmed | **fixed** (`AirToAir`) |

### The Missing Beacon

| Finding | Disposition |
|---|---|
| Nothing at the datum; nothing classified | **fixed**: MV Torres Light adrift at the wreck station; the stage is `UnitClassified` on her |
| Lane traffic 150 NM away and static | **fixed**: routed traffic on the helicopter's track |
| "Home" scored at the datum | **fixed** at 809d153a (see the note in §1: the fix in ee5fff66 was being overridden by the arrival solver, which the evidence pass for this document caught) |
| Arafura does not list the MH-60R | **fixed** (pack definition) |
| Entry advertises deployment for a blank mission | **fixed** |
| Special note promises a SW02 benefit | **fixed** |

## 3. What this batch adds, and its own open questions

The four operations (O2 Southern Cross, O3 Borrowed Shield, O4 Weather
Alternate, C2 Broken Wake) and the Korean detachment are new since the
review. Their contracts were held to the same rules and each carries a
consequence the campaign reads; the mechanisms they lean on that no shipped
file attests, and are therefore engine tests, are: `SpawnByVariableAND=…,IsTrue`
(the shipped data attests only `IsFalse`), `TaskForceModeRearmByVariableAND`
(documented in the guide, not in any shipped campaign), the one-ship
`Replaced` + `MaxUnits` pattern, land units driving `Waypoints`, and a Korean
hull with no `TaskForceCost` appearing as an allocated (not purchasable)
ship. All are on the test card.

## How this was checked

On `809d153a`, after `git status --short` came back clean:

```
python3 tools/build_all.py --from-scratch          # 17 packs, consolidated
python3 tools/check_campaign_coverage.py           # 44 files (campaign copies twice), 610 references, 157 mods/packs accounted for
python3 tools/check_load_order.py                  # 141 entries, 46 overlaps
python3 tools/check_dependencies.py
python3 tools/preflight.py "Southern Watch O1 - The Missing Beacon"   # and O2, O3, O4, C2, 04, 06, 08, 01
python3 <scratch>/verify.py                        # 26 mission files + campaign.ini (35 entries): counts, trigger references, one exit each - clean
```

plus a recovery census script over every `Taskforce1Aircraft` section (the
102/102 figure above) and the trigger dump quoted in the tables. None of it
ran Sea Power.
