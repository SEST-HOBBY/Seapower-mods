Mk57 twin exhaust

Mapped to eu_mk57 and eu_mk57_quad in systems/WeaponEffect_Mapping.ini.
Same ContainerBase frame and two-layer fire/smoke setup as Mk41.
Each layer has two Birth subemitters, driven by an invisible rate carrier.
Total visible emission rates: fire 2000/s, smoke 50/s, unchanged from Mk41.
Mk41 materials, colors, upward velocity and smoke timing are retained.
Strip width follows the two eu_mk57_exhaust panels: 0.014739 units (~0.99 m).
Particle size is reduced by the same width ratio (~half).
Offsets include the exhaust child Position=0.00502,0.001671,0.
Local X follows panel length; separation is local Z; exhaust velocity is local +Y.
The exhaust hatch opens by -75 degrees around Z; the plume stays aligned to
ContainerBase and the opening, rather than following the rotating hatch lid.
The native per-cell smoke ring is assigned as for Mk41.
No DLL, workshop model, gameplay reload value or original Mk41 effect changed.
Verified geometry against all 20 Zumwalt mount definitions (40 centers).
Offline geometry/INI check only; no in-game visual validation.

Orientation correction: positions and strip width now belong to the parent mesh
shape. Birth children emit at zero offset. Child Shape.Position was reproduced
as world-oriented in an isolated Unity test and must not be restored. Both
children sample the two equal-area ports through their shared parent births.
The mesh is emission geometry only, not a rendered ship/model replacement.
Offline Unity particle-position tests cover all four authored mount yaws.
In-game confirmation of the corrected version remains pending.
