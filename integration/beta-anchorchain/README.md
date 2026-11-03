# Bounded Anchor Chain loader for Sea Power beta Build 261026

State: DRAFT. Source only: not shipped in the SEST pack, not installed by
SETUP or any build, and not to be merged into the stable pack or published
on the Workshop until the two-stage test below passes and the owner signs
it off.

This folder holds a source fork of the MIT-licensed
[Anchor Chain 1.1.0](https://github.com/SeaPower-Modders/AnchorChain)
loader and a SEST bootstrap that loads it on the public beta. The fork keeps
the assembly name `AnchorChain` so that mods which depend on Anchor Chain
still bind to it. It is not the published Workshop `AnchorChain.dll` and it
is not a drop-in public update.

## The failure the fork fixes

Upstream `AnchorChainLoader.LoadPlugins()` loops over a set of pending plugin
classes. When a plugin throws in `TriggerEntryPoint()`, the plugin stays in
the pending set. When no plugin loads in a pass, upstream logs
`Aborting chainload` but never breaks out of the loop, so it calls the
failing plugin again and again: an unbounded CPU loop that can apply a
plugin's Harmony patches many times over. On beta Build 261026 the failed
launch's Player-prev.log printed `[AutomaticSAR] Loaded.` 351 times after
failed native patches. That fits this defect but does not prove that
Automatic SAR is the plugin that threw; the first BepInEx log of that
launch was overwritten.

The fork makes three narrow changes to `AnchorChain/Main.cs`:

1. One-shot entry: a thread-safe guard (`Interlocked.CompareExchange` on
   `_startOnce`) ignores any second call of `LoadPlugins()`, even after a
   failure, and the body runs inside a catch that logs and returns.
2. One attempt per plugin: a plugin that throws goes into a failed set and
   leaves the pending set. Success and failure are logged differently
   ("skipped for this run"), and a pending dependant never makes the loader
   call the failed plugin again.
3. A bounded loop: the loop stops when a pass loads nothing while plugins
   are still pending, and it never runs more than one pass per recognised
   plugin plus one.

Nothing else changes: no Harmony patch, game file, missile behaviour,
campaign data or Runtime 1.5.0 version check.

## Provenance and licence

- Upstream: https://github.com/SeaPower-Modders/AnchorChain
- File: `AnchorChain/Main.cs`, taken on 31 October 2026 from upstream
  `main`, version 1.1.0, MIT. `LICENSE.md` is the upstream licence,
  verbatim, and must travel with any copy of the fork.
- The build references BepInEx, AnchorChain.Preloader, Unity, Noesis,
  Harmony and Sea Power assemblies from the user's own game installation.
  None of them is committed to SEST, and `.gitignore` keeps any compiled
  DLL out of the repository.

## State

Source patch and staged test tooling only. The owner compiled the bounded
fork on 1 November 2026, with two assembly-version warnings that do not
block the build. The bootstrap's SDK build and every in-game check are still
outstanding, and no compiled beta DLL is in the repository. The PR #53
launch failure was reproduced with the unmodified upstream loader after the
PR #53 bootstrap found the mods. Do not reinstall PR #53's
`SEST.BetaAnchorBootstrap.dll`. Do not change Workshop item 3380210757 or
distribute a replacement until a controlled beta test has passed with the
bootstrap and the bounded loader together and the separate native API
failures of other mods have been reviewed.

The target is the beta, 0.8.7 Build 261026. Runtime 1.5.0 and UI Follow-up
stay off on the beta under their own SHA gates until their source and the
beta's APIs have been checked; changing Anchor Chain does not make them
compatible.

## What the bootstrap does

`SEST.BetaSafeBootstrap.cs` is a BepInEx plugin (`io.sest.beta.safeanchor`,
0.2.0).

- At `Awake` it hashes `Sea Power_Data/Managed/Seapower-Scripts.dll` and
  `BepInEx/plugins/AnchorChain.Preloader.dll`. Unless both match the
  inspected Build 261026 and preloader hashes, it logs
  `Beta safe loader INACTIVE` and does nothing else.
- On a match it polls every half second, for up to 60 seconds, the game's
  `SeaPower.FileManager` singleton (`Instance`, inherited from
  `Singleton<FileManager>`) and its `Directories` list (each a
  `SearchDirectory` with a `DirectoryInfo`). It waits until a directory of
  Workshop item 3380210757, Anchor Chain's own item, is registered and the
  list has stayed the same for three seconds. This is the registration the
  upstream preloader runs too early to see on the beta.
- It then reads `BepInEx/config/SEST-BetaAnchorChain/enable.flag`. The
  loader is enabled only when that file exists and its whole content,
  trimmed, is exactly `enable-beta-261026` (an ordinal comparison). With no
  file, any other content or an unreadable file, it logs
  `BETA SAFE BOOTSTRAP READY; enable=False` and stops. If the directory
  never settles, it logs that and loads nothing.
- Only when enabled does it check the staged `AnchorChain.dll` against the
  `AnchorChain.sha256` beside it, check the assembly identity
  (`AnchorChain` 1.1.0.0), refuse when another `AnchorChain` assembly is
  already loaded from elsewhere, check that the fork's `_startOnce` gate is
  present and unused, and call `LoadPlugins()` once.

## Build and staged testing (not a production install)

Run these from the repository root with Sea Power closed. A .NET 8 or newer
SDK is needed to build both projects for netstandard2.1: the C# 12 Anchor
Chain fork and the SEST bootstrap. The Windows Framework csc.exe cannot
resolve the netstandard2.1 type references in the game's Unity 6000
assemblies. The build never writes to the game installation; it checks the
game, preloader and Workshop `AnchorChain.dll` hashes first and writes only
to `integration/beta-anchorchain/out/` with a build receipt.

    .\integration\beta-anchorchain\build.ps1 -GameRoot "C:\Program Files (x86)\Steam\steamapps\common\Sea Power"

After the build and a code review, the first test stages the two DLLs
without enabling Anchor Chain. Stage refuses an unknown game build, files
that already exist, an existing enable.flag and the old PR #53 bootstrap.

    .\integration\beta-anchorchain\test.ps1 -Action Stage

Launch the beta to the main menu and quit, then read the log:

    .\integration\beta-anchorchain\test.ps1 -Action Report

Only when the log says `BETA SAFE BOOTSTRAP READY; enable=False` and the
staged launch was clean may a separate opt-in enable the bounded loader:

    .\integration\beta-anchorchain\test.ps1 -Action Enable

This does not replace an isolated beta test: other third-party plugins may
still crash on the beta's changed native methods. Do not use it with an
important save until the whole plugin chain has been checked. On a failure,
close the game and run:

    .\integration\beta-anchorchain\test.ps1 -Action Disable
    .\integration\beta-anchorchain\test.ps1 -Action Remove

Remove checks the recorded hash of every file before it deletes it. It
leaves Workshop item 3380210757, the original preloader, SEST Runtime 1.5.0,
the game's assemblies, subscribed mods and user settings untouched. The
bounded fork is staged in `BepInEx/config/SEST-BetaAnchorChain/`, not
copied over the Workshop author's file. The one bootstrap DLL goes in
`BepInEx/plugins/` and loads the staged fork only after the explicit enable.

### Acceptance

- The first staged launch is normal and logs `READY; enable=False`.
- The enabled launch reaches the main menu, never prints hundreds of
  repeated `AutomaticSAR Loaded.` lines, and the bounded loop ends.
- A failed plugin is not called again in the same process (look for
  "skipped for this run" in the BepInEx log).
- Repeated launches and mission changes do not install Harmony patches
  twice.
- Beta missions, World Sandbox, native F11 costs and the SEST UI count as
  compatible only once each is tested; this fork does not re-gate Runtime
  1.5.0 or fix other mods' native method signatures.
- The game still launches after the staged fork and bootstrap are removed.

Do not merge or publish the beta build until these checks pass.

## Review notes (3 Nov 2026)

Points from reading the code against the beta's Seapower-Scripts.dll
(Build 261026), to settle before the first staged launch:

- The probe is not entirely free of side effects. `Singleton<T>.Instance`
  in Build 261026 creates a `(Singleton)SeaPower.FileManager` object
  when none exists yet, and `FileManager.Directories` builds the search-directory
  list on first read (it reads usersettings.ini and the Steam
  subscriptions, and publishes the file layers). The bootstrap's first probe runs during
  BepInEx's plugin load, which may be before the game creates its own
  FileManager. The game's `Singleton.Awake` destroys an instance it created
  itself when the scene's own one wakes, so this is probably harmless, but
  a probe that first checks `Singleton<FileManager>.InstanceExists(false)`
  (or the static `_instance` field) would touch nothing. Upstream's own
  `Setup()` reads the same property when it runs.
- `AnchorChain.sha256` is written by `test.ps1 -Action Stage` beside the
  DLL it describes, so the bootstrap's hash check proves the staged file is
  the one staged, not who built it. The build receipt is the record of
  that.
- Upstream's incompatibility check removes any plugin that declares an
  `ACIncompatibility`, whether or not the other mod is present (the
  `toRemove.Add` sits outside the `if`). The fork keeps that behaviour
  unchanged.
