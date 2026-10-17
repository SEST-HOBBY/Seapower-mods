Kinetic hit effects
===================
Large: effects/explosions/emitters/kinetic_kill_hit/kinetic_kill_hit.ini
Compact / PAC-3: effects/explosions/emitters/kinetic_kill_hit_pac3/kinetic_kill_hit_pac3.ini

Both visuals use native INIs, included mesh/material files and basegame resources.
The visuals themselves do not require AC Pack or a plugin DLL.
Complete copies are installed in AC Pack; Radar Test is not required.

Euromod ammunition:
- SM-3 Block IA, IB and IIA: original MediumMissileExplosions class.
- PAC-3 MSE: original SmallMissileExplosions class.
- No custom kinetic effects installed or assigned in Euromod.

AC Pack ammunition_overwrite for these four missiles:
[Particles]
HitAirExplosionClass=
HitAirExplosion=effects/explosions/emitters/kinetic_kill_hit_pac3/kinetic_kill_hit_pac3.ini
HitEffectSpeedThreshold=2000
HighSpeedHitAirExplosion=effects/explosions/emitters/kinetic_kill_hit/kinetic_kill_hit.ini

The normal air-hit effect is compact. The large effect replaces it when missile
speed + actual hit-object speed reaches 2000 knots. Directions are ignored.
This switch requires the installed MultiStageMissiles 1.7.6 DLL. Without that
plugin only the native HitAirExplosion is used. Targetless self-destruction
retains the ordinary effect. The threshold is artistic tuning, not a physical
boundary. All these entries belong in the existing [Particles] section.
A blank Class clears inherited effect-class selection in an overwrite.

Large: 1096 visible burst particles, blue-white flash, 1.6 s expanding ejecta
shell, warm fragment streaks and debris lasting up to 6.5 s.
Compact: 480 visible burst particles, 0.16 s white-yellow flash, 0.44 s halo,
brief weak expansion, decelerating/falling fragments, 1.8-4.8 s drifting smoke.
World simulation; no added sound or dynamic point light. Local +Z is the
forward debris cone; the effect cannot determine relative collision direction.

Restart Sea Power after editing ammunition/resource INIs.
Validation: native key/resource checks and installation equality; new visuals
and speed switching still need an in-game interception test.
