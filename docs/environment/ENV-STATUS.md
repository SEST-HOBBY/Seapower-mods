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
| ENV-07 | Ice shelves | BUILD-TESTED: Natural Earth 1:10m (public domain), 158 shelves with islands as holes; Ross on both sides of 180, Ronne, Filchner, Amery, Larsen checked; Berkner and Roosevelt islands correctly not shelf | `data/ice-shelves-naturalearth-10m.json` |
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

## Third pass: ice shelves

The hand-drawn outlines are replaced by Natural Earth's `ne_10m_antarctic_ice_shelves_polys`
(public domain; natural-earth-vector master, VERSION 5.2.0-pre; source SHA-256 `8f9bf623...`,
recorded in the data file). Converted unchanged except coordinates rounded to 0.001 degree.
It is a cartographic generalisation with fixed past fronts, not a dated survey: calving since
is not reflected. The loader now handles holes (islands and ice rises inside shelves). Lookup
cost: about 31 microseconds per point over all 158 shelves. The schematic file moved to
`tests/fixtures/` and is still refused as authoritative. 81 tests.

## Fourth pass: official data and seasonal ice

- **Real, time-accurate weather.** `mno_env/openmeteo.py` turns official model output, served
  as JSON by Open-Meteo, into validated snapshots: ECMWF **ERA5** reanalysis (recorded weather,
  1940 to about five days ago) with ERA5 ocean waves, or the ECMWF **IFS** 0.25 degree forecast with
  wave-model output. BUILD-TESTED with two real IFS responses saved as fixtures (Drake Passage,
  18 Nov 2026). The Weather Lab's `--mode real` (`-RealWeather` / `-Forecast` in the launcher)
  reads the mission's own map centre, date and start time and replays that place's weather hour
  by hour; the mission description carries the CC BY attribution. Local time to UTC uses
  round(longitude/15): an assumption, recorded in the receipt.
- Live ERA5 calls from this container hit Open-Meteo's daily limit (the container shares its
  address). One ERA5 call did answer and showed CAPE marked "undefined" for 1987; that case is
  now handled and tested. On the owner's PC the quota is the PC's own.
- **Seasonal sea ice.** `mno_env/seaice.py` sets the procedural ice edge so that hemisphere
  extent follows NSIDC Sea Ice Index (G02135 v4.0) monthly medians for the campaign date,
  interpolated daily: Arctic maximum March, minimum September; Antarctic the reverse. The
  table was computed from NSIDC's 24 monthly CSV files (fetched 18 Nov; SHA-256 per file in
  `data/seaice-climatology-nsidc-g02135.json`). Default baseline 2016-2025 (Arctic September
  4.64 million km2; 1981-2010 gives 6.50). An earlier hand transcription was off by up to 1.0
  million km2 and was replaced. The procedural snapshot reproduces the targets within about
  6 % on its 2 degree grid.
- Network: this session moved to the saved "Seapower-mods" cloud environment with
  `api.open-meteo.com`, `archive-api.open-meteo.com`, `marine-api.open-meteo.com` and
  `noaadata.apps.nsidc.org` added (owner-approved).
- 93 tests.

## Fifth pass: GCO long-run real weather (owner: opens 14 Sep 2028, 2025 weather)

- `data/gco-weather-2028.json`, `mno_env/gco_weather.py`, `tools/build_gco_weather.py`,
  `RUN-GCO-WEATHER.ps1`: campaign 14 Sep 2028 = ERA5 14 Sep 2025. Opening week: five 1-degree
  chokepoint tiles and a 4-degree grid over the GCO bounds (3-hourly). Season: 8-degree global
  grid, 6-hourly, 14-day chunks, a full year per source year; campaign year 2 replays 2024-25,
  year 3 2023-24, so the weather evolves for as long as the campaign runs. About 51,600
  location-calls per campaign year (planning rule, checked separately), so about six days of
  the free quota; resumable at task and request level.
- `mno_env/composite.py`: finest real layer that covers the point and time, else the next,
  else procedural generated on demand for any date; sea ice always from the NSIDC-calibrated
  field; every value labelled with its source layer.
- GCO start moved to 2028-09-14 (owner, 18 Nov): `build_dynamic_campaign.py` START and the
  world texts in `build_dynamic_campaign.py` / `modern_world.py`; rebuilt with the CI-pinned
  numpy 2.5.3 and global-land-mask 1.0.0; the diff in both campaign.json files (and their dist
  copies) is only `start` and the date in the texts; counts unchanged (196 bases, 293 forces,
  54 patrols, 1,642 buy entries); upload manifest refreshed (4,619 files, two hashes changed);
  `check_dynamic_campaign.py` PASS. The runtime's opening panel text
  (`integration/beta-feature-parity/runtime/WorldOpeningBriefing.cs`, SITUATION line) now says
  "14 September 2028" too (owner, same day). Source only: the R15 candidate DLL and its
  build receipt (which records the old source hash, `421c3752...`) are unchanged and remain
  the record of what R15 was built from; the text reaches the game with the next runtime
  build, which has to be compiled on the owner's toolchain (not possible in this container).
- Downloads not run here (shared address over the daily limit). 96 tests.

## Sixth pass: independent review of the real-data work (18 Nov)

A 53-agent review (facts checked against the providers' own documentation sources; each code
finding attacked by two skeptics) upheld 22 findings and rejected none. All are fixed:

- **Quota** (Open-Meteo terms): under 10,000 calls a day, 5,000 an hour and 600 a minute per
  address; a request costs locations x max(1, variables/10 x max(1, days/14)). The fetcher
  now paces by that cost, waits through minute and hour limits, and stops cleanly only at the
  daily limit. The first PC run had been sending 50-location requests every second.
- **Order of multi-location answers** is not documented: responses are matched to points by
  their returned coordinates (the saved real responses did come back in order).
- CAPE is not a documented ERA5 variable on Open-Meteo: optional, never required.
- Provenance: unique snapshot ids (region, resolution, span); forecast waves pinned to
  ECMWF WAM 0.25 deg (`models=ecmwf_wam025`) instead of an unnamed blend, credited only when
  fetched; forecast statements no longer say "recorded"; non-UTC starts converted.
- Forecast responses are never replayed from saved copies online; ERA5 hours not yet
  published (five-day lag) are refused instead of accepted as empty.
- Sea ice: ice-shelf cells (Natural Earth 1:10m, 1.3 million km2) excluded from the extent
  calibration, as NSIDC extent is sea ice only; the edge parameter is now exactly the 15 %
  line (it sat about 3.5 degrees off); unreachable targets are refused; the climatology tool
  requires every year 2016-2025 and records the years used per month.
- Weather Lab real mode: --hours-per-stage honoured; the description states the real step;
  forecast and explicit starts keep the mission clock; stage 0 is sampled at the start minute;
  a bad --mission-time is an argument error; the 5x5 grid stays inside +-90 and [-180, 180).
- PowerShell: -RealWeather/-Forecast no longer trip the -Mode check; -CollectLogs matches
  the receipt to the installed file's hash, lists that build's own stages, and finds the real
  Downloads folder; the shared Steam and Python lookups run with StrictMode off so their
  registry fallbacks work (no change to `tools/lib/common.ps1`).
- The 1,082 ERA5 request URLs are byte-identical to the version running on the owner's PC
  (compared), so its saved responses stay valid.
- Seams: the composite now feathers a chokepoint tile into the global grid over its outer
  1 degree, and the opening week into the season over its last 12 hours, so weather does not
  jump at a tile border or on day 8; contiguous season chunks hand over directly. Wave
  direction is never averaged.
- Second review (38 agents) of these fixes: all original findings confirmed fixed except the
  empty-data check (only partly), and 14 new items upheld; all fixed: responses with
  unpublished hours are never saved; an oversize request cannot crash the pacer; alignment
  trusts request order within one model cell, so the marine API snapping two coastal points to
  one sea cell no longer aborts; naive times are refused; whole-hour check after UTC
  conversion; ids distinguish waves/no waves and forecast retrievals; all-null and wave-tail
  gaps are clear errors; grounded-ice cells south of 79S that the coarse mask calls water are
  out of the sea-ice area; real-mode input errors are argument errors; the exact sample start
  is recorded and shown; RESULTS.txt numbers stages per mission (H-W1, B-W1) and keeps W9-W11;
  -Package marks a partial pack; -Status reports progress.
- 123 tests.

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
