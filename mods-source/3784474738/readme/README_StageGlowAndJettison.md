# Thermal glow and multiple jettison objects — 1.3.0

All keys below belong in the ammunition INI's existing `[Models]` section.
This is a visual feature: it does not change missile flight, guidance or damage.
Old single-object jettison configurations continue to work.

## Thermal glow

Define one material for the whole missile. Each stage can select a glow mesh from
`ResourcesFolder` + `ResourcesRoot`, or use a loadable model resource path.
Use your own overlay mesh and texture; these example asset names are placeholders.

```ini
[Models]
NumberOfStages=4
ThermalGlowMaterial=assets/my_mod/materials/missile_glow.ini
ThermalGlowStartStage=2
ThermalGlowStartSpeed=1600
ThermalGlowFullSpeed=3000
ThermalGlowMaxIntensity=3
ThermalGlowHeatUpTime=1.5
ThermalGlowCoolDownTime=4
ThermalGlowFadeInTime=2

Stage1SeparationTime=5
Stage2SeparationTime=12
Stage3SeparationTime=20

Stage2GlowMesh=missile_body_glow
Stage2InheritGlow=False
Stage2GlowStartDelay=0.5
Stage2GlowFadeInTime=2

Stage3InheritGlow=True

Stage4GlowMesh=warhead_glow
Stage4InheritGlow=True
```

Stage 2 starts cold after 0.5 seconds and fades in over at least 2 seconds.
Stage 3 retains the existing glow object, heat and fade progress.
Stage 4 changes the mesh and transfers the heat and fade progress to it.
In the default atmospheric mode, speed **and altitude** affect heating. Speeds are **knots at sea level**:
the same speed produces less heating at higher altitude. These are visual tuning
thresholds, not physical surface temperatures.

| Key | Default / meaning |
|---|---|
| `ThermalGlowMaterial` | Required material resource path; omit to disable thermal glow. |
| `ThermalGlowMesh` | Optional first mesh, also usable without `NumberOfStages` (one stage). |
| `ThermalGlowStartStage` | `1`; earliest permitted stage. |
| `ThermalGlowStartSpeed` / `ThermalGlowFullSpeed` | `1600` / `3000` knots; full must exceed start. Set **both to `-1`** for time-driven engine glow. Omission keeps atmospheric defaults. |
| `ThermalGlowMaxIntensity` | `3`, range 0–100; multiplies material RGB. |
| `ThermalGlowHeatUpTime` / `ThermalGlowCoolDownTime` | `1.5` / `4` seconds, range 0.01–3600; response time constants. |
| `ThermalGlowStartDelay` / `ThermalGlowFadeInTime` | `0` / `2` seconds, range 0–3600. |
| `StageNGlowMesh` | Omit/empty to keep the preceding mesh. |
| `StageNGlowEnabled` | `True`; `False` hides glow and stops that stage's heating. The next enabled stage starts cold. |
| `StageNInheritGlow` | `True`; inherit heat, delay and fade progress. `False` starts cold with this stage's timing. |
| `StageNGlowStartDelay` / `StageNGlowFadeInTime` | Override global timing when starting cold. Inheritance does not restart these timers. |
| `StageNGlowHeatUpTime` / `StageNGlowCoolDownTime` | Override the global thermal response times. |
| `StageNGlowPosition` / `StageNGlowRotation` / `StageNGlowScale` | Local `x,y,z`; rotation in degrees, scale positive. Same mesh retains previous values; new mesh defaults to `0,0,0`, `0,0,0`, `1,1,1`. |

The glow is attached to the visible stage mesh, or to the native missile mesh
when no stage mesh is configured. Its offsets use the model's local units.
Give the overlay enough surface clearance to avoid z-fighting.

The material must expose `_TintColor` or `_EmissionColor`. For a transparent
overlay, an additive material can be defined as follows:

```ini
[Shader]
Path=Legacy Shaders/Particles/Additive
[Properties]
_TintColor=Color,{*}FF5020FF
_InvFade=Float,1
[Textures]
_MainTex=assets/my_mod/textures/missile_heat.png
```

Use a texture with soft transparent edges and suitable UVs on every glow mesh.
Color comes from the material. Brightness is individual to each missile; the
cached resource material is never modified. Glow does not create a point light.
An unsupported/missing material logs a warning and disables only thermal glow.

New saves preserve the current stage, heat and fade progress. Old saves without
thermal data restore their inferred stage cold. Pausing freezes thermal time.

## Time-driven engine/nozzle glow (1.5.2)

Set both speed keys to `-1` in `[Models]`. This selects one time-driven glow
channel for the missile; no altitude or speed is read in this mode. Omitted
speed keys retain the old atmospheric defaults. A single `-1` is invalid and
falls back to atmospheric defaults with a warning.

```ini
[Models]
ThermalGlowMaterial=assets/my_mod/materials/nozzle_glow.ini
ThermalGlowStartSpeed=-1
ThermalGlowFullSpeed=-1
ThermalGlowMaxIntensity=1
ThermalGlowHeatUpTime=2
ThermalGlowCoolDownTime=8
ThermalGlowFadeInTime=0
Stage1GlowMesh=nozzle_glow
Stage1BurnTimeDelay=1
Stage1BurnTime=12
```

This nozzle heats from Stage 1 age 1 to 13 seconds, then cools while its mesh
remains attached. `StageNBurnTimeDelay` and `StageNBurnTime` define this visual
heating window independently of whether stage thrust is configured. Missing
BurnTime means heat until the stage ends; `0` means cooling only. Separation can
remove the nozzle earlier. Native booster/sustainer times are not inferred.

Heat/cool values remain **time constants**, as in atmospheric mode: roughly 63%
of the change after one time constant and 95% after three. Stage glow delay and
fade still apply; use FadeInTime=0 if only the heat response should shape onset.
No heat accumulates before GlowStartDelay has elapsed.

Keep `StageNGlowEnabled=True` during cooling. `False` hides the overlay
immediately, as before. To keep a hot nozzle in a following coast stage, inherit
its mesh/heat with `StageNInheritGlow=True` and set that stage's BurnTime=0.
The new stage's burn window starts from its own age; inherited heat/fade does
not restart. Use InheritGlow=False when revealing a different cold engine.
An optional JettisonGlowMesh cools on detached debris as before.

One material/overlay channel is active per missile. This mode does not add a
second simultaneous atmospheric overlay. Existing atmospheric ammunition INIs
need no changes. No engine meshes are bundled.

## Up to 32 jettison objects per stage

The original unnumbered keys configure object 1. Add suffixes `2` through `32` for
additional objects. Slots may have gaps. Each configured object is emitted once
when its stage is left; the final stage needs a following transition to jettison.

```ini
Stage2JettisonMesh=cover_left
Stage2JettisonMeshPosition=-0.02,0,0
Stage2JettisonVelocity=-4,0,0
Stage2JettisonAngularVelocity=0,0,30
Stage2JettisonLifetime=15
Stage2JettisonGlowMesh=cover_left_glow

Stage2JettisonMesh2=cover_right
Stage2JettisonMeshPosition2=0.02,0,0
Stage2JettisonVelocity2=4,0,0
Stage2JettisonAngularVelocity2=0,0,-30
Stage2JettisonLifetime2=15
Stage2JettisonGlowMesh2=cover_right_glow
Stage2JettisonAudioClip2=audio/my_mod/cover_release.wav
Stage2JettisonAudioVolume2=0.5
```

Each object independently supports `JettisonMesh`, `JettisonMeshPosition`,
`JettisonMeshRotation`, `JettisonVelocity`, `JettisonAngularVelocity`,
`JettisonLifetime`, `JettisonEffectDuration`, `JettisonAudioClip`,
`JettisonAudioVolume`, and `JettisonAudioDebug`, with the slot suffix at the end.
Positions/rotations are missile-local model units/degrees. Velocity is local
**metres per second added to missile velocity**; angular velocity is local
**degrees per second**. Defaults: lifetime 25 seconds, audio volume 1.
Omitted velocities retain the original gentle separation and random tumble.

Effects follow the native effect naming convention:
`Stage2JettisonEffect2`, `Stage2JettisonEffect2Class`,
`Stage2JettisonEffect2Position`, `Stage2JettisonEffect2Rotation`,
`Stage2JettisonEffect2Scale`, `Stage2JettisonEffect2ContinuousChildren`.
The duration key is `Stage2JettisonEffectDuration2` (seconds; `-1` follows debris
lifetime, `0` disables the effect). No suffix is used for object 1.

Optional `StageNJettisonGlowMesh[2..8]` gives that piece its own glow overlay.
It inherits the departing missile's visible heat, then cools using that stage's
cooldown time and the shared glow material. Its local mount can be set with
`JettisonGlowPosition`, `JettisonGlowRotation`, `JettisonGlowScale` and the slot
suffix. These coordinates are relative to the debris, not the missile.

Jettison pieces are visual debris, not independently damaging weapons. Detached
visual debris is not serialized; loading does not replay previous jettisons.
No weapon-specific assets or ammunition overrides are included.
