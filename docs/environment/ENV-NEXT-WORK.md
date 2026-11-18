# ENV-NEXT-WORK

18 November 2026. In order. No item changes R15 release priorities (`WORK-PACKAGES-ENV.md`).

## Blockers

| # | Blocker | Unblocks | Who |
|---|---|---|---|
| B1 | DCM declares `< 0.9.0`; `check_game_version.py` fails on it at R15 HEAD. GCO cannot be tested on 0.9.3 until DCM runs there. | every GCO-side ENV item | DCM author / owner PC (PC-01) |
| B2 | No IL of 0.9.3 `Seapower-Scripts.dll` and DCM 0.25.0.1 map and save code in the repository | ENV-00 hook, ENV-02 overlay, ENV-05 save id, ENV-06 postfix | owner: `tools/capture-beta-references.ps1` |
| B3 | Weather Lab not run in game | trust in native weather triggers, SeaState-to-wave mapping | owner: `ENV-PC-PLAYTEST.md` |
| B4 | Ice-shelf geometry is Natural Earth 1:10m (published, undated fronts) | dated fronts, calving events | optional: MEaSUREs (NSIDC-0709, needs an Earthdata login) or SCAR ADD |
| B5 | No verified ice capability for any unit; no icebreaker in the collection | ice access beyond "none" | owner / GM-05 |
| B6 | Data redistribution terms (ECMWF CC BY 4.0, OSI SAF, Open-Meteo) not reviewed for shipping tiles in a Workshop item | bundled real-data tiles | owner |

## Next concrete changes

1. Owner runs the Weather Lab card; record W1-W12 in `ENV-TEST-RESULTS.md`. If W5 gives a wave
   estimate, calibrate `mission_adapter.sea_state_from_hs` from it and allow 10-12 only then.
2. From the capture (B2): list map/globe/camera types and DCM `CampaignUI` map members; write the
   off-by-default diagnostic hook; update ENV-00 with evidence and a confidence grade.
3. Port `snapshot.read/validate`, `clock`, `grid.bilinear` and `overlay.Equirect` to C# under
   `integration/beta-feature-parity/runtime/Environment/`, behind `EnvironmentEnabled=false`,
   with the Python fixtures as test data (same numbers). Build only on the owner's toolchain.
4. ENV-06 first: a postfix on DCM `MissionWriter.Text` that calls the ported mission adapter, so
   GCO battles get location- and time-correct native weather. This needs no overlay and is the
   smallest GCO-visible step.
5. Run `tools/ingest_ecmwf_opendata.py` and `tools/ingest_osisaf_ice.py` once on real files on
   the PC; commit only the resulting manifest entry and hashes (not the data) until B6 is decided.
6. Static overlay on the first proven target, with the Layers dropdown (ENV-02), then time steps
   (ENV-03): 2048x1024 R8 per layer, updates every 5-10 game seconds, double-buffered.
7. Per-save sidecar wired to DCM save/load/save-as/delete events (ENV-05); A/B save test on PC.
8. Authored weather operations (ENV-08): one Drake Passage, one Weddell, one Ross approach (all
   need BA-09 Phase A data and PC-05 for anything south of the current -62 bound), one Indian
   Ocean monsoon front inside current bounds. Each starts as a scenario-wide native-weather
   mission (the Weather Lab method), not a spatial claim.
9. Iceberg and shelf layers only after B4, and only as warnings and route gating.

## Not to do

- No unit speed, endurance, sensor or damage change from weather or ice without in-game
  evidence for that effect.
- No thunderstorm field inferred from rain alone as an observation.
- No `Action_SetSnow` (no shipped file uses it).
- No live web request from the game.
