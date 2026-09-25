Version 1.2.31: release/beta compatibility maintenance. Float/double clocks and native launch timestamps are bound once to runtime members. Effect, delayed-pulse, audio and debris deadlines retain double precision. A transitional beta float _launchTime is compared with GameTime.time rather than the separate missionElapsedTime clock, preserving launch-relative delays. Initialization failure now removes this mod's partial Harmony patches; repeated successful entry calls do not stack patches. INI keys and defaults are unchanged.

The shared TimeApi.cs source is in ../MissileControlMod; build.ps1 includes it. ../MissileControlMod/test-compatibility.ps1 validates the identical compiled DLL against both supplied game APIs and records their hashes. The local beta check uses an exported beta snapshot with the installed Unity dependencies; it is an offline compatibility check, not a live Unity test or a guarantee for future beta revisions.
# Multi-Stage Missile Visuals 1.2.31

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

Version 1.2.31 adds optional per-slot delayed starts:

```ini
Stage1FlightEffect2=effects/weapons/emitters/thrusters/control_thruster_large.ini
Stage1FlightEffect2StartDelay=1          // Seconds since launch for Stage 1; since stage entry for later stages.
Stage1BurnTime2=0.35                    // Seconds of emission after this slot's scheduled start.
Stage1FlightEffect2ContinuousChildren=True // Optional: drive continuous children of an invisible Birth/InheritNothing carrier directly.
```

`StartDelay` defaults to zero (0..3600 seconds). Only slots with a positive delay use this explicit schedule; old zero-delay ignition behavior stays unchanged. Stage 1's delay is launch-relative, so a native mesh-switch wait is not added. A delayed slot requires its stage to be active: if the stage becomes available late, elapsed emission time is deducted and an expired pulse is skipped. Separation, respawn and destruction cancel pending slots. Loading a save does not replay an expired pulse. Numeric later-stage transitions can reconstruct elapsed stage time; phase-triggered later stages retain the existing stage-time reconstruction limitation. Stage separation always cuts off a slot, even if it has burn time left.

`ContinuousChildren` defaults to False. Set it for reusable continuous thruster composites whose invisible root otherwise schedules non-inheriting children at Birth. It only changes that slot's private clone and preserves its configured orientation. Ordinary motor effects remain unchanged. On cutoff these opted-in jets retain their existing particles for a bounded tail lifetime, including world-space smoke.

### Sounds

Add these optional keys under `[Models]`:

```ini
Stage1AudioClip=audio/weapons/Missile-Large_MotorLoop.wav
InFlightSound=audio/weapons/Missile-Small_MotorLoop.wav
```

`StageNAudioClip` loops during that stage's shared burn time. `InFlightSound` continues across all stages until the missile is removed. Custom WAV files require CustomAudioLoader. Existing missile sounds and effects still play, so remove unwanted duplicates from your ammunition settings.

`StageNJettisonAudioClip` plays one optional 3D one-shot on the discarded mesh when stage N separates. It works without StageNAudioClip or a particle effect. It stays on the debris, finishes naturally and stops if the debris expires; JettisonEffectDuration only bounds the particle effect and any audio embedded in that effect prefab. Missing meshes produce no jettison sound. Loading a save does not replay previous jettisons. The final stage needs a subsequent stage/transition to be discarded.

```ini
[Models]
Stage3JettisonAudioClip= // Optional audio resource path; empty disables this debris sound
Stage3JettisonAudioVolume=1 // Sound volume from 0 to 1; 0 mutes it
```

Use the same resource paths as StageNAudioClip. The sound pauses with the game and requires no MissileControl launch configuration. Existing audio embedded in an effect prefab still plays separately; avoid duplicating the same sound there. There is no StageNSeparationAudioClip key.

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

### Directional debris with an attached effect (1.2.27)

These optional keys go in `[Models]`, alongside `StageNJettisonMesh`. They apply when stage N separates. The existing numeric/WaterExit/flight-phase separation triggers are unchanged. The final stage does not separate by itself.

| Key | Default | Meaning |
|---|---|---|
| `StageNJettisonVelocity` | Omitted | Additional `x,y,z` velocity in **metres/second along the missile's local axes at release**. +Z is forward; -Z rearward; X/Y allow sideways release. The missile's existing velocity is inherited and the configured vector is added. Omit to retain the original gentle backward release; `0,0,0` adds no impulse. |
| `StageNJettisonAngularVelocity` | Omitted | Local `x,y,z` rotation rates in degrees/second. `0,0,0` disables tumble. Omit for the original small random tumble. |
| `StageNJettisonLifetime` | `25` | Debris lifetime in simulation seconds since release; 0.01..3600. |
| `StageNJettisonEffect` | Empty | Effect resource attached directly to the detached mesh as a private child. |
| `StageNJettisonEffectClass` | Empty | Effect class alternative to JettisonEffect. |
| `StageNJettisonEffectPosition` | `0,0,0` | **Debris-local mesh units**, relative to the detached mesh's origin. |
| `StageNJettisonEffectRotation` | `0,0,0` | Debris-local Euler degrees applied to the effect's authored direction. |
| `StageNJettisonEffectScale` | `0,0,0` | Zero keeps authored scale; otherwise sets the effect root's local scale. |
| `StageNJettisonEffectContinuousChildren` | `False` | Opt in for composite control jets with an invisible Birth/InheritNothing carrier. Drives its private continuous children directly so their positions and directions follow the debris. Emission still ends at JettisonEffectDuration; other effect types retain native scheduling. |
| `StageNJettisonEffectDuration` | `-1` | Maximum new-emission time after release, in simulation seconds. -1 imposes no extra cutoff; 0 disables the effect; positive values up to 3600 stop emission after that interval. Existing particles finish their authored lifetimes while the debris exists. |

The effect emitter stays with the debris as it moves and tumbles. Particle simulation spaces remain authored: for example, world-space smoke can trail behind a moving emitter. Use a looping effect for continuous emission. The effect does not apply additional force. At the configured cutoff, particle emission and effect audio stop; at debris expiry the whole private object is destroyed. Debris owns these clocks independently of the missile and later stage changes. Only the detached root is registered for origin relocation; its effect follows as a child. Invalid durations/vectors warn and use defaults. Missing optional effects leave the debris mesh available.

`StageNSeparationEffect` remains the existing one-shot effect at the separation point. Use `StageNJettisonEffect` for a flame or smoke emitter that must travel with the discarded part. A detached part needs its own mesh; remove it from the subsequent flying-stage mesh to avoid showing it twice. The new keys also work without MissileControlMod. Detached cosmetic debris is not serialized into saved games, matching the previous jettison behavior.

The paired MissileControlMod 0.1.6 adds `Profile=BoostedTurnover`: the native motor remains active while the short launch movement retains inertia. Stage burn/separation clocks remain independent of launch alignment. See [example_boosted_tipover.ini](example_boosted_tipover.ini) for English inline comments and a forward-release example.

Source/build: `CustomSonarAudio/MultiStageMissilesMod`. The 1.2.27 working copy was based on the verified 1.2.26 source in `X:/Modding/Sea Power Modding/AC Pack/Development/CustomSonarAudio/MultiStageMissilesMod`.

### Applying settings

Respawn the launching ship after editing stage settings, then launch a new missile. Existing missiles keep their previous settings. Restart the game when changing asset files.

For a larger template, see [example_six_stage.ini](example_six_stage.ini). Remove `NumberOfStages` to return to normal missile visuals on a fresh spawn.


`StageNJettisonAudioDebug=True` enables bounded playback diagnostics for this stage (default `False`). The log records source creation, the queued request, Play, the following playback frame and source disable. It includes clip load state, sample position, playing/virtual/mute flags, listener pause/volume, listener distance and mixer group. This setting does not change volume or playback. Set it back to False after troubleshooting.

### Launch-controlled ignition (1.2.33)

MissileControlMod 0.1.11 can hold `IgnitionStage` until tip-over and upward braking finish. Configure `StopUpwardMotion`, `UpwardBrakeTime` and `UpwardBrakeMode` under `[MissileLaunchControl]`; see its README. Used alone, MultiStage retains its existing timing. The departing mesh stays attached while held; its effects retain their burn limits. Absolute separation deadlines remain unchanged, including after save/load. Keep the intended ignition deadline within `MaxControlTime + UpwardBrakeTime` to avoid the launch controller's bounded fallback.

Audio debug in 1.2.34 also records the resolved resource file, a bounded decoded PCM sample, source output and combined listener output levels, mixer volume/filter values, position, scale and active listener count. Playback is sampled for at most 16 additional points (80 ms apart) or until it ends. These are read-only diagnostics; no replay, volume boost, rerouting or file edits. The combined listener signal includes every audible sound and does not alone prove the cap is audible. Source output history may initially be empty; inspect subsequent samples.

### Surface launch timing (1.2.35)

With MissileControl 0.1.13 and `StartAfterWaterExit=True`, submerged controlled missiles wait for native water exit before starting their visual stages. Numerical `StageNSeparationTime` values and delayed Stage1 effect slots then count from that exit. The launch controller stores this clock in saves. Standalone MultiStage and surface launches retain their existing timing.

### Main-model fallback (1.2.36)

After the first successful stage mesh activates, the native main mesh remains hidden for that flight, including the terminal phase and after stage timers become idle. No INI flag is required. A missing later stage mesh keeps the last usable stage visual; loading such a flight resolves the latest available predecessor. If no stage mesh is available, the native main model remains the fallback. Reset/removal releases visual ownership so the game's launch/destruction handling can run normally.
