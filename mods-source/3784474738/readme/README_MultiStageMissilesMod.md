# Multi-Stage Missile Visuals

Configure up to 16 visual stages in an ammunition INI. Stages change models, effects and sounds; they do not change missile performance or guidance.

## Start with two stages

Add these keys to the existing `[Models]` section. Replace the example mesh names and effect paths with your own assets.

```ini
[Models]
NumberOfStages=2

Stage1Mesh=missile_complete
Stage1SeparationTime=5.5
Stage1FlightEffect=effects/weapons/stage1_motor
Stage1BurnTime=5
Stage1JettisonMesh=spent_booster

Stage2Mesh=missile_without_booster
Stage2FlightEffect=effects/weapons/stage2_motor
Stage2BurnTime=12
```

This switches to Stage 2 at 5.5 seconds after launch. The first motor effect lasts 5 seconds; the second lasts 12 seconds after Stage 2 begins.

## Stage settings

Replace `N` with the stage number, for example `Stage2Mesh`.

| Key | What to enter |
|---|---|
| `NumberOfStages` | Total stages, from 1 to 16. |
| `StageNMesh` | Mesh name from the ammunition's model resource, or a loadable model resource path. |
| `StageNSeparationTime` | Seconds **since launch**, not time spent in this stage. Numeric times must increase. Omit for the final stage. |
| `StageNFlightEffect` | Motor effect path. Use `StageNFlightEffectClass` instead to select an effect class. |
| `StageNBurnTime` | Effect and stage-sound duration in seconds from the start of this stage. Omit to continue until separation; `0` disables them. Effects stop at separation even if time remains. |
| `StageNSeparationEffect` | Effect played once when this stage separates. |
| `StageNJettisonMesh` | Detached model of the discarded part. |

Instead of a numeric separation time, use `WaterExit` for an underwater launch, or a flight phase such as `MaintainSeaSkimming` or `TerminalApproach`.

### Position, rotation and scale

Add `Position` or `Rotation` to a mesh or flight-effect key:

```ini
Stage1MeshPosition=0,0,0
Stage1MeshRotation=0,0,0
Stage1FlightEffectPosition=0,0,-0.5
Stage1FlightEffectRotation=0,0,0
Stage1FlightEffectScale=1,1,1
Stage1JettisonMeshPosition=0,0,-0.4
Stage1JettisonMeshRotation=0,0,0
Stage1SeparationEffectPosition=0,0,-0.4
```

Values use `x,y,z`; rotations are in degrees. Positions are local to the missile. Omit effect scale to keep the asset's original size; an explicit scale sets its size rather than multiplying it.

### Multiple motor effects

Each stage supports up to eight effects playing together. Number extra effects from 2 to 8:

```ini
Stage1FlightEffect2=effects/weapons/extra_smoke
Stage1FlightEffect2Position=0,0,-0.5
Stage1FlightEffect2Scale=1,1,1
Stage1BurnTime2=3
```

Extra effects use `StageNBurnTime` unless given their own `StageNBurnTime2` through `StageNBurnTime8`. An individual value of `0` disables only that effect.

### Sounds

Add these optional keys under `[Models]`:

```ini
Stage1AudioClip=audio/weapons/Missile-Large_MotorLoop.wav
InFlightSound=audio/weapons/Missile-Small_MotorLoop.wav
```

`StageNAudioClip` loops during that stage's shared burn time. `InFlightSound` continues across all stages until the missile is removed. Custom WAV files require CustomAudioLoader. Existing missile sounds and effects still play, so remove unwanted duplicates from your ammunition settings.

### Motor light

To illuminate nearby surfaces, add this separate section to the **particle-effect INI**:

```ini
[MotorLight]
Enabled=True
Position=0,0,-0.01854
Color=1,0.82,0.68
Range=0.5
Intensity=1
```

The light follows the effect's `exhaust_core` particles. Color uses RGB values from 0 to 1; range uses game world units.

## Try your changes

Respawn the launching ship after editing stage settings, then launch a new missile. Existing missiles keep their previous settings. Restart the game when changing asset files.

For a larger template, see [example_six_stage.ini](example_six_stage.ini). Remove `NumberOfStages` to return to normal missile visuals on a fresh spawn.
