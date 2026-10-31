# Beta 261026 — Anchor Chain startup compatibility

**State:** experimental source bridge, not tested in the beta, no packaged DLL, no live game or Workshop deployment.

## Root cause supported by the capture

On Build 261026, the 28 October BepInEx log has the preloader Awake and then
"Could not find AnchorChain chainloader". In the game's Player.log the
FileManager later announces it contains the Mods directory. Upstream
[AnchorChain.Preloader/Preloader.cs](https://github.com/SeaPower-Modders/AnchorChain/blob/main/AnchorChain.Preloader/Preloader.cs)
runs its search in Awake: FileManager.Instance.Directories -> *.dll ->
AnchorChain.dll. It does not retry after the game populates directories.

The deferred bridge is an **opt-in beta-only** BepInEx plugin, with these limits:
- Game SHA-256 must equal known Build 261026 Seapower-Scripts hash 3005bc6d...
- It never modifies upstream files, game DLLs or SEST Runtime 1.5.0.
- It uses *the FileManager-registered directories*, only looks for the upstream
  AnchorChain.dll, waits for 3 seconds stable visibility, and invokes the
  upstream LoadPlugins entrypoint once, with a 60 second timeout.
- Refuses multiple matching AnchorChain.dll candidates and unexpected assembly
  name/version.
- No attempt to retarget SEST runtime/UI hash pins. Even after Chainloader
  starts, Runtime 1.5.0 and UI Follow-up 1.4.2 are correctly inactive until
  they are separately reconstructed/verified against beta APIs.
- Does not solve any native API mismatch, Noesis 4.0.1 changes, mission
  geometry/trigger migration, game balance, cost data or performance stutter.

## Build (Windows .NET Framework C# compiler or Mono mcs)

Game closed:

    powershell -NoProfile -ExecutionPolicy Bypass -File integration/beta-bootstrap/build.ps1 -GameRoot "C:\Program Files (x86)\Steam\steamapps\common\Sea Power"

The script verifies the exact beta SHA-256 and builds out/SEST.BetaAnchorBootstrap.dll
locally. It uses Mono mcs when available, otherwise Windows .NET Framework
csc.exe (and references UnityEngine.dll plus UnityEngine.CoreModule.dll).
It NEVER installs the output. **Do not ship an untested DLL.**

## Validation required before beta deployment

1. On an isolated copy of beta Build 261026, verify references and compile.
2. Confirm the upstream AnchorChain.dll actually appears in a FileManager
   registered directory. If it does not, diagnose the game's changed directory
   discovery/Workshop root first.
3. Test with the upstream preloader untouched and only this beta bridge added
   as a BepInEx plugin. The upstream preloader must log its initial failure;
   then this bridge should report "Deferred Anchor Chain LoadPlugins invoked".
4. Verify actual plugin entrypoint logs (not just one bridge message), including
   Dynamic Campaign, Contact Log and Topographic Map.
5. Confirm no duplicate plugin/Harmony patches on successive mission loads,
   with game/plugin shutdown and restart.
6. Check stable Build 261021 remains untouched and its normal preloader works.
7. Rebuild/re-gate Runtime 1.5.0 and UI Follow-up separately against beta
   assemblies; continue to fail closed on uninspected signatures.

**Deployment gate:** no public Workshop upload until the above passes; retain a
known-good rollback and restore the pre-test BepInEx/plugins directory if a
test changes it.

Upstream Anchor Chain is MIT-licensed; the bridge here reuses no upstream
source and calls its public plugin loader through reflection. The approach
should be proposed upstream as a lifecycle fix after validation.
