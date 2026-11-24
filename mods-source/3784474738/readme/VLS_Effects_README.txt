Mk41 VLS effects

LauncherEffect: effects/weapons/emitters/mk41/FireEmitter_mk41_2.ini
Vent jet, emitted for0.45s. Peak1680 particles/s with an emission taper.
Particle lifetime0.75-1.083333s. The same stock16x16 multipass flipbook
transitions from flame to gray smoke. Keep scale1 and the narrow vent source.

LauncherEffect2: effects/weapons/emitters/mk41/smoke_mk41.ini
Residual vent smoke: delay0.07s, emission0.45s, lifetime6.4-9.6s.

LauncherContainerEffect: effects/weapons/emitters/mk41/smoke_mk41_ring.ini
The legacy name is retained for a filled expanding smoke cloud, not a hollow ring.
StartDelay=0.18s, Duration=0.27s: starts40% into the vent emission period;
both fire sources stop emitting at0.45s, then cool and fade. Timing is fixed,
not missile-tail detection. The parent includes fire_mk41_exit.ini and
smoke_mk41_ring3.ini as Birth children. Do not map these children separately.
Ring3 is the slower interior smoke: lifetime8-11s with a soft fade.
The outer cell cloud lifetime is6.4-8.8s.

The source fits inside the reference Mk41 opening. Its local Shape.Position
Y=-0.013 accounts for the mapped cell anchor above the opening in the tested
F123/Mk41 reference arrangement. Other cell anchor heights may require adjustment.

Additional fixed-direction wind is disabled. Particles use world simulation
and retain their authored expansion, rise and turbulence. Smoke animation
phases vary between particles. Keep color gradients at eight keys or fewer.

Vent and cell effects remain separately mapped. Temporary combined DryDock
scenery and timing changes are restored after captures. No DLL change;
WeaponLauncherEffects1.0.31 remains the intended version. Mk57 is deferred.

The low cloud has 50% faster horizontal expansion and broader late puffs.
Smoke lifetimes doubled while initial motion key times were compensated.
Alpha fades progressively; late vent growth is capped to avoid a balloon.
Emission counts and fire/source geometry are unchanged. Longer visibility
increases concurrent smoke and overdraw; no FPS benchmark was performed.
