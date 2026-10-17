Kinetic hit effects
==================
Large: effects/explosions/emitters/kinetic_kill_hit/kinetic_kill_hit.ini
Compact: effects/explosions/emitters/kinetic_kill_hit_pac3/kinetic_kill_hit_pac3.ini

Native INI visuals work without an extra plugin. Dynamic target motion and the
speed-dependent switch require AC Pack / MultiStageMissiles 1.7.8 or later.

AC Pack SM-3 / PAC-3 ammunition, in the existing [Particles] section:
HitAirExplosionClass=
HitAirExplosion=effects/explosions/emitters/kinetic_kill_hit_pac3/kinetic_kill_hit_pac3.ini
HitEffectSpeedThreshold=2000
HighSpeedHitAirExplosion=effects/explosions/emitters/kinetic_kill_hit/kinetic_kill_hit.ini
HighSpeedHitAirExplosionUseTargetVelocity=True

The switch adds missile and actual hit-object speed magnitudes, in knots.
It is an artistic threshold, not a physical damage or collision-energy model.
Euromod standard assignments remain original. Targetless self-destruction
retains its ordinary visual. Compact and conventional warhead effects unchanged.

UseTargetVelocity defaults to False. True aligns the explicit high-speed air
visual's local +Z with actual target velocity. World-space particle emitters
with [InheritVelocity] Mode=Initial use Curve as the retained fraction.
The plugin sets native local linear particle motion once, including in the
game's relocated world frame; pool cleanup restores the original modules.
Emitters with an existing VelocityOverLifetime module are left unchanged. No guidance/damage/native debris changes or added sound.
Missing/zero/nonfinite target motion leaves the native visual frame intact.
Only an explicit HighSpeedHitAirExplosion override can use this feature.

Large: 183 visible burst particles. A 0.16 s warm-white flash, 0.38 s halo,
three torn conical sheets fading by 1.3 s and a small transverse ring, brief small sparks,
seven larger glowing survivors lasting 3.2-5.4 s and 20 tumbling solid pieces.
No opaque spherical fireball, long attached smoke trails or duplicate audio.
Static DryDock has no live target velocity; its spread shows relative ejection
only. A real interception adds target momentum on top of that spread.

Restart Sea Power after DLL or ammunition edits. DryDock Reload can refresh
visual INIs. Ordinary mission effects may remain cached until restart.
