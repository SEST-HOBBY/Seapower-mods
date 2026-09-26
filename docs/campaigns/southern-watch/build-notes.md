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
not one on unlimited.** The tightest margins in the campaign are Flight Deck
Day's VH-3D at 87% of its radius and Long Way Home's Super Hornets at 74% —
both real numbers now, both inside.

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
| 4 | SW09's briefing promised service mechanics the predicate does not model | Relabelled, because there is nothing to implement. The shipped corpus uses **eleven condition types and seventeen sub-keys**, and not one tests speed, depth, heading, station, fuel or time spent inside an area; `UnitsInTheArea` is "Unit enters area". The briefing now states the rule the mission enforces — thirty-five minutes on the clock, then both ships south together — and leaves the replenishment as fiction in the fiction's voice |
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

For whoever ports the same branch's SEST Intercept Model pack: it restores
vanilla's `ammunition/damage.ini`, and with it
`InterceptChanceOutOfAltitudeOverride=0.05`, a hard 5% cap on any intercept
outside the round's altitude band. Today the Tu-95 mod's older `damage.ini`
wins and lacks the key, so there is no cap. Once it is back, the 150,000 ft
floor caps every SM-3 shot at a target below it at 5%, the 99,000 ft tier the
builder names included, so the floor has to be decided again in that port.

**Not demonstrated:** that Aegis ships now hold a ballistic raid better. An
SM-3 IIA from a Flight III Burke at a DF-21D or DF-26B raid should lock well
outside 10 NM, with no lock/unlock cycling, and a close-in shot should still
turn onto its target with a 5°/s launch turn.

## What exists

| Thing | Where |
|---|---|
| The campaign | `integration/campaign/SEST_Campaign/campaigns/sest-southern-watch/campaign.ini` — a `Type=Linear`, native **Task Force Mode** campaign: twelve main missions, four optional operations, two contingencies and seventeen story events - 35 entries |
| Requisition | `player_task_force_roster.ini` (10 priced entries) and `commander_settings.ini` (Australian commander, no same-nation discount) beside it |
| Campaign missions | the eighteen, shipped twice: under `campaigns/…/missions/` for the campaign and under `missions/SEST Southern Watch/` so the mission browser lists them too. The builder writes one copy and `tools/check_campaign_coverage.py` fails if the two ever differ |
| Dispatches | `missions/SEST Southern Watch - Dispatches/` — the eight optional episodes (Allied Dispatch ×3, Red Line, Range Week, Future Front, Cold Sea, plus the relief-perimeter episode) |
| Briefings | a `_briefing/BriefingText_en.xml` beside every mission, with SITUATION / TASK / FORCES / MODS IN PLAY. The mod list is generated from the roster, so it cannot drift from the order of battle |
| Source | `integration/campaign/campaign_data.py` (the script) and `build_pack.py` (the machinery) |
| Coverage report | `docs/campaign-coverage.md`, regenerated on every build |

`python3 integration/campaign/build_pack.py` builds it; `tools/build_all.py`
runs it in order with the other sixteen packs and consolidates it into
`SEST_Integration`.

## Where this departs from the bible, and why

- **Twenty-two missions were built, not the five-scenario vertical slice.** The
  request that started this was a campaign incorporating every mod, and
  coverage is only provable once every mod has somewhere to be. The bible's
  own sequencing advice still stands for *playing*: SW01 → SW02 → SW06 is the
  slice to test first, and it is the slice to fix first if something is wrong.
- **SW09 is written around a service window and a withdrawal, not
  replenishment.** The bible flags `ran_aor_supply` as a Teide stand-in with
  no demonstrated supply mechanism. The mission asks you to hold the service
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

## What has NOT been demonstrated

Static resolution is not a play test. None of the following is established by
anything in this repository:

- that any mission loads in game, or that every texture and model appears;
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
- that replenishment transfers anything, in SW09 or anywhere else;
- that the `UnitsInTheArea` victory triggers fire where intended, that the
  protected-unit failure resolves before victory in the same update, or that
  the neutral-loss handler prevents a win;
- that any mission's unit count is comfortable on a particular PC;
- **anything at all about the Task Force Mode layer.** That a modded RAN hull
  can be bought, crewed, assigned aircraft and deployed; that the prices are
  balanced; that completion points are awarded once and cannot be farmed by
  replay; that repair and rearm offers appear only at the service windows;
  that the anchor places the purchased force sensibly, and whether the
  anchored scripted hull is replaced by the player's first ship the way the
  developer guide says it is (the anchors carry no name for that reason;
  what is untested is the substitution itself, and the one-ship `Replaced`
  pattern Weapons Free uses); that the optional
  window expires when it should. §16 of the bible lists the seven-step
  acceptance run that would settle all of it, and every step needs the game
  running. None of it has been exercised;
- that the mission unit counts meet v1.1's density targets — they do not.
  Small missions here run 5–19 units against a 20–45 target, and the fleet
  missions 16–19 against 45–80. That is a deliberate first pass: the positions
  are snapped to proven points and the pools are thin in some theatres, so
  density is the thing to raise once a mission has actually been profiled on
  the user's PC;
- that a campaign variable survives between missions. Declaration, write and
  read are all present and statically consistent in the three chains above,
  and `IsFalse` is the only comparison the shipped data attests. Whether the
  campaign actually carries the flag forward — and whether an objective that
  completes late still writes it — needs the game;
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
  the airframe; the fraction is a planning assumption, and a jet at 87% of the
  radius it implies may still not make it home with the orbit and the
  manoeuvring a real sortie spends;
- that the engine's own fuel burn agrees with `SpeedAndRange_Cruise`. The
  figure is what the file declares as the airframe's range, not something
  observed in play;
- that `HomeBase` does what the name implies - that the aircraft will recover
  there, rather than merely being associated with it;
- that the mod-supplied campaign is surfaced by the Mod Manager at all. The
  missions are shipped a second time under `missions/` precisely so the
  campaign's content is playable either way;
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
  with exactly those 134 mods and nothing else gets a working campaign — that
  needs a clean install, which nobody has done;
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
python3 tools/preflight.py "SEST Southern Watch 01 - White Water"       # one campaign mission, the usual way
python3 tools/build_all.py --from-scratch                               # the regression gate
```

`check_campaign_coverage.py` deliberately re-derives everything from the built
mission files rather than from `campaign_data.py`, so it still tells the truth
after a mod update that the builder's roster has not caught up with.
