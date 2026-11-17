# ENV-TEST-RESULTS, 18 November 2026

Container: Linux, 4-core Intel Xeon 2.1 GHz, 16 GB RAM, Python 3.13.18, Pillow 12.3.0,
no GPU, no PowerShell, no .NET, no Sea Power. Commit base `75b8a426` (R15).

## 1. Environment suite

```
$ python3 -m unittest discover -s integration/environment/tests -t integration/environment/tests
Ran 79 tests in 14.714s
OK
```

| Module | Tests | Covers |
|---|---|---|
| `test_mission_ini` | 19 | weather-only disable, mixed strip, Enable/Reactivate/Timer refusal and strip, commented references, existing `Disabled=False`, duplicate `Clouds`, all-language rename, duplicate ids, counter below highest id, counter above highest id, state rules (thunderstorm needs Overcast, no snow action), CRLF + BOM, explicit times, conditions style, start time; Hormuz and Breakthrough; **every mission INI in the repository** (632 with triggers: 627 patched and re-verified, 5 refused) |
| `test_snapshot_clock` | 14 | procedural determinism and seed sensitivity; corrupted checksum, units, NaN, range, length, timestamp, licence, mapping statement; labelling (synthetic as observed, forecast without issue, reanalysis with issue, analogue of synthetic); lead time and order; thunderstorm only as derived risk; int16 packing; deterministic gzip; truncated/damaged gzip; leap-day analogue; interpolation weight and stale; replay vs fast-forward digest; clock preview/advance/pause/set; antimeridian sampling |
| `test_geo_polar_grid` | 12 | 23 PROJ 9.8.1 reference points for EPSG:3411/3412/3413/3976/6931/6932 (forward within 1 mm, inverse within 1e-7 degree); seam continuity in polar; poles; wrap and GCO's -100..258 frame; great circles across 180; Natural Earth land test (shelves read as water, recorded); bilinear across the seam, duplicated seam column, regional grid across 180, missing corners, polar-to-lat/lon regrid |
| `test_services` | 17 | sidecars for save A/B (no leakage), same seed in another slot, save-as, delete, missing/corrupt/foreign sidecar, unsafe ids, rules-version warning; cache round trip, wrong version, corrupt, missing, unknown id, no dataset, broken manifest (all fall back to procedural with a reason); invalid snapshot refused; forecast determinism per side, error growth, observation, recon, stale, estimate, truth untouched; ice access thresholds, sourced capability table, schematic shelves, open-ocean route equals great circle, bounded fuel, land/shelf/ice blocks, iceberg drift, lifetime and hazards |
| `test_adapter_ingest_overlay_tools` | 14 | WMO 3700 sea-state bands, oktas, wind-from direction, rain/snow/thunderstorm/fog rules, plan into Hormuz; ECMWF accumulated precipitation to mm/h (clamp and refusal), units, 0-360 rotation, row flip, thinning, OSI SAF flags, polar regrid; built snapshot validates; equirect round trip and seam; polar window full coverage; empty field transparent; texture memory; Weather Lab tool (hashes, eight stages at 300 s, refuses to overwrite, source unchanged, procedural mode) |
| `test_prototype_import` | 3 | the prototype's own 11 tests pass; its generator reproduces the demo file's manifest SHA-256 `f266be84...`; kept sources match the manifest |

## 2. Repository checks (R15 gates)

| Check | Result | Note |
|---|---|---|
| `tools/check_scenarios.py` | pass | |
| `tools/check_pack_fidelity.py` | pass | |
| `tools/check_load_order.py` | pass | |
| `tools/check_dependencies.py` | pass | |
| `tools/check_stale_phrases.py` | pass | 323 files, includes the new docs |
| `tools/check_game_version.py` | **FAIL, pre-existing** | identical at clean `75b8a426`: DCM 3813157776 declares `< 0.9.0` |
| `tools/check_campaign_coverage.py` | not run | needs `global-land-mask`, not installed in this container |
| `tools/tests` (unittest, verbose) | 396 ok, 7 errors, then the run stops at a script that needs `global-land-mask` | **the same 7 errors and 396 passes at clean `75b8a426`** (diffed); missing optional dependencies in the container |

No file outside `integration/environment/` and `docs/environment/` was changed.

## 3. Weather Lab outputs (0.9.2 export as source)

```
Hormuz       front, time kept  src 65474db0cba0d524 -> fd19df3c657863f1  triggers 10 -> 17  disabled 7,8,9,10
Hormuz       front, 10,0       src 65474db0cba0d524 -> 89738dfba9638982  triggers 10 -> 17  disabled 7,8,9,10
Breakthrough front, time kept  src 31c82d1a4a28b2a9 -> 4fca0934d5cba67e  triggers 23 -> 30  disabled 7..15
Breakthrough front, 10,0       src 31c82d1a4a28b2a9 -> c84f4f0921459151  triggers 23 -> 30  disabled 7..15
```

Corpus run over every INI with `NumberOfTriggers` under `mods-source/` and `integration/`
(632 files: vanilla 0.9.2 export, Workshop mods' missions, SEST campaigns and seeds): 627 patched
and re-verified, 5 refused for cause, 0 unexpected errors. Refused: `campaign-proto-1/campaign.ini`
(no `[Mission]`), both copies of `Demo/MissionFileInformation.ini` (two `[Trigger2]`),
`Red Madagascar 1985.ini` (two `[Environment]` sections), and one user copy of `PLAN 02` that is
not UTF-8. 8 user-mission backups that already mix CRLF and LF patch with a warning.

## 4. Performance (Python reference, not the game)

| Global grid | Cells | int16 slice | float32 slice | 72 h gzip | generate | one 9-field sample |
|---|---|---|---|---|---|---|
| 4 degree | 4,140 | 8.3 kB | 16.6 kB | 0.27 MB | 0.8 s | 52 us |
| 2 degree | 16,380 | 32.8 kB | 65.5 kB | 0.89 MB | 3.1 s | 99 us |
| 1 degree | 65,160 | 130 kB | 261 kB | 2.84 MB | 13.0 s | 276 us |

Overlay texture memory: 1024x512 RGBA32 2 MiB, 2048x1024 8 MiB, 4096x2048 32 MiB (R8: a quarter).
Python overlay build 360x180 with live sampling: 0.34 s; the map proof (3 views x 5 layers) 93 s.
Game frame time: NOT MEASURED.

## 5. Not tested

Anything in Sea Power; the PowerShell launcher; the ECMWF and OSI SAF converters on real files;
any DCM interaction; any network download.
