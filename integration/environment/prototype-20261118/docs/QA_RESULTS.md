# QA receipt — MNO GCO Environmental Prototype (18 November 2026)

## Completed successfully in the isolated build environment

1. `python3 -m unittest discover -s tests -v` — **11/11 passing**; core deterministic field, anti-meridian interpolation, map grid shape, bounds, route sample, native trigger counter and preservation, Open-Meteo adapter schema and units.
2. `node --check` on the viewer's embedded JavaScript — **pass**.
3. Headless Chromium + Playwright `set_content()` with the generated **single-file, embedded-data** HTML — **pass**; rendered without JavaScript errors.
4. Tested globe display, World projection switch, South polar projection, slider advancing 0 to 36 campaign hours, wave layer toggle, and importing a mock source-labelled JSON station record — **pass**.
5. Verified original R15 `WorldOperations.cs`/`WorldMapCostsButton.cs` and original vanilla `Hormuz.ini`/`Breakthrough.ini` weather trigger formats directly through GitHub at `89b9b4649` (read only).
6. Verified R.A.T.S. Topographic Map 1.6.x source and inspected `TopoLayer.cs`, `Patches.cs`, `Render/GlobeMesh.cs` and `Render/FlatMapRef.cs` (read only). The prototype contains **no R.A.T.S. source code**.
7. `tools/import_openmeteo.py --dry-run` — **pass**; builds properly escaped historical weather query URLs for 12 Weddell/South Atlantic station samples.

## Not tested / not claimed

- Not compiled into a Sea Power C# runtime plugin or attached to GCO's strategic globe.
- No in-game visual or behavioural test of the generated vanilla mission; Steam build is not available in this container.
- No live Open-Meteo network fetch executed; network egress from the build container is unavailable. Use the supplied importer on a connected PC.
- No actual source scenario file edited or copied into Sea Power yet; the original vanilla mission must be available on the player's Windows PC.
- No realistic physically spatial weather affecting individual units, sea-ice collision physics, glacial front drift simulation, vessel hull strength model, or GCO save-state integration.
- The moving fronts, ice cover and icebergs in the offline demo are deterministic synthetic examples, NOT historical or current observational data and NOT a navigational forecast.

## Proposed acceptance order

1. Windows source-file path, local mission install and visibility in Scenarios.
2. Native weather trigger sequence and sea-state effects in at least one vanilla mission (not saved through Mission Editor).
3. Confirm whether GCO world/strategy map has its own renderer vs the R.A.T.S. tactical `MapDisplayState` / globe mesh.
4. One georeferenced static layer on the 3D globe (with high-latitude, dateline, zoom and map lifecycle tests).
5. Local cached GRIB/NetCDF translated to compact spatial tiles, then smooth animated layer with no main-thread API requests.
6. Campaign UTC/simulation-time determinism, save/load persistence and operational consequences.
7. Ice shelf fronts, iceberg drift, sea-ice access rules, wave/air operations — each validated independently and conservatively.
