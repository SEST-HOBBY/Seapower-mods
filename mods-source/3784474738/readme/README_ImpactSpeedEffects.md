# Impact speed hit effects (MultiStageMissiles 1.7.14)

Put the alternate effect in the ammunition's existing [Particles] section.
Works on missiles and missile submunitions without requiring stages.

~~~ini
[Particles]
HighSpeedHitDefaultExplosion=effects/your_kinetic_hit.ini
HighSpeedHitDefaultExplosionUseTargetVelocity=True
~~~

The effect definition enables the feature. The direction flag is optional.
Ammunition without a HighSpeed effect definition retains ordinary effects.
No damage, guidance, collision or fuze parameters change.

These values are built-in defaults; omit them from ammunition INIs:

| Optional key | Default |
| --- | ---: |
| HitEffectSpeedThreshold | 3000 |
| HighSpeedHitEffectScaleMinSpeed | 3000 |
| HighSpeedHitEffectScaleMaxSpeed | 12000 |
| HighSpeedHitEffectScaleMin | 0.5 |
| HighSpeedHitEffectScaleMax | 5 |

At 3000 knots the alternate starts at factor 0.5; at 7500 knots its factor is
2.75; at and above 12000 knots its factor is 5. Below the threshold the ordinary
effect remains. Any key can override its default independently.
MinSpeed/MaxSpeed are finite knots, with 0 <= MinSpeed < MaxSpeed.
Size factors satisfy 0 < Min <= Max <= 20; the default maximum is 5.
To use a fixed factor, set both ScaleMin and ScaleMax to that same value.
An invalid explicit setting disables this ammunition's override with a warning.

HitEffectSpeedMode defaults to Sum (missile speed plus actual hit-object speed).
Relative uses the magnitude of the velocity difference instead: head-on sum,
pursuit difference, vector result for crossing paths. The selected mode controls
both threshold and visual size. A stationary land/water hit uses missile speed.
Invalid moving directions retain the ordinary effect. No intended-target
substitution. Targetless mid-air destruction retains its ordinary effect.

Optional specific overrides, also in [Particles]:
- HighSpeedHitAirExplosion
- HighSpeedHitShipExplosion
- HighSpeedHitObjectExplosion
- HighSpeedHitGroundExplosion
- HighSpeedHitWaterSplash
- HighSpeedExplosionOverwaterSplash

For Default/Air/Ship/Object/Ground explosions, selection prefers the matching
specific entry, then HighSpeedHitDefaultExplosion, then HighSpeedHitAirExplosion
for older air-only configurations, then the ordinary effect. Thus the Default
entry alone also covers air hits. Duplicate Air entries are unnecessary.
Explicit entries including None win. Splash slots stay independent; for open-water
impacts use HighSpeedExplosionOverwaterSplash when the game selects that slot.
Dud, shockwave and debris effects are unchanged.

The standard Effect loader supports Class, Position, Rotation and Scale suffixes.
Missing/unavailable assets fall back to the generic alternate or ordinary effect.
INI audio and Models/IndependentEffectInstances=True continue to apply.

HighSpeedHitDefaultExplosionUseTargetVelocity=True aligns the selected Default
effect with actual target velocity, including when used for an Air/Ship/Object/
Ground hit. HighSpeedHitAirExplosionUseTargetVelocity=True follows the selected
Air effect, including its fallback uses. Both flags default False. The selected
effect's flag controls behavior; explicit ship/object/ground overrides retain
native orientation. A missing, stationary or invalid target retains native motion.

World/Custom-space particles with InheritVelocity=Initial retain the midpoint
of their configured fraction of target velocity in world coordinates. Random
ejection remains in start speed/shape. Existing linear-velocity modules and
Local-space particles retain native behavior. Floating-origin handling is retained.

Size multiplies particle size, emission shape, child offsets, random ejection
speed and noise displacement on the instance. Lifetime, counts, target momentum,
damage, sound and lights are unchanged. Splashes, dud and native debris do not
scale. Nonparticle mesh renderers and existing linear-velocity modules do not scale.
Settings restore on disable for pooling. Scaling is visual, not an energy calculation.

Legacy HighSpeedHitEffectScaleReferenceSpeed remains supported when no explicit
speed bound is present: factor = clamp(speed / reference, Min, Max). A reference
must be positive and finite. An explicit speed bound selects range scaling, with
the missing bound using its default. Omission of all scale keys uses the defaults.

Inactive high-speed copies returned by the native pool are activated after
orientation, size and motion setup. Active copies are not restarted; native
pooling/lifetime and PlayOnAwake=False remain. No cooldown or frame polling.
The first 16 configured destruction events per ammunition log speed/threshold,
selected effect, size, target motion, activation and spawn result. These entries
do not prove that the camera saw particles.

Current AC Pack coverage (2026-10-17): 65 existing profiles (55 SAM kinetic effects
and 10 AIM warhead effects) inherit the defaults above. Redundant Air definitions
are removed, or migrated to Default for former air-only profiles. Effect assets,
direction settings and speed modes are retained. No preset is added to previously
unconfigured ammunition. Fully restart Sea Power after INI/DLL changes.
