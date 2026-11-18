# ENV-STATUS: environment track, 18 November 2026

SEST-DEV. Not released; nothing here is in any pack, Workshop item, R15 candidate or installer.

## Inspected

| Item | Value |
|---|---|
| Starting commit | `feature/r15-sea-power-093` `75b8a4268991849305f4938a04d95e6f606dc345` (17 Nov 21:28 UTC; remote re-checked, no newer commit). `dev`/`beta` at `a0721c18` were not used. |
| Working branch | `sest-dev/serene-bardeen-nvnmk9` (the session's assigned branch, reset to the R15 commit above before any change) |
| Input bundle | `MNO_GCO_Claude_Build_Bundle_20261118.zip`; its `SHA256SUMS.txt` matches the handoff (`8636613d...`) and the prototype ZIP (`d3775944...`) |
| Game files read | the repository's vanilla export, which is **Sea Power 0.9.2** (`fe52f5bc`, 14 Nov). No 0.9.3 file, no game, no DCM binary was available. |
| Hardware | 4-core Intel Xeon 2.1 GHz container, 16 GB RAM, Linux, Python 3.13.18. No GPU, no PowerShell, no .NET. |

## Labels

BUILD-TESTED = automated tests in this repository pass. IN-GAME TESTED = seen working in Sea
Power on the owner's PC. VISUAL DEMO ONLY = renders offline, not in the game. DESIGN ONLY =
specified, no code. BLOCKED = cannot proceed without the named input.

**Nothing in this track is IN-GAME TESTED.**

| Package | Piece | Status | Where |
|---|---|---|---|
| ENV-00 | Map render targets matrix | BLOCKED (no IL of 0.9.3 / DCM map code); matrix and adapter interface written | `docs/environment/ENV-00-map-targets.md` |
| ENV-00 | Diagnostic hook | BLOCKED (type names unknown; runtime cannot be built here) | ENV-00 doc, "What the owner can capture" |
| ENV-01 | Weather Lab generator (`mno_env/mission_ini.py`, `tools/build_weather_lab.py`) | BUILD-TESTED: 19 rule tests + all 632 mission INIs in the repository (627 patched and re-verified, 5 refused with a reason) | `integration/environment/` |
| ENV-01 | Windows launcher `RUN-WEATHER-LAB.ps1` (`-Quick`, build, -Install to `user_missions`, -Uninstall by receipt hash, -CollectLogs) | Written, NOT RUN (no PowerShell in the container); uses the repository's tested `tools/lib/common.ps1` helpers for finding the game and Python | `integration/environment/RUN-WEATHER-LAB.ps1` |
| ENV-01 | The mission in Sea Power | NOT TESTED: owner test card `ENV-PC-PLAYTEST.md` | |
| ENV-02 | Georeferencing maths (equirect, polar stereographic, EASE2) | BUILD-TESTED (PROJ 9.8.1 reference values, seam and pole tests) | `mno_env/overlay.py`, `mno_env/polar.py` |
| ENV-02 | Static georeferenced map proof | VISUAL DEMO ONLY (offline PNGs, procedural data) | `docs/environment/map-proof/` |
| ENV-02 | Overlay in the game, Layers control | BLOCKED by ENV-00 and by DCM on 0.9.3 | |
| ENV-03 | Time-indexed layers, double buffering | Reference maths BUILD-TESTED (layer built from immutable inputs into a new buffer; campaign-time sampling); game side DESIGN ONLY | `ENV-ARCHITECTURE.md` 5 |
| ENV-04 | Snapshot format `mno.environment.snapshot.v1`, validator, JSON schema | BUILD-TESTED (fixtures for corruption, units, labelling, lead time, gzip damage) | `mno_env/snapshot.py`, `schemas/` |
| ENV-04 | Local cache + offline fallback | BUILD-TESTED | `mno_env/cache.py` |
| ENV-04 | Transforms: accumulated precip, units, 0-360, row order, OSI SAF flags, polar regrid | BUILD-TESTED on arrays | `mno_env/ingest.py` |
| ENV-04 | ECMWF open-data and OSI SAF file converters | Written, NOT RUN (need optional cfgrib/netCDF4 and real files; no download made) | `tools/ingest_ecmwf_opendata.py`, `tools/ingest_osisaf_ice.py` |
| ENV-04 | Open-Meteo point sampler | Kept from the prototype, point samples only | `prototype-20261118/tools/import_openmeteo.py` |
| ENV-05 | Campaign-UTC clock, analogue offset (29 Feb rule), deterministic sampling | BUILD-TESTED (replay vs fast-forward digest equal; different seed differs) | `mno_env/clock.py` |
| ENV-05 | Per-save sidecar persistence | BUILD-TESTED offline (A/B no leakage, save-as, delete, corrupt kept + deterministic fallback) | `mno_env/persistence.py` |
| ENV-05 | Getting a save id from DCM | BLOCKED (DCM on 0.9.3; save API not inspected) | |
| ENV-05 | Forecast intelligence (observed / forecast / stale / estimated) | BUILD-TESTED (deterministic per side; recon narrows error, never changes truth) | `mno_env/forecast.py` |
| ENV-06 | Sample -> native `[Environment]` + timed triggers | BUILD-TESTED (WMO sea-state bands, oktas, no rain-only thunderstorms, no fog without visibility, never `Action_SetSnow`) | `mno_env/mission_adapter.py` |
| ENV-06 | Postfix on DCM `MissionWriter.Text` | DESIGN ONLY / BLOCKED (DCM on 0.9.3) | ENV-00 matrix |
| ENV-07 | Sea ice access rules by verified capability (none by default) | BUILD-TESTED; capability table deliberately empty | `mno_env/ice.py`, `data/ice-capability.json` |
| ENV-07 | Ice shelves | BUILD-TESTED code; geometry SCHEMATIC, refused as authoritative | `data/ice-shelf-fronts-SCHEMATIC.json` |
| ENV-07 | Icebergs (drift, uncertainty, lifetime, hazard reports) | BUILD-TESTED with fixtures; no real iceberg data | `mno_env/ice.py` |
| ENV-08 | Route evaluation (land, shelf, ice, sea state, bounded fuel) | BUILD-TESTED; not wired into GCO | `mno_env/routes.py` |
| ENV-08 | Authored Southern Ocean / monsoon operations | DESIGN ONLY (not started; needs BA-09 regions and PC-05) | `ENV-NEXT-WORK.md` |
| ENV-09 | Packaging into MNO | Not done by design: nothing is packaged until gates pass | |

## Feature flag

There is no game-side code, so nothing can switch on. The flag name is reserved as
`MNO_ENVIRONMENT_ENABLED` (`mno_env/__init__.py`) and will be an ini switch, default off, when the
runtime part exists (`ENV-ARCHITECTURE.md` 3).

## Hashes

| File | SHA-256 |
|---|---|
| Source `Hormuz.ini` (0.9.2 export) | `65474db0cba0d524...` |
| Weather Lab, Hormuz, front, time kept | `fd19df3c657863f1...` |
| Weather Lab, Hormuz, front, time 10,0 | `89738dfba9638982...` |
| Source `Breakthrough.ini` (0.9.2 export) | `31c82d1a4a28b2a9...` |
| Weather Lab, Breakthrough, front, time kept | `4fca0934d5cba67e...` |
| Weather Lab, Breakthrough, front, time 10,0 | `c84f4f0921459151...` |

The owner's 0.9.3 files may differ from the 0.9.2 export; the builder records the real source
and output hashes in `PLAYTEST_META.json` on the PC.

## Second pass, 18 November

- Install target changed from `StreamingAssets\content\MNO-Environmental-Playtest` (the
  handoff's suggestion; no repository tool has ever installed there) to the one mission file in
  `StreamingAssets\user\missions\user_missions\`, the folder the game lists player missions
  from (`tools/install-sest-packs.ps1:142-160` records that missions copied there showed up in
  the game's list). One file to add and remove, no Mod Manager step.
- `-Quick`: build and install in one command, stages 60 s apart, 10:00 start; whole test about
  10 minutes. `-CollectLogs` zips the logs and receipt for the reply.
- Game folder and Python are found with `Find-StreamingAssets` / `Get-Python` from
  `tools/lib/common.ps1` instead of a hard-coded Steam path.
- Procedural mode no longer samples a storm centre (eight identical stages); it searches ahead
  of each storm track for the point where the weather changes most (deterministic per seed).
- 80 tests.

## Corrections to earlier statements

- The prototype's `patch_vanilla_mission.py` handles the two vanilla missions correctly (its
  output disables Hormuz 7-10 and Breakthrough 7-15, as the new builder does). An early note in
  this session that Hormuz's weather triggers were referenced elsewhere was wrong: those lines
  were in Breakthrough and only re-enable triggers 1, 3, 4 and 5. The prototype's real gaps are
  in other inputs: a weather trigger that another trigger can re-enable is left live without a
  warning; triggers that mix weather with other actions keep their weather; CRLF files are
  rewritten as LF; an existing `Disabled=False` gets a second `Disabled` line; only the English
  name is changed. Each is a test in `tests/test_mission_ini.py`.
- `Action_SetSnow`, listed in the handoff as a native field, appears in no shipped mission
  (the 0.9.2 export and every Workshop mod mission in the repository). It is not written.
  `Action_SetFog`, `Action_SetThunderstorm` and `Action_SetWindDirection` do appear in vanilla
  campaign missions.
