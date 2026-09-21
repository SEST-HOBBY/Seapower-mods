# Missile Control Surfaces

Version 1.1.1 is a standalone AnchorChain submod that animates existing ammunition
SubModels. Only missiles with marked control surfaces receive a lightweight
LateUpdate controller. Guidance, flight physics, drag and damage are unchanged.

## Automatic axes and mixing (1.1.0)

Author a fin or opposing fin-pair mesh with its hinge/span along local +Y.
Use the ordinary SubModel Position and Rotation keys to place it. No control-axis
or mixing-factor keys are needed:

```ini
[Models]
NumberOfSubModels=2
SubModel1=ControlFinPair1
SubModel2=ControlFinPair2
ControlSurfaceMaxAngle=20
ControlSurfaceFullDeflectionRate=30
ControlSurfaceResponseTime=0.08

[ControlFinPair1]
Type=None
Mesh=fin_pair
Position=0,0,-0.02
Rotation=0,0,45
ControlSurface=True
ControlStages=2

[ControlFinPair2]
Type=None
Mesh=fin_pair
Position=0,0,-0.02
Rotation=0,0,-45
ControlSurface=True
ControlStages=2
```

For a plus arrangement, use Rotation=0,0,0 and Rotation=0,0,-90.
The runtime missile transform flies along +Z; do not confuse its body axes with
the modelling application's export axes. Local +Y here describes the FIN hinge,
not the missile's flight direction.

The controller captures the hinge direction from each loaded, neutral SubModel,
including parent and optional ControlObject rotations, in missile-local space.
It calculates the pitch/yaw mixture once at binding time. World heading and
subsequent fin deflection never feed back into the mixture. There are no
mesh-name, 45-degree or missile-specific rules.

Version 1.1.1 automatically reverses FRONT surfaces relative to REAR surfaces.
The reference is the geometric longitudinal midpoint of the regular flight mesh
(ResourcesMesh), in the missile's local +Z-forward frame. A fin's neutral mesh
bounds determine whether it is ahead of or behind that midpoint, including its
SubModel Position/Rotation and any offsets baked into the mesh itself.

Thus identical rotations at the front and rear produce opposite commands,
without requiring additional keys or mirrored ControlAxis values. Use separate SubModels
(and separately movable meshes) for front and rear fins; one mesh containing
both cannot animate its front and rear parts independently. The example file
shows four SubModels: two aft X-fin pairs and matching fore pairs.

Geometry is inspected once when configuring the missile. The result is stored
in the existing per-fin rate-axis vector, so LateUpdate does no extra work.
Only local hierarchy matrices are composed: no world-aligned renderer bounds
or subtraction of large world coordinates. Hidden normal-flight meshes are
included. Stage/launch-mesh visibility changes do not reclassify the fins.

If geometry is unavailable, the body reference falls back to the missile origin
and the fin location to its neutral transform origin. A surface at the reference
midpoint (within 0.000001 game units) retains the previous rear-fin convention.
This is a geometric visual convention, not a centre-of-mass or aerodynamic
solver. Explicit manual mixing factors remain authoritative and are NOT
automatically reversed by geometric position. A longitudinal hinge cannot steer
automatically and is skipped with a one-time configuration warning.

### Optional direction override

Set ControlDirection in an individual fin's SubModel section:

- Auto (or omit the key): choose the direction from its fore/aft position.
- Normal: force the existing rear/tail convention, regardless of position.
- Reversed: force the opposite of Normal, regardless of position.

For example, ControlDirection=Normal makes a front fin respond like a rear fin;
ControlDirection=Reversed makes a rear fin respond like a front fin.
Reversed does NOT mean "invert the automatically selected result": on a front
fin, Auto and Reversed normally agree. Axis derivation and pitch/yaw mixing
remain automatic. Forced directions also skip the geometry classification.

Values are case-insensitive. An invalid value produces one warning and falls
back to Auto. Existing OVWR files need no changes.

If explicit Pitch/Yaw/Roll factors select manual mixing, Auto and Normal keep
that manual command unchanged; Reversed negates the complete manual command.

Automatic mode mixes transverse pitch/yaw only. A mesh containing an opposing
fin pair cannot independently animate its two halves for roll. Roll animation
requires separate suitable meshes and manual factors.

Small turns use a smooth stronger response, without an artificial minimum:
for normalized demand x (clamped to -1..1), output is 3x/(1+2|x|) times the
maximum angle. FullDeflectionRate still sets the rate for full deflection, and
MaxAngle remains a hard limit. Tiny quaternion changes are evaluated with
atan2 so small turns are not lost when quaternion.w rounds to one.
The existing response-time smoothing remains in place.

## Optional keys and legacy compatibility

Per-surface keys:

- ControlSurface=True opts the SubModel in; Type=None is required.
- ControlDirection=Auto/Normal/Reversed optionally overrides fore/aft direction.
- ControlAxis=x,y,z overrides the local hinge, default 0,1,0. It is transformed
  by the neutral SubModel rotation, not specified in missile/world coordinates.
- ControlMaxAngle overrides the global maximum angle, in degrees.
- ControlFullDeflectionRate overrides the rate in degrees/second for full angle.
- ControlResponseTime overrides smoothing in seconds; 0 is immediate.
- ControlPivotPosition=x,y,z gives a pivot in the animated object's parent
  coordinates. Otherwise its transform origin is used. Mesh origins must
  therefore lie on the intended hinge line.
- ControlObject=child/path selects a child instead of the SubModel root.
- ControlStages=1,2,4-6 restricts visibility/animation to those MultiStage stages.
  ControlStage=2 is an alias. Omit both to keep the fin active in all stages.

If ANY of ControlPitchFactor, ControlYawFactor or ControlRollFactor is present,
that fin uses legacy MANUAL mixing. Missing factors are zero; at least one
must be finite and nonzero. Manual mode retains the old linear response.
To enable automatic mixing, remove all three keys; setting all three to zero
does not enable automatic mode.

Global ControlPitchAxis, ControlYawAxis and ControlRollAxis only affect manual
mixing. For the runtime missile's +Z-forward body frame, explicitly use
1,0,0 / 0,1,0 / 0,0,1 respectively. For compatibility, omitted manual rate axes
retain the historical defaults (X pitch / Z yaw / Y roll).
Automatic mode ignores these named-rate axes.

Global optional defaults are 20 degrees, 30 degrees/second and 0.08 seconds.
Up to 16 marked SubModels and stages 1 through 16 are supported.
Invalid definitions generate a one-time warning, not per-frame log output.

The 1.1.0 migration removes the obsolete ControlAxis, three per-fin factors
and three global rate-axis keys from all 31 currently configured AC Pack
OVWR files. Meshes (including B1/B2 variants), positions, rotations, materials,
stage restrictions and the existing angle/rate/response settings are preserved.

## MultiStage and launch meshes

The mod reads MultiStageMissiles' public CurrentStageNumber through a cached
delegate, with an older private-state fallback and no hard DLL dependency.
Without MultiStageMissiles the missile is treated as Stage 1.

Stage visibility is read every LateUpdate, after mesh switches and before
rendering. The same-frame fix from 1.0.2 is retained. Only discovery of an
absent stage driver is throttled; a bound stage getter is never frame-throttled.

When ResourcesMeshForLaunch provides a launch mesh, marked surfaces remain
hidden until Sea Power switches to the normal flight mesh. This gate is
independent of ControlStages. The original SubModel active state is respected.

The ammunition INI is reopened on container launch/respawn and save restoration.
No global Missile.OnFixedUpdate patch or per-frame INI/component scan is added.
