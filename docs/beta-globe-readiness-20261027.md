# Sea Power globe public beta: SEST readiness (27 Oct 2026)

**Scope:** October 26 public beta; Triassic Games plans general release November 11. Evidence is the publisher's announcement supplied by the player. This branch contains *only read-only analysis tools and preparation*. No mission edits, rewritten coordinates, altered weapons, upgraded DLLs, installed mod order or Workshop uploads.

## Background and compatibility risks

The beta replaces the former map geometry with a 3D globe / Lambert Conformal Conic map-and-terrain system; mission editor auto-generates a play area and exposes centre, rotation and edge length (maximum 5,000 NM per side). At higher latitudes, actual east-west separation, fuel feasibility and engagement timings can differ substantially from the old engine. More flexible sides/alliances, radar and sonar, weapons and CIWS, aircraft/carrier logic, campaign UI, triggers and layered overrides require independent regressions. **Do not treat this as only a map-rendering update.**

The existing SEST authors' coordinate convention is documented in docs/world-sandbox/work/scope-and-performance.md: X=(lon-centreLon)*60 and Z=(lat-centreLat)*60. The historical convention is not proof of the new engine's INI parsing or runtime coordinate mapping. The repo's geometry and route solvers use planar distances (including math.hypot) and/or arcminute-to-mile approximation. Keep raw mission positions unchanged until a beta editor round-trip and geolocation comparison prove what is needed. DO NOT bulk replace x coordinates with x*cos(lat): that may relocate units wrongly or double-correct a mapping the engine already handles.

## Tools

Read-only inventory, no game install needed:

    python3 tools/audit_beta_map_geometry.py
    python3 tools/audit_beta_map_geometry.py --csv > beta-geometry.csv
    python3 -m unittest discover -s tools/tests -p 'test_beta_map_geometry.py'

The audit inventories authored numeric unit positions, numeric waypoints and spawn centres, estimates latitude/longitude spans using the documented old SEST convention, flags dateline crossings and high latitudes, and highlights missing explicit play-area metadata. P1 is review priority, **not confirmed breakage**. Reports include approximate east-west arcminute distance and latitude-scaled surface estimate; no result constitutes a validated beta in-game range. Dynamic waypoint tokens (Turn/Course/Loop), trigger area details, formation-derived positions, editor-defined play areas and mission-conditional placements need separate review. Parent-relative positions are deliberately excluded from global-coordinate estimates.

## Review priorities

1. **P1:** Southern Reach Macquarie Passage (SR04; map latitude -54.3); high latitude missions and their distance/time/aircraft reach. Check all Southern Reach SR01-SR12 at 50 degrees S or more, and any Antarctic missions at 60 degrees S. Inspect the resulting editor play area and map rendering.
2. **P1:** World Sandbox and Northern Front wide-area missions; existing project scope probes report very large map-centre offsets and distant ships/aircraft/land assets. Check the 5,000 NM play-area side cap against *actual intended playable region*, not against a unit's arbitrary legacy MapCenter. Do not shrink world content automatically.
3. **P1:** Dateline edge cases: both [-180,180] and [0,360] representations, waypoints and triggers across seam. The old engine used awkward longitude wrapping; the new system claims to solve it.
4. **P2:** Tasman Shield, Southern Reach subtropical approaches and routes. Compare true timings, escort/strike-aircraft fuel, torpedo and missile range; avoid arbitrary global weapons buffs/nerfs.
5. **P2:** Anchor Chain 1.1.0 ABI. SEST menu and runtime-fixes compile against a non-shipping stub; capture installed AnchorChain version/hash, run start/load/save/UI tests, and rebuild against updated APIs only if necessary.
6. **P2:** New override file layering. Map what beta actually supports and resolve interaction with existing whole-file overrides, #!alias, #!extend, systems/language merges, load order, SEST Intercept Model and SEST Collection Fixes before migrating anything.
7. **P2:** Campaign Task Force, F11 costs, debrief styling, campaign prep imagery, side alliances and sensor sharing, mission editor trigger handling and ROE. The editor has historically rewritten Hold/Tight to Free; compare before/after saves.
8. **P2:** Aircraft/carrier support and Harpoon P-8 release in SW05; the P-8/Harpoon issue is *unverified* and must not be solved with a global missile edit. Retest SW05 and SW02 plus deck operations, recovery, replenishment and cross-deck helicopter procurement.
9. **P2:** Performance/stuttering. Capture fps/frame-time, VRAM, unit/contact counts, map extents, BepInEx log and Unity log on same scenarios and comparable settings before/after; test smaller play area only as an A/B, not permanent blanket policy.

## Reproducible beta acceptance matrix

Use **separate stable and beta copies/backups**, and record actual build, versions and mod hashes. Do not run sync-sest.ps1 install on the stable game to test the beta; it is an installer, not an audit. No need to re-author missions before comparing.

| Scenario/system | Baseline and beta checks | Evidence |
|---|---|---|
| SW05 Weapons Free | Start, task force placement, P-8/Harpoon, contact exchange, range, win/debrief | map screenshot, logs, save |
| SW02 Steel Highway | AI/ROE, deck operations, stutter A/B | same camera/settings, logs |
| SR04 Macquarie Passage | 54S geometry, route/radar, 30-min service, Bear/Midas and launch/recovery | screenshot, save, timed notes |
| Southern Reach near 60S | play-area centre/rotation/edge, actual position and fuel | editor screenshot, route lengths |
| Northern Front III | distant units, world extent, loading, terrain and frame time | editor and game screenshots |
| SEST World Sandbox x2 | campaign selection, purchases, resupply, persist/load, global geography | logs, save and menu screenshots |
| Sulu Line | frigate/destroyer helicopter options, costs and flight-deck UI | screenshot |
| Red Line 01/02 | pacing/combat, alliance and ROE changes, trigger conditions | save and timeline |
| F11 and menus | cumulative/last-game costs, debrief text, menu imagery, map key conflicts | screenshots |
| Weapons and sensors | CIWS, lookdown, sonar, SEST interception model, salvo and launch-failure behaviour | logs and mission reproducer |

Before each play: capture game and DLL version information, deployed mod list and load order, and hash existing binaries. After each play: compare with beta and preserve the original full logs locally; produce a separate review archive. Run the repo's checks:

    python3 tools/check_game_version.py
    python3 tools/check_vanilla_drift.py
    python3 tools/check_load_order.py
    python3 tools/check_alias_bases.py
    python3 tools/check_dependencies.py
    python3 tools/check_weapon_employment.py
    python3 tools/preflight.py --all

If the version checker fails on *new* beta version strings, do not use --bump until the exact new game version is captured and the branch is intentionally prepared. The "mark mods compatible" script only changes compatibility metadata and does NOT validate functionality.

## Release gate

- No production main change, Workshop upload or broad migration until stable regressions pass, fresh workshop snapshot reconciled and beta playtests evidence is collected.
- Treat separate open PRs for World P-8 model and debrief/SW05 Harpoon investigation as independent; bring them in by reviewed cherry-picks after tests, never by blind merge.
- Confirm AnchorChain runtime compatibility and game ABI against beta; do not ship the 1.1.0 stand-in stub.
- Retain the working pre-beta install and complete rollback path.
- Capture the published November 11 build and re-run gate; beta pass does not automatically prove release pass.

**Known audit limits:** file scan may include generated/browser duplicate missions; numeric waypoints are approximated only when directly parseable; the scan is a screening prioritizer, not an authoritative geodesic model or game parser.
