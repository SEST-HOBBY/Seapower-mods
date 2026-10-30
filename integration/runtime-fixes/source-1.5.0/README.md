# source-1.5.0 - reconstruction of SEST Runtime Fixes 1.5.0 (seed, 30 Oct 2026)

This folder is **not** the source of the shipped `../SEST.RuntimeFixes.dll`
(Runtime 1.5.0, SHA-256 `7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986`,
128,000 bytes, a capture from the owner's PC whose original project was never
handed over: `../README.md`). It is the starting point for rebuilding that
source, and it builds only to a scratch path:

    SEST_MONO_PREFIX=<mono prefix> python3 integration/runtime-fixes/build_plugin.py \
        --source integration/runtime-fixes/source-1.5.0 --output <scratch>/SEST.RuntimeFixes.dll \
        --reference <game>/Sea\ Power_Data/Managed/Seapower-Scripts.dll \
        --reference <game>/BepInEx/core/0Harmony.dll

`build_plugin.py` never writes the committed DLL or `plugin-build.json` for a
`--source` build, and `--source` without `--output` is refused. The captured
`7ba6d6d9...` stays what the pack ships, and SEST UI Follow-up 1.4.2 pins that
hash, until the owner decides otherwise. Do not pass
`--replace-captured-binary`.

## Where every file came from

- **Decompiled reference, downleveled to C# 7.2** (18 files): `Api.cs`,
  `CampaignCosts.cs`, `ContactHostScope.cs`, `ContactPopOutState.cs`,
  `ContactWindowBridge.cs`, `CostBounds.cs`, `CostLineKind.cs`,
  `CostReportLine.cs`, `CostWindowState.cs`, `CumulativeCombatCostsViewModel.cs`,
  `F11CombatCosts.cs`, `NativeCombatSurface.cs`, `NativeCostTypography.cs`,
  `PopOutBridge.cs`, `PreparationMap.cs`, `RuntimeFixesMod.cs`,
  `TowedSensorGuard.cs`, `UiStartupGate.cs`. The decompile is the 27 Oct
  2026 handoff's `review/pc-playtest-20261027/runtime-1.5.0-reference/`
  (ILSpy-style C# 10 of the captured DLL, byte-identical in both handoff
  zips, tree hash `035fa6279f8aea1a011f7162dc47c55cb7e1acb94a4f4dbc7e2d25e705dbf44e`
  over `sha256sum` of its 32 files; its own README calls it "not
  authoritative runtime source"). The 27-28 Oct review rewrote it
  mechanically for Mono mcs: file-scoped `namespace X;` became a block,
  each `using var x = ...;` declaration became a `using (...) { }`
  statement to the end of its block, and the one switch expression
  (`CombatPrices`, not used here) became a switch statement. Nothing else
  was changed, so these files still carry the decompiler's shapes
  (expression-bodied getters, hoisted temporaries, `bool?` where the
  original tested a field, members grouped by kind), which is where most of
  the remaining differences come from.
- **The 1.2.0 fork base verbatim** (`../*.cs` at commit 7e86df43, hashes in
  `../plugin-build.json` `fork_base.inputs`): `CampaignInventory.cs`,
  `CombatPrices.cs` (with `CombatAmount`), `Policy.cs`, `TaskForceDebrief.cs`,
  `TerrainClearance.cs`. Every method of those types is IL-identical to
  1.5.0's. `CombatHistory.cs` is the fork's file plus one line, the
  `CompletedAt` field of `CombatGameRecord` (1.5.0 has it; the fork does not).
- **`stubs/`**: `Noesis.NoesisGUI.cs` and `UnityEngine.CoreModule.cs` are
  compile-time stand-ins for the game assemblies of those names, written by
  the 27 Oct review from the MemberRefs the captured DLL records (only the
  members 1.5.0 uses, with the owner types 1.5.0 names). `build_plugin.py`
  compiles each `stubs/<Assembly>.cs` to `<Assembly>.dll` in its temporary
  folder and references it; neither is shipped. The real
  `Noesis.NoesisGUI.dll` (`c4e2c37c...`) and `UnityEngine.CoreModule.dll`
  are not in the repository or on the build machine, so every signature the
  stubs declare must be re-verified against the game's files before a build
  from here is tried on the PC. The Anchor Chain stand-in is the committed
  `integration/menu-background/stubs/AnchorChain.cs`, as for the fork base.
  `Seapower-Scripts.dll` (Build 261021, SHA-256 `eab2297b...`, the build
  1.5.0 pins) and BepInEx's `0Harmony.dll` (HarmonyX 2.9.0, `1a21cc03...`)
  are passed with `--reference` and are never committed.

## Where the build stands

With Mono mcs 6.8.0.105 (`-langversion:7.2 -optimize+`, the builder's flags;
the decompiled code needs 7.2 for a named argument before a positional one
in `NativeCombatSurface.cs`) and the references above, the build is
deterministic (two runs, same bytes) and gives SHA-256
`e466b056617664ecf9e87be64d102479035d6236f2ee775f419f7bc08ab35320`
(128,512 bytes). Its IL is identical, method for method, to the 27 Oct
review's hybrid build (`a2a873cd...`, which this folder reproduces once the
decompiled `Properties/AssemblyInfo.cs` is compiled in, named `hybrid.dll`).

Against the captured 1.5.0, **253 of 317 methods are IL-identical**
(instructions, operands, locals signature, max stack and exception handlers)
and 64 differ. None is missing or extra; all 51 types, 621 string literals
and 6 referenced assemblies' names match. The 64, by the area one agent can
finish at a time:

- **core-pins** (3): `Api.FindType`, `Api.Hooks`, `RuntimeFixesMod.TriggerEntryPoint`.
- **f11-native-windows** (15): `CumulativeCombatCostsViewModel.Change`, `.Set`;
  `F11CombatCosts.AfterUpdate`, `.BeforeDestroy`, `.Modified`, `.Poll`,
  `.SyncWindow`, `.TrackerLoaded`; `NativeCombatSurface.ApplyBounds`,
  `.BoundTo`, `.Close`, `.Root`, `.Tick`, `NativeCombatSurface/<Walk>c__Iterator0.MoveNext`;
  `NativeCostTypography.Render`.
- **popout-bridges** (17): `ContactPopOutState.Encode`;
  `ContactWindowBridge.AfterTick`, `.EnsureBound`, `.MainPanel`, `.Move`,
  `.Save`, `.Snapshot`, `.Warn`, `.get_MainRoot`; `PopOutBridge.AfterFormation`,
  `.EnsureBound`, `.FinishFormation`, `.StateForFormation`, `.TrackStandalone`,
  `.get_Host`, `.get_Root`, `.get_Screen`.
- **preparation-map** (2): `PreparationMap.Preparing`, `.Refresh`.
- **towed-sensor-guard** (3): `TowedSensorGuard.Bind`, `.Transpile`, `.Warn`.
- **campaign-costs-inventory** (24, all in `CampaignCosts`): `AddPlatform`,
  `Basis`, `BindLive`, `CampaignSource`, `CampaignView`, `CaptureLive`,
  `CaptureSavedSide`, `Categories`, `Clip`, `CompletionDate`, `Full`,
  `LegacySource`, `LiveView`, `Losses`, `MissionTitle`, `Postfix`, `PriceRaw`,
  `Prices`, `RawStores`, `Read`, `Recovered`, `SavedGames`, `TotalKind`, `Weapons`.
- **debrief** (`TaskForceDebrief`) and **terrain** (`TerrainClearance`): 0,
  as for `Policy`, `CombatPrices`, `CombatHistory`, `CombatHistoryStore`,
  `CombatGameRecord`, `CombatSideRecord`, `CombatAmount`, `InventoryLedger`,
  `CampaignInventory`, `UiStartupGate`, `CostBounds`, `CostLineKind`,
  `CostReportLine`, `CostWindowState`, `ContactHostScope`.

The differences are the decompiler's reshaping, not other behaviour: inverted
branch polarity (`brfalse` for `brtrue` with the arms swapped), an early
`ret` written as a jump, locals declared in another order or hoisted (`foreach`
arrays), `ldloc.s` for `ldloc.3` once a temporary is added, string
concatenation forms, a `bool?` temporary in `NativeCombatSurface.BoundTo`,
and the iterator's loop variable named `i` where 1.5.0 had `n`. Each is
reworked by hand against the capture's IL until the method matches.

Beyond method bodies, the capture also fixes the metadata a byte-identical
rebuild needs, all of it source order or source form:

- Type order (file order on the mcs command line): `CampaignCosts`,
  `InventoryLedger`+`CampaignInventory`, `CombatSideRecord`..`CombatHistory`,
  `CombatPrice`+`CombatPrices`+`CombatAmount`, `ContactHostScope`,
  `ContactPopOutState`, `ContactWindowBridge`, then `CostLineKind`,
  `CostReportLine`, `CumulativeCombatCostsViewModel`, `CostBounds`,
  `CostWindowState` (one file in that order), `F11CombatCosts`,
  `NativeCombatSurface`, `NativeCostTypography`, `Policy`, `PopOutBridge`,
  `PreparationMap`, `RuntimeFixesMod` then `Api` (one file, the fork's
  `SestRuntimeFixes.cs` layout), `TaskForceDebrief`, `TerrainClearance`,
  `TowedSensorGuard`, `UiStartupGate`. The seed keeps one file per type as
  the decompile has it; `Api` and the five cost types sort elsewhere.
- Member order inside `CampaignCosts/CostView`, `ContactWindowBridge`,
  `CumulativeCombatCostsViewModel` (event first), `NativeCombatSurface`,
  `PopOutBridge` (the decompiler groups properties before methods), and the
  `CompletedAt` field before `Context` in `CombatGameRecord`.
- Sixteen getters the decompiler wrote as `=> expr` (`CostView.Lines`,
  `Side.Losses`/`Total`, `ContactHostScope.Active`, `CostBounds.Width`/`Height`,
  `CumulativeCombatCostsViewModel.Title`/`Subtitle`/`Summary`/`Details`/`Notes`,
  `F11CombatCosts.Now`, `NativeCombatSurface.Ready`/`IsMouseOver`,
  `PopOutBridge.Screen`/`CanOpenStandalone`): mcs marks expression-bodied
  accessors `[CompilerGenerated]`; 1.5.0's are not marked, so the original
  wrote `{ get { return ...; } }` as the fork does.
- References: 1.5.0 references only `netstandard 2.1.0.0` for the base
  library (no mscorlib/System/System.Core), so it was compiled with
  `-nostdlib -noconfig` against the .NET Standard 2.1 reference set
  (NETStandard.Library.Ref 2.1.0, `ref/netstandard2.1/*.dll`, the same set
  SEST UI Follow-up's `build.py` takes as `--framework`) and a
  netstandard-targeting `0Harmony.dll` (HarmonyX 2.9.0 `lib/netstandard2.0`;
  the game's `BepInEx/core/0Harmony.dll` is that package's net35 build and
  stops mcs on `System.Reflection.Emit.Label`, the "Emit.Label" problem the
  handoff mentions). Built that way here, the seed's AssemblyRef table and
  heap sizes equal 1.5.0's. `build_plugin.py` has no option for that recipe
  yet; the mscorlib-referenced build it makes is what the IL comparison uses.

## Tests

None yet. The fork base's `../tests/` do not compile against this folder:
`HistoryTests.cs` calls `CampaignCosts.CampaignLines(games, 10)` (1.5.0's
takes one argument), `F11CostTests.cs` uses `CostGUI` (gone in 1.5.0), and
the mocked `SeaPower.Globals` lacks `_mainGameViewModel`, which
`ContactWindowBridge` and `NativeCombatSurface` read; a mocked harness for
1.5.0 also needs stand-ins for the Noesis types the windows and bridges use.
When `tests/` exists here, `build_plugin.py --source` compiles and runs it
like the fork's.
