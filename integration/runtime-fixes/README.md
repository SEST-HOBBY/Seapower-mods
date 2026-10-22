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

Reference compiler: Ubuntu 24.04's `mono-mcs` 6.8.0.105+dfsg-3.6ubuntu2
(installed, or unpacked into a prefix named by `SEST_MONO_PREFIX`). Its
output is deterministic (no timestamp, content-derived MVID), so the
committed DLL rebuilds byte for byte from the sources; another Mono build
may compile them to different bytes.

## Re-gated to Sea Power 0.8.7 (23 Oct 2026)

Sea Power 0.8.7 Build 261021 (21 Oct 2026) shipped a new
`Seapower-Scripts.dll`, and the 22 Oct capture's `Player.log` read
`[SEST Runtime] inactive: uninspected native assembly
eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd`: the
plugin had failed closed as designed, and from 0.8.7's release on 21 Oct
(seen in the 22 Oct capture) both corrections were off for every player.
On 23 Oct 2026 the owner's export
(`SEST-map-review-complete-20261023-020525-bfb148.zip`, recorded in
`data/map-capture-review-20261023.json`) supplied that DLL, SHA-256
`eab2297b...`, the build the log named; it is not in the repository.

- **Verifier.** `verify_native_api.py` as it stood failed on 0.8.7 although
  the API had not changed: it compared raw signature blobs, which embed
  TypeDef row numbers, and 0.8.7 inserted three types (rows shift +1, +2,
  +3). It now compares decoded type names. Each of the twelve 0.8.6 blobs
  has the same element types in the same order as its 0.8.7 counterpart
  and differs only in TypeDef indexes, consistent with those inserted
  types; what each 0.8.6 row named could not be checked without the 0.8.6
  DLL. It also checks what the plugin binds but was never checked (step 3
  below as first written): `IniHandler`'s
  `doesSectionExist` and the one exact `readValue(string, string, bool,
  bool)` among its 30 overloads, `LinearCampaignMission._index`, the roster
  item's five string properties and `CrewSkill` (`ObjectBase+CrewSkill`,
  the row constructor's ninth parameter), `UnitRow.InstanceId`,
  `UnitRows`, the public row constructor, parameter order where neighbours
  share a type, inheritance, case-insensitive lookups, the native sampler's
  reach (1.08 nm, inside `Policy.LookAheadNm`) and the Harmony targets' IL
  bodies. Those additions were checked on 0.8.7 only: the 0.8.6 DLL was not
  to hand. On 0.8.7 every check passes.
- **Behaviour.** With no 0.8.6 DLL, step 5's IL diff could not be run; a
  review of the 0.8.7 IL replaced it. Terrain: `GetSafeAltitudeOverSurface`
  still samples 0.405 nm ahead for weapons and replaces the land clearance
  with `minAltOverSea`; the sampler reaches 1.08 nm; `WeaponBase` still
  calls it with `isWeapon` true in cruise; all ten stage names exist. The
  correction stands. Debrief: the native `ReadUnitRows` now has two paths.
  A Generated or Replaced mission (52 of the 69 in SEST's four campaigns)
  shows the rows saved at mission end from the post-mission snapshot, which
  drops every destroyed surface hull: the lost ships are still missing, so
  `TaskForceDebrief` stays on (option 1) rather than retiring. A mission
  played as authored (the other 17) lists its player units from the mission
  file and marks one Lost only from a `Mission_<i>_<tag>` `IsDestroyed`
  record, the record the plugin reads too. The game writes that record only
  for a unit with a `CampaignTag` (`SavePersistentDataFromMission` skips an
  empty `_campaignTag`), and no SEST mission file gives one to a player
  unit, so there a sunk ship is listed without a Lost status
  (`ReadDamageSummary` of a missing section gives `Undamaged`) and the
  plugin has nothing to add. Tagging the authored missions' player units
  would be the fix; that is separate work, not done here. The plugin skips
  an id the native rows already show, so it cannot list a ship twice.
- **Re-gate.** `SestRuntimeFixes.cs` accepts `eab2297b...` only (0.8.6 is
  no longer accepted: Steam has moved every player on). `sest_runtime.ini`
  and `SEST_RUNTIME_README.txt` say 0.8.7. The mocked tests now take the
  game's shapes (nested `FlightStage` and `CrewSkill`, a read-only snapshot,
  the competing `readValue` overloads) and pin the no-op over a loss the
  native rows already list: 38 assertions. The rebuilt DLL is `c844a759...`.
- **On the PC (23 Oct 2026):** step 9's `Player.log` check passed. After
  syncing 990dd7f9 (`IN LINE: all 4304 installed files`), the owner saw both
  `[SEST Runtime] ... correction installed` lines.
- **Still open:** step 9's acceptance tests. Neither correction has yet been
  watched working in a mission, on 0.8.6 or 0.8.7.

### After the next game update

1. **On the PC, game closed:**
   `powershell -ExecutionPolicy Bypass -File .\tools\export-map-diagnostics.ps1 -IncludeGameAssembly`.
   It writes `SEST-map-review-complete-<date>-<id>.zip` to Downloads with
   `game-reference/Seapower-Scripts.dll` and `file-manifest.csv`. Send the
   ZIP; do not commit the DLL. Record the ZIP's name, size and SHA-256 and
   the DLL's SHA-256 in a dated `data/*-review-*.json`, as
   `data/map-capture-review-20261023.json` does.
2. **Check it is the build the log named:** the DLL's SHA-256 must be the
   one `Player.log`'s `inactive: uninspected native assembly` line printed.
   Any other hash means the game moved again; capture again.
3. **Keep the verifier complete.** Every member the plugin binds must be in
   `verify_native_api.py`; a binding added to the plugin is added there in
   the same change.
4. **Verify:** `pip install dnfile dncil`, set `EXPECTED` in
   `verify_native_api.py` to the new hash and run it on the new DLL. Every
   check must pass; a changed signature means the binding code changes too.
5. **Compare behaviour, not only signatures.** Read the IL of
   `TerrainUtils.GetSafeAltitudeOverSurface`,
   `TerrainUtils.CrudeGetHighestTerrainHeightAhead`,
   `LinearCampaignTaskForceDebriefViewModel.ReadUnitRows` and
   `LinearCampaignTaskForceSaveManager.ReadSnapshot` (and, as on 23 Oct,
   what feeds them) against the assumptions above; diff them against the
   previous build when its DLL is to hand. If the native debrief lists lost
   hulls for Generated and Replaced missions too, retire `TaskForceDebrief`
   (set its option to 0 and say so).
6. **Re-gate the plugin:** `SestRuntimeFixes.cs` (`inspected` and its
   comment, one line each), the build named in the message at the end of
   `verify_native_api.py`, the first line of `sest_runtime.ini`, and
   `SEST_RUNTIME_README.txt`.
7. **Rebuild the DLL:** `python3 integration/runtime-fixes/build_plugin.py`
   (Mono). It runs the mocked regressions and rewrites the DLL and
   `plugin-build.json`; `test_runtime_plugin.py` fails until it has run.
8. **Rebuild the pack:** `python3 tools/build_all.py --from-scratch`
   (`write_runtime_fixes` copies the plugin into `SEST_Campaign/plugins` and
   the dist), then the twelve gates and both test suites.
9. **On the PC, after syncing:** `Player.log` must show both
   `[SEST Runtime] ... correction installed` lines and no `inactive` line.
   Then the acceptance tests in `docs/playtests/fleet-terrain-debrief-20261020.md`
   (a Tomahawk MST ridge crossing; a debrief of a Generated mission that
   lost a ship, and an older debrief reopened after a save and reload).
10. **The Workshop change log and the Steam latest-update card** may say
    the corrections are back on the new build once step 9's `Player.log`
    check passes, and that they have been seen working only after its
    acceptance tests.
