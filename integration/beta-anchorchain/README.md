# Sea Power Beta 261026 — bounded Anchor Chain loader

This folder contains a source-level fork of the MIT-licensed [AnchorChain 1.1.0](https://github.com/SeaPower-Modders/AnchorChain) loader. The fork preserves its assembly name `AnchorChain` for mod dependency compatibility. It is **not** the published Workshop `AnchorChain.dll` and is **not** a drop-in public update.

## Fixed failure path

The upstream `AnchorChainLoader.LoadPlugins()` loops over pending plugin classes. If a plugin throws during `TriggerEntryPoint()`, it leaves the plugin in the pending set. If no plugin succeeds in that iteration, the upstream code prints `Aborting chainload` but **never breaks**. This permits an unbounded CPU loop and repeated partial Harmony installations. Beta Build 261026 produced 351 `[AutomaticSAR] Loaded.` messages after failed native patch installations, consistent with this defect (not proof that Automatic SAR is the faulty plugin).

The SEST fork makes three narrowly scoped changes:

1. **One-shot loader entry:** a thread-safe guard rejects repeated invocations of `LoadPlugins()`, even after a failure.
2. **One attempt per plugin:** failures are removed from the pending set. Success and failure are logged distinctly; pending dependents never force a retry of failed plugin code.
3. **Bounded/no-progress exit:** the loop stops when it cannot make progress, with a hard upper bound on iterations.

No Harmony methods, game files, missile behavior, campaign data or Runtime 1.5.0 version checks are changed.

## Provenance and licence

- Upstream: https://github.com/SeaPower-Modders/AnchorChain
- File: `AnchorChain/Main.cs`, sourced 31 October 2026 from upstream `main`.
- Upstream version: 1.1.0, MIT; retain `LICENSE.md` with derivative distribution.
- Build uses installed BepInEx, AnchorChain.Preloader, Unity, Noesis, Harmony and Sea Power reference assemblies from the **user's** game installation. None is committed to SEST.

## State / gate

**Source patch and staged test tooling only.** No compiled/validated beta DLL is available in the repository. The launch failure in PR #53 was reproduced with the unmodified upstream loader after the bootstrap discovered mods. Do **not** reinstall PR #53's `SEST.BetaAnchorBootstrap.dll`. Do not change Workshop item 3380210757 or distribute a replacement until a controlled beta test verifies bootstrap plus bounded loader and reviews independent native API failures.

The target beta is **0.8.7-261026**. Runtime 1.5.0 and UI Follow-up remain deliberately disabled on the beta until their own source and APIs can be validated; changing Anchor Chain does not make them compatible.

## Build and staged testing (not a production install)

Run from the repository root with Sea Power closed. A .NET 8+ SDK is required
to compile the MIT-licensed C# 12 upstream fork; Windows' built-in .NET
Framework csc.exe compiles the small bootstrap. The build never writes to the
game installation.

    .\integration\beta-anchorchain\build.ps1 -GameRoot "C:\Program Files (x86)\Steam\steamapps\common\Sea Power"

After build and code review, an optional first test stages the two binaries
without enabling Anchor Chain. The stage script refuses unknown or pre-existing
files and refuses the old PR #53 bootstrap.

    .\integration\beta-anchorchain\test.ps1 -Action Stage

Launch beta to the main menu and quit. Check the log:

    .\integration\beta-anchorchain\test.ps1 -Action Report

Only if the log explicitly says BETA SAFE BOOTSTRAP READY; enable=False, and
the staged launch was clean, can a separate opt-in enable the bounded loader:

    .\integration\beta-anchorchain\test.ps1 -Action Enable

This is not a substitute for an isolated beta test: unrelated third-party
plugins may still crash on native method changes. Do not use this on an
important game save until the full plugin chain has been checked. On a
failure, close the game and run:

    .\integration\beta-anchorchain\test.ps1 -Action Disable
    .\integration\beta-anchorchain\test.ps1 -Action Remove

Remove verifies the recorded hashes of all files it deletes. It leaves
Steam Workshop 3380210757, the original preloader, SEST Runtime 1.5.0,
game assemblies, subscribed mods and user settings untouched. The bounded
fork is staged in BepInEx/config/SEST-BetaAnchorChain/, not copied over
the Workshop author's file. A single BepInEx bootstrap is installed in
BepInEx/plugins/ and only loads the staged bounded fork after explicit
enablement.

### Full acceptance criteria

- First stage launch is normal and logs READY; enable=False.
- Enabled launch reaches main menu, never prints hundreds of duplicate
  AutomaticSAR Loaded messages, and the bounded loop terminates.
- A failed plugin is not retried in the same process (look for the
  "skipped for this run" message in BepInEx).
- Repeated launches and mission transitions do not double-install Harmony
  patches.
- Beta missions, World Sandbox, native F11 costs and the SEST UI can only be
  called compatible when separately tested; this fork alone does not re-gate
  Runtime 1.5.0 or fix broken mods' native method signatures.
- Game must still launch after removing the staged fork and bootstrap.

Do not merge or publish the beta build until these checks pass.
