# Hull Damage 0.6.10

Keep HullDamage.dll and HullDamage.ini in Sea Power_Data/StreamingAssets/AC Pack. Enable AC Pack in Mod Manager and Hull Damage in the AC Pack settings menu. Fully restart Sea Power after changing the DLL or settings.

## Keel fracture

Directly fatal surface-vessel torpedo hits can leave a permanent keel crease. Coincident painted tear edges separate only through hull rotation. There is no additional strip pulled out of the exterior. Lip folds retain original UVs. The final wedge is limited to 2 m or 16% of beam, whichever is smaller, by limiting bend angle. A fitted interior with decks, frames, rear bulkheads, floors, ceilings and closed perimeter walls sits behind the opening. Deck levels repeat at about 2.8 m spacing. Cavity depth scales with beam (1.4-12 m), with an additional local limit before the hull centreline. The interior uses its own embedded steel atlas; exterior lips keep the ship paint. The two shell edges rotate about the upper structural hull and open below it. Existing native hit decals are reused; one compact destroyed_2 mark is a fallback when no native mark is nearby. If the interior vertex budget is exhausted, the painted tear is retained without extra room geometry. Other impacts keep their existing marks. The insert opens during the initial bend; it does not separate the vessel into two sections.

[HullDamage] in HullDamage.ini:

```ini
UseKeelGroove=true
KeelGrooveWidthMeters=3
KeelGrooveDepthMeters=0.8
UseFlyingDebris=true
UseFlyingFragments=false
UseFlyingSubmodels=true
```

| Key | Default | Values / effect |
| --- | --- | --- |
| UseKeelGroove | true | Enable the inward recess on directly fatal torpedo keel breaks |
| KeelGrooveWidthMeters | 3 | 0.25-12 m requested lip-detail width; capped at 1.5 m and ship dimensions, not the opening width |
| KeelGrooveDepthMeters | 0.8 | 0.05-3 m requested lip-fold depth; additionally limited by beam and groove width; interior depth is sized independently |
| UseFlyingDebris | true | Master switch for flying pieces and complete submodels |
| UseFlyingFragments | false | Legacy automatic cutting/ejection of superstructure chunks; keep false for the new appearance |
| UseFlyingSubmodels | true | Complete guns/radars and other eligible submodels can detach only on directly fatal hits |
| MaxFlyingSubmodels | 8 | 1-16; additional fixed geometry/rendering budgets apply |
| MaxFlyingFragments | 48 | 1-128; only relevant when legacy fragments are enabled |
| DebrisLifetimeSeconds | 4.5 | 2-30 mission seconds |

Surviving torpedo hits briefly flex and leave local dents. Submarines receive local dents without a global crease. Missiles/shells do not cause whole-ship lifting or this transverse keel recess. A later sinking does not turn a surviving hit into a fatal effect. Whole submodels still deform with the hull after an immediately fatal hit.

## Local impact effects

Missile/shell dents use effective warhead power, ammunition mass and relative impact speed squared. They appear at full depth by default. Native gameplay damage is unchanged.

| Key | Default | Values / effect |
| --- | --- | --- |
| Enabled | true | Enable Hull Damage |
| MissileDamage, ShellDamage | true | Independent local-effect switches |
| MinimumShellCaliberMm | 75 | 0-1000 mm inclusive minimum; 0 disables this shell gate |
| MinimumUnknownShellPower | 2 | 0-10000 native power; fallback when no explicit mm caliber is available |
| MinimumLocalPower | 0.5 | 0-10000 visual intensity threshold |
| MaxLocalRadiusMeters | 12 | 0.1-1000 m radius, independent of ship beam |
| MaxLocalDepthMeters | 3 | 0.01-100 m displacement per local hit |
| MaxLocalHits | 12 | 1-24 records, plus a reserved fatal record |
| LocalAnimationSeconds | 0 | 0: finished dent; >0 to 5: gradual deformation |
| UseHullDamageDecal, UseFractureDecals | true | Native damage marks / supplementary crack marks |

Shell eligibility is cached per ammunition definition. Small rounds retain native damage/effects. Geometry and overlap limits can reduce the configured dent size. Lower local caps also reduce existing saved dents when loading.

## Torpedo motion and budgets

| Key | Default | Values / effect |
| --- | --- | --- |
| OnlyFatalKeelBreak | true | Permanent bend only on immediately fatal hits; disabling does not enable nonfatal debris or grooves |
| SingleCrease | true | One narrow bend line |
| MinimumPower | 8 | 0-10000 native torpedo power threshold |
| ReferencePower | 68 | 0.01-10000 |
| ReferenceDisplacement | 8000 | 1-1000000 tonnes |
| BaseBendDegrees | 12 | 0-20 |
| MaxTotalBendDegrees | 24 | 0-25 accumulated bend strength |
| BandLengthFraction | 0.08 | 0.02-0.4 of hull length |
| DentBeamFraction | 0.06 | 0-0.15 of beam |
| AnimationSeconds | 5 | 0.1-60 mission seconds; fixed to hit time |
| InitialLiftSeconds | 1 | 0.05-30; at most half of the sequence |
| InitialLiftRatio | 0.75 | 0-2 |
| HeaveBeamFraction | 0.075 | 0-0.3 of beam |
| ElasticBendRatio | 0.25 | 0-0.5 |
| MeshUpdatesPerSecond | 20 | 1-60; maximum scheduling rate, motion keyframes also follow phase deadlines |
| MaxHits | 4 | 1-8 torpedo records, plus a reserved fatal-break record |
| PreparationBudgetMilliseconds | 2 | 0.25-8 ms shared scheduling budget per frame |
| MaxVerticesPerMesh | 300000 | 1000-1000000 |
| MaxVerticesPerShip | 1200000 | 1000-4000000, including LODs |

## Limits

Geometry and a bounded set of possible fracture lines are prepared in the background before impact. At a fatal hit, the closest prepared line is selected for both crease and recess. The recess and its dark steel surface open progressively during the initial upward motion (normally one mission second); no new groove is cut after the five-second bending sequence. Local impact dents and marks retain their actual hit position.

The candidate spacing is approximately four metres with default settings on ordinary ships, with at most 64 lines per ship; larger vessels or wider grooves increase spacing. Lines cover the same central 80% of hull length used for bending. Shared base geometry and cached patches count against the existing preparation budgets. Only the selected compact variant enters the render buffers; other candidate variants are not rendered.

Motion follows the mission clock, including pauses. Shared interpolation prefetches phase endpoints with a latency-aware lead; visible motion jobs take priority over background warmup. The renderer is designed to interpolate each frame, but the reported in-game stepped animation remains unresolved in this release. Late batches start at the preceding visible endpoint instead of snapping through an expired interval. Very late cold batches can require a short catch-up after the nominal deadline. Individual engine readbacks/uploads cannot be interrupted: cold, newly spawned or unusually large models can still publish late under load and catch up to the hit timeline. After the last visible animation frame, the original MeshRenderer renders the final deformed vertices and the temporary interpolation renderer is deactivated. Further hits can reactivate interpolation.

Unsupported/skinned/oversized meshes remain unchanged. The 366375-vertex Nimitz aircraft collection stays excluded by the default limit. If detailed groove preparation exceeds a surface budget, it retains smooth procedural deformation without the detailed insert; it does not retry expensive cutting after impact. The shallow insert works per clipped surface, including open/non-manifold sheets; it does not reconstruct a complete ship interior or repair arbitrary overlapping model defects. Tall masts and uncut submodels receive the hull bend without a vertical groove. Legacy fragment cutting and the new groove are alternative looks; keep UseFlyingFragments=false.

Saves retain damage and fatal outcomes. Loading reconstructs the recess without replaying old debris. Repair restores native meshes. Colliders, buoyancy, flooding and damage remain native. On wrecks, supported submodel animation frames are held to avoid applying a second rotation after mesh deformation.

Identical-DLL API, activation and numerical checks cover the installed public build and available archived release/beta assemblies. Appearance and FPS still require in-game validation.

## Interior fitting

The module is clipped against local hull-surface footprints during preparation. This works with open triangles without requiring a global volume Boolean. It is a visual cavity, not a reconstruction of actual ship compartments or a guarantee of watertight global topology on arbitrary overlapping models. Two closing sidewalls are generated after clipping; there is no open view out of the insert sides.

At most 48 shared candidate lines are prepared per vessel; a fatal hit uses the nearest line for both the crease and tear. Maximum offset is half the candidate spacing. Detail adapts from the authored module to simple decks/frames/walls when the existing vertex cache is tight. All shapes and textures are embedded in HullDamage.dll; no separate assets or helper DLLs are required. New geometry is not cut in the hit or render loop. Existing saves prepare their geometry again using this layout.

Release and archived beta checks are offline. Actual in-game appearance, FPS and the previously reported uneven bend animation still require gameplay verification.

0.6.5 fixes the startup texture upload: embedded level-zero pixels are uploaded explicitly, then Unity generates mipmaps. Geometry and budgets are unchanged from 0.6.4.

0.6.10: Torpedo deformation uses the native decal contact. Fatal crack edges rotate with their attached hull half. Transparent parts do not define hull dimensions or generate rooms. Combined opaque hull/deck-family clipping bounds inserted rooms; original attachment vertices are reserved before detailed preparation. Ships of 30,000 tonnes and above retain local dents only, without global torpedo bending or keel tears. Restart the game to load an updated DLL.

0.6.10: Bow, hull, stern, body and deck meshes with a common model prefix share the fracture layout, dimensions and interior boundary. Interior rear lining stays connected across the tear. No global ocean rendering settings are changed; water appearance requires in-game review.

0.6.10 adds an opt-in, bounded event capture for investigation of missing torpedo effects. Damage rules, geometry and animation remain as in 0.6.8. This is a diagnostic update, not a confirmed fix for the intermittent failure.
