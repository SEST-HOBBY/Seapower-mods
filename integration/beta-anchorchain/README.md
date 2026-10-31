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

**Source patch only.** No compiled/fitted/final beta DLL is available in the repository. The launch failure in PR #53 was reproduced with the unmodified upstream loader after the bootstrap discovered mods. Do **not** reinstall PR #53's `SEST.BetaAnchorBootstrap.dll`. Do not change Workshop item 3380210757 or distribute a replacement until a controlled beta test verifies bootstrap plus bounded loader and reviews independent native API failures.

The target beta is **0.8.7-261026**. Runtime 1.5.0 and UI Follow-up remain deliberately disabled on the beta until their own source and APIs can be validated; changing Anchor Chain does not make them compatible.
