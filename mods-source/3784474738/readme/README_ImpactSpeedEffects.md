# Impact speed hit effects (MultiStageMissiles 1.7.12)

Put these keys in the ammunition's existing [Particles] section.
Works on missiles and missile submunitions without requiring stages.

~~~ini
[Particles]
HitEffectSpeedThreshold=2000
HighSpeedHitDefaultExplosion=effects/your_kinetic_hit
~~~

Replace the example path with an existing effect. At or above 2000 knots
configured impact speed, the alternate effect replaces the ordinary hit explosion.
Below the threshold, or without HitEffectSpeedThreshold, native effects remain.
No damage, guidance, collision or fuze parameters change.

By default, speed is the sum of missile and actual hit-object speed magnitudes.
Set HitEffectSpeedMode=Relative to account for both flight directions: magnitude
of the velocity difference (head-on sum, pursuit difference, vector result for
crossing paths). The selected mode controls both threshold and visual scaling.
A stationary land/water hit uses the missile's speed. Invalid moving directions
retain the ordinary effect. No intended-target substitution.

Targetless mid-air self-destruction retains its ordinary effect.
The intended target's speed is not used when a different object is hit.

Optional specific overrides, all in [Particles]:
- HighSpeedHitAirExplosion
- HighSpeedHitShipExplosion
- HighSpeedHitObjectExplosion
- HighSpeedHitGroundExplosion
- HighSpeedHitWaterSplash
- HighSpeedExplosionOverwaterSplash

Selection order for Default, Air, Ship, Object and Ground explosions:
1. The matching HighSpeed entry.
2. HighSpeedHitDefaultExplosion.
3. HighSpeedHitAirExplosion, for existing air-only configurations.
4. The ordinary effect.

Thus an existing HighSpeedHitAirExplosion also covers ship, object, ground and
default hits above the threshold; no additional INI keys are required.
Explicit per-slot entries (including None) remain authoritative.
Splash entries are independent:
the generic high-speed explosion does NOT replace accompanying water splashes.
For a missile striking open water, use HighSpeedExplosionOverwaterSplash because
the game can select only that splash slot.

Each alternate uses the standard Effect loader, including the Class, Position,
Rotation and Scale suffixes. For example HighSpeedHitAirExplosionScale=1.5,1.5,1.5.
INI effect audio and Models/IndependentEffectInstances=True continue to apply.
An explicit None suppresses that alternate slot. Missing/unavailable assets
fall back to the generic alternate or ordinary effect. Dud, shockwave and debris
effects are not replaced. Native air/land/ship/object classification is retained.

The threshold accepts a finite nonnegative number in knots (0 means every eligible
impact). Invalid thresholds disable this feature for that ammunition with a warning.
Settings are loaded with ammunition resources, not read per frame or per hit.
Fully restart the game after editing INIs.

Optional size scaling in [Particles] (requires MultiStageMissiles 1.7.12):
~~~ini
HitEffectSpeedMode=Relative
HitEffectSpeedThreshold=3000
HighSpeedHitEffectScaleMinSpeed=3000
HighSpeedHitEffectScaleMaxSpeed=5800
HighSpeedHitEffectScaleMin=0.5
HighSpeedHitEffectScaleMax=5
~~~
At MinSpeed the factor is Min; at MaxSpeed it is Max. Between those speeds,
size grows linearly (4400 knots = 2.75 in this example). Above MaxSpeed it stays
at Max. Below the hit threshold the ordinary effect remains.
Both speed bounds must be finite, with 0 <= MinSpeed < MaxSpeed. Size factors
must satisfy 0 < Min <= Max <= 5. Speeds use HitEffectSpeedMode and are in knots.

The earlier HighSpeedHitEffectScaleReferenceSpeed option remains supported:
factor = clamp(impact speed / reference speed, Min, Max). Explicit MinSpeed and
MaxSpeed take precedence over ReferenceSpeed. Omit both speed bounds and
ReferenceSpeed to keep fixed INI size. A partial or invalid range disables this
ammunition's high-speed override with a warning.

This factor multiplies the selected main hit's existing particle sizes, emission
shape, child offsets, random ejection speed and noise displacement. It leaves
lifetimes, counts, inherited target momentum, damage, sound and lights unchanged.
Splashes, dud and native debris do not scale. Intended for particle-based effects;
nonparticle mesh renderers and pre-existing linear velocity modules are not scaled.
Values are applied to the spawned instance, never its shared prefab, and restored
on disable before pool reuse. Below the threshold the ordinary effect still runs.
The scale is artistic, not an explosion-energy or damage calculation.
For diagnosis, Player.log records the first 16 configured destruction events per
ammunition type per game process: actual target, missile and target speeds,
configured impact speed/mode, threshold, size factor, native/alternate decision, selected slot, target-motion decision
and spawn result.
Targetless air destruction and below-threshold decisions are recorded too.
This runs only on destruction/effect events, never as a per-frame speed check.
A successful spawn does not prove the camera saw the particle effect.

Optional target direction and particle motion, in [Particles]:

~~~ini
HighSpeedHitDefaultExplosionUseTargetVelocity=True
~~~

This aligns the selected HighSpeedHitDefaultExplosion with the actual hit object's
velocity, including when it supplies an Air, Ship, Object or Ground fallback.
HighSpeedHitAirExplosionUseTargetVelocity=True does the same for the selected
air effect, including when that effect supplies a Default/Ship/Object/Ground hit.
Both settings default to False. The selected effect's setting applies:
an explicit air effect uses its own flag, not the default effect's flag.
An explicit ship/object/ground override keeps native orientation.

Without a moving actual hit object (or with invalid velocity), native orientation
and particle motion remain. The intended target is never substituted.
Eligible World/Custom-space particles with InheritVelocity=Initial retain their
configured fraction of target velocity. Existing linear velocity modules and
Local-space particles stay unchanged. Splash, dud, shockwave and debris effects
do not inherit target motion. Setup runs once per hit, with no per-frame update.


Current AC Pack SAM coverage (2026-10-17)

The KV high-speed preset is assigned only in the 55 existing SAM override files
under AC Pack/ammunition_overwrite: IRIS-T SLM/SLX, Aster, CAMM, PAC-3 MSE,
RIM variants and SA/SA-N variants. Their existing extend targets remain unchanged.
The 65 existing high-speed profiles (55 SAM and 10 AIM profiles) use threshold
3000 knots and size factors 0.5 at 3000 knots through 5 at 5800 knots.
The selected speed mode and each profile's existing high-speed effect asset
remain unchanged: the AIM profiles retain their previous warhead effects.
Ordinary hit entries remain unchanged. No high-speed preset is added to
previously unconfigured ammunition. Restart Sea Power to discard cached resources.


Selected high-speed effects are activated after orientation, scale and target-motion
setup if the native pool returns an inactive copy. Native pooling and lifetime
cleanup are retained; no cooldown or extra INI key is added. Already-active copies
are not restarted. PlayOnAwake=False is respected.
Diagnostics include activated (this correction was needed) and active (the returned
object is active in the scene). Neither value alone proves particles were visible.
