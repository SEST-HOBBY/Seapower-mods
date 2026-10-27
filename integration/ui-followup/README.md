# SEST UI Follow-up - developer notes

`SEST.ContactsFix.dll` is SEST's third Anchor Chain plugin: **SEST UI
Follow-up 1.4.2** (plugin id `io.github.sest-hobby.contacts-input-fix`),
SHA-256 `51b56f5efb4c32dcd7f9d71633564613707e6484c3cffdea1adc891b589588f7`,
79360 bytes. It is committed as built, beside its source in `source/`. The
campaign builder (`build_pack.write_contacts_fix`) copies only the DLL into
the pack's `plugins/`, next to SEST Runtime Fixes; `source/`, including
`AnchorChain.Reference.cs`, never ships (a second AnchorChain assembly in a
mod folder would be loaded beside the real one).

The DLL is the one the owner's gaming PC runs: captured from `plugins/` of
its Steam Workshop copy of the pack on 27 Oct 2026 (13:18 Brisbane), where
the 1.4.2 update had installed it beside Runtime 1.5.0. The same bytes are
in the 27 Oct handoff's PC baseline and in PR #50's dist; the 32 files in
`source/` are PR #50's `integration/ui-followup/source/`, byte for byte.
`plugin-build.json` records the DLL's hash, every source file's hash, the
pinned hashes read from the source and the toolchain. The handoff's
installer, capture scripts, release ZIP and its decompiled Runtime 1.5.0
reference are deliberately not here.

## What it fixes

It patches the game, Contact Log, Group Manager and SEST Runtime 1.5.0's
own code at run time; no DLL on disk is edited. Each part installs on its
own and logs one `[SEST UI Follow-up]` line to `Player.log` saying whether
it did.

- **Contacts keys** (`ContactsFix.cs`, `InputPolicy.cs`). Contact Log's
  shortcut check now matches only a real key-down of a bound key, so Space
  and plus/minus change simulation time without opening or closing
  Contacts.
- **Contacts pop-out** (`ContactsFix.cs` `LogicalParents`,
  `ContactsSurfaceFix.cs`, `UiRefinements.cs`). Runtime 1.5.0's
  `ContactWindowBridge` looks up Contact Log's tab buttons through the
  logical tree, which Contact Log builds them in; moving Contacts to the
  Pop-Out Windows screen moves the scaled panel that holds the contact list;
  the pop out / return button is sized to its text.
- **Quick-load key** (`UiRefinements.cs`). A quick-load bound to F9 alone
  is rebound to Ctrl+F9 in memory, leaving F9 to Contacts. Any other
  quick-load binding is left alone.
- **Preparation instructions** (`UiText.cs`). The game's aircraft and unit
  preparation popup gets the full four steps and a Start preparation
  button.
- **Group Manager (Formation Manager)** (`FormationUiMode.cs`,
  `FormationPerformance.cs`). A Stock UI / Enhanced UI switch beside the
  pop-out control; idle discovery no longer forces a full fitting search,
  and the pop-out chrome refreshes at most 5 times a second.
- **Camera compass** (`CameraCompass.cs`). The bearing tape follows the unit
  camera, on the second monitor too.
- **Cost catalogue cache, new in 1.4.2** (`CostCatalogueCache.cs`,
  `ScopeValueCache.cs`). In a mission Runtime 1.5.0's F11 window rebuilt its
  price catalogues (five files) on every 0.5 s refresh; the 27 Oct capture
  measured 253-494 ms stalls there. The cache reuses each successful result
  for the rest of the mission and clears on a mission change and on the
  Combat Cost Tracker's own config reload; failures are never cached.
- **Performance** (`PerformanceReview.cs`, `TerrainCleanup.cs`). The menu
  plugin's picture diagnostics are switched off (no `[SEST Pictures]` lines,
  whatever `sest_menu.ini` says) and its backdrop discovery pauses during a
  mission; the Contacts screen button refreshes at most 5 times a second;
  in a mission, the unused-asset unloads the game starts after building
  terrain texture arrays are batched (after 350 ms quiet, or 2 s at most);
  CV16's runway clearance reads a helicopter's own in-flight flag.
- **Diagnostics** (`StutterDiagnostics.cs`, `FramePacing.cs`,
  `DiagnosticModules.cs`). Aggregate timing, frame-pacing and memory lines
  in `Player.log` every 30 seconds, for the stutter investigation.

## Hash-coupled: inactive, harmlessly, anywhere else

The whole plugin installs only if every one of these matches by SHA-256
(read from `source/`, recorded under `pins` in `plugin-build.json`):

| Assembly | SHA-256 | Pinned in |
| --- | --- | --- |
| `SEST.RuntimeFixes` (Runtime 1.5.0, `integration/runtime-fixes/`) | `7ba6d6d9...` | `ContactsFix.cs` `RuntimeHash`, `CostCatalogueCache.cs`, `DiagnosticModules.cs` |
| `ContactLog` (Contact Log 1.0.1, Workshop 3819427362) | `a1b8b450...` | `ContactsFix.cs` `ContactHash`, `DiagnosticModules.cs` |
| `Seapower-Scripts` (Sea Power 0.8.7 Build 261021) | `eab2297b...` | `ContactsFix.cs` `NativeHashes[0]` |
| `Noesis.NoesisGUI` (the same game build's) | `c4e2c37c...` | `ContactsFix.cs` `NativeHashes[1]` |

With any of them missing or different it logs `inactive; original behavior
retained` (or `inactive: owning pack is disabled`) and patches nothing, so a
player without Contact Log, on another game build or beside another runtime
DLL gets the pack exactly as without it. Single parts carry their own pins
(Combat Cost Tracker 0.7.1, Pop-Out Windows 1.0.1, Group Manager 0.2.17,
SEST.MenuBackground.dll `9dfd561d...`, CV16; `module_pins` in
`plugin-build.json`); a mismatch there turns off that part only.

So **any change to `integration/runtime-fixes/SEST.RuntimeFixes.dll`,
including a rebuild that differs by one byte, turns this plugin off** until
it is rebuilt with the new hash in all three places.
`tools/tests/test_contacts_fix.py` fails when the pins and the committed
runtime disagree. A rebuilt `SEST.MenuBackground.dll` turns off its
picture-performance part only.

## Building it (outside the repository)

It cannot be compiled here: it compiles against the game's own
Noesis.NoesisGUI and other game assemblies, which are never committed, and
Mono mcs stops on the missing Noesis types. It was built with
`source/build.py`:

    python source/build.py --dotnet <dotnet> --compiler <csc.dll>
        --framework <NETStandard.Library.Ref 2.1.0 ref/netstandard2.1>
        --references <folder with the game's 0Harmony, BepInEx, Noesis.NoesisGUI,
                      Seapower-Scripts and UnityEngine Core/IMGUI/InputLegacy DLLs>
        --output <folder> [--runtime <SEST.RuntimeFixes.dll>]

That is Roslyn `csc` under `dotnet` with `-langversion:9 -deterministic+
-optimize+ -nostdlib+`, `AnchorChain.Reference.cs` compiled as a stand-in
`AnchorChain.dll`, then the five pure-logic suites run under `dotnet`;
`--runtime` adds `CatalogueRuntimeTests.cs`, which runs the cost cache
against the real runtime DLL. The Roslyn and .NET SDK versions used were not
recorded, so a rebuild may give other bytes even from the same source.

After a rebuild: commit the DLL, put its hash and size, and every changed
source's hash, into `plugin-build.json`, and rebuild the pack. When the
runtime changes, change `RuntimeHash` and the two other literals together
and rerun `CatalogueRuntimeTests` against the new runtime.

## Checks here

`tools/tests/test_contacts_fix.py`: the DLL matches `plugin-build.json`; the
files in `source/` are exactly the recorded ones with the recorded hashes;
every runtime pin in the source, and the hash in the DLL itself, equal the
committed runtime's `plugin-build.json`; the other pins equal the record;
the copies in `SEST_Campaign/plugins` and the dist equal the committed DLL;
and, when Mono is available (`mcs` and `mono` on the PATH, or
`SEST_MONO_PREFIX`), the five pure-logic suites compile with mcs and pass
(45 / 112 / 3768 / 41 / 12 checks on 27 Oct 2026). `CatalogueRuntimeTests`
and `verify_capture.py` need dotnet, 0Harmony or a PC capture and do not run
here.

## Open on 27 Oct 2026

The owner's PC ran 1.4.2 with Runtime 1.5.0 and reported a crash whose cause
is unknown; the last logged action was moving Contacts to the second screen,
a move that happens inside the pop-out button's own click handler. The
handoff reports the input fix, Contacts pop-out and return and the
Formation Manager controls working on the PC; that was not reproduced here.
