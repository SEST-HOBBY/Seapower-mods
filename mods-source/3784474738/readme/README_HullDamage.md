# Hull Damage 0.4.2 (AC Pack submod)

Keep HullDamage.dll and HullDamage.ini directly in Sea Power_Data/StreamingAssets/AC Pack. Enable AC Pack in Mod Manager and restart Sea Power. There is no separate mod entry. Set Enabled=false to disable only Hull Damage.

Torpedo hits dent the hull and briefly lift surface vessels. Directly fatal hits leave a permanent central keel crease, overlapping native hull_damage patches and fracture marks. Surviving ships flex and recover, retaining their dent. Submarines receive local dents and damage patches only.

Version 0.4.2 fixes staggered visible mesh updates: the next deformation state is uploaded into hidden reusable meshes, then every part switches together. Unity blend shapes interpolate the complete bend, dent and shading normals each rendered frame. Decals and emitters follow the same transition. Each model part has one active render path and one LOD membership; its original renderer stays suppressed while the interpolated renderer is used. This addresses gaps and overlapping surfaces caused by different parts displaying different animation times. Double buffering uses additional memory. FPS and the actual visual result still require an in-game check.

Version 0.4.1 concentrates the bend on one narrow line through the impact. Default upward bend and whole-vessel lift are half their 0.4.0 values; the final central sag is retained. The rise takes one second with smooth acceleration and deceleration. Rendering interpolates the full vertex positions and shading normals between mesh updates. After the lift, bow/stern endpoints return to their original relative height; native pitching, sinking and listing still apply.

Fatal surface hits also detach actual upper-model geometry. Pieces now rise by at most about 3.3 additional metres from their release point, tumble gently and fall on the native mission clock. Their visibility limit is 4.5 mission seconds, or less when submerged. Cut faces are filled with opaque steel using the game's hull_damage texture. Closure faces on the remaining ship appear only at the exposed impact region. The lower hull remains connected.

Edit [HullDamage] in HullDamage.ini beside the DLL, then restart:

    [HullDamage]
    Enabled=true
    SingleCrease=true
    OnlyFatalKeelBreak=true
    UseFlyingDebris=true
    AnimationSeconds=5
    InitialLiftSeconds=1
    InitialLiftRatio=0.75
    HeaveBeamFraction=0.075
    DebrisLifetimeSeconds=4.5

| Key | Default | Valid values / meaning |
| --- | --- | --- |
| Enabled, UseHullDamageDecal, UseFractureDecals | true | true / false |
| SingleCrease | true | true: narrow central crease; false: previous broad bend profile |
| OnlyFatalKeelBreak | true | false also permits permanent bends on surviving hits; flying debris still requires a directly fatal hit |
| UseFlyingDebris | true | Automatic upper-model cuts and flying pieces on fatal surface hits |
| MaxFlyingFragments | 48 | 1-128 pieces; also limited to 120000 active fragment vertices |
| DebrisLifetimeSeconds | 4.5 | 2-30 native mission seconds |
| MinimumPower | 8 | 0-10000; native effective damage power, not explosive mass |
| ReferencePower | 68 | 0.01-10000 |
| ReferenceDisplacement | 8000 | 1-1000000 tonnes |
| BaseBendDegrees | 12 | 0-20; bend strength before central-sag normalization |
| MaxTotalBendDegrees | 24 | 0-25 accumulated strength |
| BandLengthFraction | 0.08 | 0.02-0.4 of hull length; reference sag and preparation detail; broad mode widens for tall structures |
| DentBeamFraction | 0.06 | 0-0.15 of beam |
| AnimationSeconds | 5 | 0.1-60 mission seconds for the hull sequence; may stretch under load |
| InitialLiftSeconds | 1 | 0.05-30; time to peak, capped at half the sequence |
| InitialLiftRatio | 0.75 | 0-2; initial upward bend relative to final sag |
| HeaveBeamFraction | 0.075 | 0-0.3 of beam at reference power/displacement |
| ElasticBendRatio | 0.25 | 0-0.5; surviving-hit bend amplitude |
| MeshUpdatesPerSecond | 20 | 1-60 target pose updates |
| PreparationBudgetMilliseconds | 2 | 0.25-8 ms shared main-thread scheduling budget per frame |
| MaxHits | 4 | 1-8 normal records; one additional fatal-break slot |
| MaxVerticesPerMesh | 300000 | 1000-1000000 prepared body vertices |
| MaxVerticesPerShip | 1200000 | 1000-4000000 prepared body and eligible fragment vertices, including LODs |

Preparation happens before hits across multiple frames. Subdivision, cuts, cap UVs, reusable geometry, fragment objects and bindings are prepared ahead of combat; numeric processing runs on a background worker. A hit before preparation finishes waits for it. Individual engine readbacks/uploads cannot be interrupted by the scheduling budget. Extra RAM/VRAM is used before combat. The visible hull sequence may slow under load so its initial lift is not skipped; debris flight does not inherit this slowdown. Mission pause freezes both.

Cuts use 18 shared oblique regions across static mesh parts, LODs and damage variants. The selected cut region approximates the hit location. The central bend itself follows the impact coordinate. Pieces come from eligible intact high-detail renderers, without model-specific radar/gun names. This is geometric cutting, not recognition of whole equipment assemblies. Caps approximate solid damaged steel rather than internal compartments. Highly irregular or nonmanifold geometry can still produce imperfect seams. Over-budget meshes keep ordinary deformation and log a skipped fracture.

The native explosion's immediate destruction outcome controls permanent failure. Later flooding does not upgrade a surviving hit. Existing wrecks do not break again. HD4 save records retain damage, animation progress and fatal outcomes; loading reconstructs missing geometry without replaying old debris. Airborne pieces are transient. Older saves remain readable; SingleCrease=true displays their bends with the new profile.

The effect changes rendered geometry, decals and non-colliding visual debris. Colliders, flooding, buoyancy, weapon transforms and gameplay damage stay native. Skinned or unsupported meshes are skipped with a log message.

The identical DLL is checked offline against the installed public game and archived release/beta assemblies. These checks do not establish in-game appearance, current-beta gameplay support or measured FPS improvements.
