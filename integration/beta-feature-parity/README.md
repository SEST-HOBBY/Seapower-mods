# Beta compatibility candidate — full pre-beta SEST feature implementation

This candidate targets **beta Build 261026** (`3005bc6d…`), keeping one existing
SEST Workshop item (`3812461539`). It restores the Runtime/UI feature code for
beta testing. It does not change the Steam branch or replace campaign/data packs.
The earlier stable restore ZIP is superseded for this task.

## R4: version watermark, the beta's #!extend scan, cost item rows

Built on 3 November 2026 from the 2 November 22:26 capture, which recorded
R3 playing its first campaign mission. Runtime 1.5.2 beta; the loader,
bootstrap, UI 1.4.3 beta and Identify shim are R3's sources rebuilt with the
same compiler as the Runtime (see the build section). GPT had described these
three fixes on 2 November but its R4 build was never delivered; this is a new
implementation from the same evidence.

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
Not done: the clipped tab borders (no screenshot was attached) and ports of
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
