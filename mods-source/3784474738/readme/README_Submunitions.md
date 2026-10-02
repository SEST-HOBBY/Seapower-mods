# Missile submunitions — 1.6.0

Add these optional keys to the carrier missile's existing `[Models]` section. Each daughter is a separate native weapon with its own ammunition INI, damage, flight and seeker. No existing weapon is enabled automatically. Glow, stage meshes and visual jettison remain independently configurable.

## Example: two side-launching missiles

Replace `your_daughter_missile` with an existing ammunition INI name, without `.ini`. Merge into `[Models]`; keep your existing stage definitions.

```ini
[Models]
NumberOfSubmunitionLaunchers=1
Submunition1Ammunition=your_daughter_missile
Submunition1Count=2
Submunition1Stage=2
Submunition1Position=0.4,0,0
Submunition1Spacing=0,0,-0.5
Submunition1Rotation=0,90,0
Submunition1EjectVelocity=8,0,0
Submunition1InitialDrop=0.4
Submunition1Interval=0.15
Submunition1Aim=Parent
```

This requires an existing Stage 2. Use `Stage=1` for a single-stage carrier. `NumberOfSubmunitionLaunchers` alone enables one implicit stage. Releases begin only after native airborne flight and the visual stage system have started. The carrier continues flying after release.

## Flight-phase release

SubmunitionNTime also accepts a flight-stage name instead of seconds. Names are case-insensitive and resolved against the running game's enum.

~~~ini
[Models]
NumberOfSubmunitionLaunchers=1
Submunition1Ammunition=wp_aircraft_chaff
Submunition1ChaffSystem=WP_AIR_CHAFF_DISP
Submunition1Time=Terminal
Submunition1Count=128
Submunition1Interval=1
~~~

No NumberOfStages is required. Terminal is an alias for TerminalApproach; SeaSkimming means MaintainSeaSkimming (already at sea-skimming altitude). Use MoveToSeaSkimming to trigger during the descent toward that altitude. Other exact native names, such as MaintainHeight or MaintainLoftAlt, are accepted if available in the current game build.

The carrier must actually be in the named phase when the other Stage/Distance conditions are satisfied. A later enum value does not mean the phase was reached, and a skipped phase does not trigger a release. Once armed, the salvo continues at Interval even after leaving the phase, and its armed/progress state is saved. Changing the configured phase invalidates a saved launcher record to prevent duplicate releases. Unknown names disable that launcher with a warning. Numeric values still mean seconds, never enum ordinals.
## Launcher keys

Replace `N` with `1` through `NumberOfSubmunitionLaunchers` (maximum 128). Each group carries 1–128 rounds: at most 16384 daughters per carrier. At most four are created per fixed update; a zero interval can therefore span several updates.

| Key | Default / meaning |
|---|---|
| `SubmunitionNAmmunition` | Required ammunition INI name. Native Type=Missile, ordinary Type=Bomb, Type=Torpedo, and Type=Chaff are supported. |
| `SubmunitionNChaffSystem` | US_AIR_CHAFF_DISP; for Chaff only, a section in systems/weapons.ini supplying the native Effect and EffectPosition. |
| `SubmunitionNCount` | `1`; range 1–128. |
| `SubmunitionNStage` | `1`; release at or after entering this existing visual stage. |
| `SubmunitionNTime` | `0`; seconds since carrier launch (0..86400), or a native flight-stage name; see below. |
| `SubmunitionNDistance` | `-1` disables; otherwise maximum 3D distance to the carrier aimpoint, metres. |
| `SubmunitionNInterval` | `0`; seconds between rounds, maximum 3600. |
| `SubmunitionNMount` | Empty = carrier root. Optional exact Transform path relative to that root; it must already exist when airborne flight starts. |
| `SubmunitionNPosition` | `0,0,0`; mount-local metres. |
| `SubmunitionNSpacing` | `0,0,0`; mount-local metres added for each next round. |
| `SubmunitionNRotation` | `0,0,0`; local Euler degrees for the carried mesh and initial drop pose. At native missile flight handoff, the flight axis aligns to the inherited plus ejection velocity, retaining roll. |
| `SubmunitionNEjectVelocity` | `0,0,0`; mount-local m/s added to the carrier's actual velocity. X right, Y up, Z forward. |
| `SubmunitionNInitialDrop` | Omitted = daughter's native `[Guidance] DropDuration`, clamped to 0–120 s. `0` ignites immediately. Positive values give a ballistic unpowered missile release before native powered flight. Bombs remain in their native drop flight. Torpedoes use native parachute/water-entry timing; Chaff forms immediately. This timer applies only to missiles. |
| `SubmunitionNStowedMesh` | Empty = no extra carried visual. Optional child mesh/path resolved like a stage mesh from the carrier's resource root; one copy per round disappears on release. The launcher itself is a logical attachment, not a ship weapon system. |
| `SubmunitionNAim` | `Parent`, `Point`, or `Unguided`; see below. |
| `SubmunitionNRadius` | `0`; outer ground-plane spread radius, metres; maximum 100000. |
| `SubmunitionNInnerRadius` | `0`; inner radius 0–Radius. Equal radii produce a ring. |
| `SubmunitionNMaxSpreadVelocity` | `100`; maximum additional horizontal m/s used to aim an unguided spread release, range 0–10000. |

All specified stage/time/distance conditions must be satisfied together. Once a salvo starts, it continues at its interval even if the carrier leaves the trigger distance. Stage transitions do not cancel a salvo. Parent destruction cancels unreleased rounds; launched daughters remain independent.

Positions/spacing here use metres, unlike older visual mesh offsets. Mesh scale still comes from the asset. Use a negative Y ejection for downward release, positive Z for forward release, and positive/negative X for side ejection. With zero ejection and a positive InitialDrop, a missile inherits the carrier velocity and falls before ignition.

The ejection vector uses the mount axes, not the daughter's rotated mesh axes. `Rotation` therefore does not steer or redirect the carrier's inherited velocity. During `InitialDrop`, a missile keeps its release pose while its velocity changes under gravity. On entering native flight it aligns to that full velocity; this is an immediate pose change, not an animated turn. The base game's scalar-speed missile model then handles guidance and drag. A larger ejection speed is not a remedy for incorrect handoff direction.

## Target and guidance

- `Parent`: transfers the carrier's intended target object; if unavailable, uses its aimpoint. The daughter uses its own seeker and native guidance settings. `Radius` must be zero.
- `Point`: assigns an independent sampled aimpoint around the carrier aimpoint at that round's release. Navigation and any seeker behavior still come from the daughter INI. A seeker can subsequently select a contact, so a specific impact point is not guaranteed. A seekerless missile with native navigation is still guided flight.
- `Unguided`: requires an ordinary bomb with `[General] Type=Bomb`, `[Guidance] GuidanceType=0`, and no cluster/special subtype or native submunition. With positive Radius, an initial horizontal impulse aims at a sampled circle/ring point. There is no later aimpoint correction or seeker steering. Radius zero gives an ordinary uncorrected physical drop with inherited/ejection velocity.

Seeker activation is left to the base game. `TerminalApproachDist` is not a universal switch for every seeker type; configure and test the daughter ammunition's own guidance settings. External guidance still requires a suitable original launcher/sensor context.

Example unguided group (replace the ammunition name with your ordinary bomb INI):

```ini
Submunition1Ammunition=your_unguided_bomblet
Submunition1Count=8
Submunition1Stage=2
Submunition1Aim=Unguided
Submunition1Radius=120
Submunition1InnerRadius=0
Submunition1EjectVelocity=0,-3,0
Submunition1MaxSpreadVelocity=80
Submunition1Interval=0.05
```

The ballistic estimate uses native bomb gravity and the aimpoint elevation. Terrain slopes, parachutes, collisions, moving targets and native integration can move actual impacts outside the requested area. If the point cannot be reached within MaxSpreadVelocity, that launcher stops with a log message. There is no unlimited impulse or guaranteed-hit correction.


## Torpedo release

Use a Type=Torpedo ammunition INI and Aim=Parent or Aim=Point. The original target or sampled point is passed to native torpedo launch logic. Above water, the torpedo enters the same parachute-drop state used for native missile-carried torpedoes; its configured splash, propulsion, search depth and seeker then take over. At or below the water surface, native underwater launch is preserved. Carrier velocity plus EjectVelocity is transferred once at release. InitialDrop does not delay torpedo parachute deployment. Use an ammunition INI configured for aerial release.

~~~ini
Submunition1Ammunition=your_air_dropped_torpedo
Submunition1Count=1
Submunition1Stage=2
Submunition1Aim=Parent
Submunition1EjectVelocity=0,-3,0
~~~

## Native chaff release

Chaff uses a separate native cloud factory and launchChaffEffect, with native radar spoofing and DefensiveEffectTime from its ammunition INI. Each configured round creates one independent cloud using the effect from SubmunitionNChaffSystem. Count and Interval control the stage salvo; the original platform's chaff magazine and reload cycle are not used.

~~~ini
[Models]
NumberOfSubmunitionLaunchers=1
Submunition1Ammunition=usn_rr144_chaff
Submunition1ChaffSystem=US_AIR_CHAFF_DISP
Submunition1Stage=2
Submunition1Count=8
Submunition1Interval=1
Submunition1Position=0,0,-1
~~~

Use an existing Stage 2 or set Stage=1. Chaff forms at the configured mount position. It follows native cloud behavior: Aim, EjectVelocity and InitialDrop do not steer or propel it; Radius must be zero. Rotation, Position and Spacing place the release. A cloud-owned mount keeps emitted effects independent after the carrier is destroyed. This route is for ordinary Chaff; custom EnhancedDecoy/AirDecoy flight behavior is not part of this feature.

## Saving and limits

Released counts, salvo remainder, spread seed and missile/bomb/torpedo release metadata are saved. Chaff clouds use the native transient lifecycle; this mod adds no restoration of already emitted chaff effects. A changed or missing launcher save record disables that launcher on the restored carrier to avoid duplicate weapons; launch a fresh carrier after adding this feature to an old save. Daughter stage/glow features work, but daughters cannot launch another generation. Native nested submunition ammunition is rejected.

## Independent INI effect instances

Composite ammunition effects can optionally bypass the base game's effect pool. Add this to that ammunition INI's `[Models]` section:

```ini
[Models]
IndependentEffectInstances=True
```

The setting applies to every direct INI effect loaded by that ammunition, including booster, flight, trail, water-entry/exit, air, ground, ship, object and default hit effects. The normal `EffectsManager` setup still runs, so native lifetime handling and effect bookkeeping are retained. Effect classes selected by `...ExplosionClass` stay on the native path because they do not identify one direct prefab. Leave the setting absent for ordinary effects; independent instances use more memory than pooled instances, and effects are destroyed when their configured lifetime ends.

Requires `MultiStageMissiles.dll` 1.6.0. API and offline lifecycle checks cover the installed release and stored beta assembly; native spawning, visual placement, interception, guidance and save/load in a running Unity scene still need in-game testing. No weapon-specific ammunition or meshes are supplied by this feature.

For a long chaff salvo, use SubmunitionNCount=128 with SubmunitionNInterval=1 for one release per second. Existing launchers retain their configured counts; raising the limit does not increase ammunition automatically.
