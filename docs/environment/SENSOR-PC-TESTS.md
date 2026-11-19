# Sensor environment: what the game does, what we derive, and the owner's PC tests

Status: BUILD-TESTED. Nothing here is IN-GAME TESTED. A row becomes "PC-observed on build X" only when the owner records it
in ENV-TEST-RESULTS.md.

## What the game itself does (from its files)

The source is `mods-source/_vanilla/original/environment.ini [Sonar]`, from the 0.9.0 export. Your installed 0.9.3 may
differ: test BEFORE records it.

- **Passive ambient:**
  - The base is `BaseAmbientOceanNoise=60` dB, plus `PerSeaStateNoise=5` dB for each SeaState step.
  - `RainNoise=15` dB is added whenever Weather=Rain is on.
  - So the mission's SeaState and Rain keys are already the game's main weather-to-sonar levers, and MNO already sets
    both.
- **Convergence zones:**
  - They appear at 30 and 60 nm, each 10 nm wide, wherever the water is deeper than 3000 ft.
  - The SOFAR axis is at 800 m.
- **Thermal layer:** cross-layer loss is 6 to 12 dB. The file lists "Floe Ice, Xlayer Attenuation, Surface Duct" as
  variable, meaning the game computes them itself.
- **Radar, IR and visual:** weather affects them inside the game code. No file setting is known, so missions reach them
  only through the weather keys: Clouds, SeaState, Rain, Fog, Thunderstorm.

## What MNO now derives (planning only)

`mno_env/sensors.py` derives the following from a weather sample, a place and a date:

- **Sonar:**
  - mixed-layer depth and layer class;
  - sound absorption (Francois-Garrison), sea-ice and shrimp noise;
  - surface-duct cutoff;
  - real-world convergence zones per theatre;
  - suggested BaseAmbientOceanNoise and RainNoise for a per-mission override.
- **Radar:**
  - evaporation duct and the bands it traps;
  - rain loss per band (ITU-R P.838-3);
  - NRL sea clutter;
  - multipath.
- **EO and IR:**
  - IR range factor;
  - moon phase, altitude and lux;
  - sun altitude;
  - cloud base.

`tools/build_sensor_brief.py` turns these into the "GCO Sensor Weather" page for the five GCO theatres. Every line is
tagged:

- GAME: what the game applies.
- REAL-WORLD: a planning note the game does not model.
- UNTESTED: a [Sonar] value that nothing writes yet.

One mission-side change is already active. `Weather=Rain` now needs 0.5 mm/h to switch on and clears below 0.3 mm/h. The
reason: the game adds a flat 15 dB to passive ambient whenever it rains, and drizzle flicker should not toggle that. The
0.2 mm/h gate for snow and thunderstorm is unchanged.

## Owner PC tests (not run)

Use test copies of missions only. Record one line per row as "PC-observed on build X: ...". Report only what you observe.

| Row | What to do | What it decides |
|---|---|---|
| BEFORE | Note the build string. Copy `StreamingAssets/original/environment.ini` to Downloads\env-backup and record its SHA-256. Note whether Options > Gameplay > "Restrict air ops by sea state" is on. | The base for everything else |
| W5 | In the Weather Lab Hormuz copy, set SeaState 3, 6 and 9 (then 12 if stable). At each value, record the visible wave height, the "Ocean Noise" value in the weather panel, whether an OHP helicopter is refused launch, and whether a Kaivan FAC loses pitch above 4. | Whether the game's SeaState is a wave-height code (what MNO assumes) and whether noise clamps at 8 |
| RAIN | Deep water, night, radar off, a submarine or a loud merchant. Find the first passive detection range with Rain off, Rain on, and Thunderstorm alone. Fire Action_SetRain mid-mission. | Whether RainNoise is applied as written and follows triggers |
| FOG | A small boat closing, Fog off and on. Record the first visual or optical detection range, helicopter launch, and bombing accuracy. | What Fog actually does to sensors |
| LAYER | Water deeper than 1000 m. Read the "Layer" depth. Put the submarine 30 m or more below it under a frigate at 8 nm, with LayerDisabled False and then True. | Whether LayerDisabled is a safe lever for well-mixed seas |

The rows below test the 0.9.x per-mission file layers. They need the probe packages from the next build step
(`tools/probe_file_layers.py`, not written yet), and each row runs only if the one before it passed.

| Row | What to do | What it decides |
|---|---|---|
| A | Install a user-level language probe and look for the changed string. Uninstall it. | Whether file layers work at all |
| A2 | Install a probe that renames one F-14A squadron. Check whether the other squadrons survive. Retest after a cold restart before calling it negative. | Whether layers merge by key, by section or as a whole file |
| B | Try one per-mission folder convention at a time beside the Weather Lab mission. Then load a vanilla mission in the same session and check it is unchanged. | Where a per-mission layer goes |
| C | Put a [Sonar]-only file with the sentinel `BaseAmbientOceanNoise=90` in the per-mission location. Deep water, sea state 3, a loud merchant closing from 15 nm: the passive range should fall sharply. Before that, check Player.log for errors. Afterwards, check night lighting, sky, sea and fog. If any of those changed, the layer replaced the whole file: delete it at once. | Whether environment.ini can be layered per mission |
| D | As C, but with a full copy of your installed environment.ini. | The fallback if C replaces the whole file |
| L | After C or D, without restarting, load a vanilla deep-water mission. Detection must be normal there. | Whether a per-mission value leaks into the next mission |
| E | In water deeper than 4000 m, set ConvergenceZoneDist1 to 40: the zone should move out about 10 nm. Set MinDepthForConvergenceZones=20000: zones over 2 km water should vanish. | Whether realistic values are visible in play |
| COLLECT | Run `RUN-WEATHER-LAB.ps1 -CollectLogs`, take screenshots, and write one line per row in ENV-TEST-RESULTS.md. | |
| ROLLBACK | Delete every probe file from its manifest. Check that the environment.ini hash equals the backup and that no overrides/ folder is left in user/. Restart. Use Steam "verify integrity" only if the hash differs. | |

The untested suggestions now cover BaseAmbientOceanNoise, RainNoise, Min/MaxXLayerAttenuation, AbsorptionFactor,
SofarAxisDepthM, MinDepthForConvergenceZones (disable where the water is deep but there are no real zones) and
LayerDisabled. Until rows A, A2, B, C (or D) and L pass, MNO writes no per-mission [Sonar] file. The suggested values stay as
"UNTESTED" lines in the brief.

## Unknowns the tests answer

- The per-mission layer folder: its name, its location, whether environment.ini is allowed, and how files merge (by key,
  by section or as a whole file).
- Whether [Sonar] is read at startup, at mission load or on every query, and whether a value survives into the next
  mission.
- Whether the game's SeaState is a wave-height code or a Beaufort force, and what 10-12 look like.
- What else Weather=Rain and Fog change: radar clutter, visual and IR range, bombing.
- Whether LayerDisabled also removes the shadow zone and surface duct.
- Whether civilian merchants raise the ambient floor or only add contacts.

## Sources and limits of the derived values

- The theatre table in `sensors.py` holds shipping, depth class, convergence zones, humidity and air-sea difference. It
  is hand-set from public summaries: AIS traffic density maps, standard bathymetry, the ocean-acoustics texts cited in
  the module.
- It is approximate climatology for planning. It is to be replaced by an ERA5- and WOA23-derived table, built on the
  owner's PC. Open-Meteo is out of quota here.
- The evaporation duct uses a simplified bulk method, about 30 % low in hot, humid, unstable air.
- Mixed-layer depth and layer class are low-confidence seasonal fits.
- The game computes its own layer: its depth readout governs.
