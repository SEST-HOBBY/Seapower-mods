# ENV-00: map render targets

18 November 2026. SEST-DEV. Branch `sest-dev/serene-bardeen-nvnmk9`, started from
`feature/r15-sea-power-093` at `75b8a4268991849305f4938a04d95e6f606dc345` (re-checked on the
remote this session; no newer commit).

**Result: BLOCKED for a game-side hook.** The repository holds no IL listing or decompiled
source of `Seapower-Scripts.dll` 0.9.3 (aae79728) or of the Dynamic Campaign Mod (DCM) 0.25.0.1
covering their map drawing. No map class could be named with evidence beyond what is listed
below, so no diagnostic hook was written: a hook against a guessed type would be a claim, and it
could not be compiled here either (the runtime builds need the owner's captured references and a
.NET 8 Roslyn host, `integration/beta-feature-parity/build.py`).

What was produced instead: the georeferencing maths every target will need, tested
(`mno_env/overlay.py`, `mno_env/polar.py`), and a static proof rendered offline
(`docs/environment/map-proof/`, VISUAL DEMO ONLY).

## Matrix

| View | What renders it (evidence) | Can a georeferenced layer attach? | Confidence |
|---|---|---|---|
| Tactical map, 0.9.x | Sea Power's own map. Since the 26 Oct beta it is a 3D globe with a Lambert Conformal Conic play area; the editor saves `LambertParallel1/2`, `LambertAxisLatitude/Longitude`, `LambertExtent`, `LambertMarginNm`, `LambertControlPoint*` in `[Environment]` (`docs/beta-globe-readiness-20261027.md`). The R14 adapter for the third-party Topographic Map 1.6.2 hooks it through that mod's `GameHooks`/`MapHooks` and a deferred Noesis map patch (`integration/beta-feature-parity/tests/BetaApiTests.Topography.cs:16-85`). | Probably: R.A.T.S. (MIT, `struckl/SeaPowerTopo`) draws static imagery on the stock globe with a 1-degree sphere mesh. Not inspected in this session (outside the repository scope) and not verified on 0.9.3 by MNO. | Low: class names not established |
| DCM strategy map (GCO world view) | DCM's own UI: `DynamicCampaignMod.UI.CampaignUI.Tick()` is the per-frame entry MNO already patches (`integration/beta-feature-parity/runtime/WorldOperations.cs:144`); `WorldMapCostsButton.cs` inserts one Noesis control beside DCM's Economy button. How DCM draws its map (Unity mesh, texture, Noesis canvas or IMGUI) is **not recorded anywhere in the repository**. | Unknown. Only a UI control beside the map is proven (R14, 0.9.2). | Very low |
| DCM battle hand-off | `DynamicCampaignMod.Game.Battle.MissionWriter.Text` (token 0x06000a37) "emits native tactical mission settings and an environment map centre" (`docs/world-sandbox/engine-review/REVERSE_ENGINEERING_REVIEW.md:75`). | Not a map: this is where ENV-06 writes `[Environment]` and weather triggers (a postfix on the returned text, via `mno_env.mission_adapter.apply_plan`). | Medium for the hook point; its 0.25.0.1 signature on 0.9.3 is unchecked |
| Mission editor map | Sea Power's editor; the beta editor auto-generates the play area. | Out of scope for ENV; nothing should draw there. | n/a |
| Replay / debrief | `LinearCampaignMapViewModel` (native campaign map view model, `NativeCombatSurface.cs:369`) is used by MNO for the linear-campaign task-force panel, not for GCO. | No ENV layer planned. | n/a |

Three facts that block any GCO overlay today, independent of the renderer question:

1. `python3 tools/check_game_version.py` fails at R15 HEAD (`75b8a426`, checked in a clean
   worktree): *"3813157776 Dynamic Campaign Mod declares 0.8.3 <= v < 0.9.0, which excludes
   0.9.3"*. GCO runs inside DCM; until DCM runs on 0.9.3, no GCO environment feature can be
   tested in game (WORK-PACKAGES 1: "Dynamic Campaign Mod on 0.9.3: not established").
2. R15 itself has not run in game (PC-01).
3. The public-release 0.9.3 file is uncaptured (PC-02).

## What the owner can capture to unblock this

One read-only capture, no plugin: run the existing `tools/capture-beta-references.ps1` (it already
packs the managed DLLs and the Workshop plugins, including DCM's assembly) with Steam on the
0.9.3 build the owner plays. From that, the build assistant can list in IL, without running the
game:

- every type in `Seapower-Scripts.dll` and DCM whose name or fields mention map, globe, camera,
  Lambert, texture or `MeshRenderer`, with their `Awake/OnEnable/OnDestroy` lifecycle;
- `CampaignUI` members that own the strategy map and its camera;
- the `MissionWriter.Text` signature in DCM 0.25.0.1.

Only then should a diagnostic-only, off-by-default hook be written (`MNO_ENV_DIAG=1` in the
runtime's ini, logging type names and scene objects once per view change, changing nothing).

## Adapter interface left for the game side (DESIGN ONLY)

The layer is defined so the renderer question does not leak into the data side:

```
interface IMnoEnvGlobeTarget            // one implementation per proven view
  string Name                            // "tactical-globe", "dcm-strategy", ...
  bool   Attach(out string reason)       // false + reason on an unknown build: log, never throw
  void   SetLayer(string layer, Texture2D equirectTexture, float opacity)   // main thread only
  void   Detach()                        // destroys every object it created
```

`equirectTexture` is the plate-carree RGBA buffer `mno_env.overlay.build_layer(Equirect(...))`
produces: column 0 starts at longitude -180, row 0 at latitude +90, sampled at pixel centres,
so a UV sphere with the usual seam at 180 shows it without a visible break (the test pattern's
magenta band marks the antimeridian; `test_equirect_roundtrip_and_seam`). Polar views use
`PolarWindow` with EPSG:3976 / EPSG:3413, checked against PROJ 9.8.1.
