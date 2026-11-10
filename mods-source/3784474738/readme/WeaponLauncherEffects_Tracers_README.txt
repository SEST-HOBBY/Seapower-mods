WeaponLauncherEffects: custom tracers and visual ABM

Place this section in a projectile ammunition INI or ammunition OVWR:

[CustomTracers]
Enabled=True
Color=Red
EveryNthRound=5
SizeMultiplier=1
LengthMultiplier=1
Brightness=1
WaterRicochet=True
BurnTime=0

Color accepts the native Red, Yellow and Green presets, White, Orange or #RRGGBB.
Size and length use the AK630 tracer as the 1.0 reference. EveryNthRound counts
rounds for EG-managed projectiles; native CIWS uses the equivalent particle rate.
BurnTime is seconds; 0 adds no light-duration limit. WaterRicochet is visual only.
Custom tracers replace native projectile/tracer visuals only for that weapon's
configured ammunition. Muzzle effects, sound and other weapons are unaffected.
Use WaterRicochet=False for ABM ammunition.

WeaponLauncherEffects works without ExtendedGuidance. If EG is enabled, its
actual projectile positions and burst events drive the custom visuals.

Standalone visual ABM uses the existing ammunition section:

[ExtendedWarhead]
EffectType=KETF
AirMode=Timed
Caliber=30

Caliber is in millimetres; common ammunition filename formats are also supported.
AirMode=Timed enables the visual timer against air targets. KETF places the
visual burst ahead of the estimated target; other timed effects use arrival time.
The effect is taken from the ammunition's native hit-air-explosion setting.

Without EG, this is presentation only: native fuze, collision, damage, health and
ballistics remain unchanged. A visible burst therefore does not guarantee damage.
Gun shells use native launch time-to-target. Native CIWS uses visible tracer
particles and estimates time from the native aim position and muzzle velocity;
it does not create a separate effect for every abstract damage round.
Early water impacts or particles already removed by native collision do not
produce a later phantom airburst. With EG ownership there is no second timer.

Restart Sea Power after enabling/disabling either submod or changing DLLs.
