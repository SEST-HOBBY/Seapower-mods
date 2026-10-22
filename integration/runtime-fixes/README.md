# SEST Runtime Fixes - developer notes

SEST's own Anchor Chain plugin (`SEST.RuntimeFixes.dll`): the Tomahawk MST
terrain clearance (`TerrainClearance.cs`) and the task-force debrief's lost
hulls (`TaskForceDebrief.cs`). What it does for a player is in
`SEST_RUNTIME_README.txt`, which the campaign builder
(`build_pack.write_runtime_fixes`) copies into the pack's `plugins/` with
`sest_runtime.ini` and the DLL. The plugin installs nothing unless the game's
`Seapower-Scripts.dll` hashes to the one inspected build
(`SestRuntimeFixes.cs`, `inspected`), and `verify_native_api.py` checks a
player-exported copy of that DLL against the signatures the plugin binds.

    python3 integration/runtime-fixes/build_plugin.py   # needs mono-mcs or SEST_MONO_PREFIX
    python3 integration/runtime-fixes/verify_native_api.py <Seapower-Scripts.dll>   # needs dnfile, dncil

`plugin-build.json` records the hash of every source, the stub, the builder
and the tests; `tools/tests/test_runtime_plugin.py` fails if any of them is
edited without running `build_plugin.py`, or if the DLL in the dist differs.
`SEST_RUNTIME_README.txt` and `sest_runtime.ini` are not inputs: they can be
edited and rebuilt into the pack without Mono.

## Off on Sea Power 0.8.7 (22 Oct 2026)

Sea Power 0.8.7 Build 261021 (21 Oct 2026, Steam build 26103404) ships a new
`Seapower-Scripts.dll`. The 22 Oct capture's `Player.log` reads
`[SEST Runtime] inactive: uninspected native assembly
eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd`, so the
plugin failed closed as designed: neither correction is installed, and every
player on 0.8.7 has the game's own MST cruise height and debrief. The DLL
itself (`9aa55df8...`) is unchanged and loads.

The new hash is not simply to be added. The assembly really changed (it grew
by 13,312 bytes, and other mods' plugins report `ObjectBase.LoadStateFromFile`
and `WeaponSystemLauncher.OnUpdate` changed), and `TaskForceDebrief` reads
the saved mission state that `LoadStateFromFile` handles. The 0.8.7 DLL is
not in this repository, so nothing here can be verified against it yet.

### Re-enabling once the owner sends the 0.8.7 DLL

1. **On the PC, game closed:**
   `powershell -ExecutionPolicy Bypass -File .\tools\export-map-diagnostics.ps1 -IncludeGameAssembly`.
   It writes `SEST-map-review-complete-<date>-<id>.zip` to Downloads with
   `game-reference/Seapower-Scripts.dll` and `file-manifest.csv`. Send the
   ZIP; do not commit the DLL. Record the ZIP's name, size and SHA-256 and
   the DLL's SHA-256 in a dated `data/*-review-*.json`, as
   `data/map-capture-review-20261020.json` does.
2. **Check it is the build the log named:** the DLL's SHA-256 must be
   `eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd`. Any
   other hash means the game moved again; capture again.
3. **Extend the verifier before trusting it.** `verify_native_api.py` checks
   12 method signatures, 3 fields, the 10 `FlightStage` names and the 0.405
   lookahead constant, but the plugin also binds members it never checks:
   `SeaPower.IniHandler` (`doesSectionExist`, `readValue(string, string,
   bool, bool)`), `SeaPower.LinearCampaignMission._index` (int),
   `LinearCampaignTaskForceBuilderRosterItem.CrewSkill`, the debrief view
   model's `UnitRows`, and the snapshot items' `InstanceId`, `UnitType`,
   `UnitFolder`, `Category`, `VariantReference` and `CrewSkill`. Add them to
   `SIGNATURES` (or field checks) from the 0.8.6 DLL first, in the owner's
   `SEST-map-review-complete-20261020-103158-5173b0.zip`, so the 0.8.6 run
   still passes.
4. **Verify against 0.8.7:** `pip install dnfile dncil`, set `EXPECTED` in
   `verify_native_api.py` to the new hash and run it on the 0.8.7 DLL. Every
   check must pass; a changed signature means the binding code changes too.
5. **Compare behaviour, not only signatures.** Diff the IL of
   `TerrainUtils.GetSafeAltitudeOverSurface`,
   `TerrainUtils.CrudeGetHighestTerrainHeightAhead`,
   `LinearCampaignTaskForceDebriefViewModel.ReadUnitRows` and
   `LinearCampaignTaskForceSaveManager.ReadSnapshot` between 0.8.6 and 0.8.7.
   If the native `ReadUnitRows` now lists lost hulls itself, retire
   `TaskForceDebrief` (set its option to 0 and say so) rather than
   re-enable it: two rows per lost ship would be worse than none.
6. **Re-gate the plugin:** `SestRuntimeFixes.cs` (`inspected` and its
   comment, one line each), the message at the end of
   `verify_native_api.py` ("Native 0.8.7 ABI verified"), the first line of
   `sest_runtime.ini`, and `SEST_RUNTIME_README.txt` (its 0.8.6 sentence and
   the *On Sea Power 0.8.7* paragraph, which then goes).
7. **Rebuild the DLL:** `python3 integration/runtime-fixes/build_plugin.py`
   (Mono). It runs the mocked regressions and rewrites the DLL and
   `plugin-build.json`; `test_runtime_plugin.py` fails until it has run.
8. **Rebuild the pack:** `python3 tools/build_all.py --from-scratch`
   (`write_runtime_fixes` copies the plugin into `SEST_Campaign/plugins` and
   the dist), then the twelve gates and both test suites.
9. **On the PC, after syncing:** `Player.log` must show both
   `[SEST Runtime] ... correction installed` lines and no `inactive` line.
   Then the acceptance tests in `docs/playtests/fleet-terrain-debrief-20261020.md`
   (a Tomahawk MST ridge crossing; a debrief on a 0.8.7 save that lost a
   ship), which were never run on 0.8.6 either.
10. **Only then** put the two corrections back into the Workshop change log
    and the Steam latest-update card.
