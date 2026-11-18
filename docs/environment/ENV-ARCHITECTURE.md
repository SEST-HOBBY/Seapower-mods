# ENV-ARCHITECTURE

18 November 2026. SEST-DEV. What exists is marked; the rest is design.

## 1. Separation

```
 external data (ECMWF, ERA5, OSI SAF, Open-Meteo points)          never inside the game
        |  tools/ingest_*.py  (offline, optional readers, run by hand)
        v
 mno.environment.snapshot.v1 files  +  manifest.json   = local cache folder
        |  MnoEnvDataProvider.resolve()  (cache.py)  -> procedural fallback on any problem
        v
 MnoEnvState (clock.py)  <-  MnoEnvClock: campaign UTC seconds, offset, frame bracket
        |                         |
        |                         +-> MnoEnvPersistence: one sidecar per GCO save
        v
 consumers:  MnoEnvForecast (what a side knows)      MnoEnvMissionAdapter (native weather)
             MnoEnvIceOperations + routes (rules)    MnoEnvGlobeLayer (overlay textures)
```

The Python package `integration/environment/mno_env` is the tested reference for every box
except the game-side layer. The game side (C#, BepInEx, inside the MNO runtime) will read the
same snapshot files and port the same maths; the Python tests become its fixtures (same inputs,
same expected numbers). No network call exists in the game-side design; the only code that
can download anything is `tools/ingest_ecmwf_opendata.py --download` (optional, run by hand).

## 2. Map types and APIs

See `ENV-00-map-targets.md`. In short: tactical = Sea Power's own globe (class names unknown on
0.9.3); GCO strategy view = DCM's own UI (`CampaignUI`, renderer unknown); the battle hand-off is
DCM `MissionWriter.Text`. All three are BLOCKED on a 0.9.3 capture and on DCM running on 0.9.3.

## 3. Game-side services (DESIGN ONLY)

| Service | Responsibility | Threading |
|---|---|---|
| `MnoEnvDataProvider` | load the cache manifest once per campaign load; verify SHA-256; fallback to procedural | load on campaign load, off the render thread (Task), result handed to main thread |
| `MnoEnvClock` | campaign UTC from DCM's campaign time; never wall clock | main thread, read on DCM tick |
| `MnoEnvState` | decode at most two frames per field (bracket), cache 64 slices max | worker thread decode, immutable result |
| `MnoEnvGlobeLayer` | one `Texture2D` per visible layer, double-buffered | texture upload on main thread only, every 5-10 game seconds, not per frame |
| `MnoEnvMissionAdapter` | postfix DCM `MissionWriter.Text`: rewrite `[Environment]`, append weather triggers | synchronous, string only |
| `MnoEnvIceOperations` | access, shelves, icebergs; route previews | on request |
| `MnoEnvForecast` | per-side reports | on request |
| `MnoEnvPersistence` | sidecar per save id | on DCM save/load events |

Feature flag: an ini switch `EnvironmentEnabled=false` in the MNO runtime ini (same pattern as
the F8 pop-out switch, `RuntimeFixesMod.cs`). When off, no service is constructed. When on and
DCM is absent or its types do not match the captured signatures, log one line
(`[MNO ENV] disabled: <reason>`) and stay off. Never bypass the R15 loader's version guard.

## 4. UI (DESIGN ONLY)

A single **Environment** dropdown button beside DCM's Economy control (the position the R14 F11
costs button proved can host a Noesis control, `WorldMapCostsButton.cs`), opening a panel:

- layer toggles: Cloud, Rain, Wind, Waves, Pressure, Sea Ice, Icebergs, Forecast (independent);
- opacity slider; legend with units (`%`, `mm/h`, `m/s`, `m`, `hPa`);
- time scrub `Now / +6 h / +24 h / +72 h` that calls `MnoEnvClock.preview()` only (it cannot
  advance campaign time; tested);
- badges: data class (OBSERVED / FORECAST / ANALOGUE / PROCEDURAL), source and issue time,
  freshness, and "not a forecast of 2028" for analogue data;
- no new hotkey; F8 and F11 untouched; the panel closes and every texture is destroyed on
  leaving the strategy view.

## 5. Rendering and performance plan

Measured here (Python reference, 4-core 2.1 GHz Xeon, no GPU):

| Global grid | Cells | Slices (9 fields x 13 times) | int16 per slice | float32 per slice | gzip JSON on disk | one 9-field sample |
|---|---|---|---|---|---|---|
| 4 degree | 4,140 | 117 | 8.3 kB | 16.6 kB | 0.27 MB | 52 us |
| 2 degree | 16,380 | 117 | 32.8 kB | 65.5 kB | 0.89 MB | 99 us |
| 1 degree | 65,160 | 117 | 130 kB | 261 kB | 2.84 MB | 276 us |

Overlay textures: 1024x512 RGBA32 = 2 MiB, 2048x1024 = 8 MiB, 4096x2048 = 32 MiB; an R8 field
texture with a shader palette is a quarter of that. Plan: data at 1 degree global (2 degree in a
low-performance mode), textures 2048x1024 R8 per visible layer, two buffers per layer while
switching (16 MiB for four layers), no mip chain needed for a global overlay but one for polar
insets. Never hold more than the two bracketing frames decoded. A 0.1 degree global multi-field
archive is never loaded into memory; regional high-resolution tiles are a later step.

Frame time in the game: NOT MEASURED (no game). The owner card asks for frame time with
the layer on and off once a layer exists.

## 6. Snapshot and provenance schema

`mno.environment.snapshot.v1` (`schemas/mno.environment.snapshot.v1.schema.json`; the
conformance check is `mno_env.snapshot.validate`). Per snapshot: provider, product, version,
licence, attribution, source URL, downloaded time, source time, forecast issue time, the
campaign mapping (mode, offset seconds, a statement that it is not a forecast of 2028-2029),
grid and CRS, per field units / kind / fill / uncertainty / derivation, per time valid UTC and
lead hours, and a payload SHA-256. Modes:

- `historical_analogue`: a past date replayed at the same calendar time in the campaign;
- `current_analogue`: a recent real forecast replayed from campaign start;
- `procedural`: seeded field, the offline default;
- `synthetic_demo`: the prototype's demo only.

Rules the validator enforces: synthetic or procedural data cannot be labelled observed; a
convective field is `derived_risk` with a derivation note, never an observed lightning field; a
forecast has an issue time and lead = valid - issue; times strictly increase; units are the
canonical ones; values are within physical ranges; the checksum matches.

## 7. Persistence

`<root>/<campaign id>/<save id>.mno-env.json`, schema `mno.environment.save.v1`, written
atomically, with its own SHA-256: seed, mode, dataset id and file hash, offset, last campaign
time, rules version, per-side forecast state, resolved events. Not the profile-wide pattern of
`world-service-v1.txt`. Missing sidecar: deterministic default from the save's ids. Corrupt:
kept untouched, warning, same default until the next save.

## 8. Ice and logistics rules

Three classes (`mno_env/ice.py`): sea-ice concentration with access by an owner-sourced
capability table (empty today: no unit has a verified ice class, and the collection has no
icebreaker); ice shelves as static polygons that routes may not cross (Natural Earth 1:10m,
public domain, islands as holes); icebergs as tracked objects with drift, growing position
uncertainty and lifetime. Route previews (`routes.py`) advance through campaign time, stop at
land, shelf or impassable ice, and give hours and fuel with a bounded penalty (at most +25 %).
None of this changes a campaign until wired and PC-tested; no damage or collision anywhere.
