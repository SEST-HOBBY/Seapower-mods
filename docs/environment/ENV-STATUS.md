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

## Seventh pass: procedural model v3 and the weather chart (18 Nov)

- `mno_env/procedural.py` is now `mno.env.procedural.3`: seasonal pressure climatology
  (subtropical highs, subpolar lows, ITCZ, monsoon, Aleutian/Icelandic lows, the southern
  highs); extratropical cyclones and basin/season tropical cyclones that are born, move and die
  in 6-hour slots (so the fallback evolves for any campaign length); 10 m wind derived from the
  pressure field (geostrophic, 70 %, turned 20 degrees to low pressure; trades near the
  equator); wind sea plus storm swell; cloud and rain from ITCZ, fronts, storm cores and
  stratocumulus decks. Zonal means checked in September and January (westerlies, trades,
  Southern Ocean trough, seasonal wave climate). Tests: circulation sense around every live
  low, wind belts, tropical cyclones out of season absent, storms forming and dying over 60
  days, overlapping windows joining exactly.
- `tools/build_weather_viewer.py` + `tools/weather_viewer_template.html`: a self-contained
  map and globe chart of the first ten days from 14 Sep 2028 (VISUAL DEMO ONLY), published as
  a private artifact for the owner.
- 128 tests.

## Eighth pass: model v4 from an independent critique (18 Nov)

A four-lens critique of v3 (climatology, physics, 120-day behaviour, engineering; each issue
re-measured by two skeptics) raised 36 issues; every verdict returned so far upheld its issue.
v4 (`mno.env.procedural.4`) answers them: storms combine as a quadratic sum instead of stacking;
the climatological Aleutian/Icelandic lows and Southern Ocean trough keep only part of their
depth because passing storms supply the rest; lows drift poleward through life and die at
55-68 degrees; global mean pressure is conserved; rain rescaled (global mean 0.14 mm/h);
cloud rescaled (mean 60-62 %, clear skies possible); travelling waves give tropical and
synoptic variability; 10 m wind softly capped; waves with coastal shelter, no fixed swell floor,
Hs hard cap 13 m; tropical cyclones weaken over land and recurve more readily; season is
continuous across 1 January and the ocean-coupled features lag six weeks; Siberian high added;
air temperature gets warm and cold sectors; the Arctic ice edge keeps Norway/Barents open
and reaches Okhotsk, Bering, Labrador and East Greenland; pole rows single-valued;
great-circle storm distances. Measured 14 Sep 2028 / 15 Jan 2029 over open ocean: wind median
6.6/5.5 m/s, 99th percentile 17 m/s; Hs median 1.9/2.0 m, 99th percentile 7.0/6.5 m;
Southern Ocean westerlies 8.8 m/s and Hs 5.2 m in its winter, 5.7 m/s and 3.8 m in summer.
The Weather Lab's procedural mode now samples the mission's own map centre (`--storm-chaser`
keeps the old search). 128 tests.

## Ninth pass: model v5 from a second critique (18 Nov)

The same four-lens critique, run fresh against v4 (82 agents), upheld 38 issues. The two
largest were storm-track rain 3-5x too high while the tropics were too dry, and storm tracks
and the Southern Ocean westerlies sitting about 10 degrees too far equatorward. v5
(`mno.env.procedural.5`) answers them, tuned against a scripted harness that measures each
issue's own metric (2-3 seeds x 8 months x 8 frames, 4-degree grid, ocean only). Results below
are model / reference (GPCP, ERA5, ISCCP, NSIDC as cited by the critique).

Rain:
- Storm rain is combined in quadrature, with narrow fronts and a dry threshold.
- 46-50N in January: 5.2-6.2 / about 5-6 mm/d.
- Wet fraction at 44-56N in January: 0.39 / 0.2-0.4.
- ITCZ about 10 mm/d.
- Added an SPCZ, warm-pool and monsoon rain, and trade-wind showers. Warm pool 8.3 / 8-10 mm/d;
  Bay of Bengal in July 14.8 / 10-15 mm/d.

Storm tracks:
- Lows are born further poleward and are larger, live longer, deepen over 1-2 days, and have a
  travelling ridge with clearing behind each.
- Peak depth: median 51.6N and 57.5S. They die at 57N and 62S.
- The Icelandic low is at 63N 30W.
- January sea-level pressure at 50N: 1004 / 1004-1008 hPa.

Winds:
- Southern Ocean scalar wind in January / July: 10.9 / 11.9 m/s (reference 9-11 / 11-12).
- The Arabian Sea in July is south-westerly at 8.3 m/s with Hs 2.9 m (reference about 10 m/s
  and 3-4 m). Bay of Bengal, South China Sea and northern Australian monsoons added.
- Warm-pool winds weak.
- Cross-isobar turning 11 degrees.
- Gustiness added: calm fraction at 30S is 0.10-0.12, against 0.38-0.41 before.

Tropical cyclones:
- Land decay is cumulative and irreversible (e-folding 0.6 day over land).
- No genesis over land.
- North Indian storms head north-west.
- Re-emergence at 80 % of strength or more after crossing land: 0-11 % by basin (WPAC
  highest), against 26-92 % before. No North Indian storm reaches the Gulf.

Waves, temperature and cloud:
- Waves are zero under pack ice.
- Temperature follows the lagged season and warm currents, with a melting-ice surface and open
  water that cannot be colder than -6 C:
  - Arctic in August: 0 C;
  - North Pole in February: -30 C;
  - Hormuz in September / January: 32 / 23 C.
- Cloud saturates softly: ocean mean 70 % (reference 68-70 %), subtropics 55-63 %.

Sea ice:
- Extent is calibrated for the grid the game samples. On the 4- and 2.5-degree grids it is within
  0.02 million km2 of NSIDC.
- Regional placement corrected:
  - in March, Hudson Bay, Okhotsk, the Baltic and the Gulf of St Lawrence freeze, and the
    Irminger Sea stays open;
  - in February the Ross Sea opens while the western Weddell and Amundsen pack survives;
  - in September the central Arctic keeps its pack.

Engineering:
- The noise is blended across latitudes (no seam at 25 degrees). Its amplitudes and phases are
  re-drawn every 72 h, so it is not periodic.
- Pole rows are single-valued with calm wind, and there is no ice on land nodes.
- Snapshot IDs carry the version and the step.
- A warm 72 h, 4-degree window takes 3.1 s.

Weather Lab:
- The storm chaser never picks a land point.
- Its variety score counts cloud, sea state, rain, thunderstorm and fog changes; wind
  direction only breaks ties.

Weather chart:
- One label per high.
- Explicit UTF-8.
- Republished as version 3 of the same private artifact.

Not done:
- `created_utc` default; the critique's verifiers rejected that issue.
- Midlatitude SLP autocorrelation, apart from what the larger, longer-lived lows give.
- Remaining biases:
  - global ocean wind 6.9 / 7.3-7.5 m/s;
  - NH winter storm-track wind 9.5 / 10-11 m/s;
  - SPCZ in July 2.6 / 4-5 mm/d;
  - northern Okhotsk ice lingers into early July.

137 tests.

## Tenth pass: fog, polar routes, sea-ice fixes (18-19 Nov)

Fog. The procedural model now writes `visibility_km` (mno_env/visibility.py), so procedural weather can set the
game's Fog flag (visibility below 1 km). Visibility is the lowest of:
- sea fog from a climatological frequency table (Grand Banks, Kurils, Aleutians, Yellow Sea, Taiwan Strait,
  California, Peru, Namib, North Sea, Baltic, Barents, Iceland, Gulf in winter), after Dorman et al. ship fog;
- rain and snow;
- dust haze (Gulf, Hormuz, Red Sea, harmattan, khamsin, Asian dust), never below 1.2 km;
- Arctic sea smoke.

Fog needs light to moderate wind and no rain, is favoured by warm air moving over cold water, and comes and goes
as patches of slowly moving noise. Calibrated on mean probability at 18 naval reference points: 16-17 in range
(Southern Ocean ice edge slightly low).

Polar routes chart (tools/build_polar_routes.py, build_polar_viewer.py, data/polar-routes.json):
- Northern Sea Route (coastal and high latitude), Northwest Passage (southern and Parry Channel), Transpolar;
  McMurdo, Davis and Rothera resupply.
- Paths are joined at sea on the game's coarse land mask, outside the ice shelves.
- The chart shows weekly sea ice for a campaign year and each route's access for four ship ice classes
  (transit by routes.evaluate), with a navigation-season calendar.
- Unclassed ship, weeks passable: Northern Sea Route coastal 13, Northwest Passage southern 10,
  Parry Channel 4, high-latitude, Transpolar and McMurdo 0.
- Limits: Davis and Rothera stay open too long, as there is no coastal fast ice; no unit in the collection has
  a verified ice class.

Sea-ice fixes. The v5 regional winter terms depended on longitude only and spilled ice into the Arctic seas on
the same meridians (Okhotsk into the Laptev and East Siberian Seas, St Lawrence into Baffin Bay, Baltic into the
Barents, Bering into the Chukchi), so no Arctic route ever opened. Each term is now limited to its own latitude
band. Added the Canadian Archipelago/Beaufort old ice, the Gulf of Finland, the White Sea and Bohai/Liaodong.
The extent bisection takes the closer side of the jumps a coarse grid makes. Extent is within 0.08 million km2
of NSIDC on 4- and 2.5-degree grids.

## Eleventh pass: model v6, land and coast (19 Nov)

A five-lens review of land and coastal weather found 56 issues; 54 were confirmed by both skeptics. Its
13-step plan was prioritised by what reaches the player. In the GCO campaign the ERA5 season layer replaces
procedural after week 1, except for sea ice, visibility, waves at all-land-corner chokepoints and north of 80 N.
v6 (`mno.env.procedural.6`, new mno_env/landphys.py) does the following; values are model / reference, sampled
the way the game samples, 2.5-degree grid.

Sea-surface fields:
- Waves and sea ice on land nodes now carry the mean of the neighbouring sea nodes.
- Ships near coasts and in straits no longer see land-damped waves or ice-free coasts.
- An all-land-corner strait no longer falls back to the default SeaState 4.
- The NSIDC extent calibration mirrors this fill exactly. Pole rows are never filled.

Fog rules:
- Fog = visibility below 1 km with precipitation below 0.5 mm/h and wind below 13 m/s, judged on the final
  (possibly mixed-source) values. Rain, snow and dust never set Fog.
- Visibility is interpolated as extinction (1/km) in space and time, so a fog node is not averaged away.
- Mission plans change Fog only when the new value holds for two samples.

Snow:
- New snowfall field.
- Precipitation is snow when snowfall is at least half of it; later triggers no longer write Rain while it snows.

Land temperature:
- Continentality (upwind distance over land) on a land phase.
- Moscow -7.5 / 17.6 C (ref -7 / 19); Yakutsk -36 / 18.5 (-39 / 19); Riyadh 14.6 / 39 (14 / 36);
  Kuwait 16 / 36.5 (13 / 38).

Deserts and the Horn of Africa:
- Deserts, the Red Sea and the Gulf have no background rain; desert skies are mostly clear.
- Bab el-Mandeb and the Gulf of Aden have no Rain-flag hours in Jul-Sep (v5 rained 95-100 % of hours).

Regional winds where the grid cannot resolve the sea:
- Taiwan Strait Oct-Jan from 38-40 deg at 9-10 m/s (ref 20-50 deg, 8-11).
- Gulf shamal Jul from 335 deg at 5.8 (300-340, 5-7).
- Hormuz Sep-Nov NW.
- Red Sea north NNW 5 m/s.
- Red Sea south from 148 deg at 6.6 in Jan and from 332 in Jul.
- Aegean etesians Jul-Aug from the north at 6.7-8.7 m/s (340-30, 6-8).

Other:
- Land roughness: Amazon 2.9 m/s.
- The ocean climatology harness is unchanged from v5 within noise (baseline frozen before the change).
- The weather chart gains a "Visibility and fog" layer and a visibility readout.

Deferred to later passes: the diurnal cycle and sea breezes, gap and fall winds, mountain rain and rain shadows,
the downloaded climatology/elevation bundle (needs the owner's PC), sample-time channel corrections, visibility
for the real ERA5 layers (needs a humidity request), southern land monsoons, Meiyu. 151 tests.

## Twelfth pass: sensor environment S1 (19 Nov)

A five-lens review covered underwater acoustics, radar, EO/IR, game integration and a gameplay skeptic. It made 51
proposals, and 44 were kept after two checks each.

What the game files allow:
- Sonar is driven by a global environment.ini [Sonar] section: passive ambient 60 dB, +5 dB per SeaState step, +15 dB
  in rain, convergence zones at 30/60 nm in water deeper than 3000 ft. The game computes its own layer, surface duct and
  floe ice.
- Radar, IR and visual weather effects live in game code, reached only through the mission weather keys.
- A per-mission [Sonar] override through 0.9.x file layers is possible on paper but untested.

Built (S1):
- mno_env/sensors.py derives a sensor environment from a weather sample:
  - mixed layer and layer class, duct cutoff, convergence zones per theatre, suggested ambient and rain noise;
  - evaporation duct, ITU-R P.838-3 rain loss, NRL clutter, multipath;
  - IR range factor, moon and sun, cloud base.
  Each value is tagged GAME / REAL-WORLD / UNTESTED with source and confidence, and checked against the review's
  reference values. Example: NRL X-band SS3 at 1 deg gives -43.3 dB against a reference of -43.7.
- mno_env/sensor_brief.py and tools/build_sensor_brief.py build the "GCO Sensor Weather" page for the five theatres.
- Weather=Rain now switches on at 0.5 mm/h and off below 0.3 mm/h (hysteresis), so drizzle does not toggle the game's
  flat +15 dB rain noise.
- docs/environment/SENSOR-PC-TESTS.md holds the owner's PC test rows.

Not built: the file-layer probe tool and the [Sonar] writer, which wait on the PC tests. Also not built: the
ERA5/WOA23-derived theatre tables, ERA5 dewpoint/SST in real snapshots, and the forecast text. 155 tests.

## Thirteenth pass: more chokepoints, wider weather bounds; ice shelves in game (19 Nov)

Chokepoints. data/gco-weather-2028.json grows from 5 to 24 theatres:
- registry gates: Suez and the northern Red Sea, Mozambique Channel, Sunda, Lombok-Makassar;
- Pacific: Taiwan, Luzon, Miyako, Korea Strait;
- Europe and North Atlantic: Gibraltar, the Turkish straits, the Danish straits, the English Channel, GIUK;
- Arctic: Bering, Kola-Barents;
- others: Panama, Bass Strait, Torres Strait, Ombai-Wetar.

Each gets a 1-degree opening tile. A new 2-degree "chokepoint" layer follows every theatre for the whole campaign year
in 14-day chunks: before this, straits fell back to the 8-degree season after week 1.

Bounds. Polar bands 80-88 N and 64-80 S are added at the season resolution, so the Arctic routes and the Ross Sea get
real weather.

Composite priority: tile, chokepoint, opening, season, polar, procedural.

Cost. Existing task ids are unchanged, so cached downloads stay valid; the global season still comes before the new
layers. The year-1 plan goes from 32 snapshots (about 51,600 location-calls) to 727 snapshots (about 99,000), about
11 days of the free quota instead of 6. Setting "chokepoint_season": {"enabled": false} drops back to about 7.
sensors.THEATRES has a row for every theatre.

Campaign bounds. integration/world-sandbox/build_dynamic_campaign.py BOUNDS (62 S - 74 N, -100 to 258) is
deliberately unchanged:
- the adapter marks this extent untested;
- the handoff gates anything south of 62 S on PC-05, a polar probe with latMin -78 and a port at McMurdo
  (WORK-PACKAGES-20261118.md);
- a northern extension needs the same kind of probe.

Ice shelves in game. The game has no sea-ice, iceberg or ice-shelf objects. Its only ice term is a game-computed
"Floe Ice" in the sonar model. The bundled Natural Earth shelves (159 polygons) are used by MNO only:
- routes.evaluate blocks a route that crosses a shelf;
- sea-ice extent leaves shelf area out;
- the polar chart draws them;
- ships get no sea values there.

In play they can only appear through:
- the game's own terrain (unknown south of 62 S: PC-05 checks it);
- MNO placement and routing rules;
- briefings and charts.

156 tests.

## Fourteenth pass: model v7 land rain and the chart over land (19 Nov)

v7 (`mno.env.procedural.7`) changes land rain, measured against the land review's GPCP-style targets on a
2.5-degree grid. Values are mm/day, v6 to v7 / reference.

Over land:
- Land 60 S-60 N: 1.48 to 1.86 / 2.0-2.4.
- Eastern US: 0.18 to 2.3 / 2.8-3.5.
- US Gulf coast in July: 0.0 to 4.1 / 2.5-5.
- South-east China in June: 0.9 to 3.8 / 6-9.
- Southern Africa: January 0.4 to 5.4 / 3.5-6; July 0.6 to 0.05 / 0.4 or less.
- Brazil in January: 0.6 to 7.3 / 6-9.
- Amazon in March: 2.3 to 6.3 / 6-10.
- Northern Australia in January: 2.4 to 4.6 / 5-8.
- Europe: 3.2 to 2.8 / 1.6-2.5.
- Siberia and Canada in July: 0.8-0.9 to 2.2-2.3 / 1.5-3.
- The Sahara stays dry.

Globally:
- Global ocean 2.97 mm/day (reference 2.9-3.0).
- Other ocean statistics unchanged from v6 within noise.

How:
- A third storm slot for continental lows: Colorado/Alberta lee, Gulf coast and Genoa in winter, East Asia;
  Patagonia, the Cape and southern Australia in the south. The ocean storms are untouched.
- Summer showers and thunderstorms over humid land.
- The rain belt swings south over Africa, South America and Australia in southern summer and is broader there.
- Dry seasons suppress rain over tropical land away from the belt.
- Added: the Meiyu/Baiu front, Gulf of Mexico moisture, Cape and south-west Australia winter rain, the South Atlantic
  convergence zone, south China, central India, Thar, Sumatra squalls, the Malacca inter-monsoon and the Ethiopian
  kiremt.
- Storm rain is 40 % lighter over land.
- Convective rain comes in wet and dry spells: a lognormal multiplier normalised to a mean of 1 by latitude, on
  scales of hundreds to thousands of km, lasting days. Individual storm cells are below the grid and are not
  represented.

Still off:
- Mountain rain: Norway 3.3 / 4-7. It needs elevation data.
- South-east China in June is about 35 % low.
- Ethiopia is high in some samples.

Chart:
- Wind, rain and snow, air temperature (new layer) and visibility now shade over land as well as sea. Only waves and
  sea ice stay sea-only. Before, only waves, wind and fog had shading, all over sea only, and rain over land was
  half-strength.
- Rain uses stepped radar-style bands with snow in violet, from the new snowfall field.
- The point reading adds air temperature and precipitation type.

156 tests.

## Fifteenth pass: pressure chart and a fuller sensor brief (19 Nov)

Pressure (model): the continents carried the ocean's pressure pattern. There was a summer high over China and no heat
lows. background_pressure now has continental systems on the land's own phase:
- northern summer heat lows: Sahara, Arabia-Gulf, Pakistan-Thar, the US south-west, Mongolia-East Asia, Iberia;
- southern summer heat lows: Australia, the Chaco, Kalahari-Angola;
- winter highs: a stronger Siberian-Mongolian high, a Canadian high, and Australian, southern African and South
  American highs.

Model / reference, January and July:

| Centre | January (hPa) | July (hPa) |
|---|---|---|
| Mongolia | 1032 / ~1035 | 1009 / ~1006 |
| Persian Gulf | 1018 / ~1019 | 1005 / ~999 |
| Pakistan | 1017 / ~1019 | 1003 / ~998 |
| Australia | 1008 / ~1006 | 1019 / ~1020 |
| Chaco | 1008 / ~1006 | 1020 / ~1018 |

The heat lows also improve the Gulf shamal (July from 319 deg at 6.9 m/s) and Hormuz in autumn (W/NW). The ocean
climatology is unchanged within noise.

Pressure (chart):
- Isobars were hidden over all land poleward of 60 deg. They are now hidden only over the Greenland and Antarctic ice
  sheets.
- Isobars come from the nearest stored frame instead of a blend of two, which drew a moving low twice.
- Levels run 900-1060 hPa.
- Saddle cells are resolved by the cell centre.
- Lines carry labels in chart convention (08 for 1008).
- Highs and lows are marked at the analysed pressure centres with their central pressure (2 hPa prominence, 4 in the
  tropical trough). Storms show as a centre dot and track while isobars are on.

Sensor brief: grouped into Sonar, Radar, EO/IR, Air ops and Sonar override, with more items.
- Real world:
  - Sonar: Francois-Garrison absorption, sea-ice noise (pack quiet, marginal ice zone loud), snapping shrimp in warm
    shallow straits.
  - Radar: radar horizon (4/3 earth), surface-based duct likelihood by theatre and season, a sub-refraction check,
    clutter at 0.3 and 3 deg and S band, 20 km two-way rain loss, SATCOM Ku/Ka fade, multipath.
  - EO/IR: dust haze (visual worse than IR), a night-vision class from moonlight.
  - Air ops: carrier recovery case from ceiling and visibility.
- Game: the helicopter launch limit (each ship's MaxLandingSeaState).
- Untested overrides: SofarAxisDepthM by theatre, AbsorptionFactor, disabling convergence zones in deep but warm water,
  LayerDisabled for well-mixed seas.

Not added, because the review's checkers rejected them: aircraft icing, thermal crossover timing, HF space weather.
157 tests.

## Sixteenth pass: file-layer probe tools (19 Nov)

tools/probe_file_layers.py (standard library) and RUN-LAYER-PROBE.ps1:
- scan-dll: reads a .NET assembly's metadata without loading it (ECMA-335 tables Module to MethodDef, #Strings, #US)
  and lists the types, members and literal strings about layers, overrides, mounts and missions. Tested on the repo's
  compiled plugins.
- scan-mods: lists every overrides/ folder and, per INI file, the keys added and changed and the sections left out
  against the original. On the Kuznetsov mod it confirms partial files that only add squadrons.
- capture-env: the installed environment.ini [Sonar] keys and its SHA-256.
- install / uninstall / status: probes A-mod, A-user1, A-user2, A2, B1-B3, C and D with a manifest. Install never
  overwrites. Uninstall deletes only unchanged files and removes the folders it made.

Repo evidence used:
- Mod layers are <mod>/overrides/<original path>, with partial INI files (the Kuznetsov mod).
- The engine has an ordered FileLayer(path, LayerKind) list (BetaApiTests.cs).
- The user-level and per-mission folder names are unknown until the PC scan.

Nothing in-game tested. 162 tests.

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
