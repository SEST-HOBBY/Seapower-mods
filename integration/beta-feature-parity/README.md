# R14 — Sea Power 0.9.2 Build 261113, 14 November 2026

Runtime 1.7.0 / UI 1.5.0 / bootstrap 0.6.0, revision
`R14-20261114-sea-power-092-3f56861f`, for the public release 0.9.2 Build
261113 (`Seapower-Scripts.dll` `3f56861f…503a`) only. Built with
`build-roslyn.ps1` against `SEST-Beta-References-20261114-145515-d8e3ce`, whose
330 files match its own manifest; `verify.py` passes all 16 managed and
installer checks. Nothing here has run in the game yet.

**Pins.** Seven of the fifteen captured references moved: the game, Noesis
(`c5f13e31…`), Anchor Chain 1.2.0 (`17abaf4b…`), Pop-Out Windows 1.2.3
(`6f3668aa…`) and the three Unity modules. Anchor Chain's preloader, Identify,
Contact Log, Squad Panel, Combat Costs, Harmony, BepInEx and Cecil are
unchanged. SEST's Anchor Chain fork exports every public member of Anchor
Chain 1.2.0, so plugins built against 1.2.0 bind to it. The enable flag is
`enable-092-261113-3f56861f`.

**Loader.** `BetaAssemblyPolicy.Prepare` now checks every author image against
the members the game really has, after any rewrite and before the CLR sees it
(`UnresolvedNativeMembers`: types, fields, methods, signatures, locals and
catch types). Mono fails a whole method when it compiles a missing member, so
such an image is held with the member named instead of half-running. A plugin
whose library beside it would be held is held too (`HeldDependency`). On the
capture this holds Enhanced Decoy and Multi-Stage Missiles
(`WeaponSystemChaff._ammoInUse`, gone in 0.9.2), Osprey Mechanics
(`Aircraft.UpdateFuelConsumption(float)`) with Osprey Deck Ops, and the flat
Topographic Map. The adapters, holds and bridges pinned to author files that
no longer exist are retired with their tests: Automatic SAR, Better TacMap,
both Missile Control adapters, Osprey, Parallel Range Probe, Topography, the
old Test Range and Optimal Target images, and the inline Decoy, Sub
Ammunition, Second Thrust and R5 rewrites. Their authors' current files load
unchanged and every game member they name resolves. Still adapted: Dynamic
Campaign Mod (same audit as before), Identify, Coordinated Strike, Squad
Panel, and the current Test Range and Optimal Target images, whose native
shapes 0.9.2 keeps.

**Author build guards.** Sixteen Alpine-family DLLs carry the author's own
build check. Run against 0.9.2, six reject it (`HookChanged`): Saronic Corsair
USV and K5 Kraken (`ObjectsManager.removeObject`), Alpine Sea Power
(`CheckFiringConstraints`), the MV-75 fixture tilt (`FollowCamera.lateUpdate`)
and EC-2 jamming (`AI.MaintainMPA`). The startup holds are re-keyed to those
files; `BetaApiTests` runs every guard against the captured game and requires
SEST's decision to match the author's verdict.

**Mission ribbons.** 0.9.2's `ApplyMissionRibbonAwards(ini, int, string)` reads
the commander's nation and rank and returns `ApplyMissionRibbonAwardsCore`'s
rows unchanged, so the postfix still follows the native grant and its
persistent set. The core now skips a ribbon the commander holds, or holds a
replacement of (`ReplacesRibbon`); the runtime does the same. The game's new
`[RibbonAward_]` rules read campaign variables set by mission triggers, and no
trigger sees survivors rescued or a mission without a launch, so Red Line's two
runtime ribbons stay in the runtime.

`build-roslyn.ps1`, `build.py` and `verify.py` fall back to the preserved
Runtime 1.5.0 when the capture has no Workshop runtime file, instead of
stopping on the missing file.

# R13 — runtime mission ribbons and Admiralty filing, 10 November 2026

Runtime 1.6.5 / UI 1.4.15, revision `R13-20261110-mission-awards-499675cd`,
for the same beta 0.8.7-261107 (`499675cd…`) and Dynamic Campaign Mod
0.25.0.1 (`eacdb9a4…`) as R12 Final. On any other game build nothing binds:
the native image gate in `RuntimeFixesMod` is unchanged. The loader sources
are unchanged (AnchorChain `8692ecf9…`, Bootstrap `268462fa…`). Identify
changes only because it embeds the new runtime hash; the UI also bumps to
1.4.15 and logs the new pairing (`full Runtime 1.6.5 paired`). All game,
author and reference pins are unchanged.

## Mission ribbons granted at the debrief (`runtime/MissionAwards.cs`)

A campaign can name extra mission ribbons in a key the game ignores:

    [Mission<N>]
    SestRuntimeRibbonAwards=<spec>[|<spec>...]
    <spec>  = <ribbonId>[,<NationKey>...]?<term>[&<term>...]
    <term>  = objective:<ObjectiveId>=completed|failed|cancelled|notfailed
            | result>=<Result name>       e.g. result>=CostlyVictory
            | nolaunch
            | rescued>=<1-999>

Example: `sest_x?objective:Passage=completed&objective:Unseen=completed&nolaunch`.
Keys and values ignore case. Spaces are ignored around `|`, `?`, `&`, `=`,
the `:` of `objective:` and `>=`. The parser takes `>=` as one token, but in
campaign.ini the game's `IniHandler` trims the spaces on both sides of every
`=` before the runtime reads the value, so `> =` reaches the runtime as `>=`.
`;`, `#` and `//` must not appear: the game's `IniHandler` cuts a value at
them (the design draft's `;` separator would have reduced every spec to a
bare ID), so `?` separates the ribbon from its conditions. The key is read
as the native `TaskForceModeRibbonAwards` is: `[Mission<N>]` first, then the
mission event's own section, in every campaign rule source (the campaign
file and its `File`/`Base` definition).

- The part before `?` goes through the native `TryParseMissionRibbonAwardSpec`
  and `AllowsCommanderNation`, so nation selectors test the committed
  `TaskForceCommanderNation` exactly as native awards do; no selector means
  any commander.
- `objective:` uses the native debrief precedence (cancelled, failed,
  completed, fail at end, complete at end) over the mission's objectives; an
  ID the mission does not have is false. `result>=` compares the native
  `Result` value (Incomplete 0 to DecisiveVictory 17). `rescued>=` uses the
  debrief's `PlayerSurvivorsRescued`, clamped at 0 as natively.
- `nolaunch` (the owner's RL05 rule): no weapon launched and no gun round
  fired by any unit of the player's task force (failed launches count), read
  from the live `Globals._playerTaskforce._weaponReport`, which the snapshot
  writes to the campaign only after the awards. That includes AI-controlled
  escorts and allied units in the player's task force: one that engages on
  its own makes the term false even if the player's own boat fired nothing.
  Noisemakers, chaff, MOSS decoys, sonobuoys, paratroopers, fuel tanks and
  CIWS rounds (`ProjectileFired − CiwsRoundsFired`) do not count. A missing
  report or an inconsistent count makes it false.

A prefix and a void finalizer on `SaveDebriefSnapshot` hold the mission
and debrief and then release them (being void, the finalizer lets HarmonyX
rethrow a native fault with its original stack); a postfix on the 3-argument
`ApplyMissionRibbonAwards` runs after the native completion gate and the
native awards. Each qualifying ribbon becomes one more native row
(`ReadRibbonDefinition`, `ToAwardRow(1, N, rank, "")`), merged in the native
order (Precedence, then DisplayName) and added to the commander's distinct
`TaskForceCommanderRibbons` set. The native writers then put it in the
debrief rows, the Task Force Service Record and the save as they do a native
award. Rows are rewritten for each completion and the set is distinct, so a
replay or reload never holds a ribbon twice; a ribbon the native rules
already granted is not added. Several specs may name one ribbon: the first
that qualifies grants it. The definition is the campaign's `[Ribbon_<id>]`;
runtime-only IDs are not listed in `[TaskForceRibbons] RibbonIds`. Red
Line emits the key (RL05 Silent Passage in `[Mission15]`, RLC1 Personnel
Recovery in `[Mission11]`) with both definitions in its
`commander_settings.ini`. Its `campaign.ini` names itself as its `[File]
Base`, so the key is read twice and each debrief logs two lines per runtime
ribbon: the verdict, then "already awarded" or the same "not met" line.

The log has one line per evaluated spec (`debrief mission N: runtime ribbon
<id> AWARDED | not met: <term> (<actual>) | ...` with result, objectives,
launched, rounds, rescued and nation). A key with any invalid spec grants
nothing for that mission (one line). A binding or evaluation fault disables
the feature for the session with one line; native awards are always kept.
`MissionAwards=0` in `[Runtime]` of `plugins/sest_runtime.ini` turns it
off; it is on when the line is absent, so the shipped file is unchanged.

## Admiralty results recorded when filed (`runtime/WorldOperations.cs`)

A postfix on DCM's `Admiralty.Queue(OrderOutcome)`, the only place a result
enters `CampaignState.Outcomes`, keeps the outcome reference with its
campaign scope and coalition. The next service sample evaluates it, after
`Admiralty.OnCaptured` has reset the `Issued` of an order taken while only
on offer. Evaluation, the `SEST-WORLD-SERVICE-1` six-field line, the keys
(order or operation ID plus acceptance ticks), the same-side, Completed,
accepted and not-moot rules and the Runtime 1.6.3 legacy key are unchanged.
The unread-paper scan remains as the fallback; an outcome both unread and
filed counts once. Filed results are released only after a successful merge
(kept for the 30 s retry), change the evidence signature so a paper read
within one sample still merges, are flushed when the campaign closes, and
at most 512 wait. If the hook cannot bind or attach, one line is logged and
the unread scan continues. The Service tab and `setup/RIBBONS.txt` now say
results are recorded when filed, read or not; results filed before 1.6.5
count only if their paper was still unread under a Runtime that recorded
them (orders from 1.6.3, operations from 1.6.4).

## Checks

New verify group `runtime-mission-awards` (`tests/MissionAwardsTests.cs`):
Cecil contracts on the captured game and DCM images (the snapshot's call
order and the gate's branch targets, the award overloads' callers and size,
the player's weapon-report row and the counters each report lambda sets,
the ribbon-rule helpers by signature, the INI comment separators, the
objective, result, survivor and weapon-report members,
Admiralty.Queue/Read/Paper/OnCaptured and the sim-before-UI order) and
behaviour on the captured types (grammar and fail-closed parsing, native
nation filtering, all 32 objective flag combinations, nolaunch counting,
merge order and the native row round trip, the persistent set, the real
Harmony postfix, the void finalizer's rethrow with the original stack, the
mission-index guard, and the grant against an in-memory `IniHandler`). `native-bindings` binds `MissionAwards`;
`world-service-and-strike-bindings` drives DCM's real Queue, Read and
OnCaptured and checks that Runtime 1.6.4 (R12 Final) reads the record.
`build-workshop-support.py` accepts R12 and R13 revisions; the repair note
names R13. Under mono the patched native grant itself cannot run (Unity's
`Singleton` lookup), so the grant is a PC check.

PC checks: complete Red Line RL05 (`[Mission15]`) at CostlyVictory or better
using only countermeasures: the log line says AWARDED with launched=0 and
rounds=0, the debrief awards row and the Service Record show the ribbon with
its citation, date and rank; repeat with one torpedo (not met: nolaunch, the
native award still granted) and with only noisemakers or decoys (eligible).
Confirm RL05's task force has no AI escort that could fire, or that one
firing correctly disqualifies the mission.
Recover the pilot in RLC1 (`[Mission11]`): rescued=N matches the debrief's
survivors. Replay a completed mission and reload saves: the ribbon shows
once. A commander nation selector grants only that nation. `MissionAwards=0`
grants nothing. Complete an accepted Admiralty order and an operation's
final phase, close each paper at once, and check F11 Service counts both; a
port captured while its order is only on offer is not counted.

# R12 — World Operations and strike features included in Workshop

## World-battle preparation and exit refinement, 9 November

UI Follow-up 1.4.10 adds a native preparation checklist at the opening of a
paused world-campaign battle. Start preparation dismisses it while leaving
the clock paused; the player arranges aircraft, formation, sensors and orders
before explicitly unpausing. Replays get their own checklist. A mid-battle
save, an already unpaused game and ordinary SEST missions are not interrupted.

In a world battle the native pause menu's Exit caption is now End battle... .
Its original command still opens the native debrief. The campaign's existing
return confirmation keeps its full consequence warning, with an added note
that victory is not required. No outcome, loss or campaign-state calculation
is replaced. Quit-game wording and other pause-menu commands are retained.

The 19:10 PC capture confirms the original R12 payload was installed and the
game returned through battles normally. The new presentation still needs PC
rendering/interaction acceptance. Managed checks cover opening/replay/save
gating, inspected bindings and preservation of the original exit command.

The canonical Steam upload now carries the reviewed feature installer and
five-DLL beta payload in an inert archive under beta-support/. The normal
SETUP command stages/enables it on the exact supported game build, using the
existing probe, hash checks, Identify migration and original restore journal.
Stable active plugins remain in plugins/. Rerunning SETUP recognises an exact
Steam refresh of those active plugins and reapplies the bundled features.
Unknown installed code and changed native/author references remain refused.
No branch switch, game-DLL replacement or native save editing is performed.

This changes distribution and setup. R11 feature code (Runtime 1.6.0 / UI
1.4.9) and its world/cost/ribbon/strike behavior are retained. Native rendering
and gameplay acceptance still require PC testing. Historical records follow.

# R11 — modernised worldwide campaign, service ribbons and strike refinements

Target: the owner's 9 November 13:50 Brisbane capture, Sea Power
0.8.7-261107 (`499675cd…`). Runtime is 1.6.0; paired UI is 1.4.9.
The original world and complete regional expansion ship as one new-game
entry. Expanded-save ID `sest.world_sandbox_2028.regional` stays unchanged.
The original definition is archived for reversible legacy-save activation.
New campaign content requires a new game; existing saves keep their state.

F11 on the DCM strategic map offers Overview, Forces, Costs and Service in
a native movable/resizable/pop-out window. Campaign credits stay separate
from USD catalogue estimates. Service uses a versioned, atomic, independent
profile ledger; native DCM saves and commander records are not rewritten.
Native final-mission ribbons are added to the four authored SEST campaigns.
Existing third-party ribbons are retained. Auto-resolves do not earn manual
service, and theatre progress requires a recorded engagement position.

The current Coordinated Strike Tool keeps its own IMGUI controls and launch
logic. SEST adds shared colours and planned/remaining weapon-cost estimates.
A full native-window migration is a later UI task, not claimed in this build.

Topography 1.5.1 retains the author's removed-option fallbacks; only its
remaining shallow-water threshold is changed. The older 1.5.0 recipe remains
supported. Both inspected flat-only DLLs are held on this globe build.
Current Pop-Out Windows is hash-reviewed. DCM's salvo-hold patch targets the
new automatic-fire method and preserves the author's anti-ship-only filter
and the game's existing blocks. Original author DLLs remain unchanged.

See [R11-PC-TESTS.txt](R11-PC-TESTS.txt) for installation, limitations and PC
acceptance checks. This is a private beta candidate. No Unity or Noesis native
rendering, full campaign progression or Steam publication occurred here.
The canonical stable upload continues to carry stable code; the new beta UI
is delivered separately. Earlier implementation records follow for provenance.

## Historical R10 record

# R10 — Topographic Map restored for the captured globe beta

The 23:53 Brisbane capture confirms R9 is installed on 0.8.7-261107
(`499675cd…`) and Missile Control, Test Range and Optimal Target Distance
now report successful startup. The capture still holds both Topography DLLs.

R10 admits the captured SeaPowerTopo 1.5.0 globe DLL through a hash-pinned
private adapter. Only AnchorChain.dll changes from R9; Runtime 1.5.5, UI
1.4.8, the Identify data shim and the bootstrap retain their existing bytes.
Original author Workshop files, configuration and data are retained.

The game removed Globals._heightMultiplier and _underWaterDepthFactor.
Four reads in the author's HeightReader constructor now use the game's
fixed factors (land x1, water x2). Its existing metre-based raster also uses
the native 50 m shallow-water boundary. The game works in world units here;
the adapter preserves the map's metre units rather than mixing them.

All remaining Topography native operands resolve, CLR type discovery passes,
388 other method bodies retain their behavior, and all 65,536 signed DEM
sample values agree with native scaling after native metre/world conversion
within float round-trip tolerance (maximum 0.00390625 m). The author map-layer
constructor, day/night getter and all three lifecycle/render hook targets
are checked. The map-render hook still waits for Noesis initialization.
These are managed checks; no Unity/Noesis map was rendered in this build.

The author's current source independently documents the removed settings:
https://github.com/struckl/SeaPowerTopo/commit/635a7df109a97f8899f235f462bb7f8d44d99803
The original author is Lukas Struckl; its MIT notice is included. R10 adapts
the captured DLL locally rather than replacing its Workshop binary.

SeaPowerTopoFlat stays held on this globe game. Other R9 feature holds and
the ExtendedGuidance-off profile stay in place. This is the globe/LCC map
port; it does not enable the legacy flat-map DLL on beta.

## Install and check

Close Sea Power, extract R10 into a fresh folder and run Repair-Beta-Startup.cmd
for the existing R9 installation. Start a mission, open Map Layers and turn
on Topography (or its title-bar mountain button; default hotkey F6). Check
terrain shading, sea depths, cursor height, aircraft terrain clearance and
submarine depth/thermal overlays. Pan and zoom, switch day/night looks, try
the mission editor, then start a second mission. Check for startup errors
and responsiveness. Quit and run Capture-Repair-Results.cmd.

This is a private beta playtest repair. The canonical stable Steam upload
is separate and unchanged. R10 map rendering still needs the PC check.

## Historical R9 implementation record

# R9 — startup and Identify broadcast repair, 8 November 2026

The 22:23 Brisbane PC capture confirms R8 was installed and the game is
0.8.7-261107 (`499675cd…`), the same assembly R8 targets. The combat-cost
screenshot shows current-mission weapon and lost-store prices, including
AGR-30 at USD 70,000. It does not verify all other gameplay checks.

R9 updates the bounded loader and its private author-image adapters. Runtime
1.5.5 and UI 1.4.8 retain their existing feature implementation. Original
Workshop DLLs and data remain unchanged. The canonical stable Steam payload
is still separate.

- Missile Control 0.1.18: accept the native far-field G-limit field load. The
  author's full startup validator and its real steering transpiler are run
  in the managed checks.
- Test Range 0.2.4: bind the new fourth `GetSensorRange` argument. Its existing
  sensor postfix receives the same instance, target, ammunition and result.
  Both real author countermeasure/result validators are checked.
- Optimal Target Distance 1.2.2: group all seven native shared-launch accesses,
  including the fourth timer write after failed launch. The incompatible
  optional AAW interception subfeature stays uninstalled (`Ready=false`);
  native target rules remain and the other plugin features are retained.
- Identify Expanded: all three sender-selection player checks reject an
  unassigned object before reaching the native taskforce getter. This fixes
  the captured `FindSender` null-reference path for stop/surrender broadcasts.
- Native Windows helper DLLs are excluded before CLR metadata discovery.

## Features held on this exact game image

These exact captured author images reject the game's hook contracts and are
held before CLR load: Exterior Cameras (both duplicate copies), K5 Kraken
contact strike, XQ-58 shadow contacts, Alpine scoped runtime fixes (both copies),
MV-75/Cheyenne II systems, EC-2 comms jamming and MV-75 crew escape. Their data
and models remain installed. These are unavailable features, not repaired
feature ports. R9 does not bypass their author compatibility validators.

The preceding holds also remain: EnhancedDecoyMod, both Topographic Map DLLs
and MultiStageMissiles. ExtendedGuidance remains off by the SEST profile.
Original author files, saves, campaigns and Identify data are retained.

## PC test

Close Sea Power, extract R9 into a fresh folder and run Repair-Beta-Startup.cmd
for the existing R8 installation. Test startup, then select an owned unit and
use Identify stop/surrender orders on a contact. Check Test Range and missile
control as well as F11 current/previous/campaign costs, debrief, continuation,
preparation, Contacts/formation pop-out, compass, SAR and Osprey fuel.
Quit and run Capture-Repair-Results.cmd. The managed checks execute no Unity
launch, Noesis rendering or flight. This repair is a private beta playtest;
Steam uses the separate canonical stable upload after its gameplay checks.

## Historical R8 implementation record

# R8 — game assembly captured 8 November 2026

R8 supersedes R7 for the newly captured `Seapower-Scripts.dll` (`499675cd…`, Steam build 26502734). Noesis (`7b1fd6a6…`) and the 110 recorded plugin/game DLL entries are unchanged. The assembly hash, rather than a possibly stale Player.log version label, identifies this target.

Runtime 1.5.5, UI 1.4.8 and the bounded loader are compiled against these captured references. The Dynamic Campaign Mod night-sensor call appends the new native `nation=null` default, retaining native nation inference. The exact rewritten call and the new method contract have managed regression checks. Unknown game hashes remain inactive.

R8 retains the preceding feature implementation and exact-hash author adapters. EnhancedDecoyMod, both Topographic Map DLLs and MultiStageMissiles remain held for the compatibility reasons below; ExtendedGuidance remains disabled by the SEST profile. No new author plugin binary was substituted.

Close Sea Power and use the R8 repair with the original candidate journal/backups retained. Test startup, F11 costs/history, mission debrief/continuation, preparation, Contacts/formation pop-out, compass, SAR and Osprey fuel use. Managed and installer checks do not execute Unity gameplay or native Noesis rendering. Stable UI Follow-up 1.4.6 is a separate canonical payload and requires its own stable-build rendering check.

## Historical R7 implementation record

# R7 — beta Build 261106, captured 7 November 2026

This candidate supersedes R6 for the captured 0.8.7-261106 game. It keeps the owner's beta branch selected and upgrades the five-file candidate in place with verified backups and rollback. It is a managed-test candidate requiring a PC gameplay test, separate from the canonical stable Workshop payload.

- Runtime 1.5.4 and UI 1.4.7 bind the new game/Noesis hashes and Combat Cost Tracker 0.8.0 visibility state. Pop-Out Windows 1.1.3 is retained.
- Debrief rows accept the native trailing nation argument.
- The unchanged campaign and sub-ammunition plugins receive bounded property/terrain/fuel-refresh API bridges. SAR terrain queries append the native demPeak=false default. Osprey distance-based fuel consumption converts native cruise distance to kilograms with the native consumption ratio and BurnFuel API. Check hover and converted-flight fuel use on the PC.
- Updated author releases of WeaponLauncherEffects, SubModelStabilization, OptimalTargetDist, MissileControlMod, ParallelRangeProbe and TestRange load directly; their older pinned R5/R6 adapters are not applied.
- The beta LoadoutManager is used; its stable-only LoadoutManagerForLive duplicate is skipped before CLR load.
- EnhancedDecoyMod's single-attacher model is incompatible with the new multi-round countermeasure system and is held before CLR load. Both captured Topographic Map DLLs and MultiStageMissiles have removed native APIs and are also held. Their data stays installed; native countermeasures and native missile staging remain. ExtendedGuidance stays disabled by the SEST profile, even though its old field-layout defect was fixed by the author.

## PC checks

Close Sea Power, extract the R7 ZIP into a fresh folder, and run Repair-Beta-Startup.cmd for an existing candidate. For a fresh installation, use 1-Stage-Beta.cmd, launch to the menu then quit, and use 2-Enable-Beta.cmd.

Check startup, F11 current/previous/campaign totals and Redback prices, mission debrief and continuation, preparation, Contacts/formation pop-out and return, compass on unit video, SAR routing, and Osprey launch/conversion and fuel use. Quit and run Capture-Repair-Results.cmd. No Unity rendering, input, launch or flight has been verified by the local managed tests.

## Historical R6 implementation notes

The material below documents the preceding 261026 candidate. Its claims and PC check log strings are historical; R7's current behavior and limitations are listed above.

# Beta compatibility candidate — full pre-beta SEST feature implementation

This candidate targets **beta Build 261026** (`3005bc6d…`), keeping one existing
SEST Workshop item (`3812461539`). It restores the Runtime/UI feature code for
beta testing. It does not change the Steam branch or replace campaign/data packs.
The earlier stable restore ZIP is superseded for this task.

## R6: seven more author plugins

Built on 7 November 2026 on R5. R6 changes only the loader (`AnchorChain.dll`):
it adds seven hash-pinned adapters, one file each
(`beta-anchorchain/source/AssemblyAdapters.<Plugin>.cs`, with any bridges in
`BetaCompatibilityCalls.<Plugin>.cs` and its managed checks in
`tests/BetaApiTests.<Plugin>.cs`). The loader finds each `<Plugin>Adapter` by
reflection; Prepare lets a held-back image through only when an adapter is
pinned to its hash, and accepts only the native-field findings that adapter
names, re-checking the written image. Each adapter was built against its
investigation and an independent verification, then reviewed again against
the IL before it was merged; every review cleared it to ship with minor
findings only. 14 images now adapt (R5's seven with unchanged audits); 751
managed API checks pass, against 63 in R5.

| Plugin | What it brings back on the beta |
|---|---|
| OptimalTargetDist 1.2.1 | SystemGroup launch sharing (per-bank launch timers) |
| MissileControlMod 0.1.16 | vertical launch and tip-over, TVC turn bonus, SS-N-26 Lo-Lo profile and ring |
| ParallelRangeProbe 0.12.0 | its WorkerExpansion sensor and priority workers (CPU only) |
| TestRange 0.2.3 | the F10 Test Range tab, salvo spawning, chaff and ECM switches |
| BetterTacMap | its map layers, hotkeys and label lines |
| AutomaticSAR | automatic search and rescue for ships, submarines and helicopters |
| OspreyMechanics 1.1.45 and OspreyDeckOps 1.1.36 | the V-22 rig, hover flight, SV-22 dipping sonar and deck operations |

Still not restored, by design: MultiStageMissiles 1.7.17 (the beta's flyout is
Burst-compiled over native buffers; only the author can port it, and until
then MissileControlMod's staged rounds stage natively and the SS-N-26 hands
off after about 6 s), ParallelRangeProbe's TrajectoryPreview (needs an author
kernel), UiWorkerProbe and CombatWorker (performance only; nothing is lost),
and ExtendedGuidance 0.9.7, which SEST keeps off on both builds.

Corrections to the R5 notes below, from the independent checks of 7 November
2026. WeaponLauncherEffects suppressed the game's own launch smoke only on
the Mk 41, Mk 41 quad and Mk 35; SA-N-9's smoke is blanked by the pack's own
data and ExLS defines none, so the conclusion stands (all six fired with no
launch effect) but the stated reason was too broad. For the authors: neither
fix is "a few lines" that also suits the stable build. Appending the beta's
`failedLaunch` flag alone would break WeaponLauncherEffects on 261021; a fix
for both builds needs a signature-tolerant lookup and the result gate only
where `launch` returns bool. The Burke horizon bars are stabilised only while
a helicopter launches or lands (FlightOps); the F123 radar platforms while
their radar is on.

#### OptimalTargetDist 1.2.1.0

Restores: SystemGroup launch sharing works again on the beta, the same as on 261021. Each ship's grouped launchers share one launch timer per SystemGroup, and that timer uses the group's largest SharedLaunchInterval. Different groups fire independently even when their SystemName is the same: on usn_cg_bunker_hill_vls_2004, for example, the forward bank (WS1-8, including the eu_mk41_quad module) and the aft bank (WS9-16) each launch at most once per second, but both can fire in the same second. Grouped and ungrouped launchers don't affect each other, and ships never share timers. Ungrouped launchers (for example Mk141 at 5 s) keep the native name-based timing. This affects the 112 Workshop vessel/overwrite INIs and the 44 SEST_Integration INIs that use SystemGroup. One beta rule now also applies per group: a failed launch that is not a malfunction still uses up the group's interval, the same way the beta treats name-keyed launchers. The plugin's other features ran on the beta already and are unchanged: distance-preferred ammo, altitude gates, ammo policy carry-over, AdaptiveLoft and RangeCorrection.

Not restored: Nothing in this plugin stays lost. One related limit is outside this adapter: CombatWorker.dll is skipped on the beta because KinematicRangeResult changed from a class to a struct. That removes one of the two worker assemblies RangeCorrection's worker-aware path looks for. ParallelRangeProbe still loads, and RangeCorrection logged no error.

Audit: `launch-layout=1, locations=2`

PC checks:

- BepInEx/LogOutput.log contains the warning '[Beta compatibility] ADAPTED OptimalTargetDist in private cache: launch-layout=1, locations=2; original Workshop DLL and asset paths preserved.' followed by 'Loaded assembly OptimalTargetDist, Version=1.2.1.0, Culture=neutral, PublicKeyToken=null'.
- Player.log no longer contains '[OptimalTargetDist] SystemGroup launch sharing disabled; original name-based behavior retained: ' (and no 'Unrecognized launch layout: 1/1/1/4').
- Player.log contains '[OptimalTargetDist] loaded successfully.' (printed only when no OptimalTargetDist error or warning was logged first).
- Player.log has no '[ACModActivation 1.0] ...' warning for OptimalTargetDist and no '[OptimalTargetDist] Could not remove inactive launch-group hooks: ' line.
- While a mission with grouped ships loads, Player.log has no '[OptimalTargetDist] SystemGroup configuration rejected; previous/native launch sharing retained: ' line.
- Gameplay, compared with stable 261021 if possible: send usn_cg_bunker_hill_vls_2004 (Modern US Navy plus the Euromod LaunchGroups overwrite) against a large air raid and watch its VLS launches. Forward-bank launches (WS1-8, including the quad-pack WS6) are never less than 1 s apart. Aft-bank launches (WS9-16) are never less than 1 s apart. A forward and an aft launch can happen in the same second, so up to two per second ship-wide. Mk141 launchers keep their 5 s spacing. Without the adapter, all eu_mk41 cells shared one 1 s timer ship-wide and the quad-pack fired on its own timer.
- Optional, with weapon failures enabled in options: after a failed launch that is not a malfunction, the next launch in the same bank waits for the bank interval.

#### ParallelRangeProbe 0.12.0

Restores: On the beta, ParallelRangeProbe's WorkerExpansion module starts again and behaves as it did on 261021. Worker threads pre-compute radar horizon and radar detection-range results and AI engagement-priority scores, and those results are only used after the plugin checks them against the native game. Unit behaviour is unchanged; the gain is less main-thread CPU in busy radar and AI engagements. The Contacts module (batched plotting-table contact jobs) was already running on the beta and still is.

Not restored: TrajectoryPreview (Prediction) stays off. On 261021 it gave cached, worker-forecast AI weapon-range estimates and the attack UI's displayed range. On the beta the game computes those natively every time. The beta changed KinematicRangeResult to a struct and moved MissileSimulator to Burst, so the plugin's stable-era kernel can never pass its own bit-exact audit. Only a Euromod port can bring it back. RangeReuse (missile datalink radar-range memoising) stays off as well, but it was already off on 261021 in this install ('Conflicting hook at Update'). None of this changes gameplay results, only CPU use.

Audit: `locations=2, radar-range-bool=1, sensor-constant-fold=1`

PC checks:

- Beta 261026: BepInEx/LogOutput.log contains exactly 'ADAPTED ParallelRangeProbe in private cache: locations=2, radar-range-bool=1, sensor-constant-fold=1; original Workshop DLL and asset paths preserved.'
- Player.log contains a '[DatalinkReuse 0.12.0] ACTIVE; Contacts=True (runtime job dependency contract); RangeReuse=False (...); Prediction=False (...)' line. RangeReuse and Prediction reading False is expected on the beta.
- Player.log, from the main menu through a full mission, has no line starting '[WorkerExpansion 0.12.0] FALLBACK:', '[WorkerExpansion 0.12.0] Sensor FALLBACK:' or '[WorkerExpansion 0.12.0] Priority FALLBACK:', and no 'Worker/native result mismatch' text. Do not look for a WorkerExpansion ACTIVE line: QuietLog suppresses it.
- In a radar-heavy mission with AI engagements (for example transitBuiltInMission), write 'status' into %USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\Mods\ParallelRangeProbe\live\mode.request (so its write time changes), then open status.txt in the same folder. Expect AdditionalWorkers=ACTIVE, SensorState=enabled, PriorityState=enabled, SensorWorkerHits, SensorAudits, PriorityWorkerHits and PriorityAudits above 0, and AdditionalWorkerIds not empty.
- Repeat the 'status' request a few minutes later: the SensorWorkerHits, SensorAudits, PriorityWorkerHits and PriorityAudits counters should have grown.
- Gameplay check: radar contacts appear and AI ships and aircraft pick and engage targets at the same ranges as without the plugin. No stutter or error dialog appears when radar-equipped units first see each other.

#### MissileControlMod 0.1.16

Restores: On the beta, MissileControlMod switches on again instead of disabling itself at startup. It brings back its own features:
- controlled vertical launch, tip-over and cold-ejection timing for the 37 rounds it configures;
- the thrust-vector-control G and turn-rate bonus, including the terminal vertical rate, for its 16 TVC rounds;
- the SS-N-26/26b Lo-Lo sea-skimming profile and the ' Lo-Lo Max Range' map ring;
- save and load of in-flight controller state;
- thruster and jet-vane effects.

Steering for every missile the plugin does not configure stays exactly native. The bridge reproduces beta's own GLimitedTurnRate bit for bit, and the plugin's EffectiveG and EffectiveRate return their input for unconfigured weapons.

Not restored: Full parity with 261021 is not restored for the staged rounds. On stable, all 37 launch-control rounds also flew with MultiStageMissiles 1.7.16 driving their stages. The beta PC runs MultiStageMissiles 1.7.17, which disables itself (BuildAltitudeNodes), so:
- booster/sustainer staging is native single-stage;
- every step MissileControlMod coordinates with MSM does nothing;
- SS-N-26/26b wait in AwaitIgnition and only hand off through 'ignition wait timeout' after about 6.25 s.

That needs the separate MSM 1.7.17 port. Beta-native changes that apply to every missile stay as the beta defines them: the collision gate, effect timing and launcher-discard handling. Rounds discarded from the launcher stay native.

Audit: `file=1, locations=2, steering-shape=1`

PC checks:

- BepInEx.log contains exactly: 'ADAPTED MissileControlMod in private cache: file=1, locations=2, steering-shape=1; original Workshop DLL and asset paths preserved.'
- Player.log contains '[MissileControlMod] loaded successfully.'
- Player.log contains none of: 'Disabled; native behavior retained', 'Competing transpiler on', 'Stage adapter disabled', 'Optional stage synchronization skipped', 'Runtime initialization failed', 'Launch control requires the verified MultiStage adapter', 'Error loading assembly' for MissileControlMod. Do not look for an '[ACModActivation 1.0] MissileControlMod: enabled; ...' line: QuietLog suppresses it.
- Fire ESSM or Aster 30 from a VLS: the round climbs vertically clear of the ship and tips over smoothly before guidance takes over. Without the plugin it pitches over at once.
- Fire CAMM or SA-N-9: cold ejection, and the motor lights after tip-over.
- Fire UGM-133A, or SS-N-26 from a submarine: native underwater ascent, then a controlled tip-over after it leaves the water.
- Fire SS-N-26 from a ship and from a submarine with MultiStageMissiles inactive: it holds after launch and hands off after about 6 s. Confirm it is no worse than native: no crash, no stall into the sea.
- With dev mode on, fire an AIM-9X: during TerminalApproach the measured 'Turn Rate' readout exceeds the native G-limited value. The ceiling is about 50.9 against 36.4 deg/s at 1,500 kt.
- Fire SS-N-26 inside 65 nm: it flies sea-skimming without the loft. With ShowLowLowRange on, the map shows the ' Lo-Lo Max Range' ring, and repeated updates do not stack several rings (beta ReplaceGizmo now calls AddGizmo).
- Save and reload during a tip-over and during terminal TVC: the flight resumes, and Player.log shows no 'Invalid saved' errors.
- With weapon failures on, a dud round from a configured launcher stays native and logs no MissileControlMod errors.
- On a stable 261021 install, BepInEx.log has no 'ADAPTED MissileControlMod' line and the plugin still logs '[MissileControlMod] loaded successfully.'.

#### BetterTacMap

Restores: On beta 261026, BetterTacMap should start completely again. All 18 Harmony patch classes and the manual same-taskforce patch apply, the Ctrl+Alt+1 to 8 hotkeys start, and the settings come from the Workshop settings.cfg, so the owner's Speed=true and EtaDisplayMode=TtgSeconds take effect. Features that come back:
- The 8 map-layer entries: Contact Info: Depth, Speed, Altitude, Distress Beacons, CPA, Contact Age and Exact Enemy Depth, plus Weapon Info: Time-To-Go. Each can be turned on and off from the menu or a hotkey, and the choice is written back to settings.cfg.
- The Sensor Coverage (Radar/Sonar) and Threat Range Circles context-menu items, next to Firing Arcs and Plot Intercept Course, which already worked.
- Clicking a unit in the selected unit's taskforce opens its context menu.
- The mod's drawings are saved in a [BetterTacMap] section of the mission .ini, are no longer written as plain [DrawingLayer] polygons, and come back on load still tied to their units.
- The Waypoint ETA button cycles through Eta, Distance and TTG, with an h m s countdown for TTG.
- The extra contact-label lines (Depth, Speed, TTG, CPA, 'Last seen ... ago') keep updating, at most about 1.5 s behind (0.5 s refresh plus the author's own 1 s cache). Today they freeze whenever the game's own label inputs stop changing.

Not restored: Three differences come from the beta itself, not the adapter:
- The extra label lines are part of the game's line 3. That line now shows only while the native CONTACT_INFO_RANGE layer is visible and the label decluttering leaves room for it, so the plugin's lines are hidden whenever the game hides line 3.
- The plugin's range rings sit on the native DRAWINGS map layer and its arc wedges on ON_MAP_AREAS. Hiding either native layer also hides the plugin's drawings.
- Same-taskforce context menus open without the beta's colour-palette preparation, which only affects colour-preset pickers.

Five things could not be tested offline and need the PC:
- the eight entries actually showing in the Map Layers menu (that part of the beta UI was not in the capture);
- the multi-line label text displaying without clipping;
- frame time;
- the real (layerNumber, name) MapLayer construction, which needs the game's language singleton;
- missions saving and loading the drawings.

Audit: `attr-load-overload=1, attr-scene-ctor=1, attr-tactical-getter=2, layer-ctor=1, layers-by-id=3, layers-by-name=1, layers-list=1, line3-refresh=1, locations=1, retype-display-state=4`

PC checks:

- Beta 261026 with SEST R6: BepInEx LogOutput.log has the warning '[Beta compatibility] ADAPTED BetterTacMap in private cache: attr-load-overload=1, attr-scene-ctor=1, attr-tactical-getter=2, layer-ctor=1, layers-by-id=3, layers-by-name=1, layers-list=1, line3-refresh=1, locations=1, retype-display-state=4; original Workshop DLL and asset paths preserved.' followed by 'Loaded assembly BetterTacMap, ...'.
- Player.log has none of these lines: '[BetterTacMap] Harmony patching failed:', '[BetterTacMap] Map layer hotkeys failed to start:', '[BetterTacMap] Failed to load settings.cfg', '... is already registered - skipping to avoid clobbering another layer.', "[BetterTacMap] Could not find UnitSelectedState.HandleUnit to patch". The plugin's '[BetterTacMap] Initializing...' and '[BetterTacMap] Initialized.' lines are suppressed (VerboseLogging is false), so their absence proves nothing.
- In a mission, open the Map Layers menu on the tactical map. It lists the 8 entries: Contact Info: Depth, Weapon Info: Time-To-Go, Contact Info: Speed, Contact Info: Altitude, Contact Info: Distress Beacons, Contact Info: CPA, Contact Info: Contact Age, Contact Info: Exact Enemy Depth. Check them on the second map too.
- Turn one entry off and on from the menu, then with Ctrl+Alt+1 to 8. Each time, the matching key under [ContactInfo] in the Workshop folder's 3768036424/settings.cfg changes, and the label lines appear or disappear.
- With CONTACT_INFO_RANGE visible: a submerged contact shows a 'Depth: ... ft' line; contacts show 'Speed: ... kt' (settings.cfg has Speed=true); an in-flight weapon with a target shows 'TTG:' counting down; with an own unit selected, a closing contact shows 'CPA: x nm in t'.
- Leave an unselected, stationary submarine or surface contact for more than 15 s without touching anything. 'Last seen: ... ago' should appear and keep counting about once a second. This is the line-3 refresh; on today's beta it freezes. Check that the lines are not clipped.
- Watch frame time with many contact labels on screen, with BetterTacMap enabled and disabled. The adapter rebuilds each shown label's line 3 every 0.5 s. Also watch for labels flickering or resizing.
- Right-click a unit: the menu shows Firing Arcs, Sensor Coverage (Radar/Sonar), Threat Range Circles and Plot Intercept Course, but not the redundant Friendly/Neutral/Hostile items. With a unit selected, clicking a unit of its taskforce opens that unit's context menu. A detected life raft within reception range gets a ring marker, and turning off 'Contact Info: Distress Beacons' removes it.
- Press the Waypoint ETA button: it cycles Eta, Distance and TTG, and TTG shows an h m s countdown (EtaDisplayMode=TtgSeconds).
- Show arcs, sensor coverage and threat circles, then save the mission. The saved .ini has a [BetterTacMap] section with DrawingN keys, and no extra Polygon or Circle entries in [DrawingLayer]. Reload: the drawings come back tied to their units and follow them. Destroying a unit removes its drawings.
- For comparison, run the same checks on stable 261021, where the unadapted Workshop DLL loads as is.

#### TestRange 0.2.3

Restores: On the beta, TestRange starts again and logs '[TestRange] loaded successfully.'. F10 > Spawn shows its 'Test Range - Missile Test' tab in place of the native Missile Test view. The nation and missile catalog fills from every active file layer. Respawn selected unit, the Missile Trails toggle and Reset filters work. Every per-unit countermeasure switch behaves as on stable: chaff and decoy launches (Nulka included), defensive jamming of incoming missiles, burn-through jamming, standoff/support noise in the combined jamming model, self-screening noise, noise-jammer status and offensive jamming. A blocked support jammer adds nothing to the hostile radar's combined noise, which is what stable got by dropping it from the jammer list. When a defence filter blocks a launcher shot, the launcher carries on as it did on stable and does not enter the beta's new failed-launch cleanup. Once a salvo can run, the defence filters (Match, Launch, Hardpoint, Gun, CIWS) and the result and SENSOR_ASSESSMENT logging work again.

Not restored: Starting a missile salvo still fails while the beta loader holds back ExtendedGuidance 0.9.7. TestRange 0.2.3 requires ExtendedGuidance's diagnostics, so Start shows 'Cannot start: ExtendedGuidance diagnostics are inactive. Enable ExtendedGuidance and restart Sea Power before testing.'. Stable behaved the same with ExtendedGuidance off, which is how the owner's only 0.2.3 stable session ran. The author's gate was deliberately left unchanged. Until ExtendedGuidance is ported to the beta and enabled, the salvo defence filters and the shot/SENSOR_ASSESSMENT result logging cannot be exercised either.

Audit: `jam-hook=1, jam-legacy=1, jam-standoff=1, launch-blocked-result=1, launch-result=1, locations=2, scan-files=1, sensor-data=1`

PC checks:

- Beta 261026, R6 build installed: BepInEx log contains exactly 'ADAPTED TestRange in private cache: jam-hook=1, jam-legacy=1, jam-standoff=1, launch-blocked-result=1, launch-result=1, locations=2, scan-files=1, sensor-data=1; original Workshop DLL and asset paths preserved.' and no 'beta rewrite audit changed' or 'Inspected beta ... changed' exception for TestRange.
- Player.log contains '[TestRange] loaded successfully.' and contains no '[TestRange] Initialization failed:' line and no '[ACModActivation 1.0]' warning naming TestRange as inactive. Do not look for '[TestRange] bereit.' or the Guard 'enabled' line: the plugin suppresses both.
- Start a mission, press F10 > Spawn: the 'Test Range - Missile Test' tab replaces the native Missile Test view. Check that the tab's backgrounds line up with the beta's longer tab strip (beta DoTestWindow has 39 tab cases, stable 36). The nation and missile lists fill with no '[TestRange] UI error:' line in Player.log; Workshop and mod missiles appear once each.
- Respawn selected unit replaces the selected unit; Missile Trails toggles between 'Missile Trails: ON' and 'Missile Trails: OFF' and trails appear and disappear; Reset filters clears the filters.
- Countermeasures, no salvo needed: with Chaff / Decoys blocked on a ship, it launches no chaff or Nulka at an incoming missile; set 'Allow all' and it launches again.
- With ECM / Jamming blocked on a ship, its jammer no longer deflects incoming missiles. Used as a standoff/support jammer covering a friendly unit, it no longer shortens the hostile radar's detection range of that unit: compare the detection range with the jammer allowed and blocked, and against the same steps on stable 261021. Other units' jamming must stay unchanged, and 'Allow all' restores the effect.
- Without ExtendedGuidance, pressing Start shows the status 'Cannot start: ExtendedGuidance diagnostics are inactive. Enable ExtendedGuidance and restart Sea Power before testing.', the same as stable with ExtendedGuidance off.
- Only once ExtendedGuidance is restored on the beta and enabled: Start shows 'Test queued.' and the salvo spawns; the Results/Log window and the automatic log record the shots and SENSOR_ASSESSMENT lines with 'estimated sensor range=... nm' (there may be more than on stable, because GetSensorRange gained a caller). With 'Only CIWS', the defender's SAM launcher holds fire against the salvo and later engages other targets normally, without sticking in its engage cycle, and CIWS engages.

#### AutomaticSAR

Restores: On beta 261026, Automatic SAR now loads and finishes starting, so it works as it did on stable 261021. The right-click menu on ships, submarines and helicopters shows 'Start automatic SAR' (it changes to 'Automatic SAR running', and clicking it again cancels) and the 'SAR setting' submenu with its three saved settings. Ships and submarines are sent to sunk vessels that still have life rafts, on routes checked for water depth with a detour when the direct line is blocked. They hold the SAR speed, and a submerged submarine keeps the author's uncapped speed rather than the beta's cavitation cap. Near the wreck they brake with full reverse, and the game's own pickup takes survivors aboard until all are rescued or the unit is full. Helicopters work the rafts one at a time: they fly a waypoint 0.5 nm past each raft, slow to about 10 kn on the approach, pick up, then return to base or loiter as set. A player's own order cancels the job: a speed order (now also through the beta's new speed path), a telegraph order, a waypoint or order change, or a helicopter altitude preset. The SAR's own speed and telegraph changes do not cancel it. Sunk wrecks are put back at their map position when the centre tile changes. Status and completion alerts appear, and rescued survivors count in the debrief through the native CSAR points.

Not restored: nothing known. VTOL (MV-22B) SAR is offered only to aircraft with OspreyMechanics' 'OspreyRig.Controller'; R6 adapts OspreyMechanics too, so it should return with it (not covered by this adapter's own checks). The SAR side's VTOL speed code is already adapted. Two known small differences remain, both from how the beta handles speed. (1) While a submarine runs its uncapped SAR speed, a player speed order of exactly the same knots is ignored by the game's SpeedState, so that order does not replace the SAR speed command. The order still cancels the SAR job. (2) Route depth samples follow a straight latitude/longitude line, as on stable. In the beta's default LCC projection, the line the ship actually sails can differ from it by up to about 1%.

Audit: `bearings=1, generic-filter=1, lerp-body=1, local-retype=2, mach-make=1, speed-interface=2, speed-kind=2, speed-make=2, speed-read=2, speed-set=3, sub-speed=1, ui-forwarder=1`

PC checks:

- Launch beta 261026 with SEST. BepInEx.log must contain '[Beta compatibility] ADAPTED AutomaticSAR in private cache: bearings=1, generic-filter=1, lerp-body=1, local-retype=2, mach-make=1, speed-interface=2, speed-kind=2, speed-make=2, speed-read=2, speed-set=3, sub-speed=1, ui-forwarder=1; original Workshop DLL and asset paths preserved.' and 'Loaded plugin Automatic SAR (local.automatic-sar)' once each. It must not contain 'SKIPPED before CLR load: AutomaticSAR.dll' or 'Error loading plugin Automatic SAR'.
- Player.log must contain '[AutomaticSAR] Loaded.' exactly once. There must be no HarmonyException, NotSupportedException, TypeLoadException, MissingMethodException or BadImageFormatException that mentions AutomaticSAR, SetSpeedCommand or SarConstantSpeed.
- In a mission with a sunk enemy ship that has life rafts, right-click a ship, a submarine and a helicopter. Each menu must show 'Start automatic SAR' and 'SAR setting' once, not duplicated.
- Ship: start SAR. It must route to the wreck and hold the SAR speed (the speed panel shows a constant-knots order). Near the wreck Player.log must show '[AutomaticSAR] <ship> began full-reverse braking at <x> nm from <wreck>.' Survivors must come aboard, and the SAR alert and a '[AutomaticSAR] <unit>: <status>' line must follow when the job completes or the unit is full.
- Submerged submarine: the same rescue. Its speed must stay at the SAR value rather than dropping to the cavitation cap while it is submerged.
- Helicopter: start SAR. It must fly to each raft in turn, slow to about 10 kn on the final 0.3 nm, pick up, then return to base or loiter according to the 'SAR setting' Completion choice.
- During an active ship or submarine job, move the speed slider or press a speed button. Player.log must show '[AutomaticSAR] Automatic SAR cancelled for <unit>.' and the menu must return to 'Start automatic SAR'. Repeat with a telegraph button, a new waypoint, and an altitude preset on a helicopter job. Each must cancel. The SAR's own speed change and braking must not log a cancel.
- Pan the camera far enough to change the centre tile (or let the player unit cross tiles). A sunk wreck must stay at its map position.
- End the mission. The debrief must show the rescued survivors with the CSAR points.
- MV-22B, with OspreyMechanics adapted in R6: right-click an Osprey; the SAR items should be offered and a VTOL SAR run should hover over each raft.

#### OspreyMechanics 1.1.45

Restores: On beta Build 261026 the MV-22B, JGSDF MV-22B and SV-22 should behave as they did on stable Build 261021:
- Full V-22 model rig: nacelle tilt, rotors and rotor-blur discs, blade and wing fold, gear and doors, cabin doors and rear ramp.
- Engine-audio gating and the elevator hold during the fold.
- The hover flight model (vertical climb and descent, level zero-speed hover, sea floor).
- Hover and Slow SAR items in the MV-22 speed menu.
- Terminal auto-hover with braking and position hold at the last waypoint of a non-loop transport route. A player speed change during the approach releases it.
- Cruise-climb limit.
- SV-22 continuous dipping-sonar tasks: approach, hover at about 35 ft, deploy, listen, retrieve, then the previous speed and altitude are restored. Player speed or altitude commands cancel the task.
- Mk 54 and SSQ-53G/62F stores leave from the aft ramp.
- Empty, Transport and Ferry loadouts with capacities 0/32/0.
- OspreyDeckOps deck operations: launch-point and helipad wait, ready-up times, the USS Wasp RecoveryPoint3 to Elevator1 route repair, engine stop before the elevator.

Not restored: No feature is known to stay lost. Small differences from stable that remain:
- If another game system re-issues exactly the plugin's own speed request without passing through the plugin's two hooks' checks, the plugin keeps ownership. The speed is identical either way.
- Formation aircraft now go through SetSpeedCommand every fixed update on the beta, so the plugin's hooks run for them too. A dipping SV-22 inside a formation would log 'native speed refresh' trace lines.
- A Mach or telegraph speed captured as the dipping resume speed records its demanded knots at capture time. The request itself is restored exactly.
- While the hover prefix skips native FixedWingFlightPhysics.OnFixedUpdate, the beta's new G-force and turn-rate state is not updated. Stable skipped the same function.
- The beta changed the waypoint distance metric. Plugin braking and native arrival both use it, so they agree.

Audit: `hook-argument=2, hook-load=4, speed-field=2, speed-knots=2, speed-local=1, speed-make=5, speed-read=6, speed-set=5, speed-snapshot=1, speed-target=2`

PC checks:

- BepInEx/LogOutput.log shows '[Warning:AnchorChain] [Beta compatibility] ADAPTED OspreyMechanics in private cache: hook-argument=2, hook-load=4, speed-field=2, speed-knots=2, speed-local=1, speed-make=5, speed-read=6, speed-set=5, speed-snapshot=1, speed-target=2; original Workshop DLL and asset paths preserved.'
- The log has no '[Beta compatibility] SKIPPED' line naming OspreyMechanics.dll or OspreyDeckOps.dll, and no 'Error loading assembly at path' line for either.
- Exactly one '[Info   :AnchorChain] Loaded assembly OspreyMechanics, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null' line, and one 'Loaded assembly OspreyDeckOps, ...' line.
- '[Info   :OspreyMechanics] Compatible game clock: missionElapsedTime (double)' and '[Info   :OspreyMechanics] V-22 rig 1.1.45 ready; SV-22 sonar deployment checks actual hover attitude ...' both appear.
- '[Info   :AnchorChain] Loaded plugin MV-22 Source Mechanics (local.mv22.source.mechanics)' and '[Info   :AnchorChain] Loaded plugin MV-22 Deck Operations (local.mv22.deckops)' both appear, and there is no 'Skipping mod "MV-22 Deck Operations"' line.
- Player.log shows '[MV-22 Deck Operations] 1.1.36 loaded; shared cached identity lookup; deck routing and native armed loadouts preserved.' and no '[MV-22 Deck Operations] Patches disabled:' line.
- No '[Error  :OspreyMechanics]' line, and no AmbiguousMatchException, 'Null method for local.mv22.source.mechanics', BadImageFormatException or MissingMethodException naming OspreyRig or SetSpeedCommand.
- Mission with an MV-22B and an SV-22 on an LHD/LHA: on deck the wings and blades unfold and the nacelles go vertical. The aircraft takes off vertically, retracts its gear and converts to cruise. Rotor discs are visible.
- The MV-22 speed menu lists Hover and Slow SAR. Hover gives 0 kt with the aircraft level and holding altitude.
- Give an MV-22 a non-loop transport route. Near the last waypoint the log shows 'Terminal auto-hover <unit>: braking toward last waypoint at ...' and then 'Terminal auto-hover <unit>: arrived; commanded hover, waypoints=...'. The aircraft hovers and holds position.
- Repeat the route and change the speed with the slider during the approach. The log shows 'Terminal auto-hover <unit>: cancelled (speed command changed during approach); ...' and the aircraft keeps the player's speed. This tests the ownership bridge.
- SV-22 dipping waypoints: the log shows 'SV-22 dipping sonar <unit>: sonar task started; listening interval=...', then 'hover established; deploying at ...', 'probe underwater; listening', 'listening ended; retrieving' and 'probe stowed; sonar task completed'. Afterwards the aircraft returns to the speed and altitude it had before the task. This tests the snapshot bridge.
- During an SV-22 dip, move the speed slider. The log shows 'SV-22 dipping sonar <unit>: cancelled; native retrieval requested (player speed command: ...)' and the probe is retrieved.
- Mk 54 and SSQ buoys leave from the aft ramp. The loadout list shows Empty, Transport and Ferry, and transport capacity is 0, 32 and 0.
- On recovery the wings fold before the elevator, and the Wasp RecoveryPoint3 to Elevator1 route works. While hovering, watch for stale G or turn-rate readouts.

## R5: Weapon Launcher Effects, SubModel Stabilization, Pop-Out Windows 1.1.3

Built on 5 November 2026 from the owner's 3 November 23:09 capture. That
capture still holds R3 (`SEST.RuntimeFixes.dll` a0fb4279): the R4 repair had
not been run, so R5's repair accepts an installed R1, R2, R3 or R4. Runtime
1.5.3 beta and UI 1.4.4 beta are R4's sources with the Pop-Out pin moved; the
loader gains two adapters for Euromod's Anchor Chain Expansion Pack
(Workshop 3784474738); the bootstrap and Identify shim are unchanged R4
sources.

- **Pop-Out Windows 1.1.3.** The PC has Pop-Out Windows 1.1.3 (`5709ed68`);
  R4 pinned 1.1.1 (`9be4003d`), so in the 3 November session the Contacts,
  formation and compass bridges logged `Uninspected assembly: SeaPowerPopOut`
  and stayed off. The eleven members the bridges bind (`PopOutScreen`'s
  `Instance`, `DisplayAvailable`, `root`, `host`, `windows`, `hint`,
  `HostOpening`, `Decorate`, `Move`, `Place`, `Open`, `Remember`,
  `UpdateScreen`, `Flatten`, `FindButtonsPanel`) have identical IL in both
  builds. 1.1.3 changes window snapping, geometry and the settings panels,
  adds a popup-tracking method, and gives popped-out windows its settings
  gear and look when they load. R5 pins 1.1.3.
- **WeaponLauncherEffects 1.0.18** (`e79113f4`). Its Harmony `TargetMethod`s
  look up `WeaponContainer.launch` and `LaunchFromMagazine` by their stable
  parameter lists; the beta appended `bool failedLaunch = false` to both, so
  the lookups return null and HarmonyX stops `PatchAll` after the first two
  patch classes. Those two had already suppressed the game's own launch
  smoke and dust on the six mapped systems (Mk 41, Mk 41 quad, SA-N-9, Mk 35,
  ExLS, ExLS quad), so on the beta those launchers fired with no launch
  effect at all. The adapter routes both lookups through
  `BetaCompatibilityCalls.LauncherEffectsMethod`, which appends the flag for
  exactly those two stable lists, and gates the author's launch postfix on
  the beta's launch result, as the author's magazine postfix already is, so
  a failed launch spawns nothing. Audit: `launch-reflection=2,
  launch-result=1, locations=2`.
- **SubModelStabilization 1.1.2** (`09f6ec0e`). Its postfix on
  `VesselLoader.loadShipFromInternalResources` looks up the stable
  ten-parameter method that returned `VesselParameters`; the beta's method is
  void and takes the caller's `VesselParameters vp` first. The adapter routes
  the lookup through `BetaCompatibilityCalls.StabilizationMethod`, which
  prepends `VesselParameters` for exactly that list, and renames the
  postfix's `__result` parameter to `vp`, which HarmonyX binds by name to the
  same object at the same point. It restores the stabilised radar platforms
  and flight-deck horizon bars on the 26 configured vessels (German F123 and
  K130, the Modern US Navy Burkes, the Korean LPH, Dutch, Chilean and Indian
  hulls). Audit: `locations=2, result-argument=1, target-method=1`.

Both adapters are pinned to the captured author hashes and to the beta's
game hash, assert the beta signatures they rely on before any rewrite, and
leave the Workshop files byte-identical; a new author DLL loads as its author
wrote it. `tests/BetaApiTests.cs` checks the private images, the bridges
against the real beta methods and the name binding of every adapted patch
parameter, by reflection only.

Not in R5. The other author plugins that stop on the beta stay as R4 left
them, each reporting its own failure and leaving the game's behaviour in
place: MissileControlMod (steering-limit transpiler pattern now inside
`WeaponBase.GLimitedTurnRate`), MultiStageMissiles (`MissileSimulator.BuildAltitudeNodes`
now takes the beta's native flyout buffers), OptimalTargetDist's launch
sharing (launch layout 1/1/1/4; its name-based logic still runs), TestRange
(`SeaPower.ECM.CombinedJamUnit` is gone), BetterTacMap and UiWorkerProbe
(`GizmoLayerManager` is now a static catalogue; the layers live in
`MapDisplayState.Tactical`) and parts of ParallelRangeProbe. ExtendedGuidance
0.9.7, AutomaticSAR and OspreyMechanics stay held back before load. CombatWorker
0.2.0 stays held back too, and nothing is lost by it: it only moved the
game's own range arithmetic onto worker threads with bit-exact audits, it was
already off on the stable build through its own conflict check with
SecondThrustMod, and the beta computes those ranges in parallel itself
(`KinematicRangeBatch`). None of the nine self-stopping plugins had a new
build in the 3 November capture, and none of the authors publishes source;
the fixes for WeaponLauncherEffects and SubModelStabilization are a few
lines each and are worth reporting to the Euromod team.

## R4: version watermark, the beta's #!extend scan, cost item rows

Built on 3 November 2026 from the 2 November 22:26 capture, which recorded
R3 playing its first campaign mission. Runtime 1.5.2 beta; the loader,
bootstrap, UI 1.4.3 beta and Identify shim are R3's sources rebuilt with the
same compiler as the Runtime (see the build section). GPT had described these
three fixes on 2 November but its R4 build was never delivered; this is a new
implementation from the same evidence, and `beta/r4-20261103` is the R4
baseline for the next PC test.

- **Version watermark.** `SeaPower.VersionWatermark.OnStart` keeps its text
  active whenever `SteamApps.GetCurrentBetaName` succeeds, whatever the
  player's `[Debug] ShowVersionWatermark` option says; only the game's own
  config.ini could turn it off. `runtime/VersionWatermark.cs` postfixes
  `OnStart` and deactivates that one object, and deactivates any instance
  that started before the plugin loaded. `HideVersionWatermark=0` in
  `plugins/sest_runtime.ini` keeps it; the key defaults to on when missing.
- **The beta ignores every Workshop `#!extend` file.** Read from the IL of
  Build 261026: `FileManager.Directories` is built lazily, and when a BepInEx
  plugin reads it before SteamManager has initialised (Anchor Chain's
  preloader does, to find the chainloader; the SEST bootstrap probe does
  too) it holds the game's own three folders. `FileManager.OnStart` rebuilds
  the list, but every `SearchDirectory` it constructs opens its `_info.ini`
  through `IniHandler.open`, whose one-shot `ScanForModifierFiles` then runs
  against the stale list, because the rebuilt list is published only after
  all directories exist. Nothing rescans until the Mod Manager's Apply, so
  SEST's cost catalogs, the 129 Cross-Deck stubs and the Collection and
  Allied Fixes extends never applied in the 2 November session. That is why
  `[WeaponCosts] Missing WeaponCosts: sest_agr-30 (ASM)` and the Runtime's
  `no reference-year price` both appear although the published item's
  `sest_weapon_costs.ini` carries the section. `runtime/ModifierRegistry.cs`
  checks the registry for the pack's own modifier files once the Workshop
  folders are registered and, only when none is there, does what Apply does:
  `invalidateModifierRegistry`, a rescan, then `invalidateCache`. It logs the
  counts before and after. `ModifierRegistry=0` turns it off.
- **Cost rows.** `CombatPrices` now also reads `sest_weapon_costs.ini`,
  `sest_vessel_costs.ini` and `sest_aircraft_costs.ini` by their own names
  and uses them for a section the merged catalog lacks; the merged catalog
  still wins where it has the section. Every price records its source. The
  campaign window lists each expended round per mission, and the live window
  lists them under the categories: quantity, unit price, line total and the
  catalog section or unit file the price came from, sorted by line total.
  Saved quantity records are not changed. `tests/CostRowsTests.cs` covers the
  fallback, precedence, sources and rows against in-memory catalogs, and the
  shared catalogue cache test now measures the catalogue reads per build.

Checked but not changed: the MQ-4C Triton's `AN/ZPY-3` (430 km, Gain 60,
900 kW, `RadarsActive=True` in the missions that place it) is identical on
both builds, and no vanilla radar changed between the two exports; what did
change is the game's horizon and look-down geometry (`SensorSystem.IsInLookDown`
now uses a curvature-aware dip with a 4/3 radar Earth radius, and `GetRange`,
`RangeReaches` and `Radar.IsDetectableTarget_Conditional` are new), so any
range difference is the beta's code, to be compared in game on both builds.
Not done: the clipped tab borders (the small header crop shows the overhang;
a full view of the affected window and its display scaling are needed) and ports of
the author plugins that stop on beta APIs; their failures are their own
validations refusing changed native signatures (`MissileControlMod` steering
limits 0/0/2, `MultiStageMissiles` `MissileSimulator.BuildAltitudeNodes`,
`OptimalTargetDist` launch layout 1/1/1/4, `TestRange`
`SeaPower.ECM.CombinedJamUnit`, `UiWorkerProbe` and `BetterTacMap`
`GizmoLayerManager.Instance`, `SubModelStabilization` and
`WeaponLauncherEffects` null target methods), which an adapter cannot supply.

The repair script now replaces all five candidate files and accepts the
installed R1, R2 or R3 set as a whole; `Restore-Previous-SEST.cmd` still
restores the original backups.

For the follow-up PC capture, `tools/capture-r4-results.ps1` reuses the game
folder in the installed beta journal and also includes its Workshop library
alongside Steam's discovered libraries. The read-only collector includes SEST's
saved quantity history and installed cost catalogues, matching Global Hawk/Triton
aircraft definitions, and the layered sensor definitions. Campaign save files
are excluded. The capture fixture checks journal selection, multiple libraries,
redaction and byte-identical source files. Runtime and plugin testing still uses
the R4 payload above.

## R3: campaign menu and scenario errors

The 2 November 00:50 capture verifies the R2 scenario can initialize, but its
previous log records the Campaign menu failing at
`FileManager.GetDirectories(string)`. Its current log records the two screenshot
errors: Enhanced Decoy requires a label on the contact constructor's `ret`, and
Sub Ammunition calls the removed three-argument `Utils.openIniFile`. The latter
fails during weapon cloning and reaches `ObjectsManager.DestroyFailedUnit`;
loading a scenario therefore did not mean its complete roster loaded correctly.

R3 creates private compatibility images for the exact captured Dynamic Campaign
0.25.0.1, Enhanced Decoy, Sub Ammunition, Second Thrust and Identify DLL hashes.
The author files stay byte identical. All active direct native method/field
operands in those images are resolved against the captured beta metadata; this
also finds downstream errors before a PC test reaches them.

- Campaign directory/file enumeration adds beta's actual optional `LayerKind.All`
  argument. The other inspected optional arguments for mission unload, reaction
  acquisition and ASW attacks are appended from native metadata. Branch/EH entry
  targets retain the argument insertions; short branches are expanded safely.
- Campaign mission-path reads use the new public getter. Writes use
  `Globals.OpenMission`, respecting beta's mission mounts and private setter.
  Its one constant-speed creation/command pair uses beta `SpeedRequest.Knots`.
  Legacy secondary-side reads look up AI `Taskforce3` in registered side relations;
  the optional capability checks resolve the concrete bridges and new ASW signature.
- Campaign/Identify/Decoy map-style getters use beta's named `MapColor`, `MapBrush`
  and `MapValue` APIs. Decoy target-line styling selects the allied weapon palette
  key, and its old vehicle view-model lookup finds the existing view-model in the
  main/second map's known-unit collections; it never creates extra view-models.
- Enhanced Decoy's original contact transpiler now branches to the native
  `_sources.Add(this)` epilogue, preserving beta's registration. It uses the real
  merge label, so the original one-argument validation and transpiler remain usable.
- Sub Ammunition/Second Thrust use the four-argument full-path INI reader with
  `forceDisk=false`. Sub Ammunition's file lookup keeps the actual old first-match
  behavior (the former ignorePath comparison had no effect). Its positional
  offsets use beta's grid-frame `OffsetByGridVector`. The two captured Sub Ammunition
  DLLs have the same plugin identity; when both are present, only the canonical
  Workshop-named image enters the CLR. No duplicate file is deleted.
- Identify retains the R2 geometry/data redirection and skips unassigned-taskforce
  units during its enemy-hail scan, before calling the unsafe native property.

The upgrade accepts the reviewed R1/R2 loader/shim pairs and checks the original
restore journal against installed bytes. Its copy-failure rollback preserves the
old pair and leaves activation disabled. Runtime, UI, bootstrap and content bytes
are unchanged. **Full pre-beta parity remains unfinished:** the R2 quarantines
below and other captured author-plugin startup failures still need ports. Managed
API/IL/fixture checks do not verify campaign progression, decoy simulation or Unity
rendering; the author's complete `Hooks.Validate` also needs initialized Unity.

For the installed candidate, extract the R3 ZIP to a fresh folder and run
`Repair-Beta-Startup.cmd` with the game closed. Open Campaigns, start/continue the
failing campaign and test entering/leaving a battle, then repeat the standalone
scenario and check its roster. Quit and run `Capture-Repair-Results.cmd`.

## R2: captured mission-load failure and repair

The 1 November 23:37 PC capture reached plugin activation and installed the SEST
Runtime/UI hooks. Mission loading then stopped at
`Unity.Entities.TypeManager.GetTypesDerivedFrom` while recreating the plotting
world: `ExtendedGuidance.Runtime/RangeEntry.Value` encodes
`SensorSystem.SensorDistanceData` as a reference type, but beta defines a value
type. This is a confirmed managed mission-load blocker; the logs do not include
a native crash dump. Identify's missing `GeoPosition.CourseTo` also logged 15,081
failures in that capture.

R2 prepares assemblies **before** `Assembly.LoadFile`: it rejects that known
Extended Guidance image and checks native field layouts in other plugin images.
It also withholds the captured Automatic SAR and Osprey Mechanics images after
confirmed patch failures, plus dependent Osprey Deck Ops. Non-plugin dependency
DLLs are left to normal resolution instead of explicitly loading duplicate
Harmony/Cecil libraries. These features still need ports; full pre-beta parity
is not claimed.

For the pinned Identify image, the loader rewrites its ten CourseTo operands to
beta's same-signature `HeadingToPosition`. Two Assembly.Location accessors route
to the original Workshop path. The adapted image lives under BepInEx config;
the author DLL remains byte identical. The data-path shim verifies the original
Workshop source through the loader's source-path mapping. A real no-jobs ramming
tick now JITs/returns in the managed regression; north/east/date-line bearings and
metadata discovery across the captured mod set are checked separately.

`Repair-SEST-Beta-Startup.ps1` upgrades the already enabled first candidate. It
disables activation first, backs up the current pair, changes only the loader
and data shim, and updates installed hashes in the original restore journal.
It keeps that journal's original backups and restores the prior pair with
activation disabled if any repair copy fails. Runtime/UI bytes are unchanged.
For a fresh install or a restored candidate use the normal Stage/Enable flow.

## Implementation

- **Runtime 1.5.1 Beta:** complete reconstructed 1.5.0 implementation, including
  native F11 cost windows, campaign/last-game history, three-row debrief,
  preparation map and restart cleanup, inventories, terrain/towed-sonar guards,
  Contacts and Formation pop-out bridges. Beta changes `Globals.currentMissionFilePath`
  into a property; the F11 binding now uses its inspected static getter. Native
  game and Noesis hashes remain exact checks for the captured beta pair.
- **UI Follow-up 1.4.3 Beta:** retains 1.4.2's input, layout, catalogue cache and
  performance fixes; paired to the newly built Runtime hash. Pop-Out Windows
  1.1.1 is inspected and pinned. UI entry runs after the Runtime entry.
- **Identify Data Paths 1.1.0:** runs before Identify Expanded 3.420.6967 and after
  the paired Runtime. Redirects its `ModDir`/`RootDir` to
  `%LOCALAPPDATA%\SEST\IdentifyExpanded`, while preserving `StreamingAssets`'s
  original meaning. The installer backs up and migrates the formerly active
  local folder and removes only its load-order row. Audio/settings are retained;
  the Workshop DLL is unchanged. Deleting the local folder alone would let the
  Workshop plugin recreate it.
- **Bounded AnchorChain 1.1 fork:** preserves assembly identity and upstream API;
  each plugin is attempted once, failures are removed from the pending set, and
  a stalled dependency plan terminates. The scheduling implementation is tested
  directly with failed and blocked plugins.
- **Bootstrap 0.3.0:** waits for inherited FileManager readiness and Workshop
  registration. Staging remains inactive. A fresh per-installation token and
  successful menu-probe receipt are required before the installer can enable it.
  The obsolete PR #53 bootstrap is not used. Original preloader and Workshop
  AnchorChain files are left intact.

## Source provenance

The original Runtime 1.5.0 project has not been recovered. `runtime/` is a new
fork of its decompiled inspection reference, not a claim to have recovered that
project or to reproduce its exact binary. Its baseline is the owner's captured
`7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986`.
All 314 declared type/method contracts across 40 non-generated types are retained.
Policy and saved history/inventories are compared directly with that captured
binary; the old 1.2 source is not substituted. Stable pack binaries remain in
`integration/runtime-fixes` and `integration/ui-followup`.

`ui/` starts from the captured 1.4.2 source. The separate beta build generates one
Runtime hash pin shared by the UI modules and Identify shim. Compile against the
complete beta capture's Mono profile: a separate netstandard compiler facade
cannot resolve Harmony's `mscorlib` Emit.Label reference. No game, Noesis, Unity,
BepInEx, original author DLL or compile-time stub belongs in the deliverable.
The AnchorChain fork retains its MIT license.

## Build and validation

With PowerShell 7.4 alone, using the Roslyn compiler it ships (C# 12):

```sh
pwsh -NoProfile -File integration/beta-feature-parity/build-roslyn.ps1 \
  -Capture /path/to/extracted-beta-capture -Output /path/to/separate-candidate-output
```

That is the same build as build.py (same checks, sources, generated files
and switches) without a .NET SDK; the receipt names the compiler. R3's sources
rebuilt this way are IL-identical to R3's payload in every Runtime, loader
and bootstrap method; only the UI and shim pins differ, as they hash the
Runtime. A capture taken after a candidate was installed holds that candidate
in the Workshop folder; both scripts then take the preserved 1.5.0 from
`integration/runtime-fixes` for the provenance and parity checks.

With a .NET 8 host and Roslyn 4.12:

```sh
python integration/beta-feature-parity/build.py \
  --capture /path/to/extracted-beta-capture \
  --dotnet /path/to/dotnet8/dotnet \
  --compiler /path/to/roslyn-4.12/tasks/netcore/bincore/csc.dll \
  --output /path/to/separate-candidate-output
```

The build checks captured reference hashes and writes a receipt with source,
compiler and output hashes. It never installs a file in the game or Workshop.
Managed test executables run with Mono, captured BepInEx dependencies and Unity
managed reference DLLs. Installer fixtures run with PowerShell 7.4.6, using copies
of the real captured beta DLLs; Windows PowerShell 5.1/game execution still needs
the PC test below. The uploaded capture itself ran under PowerShell 5.1.

Validation covers numerical policy/history parity, price-factory/cache behavior,
Native/Noesis/tracker bindings, actual beta sonar and Contacts IL rewrites,
current Pop-Out interfaces, real Identify getter detours, loader failure ordering,
installer staging/nonce checks/data migration/rollback, and unchanged source hashes
for game, author files, campaigns and saves. These checks are not Unity gameplay.

## PC test sequence

Keep Steam on beta and close the game before every script.

1. Extract the candidate ZIP into Downloads and run `1-Stage-Beta.cmd`.
2. Launch beta to the main menu, wait about 10 seconds, then quit. No plugin
   chain is enabled in this probe. If no receipt appears, run the capture script.
3. Run `2-Enable-Beta.cmd`. It verifies the probe, migrates Identify data and
   enables the bounded loader for the next launch.
4. Launch beta. Confirm only Workshop Identify Expanded is listed; test F11
   costs/history, debrief, preparation and a second mission, Contacts keys and
   pop-out/return, Formation pop-out/return, and camera compass behavior.
5. Quit and run `3-Capture-Test-Results.cmd`, then provide its ZIP for review.

`Restore-Previous-SEST.cmd` restores the backed-up code pair, removes added code,
and restores the former local folder. Migrated/new data outside the game remains
available. Settings restore byte for byte if unchanged since Enable; subsequent
user edits are preserved. Backups remain under
`%LOCALAPPDATA%\SEST\BetaCompatibility\backups`.

In-game launch, rendering, second-monitor behavior and campaign progression remain
unverified until this PC test. This candidate is not a published Steam update.

R12 world operations follow-up: Runtime 1.6.1 / UI 1.4.11. F11 Overview reads
the live rank definitions, next renown threshold, recruitment unlock counts
and offered/active Admiralty rewards. It never grants or modifies rewards.
Global Maritime Operations 2028 adds eight command stages and reviewed public
airfield locations in the data pack. New campaign required for the full layout.

R12 map-cost and opening-brief follow-up: Runtime 1.6.2 / UI 1.4.12.
The strategic map uses CampaignView.Instance and its named WindowHost,
not the tactical mission RootControl or the linear Task Force menu.
Combat Costs beside Economy and F11 open Cumulative Combat Costs.
The world opening paper uses concise sections and wrapped body text;
other DCM briefings and the native close/guide commands are retained.
# R12 ribbon expansion - 10 November 2026

Runtime 1.6.3 / UI 1.4.13 adds 25 fictional world service awards, including
accepted/completed Admiralty duties, campaign-day and theatre milestones.
The existing v1 service ledger and all old award IDs are retained. Failed,
cancelled, unaccepted, moot and other-side orders cannot earn task ribbons.
Task evidence does not inflate manual-battle counts or USD history.

Authored campaigns add eight operation ribbons and six real-award
representations. Southern Watch and Southern Reach retain Australian defaults
and offer US commander nationality at native onboarding. National grants use
the captured native pipe/comma grammar and the commander's committed nation.
The native debrief requires mission completion and the required result before
granting its mission awards. All real-award citations explain their fictional
scenario qualification; they are separate from world battle-count awards.

Check F11 Service scroll/progress, completed convoy/shadow/route assignments,
native campaign ribbon racks/citations and both commander nationalities. Keep
the previously accepted opening brief, Combat Costs sidebar and direct F11.
