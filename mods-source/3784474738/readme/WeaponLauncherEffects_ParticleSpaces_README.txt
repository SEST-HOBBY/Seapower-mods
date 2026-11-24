WeaponLauncherEffects: launcher particle spaces

Main.SimulationSpace and each velocity/force/limit module's Space are respected
as authored by the effect. World smoke stays in the world after emission;
Local particles follow their emitter. The source still follows its configured
launcher/container anchor. Mixed module spaces remain supported.

Example effect sections:
[Main]
SimulationSpace=World
[VelocityOverLifetime]
Space=World

Keep emission onset and duration in the effect INI. This revision adds no
automatic missile-clearance delay and no wind override. Existing mapping
positions and rotations remain authoritative. Restart Sea Power after updating
the DLL; it cannot replace a loaded DLL through effect reload.
