# Environment work: transition note (25 Nov 2026)

This is a starting point for the next project. It covers the environment layer: weather, ocean, sea ice, icebergs,
ice shelves, sensors and file-layer probes. Nothing listed here is IN-GAME TESTED.

## Branches

| Branch | What is on it | Owner |
|---|---|---|
| `sest-dev/serene-bardeen-nvnmk9` | `integration/environment/` (Python model, data, 222 tests), the C# ice drop-in, the hand-offs, `docs/environment/` | this work |
| `feature/mno-r16` | The battle and campaign runtime (sea ice, storms, local weather, the GCO campaign), the 261123 port and the Workshop adapters | the holistic session |

The two branches share one thing: the battle sea-ice model. r16's `SeaIceModel.cs` is a port of this branch's
`mno_env/seaice.py`, and the generated data on r16 is pinned to that file's SHA-256. Change `seaice.py`, `ice.py` or
`geo.py` here and r16 must be regenerated (see `integration/environment/handoff/r16-sea-ice/README.md`).
`tests/test_handoff_r16_sea_ice.py` fails when that is needed.

## Done in this stretch

- **Sea ice:**
  - Okhotsk, Bering and Chukchi now follow the NSIDC G02135 v4.0 regional monthly medians.
  - The old model kept heavy Okhotsk ice all summer and had half the real Bering ice.
  - Applied to `feature/mno-r16` as `6e4d87784`.
  - Details and the seams that remain: `SEA-ICE-MARGINAL-SEAS.md`.
- **Icebergs:** `mno_env/icebergs.py` and `data/iceberg-climatology.json` give WMO size classes in 17 regions, by month, with
  a source per number. Write-up: `ICEBERGS.md`.
- **Ice shelves:** `mno_env/iceshelves.py` and `data/ice-shelf-attributes.json` add the front cliff, draft, depth, dated
  events and a no-go rule with stand-off. Write-up: `ICE-SHELVES.md`.
- **C# drop-in:** `integration/environment/runtime-drop-in/ice-features/` draws cliffs and bergs and applies the no-go rule.
  - It is OFF unless `IceShelves=1` / `Icebergs=1`.
  - 6771 Mono checks pass.
  - It is NOT yet registered in r16's `RuntimeFixesMod`; its README gives the one call needed.
- **GCO rename:** the text patch and PC rebuild steps are in `integration/environment/handoff/gco-rename/`.
- **Layer probes:** `RUN-LAYER-PROBE.ps1` and `PC-PLAYTEST-STEP-BY-STEP.md` step 5b are ready for the PC.

## Open: needs the owner's PC

1. **GCO runtime rebuild.** The newest compiled runtime (R15) still shows "Global Maritime Operations 2028".
   - Rebuild with `build-roslyn.ps1` against the Build 261123 capture.
   - Apply `0001-gco-rename-text.patch` first, unless r16 has already fixed the read-me and `test_regional_expansion`.
2. **Layer probes.** Run `-Scan`, then the probes in step 5b. Until rows A, A2, B, C or D, and L pass, no per-mission
   `[Sonar]` file is written.
3. **Sensor PC tests:** W5, RAIN, FOG and LAYER in `SENSOR-PC-TESTS.md`.
4. **Sea ice in game:** r16's `SeaIceTests.cs` needs the game assemblies, so it was not run here. Check that the
   Okhotsk ice is gone in July and that the Bering ice reaches about 60N in March.

## Open: decisions not yet made

- The GCO start date: 14 Sep or 1 Oct 2028.
- The weather bounds: 62S–74N or 72S–81N. r16 uses 72S–81N.
- One sea-ice noise curve and one wave-damping rule. This branch and r16 still differ.
- Whether r16's environment features default OFF when a switch is missing. Today they default ON, against the OFF-by-default
  rule.
- Whether to register the ice-features drop-in in r16.
- The Sensor Weather module for Sensor View. It exists as a proposal only; Sensor View is now an integration target in
  r16's `docs/mno/OWNER-DECISIONS-20261125.md`.

## Known limits (documented, not bugs)

- **Regional sea-ice seams:**
  - The Chukchi north border runs the wrong way in Aug–Oct 2016–2025, with a step of up to 67 points.
  - Bering Strait has steps in December and from late May to June.
- **Estimates:** several iceberg densities, the Okhotsk melt order and the Kotzebue landfast term are marked ESTIMATE in
  the data.
- **`sensor_brief` bugs:**
  - It tags all visibility as GAME.
  - Its rain gate ignores the 0.3 mm/h clear threshold, snow and clear cloud.
- **Fair-mode leak:** r16's `LocalWeatherView` samples an attached enemy unit's true position.

## Rules this work followed

- Environment features are OFF by default.
- No network calls in the game loop.
- Every number carries a source, and estimates are marked.
- Nothing is called IN-GAME TESTED without the owner's record in ENV-TEST-RESULTS.md.
- Never publish to Steam, never create a new Workshop item, and never delete item 3812461539.
- Commits use author SEST-DEV, with no AI attribution in public copy.
