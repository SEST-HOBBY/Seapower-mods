# Multi-Stage Missiles 1.7.1

Optional sounds for native INI particle effects: [INI effect audio](README_IniEffectAudio.md). Configure per-effect volume, audible distance in metres, one-shots/loops, delay, pitch and fades. Custom WAVs use the installed CustomAudioLoader.

Stage motors, ignition delays, automatic BurnTime transitions and animated stage-owned submodels: [configuration](README_StagePropulsionAndSubmodels.md). Native thrust can optionally add to stage thrust. Submodels disappear on stage changes unless the receiving stage enables InheritSubmodels.

Optional independent missiles, bombs, torpedoes and native chaff clouds are configured in [Submunitions](README_Submunitions.md). Glow and visual jettison continue to work separately. No ammunition is opted in automatically. Release and beta evidence is offline only.

Composite direct INI effects can opt out of native effect pooling per ammunition with `IndependentEffectInstances=True` in `[Models]`. This covers all direct effect slots on that ammunition while leaving effect classes and unconfigured ammunition on the base-game pool. Details and limits are in [Submunitions](README_Submunitions.md).

New in 1.5.2: set both thermal speed thresholds to `-1` for time-driven engine glow using stage burn windows and independent heat/cool response.

Features: altitude/speed thermal glow with per-stage inheritance, save restoration and optional debris afterglow; up to eight independent jettison objects per stage. Existing INIs remain valid. See [Thermal glow and multiple jettison objects](README_StageGlowAndJettison.md) for keys and examples.

# Generic Multi-Stage Missile Visual System

This is an isolated AnchorChain plug-in for both Sea Power 0.8.2 release and the unified-time beta. The output is
the deliberately inert build artifact `bin/MultiStageMissiles.dll_`; installation renames it to
`MultiStageMissiles.dll` in the AC Pack. It does not replace or rewrite `Seapower-Scripts.dll`,
`AnchorChain.dll`, SATCOM, or any other existing mod. Archived DLL versions belong in the separate
external `X:\Modding\Sea Power Modding` development directory, never beside the active DLL in a loadable mod directory.

The same `SeaPower.Missile` object remains alive for the complete engagement. Visual mesh changes create no extra weapons or hit sources. Submunitions and physical stage motors are separate opt-in features. Target, guidance, SATCOM/datalink and seeker state remain owned by the native missile.

Version 1.2.26 also exposes `MissileStageDriver.CurrentStageNumber` as a public, read-only integer.
Optional visual submods can use the INI-style stage number (`1` through `16`) without accessing or
changing MultiStage runtime state. A newly created or newly rebound driver starts at `1`.
After the final stage becomes idle and its update driver is suspended, the read-only value retains
the last active stage. Rebinding the runtime for a respawn resets it to Stage 1.

## Release/Beta time compatibility

The plug-in does not use a Sea Power build number. At runtime it inspects the available API and
prefers `GameTime.missionElapsedTime`; when that member is absent it falls back to the release
member `GameTime.time`. `WeaponBase._launchTime` is also read through reflection and converted to
`float`, so both the release `float` field and beta `double` field are supported by the same DLL.
Named `WeaponBase.FlightStage` transitions are parsed by enum name at runtime, so the beta enum
insertion does not shift configured transition meanings.

For an explicit two-assembly build check, pass the old game assembly to the build script:

```powershell
.\build.ps1 -LegacyScriptsPath 'C:\path\to\Seapower-Scripts_legacy.dll'
```

## Configuration

Staging is enabled with `NumberOfStages` in `[Models]`. `ThermalGlowMaterial` or `NumberOfSubmunitionLaunchers` also enables an implicit single stage:

```ini
[Models]
NumberOfStages=6
```

`NumberOfStages=1` through `NumberOfStages=16` use the same dynamic code. Values above 16 are
clamped to 16 with a warning. If all three enabling keys are absent, vanilla behavior is retained.

For each stage `N` from 1 through the configured count, these are the exact new optional keys:

```ini
StageNMesh=
StageNMeshPosition=0,0,0
StageNMeshRotation=0,0,0
StageNSeparationTime=
StageNFlightEffect=
StageNFlightEffectClass=
StageNFlightEffectPosition=0,0,0
StageNFlightEffectRotation=0,0,0
StageNFlightEffectScale=0,0,0
# The fully numbered StageNFlightEffect1... family is also accepted for slot 1.
StageNBurnTime=
StageNAudioClip=
StageNFlightEffect2=
StageNFlightEffect2Class=
StageNFlightEffect2Position=0,0,0
StageNFlightEffect2Rotation=0,0,0
StageNFlightEffect2Scale=0,0,0
StageNBurnTime2=
# Repeat the same pattern through FlightEffect8 / BurnTime8.
StageNSeparationEffect=
StageNSeparationEffectPosition=0,0,0
StageNJettisonMesh=
StageNJettisonMeshPosition=0,0,0
StageNJettisonMeshRotation=0,0,0
```

No jettison velocity, force, lifetime, drag, damage, guidance, physics, or stage-performance keys are
added in V1.

Detached jettison meshes use a fixed linear damping of `0.35`, so spent stages lose speed and fall
behind a missile instead of retaining their full launch velocity for their entire lifetime.

`StageNSeparationTime` accepts an absolute time in seconds since `WeaponBase._launchTime`, the special
case-insensitive value `WaterExit`, or a case-insensitive base-game `WeaponBase.FlightStage` name. For example:

```ini
Stage1SeparationTime=8.5
Stage2SeparationTime=WaterExit
Stage3SeparationTime=MaintainSeaSkimming
Stage4SeparationTime=TerminalApproach
```

A numeric transition fires when its launch-relative time is reached; configured numeric times must
increase strictly. `WaterExit` fires once an underwater-launched missile's base-game
`_checkForWaterExit` flag changes from `true` to `false` at the surface; it does not fire for ordinary
above-water launches. A named transition fires when the missile's current base-game flight stage exactly
matches the value. `Terminal` is accepted as an alias for `TerminalApproach`. A missing transition uses Delay + BurnTime when BurnTime is configured; otherwise it remains disabled. Malformed, negative, unknown or non-monotonic explicit transitions are disabled without aborting ammunition loading. The final stage needs no separation value.

Each stage has up to eight independent visual flight-effect slots. Slot 1 canonically uses the
unnumbered `StageNFlightEffect...` keys, while the fully numbered `StageNFlightEffect1...` family is
accepted as an exact alias. If both are present, the unnumbered form wins. Slots 2 through 8 append
their number directly after `FlightEffect`.
Every slot supports Sea Power's normal `Effect` key family: the direct effect resource or `Class`,
plus `Position`, `Rotation`, and `Scale`. For example, `Stage1FlightEffect2Scale=0.35,0.35,1.5`
controls only effect slot 2 of Stage 1. All configured slots spawn concurrently when the stage begins.
Each slot receives its own child transform anchor. Position and rotation are applied to that anchor,
while scale remains confined to the effect root beneath it so Unity's local particle scaling continues
to work. The anchor cancels the missile hierarchy's inherited `lossyScale`, making each configured
effect scale independent of the missile model/root scale. Later slots therefore cannot modify an
earlier slot's transform. Each anchor remains inactive while its resource prefab is cloned, cleared,
parented, positioned, rotated, scaled, and prepared. The complete slot hierarchy is activated only
after all transforms are final, so Play On Awake particles and trails cannot capture an intermediate
transform. Every active slot runs on its own direct private instance and never enters Sea Power's
global effect pool. No pooled transform, scale, particle, or lifetime state can therefore be shared
between slot 1, slot 2, another stage, or another missile. When no scale key is present, a direct
resource's original prefab scale is retained.

Normal stage loading, reload, scale, scheduling, stopping, and recovered pool-reuse events are silent.
The plug-in logs one successful startup message and otherwise only actionable warnings or errors.

`StageNFlightEffectScale` values are absolute Unity local scales, matching Sea Power's normal Effect
keys; they are not multipliers. Omit the key (or use `0,0,0`) to retain the effect prefab's original
root scale. Unnumbered `StageNFlightEffect...` keys are simply slot 1 and remain fully independent for
every stage. The unconditional private instances also prevent a large salvo from letting one missile's
stage effect overwrite another missile's effect.

`StageNBurnTime` sets physical motor duration when stage propulsion is enabled and is the shared default duration for flight effects/audio. `StageNBurnTimeDelay` delays ignition and those effects from stage entry.
`StageNBurnTime2` through `StageNBurnTime8` optionally override that duration for their corresponding
numbered slot. For compatibility, `StageNFlightEffect2BurnTime` and
`StageNFlightEffectBurnTime2` (and the equivalent suffixes through 8) are also accepted as aliases;
the canonical `StageNBurnTimeX` form takes precedence. If neither a slot override nor the shared key
exists, that effect continues until separation. Like the base-game `SustainerEffect`/
`SustainerAccelerationTime` path, the requested duration is passed directly to
the private root particle instance so it also replaces the particle asset's shorter default duration.
A shared `0` suppresses every stage effect without an individual override; an indexed `0`
suppresses only that slot. A positive value stops the applicable slot when the duration expires or at
separation, whichever happens first. With stage propulsion enabled it also limits motor output; without an explicit separation trigger, Delay + BurnTime advances to the next stage. Guidance stays native. Save loading reconstructs each slot's remaining duration instead of restarting an
already expired burn.

## Stage audio

Every stage can define exactly one looping sound with `StageNAudioClip`. The plug-in creates one
private 3D `AudioSource`, routes it through Sea Power's normal `Sfx` mixer, and inherits the relevant
booster/sustainer source's spatial rolloff, distances, pitch, volume, reverb, and mixer properties.
Unity and Sea Power therefore handle spatial attenuation and reverb; the plug-in performs no camera
distance checks, near/far crossfade, audibility override, or synthetic echo.

The unindexed `StageNBurnTime` controls the sound. A positive value stops and destroys the loop at
that stage-burn deadline; `0` suppresses it. If the shared burn time is omitted, the loop continues
until separation. Indexed visual-effect overrides such as `StageNBurnTime2` do not change the stage
sound duration. On save restore, the loop receives only the remaining shared burn time and resumes at
the corresponding position inside the audio file.

No other stage-audio configuration keys are used. Base-game resource names work directly. PCM16 WAV
paths are resolved through the installed CustomAudioLoader's normal `ResourceLoader` hook.

Example:

```ini
Stage1BurnTime=6.5
Stage1AudioClip=audio/weapons/Missile-Large_MotorLoop.wav
```

See `example_six_stage.ini` for a complete six-stage fragment.

## Mesh loading and switching

The current game uses the `[Models]` values `ResourcesFolder`, `ResourcesRoot`, `ResourcesMesh`,
`ResourcesMeshForLaunch`, and `ResourcesMeshCanister`. Stage mesh names are first resolved as child
transforms of the same cached `ResourcesFolder + ResourcesRoot` GameObject. A stage value may also
name a directly loadable GameObject resource; that fallback still goes through Sea Power's cached
`ResourceLoader.getGameObjectResource`.

`WeaponBase.initResources` stores only lightweight stage slots. A stage mesh is instantiated the first
time that stage actually becomes active; a jettison visual is instantiated only at its separation.
The resource root and each resolved slot are then cached for that missile. Stored VLS ammunition no
longer creates all of its future stage/debris hierarchies in advance. The active stage mesh is a child
of the existing missile root, with its configured local position and Euler rotation. A missing mesh
leaves the current stage or normal missile mesh active.

The finalized material from the vanilla main missile mesh is resolved once and shared across every
renderer below each stage and jettison visual, including every material slot. No per-visual `Material`
copy is allocated or leaked. If that runtime material is unavailable, the loaded `WeaponInstance`
material is used as the fallback. This ensures that nested renderers receive the texture and shader
data loaded from `ResourcesMaterialFolder` and `ResourcesMaterial`.

Sea Power calls private `Missile.ScheduleFlightEffects()` when the motor flight begins, but a surface
launch can still be displaying `ResourcesMeshForLaunch` at that moment. The plug-in records that call
and waits for the vanilla main airborne mesh to become active before enabling Stage 1. It never
changes the game's normal launch/canister switch or its timing.

## Effects

Stage effects are parsed with Sea Power's existing `Effect` class and pre-resolved by its
`ResourceLoader`:

- Up to eight flight effects are spawned concurrently as direct private resource instances. Each is
  created below an inactive per-slot anchor, receives its own final local position/rotation/scale,
  and is only then activated. It is stopped and destroyed when its effective
  shared-or-overridden burn time expires or before the next stage begins.
- A separation effect is spawned once at
  `missile.position + missile.rotation * StageNSeparationEffectPosition`, with no missile parent.
  No transform scale, hidden resource transform, or other position offset is added.
- Every vanilla booster, `InFlightEffect`, and sustainer instance remains completely untouched and
  visible. The plug-in does not stop, free, hide, disable, or clear references to those effects and
  does not start, stop, loop, or replace their audio. Its separate stage-audio children are additive
  and are the only audio sources controlled by the plug-in. Users can remove unwanted vanilla effects
  in their ammunition definitions. Custom stage effects and sounds can therefore run alongside any
  retained vanilla content. Physical stage motors are enabled separately as described in the propulsion README.

## Jettison debris

Each configured jettison visual is instantiated only when its separation occurs. It is positioned
using the missile transform before the stage mesh switch and rotated by
`missile.rotation * Quaternion.Euler(localRotation)`. It is activated while still parented to the
missile for its first visible render frame. In `LateUpdate`, its exact visible world pose is captured,
it is detached with that pose preserved, and only then is its independent physics motion enabled.

`StageNJettisonMeshPosition=0,0,0` now means exactly the missile-root world position at the separation
instant. A non-zero configured position is rotated into missile-local space and added exactly once;
missile scale is deliberately ignored. This deferred detachment prevents a speed-dependent first-frame
gap between the visible missile pose and a newly independent Rigidbody, so fixed compensating offsets
are unnecessary.

It is a plain GameObject with no `ObjectBase`, `WeaponBase`, `Missile`, guidance, target, damage, or
collider. After deferred detachment its non-kinematic Rigidbody inherits
`Missile.UnityVelocityVector` with only a gentle 0.5 m/s backward difference along the current flight
axis. No radial linear velocity, gravity, or linear damping is applied. A very small angular velocity
produces mostly axial roll instead of a strong radial tumble, and the debris is destroyed after 25
seconds. Only the INI position controls its initial separation pose.
The lifecycle component registers it with Sea Power's existing relocation set so world-origin shifts
during those 25 seconds do not leave it behind. Its one-frame deferred-detachment `LateUpdate`
callback disables itself immediately afterwards; movement remains with the Rigidbody.

## Independent physical-stage state

Sea Power's existing `WeaponBase.FlightStage`, `_stageStartTime`, and `OnFlightStageChanged` represent
launch/guidance/terminal/search phases. The plug-in may read the current `FlightStage` as a configured
separation trigger, but never changes it. `MissileStageRuntime` stores a separate zero-based
`_currentStage` in a `ConditionalWeakTable<Missile, MissileStageRuntime>` owned by the plug-in.
`MissileStageDefinition` is the dynamic definition type and the definitions are held in a
`List<MissileStageDefinition>`.

## INI reload on ship respawn

The ammunition-constructor postfix reopens and reparses the current ammunition INI every time the
base game creates new `AmmunitionParameters`. There is no permanent parsed-filename gate. Therefore,
changes to stage counts, meshes, transforms, timings, effects, and audio apply when the ship is respawned in
the same game session, following the base game's own ammunition reconstruction. Missiles and ships
that already exist retain their current snapshot. Each prepared or pooled missile also retains its
ammunition filename and `WeaponInstance`; immediately before its next launch, the plug-in compares
its runtime snapshot with the latest respawn configuration and rebuilds the staged runtime/assets when
they differ. Assets remain lazy after that rebuild. This makes edited burn times and other stage keys effective even when Sea Power reuses a
pooled missile object. Removing `NumberOfStages` removes the plug-in's cached definition and retires
the old staged runtime so the next launch returns to vanilla visuals.

## Runtime lifecycle

Configuration is reparsed when native ammunition is reconstructed. Prepared/pool-reused missiles receive the latest snapshot before launch. Meshes, effects, sound, glow and submodels are created lazily. Stage transitions manage visual ownership and motor timing; save/load restores current state without replaying old separations or daughter launches. Cleanup releases private objects.

Propulsion hooks select native Missile helpers on release or MissileSimulator helpers on beta by API capabilities. See the propulsion README for prediction limits and optional additive native thrust. Unconfigured weapons retain native propulsion.

## Build and verification

Run:

```powershell
& .\build.ps1
```

The build compiles against the currently installed DLLs, then checks:

- vanilla/no-key behavior;
- 1, 2, 6, and 10 stages;
- `NumberOfStages=20` clamping to 16 with a warning;
- absolute numeric and named base-game FlightStage transitions, including malformed and non-monotonic
  values;
- up to eight concurrent effects per stage with unconditional private instances, deterministic transforms, and inherited/overridden
  missing, zero, positive, and invalid visual burn times, including the base-game dynamic
  effect-manager duration path;
- fully visible, untouched vanilla flight effects and untouched vanilla effect audio;
- exactly one engine-spatialized audio loop per stage, base-game `Sfx` routing and inherited source
  properties, shared-burn-time stopping, and save restoration;
- render-aligned zero/configured separation and jettison positions without transform-scale or
  first-frame physics offsets;
- gentle axial-backward jettison velocity with no radial linear component or gravity;
- all mesh, flight-effect, separation-effect, and jettison position/rotation/scale values;
- replacement and removal of a previously parsed definition on respawn;
- launch-time replacement of stale staged runtimes on pooled missile objects;
- nested-renderer discovery and assignment through every renderer's complete material-slot array;
- lazy stage/debris instantiation, cached shared materials, deadline-gated cleanup, self-disabling
  debris callbacks, and the absence of a global missile fixed-update postfix;
- all six current Harmony target signatures plus the staged-missile-only local driver;
- absence of non-visual Sea Power field writes and weapon-specific identifiers;
- unchanged SHA-256 hashes for `Seapower-Scripts.dll`, `AnchorChain.dll`, and existing protected mods.

Offline tests confirm that all five transitions in a six-stage configuration reach and retain Stage 6,
and that the same algorithm handles up to 16 stages. A desktop verifier cannot render Unity particle
systems or fly a guidance/SATCOM/terminal-seeker mission. Final visual placement and the requested
guidance/SATCOM/seeker continuity scenarios still require an in-game mission using actual stage assets.

## Continuous flight sound

Optional ammunition `[Models]` key:

```ini
InFlightSound=audio/weapons/Missile-Small_MotorLoop.wav
```

Omit the key or leave it empty to disable it. This creates one separate spatial audio loop per launched staged missile. It starts after launch, continues across all stage changes and burnouts, and ends when the missile is removed or reset. StageNAudioClip remains an independent optional motor sound and can overlap it. Existing ammunition sound settings are not changed automatically. Missing clips produce a warning and disable only this sound. Saved launched missiles resume at the elapsed-flight position within the loop.

## Solidrocket surface illumination

Opt-in `[MotorLight]` section in a particle-effect INI, supported by the mod's factory postfix (native `[Lights]` remains unsupported):

```ini
[MotorLight]
Enabled=True
Position=0,0,-0.01854
Color=1,0.81704,0.67647
Range=0.5
Intensity=1
```

Creates one shadowless point light per effect instance. It illuminates nearby meshes while exhaust_core particles are alive and switches off when the flame ends or the instance is disabled. Serialized references survive native and private prefab cloning. Other effects without this section are untouched. Warm color and point-light behavior were inspected in native sam_medium_effect/usn_rim-66_booster assets. Range is in game world units.

## Launch-controlled ignition

MissileControlMod can hold a configured `IgnitionStage` until tip-over and upward braking finish. See its `[MissileLaunchControl]` keys. MultiStage used alone keeps its existing timing. A held transition keeps the departing mesh attached; its effects still obey their own burn times. Absolute separation deadlines are unchanged, including after save/load.

