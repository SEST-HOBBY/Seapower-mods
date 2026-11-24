# Ice features drop-in for the r16 battle runtime

Status: **BUILD-TESTED under Mono with stub game types. NOT PC-tested. OFF by default.**

This folder adds two things to Sea Power battles:

- **Ice shelves.** Antarctic ice-shelf fronts are drawn as ice cliffs near the camera. Ships and submarines cannot sail into them.
- **Icebergs.** Bergs from the iceberg climatology are placed in the battle area. They drift, and they can melt.

It is written for the battle runtime on `origin/feature/mno-r16` (`integration/beta-feature-parity/runtime/`). Nothing here has been copied to that branch yet.

## Files

| File | What | Goes to r16 |
|---|---|---|
| `IceFeaturesData.g.cs` | Generated tables: shelf outlines, front lines, land rings, shelf attributes, iceberg climatology | `runtime/` |
| `IceShelfRules.cs` | Pure logic: shelf containment, distance to the front, navigation rule, speed cap, cliff mesh | `runtime/` |
| `IcebergField.cs` | Pure logic: climatology, generator, drift, melt, sensor hooks, berg mesh | `runtime/` |
| `IceFeaturesBattle.cs` | The Unity-facing part: switches, game binding by reflection, speed postfix, drawing | `runtime/` |
| `tests/IceFeaturesTests.cs`, `tests/IceFeaturesGolden.g.cs` | The test exe and its golden values from the Python modules | `tests/` (optional) |
| `tests/BattleTests.cs`, `tests/stubs/*.cs` | Battle-part tests against stub `UnityEngine` / `SeaPower` types and a stand-in for r16's `Api` / `Policy` | stay here |
| `build_drop_in.py` | Compiles the pure logic and the tests with `mcs`, runs them with `mono` | stays here |

The generator is `integration/environment/tools/make_ice_features_data.py`. The Python test `integration/environment/tests/test_ice_features_drop_in.py` checks the generated files are current. It runs `build_drop_in.py` when `mcs` is installed.

## Switches

All go in `plugins/sest_runtime.ini`, section `[Runtime]`. Each feature is OFF unless set to `1`.

| Switch | Default | Effect |
|---|---|---|
| `IceShelves` | 0 | Draw shelf cliffs; keep ships and submarines out of shelves |
| `Icebergs` | 0 | Place, drift and draw icebergs |
| `IceFeaturesDiagnostics` | 0 | Log the binding, the battle date, counts, holds and the nearest berg's sensor numbers |
| `IceShelfViewKm` | 30 | Draw cliffs within this distance of the camera (5-80) |
| `IceShelfStandoffNm` | 2 | Submarine stand-off from a front (0.5-10). The 2 nm is an estimate |
| `IceShelfSurfaceLimitNm` | 0.1 | How far off a front a surface ship stops, measured from the hull centre (0.05-2). The 0.1 nm is an estimate |
| `IcebergRadiusNm` | 25 | Bergs exist within this distance of the camera (5-60) |
| `IcebergViewKm` | 30 | Bergs are drawn within this distance (2-60) |
| `IcebergMaxDrawn` | 400 | At most this many berg objects (20-3000) |
| `IcebergSeed` | 0 | Generator seed. The same seed and date give the same bergs |
| `IcebergSstC` | unset | Sea temperature for melt, in C (-2 to 15). Unset means no melt |

A value out of range falls back to the default.

## How to integrate into r16

1. Copy `IceFeaturesData.g.cs`, `IceShelfRules.cs`, `IcebergField.cs` and `IceFeaturesBattle.cs` into `integration/beta-feature-parity/runtime/`. `build.py` and `build-roslyn.ps1` compile every `runtime/*.cs`, so no build change is needed.
2. Add one call in `RuntimeFixesMod.TriggerEntryPoint`. Put it next to the `SeaIce` block, **before** the `CumulativeCombatCosts` early return:

   ```csharp
   // Beta only, default OFF: IceShelves=1 / Icebergs=1 in [Runtime] (IceFeaturesBattle.cs).
   // Install never throws; each part fails closed with one log line.
   IceFeaturesBattle.Install(assembly, lines);
   ```

3. Optional: add the pure test to `build.py`, next to `SeaIceTests.exe`:

   ```python
   compile('IceFeaturesTests.exe', [HERE / 'tests/IceFeaturesTests.cs', HERE / 'tests/IceFeaturesGolden.g.cs',
                                    HERE / 'runtime/IceFeaturesData.g.cs', HERE / 'runtime/IceShelfRules.cs',
                                    HERE / 'runtime/IcebergField.cs'])
   ```

   Without the stub files the battle part of that test is skipped. It says so.
4. Add the switches to the pack's `sest_runtime.ini` template and its docs, all set to `0`.

The code uses r16's own `Api.Type`, `Api.FindType`, `Api.Method`, `Api.Postfix`, `Api.Log`, `Api.LogFailure` and `Policy.TextOption`. `Install(assembly, lines)` takes types from the game assembly with `Api.Type`. It falls back to `Api.FindType`.

**Deliberate deviations from r16's style.** Convert them on copy if you want r16's style:

- Block namespaces (`namespace Sest.RuntimeFixes { ... }`). r16 uses file-scoped `namespace Sest.RuntimeFixes;`. Mono `mcs` cannot parse the file-scoped form, and the tests here are built with `mcs`. The Python test checks for the block form, so change that check too.
- Game members are reached by reflection, not through `using SeaPower;` and typed members. This lets the code compile without the game. Every member is bound once at install into a compiled delegate (Expression trees, or `Delegate.CreateDelegate` for the clock, as `SeaIceBattle.BindClock` does). The per-unit and per-frame paths do no `MethodInfo.Invoke` and no boxing.

## How it works

### Where the inputs come from

These are the same places r16's sea-ice code uses.

- **Date:** `Environment.get_DateTime`, the mission clock.
- **Position:** the camera, through `Utils.worldPositionFromUnityToLongLat(camera, Globals._currentCenterTile)`. Units use `ObjectBase._geoPosition`.
- **Placement:** `Utils.longLatToLocalV3`, as `SeaIceSheet.Place` does. Objects are placed again every 2 s and at once when the game moves its floating origin. Bergs drift and melt in the same 2 s step, just before they are placed.
- **Game time:** `GameTime.missionElapsedTime`. If it does not bind, bergs stay where they were made. They do not drift or melt. One log line says so. Unity's `Time.time` is not used, because it stops at 10x time compression (`GameTime._physicsTimeScaleCap`, as r16's `SeaIceBattle` notes). The no-go rule then samples on every call.
- **Date failure:** if the battle date cannot be read, the battle gets no bergs. One log line says so. No date is made up.
- **Sea state:** `Environment.get_SeaState`. It is used only in the diagnostics line.

### Ice shelves

- **Outline:** Natural Earth 1:10m Antarctic ice shelves, public domain. Simplified with Douglas-Peucker at **0.5 km**. Natural Earth at 1:10 million is itself generalised at about this scale. The golden test shows containment differs from the full outline only within 0.1 km of its edge (3 of 607 points).
- **Fronts:** Natural Earth 1:10m ice-shelf edge lines, **not** simplified. The front distance equals `mno_env.iceshelves.distance_to_front_nm`.
- **Epoch:** the fronts are a fixed past position, about 2003-2012 (an estimate). Later collapses are not shown. For example, Conger (collapsed about March 2022) is still drawn. See `docs/environment/ICE-SHELVES.md`.
- **Cliff height:** each shelf's typical front freeboard and draft from `data/ice-shelf-attributes.json`, the same values as `iceshelves.front_cliff`. Example: Ross, 30 m above water (20-40 m observed) and 190 m below (derived). Shelves with no value use the generic front: 30 m and 220 m (estimates).
- **Drawing:** a seaward face from the draft up to the freeboard, a flat top strip 1.5 km inland, an underside and an inland end wall. The 1.5 km is a visual choice. The shelf beyond it is not drawn.

### The no-go rule

- A postfix on `Compartments.UpdateWantedVelocityInKnots`. This is the hook where r16's `SeaIceBattle` caps ship speed. It acts on own **and** AI units.
- A surface ship stops with its hull centre 0.1 nm (185 m) seaward of a front. That keeps the bow of a 300 m hull out of the drawn cliff. The 0.1 nm is an estimate (half a 100-300 m hull plus a margin). No hull-length member is bound. `IceShelfSurfaceLimitNm` changes it.
- A submarine may not come inside the stand-off (2 nm, an estimate) of a front.
- The rule only lowers the speed the game asked for. Every second of game time it samples 0.25, 0.5 and 1 nm along the direction of travel.
- If a sample is in the no-go zone and closer than the hull, the hull keeps steerage way (0.1 of flank). At the limit it stops closing.
- A move along or away from the front is never capped. A hull is never trapped.
- Near a front, the inside/outside test uses the side of the nearest front line, from the full outline. So the 0.5 km simplification cannot flip it.
- The samples, the 0.1 factor and the margins are design values, not data.

### Icebergs

- **Source:** `data/iceberg-climatology.json` and `mno_env/icebergs.py`. Status ESTIMATE.
- **Same bergs as Python:** the generator uses Python's own random stream. It is a port of CPython's Mersenne Twister with its string seeding. It uses the same cells, the same order of draws, the same land rings and the same shelf rings. So `icebergs.generate(bbox, date, seed)` with the Natural Earth land mask lists the bergs a battle shows on that date, before drift. The test checks 608 bergs in 5 boxes: ids, classes, positions, sizes, drift and life all match.
- **Placement:** bergs exist within `IcebergRadiusNm` of the camera. The area is generated again when the camera moves half that far. A berg that enters later is drifted for the time since the battle began.
- **Never on land or a shelf.** The land rings are Natural Earth low resolution, the same as `geo.LandMask`. They are coarse: a narrow fjord can be missing (see below).
- **Drift:** the region's current proxy (an estimate) through `geo.displace`. Wind is not added in the battle, because no wind speed member has been inspected.
- **Melt:** only with `IcebergSstC` set. It uses the Martin and Adcroft (2010) form of the Bigg et al. (1997) rates, as `icebergs.melt_rates`. The coefficients are recalled (medium confidence). The wave-erosion term is left at zero in the battle: the game's sea state is a WMO code, not the wind-derived sea state the formula expects. So melt is basal and side convection only, which is slow.
- **Drawing:** low-poly shapes sized by the berg's own length, width, height and draft. The waterline is at sea level. The keel goes down to the draft. Tabular bergs are flat slabs. The shapes are a visual choice. A berg is drawn only within its class's day visual range (`icebergs.visual_detection_nm`), so growlers appear within about 1 nm.
- **Giant bergs** (10 nmi or more) are never generated. They are tracked by name.

### Sensor hooks

These are pure functions with tests. They are **not** wired to the game's sensors, because no sensor member has been inspected for it.

- `IcebergField.RadarFactor` / `RadarDetectionNm`: range by class and sea state, capped by the radar horizon. Growlers are lost from sea state 4 and bergy bits from 5 (estimates; the growler range is sourced).
- `IcebergField.SonarFalseContactIndex` and `FalseContact`: a 0-1 **design index**, not a probability. The flag is the index at or above 0.5 (a game rule).
- With `IceFeaturesDiagnostics=1` the log gives these numbers for the nearest berg.

## What is tested, and what is not

Tested here (`python3 build_drop_in.py`, about 7,000 checks):

- Containment on the simplified rings equals `ice.IceShelf.contains` on the same rings.
- Front distance equals `iceshelves.distance_to_front_nm`. The navigation status equals `shelf_navigation`.
- A hull driven at 30 kn toward the Ross front stops at its limit, surface and submarine. The surface ship's bow stays seaward of the front.
- No invented inputs: an unreadable date gives no bergs; an unbound clock gives static bergs.
- Density, fractional month, radar, visual, sonar, melt and the drift step equal the Python values.
- The generator gives the same bergs as `icebergs.generate`.
- Berg meshes are closed and face outward. Cliff faces point to sea.
- Against stub game types: the switches, fail-closed install, the patch target, the postfix on own and AI units, the drawn objects, drift, melt and clean-up.

**PC-untested:**

- Every Sea Power member binding. The names come from how r16's `SeaIceBattle.cs` and `SeaIceSheet.cs` use them (Sea Power 0.9.3 Build 261123). The stubs do not prove the real members exist. A missing member logs one line and leaves that part out.
- Harmony with `object __instance` in the postfix.
- Which shader loads, and how the cliffs and bergs look in game light and fog.
- Scale and placement against the real `longLatToLocalV3`, and behaviour when the floating origin moves.
- Bergs do not ride Ceto's waves. They sit at sea level.
- Performance with many units near Antarctica.
- AI units ordered into a front stop there. They are not re-routed.
- Bergs are not radar or sonar contacts, and they have no collision.
- Bergs and r16's sea-ice sheet overlap: the sheet is not cut around a berg.
- The coarse land rings may put a berg in a narrow fjord that the game draws as land. Small islands can be missing too.

## Regenerating the data

```bash
python3 integration/environment/tools/make_ice_features_data.py          # write
python3 integration/environment/tools/make_ice_features_data.py --check  # verify, no writes
python3 integration/environment/runtime-drop-in/ice-features/build_drop_in.py --check-data
```

`IceFeaturesData.g.cs` stamps the SHA-256 of every input file. That includes `icebergs.py`, `iceshelves.py`, `ice.py` and `geo.py`, so any change to them makes `--check` fail until the data is regenerated.

## References

Data:

- Natural Earth 1:10m `ne_10m_antarctic_ice_shelves_polys` and `ne_10m_antarctic_ice_shelves_lines`, public domain, naturalearthdata.com. Low-resolution land rings: Natural Earth, public domain.
- Morlighem, M. et al. (2020). BedMachine Antarctica, NSIDC-0756, doi:10.5067/E1QL9HFQ7A8M. Ice 917 and sea water 1027 kg/m3.
- USGS ROSETTA-Ice: Ross front freeboard 15-50 m. Rignot, E. et al. (2013), Science 341:266, shelf areas.
- International Ice Patrol (2024), North Atlantic Iceberg Summary: bergs crossing 48N by month. IIP data: NSIDC G10028, doi:10.7265/z6e8-3027.
- Size classes: IIP scale, NOAA JetStream "Icebergs" (https://www.noaa.gov/jetstream/icebergs-max). Environment and Climate Change Canada MANICE (2005), chapter 1, differs slightly for medium to very large bergs.
- Tournadre, J. et al. (2016), JGR Oceans 121:327-349: small iceberg limit (8 km2) and distribution.

Methods:

- Bigg, G. R. et al. (1997), Cold Regions Science and Technology 26:113-135; Martin, T. and Adcroft, A. (2010), Ocean Modelling 34:111-124: melt rates (coefficients recalled, medium confidence).
- Garrett, C. et al. (1985) and Smith, S. D. (1993): about 2 % wind drift. Wagner, T. J. W., Dell, R. W. and Eisenman, I. (2017), arXiv:1610.06403: large keels follow the deeper current.
- Bowditch, The American Practical Navigator (2019), Vol. 1, Appendix B: distance to the horizon 2.07 sqrt(h_m) nm, so geographic range 2.07 (sqrt(eye) + sqrt(height)) nm.
- Canadian Coast Guard ice hazard radar paper: growlers about 0.5 nm or not at all on conventional radar.
- Douglas, D. H. and Peucker, T. K. (1973), Cartographica 10(2):112-122: line simplification.
- Matsumoto, M. and Nishimura, T. (1998), ACM TOMACS 8(1):3-30: the Mersenne Twister. CPython `Modules/_randommodule.c` and `Lib/random.py` for seeding, `random()` and `gauss()`.

Every number in the two JSON files carries its own source and confidence. Read `docs/environment/ICE-SHELVES.md` and `docs/environment/ICEBERGS.md` before you trust a number.
