# Southern Watch — build notes

What was built from `campaign-bible.md`, where it departs from the bible, and —
more importantly — what has **not** been demonstrated.

## Native source pack: what changed here, and one retraction

`SEST_Native_Campaign_Source_Pack` is a curated set of extracts from the
shipped game and the stock campaigns. Every claim in its build brief was
re-checked against the files it points at before anything here moved. Four
things changed, and one earlier statement of mine was wrong.

**The retraction.** I previously said — in the working notes and in the reply
that accompanied them — that a cross-mission consequence could not be built:
that nothing in the shipped data showed how to gate mission nine on something
that happened in mission two, so support-ship loss could only be *stated* in
briefing text. That was wrong. `[CampaignVariables]` is shipped, and the
stock campaigns use it. Three chains are now wired and verified in the built
files:

| Written in | How | Read in | How |
|---|---|---|---|
| SW02, when the supply ship is lost | `[CampaignVariables] SW02SupplyLost=False` + `Action_VariableSet=SW02SupplyLost,True` | SW09 | `SpawnByVariableAND=SW02SupplyLost,IsFalse` on `civ_ms_amra` — lose her in the Steel Highway and the ship she would have resupplied is not on the plot seven missions later |
| SW06, when the northern group is classified | `Action_VariableSet=SW06NorthernGroupClassified,True` on the classify objective | SW11 | `Condition_Condition1_Type=VariableCheck` → `Action_UnitRevealToTaskforce=Taskforce1\|Identify` on the five-ship screen, plus an intel line naming the sortie that earned it |
| SW11, when FUJIAN is sunk | `Action_VariableSet=SW11FujianSunk,True` | SW12 | `SpawnByVariableAND=SW11FujianSunk,IsFalse` on the spoiler strike flight — leave her afloat and the last mission is contested from the air |

Only `IsFalse` appears anywhere in the shipped data, so every chain is authored
as an absence: the variable's *unset* state is what spawns a unit. An `IsTrue`
form may well exist; it is not attested, so it is not used. The reveal chain
reads the variable through a trigger condition instead, which is attested.

**Submarine depth is a named token, not a number.** The f3e2a783 fix put
numbers there — 300 to 500 feet. A census of every `RelativePositionInNM` in
the shipped missions returns 104 `low`, 88 `shallow`, 15 `periscope`, 1
`belowlayer`, 1 `AboveLayer`, and no depth number anywhere. The hunting boats
are now `belowlayer`, the semi-submersible `periscope`, the whale `shallow`,
and Collins stays at `0` — surfaced alongside, deliberately.

**The air-tasking flight rows filtered on loadouts the aircraft do not have.**
The brief flagged it; it reproduces. `usn_fa-18f_blk3` carries
`MurderHornetCAP`, not `AirToAir`; `usn_ea-18g` carries `MurderHornetSEADHeavy`
and `SEST_NGJLongRange`, not `SEAD`. The CAP and strike rows as written would
have excluded the two aircraft the roster sells for those jobs. All five rows
now list the loadout names the winning files actually define.

**Service windows follow the brief's §4 table.** Purchases open at four
force-assembly points rather than before every mission; SW10 gets rearm only,
SW12 repair and replacement aircraft but no new hulls.

What this still does not establish: that any of it behaves as intended with the
game running. A variable that is declared, written and read in three files is a
static fact about those files. Whether the campaign carries it between missions
is the seventh step of §16's acceptance run, and that step has not been taken.

## Bases, so fuel can matter — and the range is in the files

Two passes ago this campaign answered "no airbase" with `UnlimitedFuel=True`
for 48 aircraft. Then it answered it with bases and a radius I made up: 150 NM
for a helicopter, 600 for a fast jet, on the stated grounds that nothing in
the shipped data gives an airframe's range.

**That was wrong, and it was the laziest kind of wrong — I looked in one place
and stopped.** The flight model carries it, in two spellings:

- a **helicopter** declares `MaxRange` in `[Physics]`, already in nautical
  miles — MH-60R 520, SH-60K 412, CH-53 600, AH-64E 1035, VH-3D 542;
- a **fixed-wing** declares `SpeedAndRange_Cruise=<mach>,<range>` beside a
  `RangeUnits` line whose own comment reads *"Can be: Km. Any other value =
  nmi"*, so only the literal `Km` converts — F-35A 1367 nmi, Super Hornet
  1265, F-22 1841, P-8 5000 km, B-2 9000, Triton 9430.

**All 100 airframes this campaign places answer.** Aliased files defer to what
they extend, like everything else here.

One assumption remains and it is the only one: what fraction of total range is
usable as a sortie radius. A sortie comes back, so half goes out and half
returns, and a real profile spends more on reserve, join-up and time on task.
**0.40** is the planning figure that falls out of that. It is the single
number in this system not read from a file, and it is applied to a real
per-airframe range rather than standing in for one.

**Nowhere to land is now a build failure, not a fallback.** For the player's
side, an aircraft outside every usable field's radius stops the build and
names the distance, the range and the shortfall. The answer is to give the
mission something to land on — which is what the last three missions needed,
and each of them turned out to be a design gap the fuel question merely
exposed:

| Mission | What the range data showed | What it needed |
|---|---|---|
| SW08 The Open Door | The package was 707 NM from Scherger against an F-35A's 547 NM radius and a Growler's 506 | A carrier 103 NM off the target. A strike on that enclave was always going to be flown from a deck |
| SW10 Common Sea | The F-2As were homed on Darwin 428 NM away against a 360 NM radius — 856 NM of transit out of 900 NM of range, with nothing left for the orbit they exist to fly. Their station was already labelled a *detachment* | The strip they were detached from, on proven ground in the Kai group 19 NM away |
| D6 Long Reach | Five escorts 495 NM from Darwin against radii of 360 to 480 — and one of them a Rafale **Marine**, a carrier aeroplane with no carrier. The mission already had an empty "offshore picket" station | A carrier on it, 70 NM from the escort track |
| D8 The Long Perimeter | A Polish F-16 369 NM from Scherger against a 360 NM radius, and two Apaches sent 315 NM to the same field | A forward airstrip on the perimeter, which is where a perimeter operation flies from |

The result: **94 player aircraft, every one on real fuel with a real base, and
not one on unlimited.** The tightest margins in the campaign are Long Way
Home's Super Hornets and Growler at 74% of their radius and The Relief Ship's
AB 212 at 68% — both real numbers now, both inside. (Flight Deck Day's VH-3D
was at 87% when this was written; since 87fbd9a4 it starts 80 NM from its
deck, 37%.)

The rule runs **per side**, because an aircraft recovers on its own side's
deck or nobody's, and 59 native `HomeBase` lines are on red aircraft. Red and
neutral get the same search and the same bases where they exist — 13 red
aircraft are now on real fuel — but nothing fails for them: their order of
battle is not this design's to fix, and a red fighter dropping out of the sky
at bingo hands the player the mission. Before this ran per side, all 47 red
and neutral aircraft had finite fuel and no base anywhere, which would have
done exactly that.

## Adversarial pass on the reach work: two fatals in it

The reach gate went in on the strength of numbers it was reading wrong. Nine
reviewers were pointed at the shipped code with instructions to break it, and
two of them did, both with the build run rather than predicted.

**`reach()` never followed `#!extend`.** I had fixed exactly this for units two
passes earlier — `ai_roles()` and `loadouts()` follow `#!alias` because 65 unit
files are aliases — and did not think to ask the same question of ammunition.
102 files in this collection open with `#!extend`, 18 of them rounds. The
winner is a stub: `ammunition/plaaf_pl-15.ini` in mod 3789188689 is 483 bytes
of `[Guidance]`, and `MaxLaunchRange=108.1` lives in 3436170138 below it. So a
J-16 carrying a 108 NM missile read as a 15 NM one, and the DF-21 and DF-26
read as zero. The reach numbers in the previous section of these notes were
wrong; the station moves they justified happen to stand, but they were
justified on false readings and D8's in particular was decided on 15 NM for a
jet that reaches 108.

**`stores()` credited rounds from fits the unit was not flying.** A pylon map
named for a loadout the file does not offer — `pla_df-26b_tel` offers
`AntiShip,Strike,NukeStrike` and still ships a `[WeaponSystem1Default]` —
matched no known suffix and was therefore treated as a section loaded whatever
the fit. 55 of 210 placed unit/fit pairs sat on that, and it credited a
2,324 NM anti-ship round to the nuclear loadout. Suffixes now match
longest-first, and a section that plainly names a fit this unit does not offer
is skipped rather than counted as bare. One honest casualty: the `f-15ex` mod
was reached only through a targeting pod on a fit D6 was not flying, so D6's
Eagle II now flies `StrikePrecision` — which is what a strike mission should
have authored in the first place.

**`--dry-run` checked none of the air-tasking gates.** It returned before
`campaign_ini()`, which is the only caller of `tasking_rows()`, so the row and
slot pairing, the role and fit checks, the label vocabulary and the purchase
allowlists were all dead in the command whose own help says "resolve and check
everything, emit nothing". The same mutation passed `--dry-run` and failed the
real build. The campaign text is built before the exit now; it is pure, so it
costs nothing.

**A gate that answered the wrong question.** A flight label outside the six the
game localises was reported as "slot_ordinal and tasking_rows disagree about
what a slot is" — an internal drift assertion — because the rejected row never
consumed its sections. It says `'Tanker' is not an air-tasking role` now.

## Pacing: the variable the design never stated

The brief was smaller opening engagements, more reconnaissance decisions,
occasional fleet battles, consequences for losing support ships. Counting red
hulls got the first and third of those roughly right and could not touch the
question underneath, which is **whether the two sides can reach each other at
all**. A census does not distinguish a fleet action from a fleet parked 135 NM
away.

`check_reach()` reads `MaxLaunchRange` off every ammunition file a placed unit
actually hangs and compares it to the distance between the two forces at spawn.
It is a ceiling and it is used only to prove a force *cannot* reach, never that
it can — a ship whose longest round is a 28 NM SAM reads 28 and still cannot
sink anything at 20. Two numbers per role:

- **contact** — a red force further from blue than its own longest round is
  scenery, whatever the census says;
- **standoff** — red closer than this is an engagement the player was never
  given the chance to decide about. Land-on-land pairs are exempt: two ground
  forces in contact ashore is the scenario, not an ambush.

It found five missions, and one of them was mission one.

| Mission | Was | Now |
|---|---|---|
| SW01 White Water | opening, red **3 NM** inside the convoy | 20 NM, inside the boat's 49 NM reach and outside knife range. The station is authored directly onto a proven point — anywhere else and the snapper drags it back into the formation, which is how it got there |
| SW05 Warramunga's Shot | red 165 NM away with 50 NM of reach | 17 NM |
| SW06 Blind Horizon | red 98 NM away with 85 NM of reach | 61 NM. The fighters moved, not the surface group: the Triton still has to fly north to classify, and now something can meet it there |
| SW07 Long Way Home | red 159 NM away with 86 NM of reach | 68 NM |
| SW12 The First Ship Through | red 179 NM away with 85 NM of reach | 28 NM. Both groups — the one withdrawing and the one that has not acknowledged — are now inside the escort's picture, which is the whole mission |
| D8 The Long Perimeter | red on a ridge 156 NM up-country with a 6 NM SAM | on the column's route |

**`stores()` was missing a third of the ammunition in the game.** Rounds are
declared three ways — `Station7=`, `Ammunition1=` and a bare `Ammunition=` with
no index — and the parser only read the first two. That is 2,425 lines across
699 files. The Peykaap in mission one read as a 5 NM rocket boat when it
carries two Nasir at 48.6, and `ran_ffh_anzac` read as a 28 NM SAM ship when it
carries NSM at 165.6. Every reach number before this fix was wrong, and so was
the store coverage the report counts.

**Seventeen of twenty-two missions flew aircraft with nowhere to land.** The
game's own tooltip is explicit — "Use this option when an airbase is not
available for units to prevent aircraft from crashing at bingo fuel"
(`language_en/ui.ini:1081`) — and every one of those missions shipped
`UnlimitedFuel=False`. It is derived now, per aircraft and per mission: a
helicopter gets down on any deck, a fast jet needs an airbase or a real flight
deck, and the gap between the two is unambiguous in the data (every escort here
declares `AircraftCapacity=1`; Canberra 30, Charles de Gaulle 42, Type 003 85,
Ford 90).

**Two missions reported the wrong ship lost.** O1's fatal trigger watched HMAS
Arafura while its objective was the search helicopter, and C1 watched HMAS
Hobart while its objective was the recovery helicopter — so in both, losing the
ship ended the mission announcing the aircraft was gone. A fatal entry that
names its own units must now watch what its objective watches, or the build
fails; both missions take their units from the resolver instead.

## Review of 783da0f2: five findings, and what settling them turned up

Each of the five reproduced before anything moved. Two of them turned out to
be narrower than the defect underneath, and one of the review's arguments does
not survive the native census — the fix is right, the reason given for it was
not.

| # | Finding | Response |
|---|---|---|
| 1 | Eight advertised flight rows had no mission slots | Fixed, and the defect was three times the size. A row's `SlotCount` is now derived from the sections that exist, a row with no cockpit is not emitted, and the slot integer is derived too: it is the ordinal among rows sharing a LABEL, not the row's position. Eleven more rows were mis-slotted on that second rule alone. `Tanker` is gone — `ui.ini` localises exactly six air-tasking roles and that is not one of them. 28 rows of which 19 did not conform became 22 that all do, against a native invariant of 13/13 exact |
| 2 | SW06's Triton is unavailable before SW06 | Fixed at the root, which is not the purchase schedule. **No native mission binds a trigger to a slot-tagged aircraft — 20 slot-tagged sections in the shipped campaign, zero trigger references.** This campaign had twelve, across six missions. Every one now uses `JoinTaskForce=True` with a `CampaignTag`, which is what `04 Sunda Strait` does for the two A-4Gs its objectives name. The Triton is granted, not bought; SW06's Recon slot goes to the Wedgetail already in the mission |
| 3 | SW09's defeat predicate included an unadvertised third ship | Fixed, and SW07 had the same shape. One flat protect list with one objective id meant whatever sank, the same objective was reported failed: SW09 said Collins was lost when a freighter went down, SW07 blamed the tanker for a Rhino. Each fatal loss now names its own units and its own objective, and MV Coral Provider — who carries no objective and only exists when SUPPLY survived SW02 — is no longer a silent defeat condition |
| 4 | SW09's briefing promised service mechanics the predicate does not model | Relabelled, because there is nothing to implement. The shipped corpus uses **eleven condition types and seventeen sub-keys**, and not one tests speed, depth, heading, station, fuel or time spent inside an area; `UnitsInTheArea` is "Unit enters area". The briefing now states the rule the mission enforces — thirty-five minutes on the clock, then both ships south together — and the replenishment is not scored. Since 26 Sep 2026 it is not fiction either: STALWART carries a working supply system (SEST Replenishment At Sea's table, shipped by SEST RAN Fleet), so the briefing says what really crosses and the scored rule is unchanged |
| 5 | Seven positive tasks default to `Complete` | Fixed, but not the way the finding argues. `Complete` on an optional positive task is *native*: `10 Vengeance at Luzon` carries `DestroySlava=30,-30,Complete,Hidden` under the objective text "OPTIONAL: Destroy the Slava", and 39 native objectives look like that. The real gap was `Action_ObjectivesCancel` — 55 of 142 native `Complete` objectives are cancelled on the defeat path so an unearned completion cannot be banked, and this campaign's seven had **no cancel reference anywhere**. Every terminal trigger now cancels every objective it does not itself resolve, and the victory trigger completes the survival objectives explicitly, both derived rather than authored |

Two things the findings led to that they did not ask for:

**The terminal-trigger design was replaced with the native one.** Twelve
shipped missions end through a single shared exit: one trigger owns
`Action_EndMission`, it ships `Disabled=True`, and every outcome sets its
verdict and enables it (`missions/NATO/Charlies.ini` Trigger1). Ten native
uses of `Action_EndMissionDelay` and every one is `0`. This campaign had five
terminal triggers per mission with invented delays of 30, 45 and 60 seconds —
which is exactly the window the review's acceptance list asks about, a loss
landing during a victory's countdown. There is now one `EndMission` per
mission and no window at all.

**`ai_roles()` did not follow `#!alias`, and 65 unit files are aliases.**
`jp_f-2a_late.ini` is `#!alias aircraft/jp_f-2a.ini` and carries only its own
weapon systems, so reading it directly said the F-2A declares no role — which
made a fighter look like a non-combatant to the pacing check and like a
mismatch to the air-tasking gate. Role and loadout resolution now follow the
alias. The same function also has to cut the value at the first `/`, because
several of these files carry a trailing `//` comment on the `Role=` line.

New gates, each negative-tested by breaking what it checks: every emitted row
pairs exactly with its sections; no trigger may name a slot-tagged unit; a
flight label must be one of the six the game localises; a fatal loss must name
units its own objective watches; a discovered task cannot be earned before it
is revealed.

## Native source pack, second pass: three checks and what they caught

The first pass took the pack's corrections at face value and fixed them by
hand. This pass turned each one into a gate, which is the only way a fix of
that kind stays fixed. Every gate was tested by breaking the thing it checks
and confirming it fails.

**`check_flights()` — air-tasking rows against the roster.** The contract is
read off the stock rows rather than guessed. Pacific Strike's
`Recon|Recon|MPA/ASW/ESM/AEW|1|ASW/Recon/AntiShip/AEW` offers `AEW` to the
E-2C (whose only fit is AEW), `ASW/AntiShip/Recon` to the P-3C and
`ASW/AntiShip` to the S-3A: the row lists the union across the aircraft its
role filter matches, and each aircraft flies the intersection. So a fit named
in a row must be defined by some aircraft the row matches, and an aircraft the
row matches must define some fit the row names. It caught three live bugs:

| Row | What was wrong |
|---|---|
| Recon | offered `Recon` and `AEW`, which are P-3C and E-2C fit names. Nothing in this roster defines either — the P-8 has only `ASW` and `AntiShip` |
| HeloRecon | filtered on role `Helicopter`, which **no helicopter declares**. The MH-60R is `ASW,MPA,SAR`. That is almost certainly why the one stock helicopter tasking row is commented out in the shipped campaign. `SAR` is now the filter: the only token the MH-60R declares that nothing else in the roster shares |
| CAP | matched `usn_ea-18g` — all three fast jets declare `Fighter,Bomber,SEAD`, so no role token separates the Growler from the fighters — and then offered it four fits it does not have. It now carries its escort fit, AARGM-ER ×2 and AIM-260 ×2, which is how a Growler flies with a CAP anyway |

The Wedgetail and Triton still match the recon row and declare no
`AvailableLoadouts` line at all. They are exempt from the second rule
deliberately: whatever the engine gives a fitless airframe is its own default,
and inventing a preset to satisfy a checker would be worse than leaving the
behaviour unestablished.

**`trigger_integrity()` was passing vacuously, and had been since it was
written.** It parsed a section header only when the line ended with `]`; the
builder writes `[Trigger10]  #Report unhides Airlift`. So it saw zero triggers
in thirty-six mission files and reported clean every time. With the header
pattern fixed it checks **275 triggers and 901 references** — condition units
against real sections, objective actions against declared objectives,
message and intel keys against `[Language_en]`, and now trigger cross-
references too. All 901 resolve. That result is worth exactly as much as the
gate that produced it, which is why it is stated with the count.

**Per-mission purchase allowlists**, listed as *still not implemented* in the
f3e2a783 response, are implemented: `TaskForceModeAllowedRosterUnits`, which
Pacific Strike uses eleven times. The force assembles in stages — three
units at SW01, sixteen by SW09 — and SW12 sells aircraft and no hulls, which
until now was a comment above the window rather than a rule. Variants are
never restated: they come from the roster entry, so an allowlist cannot
advertise a fit the roster does not price.

**A discovered objective in SW06.** The stock shape is a report trigger that
ships `Disabled=True`, an earlier detection carrying `Action_EnableTriggers`,
and `Action_ObjectivesUnHide` on an objective flagged `Hidden` in
`[Taskforce1_Objectives]` — Triggers 8 and 10 of strike-group-molniya `03
Lifeline at the Edge of the World`, whose objectives block reads
`DestroyUSSAG=20,-20,Complete,Hidden`. Classifying the northern surface group
now reports that the escorts are screening a shuttle track, and a task to
identify it appears that was not on the briefing. It is the same
reconnaissance decision as the first one, asked again with the convoy clock
running and the Triton already north. A trigger that ships disabled and that
nothing enables is now a build failure.

`Action_DisableTriggers` does exist, incidentally — Trigger9 of that same
mission uses it. An earlier note here said it did not.

## Review of f3e2a783: what changed here

Every finding was reproduced before it was touched. The three anchor slots, the
20 unresolved objective ids, the 10 zero-depth submarines and O01's
already-satisfied victory circle were all exactly as reported.

| # | Finding | Response |
|---|---|---|
| 1 | Anchor on `Taskforce1Vessel2/3` in SW09/10/11 | The anchored ship is now sorted to the front before anything is numbered, so it is always `Taskforce1Vessel1`; the build fails if it is not. Every stock Task Force Mode mission anchors the first unit of its kind — that is the evidence, independent of the authoring guide |
| 2 | O01 starts 13.4 NM inside its own 20 NM victory circle | Arrival boxes are no longer hand-written coordinates. The roster authors a bearing and a radius; the builder solves the distance against the positions the units actually got, and rejects a box that is occupied at spawn or out of reach |
| 3 | 20 objective ids resolved to nothing | Every objective now names a predicate (`victory`, `neutral`, `protect`, `survive`, `destroy`, `arrive`) and gets its own trigger. An objective without one fails the build. SW02 now needs the cargo count **and** the medical ship in the box; SW09 needs Supply and Collins by name, after a 35-minute service window. Terminal triggers end the mission and `Action_ObjectivesCancel` the other outcome's objective |
| 4 | Purchased aircraft had no deployment path | `TaskForceModeAirTaskingAvailable` with flight rows per mission, and 27 `TaskForceModeAirTaskingSlot`/`Role` tags on the authored aircraft. Every mission that fields the task force now also carries `TaskForceModeMissionGenerationType=Generated`; leaving it blank meant the owned force never deployed |
| 5 | C01 is not outcome-gated | Not implemented — **relabelled instead**. The special note and the briefing say the recovery is offered unconditionally. Campaign variables can now gate a *unit* on a previous mission's outcome (see the section above), but gating whether a campaign *card* appears at all is a different key, and no shipped campaign does it. The briefing no longer names a ship that may still be afloat |
| 6 | Purchase and service rules were one boolean | `buy`, `repair` and `rearm` are three separate windows per mission. Purchases open at force-assembly points, not before all twelve. Per-mission purchase allowlists were open here and are now built with `TaskForceModeAllowedRosterUnits` |
| 7 | All submarines at surface depth | Authored per boat — and then **corrected again**: depth is a named token, not a number. Hunting boats `belowlayer`, the semi-submersible `periscope`, Collins deliberately surfaced alongside her tender |
| 8 | Routes and timing | `Condition_Time` is **seconds** — so the missions had no deadline at all, only a post-defeat exit timer. Each mission now has a real deadline in seconds that fails the main objective, and the arrival solver sizes every box to the mission's own clock. SW04's contact has waypoints to the box its objective depends on |
| 9 | Resolver accepted disabled Workshop folders | The fallback to exported folders absent from the canonical order is gone. Resolution is enabled-mods-only, so an unsubscribe fails the build instead of being credited |
| 10 | Range Week scored launchers as interceptions | The objective now says what the trigger tests — destroy three of four threat pads — and the authorised seaward target is exempt from the neutral-loss rule. A range safety boat and an airliner give the safety objective something it can actually fail on |
| — | Story chronology | The Enclave screen moves 2 → 12 November; the epilogue 26 → 28 November |
| — | O01/C01 real newlines in `Description=` | All mission text is normalised to the two-character `\n` escape centrally, so it cannot recur |
| — | Branch integration | `origin/feature/northern-front-iii-export` merged: the three SM-3 commits are in, and the consolidated pack carries all six SM-3/PAC-3 rounds |

Still open, and deliberately: **C01's gate** (relabelled, not built),
**mission density** against v1.1's 20–45 / 45–80 targets, and **O02–O12 /
C02–C06**. Per-mission purchase allowlists were on this list and are now
built — see the section above. Everything in the Task Force Mode layer still needs
the seven-step acceptance run in §16 of the bible.

## Bible v1.1: what changed here

v1.1 corrects v1.0 on the point that mattered most, and the correction is
right. I checked every key it cites against the exported Pacific Strike
campaign before acting on it:

| v1.1 says | Verified in `mods-source/_vanilla/original/campaigns/pacific-strike-task-force/` | Built |
|---|---|---|
| Persistence is native, not a manual ledger | `campaign.ini` `[TaskForceMode]`, `campaign_rules_en.xml` | `[TaskForceMode] Enabled=True` with the v1.1 first-pass settings |
| Requisition budget and prices | `player_task_force_roster.ini`, `<unit>=<variants>\|<points>` | `player_task_force_roster.ini`, 16 entries, prices from §13 |
| Per-mission economy keys | `TaskForceModeCompletionPoints`, `…CapPoints`, `…Repair`, `…Rearm`, `…EnableTaskForceBuilder` | emitted per mission from the §13 allocation table |
| The purchased force needs a starting position | `TaskForceModeAnchor=True` on a Taskforce1 unit | anchored in all 13 missions that field a player surface unit |
| Optional windows close | `ExpiresAfterMissionComplete`, `MissionSpecialNote_en` | O01 and C01, with expiry and a special note |
| Six-week calendar and allocations | — (design) | mission dates and completion points now match §12/§13 |
| Difficulty budgets 1250/1000/850 | `[TaskForceModeDifficulty_*]` | Supported / Standard / Veteran, repair ×0.75/1/1.25 |

**One correction back.** `ExpiresAfterMissionComplete` is a campaign **entry
index**, not a countdown: in Pacific Strike the two side missions at entries 9
and 10 both carry `=12`, which is the next main mission. A literal reading of
v1.1's "expires once the next main operation is complete" as a count would have
shipped an optional operation that expires before it can be flown. The builder
now resolves it from the mission's name to its index, and fails the build if
the name does not exist.

**Two observations worth folding into v1.2.** `usn_p8`'s squadron file labels
every squadron `USN`, so "Australian Squadron3" is a naming assumption rather
than something the file supports — the roster comment says so. And v1.1's
§13 prices are per the doc, but `raaf_f-35a` Squadron3 really is No. 75
Squadron at Tindal: the squadron file's own comment confirms it.

**Not built: O02–O12 and C02–C06.** v1.1's own release scope asks for O01 and
C01 in the vertical slice, and the remaining sixteen designs carry point
rewards and branch conditions that depend on the harness in §16's acceptance
run — which needs the running game. Building them now would mean authoring
sixteen sets of unverifiable branch behaviour. They are specified in the
bible and unimplemented here, deliberately.

## Art, and what the pack tells a stranger

Three keys carry the campaign's art, and all three were read out of the
vanilla export before they were used: `MissionImage_en` per mission entry,
`TileImagePath_en` per story event, and `BackgroundImage` once in
`[Campaign]`. The export carries text only; its PNGs were stripped, so the
first builds copied the key names and guessed the rest - 1920x1080 for every
image, `DisplayFormat=Legacy` from the 1988 linear prototype, and the story
image itself under `TileImagePath_`. The first install answered the guesses:
the briefing panel before White Water drew no mission image at all.

The stock Task Force Mode campaign's art was then measured on an installed
copy (`StreamingAssets/original/campaigns/pacific-strike-task-force/art`),
and the pack now matches it where the game is the one drawing:

| Thing | Stock | Now shipped |
|---|---|---|
| `DisplayFormat` | `MapView` (Pacific Strike; `Legacy` is the linear prototype's) | `MapView` |
| mission sheet (`MissionImage_`) | 1184x640, all fourteen | 1184x640, drawn at 2x and halved |
| event tile (`TileImagePath_`) | `bkg_tile_message.png` / `bkg_tile_newspaper.png`, 128x128 | the same two names and size, generated |
| story images | reached only through the page's `Assets[]` binding | the same; 1920x1080 inside this pack's own XAML |
| backdrop | `BackgroundImage` names a file that is not on disk in the stock folder | 1920x1080, still a guess |

**The briefing map.** The briefing screen's right-hand pane is a separate
thing from the campaign map's card: the game draws it from
`<mission>_briefing/BriefingMap_en.xml` beside the .ini, a XAML fragment
whose `<Image>` binds an asset by file stem to an image in the same folder.
Every stock mission and every stock campaign mission ships one; no SEST
mission did, so the pane was blank - the "large area where an image should
be" the first install reported. `integration/missions/briefing_maps.py`
now draws one per mission from the mission's own unit positions on Natural
Earth coastlines (own forces placed, enemy as reported areas, enemy
submarines withheld with a threat note, neutrals as shipping), at 2192x1328
for the 1095x662 canvas the stock maps are laid out on. The campaign
builder draws them for its 26 missions and mirrors them into the browser
copies; `build_briefing_maps.py` does the loose SEST missions; the
installer copies the folders beside the missions. This is ported from the
`sest-dev/peaceful-gauss-e1zvfq` session's work, re-rendered in Pillow so
the pack keeps one optional image dependency and the same keep-committed
fallback.

Whether a mod-supplied campaign's art is drawn at all is still the test
card's question; what is no longer in doubt is that the sizes and the
format are the stock ones. The `DXT5 ... requires a texture size that is a
multiple of 4` lines in the game log are the stock art's own (bkg_paper is
3000x3855, bkg_newsprint 1215x1362): they were in the log before this
campaign shipped an image, and every PNG here is a multiple of 4.

`make_art.py` draws every card, dispatch sheet and the backdrop **from the
mission files the builder has just written**, not from a parallel description.
A card therefore cannot advertise a mission that changed underneath it, and
the backdrop's graticule and marks are the twelve missions' real
`MapCenterLatitude`/`Longitude`.

The backdrop is a plotting sheet, not a map, and that is a decision rather
than a shortcut. There is no shoreline data anywhere in this repo. A drawn
coastline would be invented, and an invented Arafura Sea behind a campaign set
in the Arafura Sea is worse than an honest empty one. What it does show is
true: where the missions happen, and in what order.

Two things went wrong in drawing it and are worth keeping:

- the vignette's alpha climbed *inwards*, which painted a hard dark frame that
  stopped dead 230 px from the edge instead of fading into the middle. It read
  as a rectangle floating over the chart;
- the first de-collision pass fanned overlapping marks by a fixed number of
  DEGREES. Three missions share one patch of water, so the fan was needed —
  but a degree is a different distance on every chart, and the fan shoved
  mission 01 straight into mission 05 a degree away. It is done in pixels now,
  by relaxation, which is scale-independent by construction.

### The three things a subscriber could not have known

The pack was, until this pass, written for the person who built it:

- the campaign's own `Description` ended "See `docs/campaign-coverage.md` for
  which mod supplies what" — a repo path, to a file a subscriber does not have;
- the consolidated pack described itself as "Built by the Seapower-mods repo;
  the per-pack sources remain there," which is a note to a colleague;
- and the 140-entry load order the whole thing was built against shipped
  nowhere at all. A stranger missing one mod got a broken mission and no way
  to find out which.

`REQUIRED-MODS.txt` and `LOAD-ORDER.txt` now ship inside the pack. The first
is generated from the same `coverage()` rows the developer report uses, so it
cannot drift from what the missions actually place, and it states its own
limits rather than implying completeness: a mod may declare a manual
dependency of its own (SeaLifter does), and a unit file may `#!extend` a base
this build resolves without the campaign ever naming its mod. The full order
ships beside it for exactly that reason.

### The install that was in line with the wrong thing

`data/deploy-branch.txt` named `feature/northern-front-iii-export`. The branch
guard in `sync-sest.ps1` therefore did not fire, and the install reported

```
IN LINE: all 122 installed files match this commit (d2547151).
```

That commit contains zero Southern Watch files. "IN LINE" answers *do the
deployed bytes match the repo* — it never claimed to answer *is the repo on
the branch you meant*. The guard existed and was pointed at the wrong target,
which is the more dangerous of the two failures: it reports success.

`docs/campaigns/southern-watch/install-alignment.md` is the ordered procedure,
written so that each step carries the check that would catch the failure that
step is capable of producing.

## The release audit: sixteen findings, and what verifying them turned up

Seven dimensions swept the built pack and every finding was put to two
independent skeptics before it was believed. Sixteen survived, eight did not,
and a completeness critic found the one thing the sweep had not opened — which
turned out to be the biggest of the lot.

### The one that reached outside the campaign

`language_*/loadout_names.ini` has exactly ONE section, `[LoadoutNames]`, so
every key in it is a global loadout id rather than one aircraft's property.
The RAAF F-35A upstream renames six of those ids to suit itself —
`AntiShip=Anti-Ship JMS (Internal Only)`, `Strike=Close Air Support (Full
Payload)`, `AirToAir=Ait-to-air (Full Payload)`, typo and all — and the pack
copied its file wholesale to inherit the F-35A's loadout names.

`AntiShip` is the anti-ship loadout of **159 aircraft files** in this
collection. `Strike` of 212. `AirToAir` of 180. A French Alouette II's
anti-ship fit was displaying as "Anti-Ship JMS (Internal Only)".

Sitting at the top of the load order makes it worse rather than better: a SEST
pack's copy of a key beats the upstream's and the base game's alike, so the
pack had *guaranteed* the rename won. The US Naval Aviation Chinese file does
the same to eighteen ids, cargo types on merchant ships included — `Oil`,
`Ore`, `Troops`, `Fertilizer`.

`integration/common/registry.py` now restores the base game's value for any
key the base game already defines, and leaves alone the ids an upstream
actually invented. Restoring rather than deleting is the point: dropping the
line would only hand the key back to the upstream mod, which is still
installed and still above vanilla. Writing the correct value at priority one
is what puts the names back.

`check_load_order.py` gates it, and was negative-tested by putting the rename
back and watching the gate fail.

The same file had seven loadouts whose display text was their own internal id
— `StrikeJSOW=StrikeJSOW`, `Strike183=StrikeARRW` — while the same mod's
Chinese file named them properly. They are named now, each verified against
the stations it actually hangs: `StrikeJSOW` carries `dts_agm-154a`,
`Strike183N` the `(w62)` round, `SEST_AntiShipLRASM6` six `dts_agm-158c-3`,
counted.

### The credits file that was wrong by a factor of thirteen

An earlier pass in this branch added `CREDITS.txt`, generated from the
`# <original id>` comment on the first line of each unit file. Six files carry
that comment, so it credited six mods.

The completeness critic asked what the sweep had not diffed, and diffed it:
**79** shipped unit files are 90% or more identical to a specific Workshop
mod's file, from 28 different mods. Fifteen RAAF airbases built off Modern US
Airbase's large airfield. The Super Hornets from US Navy 2027. The Anzac, the
ESSM, the ARRW, the Rafales.

That is not a scandal — a Sea Power unit file is a whole-file override, so
there is no way to change one line of somebody's aircraft without shipping the
whole aircraft, and a patch pack is structurally a collection of other
people's files with edits in them. What was wrong was the number. A credit
derived from a convention only catches the files whose author knew the
convention. It is measured now: every shipped unit file diffed against every
file of its kind in the collection, 90% and up listed with the percentage
unchanged.

### A loss condition nobody was told about

D5 Range Week ended in instant defeat the moment one of the player's own four
air-defence units died — and reported it as a failure of "Destroy three of the
four range threat pads", which is a different exercise. The fatal rule was
`F("Pads", ["battery"])`: the right units watched, attributed to the wrong
objective. There is a `Battery` objective now that says what the rule is, and
the defeat names it.

D2 failed "Keep the carriers operating" when the player shot a neutral. Every
other mission with a neutral-harm trigger fails an objective about neutrals;
this one had none to fail. Checked all twelve rather than just the one that
was reported.

### Smaller, and all real

- A build note shipped inside `MissionSpecialNote_en`, a player-facing panel,
  explaining which engine feature the author could not implement. In all nine
  localisations.
- `_vanilla` — this repo's folder name for the game's own files — listed as a
  required mod in fifteen mission briefings, alongside the internal SEST pack
  names for packs that ship inside this one download. Both now read as "the
  base game" and "this pack".
- D2's briefing said two carriers; the mission places three, named.
- Mission 11's briefing promised a J-20 pair; there is one J-20.
- MV Lae Provider sank in the contingency after STEEL HIGHWAY and sailed again
  nine missions later, carrying cargo.
- The Dispatches folder advertised five series — "Allied Dispatches", "Red
  Line", "Future Front", "Cold Sea" — that appear on no mission a player can
  see. They live in each mission's `intro`, which is a campaign-map field, and
  the dispatches are browser entries with no campaign map.
- `commander_settings.ini` set `CommanderStartingRankLevel=5` with no
  `[OfficerRanks]` for the index to point at, and named the navy without its
  emblem. Both are base-game assets referenced by path.
- `REQUIRED-MODS.txt` put Anchor Chain under "the campaign does not call for
  them" while B-2 Spirit — which IS required — says "Requires AnchorChain and
  SeaLifter" in its own `_info.ini`. Prerequisites are derived from the
  required mods' own descriptions now, and SeaLifter is named as a
  requirement this collection does not carry.

### What the refutations were worth

Eight findings were killed. Four of them were killed on scope — "not
player-facing" — while every fact in them reproduced, and four of those facts
were wrong statements in this branch's own install procedure. The most
important: `set-mod-order.ps1` **drops** a workshop id it does not recognise;
it only appends non-numeric tokens. The procedure said the opposite, and the
script's own help text had said the opposite for longer. Both say what the
script does now.

A skeptic that refuses a finding on scope has not shown the finding is wrong.

## Geometry: the encounters were not at encounter scale, and the build could not see it

The full review's first two mission readers came back within minutes of each
other with the same shape of finding from opposite ends of the campaign. In
the opening mission, Warramunga started 46-51 NM from the convoy she is
briefed to shepherd, in a 50-minute mission an Anzac at flank covers 24 NM
of; the "identification traffic" was 130-140 NM away and sailing off; the
armed Meridian escort was stationary, facing away, with a 17 NM navigation
radar 20 NM from the nearest merchant. In SW02 the neutrals were 188 NM from
the convoy. Every gate in the build had passed every one of those files.

Two causes, both mechanical.

**The snapper deformed every offshore mission.** To keep a ship off dry land,
every vessel and submarine was moved - individually - to the nearest position
any loading mission had ever put a unit of that kind on, one proven point per
hull, never reused, up to 60 NM. A four-ship convoy took the four nearest
distinct points, which scatter; its escort took *its* nearest point, in
whatever direction that lay. SW01's authored 34 NM shipped as 46-51. SW12's
worst displacement was 43 NM, D1's 36, SW11's 33. The pool of proven water is
2,494 points across the whole theatre, which in the open Arafura is nearly
empty, so "snap to proven water" was a rule that moved stations tens of
miles to prove a thing the chart already says.

It now snaps the **station**, not the unit, and only near a coast. A station
more than 25 NM from every harvested land point is used exactly as authored -
it is open ocean and the designer put a ship on it - and recorded as unproven
so the build prints the list. Within 8 NM of a proven sea point near land, it
snaps. Neither, it refuses, with the distances, and the refusals are collected
so one dry-run names every station that needs a decision rather than the
first. The ships of a station form on the snapped point 0.6 NM apart, and the
game's own formation keys space them from there. Fifty-six stations now ship
where they were drawn; the worst drift in the campaign is 0.4 NM.

Uncovering honest positions also uncovered two accidents in the other
direction: D1's shadowers were 7 NM outside their own missile reach, and D6
had a red carrier and Ford sharing one station 0.6 NM apart. The old drift
had been pulling both into something playable by luck.

**Nothing checked that the pieces could meet.** `check_reach` asked whether
red could hurt blue. Nothing asked whether the escort could reach what it was
escorting, whether the neutrals were anywhere the player would have to tell
them from the threat, or whether a red unit meant to press the player was
pointed at them. `check_closure` now asks all three: a protected ship whose
nearest armed escort cannot close inside the mission clock at 24 kn is a hard
failure; a neutral more than 35 NM from anything protected and pointed away,
or a red unit outside its own reach facing away with no route, is reported as
"cannot take part" - because a background neutral or a picket that never
closes can be a design, but it has to be a decision you can read.
`check_reach` also stopped treating a MiG-35 seven miles outside missile
reach as scenery: red units get transit by kind now - 300 kn for aircraft,
24 kn for ships, nothing for a launcher ashore.

All three gates were negative-tested by breaking one mission each and
watching the message, then restoring.

**Re-authored at encounter scale**, from the readouts rather than by feel:
SW01's escort 8 NM astern on the convoy's heading, the trawlers 14 NM ahead
closing, the Meridian hull and its decoy 16 NM up the track to the handover
box with a route that brings it onto the convoy, the airliner crossing
overhead. SW02's traffic 15 NM ahead of Kokoda Star. SW04's whale 12 NM from
the patrol ship instead of 60. SW12's escorts 5 NM ahead, the withdrawing
group 30 NM off the bow and opening - close enough that holding fire on it is
the mission. D1's shadowers inside reach. D6's Ford on her own station.

What this does not establish: that the encounters PLAY well. It establishes
that they can happen. The clocks, the speeds and the identification puzzle
are now geometrically possible, which is the precondition the first build
skipped.

## The mission-by-mission review: what ten readers found, and what changed

Every mission got one reader with the whole file, the briefing, its campaign
entry, the bible section and the unit files behind every number it quotes,
told to play it in their head and report only what they could point at. The
first ten came back before the session's spend limit stopped the rest; the
skeptic pass that was meant to follow each finding never ran, so every
finding below was re-checked by hand against the built file before anything
moved. What they found, and what changed:

| Mission | The finding that mattered | What ships now |
|---|---|---|
| SW07 Long Way Home | The package was a tripwire, not a win condition; a lost Raptor paid out in full; two USAF F-22s joined the player's roster for good; red's AEW and tanker sat 145 NM west of the interceptors they were "behind" | Two of three package aircraft home is part of the win; the Raptors are `protect`, so a loss fails the objective; no join; the support orbit sits on the Foxhounds' back-bearing |
| SW08 The Open Door | The win box was 230 NM *behind* the transports, so the door was not between them and anything; blue spawned inside the S-400 envelope; the brief promised ninety minutes on a seventy-minute clock | Relief comes from the north-west with a hold leg, the box is on the far side of the battery, the strike starts 129 NM out with JSM on the F-35s, the brief says seventy minutes, and the entry is `detached` like the stock detached operations |
| SW09 Southern Lifeline | The Akula was 204 NM away, pointed elsewhere, with no route; nothing red could touch a ship; the "surfaced alongside for thirty-five minutes" premise was never asked of the player, so diving at t=0 and steaming 5.9 NM won at 35:00 exactly; HMAS Supply was the centrepiece unconditionally, seven missions after the campaign can sink her; the timeout text described the wrong clock; "comes home on Thursday" on a Thursday; a "Tu-214R that did not come back" airborne on the plot | The service ship is HMAS **Stalwart**; the window is a stage — both ships still inside five miles of the rendezvous *when* the clock reaches 35:00 (`UnitsInTheArea AND Time`, the shape of `03 Lifeline` Trigger8 on units that start inside the area) — and only then does the withdrawal line eighteen miles south open, on an 85-minute clock; the Akula starts 50 NM out and closes at 20 kn across the withdrawal track; one Flanker carries Kh-31A; the P-8 slot and Coral Provider each have their own station; the text says what is scored |
| SW10 Common Sea | The submarine "that ends the mission" was 144 NM away, heading away, with no route — six miles from a handover point the solver had long since moved; the brief promised a surface group and an F-2A anti-ship sortie, the file had neither, and the F-2As were a CAP slot spawned 17 NM in front of four Flankers; no red weapon could reach a merchant; "locate and break off the submarine" was scored as a kill and paid out at mission end regardless; the two-of-three cargo rule was never stated; the win re-completed the Allies objective after a Japanese ship was sunk | The boat sits across the solved track 38 NM from the convoy; a Type 054A comes in from the east; the F-2As carry ASM-3 and are not a slot; the J-10C carries YJ-91; the fighters start a hundred miles out with routes; the submarine objective is `UnitClassified` and fails if never done; the brief states two-of-three; the win line no longer re-completes a protect objective whose loss the mission survives |
| SW03 Rig Seventeen | Victory text said "both airframes" for a one-helicopter win; "bring both amphibious ships home" had no home | The text says what is scored: one lifter with the crew, both ships afloat |

Two changes to the builder came out of it, both general:

- **A victory stage can carry a clock.** `after=dict(kind="area", ...,
  after_minutes=N)` emits the area test and a `Time` condition in one trigger,
  `<Condition1> AND <Condition2>`. The vanilla export uses exactly this on
  units that *start inside* the area (`03 Lifeline` Trigger8, two vessels 1.6
  and 2.4 NM inside a 10 NM area, `Time=120`), which is the evidence that
  `UnitsInTheArea` is a state and not only an entry event. It is the nearest
  thing the engine has to a dwell.
- **The win line completes only the survival objectives whose loss ends the
  mission.** A `protect` objective the mission survives losing had already
  been failed by its own trigger, and the vanilla-pattern win line was
  flipping it back to complete on the same debrief. `StatusAtMissionEnd`
  resolves the held case on its own.

What the readers said the campaign does well is worth keeping in view: the
briefings are honest about the engine in the fiction's own voice, the
terminal triggers are cleanly separated and funnel through the one stock
exit, and the premises — a second navy arriving so an exhausted escort force
can look down while someone else looks up; a submarine on the surface being
the most vulnerable thing either ship will ever do — are the strongest hooks
in the campaign. The fixes above were made so those premises are what the
file actually plays.

## Review of 057405fe: what settling it changed

The independent review of `057405fe` and the second-pass reader findings are
dispositioned row by row in `review-disposition.md`, with the built trigger
each answer rests on. The shape of what changed:

- **Recovery is checked against the files, not the distance.** `deck_fit()`
  reads the deck's `AircraftSupported` and the airframe's `CarrierCapable`
  through `#!alias`; VTOL is fixed-wing that may use a deck naming it; a
  player aircraft with nowhere to go fails the build. `check_purchased_recovery()`
  runs the same test for every type a window sells against the mission's
  decks. `deck_size()` falls back to the `[AirGroup]` a hull embarks when it
  writes no `AircraftCapacity` - the five vanilla Soviet hulls and every
  Korean hull declare their decks that way. Census on the built files: 102
  player aircraft, 102 compatible, none undeclared or homeless.
- **Anchors are the player's ships.** The guide says the generated mission
  replaces `Taskforce1Vessel1` with the player's first ship, so no generated
  anchor carries a name (the builder refuses one) and the fiction addresses
  "your flagship". Weapons Free is the guide's one-ship pattern: `Replaced`
  with `TaskForceModeMaxUnits=1`.
- **A blank generation type is a model, not an omission.** SW07, SW08 and
  O2 launch as authored. (O1 and C1 did as well, until they were found
  bringing back ships the player had lost; their notes never said nothing
  of the player's sailed - see "Side operations sail your ships".)
  No deployment keys, no rows, no airbase
  prep, `Includes*=False`, and a note that says nothing of the player's
  force sails. The builder refuses flights or a slot tag on such a mission.
- **Per-unit stages.** Rig Seventeen builds one pickup → extraction →
  lost-after-pickup chain per lifter, so the aircraft that visited the
  platform is the one that has to come home.
- **Coral Pioneer is required by every win that places her and fatal
  wherever a win does not depend on arrival**; every other merchant is unique
  to its mission. No `JoinTaskForce` anywhere: allied aircraft are
  allocations, never grants.
- **Every purchase has a path.** The KC-46 is theatre support; the finale
  sells aircraft against a CAP row with airbase prep and Darwin placed,
  plus Arafura and Anzac as replacement hulls; Collins, Supply, Choules,
  Canberra and Mogami left the roster. Every builder window says when the
  next one is (`TaskForceModeBuilderSituation_en`).
- **Eight consequence chains**, all in the guide's or the shipped data's
  syntax: `SW02SupplyLost`, `SW06NorthernGroupClassified`, `SW11FujianSunk`,
  `SW09ServiceHeld` (→ `TaskForceModeRearmByVariableAND` on Common Sea),
  `O1BeaconFound`, `O2KiwiPicture`, `O3ShieldJoined`, `O4LanggurStocked`.
- **Geometry that the story can survive.** Steel Highway and After the Wake
  moved to the Gulf of Papua; every arrival box that is a place (carriers,
  a distribution point, a strip, a ship) is authored rather than solved,
  and the solver is used only for bearings.
- **Four operations and a Korean detachment**: O2 Southern Cross, O3
  Borrowed Shield, O4 Weather Alternate, C2 Broken Wake - see the bible's
  "As built" table. Euromod-South Korea Navy (3789208859) is catalogued,
  ordered after the other Euromod addons, and supplies Sejong the Great,
  Daegu and the Lynx as a temporary attachment.

One thing the evidence pass for the disposition caught: `O1` was still listed
in `ARRIVALS`, and the solver overrides an authored box whenever a bearing is
given, so the "helicopter home" win the rewrite drew on the ship had shipped
as a circle 71 NM from her. `809d153a` removes the entry. An authored `at=`
and an `ARRIVALS` bearing must never both exist for one mission.

## Automatic SAR and the MV-22B

Both were subscribed but uncatalogued, and the sync writes only catalogued
mods into the order - so the Mod Manager showed them as not loaded. Both are
catalogued now (`data/mod-catalog.json`, `data/load-order.tokens.txt`).

**Automatic SAR** (3774105087) is a code mod: a DLL the export skips, plus
language files. It is used through a mechanism the game already has. The
Task Force debrief pays survivors picked up as requisition points
(`ui.ini [TaskForceDebrief]`: "{0} survivors -> {1} additional point(s)
awarded"), driven by `CSARPointModifier`. The campaign had set that to 100 to
keep rescue from becoming income; it now ships the stock campaign's 10, and
the campaign description tells the player that rescue pays and where the
command is. Which way the modifier scales is unstated - the stock comment
reads "100 survivors reward 1 pt" beside a value of 10 - so test card 6A.3
reads the debrief line to settle it.

**The MV-22B** (3806466625) is an unarmed tiltrotor, `UnitType=VTOL`,
`CarrierCapable=True`, 32 seats on its Transport fit. It enters as US
Marine lift out of Darwin, which is where the Marine Rotational Force flies
them, and never as a purchase:

- **Rig Seventeen**: one of the two rescue lifters is now an MRF-D Osprey
  off HMAS Canberra (the class has hosted MV-22Bs in Talisman Sabre; the RAN
  Fleet builder's `deck` key adds it to Canberra's list, and the recovery
  gate homes it there). The rig's head count fell from forty-one to thirty:
  forty-one never fitted one lift - the Super Stallion seats 37 - while the
  win has always been one lifter's chain.
- **The Long Perimeter**: two Ospreys bring the airhead's first lift in
  from 58 NM south-west, the last five miles inside the ridge Tor's
  envelope, scored by a new Lift objective (15/-10, fails at mission end).

The same export carried a U.S. Navy 2027 update (sixteen new Flight I/II
Arleigh Burke hulls, variant and language changes) and author updates to
Euromod's interceptors. None of it changes a unit the campaign places; the
six rounds Collection Fixes rebuilds (SM-3 IA/IB/IIA, SM-6, SM-6 IB,
PAC-3 MSE) take the author's new kill probabilities, penalties, numeric RCS
and body areas, and every SEST delta (the loft angle, the 150,000 ft gate,
the flight times) still lands on top. All 26 campaign missions and the
loose missions preflight clean against the new files.

## The Anzac's ESSM

Reported in game: the ESSM Block II flew like an anti-ship missile, a metre
above the sea. The Anzac's Mk41 fired the Anzac mod's own "RIM-162 ESSM",
which the RAN Fleet pack had been re-shipping unchanged under a space-free id.
That file is a RIM-7F template its author left flagged `REQUIRES STATS
REVISION`: no kinematic model at all (no `ApplyKinematics`, no
`MaxLoftAlt`/`MaxLoftAngle`, no `TypicalTargetAlt`), and a 26 ft attack floor
that puts every sea-skimming anti-ship missile outside the band where the
engine "greatly increases missile deviation".

The Mk41 now loads Euromod's `usn_rim-162h`, a complete active ESSM Block II
(5 ft floor, lofts to 60,000 ft at 40 degrees with a terminal loft, 27 NM).
It is datalink midcourse, and the ASMD hull's Mk41 blocks already take a
guidance channel from CEAFAR (ten weapon channels) - the condition the
weapon-employment gate checks, which passes. Hobart still fires the Block I
(`usn_rim-162a`, semi-active).

What the files cannot settle: all three ESSMs in the collection declare
`SecondaryTargetType=ASuW`, which lets the AI fire them at ships. A surface
shot flies low whichever round it is. If the new round is ever seen doing it,
the question is what it was fired at, and dropping the secondary type is a
one-line change. The same sweep checked the wider theory and ruled it out:
the stock game ships 53 of its 71 air-defence and air-to-air missiles with
no climb profile at all, so a missing loft is not by itself a fault.

## Side operations sail your ships; helicopters are helicopters

Reported in game after White Water: the next operation "didn't seem
persistent at all" - no damage, and a ship short had come back - a stray
contact near 0°, 0° with a blue unit pushed to the edge of the tactical map,
the Seahawk showing a French flag, and not much to do.

**O1 and C1 sail the player's force now.** Both were blank-generation
missions: The Missing Beacon placed HMAS Arafura and a Seahawk, After the Wake
placed HMAS Hobart and a Seahawk, and all three `Includes` flags were False,
so the game launched the files as written and nothing of the player's
deployed. Pacific Strike has four side missions. Three (03A, 07A, 08A) are
detached submarine sorties whose note says in so many words that "your task
force will not deploy"; the fourth, 03B Holding the Lombok Strait, is
`Generated` and sails a ship from the player's own task force. Ours said
nothing of the kind, and they came the day after missions in which the player
can lose hulls. C1's Hobart is on sale before Steel Highway, so a player who
bought and lost her there got her back the next morning. That breaks the
campaign's own rule: a destroyed ship never sails again as the same surviving
ship.

Both are `Generated` now - 03B's shape - with `TaskForceModeAnchor` on the lead
ship, a detachment of the player's choosing and a Ship's Flight row for a
bought Seahawk. No builder, no repair: each is the next day. Each win names
the lead ship (`Taskforce1Vessel1`, which the generated mission fills with the
player's first ship), so each pairs it with a loss terminal on that ship -
stock's "Flagship must survive", which every anchor-named win in Pacific
Strike has. Without it a detachment that lost its lead sailed on towards a
win nothing could give.

- **The Missing Beacon** is a race. MV Torres Light is adrift with her bridge
  recorder aboard, and MV Meridian Salvor - an 11-knot Delvar-class support
  ship, Meridian's usual Iranian-built hardware, weapons Hold - is steaming
  for her. Meridian needs 13 NM to her one-mile ring: 71 minutes. The lead
  ship needs 16.5 NM to its 1.5-mile ring: 34 minutes for an Anzac (29 kn,
  the file that loads), 35 for a Hobart, 45 for an Arafura, 55 at a
  conservative 18 kn. So a frigate lead can waste half an hour and still win;
  an Arafura or a ship slowed by White Water's damage cannot. Classify the
  coaster, then get the lead ship alongside; that win writes `O1BeaconFound`,
  so Steel Highway's reveal now depends on the recorder being recovered, not
  only seen. Meridian inside her ring first ends the mission - stock's own
  shape, 01 Raid on Okinawa's "Assault unit reaches Kume - player defeat" (a
  Taskforce2 unit in an area, `AreaDisplaySide=Both`), built by a new
  `denied` entry. Sinking her removes the competitor and fails `Restraint`
  (+10 held, -20 broken); the player still has to get alongside. The mission
  is 90 minutes, and its timeout is written for the only case that reaches
  it: Meridian out of the race and nobody alongside by dark.
- **After the Wake** is the same recovery, flown by the player's own ships:
  take the lead ship through the drift box to its northern edge. The first
  draft also asked her to be in the box "past the half hour", with the Time
  condition in the win trigger - which ships `Disabled=True` behind a stage.
  Whether a Time condition in a Disabled trigger reads the mission clock or
  the time since it was enabled is not settled by any stock file, and one
  reading made the half hour a no-op while the other put the win after the
  deadline at 18 knots. So there is no timer: the win is the edge. The
  Seahawk objective went, because a Ship's Flight slot may not be named by a
  trigger. Classifying the Type 039C is an optional +10.

**SW07's picket was the same defect.** It placed a named HMAS Perth - Anzac
`Variant8`, on sale from the first window and losable in Weapons Free or
Blind Horizon three days earlier - in a blank mission that would sail her
again undamaged. Its picket is HMAS Arunta (`Variant2`), which the roster
never sells and no other mission places. SW08 and O2 are the remaining
blank-generation missions; their named blue hulls (USS Theodore Roosevelt,
HMAS Pilbara) are not for sale, and O2's note now says, as SW07's and SW08's
do, that nothing of the player's force sails.

**Helicopters were in the wrong sections.** Every helicopter placement in the
stock and workshop missions - 60 of them, 97 counting the copies in the
user's own mission folder - sits in a `[TaskforceNHelicopterM]` or
`[NeutralHelicopterM]` section counted by `NumberOf...Helicopters`. The format
guide lists the family separately, stock names units with
`Taskforce1Helicopter1NameOverride`, and stock conditions test
`Condition_UnitType=Helicopter` separately from `Aircraft`. This builder filed
every helicopter as `Aircraft`, in 16 missions; O1's Seahawk was the first to
fly from an authored section, and it did little. A helicopter family now
exists end to end: the counts, name overrides, trigger references, the
player-force-gone condition (a flying force is `Aircraft,Helicopter`, stock's
comma form), the threat profile, the art, the briefing maps, preflight, and
`check_campaign_coverage.py`, which now fails a helicopter in an `Aircraft`
section or anything else in a `Helicopter` one. VTOL stays in `Aircraft`, as
stock's Yak-38s do. Formations are split by how units move as well: SW05 had
its Seahawk slot in a 0.1 NM Vic with two F-35As, and SW12 had a P-8 with a
Seahawk. A surfaced submarine in company with a ship (SW09's Collins and
Stalwart) is still one formation.

**The RAN's helicopters fly under the Australian flag.** An aircraft's nation
is its squadron's `Nation` - stock's `usn_p-2h_squadrons.ini` gives its RAAF
squadron `Nation=Australia` and `flag_australia`.

- Every MH-60R squadron in every mod is US Navy, and the table that won was
  also the wrong one: 3590477166's, naming a `number` serial submodel the
  winning model does not have (U.S. Navy 2027's `usn_mh-60r` draws United
  States Naval Aviation's sh60 mesh, with `Modex` and `Emblem` submodels).
  SEST Collection Fixes now composes the table from 3737267013's 19
  squadrons, the set written for that model, and appends `Squadron20` - 816
  Squadron RAN, `Nation=Australia`, the Australian flag, the Default livery
  and serials, no US badge. It also ships 3737267013's names for Squadron1-3,
  because 3590477166's load above them and would have labelled HSM-35's
  livery HSM-51. Every RAN MH-60R - the campaign's, the roster's, the RAN
  Fleet air groups', the four RAAF bases' - uses it. (SW08's USS Theodore
  Roosevelt keeps her own US squadrons, as she should.) The unit is credited to U.S. Navy
  2027, the file the game reads.
- The S-70B-2 flew only with the RAN (816 Squadron, the Tigers), and its mod
  names its one squadron "S-70B-2 'Tiger'" - with `Nation=US`. Collection
  Fixes changes that one value in `[Default]` and `[Squadron1]`.

**A dependency the builder could not see.** Taking the MH-60R squadron table
away from 3590477166 took it off the required list, and the review of this
change caught what that broke: ADO Nimitz 2000s' carrier - D2's USS Carl
Vinson - draws its deck Seahawks from 3590477166's
`assets/models/aircraft/usn_sh-60b/` folder, and nothing else ships it. That
mod had been required only by accident. The builder and the coverage gate now
follow every `Resources…Folder=assets/…` path in a placed unit's own file to
the mods that supply it, and credit them as `asset`. On this collection that
adds exactly one row, 3590477166, "a model a placed unit draws", and the
required list is back to 135. One consequence is left open: that prop names
`AircraftLivery=usn_mh-60r`, and the composed table's liveries were painted
for the sh60 mesh, not the SH-60B one the prop draws. If the game applies a
squadron livery to a deck prop the way stock pairs them, Carl Vinson's deck
Seahawks will look wrong; the test card checks it.

**What the files could not explain.** No placed unit in O1, SW01, SW02, C1 or
O2 is anywhere near 0°, 0°, and no position key is missing. The one
structural departure from stock O1 had - a helicopter in an `Aircraft`
section - is gone; a Task Force mission with no anchor was not one (stock's
03B, 07A and 08A have none). Nothing in the mod files names France for the
MH-60R. The squadron table now sets the nation explicitly, which settles the
flag whatever the old source was, and the stray contact goes on the test card
as a watch item, not as fixed.

**Not demonstrated:** a helicopter air-tasking slot has no working stock
precedent. Stock's one `HeloRecon` row is commented out, and its helicopters
are grants in `Helicopter` sections. The slot now sits in the family stock
uses for helicopters, but whether the air-tasking screen fills it is still
the test card's question. Neither is the telegraph mapping for a hull with
no `TelegraphVelocities`: the Delvar is capped by her own 11-knot maximum,
which is why she was chosen.

## Red aircraft that were briefed to come

The airliner that circled one spot in White Water had a sibling problem on
the red side: an aircraft with no `Waypoints` holds an orbit over its spawn,
and several briefings describe a strike, a sweep or an interceptor that
arrives. Every red aircraft without waypoints - 52 in 16 missions, the
campaign's, the dispatches' and the Banda and Northern Front vignettes' -
plus SW11's J-15D (routed, but flying as the #2 of an unrouted leader) was
read against its own briefing, weapons and triggers, and each proposed route
was put to an independent reviewer who checked the timing against the built
positions, speeds and weapon ranges. 34 hold a station their text gives them
(AEW, tankers, pickets, the Bomber Stream's trail) and are unchanged; 18 now
fly, and the J-15D flies its own route.

| Mission | Aircraft | Was | Now |
|---|---|---|---|
| SW05 Weapons Free | JH-7A strike pair | 97 NM out with a 59-NM YJ-91: "the counter-strike arrives" never did | marshals on the SAG's back-bearing, runs onto the frigate's box, goes home; first shot about 14 minutes |
| SW07 Long Way Home | MiG-31 pair | 99 NM from the tanker, R-33 reaches 86 | sweeps to TEXACO's station, turns back to their own AEW and tanker; a tanker that leaves at once is never in reach |
| SW09 Southern Lifeline | Tu-214R scout; Su-30 pair | orbiting 150 NM out, the scout leading the Flankers' formation | the scout looks from 33 NM west of the box and leaves; the pair comes down the outside of the box, Kh-31A window at about 30 minutes; each on its own station |
| SW11 Fujian's Shadow | J-15D anti-ship shooter | routed, but as #2 under an unrouted J-35 leader | its own station; `Strike` now names that station, not `red_air#2` (which after the move would have been the KJ-600) |
| SW12 The First Ship Through | JH-7A spoiler strike | 73 NM out with a 59-NM YJ-91 | opens east, is inside YJ-91 range of the convoy at about 21 minutes, passes over it at about 35-38, goes home |
| D6 Long Reach | J-36 / J-50 pair | orbiting 134 NM north-north-west of the stream, 96 NM off its track; the J-50's PL-15s never reached | onto the stream's line and back down it |
| D7 Before the Lifeline | Bear G; the aggressor sweep | the Bear orbited; "before its release line" was prose | the Bear flies to its release point, where the serial now ends - the Bear inside five miles of it fails `Serial` (O1's `denied` terminal); the sweep goes ahead of it onto the strike detachment; the Badger has its own station so the Bear's Vic no longer drags it at the Tomcats |
| Banda: Foxhound Sweep | MiG-31 pair | 300 NM out | onto the Wedgetail at Telegraph 4: at 3 a Foxhound is slower than the Wedgetail and the tanker at full power, and "speeds you cannot chase" was untrue. Because they can now reach the orbit, losing the Wedgetail or the tanker fails `HVA` and ends the mission - before, nothing failed it, and shooting the MiGs down afterwards still paid it |
| Banda: Triton's Picture | J-16 pair | a CAP over the Aru Islands | "already up and looking for it": down to the Triton's station |

Formation members fly the same route (the SW10 and D1 convention), so a
wingman whose leader is shot down does not go back to circling its spawn.
Every spawn is where it was. The splits used a station per aircraft that
left, and a station per aircraft that would otherwise have been re-seated:
SW09's Ka-27RLD and SW11's KJ-600 and J-20A (the J-20A, re-seated, had
tipped its nearest deck from Liaoning to Fujian). SW11's red air wing no
longer flies as one 0.1 NM Vic of fighters, an AEW aircraft and the
shooter; the J-35, the KJ-600 and the J-20A each hold their own spawn.

## The SM-3 seeker, from the Aegis BMD pack

The `sest-dev/kind-faraday-ctr5h0` branch carries a standalone SEST Aegis BMD
pack for the three Euromod SM-3s. The pack is not ported. It ships the same
three files as Collection Fixes, which consolidation refuses, and most of it
is already here or was decided otherwise later. Its 100,000 ft floor gave way to the user's
150,000 (`e5eda59c`). It kept the 300,000 ft loft ceiling and 300 s of flight,
where this branch lofts to the target and flies 600/600/900 s (`d2547151`).
It cut the IIA's declared range from 1,500 NM to the 729 NM that 300 s
allowed; here the IIA keeps 1,500 and gets the 900 s to fly it. It raised the
IIA's `TypicalTargetAlt` to 800,000 ft because 200,000 sat under the old
220,000 ft floor; it sits inside the band now. Its `LiftFactor` was borrowed
from the PAC-3 MSE, not written for this round by anyone. Its two penalty
values were already the same here.

One part was still missing, and it is now in Collection Fixes. Without the
Anchor Chain preloader, still an unverified install, the SM-3 homed on a stub
in its base file: an 18 s unguided first phase (14 s on the IIA), an 8 NM
terminal handover and a 10 NM / 30° seeker. The author's own values ship in
the Anchorchain Expansion's `ammunition_overwrite/usn_rim-161*_OVWR.ini`,
which only the preloader reads. The builder now folds them in: a 5 s first
phase, a 50 NM handover, a 100 NM / 90° seeker, `LaunchTurnRate=5`,
`TimeLimited=True`, and the overwrite's 90° loft in place of the 85° on the
base file's disabled line, so the round climbs the same way on both installs
(the builder comment gives the reasons). The builder re-reads the overwrite on
every build and stops if the author changes a value it copies, declines or
agrees with, or adds a key. One difference remains by design: with the
preloader, the overwrite still sets the IIA's `MaxFlightTime` to 3000 s on top
of the 900 s this pack ships.

The same branch's SEST Intercept Model pack is now ported
(`integration/intercept-model/`). It restores vanilla's
`ammunition/damage.ini`, and with it `InterceptChanceOutOfAltitudeOverride=0.05`,
a hard 5% cap on any intercept outside the round's altitude band. Before it,
the Tu-95 mod's older `damage.ini` won and lacked the key, and the 7% reading
against supersonic-high targets far below the old 220,000 ft floor suggests
there was no cap. If the cap is live, the 150,000 ft floor holds every manual
SM-3 shot at a target below it to 5%, the 99,000 ft tier the builder names
included; automatic launch below the floor was already off. The floor was
kept at 150,000 in the port: it is the user's choice, and it should be decided
again once the paired builds from `tools/make_intercept_ab_builds.py` have
shown in game whether the cap is live. Nobody has run them yet. The same test
decides D5 Range Week: its Shahed-136s are authored to fly no higher than
300 ft, under the David's Sling Stunner's 500 ft floor and THAAD's 20,000 ft,
so with the cap live neither battery does better than 5% against them, and
losing one launcher or radar ends the trial.

**Not demonstrated:** that Aegis ships now hold a ballistic raid better. An
SM-3 IIA from a Flight III Burke at a DF-21D or DF-26B raid should lock well
outside 10 NM, with no lock/unlock cycling, and a close-in shot should still
turn onto its target with a 5°/s launch turn.

## The buy-list and mission audit

An audit of both rosters and every mission unit list, written before the
Replenishment, A-10C+ and Intercept Model ports landed and re-checked against
the tree after them. What it changed, by group:

**The roster.** The KC-46 was priced at 75 points and no purchase window ever
sold it: `allowed_roster_units()` refused an allowlist naming something the
roster did not price, and nothing refused the reverse. The builder now does
(`check_roster_on_sale()`), and it was run against the unedited roster first -
it stopped the build on `usaf_kc-46a_boom` - before the entry came out. The
unarmed Triton cost 60 against the armed P-8's 45 for the same patrol row; it
is 40 now and the P-8 55, in both campaigns, which keeps the Triton under the
F-35A (45) and the P-8 level with the Growler. Two windows sold aircraft no
row could fly: window 03 sold the F-35A two operations before Weapons Free's
strike row could take it (it goes on sale at window 05 now, where it first
flies), and window 11 sold the Seahawk, Wedgetail and Triton into a carrier
action with only CAP and Attack rows (window 12 sells all three for the
finale). The P-8 stays on sale at window 11: its Bomber role and AntiShip fit
take the Attack row, which the audit had missed. Window 09 has the same shape
- fighters on sale two operations before a fighter row, and on sale again at
window 11 - and was left alone: those are replacement sales of aircraft the
player has been able to buy and fly since window 05.

The independent review of the roster group found two things the audit left
wrong. Window 11's note told the player patrol aircraft were not offered
while the P-8 was, and said helicopters and patrol aircraft "remain
available" in a window that sold neither; it now names the P-8 and says the
Seahawk, Wedgetail and Triton come back before The First Ship Through. And
the bible's opening budget example bought a P-8 before SW01 and two F-35As
before SW02, neither of which any built window sells; it buys only what the
windows offer now.

**Retired types out of 2028.** Rule 3 puts retired types in COLD SEA, and
three had stayed in the 2028 lists:

- SW12's "Eyre Flight" was an S-70B-2, which the RAN retired in 2017, on an
  Arafura, which has a flight deck and no hangar. It is gone; the forces line
  says "HMAS Eyre attached", and the helicopter over the convoy is the
  player's MH-60R on the Ship's Flight row.
- D2's Texaco 60 was a KC-10A, which the USAF retired in 2024. It is a KC-46
  now, still `air#2`, so the Tanker objective reads it; the brief says KC-46.
- D5's counter-launcher was an A-10A. It is the SEST A-10C+ with its own
  AntiArmor fit. D8's Hog 22 already covers that pack, so this is a second
  placement rather than a coverage one; it was chosen over leaving the A-10C+
  in D8 alone because a counter-launcher shot is what the plus pack's
  Litening pod and laser are for, and any 2028 A-10 in D5 would be an A-10C
  of one pack or the other. The A-10A mod is still placed, by D7's exercise
  field.

D7 (July 1988) takes what left: HMAS Adelaide (vanilla
`ran_ffg_adelaide_shorthull` Variant1, in service 1980-2008) in the surface
group, an S-70B-2 as Tiger 01, and the KC-10A as the exercise tanker on its
own track - not on the "high" station, whose every unit the Recovery
objective protects. The vanilla Adelaide's `AircraftSupported` is the
Squirrel-era list and leaves the S-70B-2 out, so the builder homes the
Seahawk on Kitty Hawk, whose file lists nothing; it is named Tiger 01 rather
than Adelaide's flight for that reason. The KC-10A homes on the exercise
field.

The independent review of this group found Tiger 01 on the S-70B-2 file's
Default fit, which hangs four Hellfires beside its torpedoes. The RAN's
Seahawks of 1988 carried Mk 46 torpedoes and sonobuoys, and no Hellfire, so
Tiger 01 flies the file's own ASW fit now. The same review noted that the
real USS Kitty Hawk spent 1988 in her service-life extension at
Philadelphia; D7 placed her before this audit and is an exercise that turns
live, fiction from its first line, so she stays and nothing here claims
otherwise.

**The Growler flies conventional.** Every fit on `usn_ea-18g` hung the AIM-260:
the Growler pack's pylon convention puts it on the fuselage seats (11/12) of
each fit it re-cuts, and its own SEST fits carry it too. Rule 3 keeps JATM in
Future Front, and SW07, SW08 and TS11 flew it anyway, through
`MurderHornetSEADHeavy`; the CAP and Attack rows offered three AIM-260 fits.
The pack now builds `SEST_SEAD120D` on `usn_ea-18g` - `MurderHornetLightsOut`'s
seats with the AIM-120D the upstream file hangs on 11/12, derived from the
same plan so the two cannot drift: 2x AGM-88G, 2x AIM-120D, two wing tanks,
no AIM-260 and no AIM-424. It is the only Growler fit on the CAP and Attack
rows, and Grizzly 31 (SW07), SW08's Growler and TS11's Attack cockpit fly it.
Fujian's Shadow's Growler is Ford's `usn_ea-18g_2020`, which already had a
conventional `SEAD` fit (AGM-88G, AIM-120D); it is named on the unit now
rather than left to the first fit, and that window's Attack row adds `SEAD`
because the cockpit used to match the row only through `SEST_NGJLongRange`.
Southern Reach imports the shared row without it - no such Growler flies
there, and a fit nothing in the flight defines fails `check_flights`. Future
Front places no Growler and is untouched. `check_weapon_employment` and
`preflight` pass with the new fit. The Dingtools Weapon Pack, which SW07's
AIM-260 used to credit, is still reached: through the F-15EX's AIM-120D in
Long Reach here, and through a model the F-35A draws in Turning North for
Southern Reach.

**Supply ships.** The audit proposed supply ships for two missions here, and
one went in.
Western Passage's second tanker was a vanilla merchant (`civ_ms_ritina`, "MT
Passage Trader") in a dispatch whose whole objective is a European
replenishment group; she is **RFA Tidesurge** now (`rn_aor_tide` Variant3,
SEST Replenishment), the rotation's own fleet tanker, in the same slot of the
same group under the same objective - one hull for another, no new target,
no new protected unit. Fujian's Shadow gets neither of the two proposed
(a Type 901 with Fujian, a Kaiser with Ford). A working supplier on the
player's side in the fleet action would let the task group refill its
magazines at sea before The First Ship Through, whose window sells no
ammunition because the finale is fought on what the fleet action left; and a
red replenishment ship in Fujian's group adds a logistics target the brief
tells the player not to chase and nothing the fight needs. Southern Reach and
Red Line's Chinese replenishment ships are the real classes now - see their
build notes.

**The restored intercept table.** SEST Intercept Model puts back the 5%
ceiling on any surface-to-air shot outside the round's altitude band, and the
YJ-83 family skims at 8 ft - under the 10-ft floor of every SAM a Hobart
carries and of the Burkes' SM-2 and SM-6. If the ceiling is live, Blind
Horizon and Fujian's Shadow are harder than they were built to be, and only
the ESSM Block 2 (Anzacs, Lucas) and Ford's RAM are inside the band - Sejong's
RAM has the 10-ft floor too. The test card's 6F re-flies both air defences
and says what each outcome means; Southern
Reach's card re-flies TS09 against the same result. Range Week's David's
Sling carries a note at the unit: its Stunner is the one round of that pack
anything in the campaigns loads, so it is the pack's whole coverage.

## What exists

| Thing | Where |
|---|---|
| The campaign | `integration/campaign/SEST_Campaign/campaigns/sest-southern-watch/campaign.ini` — a `Type=Linear`, native **Task Force Mode** campaign: twelve main missions, four optional operations, two contingencies and seventeen story events - 35 entries |
| Requisition | `player_task_force_roster.ini` (10 priced entries) and `commander_settings.ini` (Australian commander, 20% same-nation discount since 28 Sep) beside it |
| Campaign missions | the eighteen, shipped twice: under `campaigns/…/missions/` for the campaign and under `missions/Southern Watch/` so the mission browser lists them too. The builder writes one copy and `tools/check_campaign_coverage.py` fails if the two ever differ |
| Dispatches | `missions/Southern Watch - Dispatches/` — the eight optional episodes (Allied Dispatch ×3, Red Line, Range Week, Future Front, Cold Sea, plus the relief-perimeter episode) |
| Briefings | a `_briefing/BriefingText_en.xml` beside every mission, with SITUATION / FROM / COMMANDER'S INTENT / TASK / FORCES / TIME, and RULES OF ENGAGEMENT where protected neutrals are on the plot; one TextBlock per paragraph, the task as bullets. Mod provenance lives in REQUIRED-MODS.txt and the coverage report, not in the briefing |
| Source | `integration/campaign/campaign_data.py` (the script) and `build_pack.py` (the machinery) |
| Coverage report | `docs/campaign-coverage.md`, regenerated on every build |

`python3 integration/campaign/build_pack.py` builds it; `tools/build_all.py`
runs it in order with the other nineteen packs and consolidates it into
`SEST_Integration`.

## Where this departs from the bible, and why

- **Twenty-two missions were built, not the five-scenario vertical slice.** The
  request that started this was a campaign incorporating every mod, and
  coverage is only provable once every mod has somewhere to be. The bible's
  own sequencing advice still stands for *playing*: SW01 → SW02 → SW06 is the
  slice to test first, and it is the slice to fix first if something is wrong.
- **SW09 is scored on a service window and a withdrawal, not on
  replenishment.** The bible flagged `ran_aor_supply` as a Teide stand-in with
  no demonstrated supply mechanism. Since 26 Sep 2026 she has one (SEST
  Replenishment At Sea's table, shipped by SEST RAN Fleet: half a mile, 12 kn,
  nothing dearer than 8000 points), and the briefing says what crosses: COLLINS'
  torpedoes, and an escort's missiles up to an NSM, a Tomahawk or an SM-6. No
  condition type can count a transfer, so the scoring did not change: the
  mission asks you to hold the service
  box for thirty-five minutes — `UnitsInTheArea AND Time` on ships that start
  inside the area, the shape of `03 Lifeline at the Edge of the World`
  Trigger8 — and then withdraw. Collins is placed surfaced; *staying*
  surfaced is a house rule stated in the briefing, because no condition type
  reads depth.
- **The bible's four-arrival carry-over for SW02 is not scored.** The win is
  three of four with Kokoda Star among them, and the mission ends ten seconds
  after it fires; a fourth hull two minutes astern in the column can never be
  counted. An objective that cannot complete is worse than none.
- **Armed merchants never fire.** Every `ran_ms_*` hull in a convoy ships
  `WeaponStatus=Hold`: the auxiliary pack's merchants carry guns and, on the
  Super P, Styx, and a "priority ship" that opens fire on its own escort's
  contact is not the mission. The pack stays in the campaign because coverage
  needs it; the guns are decoration.
- **Slot-tagged aircraft carry no `NameOverride`.** Whatever the player puts
  in an air-tasking slot keeps its own name, as every slot-tagged section in
  the shipped campaign does; the briefing never promises a callsign for one.
- **Theatres follow the position evidence.** Each is somewhere a mission in
  this repo (or in the stock game) has already put a unit of that kind — see
  below. That is why the Levant, the Gulf and the Med do not appear: the
  collection's own missions have never sailed there, so there is no proven
  water to snap to.
- **The bible's `plan_type_055_2026` / `plan_type_052d_p3` / `plan_type_054a_p5`
  advice was followed.** `plan_ddg_type_055` and friends resolve to files under
  `mods-source/3594891803/PLAN mod test/vessels/`, which is two directories
  deep and therefore a path the game never loads. The builder's index excludes
  unreachable paths for exactly this reason.

## How positions were chosen

Every sea and land position is **snapped** to a point some already-loading
mission put a unit of that kind on — the repo's own missions plus the stock
missions and the two stock campaigns, about 5,300 distinct points after
de-duplication. The furthest any station anchor had to move is in the coverage
report's header (36 NM at the time of writing, in the western Timor Sea where
the pool is thinnest). Aircraft are airborne and are placed directly.

`lat = MapCenterLatitude + z/60`, `lon = MapCenterLongitude + x/60`: checked
against the two RAAF bases NORTHERN FRONT II places, which resolve to within a
mile of the real Darwin and Scherger.

This makes a ship-on-land placement very unlikely. It does not make it
impossible, and it says nothing about depth, reef or channel width.

## Rig Seventeen would not load (27 September)

The first in-game report of a mission failing to load. `Player.log` (install
snapshot `9208d39e`) ends with a `NullReferenceException` in
`SeaPower.SceneCreator.ResolvePlacedCampaignAircraft`, straight after the
Osprey's and the CH-53's models load. Every reference in the mission resolved;
what was wrong was a flag. The builder wrote `TaskForceModeIncludesAirwing=True`
whenever a mission placed any Taskforce1 aircraft, on the belief that the
Includes flags were display only. The stock task-force campaign never does
that: every one of its missions with `IncludesAirwing=True` has at least one
air-tasking row, and the ones whose Taskforce1 aircraft are authored set
dressing (01, 02, 03B, 04) say `False`. Rig Seventeen said `True` over an
authored Osprey and CH-53 with no row to put the player's aircraft in, and so
did O3 Borrowed Shield. `IncludesAirwing` now follows the rows: `True` only when
the mission emits at least one. Those two missions change; nothing else does.
The same day Rig Seventeen loaded when unlocked straight onto a fresh force,
and that was taken as confirmation. It was not: see the next section.

## Rig Seventeen died again after 01 and 02 (27 September)

Played through from White Water, Rig Seventeen died the same way with the
flag already `False`. So the flag was never the cause: the first crash had
`IncludesAirwing=True` and the second `False`, and both came after a
campaign played through with a small force. The first log shows that force:
one Hobart and the MH-60Rs. The one direct load that worked was onto a force
bought fresh for the mission.

The exception carries the game's own note, `| 1 vs 3`. Rig Seventeen's
authored Osprey and CH-53 were homed on `Taskforce1Vessel3` (HMAS Canberra,
an authored ship behind the anchor), and the force that crashed had one
ship. The reading that fits both crashes and the pass: in a mission the
player's force is generated into, a `Taskforce1VesselN` home base is looked
up among the player's own ships, and a small force has no third one. The
first log also has the slot MH-60R, homed on `Taskforce1Vessel1`, reporting
"is full but has no home base" to Automatic SAR, so those references were not
resolving as written even where nothing crashed.

Stock never writes one. No Taskforce1 aircraft in any mission of the stock
task-force campaign names a Taskforce1 ship as its `HomeBase` - helicopters
included. They name a Taskforce1 airfield (`Taskforce1LandUnit1`) or nothing,
and slot aircraft with no home (06, 08, 09) fly on finite fuel. The builder
now follows that: in a `Generated` or `Replaced` mission a player-side
aircraft is still checked against the decks in reach (a build with nowhere
to land still fails), but it is never written a `HomeBase` naming a
Taskforce1 ship. Airfield homes and missions that launch as authored (SW07,
SW08, O2 and the detached operations) are unchanged. 44 lines go, one per
aircraft, across 38 missions of the three campaigns (12 Southern Watch, 21
Southern Reach, 5 Red Line); nothing else in the files moves. `test_build_pack.py` (`HomeBases`) holds the rule.

Not proven until the mission loads on a carried-over force: test card 7.3a.

## The Campaign Rules button (27 September)

The button at the bottom right of the campaign map opens
`campaign_rules_<lang>.xml` from the campaign's folder. The stock task-force
campaign ships one; these three did not, so it opened nothing. Each campaign
now ships `campaign_rules_en.xml`, built by `campaign_rules()` from the stock
page with only the passages that are not true here replaced: the title and
welcome, the commander section (one fixed nation, and the discount - see
"Same-nation discount" below), ships sold without aircraft
(`ShipIncludesAirwing=False`), helicopters from the first window, no
submarines on sale, and the proficiency table's Survived Missions column read
from `CrewSkillThresholds` (1/4/9/16, where stock's page said 1/2/4/7; since
0.8.3 the game binds that column itself - "Sea Power 0.8.3" below). The
price table, refund percentages and survivor reward are Bindings the game
fills from each campaign's own files. If the stock page changes, the build
stops rather than ship a half-edited one. English only, as stock.

## Steel Highway froze (28 September)

Restarted from the campaign map twice, Steel Highway ran and then stopped
responding in the middle of the mission (Windows: not responding, nearly 8,000
CPU seconds). Player.log ends mid-mission with the P-8 and a Seahawk sent to
their recovery points, and nothing after. The cause was in BepInEx's own log,
which Player.log does not carry: every line of its tail came from one code mod,
the PLA & PLAN & PLAAF AEP (Workshop 3789188689), whose SubAmmunition code
logged `SONO pos` / `SETGEO bomb` with a full stack trace every time a sonobuoy
or bomb moved - every physics tick, for every one in the water. Its
`debug.ini` ships `Enabled=1`; its own comment says to set 1 only while chasing
a missile that self-destructs after launch. The switch had been on since the
mod was first exported (20 Sep), and harmless until BepInEx and Anchor Chain
were installed on 27 Sep and its code began to run. A mission full of
sonobuoys - a P-8 and Seahawks hunting a submarine - is its worst case.

`tools/quiet-mod-debug.ps1` sets it to 0, changing that one value and nothing
else in the file (checked byte for byte against the exported copy), and
`sync-sest.ps1` runs it on every sync because a mod update puts the author's
file back. `capture-context.ps1` now takes the tail of BepInEx's
`LogOutput.log` too, with its size. Not proven until Steel Highway runs its
submarine hunt to the end with the switch off: test card 7.3b.

## Open Allocation (27 September)

Asked for: a switch that puts assets on sale before the story releases them.
The storyline's force-allocation windows stay where they are; what changes is
what each window offers. Each campaign now also appears in the campaign list
as an Open Allocation twin - "Southern Watch - Open Allocation (Royal
Australian Navy)" and the same for Southern Reach and Red Line - and in the
twin every window whose builder is open offers the whole roster: in Southern
Watch, the Hobart, the P-8, the F-35A, the Super Hornet, the Growler, the
Wedgetail and the Triton are all on sale before White Water.

Why a twin and not a switch inside the campaign. The game ties purchases to
the roster and each window's `TaskForceModeAllowedRosterUnits`, and nothing
else: a difficulty preset carries points, airwing, loadout, repair, refund and
crew keys only (the Difficulty* strings under `ui.ini [TaskForceMode]`), and
no stock key conditions an allowlist on a campaign variable. The game's own
start option, Unrestricted mode ("every unit in the game can be purchased,
ignoring the campaign roster and mission restrictions"), is the opposite of a
curated roster. A second campaign entry is the one switch the game can read,
chosen at the start the way its own start options are. The standard
campaign's files are not touched by it, so a save under way reads the same
campaign it did.

What the twin is. `open_allocation_ini()` takes the base campaign.ini and
changes four kinds of line: `[File] Base` (the file's own location), the
campaign's name and description, and in each open window the allowlist (every
roster entry, every priced pick) and the situation, which now opens "Open
Allocation: the whole roster is on offer at this window. The story's
allocation for it reads:" before the unchanged story text. A repair-only stop
keeps its text; nothing is on offer there. Every `MissionFile` and art path
still points into the base campaign's folder - they are StreamingAssets-
relative in every stock campaign - so the twin ships five files (the spine, a
rules page saying so, its own roster and REQUIRED-MODS - retitled for the
twin, and in Southern Watch and Southern Reach with the allied fleet and the
mods it needs added - and a byte-identical copy of the commander settings),
not a second copy of the missions. Points, prices, gates, rewards, one-ship
operations and deployment rules are the base
campaign's; an aircraft bought before a mission has a row or an airbase for
it waits in reserve, as it would have. `check_campaign_coverage` compares each
twin with its base section by section from the built files: it fails on any
other difference, and on any of those changes missing; `test_build_pack.py` (`OpenAllocation`) holds the transform.

Not demonstrated: that the game lists a campaign whose missions live in
another campaign's folder, and loads them - stock never does it, and nothing
in stock says it cannot - or that the twin's progress is saved apart from the
standard campaign's, which it should be as a campaign file of its own. Test
card 6G (G.1, G.3, G.4).

## The allied fleet (28 September)

What the player wanted from Open Allocation was the allied fleet - US, UK,
NATO and Pacific allies - costed and in the Unit Catalog, not only the
campaign's own roster sooner. The Open Allocation versions of Southern Watch
and Southern Reach now sell it beside the campaign's roster, from the first
force allocation; the standard campaigns keep their story roster, and Red
Line's PLAN commander gets no allied fleet.

The list (`integration/campaign/allied_fleet.py`, 106 classes before the
aircraft filter) was curated from the enabled collection: every unit file
whose variants or squadrons are registered to an allied nation, one entry per
class per navy, the most modern and complete file where mods duplicate a
class, picks in service in October 2028 (the files' own `ServiceDate` where
they give one, a stated judgment where they do not) and registered to one
nation. Prices are capability tiers on the campaign's own scale - Anzac 240,
Hobart 480, Arafura 100, F-35A 45, P-8 55, Seahawk 20 - for example a Burke
Flight III 520, a Type 45 460, a FREMM 360, a Virginia 460-500, a Rafale M 50,
a Typhoon 45. They are list prices: the same-nation discount
covers only the four Australian additions (Canberra, Choules, Supply, Collins)
and the campaign's own units. Ships come without aircraft here, so the big
amphibians and the carriers are priced as hulls (Ford 650, Nimitz 600,
Charles de Gaulle 550, Wasp 550, Canberra and Juan Carlos 500, Mistral 450):
no row launches from a bought deck.

Aircraft are sold only where they can fly: `usable_allied()` keeps one only
if some air-tasking row with a cockpit in the campaign takes it and it
recovers in every row that would, by the same deck and field test the build
applies to the campaign roster, and only if every row whose roles take it
offers one of its fits (`check_flights`, run per aircraft and then over the
whole twin roster). That leaves 15 allied aircraft types in Southern Watch's
version and 8 in Southern Reach's; the rest - bombers, AEW,
tankers and gunships (no row asks for them), the allied helicopters (the RAN
decks in the missions list only the MH-60R), and several fighters in the
Tasman (no field in reach of the CAP slots) - are listed by the build with
the reason. Submarines are sold; one sails only in a mission that includes
the owned submarine (Southern Lifeline; Great Australian Bight), and the
rules page says so. Southern Watch's version sells 83 allied units, Southern
Reach's 76.

Two independent reviews of the first cut changed it. Code: the F-16CM had
passed the recovery test while matching the Weapons Free strike row, which
offers none of its fits - the base build refuses that, and the twin's roster
had never been put through the same check; it is now, and the F-16CM, the
E-3G, both E-2Ds, the AC-130J, the MQ-9 and the French Panther go. The twin's
rules pages and spine are built before the pack folder is cleared (and in a
dry run); the gate compares the twin's description exactly, parses roster
lines by section (a uid may carry an apostrophe: Ronarc'h), refuses a unit
priced twice or a base line moved, and reads the twin's aircraft loadout
names. Data: the Ticonderogas out (all retire by the end of FY2027),
Eisenhower out (hull life ends October 2027), the F-35C's disestablished
VFA-101 and the Super Hornet's VFA-115 (now on the F-35C) out, the F124 and
F125 spelled as their files are (`MLU`; the roster now refuses any key its
file spells differently), and prices evened: Zumwalt 480 (its CPS cannot
strike ships), Jeongjo 520, Sejong 480, Iver Huitfeldt 400, Galicia 250.
Display quirks left in the mods: Charles de Gaulle's class name carries
"(2018-2027)", the German Typhoon shows the RAF's "FGR.4", and Mogami's fourth
hull is spelled "Mikma" in its short name.

Left out on review: Dokdo (its file has no flight deck), the Pohang
corvettes (2028 service unverified), and the Freedom LCS, which would show in
game as "Wasp-class (Early)" because its mod's `vessel_names.ini` comments out
the Wasp header. Not in the collection at all, so not for sale: Queen
Elizabeth, Astute, Type 26 and 31, Cavour, the America-class LHA and San
Antonio LPD, Izumo, Kongo, Soryu and Taigei, and any RNZN warship. Upstream
problems found on the way: the K130 corvette's unit files say `Nation=GER`
against `Germany` in its variants, so the build refuses it; the UK Poseidon
squadrons inside `usn_p_8a` say `Nation=uk` in lower case.

Not demonstrated: that the game reads a roster and allowlist of this length
(about a hundred entries; allowlist lines of about 5,000 characters, where
stock's run to about 1,000), that a bought carrier or LHD sails without an
air group as expected, and that a bought submarine waits in reserve outside
its one mission. Test card 6G, G.7-G.9.

## Same-nation discount (28 September)

Asked for: the player noticed an Australian commander got no same-nation
discount. All three campaigns now carry Pacific Strike's own
`SameNationUnitDiscount=0.2`, and so do the Open Allocation twins, which
copy the commander settings byte for byte.

It shipped at 0 on the bible's caution: the Super Hornet, Growler, P-8 and
Seahawk on sale are US-named unit files (`usn_*`), and a discount keyed to
the unit's nation might price them as American. They are not American in the
files. None of the unit files on these rosters declares a nation; the
squadron (aircraft) or hull variant (ship) does - the same place the game
takes the flag from - and every pick on sale is registered to Australia
there: the Super Hornet's Squadron8 and the Growler's Squadron6 (SEST
Growler pack), the P-8's Squadron3 (SEST Allied Fixes), the Seahawk's
Squadron20 (SEST Collection Fixes), and the RAN hull variants. Red Line's
roster is Chinese throughout. Stock does exactly this: Pacific Strike sells
`usn_fa-18a=Squadron7,Squadron8` to an Australian commander with a 20%
discount, and its squadrons file registers both to Australia; its RAN hulls
carry their nation in their variants, as ours do. The prefix table in the
base game's `nations_reference.ini` (`usn` = US) cannot be what prices the
discount: it has no entry for the `ran_` and `jasdf_` units Pacific Strike's
Australian and Japanese commanders buy. So the discount covers every unit on
the three campaigns' rosters (and on Red Line's twin): about 25% more buying
power than the budgets in the bible were set for, and no choice between
nations to make, since they sell no foreign units. The Southern Watch and
Southern Reach Open Allocation twins also sell the allied fleet ("The allied
fleet" above) at list price: there the discount covers the 14 classes
registered to Australia, and the 79 (Southern Watch) and 72 (Southern Reach)
classes registered to other nations cost their listed price.

`roster_nations()` re-reads those files on every build and stops on a pick
with no declared nation (an empty or commented-out `Nation=` counts as
none), a unit whose picks disagree, or a unit file whose own Nation differs
from its picks'; the rules page's new National Purchase Discount section
uses the stock line and its `{Binding SameNationDiscountPercentText}`, then
says the discount covers the whole roster - or, where foreign units are on
sale (the Southern Watch and Southern Reach twins), how many classes it
covers, with the rest counted by nation (Southern Watch's: "from USA (24),
France (10), ...") rather than named. `test_build_pack.py` (`SameNationDiscount`)
holds it.

Not demonstrated: that the game reads a unit's nation for the discount from
the squadron and variant, as it does for the flag (test card G.6), how it
rounds (Pacific Strike's changelog: the discount always takes at least a
point off), whether repairs are charged on the discounted or the listed
price, and whether a campaign already under way picks the new value up.

## Sea Power 0.8.3 (2 October)

The game updated to 0.8.3 Build 261001 (1 Oct; the repo had reasoned from
0.8.2 Build #358 of 20 Jul). Between the two the game overhauled gunnery and
fire control, tweaked CIWS and gave the Phalanx a sustained-fire cooldown,
moved several ships' CIWS to APDS rounds, fixed bombing accuracy and
campaign persistence, added SA-N-1D, SA-N-3B and SA-N-4C, the Type 021,
the Spruance VLS, Bunker Hill, the Improved Victor III, three JMSDF
destroyers, the RAAF Nomad and Searchmaster, a KC-10 and a Scud-B launcher,
and gave the campaign rules page bindings for the Survived Missions column.
The vanilla export is 4,051 text files (3,851 before): 200 added, 1,080
changed. `tools/check_vanilla_drift.py --since a4d3c1c1` reads it: 32
files SEST packs override, every one derived by a builder; no merged-key
clash; 198 fielded units changed, none removed; 41 new unit files.

Rebuilt from scratch, five builders stopped where their own checks said,
and each was rebased (`docs/packaging-and-recovery.md`, *After a Sea Power
update*, has the record):

- `build_pack.py`, `campaign_rules()`: the stock page's Survived Missions
  cells are now `{Binding <Level>CrewSkillSurvivalRequirement}`, which the
  game fills from each campaign's `CrewSkillThresholds`. The build used to
  write 1/4/9/16 into the page in place of stock's 1/2/4/7; now it only
  proves the five bindings are there. The player sees the same numbers,
  from the game rather than from us.
- Collection Fixes, `MISSING_SENSORS`: the Side Globe jammer that Varyag
  and the improved Kirov mount is now cloned from the game's own new
  `[Gurzuf] # Side Globes` (S/C/X/Ku, JamChance 0.3, a big sensor with
  noise-jamming power) instead of the Sovremenny's smaller `Start_ECM`. A
  section header may now carry a comment, and the clone reads past it.
- Intercept Model: the game's `damage.ini` gained
  `InterceptChanceFloor=0.05`. The Tu-95 mod's copy predates it, so it is a
  ninth key that copy lacks; `VANILLA_SINCE` pins it and the shipped file
  carries it. The eight intercept keys and the VeryLarge decision are as
  they were.
- SEST Replenishment: the Sacramento, which the Type 901 is cloned from,
  fires `usn_cal_20mm_apds` from its Phalanx since the 28 Sep build, so the
  refit's magazine slot is keyed on that round and the Type 730s still get
  their 30 mm. The nine vanilla-forked supplier hulls took the game's new
  `[CombatSystems]` blocks and area values; `check_pack_fidelity` proves
  every byte of difference is the intended insertion.
- Allied Fixes: the Apache mod's 2 Oct update put the Sea Apache on
  `usn_agr-20b_apache` like its Army airframes; the Redback fit it derives
  is byte-identical to before.

One more thing moved without a builder noticing, which `preflight --all`
caught: the game's Tu-95RT no longer offers a Default fit, and four of them
in the editor missions `01 Threads` and `02 Hot Gulf` named none - the
editor's map panel crash this repo already had a fix for
(`fix_loadout_variants.py --all --write`; they now name `Recon`).

Two files joined the pack, so it is 1203: the early Wasp (Modern US Navy
released it from a Pending folder, so Replenishment meters it like the other
LHDs) and the SY-1 (the Type 021 the game added carries it, so it is now a
ship-carried missile the metering tags). Nothing new is placed in any
campaign: every unit 0.8.3 added is a 1960s-90s type, out of service in
2028. Every pack now declares `ApproximateVersion=0.8.3`
(`check_game_version.py --bump`); 23 Workshop mods declare 0.8.2, which the
Mod Manager accepts as a lower patch, and Coordinated Strike Tool's range
admits 0.8.3.

The same export updated Euromod (433 files: 270 rounds re-tuned and a new
`vessels_overwrite/` folder of 132 `#!extend` files, one per hull, each
assigning a combat system - see below), its Anchorchain expansion,
Identify Expanded, Modern US Navy (the ES-3A moved to US Naval Aviation),
US Naval Aviation, the German Navy, Flight Deck Ops, the F-22, the MiG-29
family, the Apache and the Fury. Every gate passes on them.

**What the announcement adds (3 October).** The Steam post for 0.8.3 names
the systems behind the file changes, and five of them bear on this pack:

- *OODA and combat systems.* A ship's `[CombatSystems]` block names a
  profile in `systems/combatsystems.ini` (new; 55 vanilla profiles) that
  sets reaction time, datalink tier and the number of contacts its CIC
  works and evaluates at once; 126 vanilla hulls declare one, Euromod
  assigns 162 by `#!extend`, and the game derives a hull that declares
  nothing from its service year, with default slots. The pack's hulls
  inherited whatever their donors had: the Hobart `AEGIS_Mk7` (vanilla's;
  reaction VeryFast, 100 contacts, 4 evaluated), the Arafura, Canberra and
  Choules `NTDS` (Medium, 10, 2 - a 1960s profile their Spanish donors
  chose), Supply `None` (VerySlow, 2, 1), and the Anzac, Collins and Mogami
  nothing. Not yet assigned: the Anzac's 9LV/CEAFAR fit, the Collins and
  the Mogami's OYQ-1 all have Euromod profiles of the right shape
  (`9LV_Multirole_MLU`, `Submarine_Integrated`, `OYQ_Integrated`: VeryFast,
  96, 5), and SEST Collection Fixes can ship clones of them under SEST
  names as it does for sensors, so the pack does not depend on Euromod's
  ids. Done on 3 October - *Combat systems and the CIWS model*, below.
- *CIWS.* Bursts are now simulated as projectiles: the Phalanx section
  gained `FireControlMode`, `ReactionTime`, `BurstTime`, `VolleyMaxRounds`
  and `VolleyCooldown`, and its `MissileInterceptChance` fell from 65 to 40
  as a "calibration anchor". The PLAN Pack's six CIWS sections (Type 730
  and 1130, last updated 15 Aug) keep the old keys and an anchor of 85;
  under the new model that is a strong Chinese CIWS until its author
  retunes it. Red Storm's seven carry no old key. Nothing SEST ships
  defines a gun system; a `systems/weapons.ini` with retuned `[Type_730]`
  and `[Type_1130]` sections would win the merge from the top of the order.
  Done on 3 October, and the same look found something larger - below.
- *Night.* "Ground attacks at night now require suitable vision
  capability": vanilla's visual sensors carry `NightVisionLevel` (0 for
  eyes, 0.25 for a modern sight, 0.3 for the B-52's AVQ-22). The F-15EX
  mod's Sniper and LANTIRN pods already declare `NightCapable=True` and
  `NightVisionLevel=1`, so The Open Door (04:50) and Long Reach (01:20)
  strike as before. The game's own tooltip now flags a daylight-only
  aircraft or fit at night; none is expected.
- *Player aircraft return to base on Weapons Hold.* 21 campaign missions
  start a player aircraft at Hold - every Wedgetail, Triton, tanker, the
  E-2D, Rivet 21, Red Line's KJ-500, Y-9 and Z-9s - because Hold was the
  state that never fires. Whether the game now sends a pre-placed Hold
  aircraft home, or only one the player switches to Hold in flight, the
  first play of Approaches shows; if it is the former, every one of them
  moves to Tight, which for an unarmed aircraft is the same thing.
- *Standing Orders.* "Ships on Weapons Tight engage hostile aircraft" is
  off by default now (the tooltip says it made ships radiate), and "Ships
  use anti-ship missiles on Weapons Free" is a new toggle whose default
  the files do not show. Both are the player's to set, and the test cards
  say so.

Smaller: the game dropped its KC-135A and Tu-16N stubs (the KC-135 was
"replaced with proper KC-10", a 1971 airframe the USAF retired in 2024).
The export cannot delete, so both were removed from `_vanilla/original` by
hand on the announcement's word, and the drift tool then found what
depended on them: the three RAAF bases that generated a KC-135A detachment
(Tindal, Learmonth, Butterworth) now generate the KC-135 Stratotanker mod's
airframe, which Long Way Home already fields; Southern Watch D7's Badger
tanker comes from the Tu-16N mod, not the stub, and stands. The game also
removed `IdentificationRate` from every ESM set "as it was causing issues";
the Rivet Joint mod's four sets still carry it. Aircraft radar cross
sections and air-search radar gains were rebalanced together in vanilla,
and modded aircraft keep their old, smaller values. Task Force Mode gained
Workshop authoring support and a Workshop tag, and the stock campaign's
missions now carry `DynamicGeneration*` keys for a persistent theater
roster, which an authored campaign may adopt later. "Fixed missing
briefings for generated missions" is the bug that left the briefing pane
blank in these campaigns before the charts were drawn.

## Combat systems and the CIWS model (3 October)

The two decisions the section above left open are taken, and one thing the
CIWS data turned up on the way is fixed. The rule throughout is the one
Collection Fixes has always run on: nothing invented. Every profile is a
clone of a Euromod one; every CIWS keeps its author's numbers wherever the
model did not change them; and where a mod's stale copy hides the game's own
text, the game's text is restored. The shared tables and helpers are
`integration/common/combat.py`; the collection-wide part is in
`integration/collection-fixes/build_patch.py` (`STALE_VANILLA_COPIES`,
`CIWS_RETUNE`, `EXTENDS`). The pack grows from 1203 to 1265 files: 60
extend files, a `combatsystems.ini` and a `weapons.ini`.

**Combat systems.** SEST Collection Fixes ships `systems/combatsystems.ini`
with 23 profiles under SEST names, each cloned from the Euromod profile of
the matching shape, so nothing depends on Euromod's ids and a build stops if
anyone starts defining a `SEST_` name. One key is edited, and it is marked
on each clone that carries it: the three Russian profiles sit one datalink
tier below the NATO body they borrow, which is where vanilla's own
calibration puts every Soviet profile against its NATO contemporary
(Alleya_2M, Lesorub and Sapfir_U are tier 4 against AEGIS_Mk7 and NTDS's 5;
Koren 4 against ADAWS's 5). Vanilla names are used directly where vanilla
models the ship or its generation.

Who gets what:

- *RAN Fleet*, set by its builder on the hull: Hobart `SEST_AEGIS_BL9`
  (was vanilla's AEGIS_Mk7; the RAN's Aegis refresh), Anzac `SEST_9LV_MLU`
  (declared none; Saab 9LV Mk3E with CEAFAR), Canberra and Arafura
  `SEST_9LV_Compact` (were NTDS, the 1960s profile their Spanish donors
  chose), Supply `SEST_9LV_Compact` (was None - VerySlow, no datalink; the
  Supply class carries 9LV). Choules keeps the Galicia's NTDS: datalinked
  and slow is what a dock landing ship without a modern CMS gets, and the
  real ship's fit is not on record. Collins takes none - see submarines.
- *Mogami*: `SEST_OYQ_Integrated`, her OYQ-1.
- *Sixty mod hulls the campaigns field that declare none* get one by
  `#!extend`: a `vessels_overwrite/<id>_CombatSystems_SEST.ini` per hull,
  carrying only the block. This is the mechanism Euromod uses on 162 hulls,
  132 of them other mods' (Modern US Navy's 75, the German, British, Dutch,
  Italian, Danish and JMSDF packs), from higher in the order than the hull -
  which is the SEST position. The sixty were computed, not chosen: every
  vessel the built missions place whose winning file declares no
  `[CombatSystems]`, is not already extended by a mod, is not an alias and
  is not a submarine. Red: the PLAN Pack's 052D (`SEST_PLAN_AAW`), 055
  (`SEST_PLAN_Cruiser`), 054A and the 2017 Shenzhen (`SEST_PLAN_Multirole`),
  056A (`SEST_PLAN_Compact`); Liaoning, Shandong, Fujian and the Type 004
  (`SEST_PLAN_Carrier`); the Type 071 (`SEST_PLAN_Amphibious`); Red Storm's
  twelve PLAN hulls likewise; the Luda and Sovremenny take vanilla's own
  `ZKJ-3` and `Sapfir_U`; Russian Navy 21's Gorshkovs and Project 21956
  `SEST_RU_AAW`, the Grigorovich `SEST_RU_Multirole`, the Steregushchiy and
  Gremyashchiy `SEST_RU_Compact`; the Kuznetsov and Varyag `Lesorub_55`, the
  improved Kirov `Alleya_2M`, the Slavas `Lesorub_1164`, the Nakhimov refit
  `SEST_RU_AAW`; Iran's Peykaap vanilla's `Titanit`. Blue: the Ford and the
  2000s Nimitz (`SEST_SSDS_Carrier`), the 2027 Ticonderoga, Red Storm's
  Hobart and Korea's KDX-III (`SEST_AEGIS_BL9`), the 2030 Flight III
  (`SEST_AEGIS_BL10`), the FFG Upgrade Adelaide (`SEST_9LV_Compact_MLU`),
  the French carrier, Horizon, FDI, Aquitaines and La Fayettes (SENIT,
  PAAMS, SETIS and compact clones), the Daegu, the old Type 23
  (`SEST_CMS_SeaCeptor`), and the deprecated Seahawk mod's Spruance and
  Perry, which get back the `NTDS_TAS` and `Mk92_CAS_Link14` vanilla gives
  the same hulls. The 2027 Burkes are aliases of Modern US Navy hulls
  Euromod already extends, and take nothing of their own.
- *Submarines: none.* Vanilla assigns none of its 46 a profile, and
  neither does this pack, for the RAN's Collins or anyone's. Euromod does
  assign its Type 212As one; the test card asks what the game shows for a
  boat that declares none before that is reconsidered.

The guards: a hull that starts declaring its own system, that another mod
starts extending, that becomes an alias or a submarine, or a donor profile
that changes shape, stops the build and names itself.

**CIWS: what the data turned up first.** Four aircraft mods - Tu-95MS, MORE
SU24M VARIANTS, KC-135 Stratotanker and Su-30SM2 - each ship a 213-section
copy of the game's `systems/weapons.ini` whose only addition is one
section, `[SA-26]`. The four copies are identical to one another on every
shared section, and the copy predates 0.8.3: 67 of its sections differ from
the current game, every one by keys the game *added* (the burst model on
`AK630`, `MK15` and `AK230`; `ForceMoveToLoadPosition` on the Mk 10, 11,
13, 22 and 26 and the SA-N-1, 3 and 4; `FireRate` on ASROC and the Mk 13),
none by a key removed or a value changed. `systems/` merges section by
section and the copies outrank vanilla, so on every vanilla AK-630 (76
fielded mounts), Phalanx Block 0 (39) and AK-230 (10), and on every stock
gun and launcher among those 67, the 0.8.3 model was not being read at all.
Collection Fixes now ships the game's own text for 66 of them (the 67th,
SA-N-9, the Kuznetsov mod redefines above the copies and keeps). The build
checks the four copies still agree with one another, so a real edit by one
of those authors stops it rather than being overwritten, and a section some
other mod deliberately redefines above the copies is left to that mod.

**CIWS: the retune.** The 22 mod CIWS the campaigns field are moved onto the
0.8.3 keys - `FireControlMode`, `ReactionTime`, `BurstTime`,
`VolleyMaxRounds`, `VolleyCooldown`; `MinimumMissileInterceptTime`, which
the game dropped, removed - with their own rotation rates, fire rate,
magazine, reload, effects and audio kept. A self-contained mount (dome radar
or EO on the gun) takes the Phalanx pattern, closed-loop; an off-mount
director takes the AK-630 pattern. The anchors sit on vanilla's own ladder:
Phalanx Block 0 40, Block 1 (APDS) 50, AK-630 20, AK-230 10, a hand-aimed
20 mm 2.

| Section | Was | Now |
|---|---|---|
| Type 730 (PLAN Pack's two; the Type 071's own) | 85 / 85 / 75 | 55; the PLAN Pack's 15 s "reload" of 2900 rounds becomes 180 |
| Type 1130 (PLAN Pack's two) | 102 | 60; the 25 s reload becomes 240 |
| Phalanx Block 1A (`MK15B`, `eu_MK15B`) | 85 | 50, vanilla's Block 1 |
| Phalanx Block 1B (`MK15C`, `eu_MK15C`) | 90 | 55, one step above |
| Goalkeeper (Euromod) | 80 | 55 |
| Kashtan (the Kuznetsov mod's; 32 fielded mounts name it), Red Storm's CADS-N-1, the improved Kirov's Kortik gun, Russian Navy 21's Kortik-M | 95 / 60 / 50 / 95 | 45 |
| Palash | 95 | 50 |
| AK-630M | 80 | 25, the AK-630 pattern with a better director |
| Millennium Gun (35 mm AHEAD) | 90 | 35 |
| MLG 27 | 25 | 15 |
| Narwhal and F2 20 mm, DS30M Mk 2, Mk 38 Mod 4 (remote autocannon in CIWS slots) | 50 / 50 / 70 / 70 | 5; the two Euromod guns declare no CIWS module, so only their anchors move |

The build stops the day a mod adopts the new keys itself, so each entry is
deleted then rather than retuning the author's retune. Vanilla's Phalanx
Block 0 is what the Anzac mod names (`MK15`: anchor 40, 3000 rounds a
minute, 989 loaded); the ASMD Anzacs carry Block 1B, so the RAN Fleet
builder points the mount at vanilla's `MK15_Blk1` (Block 1, APDS: 50, 4500,
1550), on the same burst model. Left on the old keys, deliberately: the
light guns whose anchor is already -1 or under 10 (DS30B, DS30M, the 25 mm
KBA, the machine guns), which the model barely touches.

**Not settled here**, and on the test cards: that an extend shipped by the
SEST pack lands on a hull another mod ships (Shift+Y on a 054A reading SEST
PLAN Multirole proves it; the game's default disproves it, and the sixty
files then move into the hull copies SEST Replenishment already ships);
how the retuned Type 1130 and Kashtan behave against a salvo; what the
game shows for a submarine. The sensors file has the same shape of problem
on a smaller scale - two of the four aircraft mods also carry a stale
`sensors.ini`, and a sensor-overhaul mod redefines 202 vanilla sensors on
purpose - and is left for a round of its own.

**Auto Time-on-Target retired.** Unsubscribed on 3 October (Coordinated
Strike Tool is the one salvo planner kept); removed from the canonical
order, the catalogue's active set, the code-mod tier and the campaign
excuses, so the sync stops re-adding it. `check_inventory` is red on it
until the next export prunes its folder.

## Seven mod updates and 0.8.4, the same afternoon (3 October)

The export that followed the morning's build brought more than the two
updates Steam had shown: Euromod Main, Modern US Navy, US Naval Aviation,
the PLAN Pack, the PLA Land Unit Pack, the J-16 (retitled *Rebuilt J-16 /
J-16D*) and Buildings and Objectives, and the game itself had moved to
**0.8.4 Build 261002** on 2 Oct (two fixes: the mod menu's folder picker,
null references). Every pack declares 0.8.4 (`check_game_version.py --bump
0.8.4`). The one that mattered was the PLAN Pack, and it mattered because it
did, on its own, most of what the morning's section did for its hulls:

- **It ships its own `systems/combatsystems.ini`** - the ZKJ-4/5 and ZBJ-1
  families (ZKJ-5A on the 054A: Fast, tier 5, 64 contacts; ZBJ-1A on the
  052D: VeryFast, 100; ZBJ-1B on the 055 and its Fujian: VeryFast, 180;
  ZKJ-5B on the 056A: Fast, tier 4, 24), two datalink-only profiles for
  small units and AEW profiles for the KJ-500 and KJ-600 - and **every hull
  now declares a `[CombatSystems]` block**. The eight `#!extend` files the
  morning gave its hulls would have doubled the block, and the guard written
  for exactly this stopped the build and named them; they are gone (the
  052D, 055, 054A, Shenzhen, 056A and Fujian entries, with the
  `SEST_PLAN_Compact` profile only the 056A took). The SEST PLAN profiles
  remain on the hulls that still declare none: Red Storm's twelve, the
  Liaoning and Type 004, the Type 071, the Chinese Navy mod's Luda and
  Sovremenny. For comparison the PLAN Pack's author rates the 054A one
  grade below the Euromod-shaped `SEST_PLAN_Multirole` (64 contacts against
  48, but Fast either way) and the 052D the same as `SEST_PLAN_AAW` in band
  and a little under in contacts; a PLAN frigate and a Red Storm one now
  carry systems from two authors, which is the collection as it is.
- **It moved its Type 730 and 1130 onto the 0.8.3 keys itself**: the 730 at
  anchor 65 (closed loop, 1000-round volleys, 5 s), the 1130 at **90** with
  `ReactionTime=1.5`, 2800-round volleys, 7 s cooldowns, a 5500-round
  magazine and a 20-minute reload - a strong CIWS by the vanilla ladder
  (Phalanx Block 1 is 50), and the author's call under the new model. The
  morning's entries for the four sections (55 and 60) went the way the
  policy says: the guard stopped on the first and they were deleted rather
  than retuning the author's retune. The Type 071 mod's own copy of the 730
  is a different mod, still on the old keys, and keeps its SEST retune.
  Eighteen mod CIWS stay retuned, 66 vanilla sections stay restored.
- **It ships a Fujian** (`plan_cv_type_003`, 2309 lines, with animations and
  the same air wing of its own new J-15T, J-15DT, J-35, KJ-600 and Z-18s
  that the Fujian mod gives it) above the Fujian mod in the order, so the
  carrier the game reads in SW11, TS09 and RL01 is the PLAN Pack's. The
  campaign builder's roster rule caught it twice ("rostered for
  fujian-cv-18, but the game reads nothing of its from this unit") and both
  roster lines now credit the PLAN Pack. The Fujian mod stays subscribed:
  it is still the only source of 25 PLAAF rounds (PL-10/15/17, KD-88, the
  LS-6 family, YJ-91...) that the J-35 and others fire, which is what keeps
  it reached. One thing the new hull carries that the gates see: its two
  FQF-2500 decoy magazines name a round (`plan_f3200a`) no enabled mod
  defines, at a count of zero. Nothing to fire and nothing lost; waived in
  `check_weapon_employment.py` against that unit and that defect only.
- Also in the PLAN Pack: the KJ-500, Y-8/Y-9 family, Ka-28/31 and Z-9 files
  rewritten, its sensors file rewritten, most rounds re-tuned, new Z-8J.
  Red Line's KJ-500 and Y-9s and the Z-9s the missions place all still
  resolve (`preflight --all`, `check_weapon_employment`).

The others, smaller: US Naval Aviation added a P-8A with HAAWC (its own
`usn_p-8a`; the campaigns' Poseidon is the stock `usn_p8`), renamed its
Osprey `usn_v-22` to `usmc_mv-22b` (nothing SEST ships named the old id;
Modern US Navy's Wasp now embarks the new one, and the Replenishment copy of
the early Wasp follows it) and touched the F-35B. Euromod turned its SM-2
Block II stub into a full file. The J-16 was rebuilt with a J-16D beside it
and its own PL-10/15/17 and YJ-91 under `plaaf_j16_` ids; Red Line's Enclave
11 and 12 and the Banda vignettes still fly it, AirToAirLongRange intact.
The PLA Land Unit Pack re-tuned its rounds and the HQ-19 the land-defence
builder reads through the extend chain; the Spratly layers rebuilt the same.
Modern US Navy's Wasp gained two accountable categories for its flight deck.

The pack is 1257 files (1265 less the eight PLAN Pack extend files). Every
gate is green with the inventory's known reds; the catalogue carries the
J-16's new title, the PLAN Pack's takeover and the Fujian mod's supersession.
Separately, the snapshot carries the first Task Force Mode save on record -
Southern Watch (Open Allocation), mission 2 done
(`docs/packaging-and-recovery.md`, *What the update does to a Task Force
Mode save*).

## The first play test: the Situation button, a datum, the cable dates, and the Rafale (3 October, evening)

The player's first Task Force Mode run - Southern Watch, four entries deep
(White Water, The Missing Beacon, Steel Highway, After the Wake), the save
reopening and continuing after the day's two rebuilds - came back with three
notes and a decision. Each is in the build now.

**Steel Highway's submarine was on the plot from the first minute.** By
design, as it turned out: the save shows The Missing Beacon completed, and
finding Torres Light's recorder sets `O1BeaconFound`, which Steel Highway
answered with a `Classify`-level reveal held for the whole mission - "the
contact is classified on the plot and held there for the operation". That is
too generous for a mission whose premise is the time it takes to classify
that contact. The model now is the stock Sub Duel's "Initial contact": a bare
reveal (a detection, no class) that holds fifteen minutes and ages off. The
bridge record puts a datum on the plot and classification stays the
player's; the intel line says so. The Quiet Passenger's Kiwi 01 reward, the
same shape, is treated the same way. `reveal_if` entries take a `level` ("" for
the bare reveal) and a `time` now; the two other reveals (Fujian's Shadow's
escorts, Identify, held) are as they were. The report also said "two
submarines"; the mission places one, the briefing says one, and what the
second symbol was - the revealed track beside a sonar contact on the same
boat, most likely - is on the test card to look at again.

**The Situation button.** Since 0.8.3 a linear campaign may name an enemy
roster file, and the Situation button at the bottom right of the campaign
screen then shows the enemy theatre ORBAT and tracks it as units are
encountered or destroyed; the stock Pacific Strike's file also feeds its
dynamic unit generator, which these campaigns do not use. Every campaign and
twin now ships `enemy_theater_roster.ini`, generated from the units its
missions place (`enemy_roster_ini` in `build_pack.py`): every Taskforce2
vessel, submarine, aircraft and helicopter, in the stock file's sections -
`SurfaceMajorFlagships` for the big hulls with a flight deck (the carriers,
the Type 071, a Kirov), `SurfacePersistent` with exactly the variants the
missions use, `SubmarinesPersistent`, `AircraftReusable` with the squadron
and the largest flight a mission flies - filed under the nation the unit's
own variant or squadron registers it to, so Red Line's coalition sorts into
RAN, USN, JMSDF and RNZN. An unarmed hull (the merchants and fishing boats a
mission places on the enemy side as traffic) is not order of battle and is
left out. The PLAN block carries the stock `ShowOnlyClassName=True`, class
and hull number rather than names. Nothing is hidden. `campaign.ini` names
the file in `[DynamicUnitGeneration]`, the stock key. Whether the panel
tracks a pre-placed unit's loss (the stock notes say story units are
tracked; ours are all story units in that sense) is the test card's to
settle: sink Steel Highway's Type 039C and look.

**The date-time groups stay military.** The Port Moresby cable reads
`DTG: 210600Z OCT 28` - day 21, 0600 Zulu, October 2028, the form a signal
carries - and the first play read it as the 28th. The build briefly wrote the
year in full; the player chose the realism, so every date-time group in the
three campaigns is back to the military form, and this note is where a
reader who meets `OCT 28` can look it up.

**The Rafale is retired.** The Dassault Rafale mod left the player's
subscriptions on 28 Sep, and on 3 Oct the player retired it rather than
resubscribe. No other mod in the collection ships a Rafale (the French Navy
pack's Charles de Gaulle names the Rafale mod's `fr_rafale_m_l` and tanker in
its air group, and sails without fighters until one returns). Gone with it:
D3 The Relief Ship's Rafale CAP pair and its station (the group's Harriers
and air defence cover the window), D6 Long Reach's Rafale 41 escort (four
escorts remain), the allied fleet's Rafale M and B, the Banda vignette
*Rafale, Timor Gap*, and the SEST Rafale F5 pack, which existed to give the
late Rafales JATM, MALICE and LRASM fits (`docs/packaging-and-recovery.md`,
*Retired packs*; git holds everything). The pack is 19 packs and 1260 files,
and the four checks that were red on the committed tree for the Rafale are
green; no rebuild needs the archive any more. (For one build: the evening's
export brought a mod that ships the same Rafales, and the next section has
them back.)

**The Ford's Seahawks.** Found on the way: Modern US Navy's 3 Oct update
dropped `usn_mh-60r_26`, its Seahawk under the 2026 fit, and the Ford mod's
air group embarks ten of them - so the carrier Fujian's Shadow fields, and
the NF3 scenarios, would have sailed with no helicopter. The Replenishment
copy of the Ford, which is the file the game reads, now embarks ten
`usn_mh-60r` instead (`AIRGROUP_FIXES` in `common/ras.py`, applied and
proved the way `STORE_FIXES` repairs a broken round id); the Banda vignette
that gives the Ford its own air group names the same. Your NORTHERN FRONT
and Banda Front editor missions carry the old id in their Ford air groups
and place no such helicopter themselves, so the game drops the line.

## Four new mods, the Chinese loading tips, and the Rafale back (3 October, late evening)

The player's evening export (`bb2316d4`) carried four new subscriptions -
Moloti's Armed Merchantmen (3485917612), French Air Force (3758943352), the
MV-75 Cheyenne II (3810611344) and the PLAAF Aircraft Pack (3812111085) - and
updates to Euromod (fifteen Italian rounds), both Italian navy mods and Modern
British Navy (combat-system blocks on their own hulls, which Euromod also
extends; their problem, noted), JMSDF and the B-1B. Every guard held through
the rebuild; this section is the four new mods, and one fault the first screen
after subscribing showed.

**Every loading-screen tip was in Chinese.** The player's report, and the
cause is small: the PLAAF Aircraft Pack ships
`language_en/loading_tips_plaaf.ini`, a `[LoadingTips]` section of eleven
tips and a header written in Chinese and filed under the English folder. The
game merges language files key by key across the load order whatever the file
is called, and the section's keys are positional - `Count`, `Header`,
`Tip001`... - so the mod's eleven keys landed on vanilla's and the game read
them. (The same author's PLAN Pack files its tips under `language_cn/`, where
they belong.) The fix follows the merge rule the other way: SEST Collection
Fixes now ships vanilla's own `language_en/loading_tips.ini` text word for
word, from the top of the order, so every key the mod overwrote has its
vanilla value again (`build_loading_tips()`); the header names the offender
while one exists. The same positional rule is what lets SEST have tips of its
own, which the player asked for: eight `SEST:` tips (the Situation button,
how to read a date-time group, what a datum is, what a SEST fit is, Open
Allocation and the discount, side operations and losses, the survivor
reward, the two files beside each campaign) are numbered from vanilla's
Count upward at build time - Tip020 to Tip027 behind the game's nineteen,
Count raised to 27 - so a vanilla update that adds tips pushes them along
instead of colliding, and the build stops if vanilla's numbering is ever
not 1..Count. The drift tool learnt the shape: a language section a pack
carries in full (every vanilla key present) MIRRORS a key vanilla adds at
vanilla's value, and reports a key vanilla adds over one of the pack's own
as MASKED - a rebuild renumbers; a section that only adds names is still a
clash on every new key, because those builders stop on the name. The one Chinese line
in the mod's `ammunition_names.ini`, the H-6J's RKL-600 ESM pod, gets an
English name from the same pack (`ENGLISH_STORE_NAMES`), and that writer too
stops the build the day the mod names it in English itself.

**The Rafale is back.** The morning's retirement lasted one build. The French
Air Force mod ships the whole Rafale family under the ids the Dassault Rafale
mod used - `fr_rafale_b/c/m`, the `_l` late standards, the `_l_nuclear` pair,
the M tanker, `exp_rafale_*` export versions - with the Mirage 2000 family,
the A330 MRTT for several nations, the A400M and a French MQ-9A: 160 aircraft
files and 39 rounds. Everything retired at 06:56 came back on it: D3 The Relief
Ship's CAP pair and station (on this mod's `fr_rafale_m`), D6 Long Reach's
Rafale 41 (SEST Rafale F5's `fr_rafale_m_l`, flying the AIM-260 fit - it is an
escort, and the Enterprise is there for its deck), the allied fleet's Rafale M
and B Late (three and nineteen squadrons, as before), the Banda vignette
*Rafale, Timor Gap*, and the SEST Rafale F5 pack, whose builder reads
`3758943352` now. The French Navy pack's Charles de Gaulle has her
`fr_rafale_m_l` and `fr_rafale_m_tanker` air group again. One thing changed
under the pack: the new mod's Rafale M Late hangs ONE SCALP or ONE Exocet on
the centreline (station 11, seat `AM39Center`) with wing tanks on 7/8 and the
outer MICA rails empty, where the old mod hung two under the wings. The pack
follows the author's geometry, so the M's `SEST_MALICE` and
`SEST_AntiShipLRASM` carry one round each on that seat, already with two
tanks, and have no three-tank `_ER` twin; the land-based B and C Late keep
two under the wings and all six fits. The vignette's four Rafale M fly
`SEST_AntiShipLRASM` (one LRASM, two tanks) and its brief says so. The
derivations are per airframe now and the builder stops if a donor carries
none of the rounds a fit swaps; the M's AntiShip fit still hangs the legacy
`fr_mica-em`, which is swapped like the NG. The old mod's catalogue entry
stays, `unsubscribed`, as the record; the pack is 20 packs.

**Where the four sit, and what each places.** The two aircraft packs go to
the bottom of the order, above Red Storm Arsenal only. The French Air Force
contests twelve files and every one is an identical or older copy of a round
a specialist mod already wins (seven of the MQ-9 Reaper's `uav_*`, the French
Navy pack's `fr_am-39_B2` identical and its `fr_gbu-12` the weaker warhead,
two paratrooper rounds typed Bomb where the Soviet AEW&C pack types them
Paratrooper); the PLAAF Aircraft Pack contests 56 and loses all of them to the
J-11, J-8, Fujian, Type 003 and the other PLAAF mods, so what loads is its
H-6J/K/N bombers, J-7s, J-10A and 39 rounds, the YJ-12 and YJ-21 among them.
The merchantmen sit beside Merchants Expanded, the MV-75 beside the MV-22B;
neither collides with anything. Each is placed once, which is what coverage
asks: Southern Lifeline (SW09) has an Okean-class intelligence trawler with a
ZU-23 and a Bofors keeping station twelve miles off the support group, weapons
held - the eyes the Tu-214R and the Flankers work from, and an armed hull, so
the Situation roster lists it under Russia; Fujian's Shadow (SW11) has an
H-6K Late with four YJ-12 on the J-15D's run at the transports, a minute
behind it (the Strike objective still names the J-15D; the Badger is the
second salvo the screen has to be ready for); The Long Perimeter (D8) has an
Army MV-75 as the third lifter in the Osprey stream, Transport fit. The MV-75's
squadron table declares no squadrons, which the builder already allowed for;
its `_info.ini` puts its name under `[General]`, which is why the Mod Manager
shows it by number with an (A) badge. 1264 files; 106 + 68 tests.

## The planned window, the sea's price, and SETUP in the pack (4 October)

The first public comments on the Workshop item, within a day of it going
up. MattS, twice: *Macquarie Passage* cannot be finished - HMAS Supply makes
seven knots at flank in its sea state 5, and his second attempt failed on
time a quarter of a mile short of the withdrawal line. Dat Guy: every
mission is on a clock, the opposing forces in *White Water* and *Steel
Highway* start too close, *Southern Cross* cannot be won. Both were right
about the clock, and the repo's own numbers say why.

What the files said. All 58 missions ended on a `Condition_Type=Time`
trigger that failed the main task; the planned `minutes` (45 to 120) was
also the failure time. Stock Pacific Strike has no Time condition in any of
its fourteen missions - they end when their objectives resolve. No SEST
victory is clock-based: 50 are `arrive`, 8 `destroy`, and only four
missions have an in-mission timed check. So the clock was never the win,
only the loss, and it was sized by a planner that assumed every ship makes
her class speed in any sea.

Four changes in the builder, and the missions it moved:

1. **The window and the deadline are two numbers.** `minutes` stays the
   planned window and still sizes every placement and reach check. At that
   minute a new trigger ("Window closed") sends `BehindScheduleMessage`:
   the window has closed, command holds the line for about N minutes more,
   finish the task. The mission is lost at `DEADLINE_FACTOR` (1.5) times
   the window - a 60-minute plan fails at 90, a 90 at 135. Stock runs no
   clock at all; this keeps the pressure the design wanted and stops a
   plan that was right on paper from being a replay a cable short.
2. **Ships pay for the sea.** `SEA_SPEED` scales a Vessel's planning speed
   by the mission's sea state: 1.0 to state 2, then 0.9, 0.7, 0.45 (state
   5), 0.35, 0.3, 0.25. Submarines dive under it and aircraft fly over it.
   It is calibrated on the one measurement in hand (Supply, state 5, seven
   knots, 0.4 of the 18 the table assumes) and shaded conservative either
   side; the game's own curve is not in any file this repo reads. It feeds
   the arrival solver (`ship_speed`), the authored-box reach check, an
   authored convoy speed (`transit`), and the escort closure check.
3. **A held stage comes off the window.** An arrival whose stage keeps the
   units inside an area around one of their own starts until a minute
   (Macquarie Passage's service check, Southern Lifeline's rendezvous) is
   time at anchor: `hold_minutes()` takes it off both the solver's budget
   and the reach check. The comment in SR04 that said "the solver does not
   know the first thirty minutes are spent at anchor" is no longer true.
4. **One build names every short box.** The authored-box reach check used
   to raise on the first failure; it now reports through `REACH_PROBLEMS`
   with the rest of the geometry, so a pass over the speed table does not
   cost a rebuild per mission to read.

With the sea priced, seven missions no longer reached their own boxes
inside the plan, and each was moved or lengthened rather than given more
clock everywhere:

| mission | sea | was | now |
|---|---|---|---|
| SR04 Macquarie Passage | 5 | withdrawal line 20 NM north of Buckles Bay | 16 NM (`at=(-54.24, 159.05)`), 45 minutes under way after the check |
| SW09 Southern Lifeline | 2 | box 18 NM from Collins, 50 minutes after the rendezvous | a mile nearer (`at=(-13.78, 148.35)`) |
| SW C1 After the Wake | 4 | survivors' datum 18 NM from the frigate | 13.5 NM (`at=(-10.48, 144.62)`) |
| SR03 Search Datum | 5 | datum 18 NM from the escort | 8 NM (`at=(-52.12, 139.75)`) |
| TS08 Great Australian Bight | 4 | Collins 25 NM west of the escorts (31 on the plot) | 20 NM (`S(-35.62, 132.15)`): the escort's 80 minutes reach 24 |
| TS11A The Twelve-Mile Line | 3 | 80 minutes, the circle a cable past reach | 85 minutes; the circle stays on the twelve-mile line |
| RL06 The Quiet Side | 5 | 80 minutes, the tender a mile short of the holding position | 95 minutes; the position stays thirty miles west of the decoy station |

Not touched, on purpose: the four in-mission timed checks (they are story
beats), and the opening ranges in *White Water*, *Steel Highway* and
*Southern Cross*, which want a play-test with the new clock before anything
moves.

**SETUP in the pack.** Ordering 148 mods by hand from LOAD-ORDER.txt is
the step a stranger fails at, and the script written for the friend's
install now ships at the pack root: `SETUP - double-click me.cmd` and
`sest-setup.ps1`, copied byte for byte from `integration/campaign/setup/`
(CRLF; `.gitattributes` marks source and both outputs `-text` so the
install's SHA-256 matches the commit on either OS). Mod Manager > Open
Folder on the pack, quit the game, double-click SETUP. It finds the pack
from its own location (a Workshop download under `workshop/content/
1286220/<id>`, or a copy placed in StreamingAssets by hand; run from
anywhere else it looks for the one Workshop copy), refuses to run while
the game is up or while both a Workshop and a local copy exist, checks
that every id in LOAD-ORDER.txt is downloaded and names the missing ones
with links, installs Anchor Chain's preloader from the project's latest
GitHub release when neither `winhttp.dll` nor `BepInEx` is in the game
folder - relaunching itself elevated through UAC when the folder is not
writable, so nobody is told to "run as administrator" - sets the PLA &
PLAN & PLAAF AEP `debug.ini` switch off, and writes `[LoadOrder]`: the
pack's folder token first, the ids in LOAD-ORDER.txt's order, all on, the
player's other mods after them with their flags kept, stale and
undownloaded entries dropped, the file's other sections and line endings
untouched, a timestamped backup beside it. The `-Pause` the .cmd passes
keeps the window open; a console run without it does not pause. Exercised
on a fake Steam layout (two libraries, one on a drive that is not there;
148 downloaded ids; a settings file with a shuffled order, disabled
entries, a stale tail and `[LoadOrder]` first and last, CRLF and LF):
Workshop mode, local mode, standalone, both conflicts, a missing mod,
a missing settings file, the forced non-admin path (elevation refused ->
nothing changed) and the forced elevated-but-unwritable path; re-running is
byte-identical. `REQUIRED-MODS.txt` no longer opens with "try the Mod
Manager's Sync button": the item's Required Workshop IDs are left empty on
purpose, because the Mod Manager answers a required item below its
dependant by offering to move all of them above the pack, which would
undo every fix in it. The pack's `_info.ini` and `LOAD-ORDER.txt` say
where SETUP is. 1266 files.

**Read against itself before it shipped.** A review of the change found
the texts had not moved with the trigger. Thirty of the 58 timeout bodies
named the minute they were written for - "Seventy-five minutes and the
ships are still south of the line", "0820, and FUJIAN is short of her
station", "within ninety minutes" - and the Deadline that shows them is now
half as long again later, so the red card would have quoted a time the
yellow one had already explained away. The figure is the builder's now:
`{Deadline}` / `{deadline}` is the deadline in minutes spelled out in the
texts' own style ("One hundred and twelve minutes and..."), `{deadline_clock}`
its HHMM from the mission's start, both filled by `clock_text()` at render,
and `check_message_texts` stops the build on a timeout body that names a
minute or a clock time itself, so the next `minutes=` change cannot strand
one. All thirty were rewritten to the placeholders (SW01's "half an hour
after sunrise" became "well after sunrise"; the SW texts live in
`TIMEOUTS`, the rest in their modules). Every briefing's TIME section said
the task failed at the planned minute; it now gives both numbers from the
same source as the triggers. The setup script took three hardenings from
the same review: the administrator relaunch passes the Steam root and the
settings path it already resolved (a UAC prompt answered with a parent's
password otherwise ran against the parent's profile and told the child to
"use your own account"), launches `$PSHOME`'s console host rather than
whatever host ran the script (from the ISE, `-File` only opens the file),
and reads the child's exit code before saying it finished - `Fail` now
exits 1, which is also what lets the launcher pause on a failure without
pausing twice. `test_build_pack.py`'s new tests had been written below its
`unittest.main()` line and ran only under `-m unittest`; the block is at
the end of the file again.

Not demonstrated: the game's actual speed curve against sea state (one
point, one hull); that `BehindScheduleMessage` displays (it uses the same
`Action_Taskforce1_Message` as the start message); that the game is
indifferent to a `.cmd` and a `.ps1` in a Workshop folder (mods ship
`.md` and `.txt`; no mod in the collection ships a script); the UAC
relaunch on a real Windows desktop; and SETUP on a PC where Steam lives
somewhere other than the registry's default. Test card H.15-H.18.

## Published, and what came back (4 and 5 October)

Most of this lives outside the repo - on Steam, in the game's Mod Manager
and on the player's PC - and is written down here so the next session does
not have to find it again.

**What is published.** One Workshop item, "SEST Integration Pack -
Modernised Campaigns" (3812461539), Public, carrying all three campaigns:
Southern Watch, Southern Reach / Tasman Shield and Red Line. The 4 October
build (`d4fd1668` and `fa692245`, SETUP in the pack) is the one on it, and
`fa692245` is the head of the deploy branch the PC syncs from. Its
dependencies come from the collection "SEST - Modernised Campaign
Collection" (3812390790): 149 items, the 148 Workshop mods in
`data/load-order.tokens.txt` plus the pack, under a banner reading "149
Workshop items, 3 campaigns, 19 fix packs". The pack description, change
log, collection description and a pinned "Read first" discussion were
rewritten for the 4 October update (the SETUP install steps, the 1.5x
clock, Red Line's November 2028 to February 2029 dates), and the
collection banner and pack images were redone.

**Required Items are empty on purpose.** The item's Required Workshop IDs
are left empty, and nothing should rely on the Mod Manager's Sync for this
pack. The Mod Manager's dependency check ("Must load above this mod")
offers to move every required item above the pack, which undoes every fix
in it. The collection carries the dependencies instead, and SETUP sets the
order (test card H.15 and H.16). *Changed in October 2026:* the item's
Required Items now list the load order's Workshop mods, for the one-click
subscribe, and SETUP still sets the order; `publishing.md` (*Dependencies*)
has the current rule and the untested prompt.

**The first uploads failed on Steam Cloud, not on the pack.** They ended
`k_EResultLimitExceeded`, with 0 B on the item. Sea Power's Steam Cloud
was at its 1,000-file cap, almost all of it
`StreamingAssets\user\missions\NEW MISSIONS CLEAN` (804 files). That folder
was moved to `%USERPROFILE%\Documents\SeaPower-moved-out-of-cloud`, which
left the cloud at about 180 files, and the upload went through. Uploads
will fail the same way if the cloud goes back over 1,000 files.

**Updating the item.** Mod Manager > Create Mod > Update Existing > Pick
Folder `StreamingAssets\SEST_Integration` > Submit, then confirm in
`Player.log`: `m_eResult: k_EResultOK`. The Create Mod image picker only
browses StreamingAssets, so the preview image lives at
`StreamingAssets\SEST-preview.jpg` (124 KB), outside the pack folder.

**The first public comments.** MattS and Dat Guy: the section above
(`d4fd1668` answers Macquarie Passage and the clock). Dat Guy also found
that the bought ASW aircraft spawns far away, and the reason Southern
Cross cannot be won is a spotter drone and an escort boat with Harpoons
against an unarmed landing ship. When this record was written all of that
was held for play on the new clock; it was taken up later on 4 October, in
*Opening ranges in White Water and Steel Highway* and *Southern Cross, and
the opening gate* below (`9ed587e7`, `e062fb3c`). strykerpsg asked about the
deprecated mods. Three are kept on purpose, as the only source of units
the campaigns use: the Anzac (3440622312), the S-70B-2 Seahawk
(3403661005) and the E-7A Wedgetail (3499239964). Replacing them is not a
priority.

**The friend's fresh-PC test.** He subscribed to the collection and opened
the pack folder from the Mod Manager. `SETUP - double-click me.cmd` was
not there at first; it appeared a minute or two after he quit the game,
and then ran normally. The cause is not established: the player is sure
the item showed as updated before his friend launched the game, and that
the game was closed when it updated. The friend's
`Steam\logs\workshop_log.txt` lines for 3812461539, with his launch and
quit times, would settle it. Not yet reported (test card H.15-H.18):
whether the UAC elevation ran, whether the pack sits first with 149
entries, whether the campaigns are listed, and the yellow "Behind
schedule" card in The Quiet Passenger at 45:00.

**Two in-game notes that are game behaviour, not the pack.** An F-15EX
that "can't shoot a UAV" was at Weapons Tight with the drone not
classified hostile; it resolved once the drone was classified. A Forpost
RCS/IR patch was offered and not requested, so the pack has none. ECM
switching off after a second is Weapons Tight too: at Tight the game runs
jammers defensively only.

Still open after publishing: the moved openings in White Water, Steel
Highway and Southern Cross, not yet reported from play (H.19-H.22);
`SEA_SPEED`, calibrated on one data point
(H.18 re-checks it); the "Behind schedule" message, not yet seen in game;
trimming the 148-mod list; and the Task Force economy, helicopter recovery
and replenishment, none of them proven in game.

## What has NOT been demonstrated

Static resolution is not a play test. None of the following is established by
anything in this repository:

- that every mission loads in game (White Water, The Missing Beacon, Steel
  Highway, After the Wake and, on a fresh force, Rig Seventeen have: 27 Sep
  and 3 Oct above; Workshop subscribers reported others on 4 Oct), or that
  every texture and model appears;
- that a helicopter can recover aboard the ship it is assigned to - and,
  new with the review fixes, that a Lynx recovers on Sejong the Great (a deck
  declared by `[AirGroup]` alone), a Harrier on Charles de Gaulle, the U-2 on
  Kitty Hawk (its file says `CarrierCapable=True`), and an F-35A on the
  Langgur strip;
- that `SpawnByVariableAND=…,IsTrue` spawns a unit (the shipped data attests
  only `IsFalse`); SW06's Sejong the Great and SW08's KC-46 depend on it;
- that `TaskForceModeRearmByVariableAND` (the guide's key; no shipped
  campaign uses it) grants or withholds Common Sea's rearm;
- that a `Replaced` mission with `TaskForceModeMaxUnits=1` accepts exactly
  one vessel, and that `UnitsAreOutOfAmmo` then reads the ship the player
  sent rather than the authored placeholder;
- that a land unit with `Waypoints` drives them (the D3 column and roadblock,
  the D8 column; eight native sections carry the key);
- that a per-unit stage chain behaves: the lifter that visited the platform
  is the one whose withdrawal trigger is enabled, and losing it after the
  pickup ends the mission;
- that a Korean hull with no `TaskForceCost` appears and fights as an
  allocated ship; the mod's hulls are never sold, so the cost line is never
  read;
- that the tankers can actually pass fuel to the receivers in the same mission;
- that STALWART's or SUPPLY's supply system transfers what it is tuned to,
  in SW09, SR04 or anywhere else: the system is real since 26 Sep 2026, but
  no transfer from either hull has been seen in game;
- that the `UnitsInTheArea` victory triggers fire where intended, that the
  protected-unit failure resolves before victory in the same update, or that
  the neutral-loss handler prevents a win;
- that any mission's unit count is comfortable on a particular PC;
- **most of the Task Force Mode layer.** Buying a force and carrying it
  from mission to mission has been seen: the 3 Oct play test ran Southern
  Watch four entries deep in one save (White Water, The Missing Beacon,
  Steel Highway, After the Wake), the save reopening and continuing ("The
  first play test" above). Still unproven: that the prices are balanced;
  that completion points are awarded once and cannot be farmed by replay;
  that repair and rearm offers appear only at the service windows; that the
  anchor places the purchased force sensibly, and whether the anchored
  scripted hull is replaced by the player's first ship the way the developer
  guide says it is (the anchors carry no name for that reason; what is
  untested is the substitution itself, and the one-ship `Replaced` pattern
  Weapons Free uses); that a carried-over force loads into Rig Seventeen
  (test card 7.3a); that the optional window expires when it should. §16 of
  the bible lists the seven-step acceptance run that would settle the rest,
  and every step needs the game running;
- that the mission unit counts meet v1.1's density targets — they do not.
  Small missions here run 5–19 units against a 20–45 target, and the fleet
  missions 16–19 against 45–80. That is a deliberate first pass: the positions
  are snapped to proven points and the pools are thin in some theatres, so
  density is the thing to raise once a mission has actually been profiled on
  the user's PC;
- whether an objective that completes late still writes its campaign
  variable. That a variable survives between missions was seen on 3 Oct:
  `O1BeaconFound`, set in The Missing Beacon, fired Steel Highway's
  `VariableCheck` reveal ("The first play test" above). `IsFalse` is still
  the only comparison the shipped data attests;
- that an air-tasking row behaves the way the stock rows imply. `check_flights()`
  proves each row is internally consistent with the roster; it cannot prove the
  engine intersects fit lists per airframe, nor what it does with the Wedgetail
  and Triton, which declare no loadouts at all;
- that a `Hidden` objective stays hidden, that `Action_EnableTriggers` reaches a
  trigger that shipped `Disabled=True`, or that such a trigger's own
  `Condition_Time` is measured from mission start rather than from the moment it
  was enabled. The stock mission sets that time to a value its enabling trigger
  has already passed, which is consistent with either reading;
- how the engine breaks a tie between two terminal triggers. The shared exit
  means only one `Action_EndMission` exists and no delay window is open, which
  is what twelve native missions do; it does not stop two outcome triggers
  setting `Action_Victory` in the same update, and no shipped byte says which
  one wins. `missions/NATO/Sub Duel Pacific Shield 1971.ini` has the same
  unguarded race between a deadline and a victory;
- that a `Disabled=True` trigger's own `Condition_Time` is measured from
  mission start rather than from the moment it is enabled. Native sets that
  time to a value already passed, which is consistent with either reading, and
  both the discovery chain and the shared exit depend on it firing promptly;
- what the engine does with a purchased aircraft assigned to a flight. Every
  row now pairs with cockpits and no objective depends on one, which is the
  native invariant; whether the assignment itself works is the acceptance run;
- that a force inside its own weapon's reach will actually engage. The reach
  check proves a red group CAN affect blue; whether the AI closes, shoots or
  sits there is the game's business and nothing here has watched it happen.
  Several of these red groups have no `Waypoints` and no `Telegraph`, so they
  are stationary by construction;
- that `MaxLaunchRange` is the number that matters. It is the round's envelope,
  not the launcher's arc, the sensor's detection range or the fire-control
  solution, and it says nothing about whether the weapon suits the target - a
  28 NM SAM and a 28 NM anti-ship missile read identically here;
- that 0.40 of total range is the right sortie radius. The range is read from
  the airframe; the fraction is a planning assumption, and a jet at 74% of the
  radius it implies may still not make it home with the orbit and the
  manoeuvring a real sortie spends;
- that the engine's own fuel burn agrees with `SpeedAndRange_Cruise`. The
  figure is what the file declares as the airframe's range, not something
  observed in play;
- that `HomeBase` does what the name implies - that the aircraft will recover
  there, rather than merely being associated with it;
- (settled since: the campaign and its Open Allocation twin are listed on
  the campaign screen and have been played from it, per the 27 Sep and 3 Oct
  play tests above.) The missions are still shipped a second time under
  `missions/` so they are playable from the mission browser too;
- that the game displays ANY of this art. `BackgroundImage`,
  `MissionImage_en` and `TileImagePath_en` are keys the vanilla campaigns set,
  and the paths they are given here resolve to files that exist in the pack.
  Whether a mod-supplied campaign's art is loaded the same way the base game's
  is has not been watched happen. The first install, on `Legacy` with
  1920x1080 sheets, drew no mission image; the pack now ships the stock
  `MapView` and the stock sheet and tile sizes, measured on an installed
  copy, and the next install is the test;
- what resolution or aspect the game wants for the BACKDROP. The stock
  campaign's `BackgroundImage` names a file that is not on disk, so 1920x1080
  remains a guess constrained only by DXT5 needing multiples of 4. A backdrop
  that is letterboxed, cropped or stretched is a possibility this build
  cannot rule out;
- that `REQUIRED-MODS.txt` is SUFFICIENT. It is derived from what the missions
  place, which makes it necessary-by-construction and complete with respect to
  the load order it was built against. It is not a proof that a subscriber
  with exactly the mods it lists and nothing else gets a working campaign — that
  needs a clean install with only those mods, which nobody has done (the
  friend's fresh-PC test above took the whole collection, and its results
  are not yet reported);
- what a mission does when it names an absent unit. The pack said, for one
  build, that a missing mod meant "a mission that will not load" - a claim
  nothing here supports. `REQUIRED-MODS.txt` now says instead that the
  behaviour is untested and names both possibilities. Whether an unresolvable
  `Type=` drops the unit or stops the load has not been observed;

What *is* established, on every build: every `Type=`, `LoadoutVariant=`,
`SquadronReference=` and `VariantReference=` in all twenty-six missions resolves
against the file that wins the current load order, and every enabled mod is
reached by something the campaign places — or carries a written reason why it
cannot be.

## Checking it

```bash
python3 tools/check_campaign_coverage.py                                # coverage + references + roster, from the BUILT files
python3 tools/preflight.py "Southern Watch 01 - White Water"            # one campaign mission, the usual way
python3 tools/build_all.py --from-scratch                               # the regression gate
```

`check_campaign_coverage.py` deliberately re-derives everything from the built
mission files rather than from `campaign_data.py`, so it still tells the truth
after a mod update that the builder's roster has not caught up with.

## Opening ranges in White Water and Steel Highway (October 2026)

The first public report said both openings start too close: the AI sees the
convoy at once, the escort has to race to get its SAMs between a sea-skimmer
and the merchants, Steel Highway's submarine is right there, and a bought
ASW aircraft spawns far away. The built files agreed.

**White Water.** Warramunga started 8 NM astern of the merchants, with the
Peykaap-III (Nasir, 49 NM) and its decoy 16 NM ahead of them - inside the
boat's own 17 NM radar from the first second, with the merchants between it
and the only SAM. Now Warramunga starts 3 NM ahead on the threat axis with
her Seahawk beside her, and the Meridian pair starts 29 NM from the merchants
(26 from the frigate), east-north-east, beyond the trawlers and its own radar,
routed down the convoy's track. The handover box is unchanged. (The first
cut put it at 25 and 22; the opening gate below moved it out.)

**Steel Highway.** The escort group started 17 NM from the convoy the
briefing says it is in company with, and 13 NM from a 039C (YJ-18, Yu-6)
with weapons free - astern of everybody, not across the planned track - and
the P-8 slot shared the Wedgetail's station, about 60 NM from the boat at
30,000 ft. Now the escorts start 2 NM ahead of the merchants, the boat starts
30 NM up the track just north of it, at the far edge of the approach box,
creeping in toward the track below the layer, and the P-8 slot has its own
station over the sonobuoy field at 6,000 ft, 10 NM from the datum. The
briefing says where the datum is and that an assigned Poseidon starts over
it. Gulf traffic moves up to 15 NM ahead of the merchants, where it is part
of the picture.

Every gate passes. What this does not establish is how the AI behaves at
the new ranges; test card rows H.19 and H.20 ask for it.

## Southern Cross, and the opening gate (October 2026)

**Southern Cross could not be won.** Meridian Escort 3 started 43 NM from
HMAS Pilbara with weapons free and Nasir (49 NM), and its Forpost drone
started 8 NM from Pilbara, so the boat had a track on her from the first
second. Pilbara (Arafura, Variant3) carries a 4 NM Mistral and nothing else
that stops a sea-skimmer, and she is the player's only hull, so the
mission's "player force gone" trigger ended it when she sank. Now the boat
and its drone keep company with the coaster, 34-38 NM from Pilbara, and the
boat is weapons tight: 24 October is the week before Weapons Free, and it
shadows the lane rather than opening the war on it. Kiwi 01 still has to
go to them to name the coaster.

**The same thing, campaign-wide.** The report called it a common theme, and
it was. A new gate, `check_opening`, now runs on every mission in all three
campaigns and fails the build when a red unit with weapons FREE at the start:

- is a surface ship inside 25 NM of the player's nearest hull (each on the
  other's radar from the first second);
- is a submarine inside 25 NM (inside its own torpedo reach of the first
  ship it hears);
- is an armed aircraft with less than 20 NM of flying before its own
  anti-ship launch range (that range counted to 100 NM at most, so a
  standoff bomber needs to start 120 NM out, where the AEW sees it); or
- holds a player ship in anti-ship reach with a red aircraft already within
  25 NM of her giving the track (Southern Cross).

Only anti-ship missiles and torpedoes count as reach (`ship_reach`); the
old `reach()` read a Ka-28's sonobuoys as a 100 NM threat. Tight and Hold
units do not fire first and are not measured. A unit the story puts in
contact on purpose can say why with `contact="..."`; none does yet.

What it found, and what moved:

| Mission | Was | Now |
|---|---|---|
| SW01 White Water | Peykaap 22 NM from Warramunga | 26 NM (29 from the merchants) |
| SW04 The Quiet Passenger | Type 039 18 NM from the lone OPV, free | Tight: the week before Weapons Free, a boat that has been quiet eleven hours |
| SW05 Weapons Free | Peykaap 10 NM from the merchants | 28 NM ahead on their track, closing |
| SW10 Common Sea | 039C 15 NM from the Anzac | 32-35 NM, across the convoy's track |
| SW11 Fujian's Shadow | J-15D and H-6K 116-117 NM from Ford | 126 NM |
| SW12 The First Ship Through | Kilo 15 NM from Eyre; JH-7A pair 73 NM | Kilo 27 NM down the track; JH-7A 85 NM |
| O2 Southern Cross | as above | as above |
| O3 Borrowed Shield | Kilo 16 NM from the Anzac | 27-28 NM from both groups, working onto the Korean track |
| C1 After the Wake | 039C 14 NM from the Anzac | 26 NM, north of the box, still in torpedo range of the search |
| C2 Broken Wake | Kilo 19 NM; J-15D pair 79 NM | Kilo 33-34 NM ahead of Stuart's track; pair 124 NM |
| D1 Western Passage | MiG-35 pair 84 NM | 95 NM |
| D4 Return Passage | F-35A and P-8 110-113 NM | 120+ NM |
| TS05 Under the Tasman | Z-9 11 NM from Farncomb, ROMEO 22 | Z-9 31, ROMEO 26 (the furthest the destroy gate lets Collins still reach), frigate 42 |
| TS06 Bass Strait | Z-9 27 NM from the tanker | 30 NM |
| TS08 Great Australian Bight | Yasen 22 NM from Collins | 28 NM west, the same 26 NM from the rendezvous |
| TS09 The Southern Convoy | J-15 strike 58-64 NM from the convoy | forming up beyond its carrier, 125 NM |
| TS11 Approaches | J-15 strike 75-81 NM from the escorts | forming up beyond its carrier, 125 NM |
| RL02 Routes They Can See (Red Line) | Virginia 21 NM from the escort, Mk 48s free | 28 NM east, closing across the track (found later, below) |

Not changed, on purpose: warships with long-range anti-ship missiles that
start 30-100 NM away (an over-the-horizon shot is the realistic one, and they
need a track to take it), and the player's own AEW and patrol aircraft,
which see a lot from the first second because that is what a Wedgetail at
32,000 ft does. Whether the AI classifies faster than a real crew would is
the game's model and not something a mission file sets.

What this does not establish is how the AI plays at the new ranges; test
card rows H.21 and H.22 ask for it.

**What the gate missed, and why.** A second fact-check of the Steam text
found one weapons-free boat still inside 25 NM: Red Line's GOLF, a Virginia,
21 NM from the 054A in Routes They Can See. `ship_reach` read her as
unarmed, because her four Mk63 tubes name no round - they say
`AssociatedMagazine=TorpedoRoom`, and her 22 Mk 48s are listed only in that
`[TorpedoRoom]` section, which `stores()` never reads. `ship_reach` now also
reads every magazine a launcher names; with it, the gate flags GOLF and
nothing else across the three campaigns. GOLF now starts 28 NM east of the
frigate, still closing across the tanker's track (her purpose in the
mission). A test pins the torpedo-room case.

Also corrected here: the Steel Highway P-8 slot started about 60 NM from
the boat, not 48 as first written (48 was its distance from the escorts).
And the air rule's standoff cap means a bomber whose missile reaches past
120 NM can still start inside its own launch range, 120-130 NM out; the
Steam text says so rather than claiming no strike starts in range.

