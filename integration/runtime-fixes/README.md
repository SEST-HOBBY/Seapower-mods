# SEST Runtime Fixes - developer notes

SEST's own Anchor Chain plugin (`SEST.RuntimeFixes.dll`): the Tomahawk MST
terrain clearance (`TerrainClearance.cs`), the task-force debrief's lost
hulls (`TaskForceDebrief.cs`) and the campaign combat cost rows
(`CampaignCosts.cs`). What it does for a player is in
`SEST_RUNTIME_README.txt`, which the campaign builder
(`build_pack.write_runtime_fixes`) copies into the pack's `plugins/` with
`sest_runtime.ini` and the DLL. The plugin installs nothing unless the game's
`Seapower-Scripts.dll` hashes to the one inspected build
(`SestRuntimeFixes.cs`, `inspected`), and `verify_native_api.py` checks a
player-exported copy of that DLL against the signatures the plugin binds.

    python3 integration/runtime-fixes/build_plugin.py   # needs mono-mcs or SEST_MONO_PREFIX
    python3 integration/runtime-fixes/verify_native_api.py <Seapower-Scripts.dll>   # needs dnfile, dncil

`plugin-build.json` records the hash of every source, the stub, the builder,
the tests and the two price-rule tables in `tests/`;
`tools/tests/test_runtime_plugin.py` fails if any of them is edited without
running `build_plugin.py`, or if the DLL in the dist differs (until
`tools/build_all.py` copies the rebuilt DLL there). The validation line in
`plugin-build.json` takes its assertion count from the test run.
`SEST_RUNTIME_README.txt` and `sest_runtime.ini` are not inputs: they can be
edited and rebuilt into the pack without Mono.

Reference compiler: Ubuntu 24.04's `mono-mcs` 6.8.0.105+dfsg-3.6ubuntu2
(installed, or unpacked into a prefix named by `SEST_MONO_PREFIX`). Its
output is deterministic (no timestamp, content-derived MVID), so the
committed DLL rebuilds byte for byte from the sources; another Mono build
may compile them to different bytes.

## Campaign combat costs (24 Oct 2026)

Phase 1 of `docs/combat-costs/campaign-costs-design.md` (the owner's
"cumulative combat costs"; the Situation-window block is phase 2 and not
built). `CampaignCosts.cs`, option `CampaignCombatCosts=1`, Harmony id
`io.github.sest-hobby.campaign-combat-costs`.

- **When.** A postfix on `LinearCampaignTaskForceDebriefViewModel.Load`
  (assembly, instance), which clears and refills the Mission Summary every
  time a debrief opens, after a mission or reopened from the map.
- **What it reads.** The game's own `[Mission_<i>_TaskForceDebrief]`
  sections in `LinearCampaignTaskForceModeRules.OpenCampaignStateIni()`,
  through the game's own readers: `HasDebriefSnapshot`,
  `GetDebriefSectionName`, `TryParseRegisterRows` for `KillRows` (enemy
  losses) and `LossRows` (player losses), and `TryReadWeaponReports` plus
  `TaskforceWeaponReport.BuildTaskforceTotals()` for `PlayerWeaponReport` and
  `EnemyWeaponReport`. Each completed mission with a snapshot is counted
  once; the game writes none for failed attempts and keeps the first for a
  replay. It never writes: no `writeValue`, `saveFile` or change to a
  dictionary returned by `get_Data`; the mocked tests compare the state's
  data before and after.
- **What it counts.** Weapons: `Launched + ProjectileFired` per `AmmoRef`
  (the tracker's `_number`; CIWS bursts are already in `ProjectileFired`).
  Losses: destroyed rows only (kill rows include damaged units), price x
  `Count`; `Vessel`/`Submarine` from `vesselcosts`, `Aircraft`/`Helicopter`
  from `aircraftcosts`, so air-group rows (aircraft aboard a lost ship or on
  deck) count. Land and other rows are not priced; the log counts them.
  Neutral is omitted.
- **Prices (`CostPolicy`).** CombatCosts 0.7.1's rules, read from the IL of
  `CombatCosts.dll` 74afa902...: catalogs opened with
  `Utils.openVirtualIniFile(<folder>, <name>, <name>, false)` (every enabled
  mod's `#!extend`, SEST_Combat_Costs included) and read through `get_Data`;
  unit files with `Utils.openIniFile(<root>, "/<ref>.ini", false, true)`
  (`/ammunition`, the row's folder or `/vessels`, and `/aircraft` for both
  aircraft kinds); `SharedSettings.Apply` (config.ini's `UseCurrentYearCosts`
  and `CurrentYear` replace the weapon catalog's); `ResolveField` (missing
  falls back, blank wins and stays unknown; list-wide, entry and per-field
  `Override*`); `ParsePrice` (ASCII digits and one point, 0 to 1e15);
  `CurrentYearCost` never falls back to the historical price. A weapon whose
  category is invalid or `Ignore`, or which has no category and a type
  outside Missile and the fallback table, is excluded exactly as the tracker
  excludes it (no "+ ?"). `integration/common/costs.py` mirrors the same
  rules; `tests/cost_precedence.tsv` and `tests/cost_exclusion.tsv` are read
  by both `tests/RuntimeTests.cs` and `tools/tests/test_combat_costs.py`.
- **Rows.** Appended after the native four, neutral styling: Weapons,
  Losses, Mission (this mission), Campaign (every completed mission, with
  the count), Basis (`USD, IOC prices` or `USD, <CurrentYear> prices`), and
  Unpriced only when a `+ ?` is shown. An unknown price is never $0. An
  absent or unreadable weapon report reads `not recorded` (with `+ ?`); a
  blank one, which the game writes for "fired nothing", reads `$0`. Format:
  invariant, 3 significant digits, half away from zero, K/M/B/T.
- **No rows** (logged once a session) when there is no state INI, no
  snapshot for the mission, or the tracker's three catalogs lack `[Costs]`
  (the tracker is not enabled; SEST's extend files have none). A unit file
  that cannot be read counts as unpriced and is logged once. Any other
  exception: nothing is added, the native rows stay, and the module turns
  itself off for the session (`campaign combat costs disabled for this
  session: ...`).
- **Log.** `campaign combat costs installed: ...` at startup; at the first
  debrief `combat costs: tracker price lists found; CombatCosts.dll <sha12>
  (rules mirrored from 0.7.1 74afa902...)` (another tracker build is noted,
  not gated); at each debrief one `combat costs mission <i> (<basis>): ...`
  line with raw decimals; and the first time an item is unpriced in a
  session `combat costs: no <basis> price for weapon <ref>, vessel <ref>,
  ...` (at most 20 names), which feeds the cost-list research.
- **Checked.** `verify_native_api.py` on 0.8.7: every bound member with its
  signature and parameter order, the second `readValue` overload, the
  snapshot row's fields, the enum names, and the bodies it relies on
  (`INSPECTED`). Mocked tests: 163 assertions in all, including both shared
  tables. The rebuilt DLL is `76f2862c...`; until `tools/build_all.py` copies
  it into the dist, `test_runtime_plugin.py` reports the dist copy as
  different. Nothing has been seen in game yet.
- **Open: the PC acceptance checks** (design section 11, A1-A13): startup
  line; a first mission compared with the F11 panel (weapons equal, losses
  cover hulls, the helicopter aboard and the aircraft in flight); the log
  line; a second mission's campaign sum and `(2 missions)`; an older debrief
  reopened; save, quit and continue; a failed attempt and a replay; a new
  campaign; current-year mode (owner only, reverted); the option off; the
  tracker disabled; an unpriced weapon and a side that fired nothing. Say
  "seen working" only after A2-A9 pass.

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
  `[SEST Runtime] ... correction installed` lines. The 23 Oct capture
  (87c0feb5, taken with 28f62cd3 installed) shows them too, in
  `data/install-snapshot/player.log`, with no `inactive` line; the installed
  `SEST.RuntimeFixes.dll` is `c844a759...`, the dist's.
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
   (set its option to 0 and say so). For the campaign costs, also read
   `SaveDebriefSnapshot` (completed missions only, no replays; which
   registers feed `KillRows` and `LossRows`), `WriteWeaponReport` (blank for
   "fired nothing"), `TryReadWeaponReports` and `ReadWeaponReport`,
   `ReadRegisterRows`, `BuildTaskforceTotals` and `RecordCiwsRoundsFired`
   (CIWS bursts inside `ProjectileFired`).
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
   `[SEST Runtime] ... correction installed` lines, the `campaign combat
   costs installed` line and no `inactive` line.
   Then the acceptance tests in `docs/playtests/fleet-terrain-debrief-20261020.md`
   (a Tomahawk MST ridge crossing; a debrief of a Generated mission that
   lost a ship, and an older debrief reopened after a save and reload).
10. **The Workshop change log and the Steam latest-update card** may say
    the corrections are back on the new build once step 9's `Player.log`
    check passes, and that they have been seen working only after its
    acceptance tests.

### After a Combat Cost Tracker update

The campaign costs never call the tracker, but they copy its price rules.
When `CombatCosts.dll` changes (the first debrief's log line names a hash
other than 74afa902...), re-read in its IL `Price::.ctor`,
`CostRules.Resolve`, `ResolveField`, `Preference`, `Value`, `ParsePrice` and
`ValidCategory`, `VesselRules.Resolve` and `AircraftRules.Resolve`,
`SharedSettings.Apply`, `Overlay.LoadConfig`, `GetPrice`, `GetVesselPrice`
and `GetAircraftPrice`, and the catalog paths and arguments, against 0.7.1.
Change `CostPolicy`, `integration/common/costs.py` and the two tables in
`tests/` together, then rebuild.
