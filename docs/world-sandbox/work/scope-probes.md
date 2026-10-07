# In-game probe set: world scope, scale and persistence

Probes are opt-in measurement files. They answer what the repository cannot. Each probe asks one question and gives an observable pass/fail. Each also says how its result changes the world build: one mission, a hybrid, or linked regional missions. Nothing here was run in game. Tags: **[GAME]** engine or stock data, **[BUILDER]** SEST tooling, **[UNMEASURED]** no evidence either way.

## What the evidence already settles, and what it leaves open

- **Settled [GAME]:** units 8,000–12,000 file units (up to ~8,240 NM) from MapCenter have loaded, run and been saved. NORTHERN FRONT III FINAL proves this (`data/install-snapshot/saves/New midgame.sav`), and so does stock content (`Strawberries Can Kill (Red Side).ini:73`, 12,160 file units). RelativePositionInNM is arcminutes on both axes, with z positive north. GeoPosition is also supported (`MissionFileInformation.ini:436-440`).
- **World extent needed (scratch calculation, anchor coordinates approximate):** the best single centre is about 42N 20E. From there all 22 project anchors lie within about **7,000 NM** great-circle, with max |x| ≈ 10,700 and |z| ≈ 5,600 file units. That is already inside the proven range. So P1 checks accuracy, behaviour and cost at distance. It does not ask whether far placement can be written.
- **Open:** whether far-off regions keep simulating while the camera is elsewhere. Also open: behaviour across ±180, real active-unit cost, idle airbase cost, save/reload state fidelity, and the distance metric at high latitude.

### Findings from this pass (new evidence, used below)

1. **[GAME] The save `[PlottingTable] Payload=` can be decoded.**
   - Method: replace `{/}` with `//`, base64-decode, then gunzip. The result is a Unity DOTS `EntityBinaryFile`. For `NORTHERN FRONT MIDGAME III.sav:21926-21927`, 13.2 MB of text expands to 172.6 MB.
   - Type-name strings: `ESMContact` 37,353, `RadarContact` 5,691, `PassiveSonarContact` 1,745, `VisualContact` 1,652.
   - `New midgame.sav`: 55,086 / 17,711 / 1,884 / 1,990.
   - The 37-unit `Carrier 1v1 Coby…sav`: 9,775 / 9,628 / 0 / 1,456, in a 5.7 MB file.
   - Inference: save size follows the sensor-contact picture (emitters × ESM receivers), not unit count. `config.ini:8 SaveLoadSensorDataEnabled=True` fits this. **P4 must therefore vary radar emission.**
2. **[UNMEASURED] Saves may depend on a base file.** All three mid-mission saves say `BaseFile=missions\_temp\_TempMission.ini` (line 5). That editor temp file has since been overwritten (it now holds NF III FINAL NEWEST). Whether a reload depends on BaseFile is unknown.
3. **[GAME] A stock dormancy mechanism exists.** A unit can start with `Disabled=True` and be woken by a trigger with `Action_SetEnabledStatus=True` (`Campaign Scenarios/Pacific Strike/01A Senkaku Run.ini:583`, `:720`). Stock uses it on 43 aircraft, 7 helicopters, 1 vessel (`Tutorials/Officer_Training_1.ini:88`) and 1 submarine (`pacific-strike-task-force/missions/07 Action in the Java Sea.ini:442`). It is never used on land units. Its cost is [UNMEASURED].
4. **[GAME] Saves store per-system state that P6 can diff.** Examples: `CurrentIntegrity` (`NORTHERN FRONT MIDGAME III.sav:183`), `FloodingCompartments` (:674), `Ammunition1_Count`/`_InitialCount` (:257-258), and supplier stock `AmmoCapacity=200000` / `CurrentAmmo=193820` in `[Taskforce2LandUnit8SupplySystem6]` (:9458-9469).
5. **[BUILDER] Ships need the SEST Replenishment pack to resupply other ships.** Stock `vessels/usn_aoe_sacramento.ini:303-319` has its supply block commented out. The working block is SEST's: `integration/replenishment/SEST_Replenishment/vessels/usn_aoe_sacramento.ini:304-314` (TruckSupplySystem, AmmoCapacity 600000, SupplyRange 1.0 NM, MaxOwnVelocity 13, MaxTargetVelocity 16).
6. **[BUILDER] Correction to the builder-limits lens: the Diego Garcia lagoon reads as water.** I tested four lagoon points (e.g. -7.35, 72.43) against the scratch global Natural Earth extract and against raw `ne_10m_land` ray-casting. All read water: Natural Earth draws Diego Garcia as a C-shaped 27-point rim, not a filled disc. Hood Canal (47.73, -122.72), Kola Bay at Severomorsk (69.07, 33.42) and Apra inner harbour (13.44, 144.66) do read as land.
7. **Guam–Hainan is 2,057 NM**, not about 1,800. That is great-circle Andersen–Yulin; by sea via the Bashi Channel it is about 2,180 NM.

---

## Rules common to every probe

- **Opt-in and never deployed.**
  - Keep probe files out of `integration/missions/`. `tools/install-sest-packs.ps1:143-183` copies every `.ini` there, recursively, into the game.
  - Keep them out of `integration/dist/` and out of the builder's position pool (`integration/campaign/build_pack.py:751-754` POOL_ROOTS). Untested positions must not become "proven points".
  - Suggested home: `docs/world-sandbox/probes/`, with filenames prefixed `ZZ PROBE`. The user copies a probe by hand into `<StreamingAssets>\user\missions\user_missions` (path from `install-sest-packs.ps1:155`) and deletes it afterwards.
  - Do not let a later snapshot carry probe files into `mods-source/_vanilla/user/missions`, which is also a pool root.
- **Generate the files with a standalone script, not `build_pack.py`.** Its output is hard-wired to `SEST_Campaign` and it rewrites pack files (`build_pack.py:68`, `:6246-6259`). The script should also write an `expected.json` (intended lat/lon per unit, expected arrival times) so the captured saves can be scored automatically.
- **Preflight cannot see these files.** `tools/preflight.py:262-271` only finds missions in `integration/missions` or `integration/campaign`. Either copy `Type=` lines from missions that already load, or add a path argument to preflight [BUILDER].
- **Placement maths:**
  - `x = (lon − MapCenterLongitude) × 60`
  - `z = (lat − MapCenterLatitude) × 60`
  - z is positive north. The stock comment at `MissionFileInformation.ini:443` has the sign backwards.
  - Normalise longitudes to ±180, except where P3a tests otherwise.
- **Unit content:** stock unit types only, except P6. Run P4 and P5 twice:
  - with BepInEx code mods disabled, as the engine baseline;
  - with the full current install.

  Two known code-mod exception floods would otherwise distort the results: PLA AEP per-tick logging (build-notes 1331-1352) and the CV16 `_isInFlight` flood of 6,398 exceptions.
- **Keeping idle probes idle:** set `[Debug] AllowEnemyUnitsAttackPlayer=False` (`MissionFileInformation.ini:32`) and `WeaponStatus=Hold`. Otherwise the engagement limits on time compression (`changelog.txt:5121`) skew the measurements. `AllowControlOfEnemyUnits=True` (:19) helps when inspecting Red units.
- **Launching:** start from the mission list, not the editor test button. Record each save's `BaseFile=` line.
- **Record sheet (every run):**
  - game build (the changelog says 0.8.4 Build 261002, `changelog.txt:6`); repo commit; mod list and load order (`tools/capture-context.ps1`); BepInEx on or off
  - CPU and RAM (still unknown) and GPU (RTX 2070 SUPER, 8 GB, `player-prev.log:15-17`); resolution and graphics preset
  - **load time:** stopwatch from clicking Start to the first controllable frame
  - **FPS:** overlay average over 60 s
  - **effective time compression:** game minutes advanced in 2 real minutes ÷ 2, at nominal 20x and 100x. Note any cap the HUD imposes (`config.ini:13 MaxTimeCompression=100`).
  - RAM and VRAM; the count of "Exception" lines in Player.log
  - save duration, `.sav` size, Payload length, and the decoded contact counts
- **Saves:** `capture-context.ps1 -IncludeSaves` copies only the 6 newest saves, campaign saves first (`:318-331`). Capture straight after each probe, or copy saves by hand.
- **Performance logging:** use `config.ini:3 EnablePerformanceLogging=True` only in a separate pass. The changelog says it adds garbage-collection overhead (`changelog.txt:5302`), so never compare FPS between logged and unlogged runs. Note where its output appears, and revert config.ini afterwards.

---

## Summary

| ID | Question | Decides | Order |
|---|---|---|---|
| P0a | Do the existing mid-mission saves reload on 0.8.4, and do they depend on BaseFile? | Whether saves can carry persistence | 1 |
| P0b | How do the existing large missions (241 to 974 units) load and run? | Starting step for P4 | 1 |
| P1 | Is a unit placed 250 to 10,000 NM from MapCenter correct and live? | Single origin, yes or no | 2 |
| P3a | Do units coexist and cross at ±180? | The only engine fact that could force a Pacific split | 2 |
| P3b | Are 69N and 52S placement and terrain correct? | Usability of Kola and Falklands | 3 |
| P2 | Do two theatres 2,057 NM apart both simulate and interact? | Simultaneous theatres in one mission | 3 |
| P6 | Does save/load preserve damage, magazines, supplier stock and event state? | Persistence vehicle | 4 |
| P4 | How do load time, FPS, effective time compression and save size scale with unit count? | Population budget; need for dormancy | 5 |
| P5 | What do aircraft parked at airbases cost compared with airborne aircraft? | Airbase inventory policy | 5 |
| P7 | Does the engine measure distance in true NM or in file units at high latitude? | Builder geometry (not architecture) | 6 |
| P8 | Does game terrain have water where Natural Earth draws land? | Builder water handling (not architecture) | 6 |

---

## P0a – Reload existing saves (no authoring)

- **Question:** do `New midgame.sav` (22.8 MB, 298 units, 30 weapons in flight) and `NORTHERN FRONT MIDGAME III.sav` (14.0 MB) reload on 0.8.4? Does reload depend on the overwritten `_TempMission.ini`?
- **Procedure:**
  1. Load each save and time it.
  2. Without unpausing, save as `P0a-<name>-reloaded`.
  3. Unpause for 5 game minutes and save again.
- **Record:** load time; unit count; airborne aircraft and weapons in flight against the original; FPS; effective time compression. Then diff the unit sections of original and reloaded saves, excluding Payload and timestamps.
- **Pass:** loads; unit sections match (GeoPosition within 0.01 NM; integrity, ammunition and supply keys identical); simulation continues. **Fail modes:** refuses to load; loads content from the other mission (shows a BaseFile dependency); state drifts.
- **Effect on the world build:**
  - Pass: mid-mission saves are a working persistence vehicle at about 300 units.
  - A BaseFile dependency means the world mission file must be versioned and frozen for each save generation, never edited in place. That applies to any architecture.

## P0b – Existing large missions (no authoring)

- **Missions:** NORTHERN FRONT III FINAL (241 units plus about 546 based aircraft), SEST Banda Front EDITED (857), SEST Indo-Pacific Land Assets (974). The last two have no simulation record.
- **Record:** the common sheet, over 10 game minutes. Then save and record the save size.
- **Pass:** loads in under 10 minutes and stays responsive. **Fail:** a hang (note the last line of Player.log), a crash, or an unusable frame rate.
- **Effect on the world build:** this sets P4's starting step. If 974 runs well, P4 starts at 600/1000. This is real content and complements P4's synthetic cells.

## P1 – Distant placement ladder

- **Question:** does a unit at 250 / 1,000 / 3,000 / 6,000 / 10,000 NM from MapCenter spawn at the correct latitude and longitude, over correct terrain or water? Does it stay live while unobserved?
- **Setup:**
  - Centre **0.0, -30.0** (open equatorial Atlantic, away from 0,0). On the equator one x unit equals one true NM, so this probe tests distance separately from latitude distortion, which P7 covers.
  - Land and sea at each rung come from the scratch Natural Earth check:

    | Rung | File offset | Lat, lon | Surface |
    |---|---|---|---|
    | E250 | x=250 | 0, -25.83 | sea |
    | E1000 | x=1000 | 0, -13.33 | sea |
    | E3000 | x=3000 | 0, 20.0 | land (DRC interior) |
    | E6000 | x=6000 | 0, 70.0 | sea |
    | E10000 | x=10000 | 0, 136.67 | sea, 63 NM off New Guinea |
    | N250 | z=250 | 4.17, -30 | sea |
    | N1000 | z=1000 | 16.67, -30 | sea |
    | N3000 | z=3000 | 50, -30 | sea |
    | N4800 | z=4800 | 80, -30 | land (Greenland ice) |

  - At every rung:
    - one aircraft at 25,000 ft with a 20 NM waypoint. Aircraft do not depend on terrain, and 25,000 ft clears the ice sheet.
    - one ship if the rung is water: Telegraph slow, `Waypoints=Course,90/90,20,0` (`MissionFileInformation.ini:492`).
    - one land unit with height `low` if the rung is land.
    - a **GeoPosition twin** of the ship or land unit, 2 NM north (`:436-440`).
  - **Variant B:** identical world positions, with MapCenter moved to the E10000 rung and x/z recomputed. This is the A/B test for the "best performance" tooltip (`ui.ini:1256`).
- **Procedure:**
  1. Load (stopwatch) and pause.
  2. Visit every rung: take a screenshot and measure FPS at 1x for 30 s.
  3. Park the camera at the centre, run 30 game minutes at 20x and save.
  4. Park the camera at E10000, run 30 minutes and save.
  5. Repeat for Variant B.
- **Record:** saved GeoPosition against intended, for each unit; saved altitude of land units; ship displacement during the period the camera was away; FPS per rung; load time A against B.
- **Pass:**
  - every unit spawns within 0.1 NM of its intended position (NORTHERN FRONT showed 0.001 NM);
  - relative and GeoPosition twins agree;
  - ships sit on water and land units have non-zero altitude;
  - unobserved units advance the expected distance ±5%;
  - nothing jumps when the camera moves;
  - FPS at far rungs is within 10% of the centre rung.

  Fail is recorded per rung, which gives a measured distance threshold.
- **Effect on the world build:**
  - Pass out to 7,000 NM or beyond: one origin can hold the whole world, and regions are only an authoring convenience.
  - Fail beyond distance D, with D under 7,000: partition so that no unit is farther than D from its mission centre. The number of missions follows from D, not from an assumption. Also check whether the GeoPosition twin fails the same way.
  - B materially faster than A: place the world centre where play concentrates.

## P2 – Two theatres in one mission (Guam and Hainan)

- **Question:** can both theatres operate at once (patrols, sorties, recoveries) while the camera is in the other one? Do AI routes and air sorties work across the 2,057 NM gap?
- **Setup:**
  - Centre **A** is the midpoint, 15.83, 127.10 (about 1,020 NM to each theatre). Centre **B** is the editor default, 54.27, -26.28 (the NORTHERN FRONT case).
  - **Guam (Blue):**
    - `airfield_small_1` at Andersen, using the stock position and air-group pattern from `NATO/Showdown off Guam Blue 1985.ini:504-515` (`usaf_b-52g`, `usn_p-3c`, `usaf_f-4e`);
    - two surface combatants on a 4-waypoint box off Apra;
    - a neutral merchant routed Apra → 16N 130E → 21N 121E (Bashi Channel) → 18.5N 119E → 18.10N 109.60E. All legs are open water by the scratch check, about 2,180 NM.
  - **Hainan (Red):**
    - an airfield at Yulin. Stock options: `airfield_small_1` (`PLAN/PLAN 02 Battle of the South China Sea.ini:507`) or `wp_airbase_4` (`pacific-strike-task-force/missions/10 Vengeance at Luzon.ini:1100`), with `pla_h-6d` and `pla_j-7c` groups;
    - two surface ships on a patrol box off Yulin.
  - **Cross-gap traffic:**
    - (i) a Blue B-52G, airborne, `HomeBase` = Andersen, waypoints to a point 100 NM south-east of Yulin and back;
    - (ii) a Red H-6D, airborne, `HomeBase` = Yulin, flying to 150 NM west of Guam and back;
    - both with `UnlimitedFuel=True`, a stock key (`changelog.txt:1226`), so fuel range does not decide the result;
    - (iii) at t=30 min, a trigger with `Action_AirStrike=Bomb`, `Action_AirStrikeSources` = the Hainan airfield and `Action_Units` = the Blue ships off Apra (pattern: `NATO/Hormuz.ini:411-421`).
  - **Instrumentation:** `UnitsInTheArea` triggers (pattern: `Warsaw Pact/Breakthrough.ini:831-834`, `UnderCoverOfTheRain.ini:577-584`) that post messages with game time. One sits on each Red patrol waypoint (radius 3 NM), one on the Yulin approach and one on the Guam approach (radius 30 NM).
- **Procedure:**
  1. Keep the camera at Guam for 3 game hours at 20x, **never visiting Hainan**, then save S1.
  2. Move the camera to Hainan, run 2 more hours and save S2.
  3. Reload S1 and compare.
  4. Optional: run the merchant's full transit at 100x, about 73 real minutes at 18 kt.
- **Record:** message times against expected (distance ÷ the ground speed the UI shows); saved positions; landings (LastLaunchTime, airborne count); whether the strike launched, when, and by what path; any jumps on camera switch; FPS per theatre; differences between A and B.
- **Pass:**
  - the unobserved Red patrol logs every waypoint on schedule ±10%;
  - cross-gap aircraft arrive within ±10% and return to land;
  - the strike either launches and transits, or a clear game refusal appears (e.g. `RebaseTooFar`, `ui.ini:4159`), which is recorded as a range rule;
  - no teleports;
  - S1 reloads faithfully.
- **Effect on the world build:**
  - Pass: theatres coexist in one mission.
  - The unobserved theatre freezes or desynchronises: the engine only simulates near the camera. That rules out simultaneous persistent theatres in one mission and points to a hybrid (one active theatre, others dormant through `Disabled=True` and triggers) or to linked missions.
  - Only cross-gap AI routing fails: keep one mission and move forces between theatres by trigger hand-off (despawn at a gate, spawn at the destination). That is builder work, not a split.

## P3a – Antimeridian (±180)

- **Question:** do units on both sides of 180° coexist (detection, terrain, no relocation loop), and can they cross? Which longitude convention does the engine accept?
- **Setup:** centre **30.0, 178.0**, open ocean.
  - **East-side ship** at 179.9E (x=+114), with three eastbound twins 2 NM apart:
    - `E-course`: `Course,90/90,120,0`
    - `E-unwrap`: explicit waypoint x=+234 (lon 181.9)
    - `E-norm`: explicit waypoint x=-21,366 (lon -178.1, the convention the EUROMOD mission uses)
  - **West-side spawn twins** at 179.9W, 2 NM apart:
    - `W-norm`: x=-21,474
    - `W-unwrap`: x=+126
    - `W-geo`: `GeoPosition=30.0,-179.9,0`
    - plus one westbound ship with a Course waypoint
  - **Detection pair:** a Blue ship east of the line and a Red ship west of it, 10.4 NM apart, radars on, weapons Hold. A **control pair** sits at 170E, 10 NM apart (12 file units at 30N).
  - **Terrain:** land units with height `low` at Amchitka (51.38, 179.26) and Adak (51.88, -176.65), 155 NM apart either side of the line.
- **Procedure:**
  1. Follow `E-course` across the line with the camera.
  2. Pan the camera between Amchitka and Adak.
  3. Save while a unit straddles the line, then reload.
- **Record:** spawn errors for each twin; the path each crossing ship takes (does E-norm sail the long way round?); saved longitude after crossing; time to detection against the control pair; Amchitka and Adak altitudes; camera or unit jumps or an FPS collapse (the relocation loop in `changelog.txt:4380`); reload accuracy.
- **Pass:** all spawn variants within 0.1 NM (or a recorded list of which convention works); crossers take the short path and keep continuous positions; detection matches the control pair; both Aleutian units have plausible altitude; no loop; reload is faithful.
- **Effect on the world build:**
  - Full pass: one mission can span the Pacific, including Hawaii and the US West Coast. The builder must emit the convention that worked and add longitude wrap to `nm_between` (`build_pack.py:816-819`), `sea_routes.py:155-160` and `briefing_maps.py:171-185` [BUILDER].
  - Units coexist but cannot cross: keep one mission, and handle transpacific transits by gateway triggers at the line.
  - Units cannot even coexist: this is **the only result that would force a regional split on engine grounds**. Theatres east of 180 (Hawaii, Midway; the US West Coast if its routes must cross) would become a linked mission.

## P3b – High latitude and southern hemisphere

- **Question:** are placement, terrain and movement correct at 69N and 52S?
- **Setup:** two small files with local centres.
  - **Kola**, centre 69.6, 35.0: ships in open Barents water (19 NM offshore); a land control at the stock `wp_airbase_4` position (`NATO/Northern Vigil.ini:398`); a land unit with height `low` at the Severomorsk airfield.
  - **Falklands**, centre -51.7, -58.0: a land unit with height `low` at Mount Pleasant (-51.823, -58.447); ships east of Stanley (-51.70, -57.50, 8.7 NM offshore); an aircraft in orbit. No stock unit lies within 959 NM of the Falklands, though the biome exists (`terrain/biomes.ini:5`).
- **Record:** spawn error; land altitude; a screenshot of the terrain; ship movement.
- **Pass:** within 0.1 NM; plausible altitude; island visible; ships float and move.
- **Effect on the world build:** a pass needs no special handling. Missing Falklands terrain is a gap in the game's data. Splitting missions would not fix it, so the Falklands would be sea-only or off-map.

## P4 – Population scale

- **Question:** how do load time, FPS, effective time compression, save size and reload fidelity scale with placed-unit count? Is the cost driven by count, by spread, or by radar emission?
- **Setup:**
  - Stock types only, built from a fixed **50-unit cell** so each step is linear:
    - 20 land units: SAM/radar sites, depots and vehicles, placed at land points that stock missions have already used near each cluster, e.g. `Dangerous Straits 1985.ini:644` (Souda) and `04 Chagos Gambit.ini:483` (Diego Garcia);
    - 15 ships: 8 anchored, 7 on 2-waypoint loops at 12 kt;
    - 5 submarines on slow patrol;
    - 6 aircraft airborne on racetracks with a HomeBase;
    - 4 neutral merchants on long routes.
  - Weapons Hold, and `AllowEnemyUnitsAttackPlayer=False`.
  - Steps: **50 / 150 / 300 / 600 / 1000**. 1000 brackets the 974-unit file.
  - Centre: the candidate world centre, 42, 20.
  - **Variants:**
    - **S-quiet:** cells spread over 6 clusters (Norwegian Sea, East Mediterranean, Arabian Sea, Diego Garcia, Timor Sea, Philippine Sea); radars off except one SAM radar per cluster. Run every step.
    - **S-emit:** the same, with all radars on. Run at 300 and at the last step that passes S-quiet. This tests the contact picture behind finding 1.
    - **C-quiet:** the same count in a single cluster. Run at the last passing step and the first failing step.
    - **D-dormant:** 1000 units, 80% of them `Disabled=True`, compared with 200 active. Include a small land-unit subset, because stock never uses this flag on land.
  - Optional: set `MaxTimeCompression=200` once and check whether the HUD offers it, then revert.
- **Record:**
  - the common sheet, at each step;
  - a save at T+30 min and another at T+4 h of game time at the same population (does Payload grow with time?);
  - reload, then an immediate re-save to check unit count and key fidelity.
- **Proposed acceptance thresholds** (the user's playability choice, not engine facts):
  - loads without a hang over 10 minutes;
  - 30 FPS or more at 1x at the busiest cluster;
  - effective time compression of at least 50x when 100x is selected;
  - a save takes 60 s or less, and the reload has an identical unit count.

  The highest passing step is **N\***. Classify it as GAME-on-this-PC, not as an engine limit.
- **Effect on the world build:**
  - N\* is at or above the register's active world population: one mission.
  - S fails at a count where C passes: spread itself costs something; reduce the regions per mission (hybrid), sized by measurement.
  - S and C fail at the same N: the cost is unit count, not geography. Regional missions only help if each region stays under N\*.
  - D-dormant is cheap: **hybrid single mission**. The world stays populated but dormant, and forces are enabled by trigger per operation.
  - S-emit is far costlier or produces much larger saves than S-quiet: emission discipline (radars off when idle) becomes a world-wide authoring rule.

## P5 – Idle airbase cost

- **Question:** what do aircraft parked in airbase air groups cost, compared with empty bases and with the same aircraft airborne?
- **Setup:** 6 stock airbases at stock-used sites (Andersen, Souda, Diego Garcia, Kola, Yulin, plus one more), using `airfield_small_1` / `wp_airbase_4` (format: `MissionFileInformation.ini:401-410`).
  - **A:** no custom air group (record what each base spawns with by default).
  - **B:** about 100 parked aircraft per base, 600 in total. NORTHERN FRONT III loaded with 546–634.
  - **C:** 500 parked, plus 100 placed as airborne aircraft with `HomeBase`, flying CAP racetracks.
- **Record:** aircraft accepted against requested per base (a capacity rule, [GAME]); the common sheet; any aircraft the AI launches unprompted in the first 60 game minutes; parked counts and CAP behaviour after save and reload (`config.ini:9 SaveLoadFlightDeckEnabled`; `changelog.txt:49` fixed CAP after reload).
- **Pass:** B costs at most 10% more FPS and time compression than A, and loads at most 30 s slower; parked counts are identical after reload; no unprompted mass launches.
- **Effect on the world build:**
  - Parked aircraft are cheap: populate world airbases at full inventory in one mission. Only sorties cost anything.
  - Parked aircraft are expensive: inventory becomes the scale driver. Keep inactive regions' inventories as roster data (the stock theatre roster and Dynamic Unit Generation, `changelog.txt:344-349`) and create them when a region activates. That is a hybrid, not a regional split.

## P6 – Save/load fidelity of combat and supply state

- **Question:** do damage, flooding, expended magazines, supplier stock, ongoing transfers, losses and trigger state survive a save and reload without resetting, duplicating or re-rolling?
- **Setup:**
  - Local scene. The SEST Replenishment pack is required (finding 5).
  - `usn_aoe_sacramento` with the SEST supply block, alongside a receiver whose round `tools/check_reloadable.py` reports as reloadable. Keep both within SupplyRange and the speed limits (`:308-311`).
  - A target ship damaged by an enemy `Attack=` entry with a fixed shot count at t=60 s (`MissionFileInformation.ini:505-512`).
  - A shooter that expends a known salvo.
  - One unit destroyed by `Action_DestroyUnits` at t=30 s (`:737`).
  - One trigger message that has already fired, and one pending at t+2 h.
  - An airbase with one parked group and one aircraft mid-sortie.
- **Procedure:**
  1. Start a transfer. At T1, mid-transfer, save S1 and note the on-screen damage, ammunition and supply panels.
  2. Quit and restart the game, load S1, and save S2 at once while paused.
  3. Unpause for 5 minutes and save S3.
  4. Then edit the base mission in the editor and try S1 again (the BaseFile test).
- **Compare:** the S1 and S2 keys from finding 4, plus GeoPosition, Heading and VelocityInKnots, IsDestroyed and unit counts, LastLaunchTime, and `FlightDeck_*` keys.
- **Pass:**
  - S1 equals S2;
  - in S3 the supplier's `CurrentAmmo` keeps falling from its S1 value and the receiver's count keeps rising;
  - the destroyed unit stays destroyed;
  - the fired trigger does not fire again and the pending one fires once;
  - S1 is unaffected by the base-file edit.
- **Effect on the world build:**
  - Pass: in-mission save/load is the persistence vehicle, whether for a single mission or a hybrid.
  - A state field resets: that state cannot be trusted across any mid-mission save. Expose the limit, or carry it through campaign persistence. In that case run **P6-L**, a two-mission linear test campaign using CampaignRearm/Repair (`changelog.txt:1807`), to see what carries over between missions.
  - P6-L is required before choosing linked missions.

## P7 – Distance metric and path shape at latitude

- **Question:** do movement and area triggers use true NM or file units? Do long legs follow great circles?
- **Setup:** centre 45, -30. Three open-water lanes: 0N (0, -25), 45N (45, -30) and 69.5N (69.5, 0).
  - In each lane, a ship at 15 kt with one waypoint **60 true NM** east. That is x = 60, 84.9 and 171.3 file units respectively.
  - In each lane, a `UnitsInTheArea` trigger centred 30 true NM east of the ship's start, radius 10.
  - An aircraft with `UnlimitedFuel=True` flying from 60N 40W to 60N 20E at a fixed cruise speed. Save at about 1.9 h of flight.
- **Expected times:**

  | Measure | If true NM | If file units |
  |---|---|---|
  | Ship arrival, all lanes | 4.0 h | 4.0 / 5.66 / 11.4 h (0N / 45N / 69.5N) |
  | Trigger at 69.5N | about 1.33 h | about 1.77 h |

  For the aircraft at 450 kt:

  | Path model | Distance | Time | Mid-route position |
  |---|---|---|---|
  | Great circle | 1,737 NM | 3.86 h | 63.4N at 10W |
  | Along the parallel | 1,800 NM | 4.0 h | 60.0N |
  | File plane | 3,600 units | 8.0 h | – |

- **Pass/fail:** classify the metric as TRUE (within ±5% of the true-NM column) or FILE-PLANE, and the path as great circle or straight line in lat/lon.
- **Effect on the world build:** this is a builder decision, not an architecture one.
  - TRUE: convert the builder's 16 x/z `hypot` sites (e.g. `build_pack.py:1791`, `:1891`, `:2561`, `:3719`, `:4891`) and `nm_between` to great-circle distance.
  - FILE-PLANE: the engine itself stretches east-west distances at high latitude in every mission, so splitting cannot fix it. Author Kola, Norway and Falklands distances in file units.

## P8 – Water at disputed anchorages

- **Question:** does game terrain show water where Natural Earth 1:10m draws land?
- **Sites:** Hood Canal at Bangor (47.73, -122.72), Kola Bay at Severomorsk (69.07, 33.42) and Apra inner harbour (13.44, 144.66). Controls that Natural Earth already shows as water: Diego Garcia lagoon (-7.35, 72.43) and Cockburn Sound (-32.20, 115.72).
- **Setup:** one tiny file per site with a local centre. A patrol craft and a submarine at periscope depth, each with a 2 NM waypoint along the channel, plus a land unit with height `low` on the shore.
- **Pass:** the craft float and move 2 NM; the submarine does not get stuck (`changelog.txt:861`); a screenshot shows water.
- **Effect on the world build:** builder only. Where game water exists, add per-site water overrides instead of snapping units away. Where it does not, represent the base with pier-side land units and an offshore anchorage.

---

## Decision matrix

| Outcome | Architecture |
|---|---|
| P1 passes to 7,000 NM or more; P2 passes; P3a passes; P6 passes; N\* ≥ world active population | **Single persistent world mission.** Regions are authoring units only. |
| As above, but N\* < population and D-dormant (or cheap parked aircraft in P5) passes | **Hybrid single mission.** A dormant population is woken by triggers per operation, and remote inventories are held as roster data. |
| P3a: units coexist but cannot cross | One mission, with gateway triggers for transpacific moves. |
| P3a: units cannot coexist | Split only the theatres east of 180 into a linked mission. Everything else stays together. |
| P2: an unobserved theatre freezes | One active theatre at a time (hybrid), or linked missions. Either way P6-L must pass. |
| P1 fails beyond D < 7,000 NM | Use the minimum number of missions that keeps every unit within D of its centre, computed from the measured D. |
| P6 fails on a state field | Persistence for that field is unavailable in any architecture until P6-L shows campaign carry-over works. Disclose the limit. |

Linked regional missions are justified only if P2 or P3a fails, if P1 fails below the world radius, or if N\* is below a single theatre's needs even with dormancy. They also require P6-L to pass. A single map centre with relative coordinates is not evidence for them on its own.

## What the probes cannot settle

- The performance results from P0b, P4 and P5 are GAME-on-this-PC. A pass is a lower bound on what the game can do; a fail is not an engine-wide limit.
- None of these probes tests AI pathfinding on long coastal routes (for example Brest to the Mediterranean via Gibraltar). Add that only if P2's routed merchant shows problems.
- Whether background data (`LoadBackgroundData`) creates every global entry or filters by distance stays open. Add one variant to P4 if a world background layer is planned.

Scratch artefacts are outside the repo; the repo was not modified (`git status` clean):
- `docs/world-sandbox/work/scripts/near.py` lists stock unit types near the anchors.
- The save's key census was a scratch listing and is not kept; rerun it from `data/install-snapshot/saves/` if needed.
- The scratch `global_coast.json` was used for the land/sea checks. The Payload decode and world-extent calculations were run inline and not kept.
