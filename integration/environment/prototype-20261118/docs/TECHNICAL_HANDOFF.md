# Modern Naval Operations: Global Command Operations — environmental prototype handoff

**Evidence cut-off:** 18 November 2026 (Australia/Brisbane).  
**Status:** Generated, unit-tested web prototype; *not* integrated, compiled or playtested in Sea Power.  
**Mod layout:** Modern Naval Operations is the **single all-in-one mod**. Global Command Operations (GCO) is the **persistent world campaign** inside it. No separate environmental Workshop item is assumed.

## Verified existing affordances

1. **R.A.T.S. Topographic Map** (MIT, https://github.com/struckl/SeaPowerTopo) demonstrates the globe-rendering approach in Sea Power 0.9.1: `Render/GlobeMesh.cs` aligns a georeferenced quad texture with the stock sphere's 1-degree cells and visible cap; `TopoLayer.cs` registers a tactical map layer; `Patches.cs` uses staged Harmony hooks to avoid early Noesis initialisation. This is a validated *technical precedent* for a map overlay, **not** proof of an animated GCO strategic-map layer. Do not copy any source code without retaining the MIT licence and attribution. Better approach: implement original renderer with the same proven geometry concepts and isolated namespace, with user-licensed dependencies.
2. **MNO R15 repository (89b9b4649)**: `integration/beta-feature-parity/runtime/WorldMapCostsButton.cs` adds a Noesis UI control to the Dynamic Campaign Mod strategy view, beside Economy; `WorldOperations.cs` observes `CampaignSession` and its strategic active lifecycle. These are relevant attachment points, **not evidence that the DCM strategy map is a drawable `MapControl` or the same tactical `MapDisplayState`.** It also explicitly treats DCM state/saves as read-only. Research a supported campaign save-extension before writing environmental persistence.
3. **Vanilla mission weather triggers**: `Action_SetClouds`, `Action_SetSeaState`, `Action_SetRain`, `Action_SetFog`, `Action_SetSnow`, `Action_SetThunderstorm`, and `Condition_Type=Time` are documented. The original vanilla `Breakthrough.ini` and `Hormuz.ini` include existing weather triggers. In addition to appending them, the mission's `NumberOfTriggers` must be increased. Test trigger precedence and mission editor reserialization; scenario files should be playtested through the Scenarios menu and NOT saved with Mission Editor once hand-edited.

## Produced this iteration

- `src/environment_model.py`: deterministic gridded weather and sea-ice demonstration, temporal frames, anti-meridian handling, bilinear sampling and a non-navigational risk score.
- `web/MNO_GCO_ENV_VIEWER.html`: one-file **offline** animated world and globe weather/ice demonstration. The data are fully embedded; double-click on Windows. Draggable 3D globe, flat world chart, polar view, weather controls, route alternatives, iceberg symbols and time replay.
- `tools/import_openmeteo.py`: opt-in **real API** request adaptor. Output is a sparse, source-tracked point-observation record that can be loaded in the viewer as green station dots with original UTC timestamps. It must **not** be described as a complete global high-resolution field.
- `tools/patch_vanilla_mission.py`: non-destructive weather-trigger converter for a vanilla or MNO local scenario. Clones it, disables unreferenced *weather-only* triggers to avoid conflict, appends animated weather stages, updates `NumberOfTriggers`, and generates standalone mod `_info.ini`. Native Sea Power in-game test is still required.
- `RUN-VANILLA-PLAYTEST.ps1`: optional install to `StreamingAssets/content/` for an isolated local mod. SHA-256 verifies original file unchanged. Never writes to GitHub, Workshop, or R15 branches.
- `tests/`: deterministic weather, anti-meridian, import contract, conversion, and trigger safety checks.

## Recommended runtime modules in MNO (future — do not treat as implemented)

| Module | Responsibility | Lifecycle |
|---|---|---|
| `MnoEnvDataProvider` | Load a validated local snapshot; never issue unbounded live API calls in Unity's render/update loop | Startup / campaign load |
| `MnoEnvClock` | Map campaign UTC -> data UTC/forecast lead; support replay seed & save version | Strategic simulation tick |
| `MnoEnvState` | Pressure, cloud, rain, wind vectors, wave grids, sea ice, uncertainty, provenance | Immutable snapshot / atomic replacement |
| `MnoEnvGlobeLayer` | Projection-correct layered rendering, tile cache, alpha blending, visibility toggles | GCO strategic-map view |
| `MnoEnvTacticalLayer` | Reuse same gridded data for local tactical overlays; more frequent refresh only for visible viewport | Mission tactical map |
| `MnoEnvMissionAdapter` | Translate environmental snapshot to supported initial `[Environment]` and time-trigger fields | Before scenario generation |
| `MnoEnvIceOperations` | Ice concentration and route eligibility, escort/ice-strength class; **no collision claims** | GCO movement/supply calculation |
| `MnoEnvForecast` | Observed, forecast, stale and uncertain information as distinct player knowledge states | Intelligence reports |
| `MnoEnvPersistence` | Save source time, campaign time, run ID, generator seed, environmental ruleset and relevant deterministic state | GCO save/restore |

### Integration order

1. Confirm **GCO strategy view's actual globe type** via inspected runtime assembly, including whether its rendering source is shared with the tactical map. Record screenshots and a minimal Harmony hook signature. Do not assume the R.A.T.S. tactical map hook applies to GCO.
2. Render **one static georeferenced texture** on GCO globe, in a single limited test region. Test high latitude, longitude 180 crossing and view/camera change. Ensure no visible seams, symbol occlusion or depth issues.
3. Swap the texture once every 5-10 game seconds (UI test), not once per rendered frame. Profile allocations and FPS with 10,000 moving entities / heavy UI scenario as appropriate.
4. Load real compacted local data, not network data on the Unity main thread. Handle offline mode, missing timestep, corrupted cache, and provenance metadata.
5. Attach a deterministic environmental tick to a GCO campaign-time clock; persist and reload. Preserve existing save semantics. Do not assume the ability to mutate DCM game state based on current `WorldOperations` read-only integration.
6. Map regional weather into generated mission settings and trigger schedule; prove weather evolution in tactical gameplay. Avoid changing unsupported physics and acknowledge that native weather is generally scenario-wide.
7. Add routing, ship-specific limitations, air-deck constraints, supply delays and polar access via campaign rules, *only after calibration and fixture tests*.

## Scientific fidelity and data-path plan

Use the following *separate* data streams; do not conflate them or simulate a single drifting polygon for every ice type.

- **Weather:** pressure, 10m u/v wind, precipitation rate, total cloud fraction, storm metadata and lead-time uncertainty. Near term: ECMWF IFS open-data GRIB2 at 0.25° or 0.1°; historical: ERA5. Do not claim future fictional years are a forecast; use historical analogue replay or statistically fitted climatology with explicitly labelled perturbations.
- **Ocean:** significant wave height, direction, period, currents and SST. Do not directly equate Beaufort or Douglas sea-state numbers to significant wave height without calibration. Use dedicated wave products. The current demonstration uses a deliberately rough mapping for visual test only.
- **Sea ice:** concentration/edge, landfast ice, ice type, drift vector and thickness where available. OSI SAF provides near-real-time daily concentration and drift products with separate resolutions. Respect projection/time-step and uncertainty.
- **Ice shelves:** floating glacial fronts remain grounded upstream and change over long timescales through flow and calving. Resolve *shelf fronts* on appropriate timescales (months/years), not hours like weather systems. Use authoritative Antarctic geometry and treat dynamic calving events as stochastic if not data-backed.
- **Icebergs:** tracked large iceberg polygons/points, currents and wind-driven drift, life cycles after calving; include uncertainty growth. The current moving map triangles are explicitly fictitious demonstration markers, not a collision model.

### Cache schema (initial proposal)

```text
MnoEnvironmentSnapshot v1
  metadata: dataset_id, provider, licence, issued_time_utc, valid_time_utc,
            original_time_utc, simulation_time_utc, resolution, hash, source_url,
            coordinate_reference=WGS84, uncertainty_class, replay_rule
  tiles:   time_index, bounding_box, lon_wrap, dimensions, field_name, unit, values
  ice:     sea_ice_concentration, drift_u/v, polygons, static_shelf_fronts,
           iceberg_tracks, quality_flags
  runtime: deterministic_seed, current_index, interpolation_rules
```

### Key risks and explicit non-goals of the initial playtest

- Native weather actions are **scenario-wide**, not weather cells localised at each ship. Moving overlay cells are visual/strategic simulation only until runtime supports local atmospheric effects; do not imply users experience geographically local storms in tactical view.
- No dynamic sea-ice collisions or ship damage from ice have been proved. Use strategic access restrictions first.
- The live API sample is sparse point data, not full-grid interpolation/assimilation. For high-resolution production, ingest GRIB/NetCDF in a separate tooling pipeline, reproject to globe tiles, compress time-series and publish static caches alongside the mod.
- Free-access APIs can limit commercial redistribution, usage frequency and attribution. Recheck licences and quotas before releasing derived data and before reuse in other SEST products.
- GCO UI availability and compatibility are not identical to the tactical R.A.T.S. overlay; special care with Noesis/Harmony/BepInEx/Anchor Chain/R.A.T.S. Keel startup order, 0.9.3 game changes and Steam mod loader selection.

## Tests for acceptance (must be run on a Windows Sea Power install)

- [ ] Vanilla weather lab appears in Scenarios when local mod is enabled
- [ ] Weather lab starts without game or mod loader errors
- [ ] Cloud density, rain, thunderstorm, fog and sea state change as triggers fire; time offset matches expected values
- [ ] Flight deck / sonar behaviour changes only where the engine actually supports it; note FPS and native logs
- [ ] On mission exit, no residual weather state leaks into another mission
- [ ] Existing vanilla campaign and R15 candidate remain bitwise unchanged
- [ ] External viewer works offline, with UI time scrub / frame replay, 180° wrap and polar globe
- [ ] R15 / GCO strategy globe **mapping** is explicitly proven or falsified in source inspection before integration
- [ ] GCO save/load environmental state is implemented and independently replay tested before release

## Technical references

- [R.A.T.S. Topographic Map, source under MIT](https://github.com/struckl/SeaPowerTopo)
- [MNO R15 repository baseline](https://github.com/SEST-HOBBY/Seapower-mods/tree/89b9b4649)
- [Vanilla mission trigger guide](https://steamcommunity.com/sharedfiles/filedetails/?id=3392721470)
- [ECMWF Open Data IFS/AIFS](https://www.ecmwf.int/en/forecasts/datasets/open-data)
- [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api)
- [Open-Meteo Marine API](https://open-meteo.com/en/docs/marine-weather-api)
- [OSI SAF polar sea-ice products](https://osi-saf.eumetsat.int/products/sea-ice-products)
- [Natural Earth public domain vector data](https://www.naturalearthdata.com/about/terms-of-use/)
