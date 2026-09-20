# Southern Watch — build notes

What was built from `campaign-bible.md`, where it departs from the bible, and —
more importantly — what has **not** been demonstrated.

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
| 5 | C01 is not outcome-gated | Not implemented — **relabelled instead**. The special note and the briefing now say the recovery is offered unconditionally and that gating it on the lost-cargo outcome needs a saved condition this build has not demonstrated. The briefing no longer names a ship that may still be afloat |
| 6 | Purchase and service rules were one boolean | `buy`, `repair` and `rearm` are three separate windows per mission. Purchases open at four force-assembly points, not before all twelve. Per-mission purchase allowlists are still **not** implemented |
| 7 | All submarines at surface depth | Authored per boat: hunting boats 300–500 ft down, the semi-submersible at 60, Collins deliberately surfaced alongside her tender |
| 8 | Routes and timing | `Condition_Time` is **seconds** — so the missions had no deadline at all, only a post-defeat exit timer. Each mission now has a real deadline in seconds that fails the main objective, and the arrival solver sizes every box to the mission's own clock. SW04's contact has waypoints to the box its objective depends on |
| 9 | Resolver accepted disabled Workshop folders | The fallback to exported folders absent from the canonical order is gone. Resolution is enabled-mods-only, so an unsubscribe fails the build instead of being credited |
| 10 | Range Week scored launchers as interceptions | The objective now says what the trigger tests — destroy three of four threat pads — and the authorised seaward target is exempt from the neutral-loss rule. A range safety boat and an airliner give the safety objective something it can actually fail on |
| — | Story chronology | The Enclave screen moves 2 → 12 November; the epilogue 26 → 28 November |
| — | O01/C01 real newlines in `Description=` | All mission text is normalised to the two-character `\n` escape centrally, so it cannot recur |
| — | Branch integration | `origin/feature/northern-front-iii-export` merged: the three SM-3 commits are in, and the consolidated pack carries all six SM-3/PAC-3 rounds |

Still open, and deliberately: **C01's gate** (relabelled, not built), **per-mission
purchase allowlists**, **mission density** against v1.1's 20–45 / 45–80 targets,
and **O02–O12 / C02–C06**. Everything in the Task Force Mode layer still needs
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
