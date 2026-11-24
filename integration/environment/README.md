# MNO environment (ENV track)

Modern Naval Operations / Global Command Operations: weather, ocean state and ice.
**Not released, not packaged, nothing here loads in the game.** Status per piece:
`docs/environment/ENV-STATUS.md`.

| Path | What |
|---|---|
| `mno_env/` | Python reference implementation, standard library only: snapshot format and validator, polar projections, grids, campaign clock, procedural fallback, cache, per-save persistence, forecast intelligence, mission INI weather patching and adapter, ice and routes, overlay maths |
| `tools/build_weather_lab.py`, `RUN-WEATHER-LAB.ps1` | ENV-01 Weather Lab: build from an installed vanilla mission; `-Quick` builds and installs one file into `user_missions`; `-CollectLogs`; `-Uninstall` |
| `tools/render_map_proof.py` | Offline georeferenced map proof (needs Pillow) -> `docs/environment/map-proof/` |
| `tools/validate_snapshot.py`, `tools/build_procedural_snapshot.py` | Snapshot conformance check; procedural cache entry |
| `tools/ingest_openmeteo_grid.py` | Real weather for a region and date from official models (ERA5 recorded, ECMWF IFS forecast, waves) via Open-Meteo JSON into the cache |
| `tools/refresh_seaice_climatology.py` | Recompute the seasonal sea-ice table from NSIDC's monthly CSVs |
| `tools/ingest_ecmwf_opendata.py`, `tools/ingest_osisaf_ice.py` | Offline converters for raw GRIB/NetCDF files (optional readers; not run in the repository) |
| `schemas/` | JSON schema of `mno.environment.snapshot.v1` |
| `data/` | Ice capability table (empty on purpose), Natural Earth 1:10m Antarctic ice shelves and their fronts, per-shelf attributes (`ice-shelf-attributes.json`, see docs/environment/ICE-SHELVES.md), iceberg climatology (`iceberg-climatology.json`, see docs/environment/ICEBERGS.md), NSIDC sea-ice climatology |
| `prototype-20261118/` | The supplied prototype, sources unchanged (`IMPORTED.md`) |
| `tests/` | 219 tests |

```bash
python3 -m unittest discover -s integration/environment/tests -t integration/environment/tests
```

```bash
python3 integration/environment/tools/build_weather_lab.py --source "mods-source/_vanilla/original/missions/NATO/Hormuz.ini" --output /tmp/lab --mission-time 10,0
```

Everything labelled procedural or synthetic is **not real weather**. Analogue modes replay real
past or current data at the fictional 2028-2029 campaign dates; they are not forecasts of those
years.
