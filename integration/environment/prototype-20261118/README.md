# Modern Naval Operations / Global Command Operations — Environment Prototype

**Draft built 18 November 2026 | MNO all-in-one mod | GCO world campaign**

## Contents

- **`web/MNO_GCO_ENV_VIEWER.html`** — a functional offline animated globe/world viewer. It includes deterministic moving storms, cloud and precipitation cells, sea ice, iceberg *markers*, approximate shelf fronts, and three route assessments. **Double-click this HTML file; no web server is needed.**
- **`RUN-VANILLA-PLAYTEST.ps1`** — create a separate Sea Power mission based on the vanilla Hormuz or Breakthrough mission and optionally install as an isolated local test mod.
- **`tools/import_openmeteo.py`** — opt-in online point-data API import (sparse and unblended). `--dry-run` previews requests without accessing the API.
- **`tools/patch_vanilla_mission.py`** — independent mission patch generator: no original file changes.
- **`docs/TECHNICAL_HANDOFF.md`** — detailed architecture, R.A.T.S. code precedent, source data plan, limitations and real-game test checklist.
- **`src/environment_model.py`** and **`tests/`** — deterministic no-dependency environmental model and 11 Python unit tests.

**Critical distinction:** The browser viewer works and the standalone mission generator is syntactically tested, but no Sea Power in-game run, weather visual effects, globe plugin or GCO persistence is yet proven. The shipped example fields are synthetic, not real global weather.

## Quick start: Windows browser demo

Extract this ZIP. Double-click `web\MNO_GCO_ENV_VIEWER.html`. Press Play, scrub the time control, rotate the globe by dragging, and toggle clouds, precipitation, sea ice, wind, waves or pressure. Switch to World or South polar projection. Compare route A/B/C. Time progression is 6 campaign hours per replay frame. The moving iceberg markers and ice shelf fronts are schematic.

## Quick start: vanilla Sea Power playtest

From **Windows PowerShell**, `cd` into this extracted folder, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN-VANILLA-PLAYTEST.ps1 -GameRoot 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power' -Mission Hormuz -Mode front -Install
```

This requires Python 3 with `py -3` or `python`. Change `-GameRoot` if Steam is installed on another drive. The script reads the **original vanilla** `NATO\Hormuz.ini`, writes a new version under `examples\MNO-Environmental-Playtest\missions`, and copies **only that separate local mod folder** to `Sea Power_Data\StreamingAssets\content\MNO-Environmental-Playtest`. It does **not** modify the original scenario, R15, GitHub or Steam Workshop. The expected copied files are `_info.ini`, `missions\MNO Weather Lab - Hormuz.ini`, and `PLAYTEST_META.json`.

If you want to inspect before installation, omit `-Install` and check the generated folder. The vanilla Breakthrough mission also works as the source: replace `-Mission Hormuz` with `-Mission Breakthrough`. `-Mode front` produces eight deliberately accelerated, dramatic, scripted weather stages; `-Mode grid` samples the synthetic Southern Ocean dataset instead (not necessarily geographically relevant to Hormuz). Sea Power's weather actions remain scenario-wide, not per-cell physical weather.

In Sea Power: enable **MNO - Environmental Playtest** in the mod selection if needed, then go to **Scenarios** and run the generated scenario. Do **not** resave the hand-edited test via Mission Editor, which may reserialize or discard custom triggers. Check changes every 300 in-game seconds. If the mod isn't listed, inspect `Player.log` and the local content-folder layout; loader behaviour varies by build.

**Uninstall:** close Sea Power, then manually remove only the folder `Sea Power_Data\StreamingAssets\content\MNO-Environmental-Playtest`. Don't touch `original`, your main MNO mod or its Workshop files.

## Playtest against an MNO scenario instead of vanilla

```powershell
py -3 .\tools\patch_vanilla_mission.py --source 'C:\path\to\Seapower-mods\integration\campaign\SEST_Campaign\missions\Southern Reach\Southern Reach 09 - Cold Route.ini' --output-dir '.\examples\MNO-Environmental-Playtest' --mode grid --latitude -54 --longitude -49
```

Only run this against a **local copy** and treat dependency/mission-logic compatibility as unverified. Do not mix with the R15 release artefact without separate regression testing.

## Real API requests (network access on your PC required)

```powershell
py -3 .\tools\import_openmeteo.py --mode archive --region weddell --start 2025-09-14 --end 2025-09-16 --dry-run
py -3 .\tools\import_openmeteo.py --mode archive --region weddell --start 2025-09-14 --end 2025-09-16
```

The second command fetches Open-Meteo UTC hourly historical point samples and saves `data\openmeteo_observations.json`. In the offline HTML viewer, use **Load real API station JSON (local file)** to inspect these stations as green dots and read their original source timestamps. The imported points **do not replace or assimilate** the synthetic global weather raster: this is a source-verified API-to-map connectivity test, not yet a complete high-resolution weather simulation. For data licensing and gridded weather/ice ingestion, see `docs/TECHNICAL_HANDOFF.md`.

## Run unit tests and rebuild offline viewer

```powershell
py -3 -m unittest discover -s tests -v
py -3 .\tools\build_demo.py
```

The model has no pip dependencies. Rebuilding the viewer from the included source uses the bundled coastline data, so it doesn't need GeoPandas/pyogrio. The optional `tools/coastline_extract.py` is for updating the public-domain coastline outlines from the author's build environment; it is not necessary at runtime.

## Status

- R.A.T.S. validates the general **globe overlay rendering geometry** but not an animated **GCO** view.
- The browser demonstrates movement, projection and interaction without requiring Sea Power to run.
- The test mission exercises only supported **global** Sea Power weather changes via INI triggers.
- Full live/weather-cell coupling, physical ice drift/collision and a persistent GCO environmental save extension are proposed next steps, not delivered features.
