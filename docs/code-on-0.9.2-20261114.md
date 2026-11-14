# SEST's code against Sea Power 0.9.2 — a trial, 14 November 2026

The owner's PC sent `SEST-Beta-References-20261114-145515-d8e3ce.zip` on
14 November (written by `tools/capture-beta-references.ps1` at 14:55 +10:00):
330 DLLs of the installed game, BepInEx and the Workshop mods, with the
game's and BepInEx's logs. The game is 0.9.2 Build 261113, a public release;
its `Seapower-Scripts.dll` is `3f56861f...503a`.

This is what SEST's plugin sources do against those files. **Nothing here
is a candidate.** No plugin source in the repository was changed, nothing
was packaged, and nothing can be installed from this. It is a list of what
holds and what a candidate for 0.9.2 has to change.

## What the PC does today

`BepInEx\LogOutput.log` of the 14 November launch (written 14:32, in
`data/install-snapshot/bepinex.log`):

```
[Info   :   BepInEx] 2 plugins to load
[Info   :   BepInEx] Loading [AnchorChain Preloader 1.0.0]
[Error  :AnchorChain Preloader] Could not find AnchorChain chainloader
[Info   :   BepInEx] Loading [SEST Beta Safe Anchor Chain 0.5.0]
[Warning:SEST Beta Safe Anchor Chain] Beta safe loader INACTIVE: uninspected game/preloader build.
```

So BepInEx starts, and **no code mod loads: not SEST's, and not any other
author's.** Anchor Chain's own preloader (1.0.0, in `BepInEx\plugins`) looks
for `AnchorChain.dll` in the game's mod directories as they are when BepInEx
starts and does not find it, although Anchor Chain 1.2.0 is installed, is
second in the load order and is on. SEST's own loader refuses any game file
it was not matched to. `winhttp.dll` is beside `Sea Power.exe`.

A correction to the notes of 14 November morning, which said BepInEx had
written no log since 12 November: the date in the log's first line
(`BepInEx 5.4.23.2 - Sea Power (12/11/2026 10:29:37 PM)`) is the date of
`Sea Power.exe`, not of the launch. The capture's `game-build.txt` gives the
same minute for the executable. BepInEx has been starting all along.

Whether Anchor Chain's author has a preloader for 0.9 cannot be read from
here (Steam's pages are not reachable where this is written). The Workshop
page of Anchor Chain (3380210757) is the place to look.

## The trial

In a scratch copy of `integration/beta-feature-parity`,
`integration/beta-anchorchain`, `integration/runtime-fixes` and
`integration/ui-followup` at this branch, with the build script's refusals
turned into messages, PowerShell 7.4.6's Roslyn compiled every source
against the capture's references, and Mono 6.8 ran the managed test
programs `verify.py` runs. The installer fixtures were not run.

**1. The sources as they are.** All five assemblies and all twelve test
programs compile with no error. Eight test programs pass outright (runtime
API preservation, history and policy parity, price caching, Identify path
detours, the loader's scheduler, cost rows, world-battle preparation, and
the world service with its Dynamic Campaign Mod 0.25.0.1 bindings, 173
checks). The others stop at a pin, which is what a pin is for: the game file, the Noesis
UI file (`c5f13e31...`) and Pop-Out Windows, which is now 1.2.3
(`6f3668aa...`; the UI accepts 1.1.3 and 1.2.0).

**2. With those three pins moved to the captured files**, in the scratch
copy only:

| check | result |
|---|---|
| native bindings (terrain, debrief, preparation map, campaign costs and inventory, F11, watermark, modifier registry, mission awards, tracker 0.8.0, the deferred hooks, Group Manager and Pop-Out bridges) | pass |
| the Contacts, sonar and Pop-Out IL rewrites | pass |
| loader pre-load policy and Identify geometry | 16 checks, 1 fails (the Osprey deck code, below) |
| mission ribbons | fails: the game changed |
| the adapters for other authors' plugins | several fail: the authors changed |

**The one change in the game that reaches SEST's own code.**
`LinearCampaignTaskForceRibbonRules.ApplyMissionRibbonAwards(ini, int,
string)`, which the runtime mission ribbons are a postfix on, is now a
short wrapper. It reads the commander's nation and rank and hands over to a
new `ApplyMissionRibbonAwardsCore`, which does what the old body did and
more: a spec can require a ribbon already held (`RequiresRibbon`), carry
conditions (`ConditionsAnd`, `ConditionsOr`, tested by
`LinearCampaignTaskForceLogisticsRules.CheckVariableConditions`), and a row
carries citation text. The members SEST binds by reflection are all still
there with the same signatures, so the binding passes; the test that pins
the method's body does not, and the postfix has to be read against the new
body before it is trusted.

That change is also a feature. The game's South Atlantic campaigns now
award ribbons on conditions, in the campaign file itself:

```
[Mission25]
TaskForceModeRibbonAwardRules=UK08_DSOBar

[RibbonAward_UK08_DSOBar]
Ribbon=distinguished_service_order_bar,UK
AwardByVariableAND=UK08PortHarrietCleared,IsTrue|UK08SapperHillCleared,IsTrue|...
RequiresRibbon=distinguished_service_order
```

with the variables set by mission triggers (`Action_VariableSet=...,True`).
Red Line's two runtime ribbons are
`sest_personnel_recovery?objective:Pilot=completed&rescued>=1` and
`sest_silent_passage?objective:Passage=completed&nolaunch`. The objective
half of each can be written the game's way. Whether a trigger can see "no
weapon was launched" or "one survivor was recovered" is not known. If it
can, the two ribbons need no plugin at all. This is the owner's decision
(release notes, decision 6).

**Other authors' plugins.** The loader rewrites some of them for the game's
changed API, and the tests hold each rewrite to the exact author file it was
written for.

- Still the same files, and the rewrites apply as before: Dynamic Campaign
  Mod 0.25.0.1, Identify Expanded, Optimal Target Distance 1.2.2, Test
  Range 0.2.4, Coordinated Strike Tool 1.3.1, Group Manager 0.2.17. After
  them every game member these six name is found in 0.9.2 (5,717 references
  in the first group the test reads).
- Rebuilt by their authors for 0.9, so SEST's rewrite no longer applies and
  is probably no longer needed: Sub Ammunition and Second Thrust (the mod
  now ships its old files as `backups/*_pre-090-api.dll`, and the duplicate
  `SubAmmunitionMod.fixed.dll` is gone) and Automatic SAR (not the
  3 November file any more). Every game member the three name is found.
- Of the 69 plugin files the loader would admit, 12,894 references to the
  game resolve and 32 do not, in four files: Enhanced Decoy Mod (the chaff
  launcher's `_ammoInUse`, 19 places), Multi-Stage Missiles (the same field
  and `ChaffCloud.launchChaffEffect`), Osprey Mechanics
  (`Aircraft.UpdateFuelConsumption`) and the flat Topographic Map (ten map
  members). Those four fail on 0.9.2 whoever loads them, until their
  authors rebuild them. Enhanced Decoy Mod, Multi-Stage Missiles and the
  flat map were held back on the beta already; the decoy mod and Osprey
  Mechanics are newer files than the ones the loader's hold and rewrite were
  written for, so neither applies to them now, and the Osprey deck code
  that depends on Osprey Mechanics is not released.

## What a candidate for 0.9.2 would take

1. Move the pins (game, Noesis, Pop-Out 1.2.3) in the thirteen source and
   test files that carry them, the enable flag's name, the installer and
   repair texts and SETUP's table of game files.
2. Mission ribbons: read the postfix against the new wrapper and core, write
   the body test again, or move the two ribbons to the game's own rules.
3. Retire the rewrites the authors have made unnecessary, hold the four
   files above before they load, and refresh the fixtures.
4. Run the installer fixtures and write the PC test sequence. A candidate is
   then what every candidate has been: compiled and checked here, and not
   trusted until the owner has run it.

None of this has been run in the game.

## Outcome: R14, 14 November 2026 (afternoon)

The candidate the list above describes is built:
`integration/beta-feature-parity/candidates/R14-20261114`, revision
`R14-20261114-sea-power-092-3f56861f`, Runtime 1.7.0 / UI 1.5.0, bootstrap
0.6.0. `integration/beta-feature-parity/README.md` has the details. In short:

- Seven pins moved, not three: Anchor Chain 1.2.0 and the three Unity
  modules changed too. All seven come from the capture, which matches its own
  manifest file for file.
- Every author image is now checked against the game's real members before it
  loads, after any SEST rewrite. That holds the four files above, and Osprey
  Deck Ops with Osprey Mechanics, by what they call rather than by hash. The
  adapters and holds pinned to author files the capture no longer has are
  retired with their tests.
- Six Alpine-family plugins' own build guards reject 0.9.2. SEST holds them
  before they load; the tests run each guard against the game.
- Mission ribbons: the postfix still follows the native grant; the contract
  test now pins the wrapper and the core, and the runtime adopts the core's
  rule against granting a held or replaced ribbon again. Decision 6's ribbon
  question is answered by the game's code: no trigger sees survivors rescued
  or a mission without a launch (`AircraftRecovered` is flight-deck recovery),
  so both Red Line ribbons stay in the runtime.

`verify.py` passes all 16 managed and installer checks against the capture.
The cross-build repair fixture (an installation enabled by R13 on 0.8.7,
repaired to R14) needs the 0.8.7 reference capture, which is not here; R14's
repair receipt still lists R13 and the fifteen earlier sets. Nothing has run
in the game.
