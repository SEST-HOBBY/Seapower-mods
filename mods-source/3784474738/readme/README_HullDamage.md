# Hull Damage 0.5.9 (AC Pack submod)

Keep HullDamage.dll and HullDamage.ini directly in Sea Power_Data/StreamingAssets/AC Pack. Enable AC Pack in Mod Manager and restart Sea Power. Set Enabled=false to disable only Hull Damage.

Missiles and shells now create local dents and overlapping native hull_damage decals on ships and submarines. Size and depth use the game's effective warhead power, ammunition Mass in kilograms and relative impact speed. Kinetic energy uses 0.5 * mass * relative speed squared. High-energy strikes now create substantially deeper and wider dents; larger warheads spread damage more widely. MaxLocalRadiusMeters=12 and MaxLocalDepthMeters=3 cap each new missile/shell dent independently of ship beam (12 m radius / 24 m diameter, 3 m displacement). Native decal footprints follow the capped radius. Existing saved local hits are also reduced to these caps on load, scaling depth with any radius reduction to retain safe strain. Raising the limits does not enlarge saved hits. Torpedo effects are unchanged. Geometric strain and overlap limits prevent folded/inverted surfaces. This is a bounded visual approximation. Mass is the ammunition entry's mass, including any fuel/booster mass the entry retains. Missing mass or velocity contributes no kinetic effect; warhead effects still work.

Missile/shell dents appear at full depth by default, with one shared mesh publication and no gradual deformation. Preparation, contact lookup and uploads remain queued: a heavy scene can delay visibility, but no intermediate dent poses are calculated. Instant local-only damage uses the original MeshRenderer with final vertex positions; it does not depend on a blendshape weight or substitute renderer. Concurrent torpedo motion retains its smooth transition. Set LocalAnimationSeconds above zero to restore gradual local deformation.

Normal startup emits one short readiness line. Real warnings and errors remain visible; routine effect diagnostics are suppressed.

Contact points are projected along the incoming flight direction onto the visible mesh, so deck/superstructure hits also work when the collision model lies below the visible surface. The matched triangle normal directs the dent and decals. If no visible triangle is found, the native contact is retained.

Shells below 75 mm no longer add deformation or extra Hull Damage decal records by default. The gate reads an explicit mm caliber from the ammunition filename; without one, it uses native WarheadData Power before armor/fragmentation modifiers. Known small calibers cannot bypass it through speed or power. Caliber/power eligibility is classified once per encountered ammunition name/base-power combination and cached across native copies. Repeated hits reuse the stored result; they do not parse caliber or compare these thresholds again. The stock 57 mm power is 1.5 and 76 mm power is 2.4; the unknown-caliber fallback of 2 is an approximation. Native game damage and hit effects continue. Existing saved dents remain.

Shell speed is sampled from the final flight segment before collision clipping. Missile speed comes from its current velocity, with target motion subtracted. The effect requires native hit data close to a surface contact; remote airbursts and secondary explosions are excluded. Armor that stops penetration reduces the visual effect. Small rounds below MinimumLocalPower are ignored. MaxLocalHits limits additional local damage records per vessel independently of torpedoes; after the limit, ordinary game damage and decals continue.

Torpedoes retain their existing behavior: surface vessels briefly lift/flex; directly fatal hits leave one permanent central keel crease with fracture marks and short-lived pieces cut from upper geometry. Surviving torpedo hits leave a dent after flexing back. Submarines receive local dents only. Missiles and shells do not trigger this whole-ship lift, keel crease or geometric cutting sequence. Fatal local hits can detach nearby complete submodels.

Edit [HullDamage] in HullDamage.ini beside the DLL, then restart:

    [HullDamage]
    Enabled=true
    MissileDamage=true
    ShellDamage=true
    MinimumShellCaliberMm=75
    MinimumUnknownShellPower=2
    MinimumLocalPower=0.5
    MaxLocalHits=12
    LocalAnimationSeconds=0
    OnlyFatalKeelBreak=true

| New key | Default | Valid values / meaning |
| --- | --- | --- |
| MissileDamage, ShellDamage | true | true / false, independent switches |
| MinimumShellCaliberMm | 75 | 0-1000 mm, inclusive minimum for shells; 0 disables the shell-specific gate |
| MinimumUnknownShellPower | 2 | 0-10000; native WarheadData Power threshold only when caliber is unknown |
| MinimumLocalPower | 0.5 | 0-10000; combined visual intensity threshold for missiles/shells |
| MaxLocalRadiusMeters | 12 | 0.1-1000 m; maximum local influence radius per missile/shell hit |
| MaxLocalDepthMeters | 3 | 0.01-100 m; maximum displacement per missile/shell hit |
| MaxLocalHits | 12 | 1-24 additional local damage records per vessel |
| LocalAnimationSeconds | 0 | 0: immediate finished dent; >0 to 5: animated duration in mission seconds |

| Key | Default | Valid values / meaning |
| --- | --- | --- |
| Enabled, UseHullDamageDecal, UseFractureDecals | true | true / false |
| SingleCrease | true | true: narrow central crease; false: previous broad bend profile |
| OnlyFatalKeelBreak | true | false also permits permanent bends on surviving torpedo hits; debris still requires a directly fatal torpedo hit |
| UseFlyingDebris | true | Automatic upper-model cuts and flying pieces on fatal surface torpedo hits |
| MaxFlyingFragments | 48 | 1-128 pieces; also limited to 120000 active fragment vertices |
| DebrisLifetimeSeconds | 4.5 | 2-30 native mission seconds |
| MinimumPower | 8 | 0-10000; torpedo threshold, native effective damage power |
| ReferencePower | 68 | 0.01-10000 |
| ReferenceDisplacement | 8000 | 1-1000000 tonnes |
| BaseBendDegrees | 12 | 0-20; bend strength before central-sag normalization |
| MaxTotalBendDegrees | 24 | 0-25 accumulated strength |
| BandLengthFraction | 0.08 | 0.02-0.4 of hull length; reference sag and preparation detail; broad mode widens for tall structures |
| DentBeamFraction | 0.06 | 0-0.15 of beam; base dent scale before energy and geometry limits |
| AnimationSeconds | 5 | 0.1-60 mission seconds for the hull sequence; may stretch under load |
| InitialLiftSeconds | 1 | 0.05-30; time to peak, capped at half the sequence |
| InitialLiftRatio | 0.75 | 0-2; initial upward bend relative to final sag |
| HeaveBeamFraction | 0.075 | 0-0.3 of beam at reference power/displacement |
| ElasticBendRatio | 0.25 | 0-0.5; surviving-hit bend amplitude |
| MeshUpdatesPerSecond | 20 | 1-60 target pose updates |
| PreparationBudgetMilliseconds | 2 | 0.25-8 ms shared main-thread scheduling budget per frame |
| MaxHits | 4 | 1-8 torpedo records; one additional fatal-break slot |
| MaxVerticesPerMesh | 300000 | 1000-1000000 prepared body vertices |
| MaxVerticesPerShip | 1200000 | 1000-4000000 prepared body and eligible fragment vertices, including LODs |


Undamaged ships keep their original shared render meshes and materials while damage geometry is prepared in reserve. They do not run per-frame damage-renderer, fragment or effect-anchor updates. After preparation, settled damage does not schedule further geometry jobs unless another hit or model change requires one. Before an immediately fatal hit, parts that move relative to the ship, including radar/gun descendants, are restored to their original geometry and excluded from deformation for that source mesh. Motion is detected from hierarchy transforms during the periodic model scan and before a new damage pose; a newly moving part may take up to three seconds to be excluded. Ship travel, roll and pitch do not count as relative part movement. Instant local hits upload and publish only meshes whose pose actually changes; untouched parts retain their existing renderer mesh.

Geometry, visible-surface lookup trees, transverse subdivisions and cut faces are prepared ahead of hits on the existing background worker and frame-budgeted queue. Hidden mesh uploads and shared interpolation keep all parts at the same animation phase. Extra subdivision supports local dents on sparse hull/deck polygons; vertex budgets can limit detail. More prepared geometry costs RAM/VRAM. Individual engine readbacks/uploads cannot be interrupted by the scheduling budget. Hits before preparation finishes wait for it. Pause freezes animation.

Cut faces use opaque damaged steel; fragment flight lasts up to 4.5 mission seconds by default. Whole submodels use a separate rigid snapshot path. Irregular meshes may produce imperfect seams. Over-budget cuts fall back to deformation. Unsupported or oversized individual meshes stay unchanged and are logged; supported hull/deck parts continue. Hull and broad surfaces are prepared before smaller details. The ship vertex budget counts prepared bodies and debris, not every unprocessed source mesh. If extra subdivisions or cut geometry exceed the remaining budget, preparation retains simpler deformation geometry where possible. Skipped meshes are not repeatedly retried unless their source mesh changes. Skinned meshes remain unchanged.

HD7 saves retain torpedo/local damage, animation progress and pending surface projections. HD1-HD6 remain readable; HD5 local contacts are corrected to the visible surface on load while preserving their saved strength. Loading restores damage without replaying old debris. Colliders, flooding, buoyancy and gameplay damage remain native. Surviving vessels retain native submodel animation; on a wreck, supported submodel frames are held for deformation.

The same DLL is checked offline against the installed public build and available archived release/beta assemblies. In-game appearance, actual FPS and current-beta gameplay support still require in-game validation.


UseFlyingSubmodels=true enables complete submodel detachment, with UseFlyingDebris=true as the master switch. Only a hit that immediately destroys a surface vessel can detach an assembly; surviving hits, later flooding and hits on an existing wreck cannot. Missile/shell selection uses mounting points inside the capped dent radius. Torpedoes use the prepared fracture band during the upward phase. Skinned models, separate units, hull-sized objects and over-budget assemblies remain in place. Before a fatal hit, registered submodels retain their native geometry. On immediate destruction, supported submodels join the same vertex deformation and published interpolation as the hull. Their native animation frames are held at the hit pose on the wreck. They are not split into duplicate geometric fragments; whole-submodel release retains its separate budgets.

MaxFlyingSubmodels=8 accepts 1-16. Additional fixed limits are 60000 vertices/32 renderers per assembly and 120000 vertices/96 renderers per hit. Parent assemblies include their descendant barrels/dishes and cannot be emitted twice. Render-only copies capture the currently displayed deformed vertices and share existing materials; unchanged parts retain their existing mesh. No weapon logic or colliders are cloned or reparented. Flight uses the existing low arc and DebrisLifetimeSeconds. Base covers use opaque hull_damage steel; mount scars use the existing damage decal system. Base covers approximate the assembly footprint. Native LOD/damage alternatives are hidden with the source. HD7 records fatal local outcomes; loading reapplies removal without replaying flight. Geometry and performance still need in-game validation.


Version 0.5.9 restores actual submodel mesh deformation only after an immediately fatal surface-vessel hit. Preparation is queued once at that point and can delay the visible damage sequence. Surviving hits keep the existing moving-part exclusion. Large/unsupported meshes, including the 366375-vertex Nimitz F/A-18 collection, remain excluded by the existing budgets. No rigid follow proxy is used. Whole submodels released as debris take a snapshot of their visible interpolated geometry, and both source and damage renderers are hidden together.
