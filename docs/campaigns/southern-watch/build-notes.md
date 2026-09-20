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

## What exists

| Thing | Where |
|---|---|
| The campaign | `integration/campaign/SEST_Campaign/campaigns/sest-southern-watch/campaign.ini` — a `Type=Linear`, native **Task Force Mode** campaign: twelve main missions, one optional operation, one contingency and nine story events |
| Requisition | `player_task_force_roster.ini` (16 priced entries) and `commander_settings.ini` (Australian commander, no same-nation discount) beside it |
| Campaign missions | the fourteen, shipped twice: under `campaigns/…/missions/` for the campaign and under `missions/SEST Southern Watch/` so the mission browser lists them too. The builder writes one copy and `tools/check_campaign_coverage.py` fails if the two ever differ |
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
- **SW09 is written around survival and a service window, not replenishment.**
  The bible flags `ran_aor_supply` as a Teide stand-in with no demonstrated
  supply mechanism. The mission therefore asks you to hold the window and
  withdraw; Collins is placed surfaced, and the surfacing rule stays a house
  rule stated in the briefing rather than a scripted one.
- **No `MissionImage`, `BackgroundImage` or `TileImagePath` keys.** Every one
  would point at a `.png` this repo cannot produce. A dangling art reference is
  worse than a plain campaign card.
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
- that a helicopter can recover aboard the ship it is assigned to;
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
  that the anchor places the purchased force sensibly; that the optional
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
- that the mod-supplied campaign is surfaced by the Mod Manager at all. The
  missions are shipped a second time under `missions/` precisely so the
  campaign's content is playable either way.

What *is* established, on every build: every `Type=`, `LoadoutVariant=`,
`SquadronReference=` and `VariantReference=` in all twenty missions resolves
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
