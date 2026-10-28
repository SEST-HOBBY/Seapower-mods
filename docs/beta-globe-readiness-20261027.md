# Sea Power globe public beta: SEST readiness (27 Oct 2026, revised 28 Oct)

**Scope:** the October 26 public beta; Triassic Games plans general release on November 11. The evidence for both is the publisher's announcement supplied by the player. The work behind this note adds a read-only audit tool (`tools/audit_beta_map_geometry.py`), its tests (`tools/tests/test_beta_map_geometry.py`) and this note. It edits no mission, coordinate, weapon, DLL, mod order or Workshop item.

## Background and compatibility risks

Per the announcement, the beta replaces the former map geometry with a 3D globe / Lambert Conformal Conic map-and-terrain system, and the mission editor auto-generates a play area and exposes its centre, rotation and edge length (at most 5,000 NM per side). At higher latitudes, actual east-west separation, fuel feasibility and engagement timings can differ substantially from the old engine. More flexible sides/alliances, radar and sonar, weapons and CIWS, aircraft/carrier logic, campaign UI, triggers and layered overrides need their own regression tests. **Do not treat this as only a map-rendering update.**

SEST's coordinate convention is documented in `docs/world-sandbox/work/scope-and-performance.md` (section 2.1): x = (lon - centre lon) x 60 and z = (lat - centre lat) x 60, with no cos(lat) factor; that report checked it against engine-written saves. The 0.8.7 game code agrees for waypoints: `SceneCreator.ReadWaypoints` scales x and z by 27.5595 Unity units per NM, and `Utils.worldPositionFromUnityToLongLat` turns 330.714 units into 0.2 degree, so one NM of offset is one arcminute of latitude or longitude at any latitude. That is what 0.8.7 does, not proof of what the beta does with the same numbers. The repo's mission tools (`integration/campaign/build_pack.py`, `integration/mission-seeds/sea_routes.py` and others) use planar distances (`math.hypot`) on these offsets. Keep raw mission positions unchanged until a beta editor round-trip and a geolocation comparison show what is needed. **Do not bulk-replace x with x*cos(lat):** that may move units to the wrong place or double-correct a mapping the engine already handles.

## The audit tool

Read-only; no game install needed:

    python3 tools/audit_beta_map_geometry.py
    python3 tools/audit_beta_map_geometry.py --out beta-geometry.csv
    python3 -m unittest discover -s tools/tests -p 'test_beta_map_geometry.py'

`--out` writes the CSV as UTF-8. `--csv` prints the same CSV to standard output instead; in Windows PowerShell 5.1, `>` saves that as UTF-16, so use `--out` there.

By default it reads the campaign missions (`integration/campaign/SEST_Campaign/campaigns`), the mission seeds (`integration/mission-seeds`) and the two World Sandbox campaigns (`integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns/*/campaign.json`). `--root` takes any INI, `campaign.json` or folder instead.

- **Missions:** unit positions, random-spawn centres and waypoints, decoded with the convention above. A waypoint is `x,height,z` (the height may be a word such as `Periscope` or `BelowLayer`), optionally followed by orders after `/` or the broken bar (`SetTelegraph`, `SetSensors`, `SetWeaponStatus`, `AttackAtWaypoint`); `Loop` ends the route, as it does in the 0.8.7 reader. Keyword legs that the game places at run time (`Course`, `Turn`, `FollowLoose` and the like) are counted, not mapped, and malformed tokens (fewer than three fields, for example) are counted separately; no SEST mission has either today. Each row gives the east-west extent in file units ("old", the flat-map distance) and scaled by cos(latitude) (what the same latitudes and longitudes measure on a globe), the north-south extent, and the great-circle distance from the map centre to the nearest position when that is over 1,000 NM. Parent-relative positions (`PositionRelativeTo`) are left out.
- **World Sandbox:** bases and their airfields, placed forces, patrol rings, traffic lanes and airways, all already geographic latitude/longitude. Each campaign row gives the latitude and longitude range, positions written past 180, route legs that cross 180, positions at 50 degrees or more and positions outside the campaign's bounds, with the names listed under the row. The tactical maps the game generates for each engagement are not modelled.
- **Play area:** no SEST mission sets a play-area key, so the beta editor's auto-generated play area is unverified for every one. The tool says this once under the mission summary.

P1/P2/P3 is a review order, **not confirmed breakage**: P1 is a position or map centre at 50 degrees or more, a crossing of 180, or an extent of 4,500 NM or more; P2 is 35 degrees or 2,500 NM. No result is a validated beta range.

**Result on 28 Oct (repo data as of a3c42251):** 119 missions, P1 46, P2 16, P3 57, from 11,307 positions; every waypoint token maps, no mission crosses 180, and none sets a play-area key. Both World Sandbox campaigns are P1.

## Review priorities

1. **P1: Southern Reach and the far south.** SR04 Macquarie Passage (map centre 54.3S) reaches 56.5S; SR01-SR11 all reach 50S or more, and SR01, SR07, SR08 and SR10 reach 60S or more (SR08 The Gateway to 77.8S, SR01 Southern Departure to 66.7S). Tasman Shield 02, 06 and 11 pass 50S. SR12 (41.5S) is P2. Check distance, time and aircraft reach, and inspect the editor play area and map rendering.
2. **P1: missions on the Northern Front datum.** 21 mission seeds (Northern Front II and III, the SEST NF3 scenarios, AUS DEF, DARWIN US SUPPLY, both Sulu Sea Offensive drafts and others) use 54.27N 26.28W as their map centre, 4,495-7,642 NM from their nearest position. 20 of them have no position at 50 degrees or more; 17 are P1 only because of the centre (the other three, NORTHERN FRONT III FINAL NEWEST, SEST NF3 - Boomer Hunt and SEST NF3 - Sanctioned Convoy, also span more than 4,500 NM east-west). If the beta builds the play area (at most 5,000 NM a side) round the map centre, none of their positions would be inside it. Check the play area against the region actually played, not against the legacy centre. Do not shrink or move content automatically.
3. **P1: World Sandbox (both variants).** The builder writes longitudes in a continuous frame, -100 to 258 with the seam over Mexico, so Pacific places east of 180 are 180+ (San Diego 242.8, Pearl Harbor 202.055): 36 positions per variant, at five US bases, the Carl Vinson group, four patrols, the Trans-Pacific lane and the Honolulu-San Diego airway (see the comment above `BOUNDS` in `integration/world-sandbox/build_dynamic_campaign.py`). One Trans-Pacific leg crosses 180 (30N 160E to 24N 190, which is 170W). 78 positions in the world campaign and 87 in the regional one are at 50 degrees or more: Kola and the Northern Fleet, Norway, the Baltic and North Sea bases, the UK, Kamchatka, the Falklands, Punta Arenas and the inland Russian bomber bases (Engels, Belaya, Ukrainka). Check campaign start, purchases, resupply, save/load and the engagements generated at those places.
4. **P1: dateline handling.** Beyond the World Sandbox, no mission has positions on both sides of 180; the closest is Tasman Shield 03 Chatham Watch, whose positions reach 179.6E. Check both the -180..180 and the 0..360 forms in the beta, including waypoints and triggers near the seam.
5. **P2: Tasman Shield, the Southern Reach approaches and their routes.** Compare true timings, escort and strike-aircraft fuel, torpedo and missile range; avoid global weapon buffs or nerfs.
6. **P2: Anchor Chain ABI.** The menu and runtime plugins are compiled against a stand-in for Anchor Chain 1.1.0 (`integration/menu-background/stubs/AnchorChain.cs`, never shipped). Record the Anchor Chain version and hash the beta loads, run start/load/save/UI tests, and rebuild against an updated API only if needed.
7. **P2: override file layering.** Map what the beta supports and how it interacts with the existing whole-file overrides, `#!alias`, `#!extend`, systems and language merges, load order, the SEST Intercept Model and SEST Collection Fixes before migrating anything.
8. **P2: campaign UI and editor behaviour.** Campaign Task Force, F11 costs, debrief styling, campaign prep imagery, side alliances and sensor sharing, trigger handling and ROE. The editor has historically rewritten Hold/Tight to Free; compare saves before and after.
9. **P2: aircraft and carriers.** Retest SW05 (P-8 Harpoon release) and SW02 (deck operations), plus recovery, replenishment and cross-deck helicopter procurement. Fix any problem in the unit or weapon concerned, never with a global missile edit.
10. **P2: performance and stutter.** Capture fps/frame time, VRAM, unit/contact counts, map extents, the BepInEx log and the Unity log on the same scenarios and comparable settings before and after. Test a smaller play area only as an A/B, not as a blanket policy.

## Reproducible beta acceptance matrix

Use **separate stable and beta copies or backups**, and record the game build, versions and mod hashes. Do not run `tools/sync-sest.ps1` against the copy you keep for stable play to test the beta: it pulls, installs and reorders mods; it is an installer, not an audit. Missions do not need re-authoring before the comparison.

| Scenario/system | Baseline and beta checks | Evidence |
|---|---|---|
| SW05 Weapons Free | Start, task force placement, P-8/Harpoon, contact exchange, range, win/debrief | map screenshot, logs, save |
| SW02 Steel Highway | AI/ROE, deck operations, stutter A/B | same camera/settings, logs |
| SR04 Macquarie Passage | 54S geometry, route/radar, 30-min service, Bear/Midas and launch/recovery | screenshot, save, timed notes |
| SR01/SR07/SR08/SR10 (60S and beyond) | play-area centre/rotation/edge, actual positions and fuel | editor screenshot, route lengths |
| Northern Front III / SEST NF3 Carrier Duel | where the play area lands when the centre is 5,900-7,600 NM from every unit; distant units, loading, terrain, frame time | editor and game screenshots |
| SEST World Sandbox x2 | campaign selection, purchases, resupply, save/load; engagements near San Diego, Pearl Harbor, Kola and the Falklands | logs, save and menu screenshots |
| Sulu Line | frigate/destroyer helicopter options, costs and flight-deck UI | screenshot |
| Red Line 01/02 | pacing/combat, alliance and ROE changes, trigger conditions | save and timeline |
| F11 and menus | cumulative/last-game costs, debrief text, menu imagery, map key conflicts | screenshots |
| Weapons and sensors | CIWS, lookdown, sonar, SEST Intercept Model, salvo and launch-failure behaviour | logs and mission reproducer |

Before each play, record the game and DLL versions, the deployed mod list and load order, and hash the installed binaries. After each play, keep the full logs locally and make a separate review archive. Run the repo's checks:

    python3 tools/check_game_version.py
    python3 tools/check_vanilla_drift.py
    python3 tools/check_load_order.py
    python3 tools/check_alias_bases.py
    python3 tools/check_dependencies.py
    python3 tools/check_weapon_employment.py
    python3 tools/preflight.py --all

If the version checker fails on a new beta version string, do not use `--bump` until the exact game version is captured and the change is intended. `tools/mark-mods-compatible.ps1` (and SETUP's equivalent for players) changes compatibility metadata only; it does not show that a mod works.

## Release gate

- No Workshop upload and no bulk mission change for the beta until the stable regressions pass, a fresh Workshop snapshot is reconciled and beta play-test evidence is collected.
- Confirm that the Anchor Chain the beta loads still provides the `ACPlugin` attribute and `IAnchorChainMod` interface the stand-in declares, and that the game API the SEST plugins call is unchanged.
- Keep the working pre-beta install and a complete rollback path.
- Capture the published November 11 build and run the gate again; a beta pass is not a release pass.

**Known audit limits:** the mission seeds include drafts and near-duplicates (for example NORTHERN FRONT III FINAL and FINAL NEWEST); the default roots leave out the mission-browser copies under `integration/campaign/SEST_Campaign/missions` and the dist copies, which repeat the campaign files. Positions come from the 0.8.7 convention only; formation offsets, trigger areas, editor-defined play areas, conditional placements and the World Sandbox's generated engagement maps are not modelled. The tool is a screening aid, not a geodesic model or a game parser.
