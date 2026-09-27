# Stage propulsion and submodels (1.5.0)

Put stage keys in the ammunition INI's `[Models]` section. No ammunition is enabled automatically.

## Motors

`StageNAcceleration` enables physical stage motors. Values use the same acceleration convention as native `Acceleration` (G). `StageNBurnTime` is the motor duration in seconds and remains the shared default for stage effects/audio. `StageNBurnTimeDelay` delays ignition, stage effects and stage audio from entry into that stage; default `0`.

Stage 1 waits for native motor readiness (including InitialDrop/water-exit handling) and optional launch-controller gates before its burn clock starts. Later stages use their actual entry time. Explicit numeric SeparationTime still uses the launch clock.

Native thrust is disabled by default for weapons using stage motors. `UseBaseGameThrust=True` **adds native thrust to stage thrust** using native ignition/timing. It does not replace stage thrust. Old visual-only configurations without `StageNAcceleration` or `UseBaseGameThrust` retain native propulsion.

Setting only `UseBaseGameThrust=False` supplies no replacement thrust. Define a positive `StageNAcceleration` and BurnTime for each powered stage. Otherwise a slow missile can trigger native stall destruction as its motor starts, including immediately after water exit. BurnTime alone does not specify thrust strength.

A stage without an explicit `StageNSeparationTime` advances after its Delay + BurnTime. Explicit launch-relative seconds, `WaterExit` and named flight-stage triggers still work. An event-triggered stage starts its own burn clock when it actually becomes active. Leaving a stage stops its motor. A stage without BurnTime or a separation trigger remains active.

Positive acceleration requires BurnTime. Missing acceleration means a coast stage. BurnTime `0` means no burn. Delay: `0..3600` s; BurnTime: `0..86400` s; Acceleration: `0..1000` G. Invalid motor definitions log a warning and disable stage thrust; native thrust is available only if explicitly enabled. Indexed `StageNBurnTime2..8` remain effect-only overrides.

```ini
[Models]
NumberOfStages=3
UseBaseGameThrust=False
Stage1Acceleration=8
Stage1BurnTime=5
Stage1BurnTimeDelay=0
Stage2Acceleration=4
Stage2BurnTime=12
Stage2BurnTimeDelay=2
Stage3Acceleration=0
```

This burns Stage 1 for 5 s, enters Stage 2, coasts for 2 s, burns for 12 s, then enters the final coast stage. No SeparationTime is needed. Native guidance, ballistic flight mode, drag and speed rules remain in force; added thrust can still change the trajectory and available range.

Prediction includes stage thrust. Future `WaterExit`, flight-phase or external controller delays cannot be known exactly in advance; prediction uses the configured sequence as an estimate, while live flight uses actual stage-entry times. Beta range prediction uses the native altitude route and drag function with numerical stage-motor integration. Gameplay accuracy and performance still require in-game testing.

## Stage-owned submodels

Use `StageNSubmodel1` through `StageNSubmodel16` to reference object sections. Register those sections under `[Submodels]`. Each section supplies `Mesh` (or `Object`), optional local `Position`, `Rotation`, and `Scale`. Mesh paths resolve like StageNMesh. The mod creates separate visual objects; do not also instantiate the same objects through native `[Models] SubModelN` entries unless duplicates are intended. Objects use the weapon material/bundled fallback, like stage meshes.

**On stage change, previous stage submodels disappear by default.** Set `StageNInheritSubmodels=True` on the **receiving** stage to keep all current objects and their animation progress. This also works when the main mesh changes. A later stage with False (default) removes the entire inherited set. Physical debris is configured separately with JettisonMesh entries.

Optional per-object keys:

| Key after `StageNSubmodelM` | Value / default |
|---|---|
| `StartPosition`, `EndPosition` | Local x,y,z, same model units as StageNMeshPosition |
| `StartRotation`, `EndRotation` | Local Euler x,y,z, degrees; full turns allowed |
| `StartScale`, `EndScale` | Local x,y,z factors |
| `Duration` | Seconds, `0..86400`; default 0 (instant after Delay) |
| `Delay` | Seconds from stage entry, `0..86400`; default 0 |
| `Interpolation` | `SmoothStep` (default) or `Linear` |

Missing Start uses the object's current pose; missing End keeps that channel at its start pose. Explicit Start poses hold during Delay. Inherited animations continue without restarting. To start a new animation on an inherited object, reference the same section in the new stage and provide new transform keys. Relisting it without transform keys does not restart it. Save/load preserves stage age, active objects, animation age and start poses. Timing follows mission time, including pause and time compression.

```ini
[Models]
NumberOfStages=3
Stage1Acceleration=8
Stage1BurnTime=5
Stage1Submodel1=PayloadDoor
Stage1Submodel1StartRotation=0,0,0
Stage1Submodel1EndRotation=0,90,0
Stage1Submodel1Delay=4
Stage1Submodel1Duration=3
Stage2Acceleration=4
Stage2BurnTime=12
Stage2InheritSubmodels=True
Stage3InheritSubmodels=False

[Submodels]
SubModel1=PayloadDoor

[PayloadDoor]
Mesh=payload_door_left
Position=0,0,0
Rotation=0,0,0
Scale=1,1,1
```

Replace `payload_door_left` with an existing bundled mesh path. The door begins opening at 4 s, continues across the stage change at 5 s, finishes at 7 s, and disappears when Stage 3 starts. Use one numbered entry per object; sparse indices are supported. These are visual objects, not extra weapons or colliders.

Evidence: one DLL checked against the installed public release and the available stable-beta assembly snapshot. Binary references, runtime API selection, real native thrust delegates, staged/additive thrust, timing policies, animation/save policies and lifecycle hooks checked offline. Unity object creation, Harmony patch installation and live ballistic/animation behavior are not yet tested in-game.
