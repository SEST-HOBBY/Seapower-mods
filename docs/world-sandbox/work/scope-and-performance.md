# World sandbox: scope and performance evidence

**Status:** evidence report only. Nothing in the repo was changed and nothing was run in game. The repo HEAD is `50cad91b` ("docs: include original world research and repair browser handoff", the `feature/world-campaign-draft` commit). The installed game is **0.8.4 Build 261002** (`mods-source/_vanilla/changelog.txt:6`).

**Tags**
- **GAME**: engine behaviour or stock data.
- **BUILDER**: SEST tooling.
- **UNMEASURED**: no evidence either way.
- **GAME-on-this-PC**: a performance result from the player's machine. It is a lower bound, not an engine limit.

**Path aliases**
- `CL` = `mods-source/_vanilla/changelog.txt`
- `stock/` = `mods-source/_vanilla/original/`
- `MFI` = `stock/missions/Demo/MissionFileInformation.ini`
- `saves/` = `data/install-snapshot/saves/`
- `bp` = `integration/campaign/build_pack.py`
- `SW-notes` = `docs/campaigns/southern-watch/build-notes.md`
- `scratch/` = `docs/world-sandbox/work/scripts/` (the two scripts this report cites; other figures were computed inline)

**Coordinate convention used throughout**
- x = (lon − MapCenterLongitude) × 60
- z = (lat − MapCenterLatitude) × 60
- z is positive north. "File units" means these arcminutes (see §2.1).

---

## 1. Bottom line

- **[GAME, high] The map centre is a coordinate datum, not a boundary.**
  - The engine-written save `saves/New midgame.sav` (NORTHERN FRONT III FINAL, centre 54.27,−26.28 at `:73-74`) holds 298 units. Their GeoPositions lie 6,444–8,781 NM great-circle from the centre and up to 3,450 NM from each other (`scratch/savespread.py`).
  - Stock `stock/missions/Warsaw Pact/Strawberries Can Kill (Red Side).ini:73` places a carrier at x = 12,117.71.
  - With a candidate world centre of 42N 20E, every project anchor lies within 7,002 NM (Pearl Harbor) and |x| ≤ 10,677. Both figures are inside what has already loaded, run and been saved.
  - Two parts of the world's geometry are not yet covered by played content:
    - |z| = 5,629 at Mount Pleasant, against 4,529 in the save.
    - Unit-to-unit separations up to about 10,150 NM (Norfolk–Stirling), against 3,450 NM in the save.
- **[GAME, high] The game states no extent limit, unit cap or theatre requirement.**
  - Its only statement about the centre is a performance hint of unknown size: "drag this to the center of the scenario for best performance – also used to calculate the Local time" (`stock/language_en/ui.ini:1256`).
  - Absolute `GeoPosition=` placement also exists (`MFI:436-440`), so the format does not force centre-relative placement.
- **[GAME, medium risk] The ±180° date line is the one engine edge on record.**
  - The changelog says so: "edge of our flat Earth" (`CL:2618-2619`), "relocation loop (still WIP)" (`CL:4380`) and "Trial of fix" (`CL:4096`).
  - No repo mission has units on both sides of the line (scratch scans from three lenses).
  - The only mission next to it writes a unit 0.7° west of the line as x = 21,549.23, which is +359° in the flat frame (`mods-source/3629144864/missions/EUROMOD/EUROMOD showcase german.ini:44,227`).
  - So one mission spanning Hawaii and Guam/Japan is untested in either direction. Probe P3a covers it.
- **[BUILDER, high] Today's binding constraints are ours, and each can be extended:**
  - snapping to proven positions, with zero coverage at San Diego, Norfolk, Pearl Harbor, Brest and the Falklands;
  - a coastline extract fixed to 100–180E / 25–72S;
  - x/z distance maths that treats arcminutes as nautical miles;
  - no longitude wrap in `nm_between`, `sea_routes.py` or `briefing_maps.py`;
  - output hard-wired to `SEST_Campaign`;
  - mission clocks of 45–75 minutes.

  None of these is evidence about the engine.
- **[UNMEASURED, high] Capacity is unmeasured, so the single mission vs hybrid vs linked missions decision is open.**
  - No load time, frame rate, effective time compression or reload result exists for any large or far-flung mission.
  - The largest mission that was played and saved has 298 units plus 634 aircraft in air groups. Files with 857 and 974 units have no simulation record.
  - Also unknown: whether an unobserved theatre keeps simulating, and whether saves reload.
  - **None of this blocks the world population register.**

---

## 2. What the game evidently supports

### 2.1 Positions are an arcminute lat/lon datum, not a local flat map [GAME, high]

- **Format.** `RelativePositionInNM=x,y,z` decodes as lat = centre + z/60 and lon = centre + x/60, with no cos(lat) factor.
  - NORTHERN FRONT III FINAL places Darwin at `9429.85,low,-4001.8` (`integration/missions/NORTHERN FRONT III FINAL.ini:2087`). That decodes to −12.4267, 130.8842.
  - The game-written save has `GeoPosition=-12.4266681555732,130.884157640465` (`saves/New midgame.sav:238`).
  - In `NORTHERN FRONT MIDGAME III.sav`, 49 of 52 land units match within 0.1 NM. The 3 outliers are rigs that were moved later (builder-limits lens, scratch `savecheck.py`).
  - The stock Texas twins differ by exactly dx = 3669.00 = 61.15° × 60 (`stock/missions/NATO/Don't Mess With Texas (Blue Side).ini:110-111` against `stock/missions/Warsaw Pact/Don't Mess With Texas (Red Side).ini:33-34,72`).
- **Consequence.** One x unit is cos(lat) NM on the ground: about 0.36 NM at 69N and 0.62 NM at 52S.
- **The stock documentation is wrong in two places.** It says "negative values go west for x and north for z" (`MFI:443`) and "offset in miles" (`MFI:447`). The data show z is positive north. The developer calls the frame "our flat Earth" (`CL:2618`), and `stock/ui/minimap.ini:15` says "one degree is 60nm".
- **The builders already match the game:** `bp:770-773`, `integration/missions/build_northern_front_ii.py:44-51` and `integration/missions/build_land_defence.py:772`.

### 2.2 Units far from the centre load, run and save [GAME, high]

**Engine-written saves**

| Save | Units | Distance from centre (great-circle) | Largest separation | Size | Created |
|---|---|---|---|---|---|
| `saves/New midgame.sav` | 298 | 6,444–8,781 NM | 3,450 NM (2.21N 163.07E to 5.60S 106.07E) | 22.8 MB | 2026-08-25 (`:6`) |
| `saves/NORTHERN FRONT MIDGAME III.sav` | 205 | 7,324–8,735 NM | 2,044 NM | 14.0 MB | 2026-08-24 |

Source: `scratch/savespread.py`.

- **New midgame.sav also holds** 30 weapons in flight and 634 aircraft in custom air groups (observations lens census).
- **Its base mission.** The save's language-block names read "NORTHERN FRONT III FINAL backup-20260825-140511" (`saves/New midgame.sav:60-67`). That file exists at `mods-source/_vanilla/user/missions/user_missions/NORTHERN FRONT III FINAL backup-20260825-140511.ini`.
- **Simulated time.** At least 45 minutes: the largest `LastLaunchTime` is 2,720 s. The save clock reads 18:53 (`:69`) against a base start of 13:00 (backup `:60`). The base has `ConvertTimeToLocal=True` (backup `:61`), so how much time elapsed is not established.
- **Build.** The save predates 0.8.4. On 25 Aug the current builds were 0.8.2 #363 (4 Aug, `CL:386`) and #364 (31 Aug, `CL:256`). It has not been tested on 0.8.4.

**Stock content does the same**
- Three stock missions use the North Atlantic centre 54.27,−26.28 while every unit sits 3,900–12,160 file units away:
  - `Strawberries Can Kill (Red Side).ini:33-34,73` (NW Pacific);
  - `stock/missions/NATO/Better Part of Valor 1988.ini:112-113,136` (Yucatan Channel). The developer still maintains this mission (`CL:1226`).
  - `Don't Mess With Texas (Red Side).ini:72` (Syrian coast).

**Probably the editor default.** 237 of the 394 `.ini` files under `mods-source/_vanilla/user/missions` use 54.27,−26.28, as does the Workshop editor file `mods-source/3491248180/missions/_Custom Mission.ini:25-26`. That this is the editor default is an inference (medium confidence).

**Real spans inside one mission**
- Stock neutral-vessel waypoints span 4,913 NM, from the East Mediterranean to the Chesapeake (`stock/missions/Warsaw Pact/UnderCoverOfTheRain.ini:495,503`).
- Typical stock missions are small: median spawn span 193 nm, or 330 nm including waypoints (game-data lens).

**Extent the world needs, against what is proven**

Anchors are approximate. World figures are measured from a centre at 42N 20E (scratch calculation).

| Measure | World needs | Largest in played and saved content | Largest in any file |
|---|---|---|---|
| Great-circle distance from centre | 7,002 NM (Pearl) | 8,781 NM (`New midgame.sav`) | — |
| \|x\| | 10,677 (Pearl) | 11,361 (save, 163.07E) | 12,117.71 (`Strawberries Red:73`) |
| \|z\| | **5,629** (Mount Pleasant) | 4,529 (save, 21.22S) | 4,819 (`integration/missions/AUS DEF.ini:549`, no play record) (`scratch/maxz.py`) |
| Unit-to-unit separation | **~10,150 NM** (Norfolk–Stirling); 9,547 (Yokosuka–Mount Pleasant) | 3,450 NM | 4,913 NM (stock waypoints) |

The two bold rows are gaps. Neither is a known limit; both are untested.

### 2.3 Absolute placement exists [GAME, high]

- **The syntax:** `GeoPosition=lat,lon,alt`, with altitude in feet (`MFI:436-440`).
- **Stock uses it:** `stock/missions/NATO/Hormuz.ini:158`, `Hormuz_hard`, `Hormuz_tarawa`, and `Don't Mess With Texas (Red Side).ini:80`.
- **The editor reads it:** "Mission Editor: GeoPosition support on unit loading" (`CL:5348`).
- **Saves store GeoPosition for every unit,** and the developer moved saved positions away from Unity coordinates (`CL:2485`).
- **No SEST Python tool reads or writes GeoPosition** (grep of `*.py`, builder-limits lens).

### 2.4 The engine moves its runtime origin [GAME, existence high; floating-origin reading medium]

- **The changelog refers to "relocation events" around a "center tile":**
  - `CL:5099`: a cascade of endless relocation events;
  - `CL:4793`: ASROC during a relocation event;
  - `CL:4030`: dead units teleported by faulty relocation handling;
  - `CL:3482`: weapons relocation on save load;
  - `CL:2882`: autogen buildings jumping during relocation;
  - `CL:2236`: ghost objects at the world origin.
- **A runtime log shows each object carrying both a Unity position and a geo position:** `SONO pos=(-666.47, -0.01, 13.98) geo=lat=-10.2999 lon=144.1053` (`git show f494117b:data/install-snapshot/bepinex.log`).
- **Reading:** MapCenter is a file datum, not a fixed physics origin. What triggers a relocation, and whether there is a distance threshold, is not documented.

### 2.5 Terrain is global but streamed [GAME, medium]

- **Biomes cover the world.** There are 11 biomes, including Falklands (`stock/terrain/biomes.ini:2-13`; `:5` Biome3=Falklands).
- **Terrain and clouds stream in chunks:** `stock/terrain/terrain.ini:20` ChunksViewDistance=4; `stock/clouds.ini:39` "one chunk is about 50km wide".
- **Land units have a placement floor:** `terrain.ini:28` MinHeightForLandUnits=1.0.
- **Terrain was sampled far from the centre.** Saved land-unit altitudes are non-zero and differ by site: Darwin 163.88 (`New midgame.sav:238`) and Scherger 143.46 (`:496`). The unit of that value in saves is not documented.
- **The heightmaps are not in the repo,** so terrain coverage at each project location is unverified. In particular there is no stock unit within 959 NM of the Falklands (game-data lens).

### 2.6 Scale on record [GAME]

- **Stock maximum: 87 declared units**, in `stock/campaigns/pacific-strike-task-force/missions/09 Shadows off Palawan.ini:277-287`. The "130 units" in the game-data lens is a double count; see the appendix.
- **Played and saved:** 298 units plus 634 aircraft in air groups (`New midgame.sav`).
- **Loaded and re-saved in the editor, with no simulation record:** SEST Banda Front EDITED, 857 units (`integration/missions/README.md:91-93`).
- **No recorded load at all:** SEST Indo-Pacific Land Assets, 974 units.
- **No key or UI string declares a unit cap.** The only caps found are:
  - a per-air-operation concurrent cap (`stock/language_en/ui.ini:424`);
  - `TaskForceModeMaxUnits` in a campaign (`stock/campaigns/pacific-strike-task-force/campaign.ini:637`);
  - the RebaseTooFar range check (`ui.ini:4159`).
- **Scaling cost is real but unquantified.** The developer has optimised mission loading, sensors and line of sight, and large formations (`CL:2275-2278`), plus the threat and weapons tracker (`CL:65-67`) and chaff (`CL:3488`).

### 2.7 Time compression [GAME, high]

- **Configured cap:** 100× (`stock/config.ini:13`, `CL:5344`).
- **The engine also limits compression on its own:**
  - during engagements (`CL:5121`);
  - for sonobuoys (`CL:5104`);
  - for guns and CIWS (`CL:5022`).
- **High-compression bugs have been fixed repeatedly:** `CL:2157`, `:1512`, `:865`.
- **Arithmetic only, not measured:** at 100×, one game day takes 14.4 real minutes, and a 2,000 NM transit at 20 kt takes about 60 real minutes.

### 2.8 Stock persistence, dormancy and world data [GAME]

- **Mid-mission save/load is switched on:** `stock/config.ini:7-9` (SaveLoadEnabled, SaveLoadSensorDataEnabled, SaveLoadFlightDeckEnabled).
- **Linear persistent campaign.** Losses and expenditure carry forward, and resupply is available: `stock/campaigns/strike-group-molniya-campaign/campaign.ini:5,9,21`.
  - Its missions use 5 different centres.
  - There are rearm, repair and air-group reset flags (`CL:1805,1807,1046`).
  - Campaign persistence was still being fixed in the 0.8.x builds (`CL:44`).
- **Enemy theatre order of battle:** `stock/campaigns/pacific-strike-task-force/enemy_theater_roster.ini:3,8`.
- **Dynamic Unit Generation** (`CL:344-349`) runs on the player's install (`data/install-snapshot/player-prev.log:414`).
- **Dormancy.** A unit can start with `Disabled=True` and be woken by a trigger with `Action_SetEnabledStatus=True`:
  - examples: `stock/missions/Campaign Scenarios/Pacific Strike/01A Senkaku Run.ini:583,720` and `MFI:735`;
  - stock uses it on aircraft, helicopters, 1 vessel and 1 submarine, never on land units (probe pass).
- **Global node-and-link world data.**
  - `stock/campaigns/campaign-proto-1/campaign.ini:1-15` is a theatre-wide prototype with no MapCenter.
  - `airports.ini` has 48 airports, including Hickam, Andersen, Kadena, Elizovo and Midway.
  - `sea_points.ini` has 431 points covering only lon −87.47 to 61.16, so the sea network has **no Pacific coverage**.
- **World-spanning background data** is attached to single missions, for example `UnderCoverOfTheRain.ini:640`. Whether distant entries are actually created is UNMEASURED.

### 2.9 Save contents [GAME, verified here]

- **The payload decodes.** `NORTHERN FRONT MIDGAME III.sav:21927` holds a `[PlottingTable] Payload=` of 13,230,721 characters. Replacing `{/}` with `//`, base64-decoding and gunzipping it gives 172,560,084 bytes beginning `DOTSBIN!`.
- **Contact type-name occurrences** in that payload: ESMContact 37,353, RadarContact 5,691, PassiveSonarContact 1,745, VisualContact 1,652.
- **Inference (medium):** save size follows the sensor-contact picture, not unit count. This fits `config.ini:8` SaveLoadSensorDataEnabled=True.
- **Saves hold per-system state** that can be diffed after a reload: `CurrentIntegrity`, `FloodingCompartments`, `Ammunition*_Count`, and supplier `CurrentAmmo` (`NORTHERN FRONT MIDGAME III.sav:183,674,257-258,9458-9469`).

### 2.10 Failure history: nothing is attributed to size or extent [GAME]

- **Crashes and load failures were all content or reference faults:**
  - the KJ-500/P-8 map-panel crash (`docs/design-notes.md:495-527`);
  - the startup `AirGroup` KeyNotFound (`docs/design-notes.md:463-469`);
  - Rig Seventeen's NullReference (`SW-notes:1263-1312`);
  - the map-UI NullReference from the renamed Spruance hull (commit `cdc4c0a1`).
- **The Steel Highway freeze was caused by a code mod,** which logged a full stack trace on every physics tick (`SW-notes:1331-1352`, commit `9ea7ae00`).
- **A second code-mod flood was never analysed:** the CV16 `_isInFlight` exception, 6,398 times (`git show 6555a94f:data/install-snapshot/player-prev.problems.txt`).
- **The 20 Sep stuck load is unattributed:** "a rollback on the balance of evidence, not a diagnosis" (commit `e2003125`).

### 2.11 Other in-game behaviours that matter for a persistent world [GAME]

- **Editor round-trips flatten ROE.** A round-trip turned every Hold and Tight weapon status into Free (`docs/design-notes.md:103-138`). `restore_roe.py` is the builder mitigation (`integration/missions/README.md:208-231`).
- **Aircraft orbit when their route ends.** One with no waypoints orbits its spawn point, and one that reaches its last waypoint orbits there (commit `1ff115b7`).
- **Sea state cuts ship speed:** a replenishment ship made 7 kn at flank in sea state 5 (`SW-notes:2045-2048`; `ui.ini:1250`).

---

## 3. Limits that belong to our builders, and how to extend each

| # | Builder limit | Evidence | Effect on a world build | Extension |
|---|---|---|---|---|
| B1 | Pool snapping: land, port and coastal units must snap within 60 NM to a point an earlier mission used, or the build exits | `bp:34-42`, `:87`, `:751-754` (POOL_ROOTS), `:974-1003`, `:5860` | Fails at San Diego (766 NM), Norfolk (989), Pearl (1,513), Kitsap (980), Stirling (927), Brest (512), Mount Pleasant (2,965), Bahrain (90), Souda (92) and others. It shaped earlier theatre choice: "no proven water to snap to" (`SW-notes:1236-1240`) | Use `GEOGRAPHY="coast"` with a global extract (B3) or `global_land_mask` (B5). Do not add untested probe or Workshop positions to the pool |
| B2 | Offshore stations more than 25 NM from every pool land point are accepted unvalidated | `bp:825-829`, `:929-971` (case 1 "unproven") | Every offshore station off the US coasts, Hawaii, the Falklands and Brest goes in unchecked | The same fix as B1 |
| B3 | Coastline extract covers one box: 100–180E, 25–72S | `tools/make_coast_extract.py:97-98`; `integration/campaign/geo/southern_theatre_coast.json` | Coast mode reports every world position outside the box as a problem | Cut a global extract with the repo's own code. Measured in scratch: 9,632 rings, 8.7 MB, 3.8 s to cut, 1.7 s to index, 6–8 ms per query |
| B4 | Natural Earth 1:10m outer rings only; lakes and holes dropped | `coast.py:51`; `make_coast_extract.py:112` | Hood Canal (47.73, −122.72), Kola Bay at Severomorsk (69.07, 33.42) and Apra inner harbour (13.44, 144.66) read as land. **Diego Garcia lagoon reads as water** (probe pass, correcting the builder-limits lens) | Per-site water overrides after P8. Otherwise pier-side land units plus an offshore anchorage |
| B5 | Only mission-level tools use the worldwide 1 km land mask | `integration/missions/fix_land_positions.py:31-45`, `sea_routes.py:31-34`; `build_pack.py` does not use it. Not installed in this container | A global check exists but the campaign builder does not use it | Wire `global_land_mask` into placement |
| B6 | About 16 distance and bearing sites in `bp` treat x/z as nautical miles | 18 `math.hypot` lines in `bp` (e.g. `:1791`, `:1891`, `:2561`, `:3719`, `:4891`); `_bearing` docstring `:2453-2457` | Overstates east-west distance by 1/cos(lat): ×1.49 at Brest, ×2.79 at Kola | Convert to lat/lon and great-circle. Final form waits on P7 |
| B7 | No antimeridian wrap | `nm_between` `bp:816-819` (flat mean-latitude formula); `coast.py:40-44,82`; `sea_routes.py:155-160` (bounding box); `integration/missions/briefing_maps.py:171-185`; `bp` harvest `:795-796` | Guam–Pearl computes as 17,333 NM, true 3,305. Lanes across 180 cannot be routed | Normalise longitudes and wrap deltas. The form to emit waits on P3a |
| B8 | Civil airway stretch is unclamped | `bp:1606-1617`; `civil_reach_nm` `:813` | Under a long persistent clock, waypoints go past the poles | Clamp the stretch, or loop the route |
| B9 | Mission clocks and density budgets are design choices | `integration/campaign/campaign_data.py` (45–75 min); `docs/campaigns/southern-watch/campaign-bible.md:383-385` ("not measured engine limits"); `SW-notes:2316-2321` | Not evidence of an engine cap | Replace with the measured N\* from P4 |
| B10 | Output is hard-wired to the published pack | `bp:68` (OUT = SEST_Campaign); `:6246-6259` rewrites `_info.ini`, REQUIRED-MODS and LOAD-ORDER | Reusing `bp` as-is would change published content | A world builder needs its own output root (required by "keep published content unchanged") |
| B11 | Preflight only finds missions in `integration/missions` or `integration/campaign` | `tools/preflight.py:262-271` | Probe and world files are not checked | Add a path argument |
| B12 | No tool emits GeoPosition | grep of `*.py` | Every unit is centre-relative | Optional geo emission once P1 confirms GeoPosition for every unit class |
| B13 | Briefing maps cannot frame a global or date-line mission | `briefing_maps.py:171-190`, `:342`, `:434-436` | Cosmetic | Per-region insets; the game can generate its own view (`ui.ini:704`) |
| B14 | Scenario carving was a design judgment | `tools/make_scenarios.py:3-6` ("heavy for a quick fight") | Not evidence | — |

Pool sizes differ between replicas: 2,277 or 2,496 unique sea points and 2,761 land points. The `bp` docstring's "about 33,000" is the pre-dedupe count, and the build notes say 5,300 (`SW-notes:1250-1258`). Both replicas agree that the regions listed in B1 have no coverage.

---

## 4. What is unmeasured, ranked by the decision it controls

1. **Does a theatre keep simulating while the camera is elsewhere, and do theatres interact across a gap?** Nothing in the repo shows two active groups more than 3,450 NM apart. This decides between one mission and a hybrid or linked missions. Probes: P2, plus P1's far rungs.
2. **Antimeridian.** Can units coexist across ±180 (detection, terrain, no relocation loop), and can they cross it? Which longitude form does the engine accept? The only repo example writes the far side as +359° (`EUROMOD showcase german.ini:227`). This decides whether the Pacific east of 180 can join the world mission. Probe: P3a.
3. **Active-unit capacity N\* on the player's PC,** and whether the cost comes from count, spread or radar emission. Nothing has been measured (`docs/world-sandbox/gameplay-and-tests.md:39`; `git show 67c65155:docs/banda-front-lean-verification.md:87-88`). The CPU and RAM are unknown; the GPU is an RTX 2070 SUPER with 8 GB (`data/install-snapshot/player-prev.log:15-17`). This sets the population budget. Probes: P0b, P4.
4. **Save and reload fidelity, and dependence on BaseFile.** All three mid-mission saves point at `missions\_temp\_TempMission.ini` (`:5`), which now holds a different mission. No reload has been recorded. This decides the persistence vehicle. Probes: P0a, P6, P6-L.
5. **Cost of dormant units and parked aircraft.** This decides whether a hybrid is viable. Probes: P4 D-dormant, P5.
6. **Effective time compression at scale.** Does an engagement in one region cap compression for the whole world (`CL:5121`)? This affects transits and resupply in every architecture. Probes: P2, P4.
7. **The z range and very large separations.** Mount Pleasant needs |z| = 5,629 and separations reach 10,150 NM; both are beyond played content (§2.2). Probe: P1 Variant C.
8. **What a distant centre costs.** The tooltip at `ui.ini:1256` gives no number. This decides where to put the centre. Probe: P1 Variant B.
9. **The engine's distance metric and path shape at high latitude.** This is builder geometry only. Probe: P7.
10. **Game water at disputed anchorages, and terrain at the Falklands.** This is builder placement only. Probes: P8, P3b.
11. **Per-tick cost of code mods** at world scale (the PLA AEP and CV16 floods, §2.10). Every probe runs once with BepInEx off.
12. **Whether `LoadBackgroundData` creates every global entry.** Only matters if a world background layer is planned. Possible P4 variant.
13. **Payload growth over a long session.** It is driven by contacts (§2.9). Probe: P4 saves at T+30 min and T+4 h.

---

## 5. Implications for the world register

### 5.1 What can be authored now, whatever the probes show

The register is **not blocked**. Every probe outcome changes how records are *emitted*, not what the records *are*.

- **Positions:** store each record as absolute lat/lon (−180 to 180), never as x/z. Missions derive x/z, or GeoPosition, for whichever centre or centres the probes support (§2.1, §2.3).
- **Region:** an authoring and checking tag, not a mission boundary.
- **Every researched installation and associated force**, with:
  - an allocation class: resident, deployed or support;
  - a candidate run state: active, dormant (`Disabled=True` plus a trigger, §2.8), or roster-only (theatre order of battle or Dynamic Unit Generation);
  - for air units, inventory split into parked and airborne.
- **Provenance per field:**
  - a source claim (an R01–R03 line);
  - a verified fact (repo evidence path);
  - a proposed scenario allocation.

  These must stay distinguishable.
- **Collection mapping per record:** stock, SEST or Workshop type. Missing assets are listed explicitly.
- **Logistics links:**
  - great-circle distance;
  - a sea-network flag, since stock sea points do not cover the Pacific (§2.8);
  - an explicit **crosses-antimeridian** flag;
  - resupply capability: ship-to-ship replenishment needs the SEST Replenishment pack (`integration/replenishment/SEST_Replenishment/vessels/usn_aoe_sacramento.ini:304-314` against the stock block commented out at `stock/vessels/usn_aoe_sacramento.ini:303-319`).
- **Placement status per site:**
  - proven (pool);
  - Natural Earth water;
  - Natural Earth land, pending P8 (Kitsap, Kola Bay, Apra inner);
  - pier-side fallback;
  - no stock terrain evidence (Falklands, pending P3b).
- **Routine activity,** with a route-duration field. Routes must outlast the session, because aircraft orbit when their route ends (§2.11).
- **Radar posture when idle:** cheap to record now. It may become a world-wide rule if P4's S-emit run is costly.

**Do not bake in:** a map centre; a per-mission unit budget (B9); a regional split; or x/z values.

### 5.2 Decisions that wait on probes

| Decision | Waits on | Working default until then |
|---|---|---|
| One coordinate origin for the whole world, or partition at a measured distance D | P1 (A, B, C) | One origin at about 42N 20E, already inside proven \|x\| and great-circle distance |
| Pacific east of 180 in the same mission | P3a | Same mission; links flagged |
| Theatres active at the same time | P2 | Assume yes for authoring |
| Size of the active population; use of dormancy | P0b, P4, P5 | Record run state per record; no cap |
| Persistence vehicle: mid-mission save, or campaign carry-over | P0a, P6, P6-L | Freeze and version any world mission file used for saves |
| Great-circle or file-plane distance in the builder | P7 | Store true great-circle distance; derive from it |
| Water overrides at anchorages | P8, P3b | Status flags only |
| Where the centre sits | P1 Variant B | Centroid of play |

**Decision matrix** (from the probe design):

| Outcome | Architecture |
|---|---|
| P1 passes to at least 7,000 NM (and Variant C passes); P2, P3a and P6 pass; N\* is at least the active population | **Single persistent world mission.** Regions are authoring units only |
| As above, but N\* is below the population, and D-dormant or cheap parked aircraft (P5) pass | **Hybrid single mission.** A dormant population is woken by trigger per operation; remote inventories are held as roster data |
| P3a: units coexist but cannot cross | One mission, with gateway triggers for transpacific moves |
| P3a: units cannot coexist | Split **only** the theatres east of 180 into a linked mission |
| P2: an unobserved theatre freezes | One active theatre at a time (hybrid), or linked missions. Either way P6-L must pass |
| P1 fails beyond a distance D below 7,000 NM | The minimum number of missions that keeps every unit within D of its centre, computed from the measured D |
| P6 fails on a state field | That field cannot persist in any architecture until P6-L shows campaign carry-over works. Disclose the limit |

Linked regional missions are justified only if P2 or P3a fails, if P1 fails inside the world radius, or if N\* is too small even with dormancy, **and** P6-L passes. A shared centre with relative coordinates is not evidence for them on its own.

---

## 6. Probe plan

Probes are opt-in measurement files. Nothing below has been run.

### 6.1 Rules common to every probe

- **Never deploy probe files.**
  - Keep them out of `integration/missions/`, because `tools/install-sest-packs.ps1:143-160` copies every `.ini` under it into the game.
  - Keep them out of `integration/dist/`.
  - Keep them out of every `bp` POOL_ROOT (`bp:751-754`), so untested positions never become "proven points".
  - Do not let a later snapshot carry probe files into `mods-source/_vanilla/user/missions`, which is also a pool root.
- **Suggested home:** `docs/world-sandbox/probes/`, with filenames prefixed `ZZ PROBE`. The user copies each probe by hand into `<StreamingAssets>\user\missions\user_missions` and deletes it afterwards.
- **Generator:** a standalone script, never `bp` (B10). It also writes an `expected.json` with intended lat/lon and arrival times, so captured saves can be scored automatically.
- **Preflight:** it cannot see these files (B11). Copy `Type=` lines from missions that already load, or add a path argument to preflight.
- **Placement maths:** as in §2.1, with z positive north and longitudes normalised to ±180, except where P3a deliberately tests otherwise.
- **Unit content:** stock unit types only, except P6, which needs SEST Replenishment.
- **BepInEx:** run P0b, P4 and P5 twice, once with code mods disabled (engine baseline) and once with the full install.
- **Keeping idle probes idle:** set `[Debug] AllowEnemyUnitsAttackPlayer=False` (`MFI:32`) and `WeaponStatus=Hold`. `AllowControlOfEnemyUnits=True` (`MFI:19`) helps inspection.
- **Launching:** start from the mission list, not the editor test button. Record each save's `BaseFile=` line.
- **Record sheet (every run):**
  - build (0.8.4 Build 261002), repo commit, mod list and load order (`tools/capture-context.ps1`), BepInEx on or off;
  - CPU, RAM, GPU, resolution and preset;
  - load time by stopwatch, from Start to the first controllable frame;
  - FPS, averaged over 60 s;
  - effective time compression: game minutes advanced in 2 real minutes ÷ 2, at nominal 20× and 100×;
  - RAM and VRAM, and the count of "Exception" lines in Player.log;
  - save duration, `.sav` size, Payload length, and the decoded contact counts (§2.9 method).
- **Capturing saves:** `capture-context.ps1 -IncludeSaves` copies only the 6 newest saves (`:318-331`). Capture straight after each probe.
- **Performance logging:** run `config.ini:3 EnablePerformanceLogging=True` only in a separate pass, because it adds garbage-collection overhead (`CL:5302`). Never compare its FPS with unlogged runs, and revert the setting afterwards.

### 6.2 Summary and order

| ID | Question | Decides | Order |
|---|---|---|---|
| P0a | Do the existing mid-mission saves reload on 0.8.4, and do they depend on BaseFile? | Persistence vehicle | 1 |
| P0b | How do the existing 241- to 974-unit missions load and run? | P4's starting step | 1 |
| P1 | Is a unit placed 250–10,000 NM out correct and live, including at \|z\| > 5,600? | Single origin | 2 |
| P3a | Do units coexist and cross at ±180? | The only engine fact that could force a Pacific split | 2 |
| P3b | Are 69N and 52S correct? | Kola and Falklands usability | 3 |
| P2 | Do two theatres 2,057 NM apart both simulate and interact? | Simultaneous theatres | 3 |
| P6 | Does save/load preserve damage, magazines, supply and trigger state? | Persistence vehicle | 4 |
| P4 | How do load, FPS, time compression and save size scale with count, spread and emission? | Population budget; dormancy | 5 |
| P5 | What do parked aircraft cost? | Airbase inventory policy | 5 |
| P7 | True NM or file units at latitude? | Builder geometry | 6 |
| P8 | Is there game water where Natural Earth draws land? | Builder water handling | 6 |

### 6.3 Probe designs

**P0a – Reload existing saves (no authoring)**
- **Targets:**
  - `saves/New midgame.sav` (22.8 MB, 298 units, 30 weapons in flight);
  - `saves/NORTHERN FRONT MIDGAME III.sav` (14.0 MB).
- **BaseFile A/B, new in this pass.** The base of New midgame.sav is identifiable (§2.2), so test it both ways:
  1. Back up the player's current `_temp/_TempMission.ini`, which now holds NF III FINAL NEWEST.
  2. Load with it in place (run A).
  3. Copy `NORTHERN FRONT III FINAL backup-20260825-140511.ini` into `_temp/_TempMission.ini` and load again (run B).
  4. Restore the original afterwards.
  5. Do not run `install-sest-packs.ps1 -PurgeBackups` before this probe: it deletes `* backup-<stamp>.ini` files from the game folder (`install-sest-packs.ps1:150-158`).
- **Procedure:** load and time it; save `P0a-<name>-reloaded` without unpausing; unpause for 5 game minutes and save again.
- **Record:** load time; unit count; airborne aircraft and weapons in flight against the original; FPS; effective time compression; a diff of the unit sections, excluding Payload and timestamps.
- **Pass:** it loads; GeoPosition within 0.01 NM; integrity, ammunition and supply keys identical; simulation continues.
- **Fail modes:** refuses to load; loads the other mission's content (a BaseFile dependency); state drifts.
- **Effect on the world build:**
  - Pass: mid-mission saves are a working persistence vehicle at about 300 units.
  - BaseFile dependency: the world mission file must be versioned and frozen for each save generation, in any architecture.

**P0b – Existing large missions (no authoring)**
- **Missions:**
  - NORTHERN FRONT III FINAL: 241 units plus about 546 aircraft in air groups;
  - SEST Banda Front EDITED: 857 units;
  - SEST Indo-Pacific Land Assets: 974 units.
- **Procedure:** fill in the common sheet over 10 game minutes, then save and record the size.
- **Pass:** loads in under 10 minutes and stays responsive.
- **Fail:** a hang (note the last line of Player.log), a crash, or an unusable frame rate.
- **Effect on the world build:** this sets P4's starting step. If 974 runs well, P4 starts at 600/1000.

**P1 – Distant placement ladder**
- **Variant A setup.** Centre 0.0, −30.0. On the equator one x unit is one true NM, so distance is tested separately from latitude distortion (P7).

  | Rung | Offset | Lat, lon | Surface |
  |---|---|---|---|
  | E250 | x=250 | 0, −25.83 | sea |
  | E1000 | x=1000 | 0, −13.33 | sea |
  | E3000 | x=3000 | 0, 20.0 | land (DRC) |
  | E6000 | x=6000 | 0, 70.0 | sea |
  | E10000 | x=10000 | 0, 136.67 | sea, 63 NM off New Guinea |
  | N250 | z=250 | 4.17, −30 | sea |
  | N1000 | z=1000 | 16.67, −30 | sea |
  | N3000 | z=3000 | 50, −30 | sea |
  | N4800 | z=4800 | 80, −30 | land (Greenland ice) |

  - At every rung:
    - an aircraft at 25,000 ft with a 20 NM waypoint;
    - a ship if the rung is water, at Telegraph slow with `Waypoints=Course,90/90,20,0` (`MFI:492`);
    - a `low` land unit if the rung is land;
    - a GeoPosition twin of the ship or land unit, 2 NM north (`MFI:436-440`).
  - All rungs are present at once, so the probe also tests concurrent separations of several thousand NM (§4 item 7).
- **Variant B:** the same world positions, with the centre moved to E10000 and x/z recomputed. This is the A/B test for `ui.ini:1256`.
- **Variant C, new in this pass:** the candidate world centre 42, 20, with one ship or land unit and one aircraft at each of:
  - Mount Pleasant: x = −4,707, z = −5,629, the largest \|z\| of any anchor;
  - Pearl Harbor: x = −10,677;
  - Stirling: z = −4,454;
  - Darwin;
  - Severomorsk.

  This covers the \|z\| gap and the ~10,000 NM separations beyond played content (§2.2) at the actual world geometry.
- **Procedure:**
  1. Load (stopwatch) and pause.
  2. Visit every rung: screenshot, and measure FPS at 1× for 30 s.
  3. Park the camera at the centre, run 30 game minutes at 20× and save.
  4. Park the camera at the farthest rung, run 30 minutes and save.
  5. Repeat for Variants B and C.
- **Record:** saved GeoPosition against intended; saved land-unit altitude; ship displacement while unobserved; FPS per rung; load time A against B.
- **Pass:**
  - every unit within 0.1 NM of its intended position (NORTHERN FRONT achieved 0.001 NM);
  - relative and GeoPosition twins agree;
  - ships on water and land units at non-zero altitude;
  - unobserved units advance the expected distance ±5%;
  - nothing jumps when the camera moves;
  - FPS at far rungs within 10% of the centre rung.

  Failures are recorded per rung, which gives a measured distance D.
- **Effect on the world build:**
  - Pass to at least 7,000 NM, and C passes: one origin holds the whole world.
  - Failure beyond D < 7,000: partition so that every unit is within D of its centre. Check whether the GeoPosition twin fails the same way.
  - B materially faster than A: centre the world where play concentrates.

**P2 – Two theatres in one mission (Guam and Hainan, 2,057 NM apart)**
- **Centres:** A is the midpoint, 15.83, 127.10. B is 54.27, −26.28.
- **Guam (Blue):**
  - `airfield_small_1` at Andersen, using the stock pattern in `stock/missions/NATO/Showdown off Guam Blue 1985.ini:504-515` (B-52G, P-3C, F-4E);
  - two combatants on a 4-waypoint box off Apra;
  - a neutral merchant routed Apra → 16N 130E → 21N 121E → 18.5N 119E → 18.10N 109.60E, about 2,180 NM, all water by the scratch check.
- **Hainan (Red):**
  - an airfield at Yulin, using `airfield_small_1` (`stock/missions/PLAN/PLAN 02 Battle of the South China Sea.ini:507`) or `wp_airbase_4` (`stock/campaigns/pacific-strike-task-force/missions/10 Vengeance at Luzon.ini:1100`), with H-6D and J-7C groups;
  - two ships on a patrol box off Yulin.
- **Cross-gap traffic:**
  - a Blue B-52G (HomeBase Andersen) flying to 100 NM south-east of Yulin and back;
  - a Red H-6D (HomeBase Yulin) flying to 150 NM west of Guam and back;
  - both with `UnlimitedFuel=True` (`CL:1226`);
  - at t = 30 min, a trigger with `Action_AirStrike=Bomb` from the Hainan airfield against the Blue ships off Apra (pattern: `stock/missions/NATO/Hormuz.ini:411-421`).
- **Instrumentation:** `UnitsInTheArea` triggers that post timed messages (pattern: `stock/missions/Warsaw Pact/Breakthrough.ini:831-834`):
  - one on each Red patrol waypoint (radius 3 NM);
  - one on the Yulin approach and one on the Guam approach (radius 30 NM).
- **Procedure:**
  1. Keep the camera at Guam for 3 game hours at 20×, never visiting Hainan, then save S1.
  2. Move the camera to Hainan, run 2 more hours and save S2.
  3. Reload S1 and compare.
  4. Optional: run the merchant's full transit at 100×.
- **Pass:**
  - the unobserved Red patrol logs every waypoint on schedule ±10%;
  - cross-gap aircraft arrive within ±10% and land;
  - the strike either launches or produces a clear game refusal (e.g. RebaseTooFar, `ui.ini:4159`), recorded as a range rule;
  - no teleports;
  - S1 reloads faithfully.
- **Effect on the world build:**
  - Pass: theatres coexist in one mission.
  - The unobserved theatre freezes: hybrid (one active theatre at a time) or linked missions.
  - Only cross-gap AI routing fails: keep one mission and use trigger hand-offs (a builder task).

**P3a – Antimeridian**
- **Setup:** centre 30.0, 178.0.
  - East-side ship at 179.9E (x = +114), with three eastbound twins 2 NM apart:
    - `E-course`: `Course,90/90,120,0`;
    - `E-unwrap`: explicit waypoint x = +234 (lon 181.9);
    - `E-norm`: explicit waypoint x = −21,366 (lon −178.1, the EUROMOD form).
  - West-side spawn twins at 179.9W, 2 NM apart:
    - `W-norm`: x = −21,474;
    - `W-unwrap`: x = +126;
    - `W-geo`: `GeoPosition=30.0,-179.9,0`;
    - plus one westbound ship.
  - Detection pair: a Blue ship and a Red ship 10.4 NM apart across the line, radars on, weapons Hold. A control pair sits at 170E.
  - Land units at height `low` at Amchitka (51.38, 179.26) and Adak (51.88, −176.65).
- **Procedure:** follow `E-course` across the line; pan between Amchitka and Adak; save while a unit straddles the line, then reload.
- **Record:** spawn error for each twin; the crossing path (does E-norm sail the long way round?); longitude after crossing; detection time against the control pair; altitudes; jumps, an FPS collapse or a relocation loop (`CL:4380`); reload accuracy.
- **Effect on the world build:**
  - Full pass: one mission spans the Pacific. The builder emits whichever form worked and adds wrap (B7).
  - Units coexist but cannot cross: gateway triggers at the line.
  - Units cannot coexist: **the only result that forces a regional split on engine grounds**, and only for the theatres east of 180.

**P3b – High latitude and southern hemisphere**
- **Kola,** centre 69.6, 35.0:
  - ships in open Barents water;
  - a land control at the stock `wp_airbase_4` position (`stock/missions/NATO/Northern Vigil.ini:398`);
  - a `low` land unit at Severomorsk airfield.
- **Falklands,** centre −51.7, −58.0:
  - a `low` land unit at Mount Pleasant (−51.823, −58.447);
  - ships at −51.70, −57.50;
  - an aircraft in orbit.
- **Pass:** within 0.1 NM; plausible altitude; the island visible; ships float and move.
- **Effect on the world build:** missing Falklands terrain is a gap in the game's data. Splitting missions cannot fix it, so the Falklands would become sea-only or off-map.

**P4 – Population scale**
- **The 50-unit cell (stock types only):**
  - 20 land units at stock-used points (e.g. `stock/missions/NATO/Dangerous Straits 1985.ini:644` and the Diego Garcia position in `04 Chagos Gambit.ini:483`);
  - 15 ships: 8 anchored, 7 on 12 kt loops;
  - 5 submarines;
  - 6 airborne aircraft with a HomeBase;
  - 4 merchants.
  - Weapons Hold, and `AllowEnemyUnitsAttackPlayer=False`.
- **Steps:** 50 / 150 / 300 / 600 / 1000. Centre 42, 20.
- **Variants:**
  - **S-quiet:** 6 clusters (Norwegian Sea, East Mediterranean, Arabian Sea, Diego Garcia, Timor Sea, Philippine Sea), with one SAM radar per cluster. Run every step.
  - **S-emit:** all radars on. Run at 300 and at the last step S-quiet passes. This tests the contact-picture inference in §2.9.
  - **C-quiet:** one cluster. Run at the last passing step and the first failing step.
  - **D-dormant:** 1000 units, 80% `Disabled=True`, against 200 active. Include land units, which stock has never disabled.
  - Optional: set `MaxTimeCompression=200` once to see whether the HUD offers it, then revert.
- **Record:** the common sheet at each step; saves at T+30 min and T+4 h at the same population (does the payload grow?); reload, then an immediate re-save.
- **Acceptance (the user's playability choice, not engine facts):**
  - no hang over 10 minutes;
  - 30 FPS or more at 1× at the busiest cluster;
  - at least 50× effective when 100× is selected;
  - a save takes 60 s or less, and the reload has an identical unit count.

  The highest passing step is N\*, classified as GAME-on-this-PC.
- **Effect on the world build:**
  - N\* at or above the active population: one mission.
  - S fails where C passes: spread itself costs something; size the regions per mission by measurement.
  - S and C fail at the same N: count is the cost; regional missions help only if each stays under N\*.
  - D-dormant is cheap: hybrid single mission.
  - S-emit costly: radars off when idle becomes a world-wide authoring rule.

**P5 – Idle airbase cost**
- **Setup:** 6 stock airbases (Andersen, Souda, Diego Garcia, Kola, Yulin, plus one more), using the format in `MFI:401-410`.
  - **A:** no custom air groups.
  - **B:** about 100 parked aircraft per base, 600 in total.
  - **C:** 500 parked plus 100 airborne on CAP with a HomeBase.
- **Record:**
  - aircraft accepted against requested per base (a capacity rule, GAME);
  - the common sheet;
  - any unprompted launches in the first 60 game minutes;
  - parked counts and CAP behaviour after a reload (`config.ini:9`; CAP after reload was fixed at `CL:49`).
- **Pass:** B costs at most 10% more FPS and time compression than A and loads at most 30 s slower; counts identical after reload; no mass launches.
- **Effect on the world build:**
  - Cheap: populate every world airbase at full inventory in one mission.
  - Expensive: keep inactive regions' inventories as roster data or Dynamic Unit Generation (`CL:344-349`), created when a region activates. That is a hybrid, not a split.

**P6 – Save/load fidelity of combat and supply state**
- **Setup:**
  - `usn_aoe_sacramento` with the SEST supply block alongside a receiver whose round `tools/check_reloadable.py` reports as reloadable, within SupplyRange and the speed limits (`SEST_Replenishment/vessels/usn_aoe_sacramento.ini:308-311`);
  - a target damaged by an `Attack=` entry with a fixed shot count (`MFI:505-512`);
  - a shooter that expends a known salvo;
  - one unit destroyed by `Action_DestroyUnits` at t = 30 s (`MFI:737`);
  - one trigger already fired and one pending at t+2 h;
  - an airbase with a parked group and a sortie in progress.
- **Procedure:**
  1. Save S1 mid-transfer.
  2. Restart the game, load S1 and save S2 at once while paused.
  3. Unpause for 5 minutes and save S3.
  4. Edit the base mission in the editor and try S1 again.
- **Compare:** `CurrentIntegrity`, `FloodingCompartments`, `Ammunition*_Count`, supplier `CurrentAmmo`, GeoPosition, Heading, VelocityInKnots, IsDestroyed, LastLaunchTime and `FlightDeck_*`.
- **Pass:**
  - S1 equals S2;
  - in S3 the supplier's stock keeps falling and the receiver's keeps rising;
  - the destroyed unit stays destroyed;
  - triggers fire exactly once;
  - S1 is unaffected by the base edit.
- **Effect on the world build:** a pass makes in-mission save/load the persistence vehicle. A field that resets cannot persist mid-mission. Run **P6-L**, a two-mission linear test campaign using CampaignRearm/Repair (`CL:1807`), which is required before choosing linked missions.

**P7 – Distance metric and path shape**
- **Setup:** centre 45, −30.
  - Lanes at 0N, 45N and 69.5N, each with a ship at 15 kt and one waypoint **60 true NM** east (x = 60, 84.9 and 171.3).
  - In each lane, a `UnitsInTheArea` trigger 30 true NM east, radius 10.
  - An aircraft with `UnlimitedFuel=True` flying from 60N 40W to 60N 20E at 450 kt; save at about 1.9 h of flight.
- **Expected times:**

  | Measure | If true NM | If file units |
  |---|---|---|
  | Ship arrival | 4.0 h in all lanes | 4.0 / 5.66 / 11.4 h |
  | Trigger at 69.5N | about 1.33 h | about 1.77 h |

  | Aircraft path model | Distance | Time | Mid-route position |
  |---|---|---|---|
  | Great circle | 1,737 NM | 3.86 h | 63.4N at 10W |
  | Along the parallel | 1,800 NM | 4.0 h | 60.0N |
  | File plane | 3,600 units | 8.0 h | – |

- **Effect on the world build (builder only):**
  - TRUE: convert B6 and `nm_between` to great-circle distance.
  - FILE-PLANE: the engine itself stretches east-west distance in every mission, so splitting cannot fix it. Author high-latitude distances in file units.

**P8 – Water at disputed anchorages**
- **Sites:** Hood Canal at Bangor (47.73, −122.72), Kola Bay at Severomorsk (69.07, 33.42) and Apra inner harbour (13.44, 144.66).
- **Controls:** Diego Garcia lagoon (−7.35, 72.43) and Cockburn Sound (−32.20, 115.72).
- **Setup:** one tiny file per site, each with a patrol craft and a submarine at periscope depth, each given a 2 NM waypoint, plus a `low` shore unit.
- **Pass:** the craft float and move 2 NM; the submarine is not stuck (`CL:861`); a screenshot shows water.
- **Effect on the world build (builder only):** water overrides where game water exists; otherwise pier-side land units plus an offshore anchorage.

### 6.4 What the probes cannot settle

- P0b, P4 and P5 measure this PC only. A pass is a lower bound on what the game can do; a fail is not an engine-wide limit.
- AI pathfinding on long coastal routes, such as Brest to the Mediterranean via Gibraltar, is not tested. Add it only if P2's merchant shows problems.
- Whether `LoadBackgroundData` creates every global entry stays open. Add a P4 variant only if a world background layer is planned.

---

## Appendix: discrepancies in the input findings, reconciled during verification

1. **Largest stock mission.** The game-data lens's "Red Madagascar 130 units" is a double count. `stock/missions/NATO/Red Madagascar 1985.ini` contains its `[Environment]`/`[Mission]` body twice (`:117-140` and `:945-968`), with 65 units per copy. The stock maximum is 87 declared units in `09 Shadows off Palawan.ini:277-287` (86 excluding one biologic).
2. **Diego Garcia lagoon.** It reads as **water** in Natural Earth 1:10m, because the atoll is drawn as a C-shaped rim (probe pass). The builder-limits lens's "on_land=True" was wrong. Hood Canal, Kola Bay and Apra inner harbour do read as land.
3. **"Already inside the proven range."** This is true for great-circle distance from the centre (needed 7,002 NM against 8,781 NM in a save) and for \|x\| (10,677 against 12,117.71 stock). It is **not** true for \|z\| (5,629 against 4,529 played) or for unit-to-unit separation (about 10,150 against 3,450 NM played). Hence P1 Variant C.
4. **Spread of the played NORTHERN FRONT mission.** The engine-written save measures 3,450 NM, against the mission file's 3,145 NM; units moved during play. Distance from the centre in the save is 6,444–8,781 NM great-circle (`scratch/savespread.py`). The lens figure of 7,300–8,240 NM covered the airbases only.
5. **Elapsed game time in New midgame.sav.** The existing-missions lens's "12:00 to 18:53" used the wrong base. The base was the 25 Aug 14:05 backup, which starts at 13:00 with `ConvertTimeToLocal=True`. Only "at least 45 minutes of activity" (`LastLaunchTime` 2,720 s) is established.
6. **Builder pool size.** Unique sea points are 2,277 or 2,496 depending on the replica; land points are 2,761. The docstring's 33,000 is the pre-dedupe count. The coverage conclusions are unaffected.

---

Scripts written for this report: `docs/world-sandbox/work/scripts/savespread.py` and `docs/world-sandbox/work/scripts/maxz.py`. The save-payload decode was checked inline.
