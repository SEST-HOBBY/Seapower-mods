# W88 / Mk 5 reentry vehicle

Ammunition ID: `usn_w88_mk5`. Requires Euromod's current `eu_missile_w88_mk5` mesh, the Trident II material and AC Pack MultiStageMissiles 1.5.0+.

The body uses `assets/europack/models/weapons.obj` and the same `ugm-133a_mat.ini` as Trident II. A separate `eu_missile_w88_mk5_glow.obj` sits above the surface, with nose-bright/aft-fading UVs for the existing shared thermal material. The original mesh and body UVs are unchanged. Regenerate the overlay if the body geometry changes.

This is an unpowered native Missile with inertial point guidance and no seeker. It inherits carrier velocity when spawned by the submunition system. Native drag, guidance and collision rules apply. It is not an unguided Bomb; use `Aim=Point` or `Aim=Parent`. Gameplay damage/explosion settings reuse the existing Trident baseline; Power is not a yield value.

Glow starts cold and fades in over two seconds only when the speed/altitude heating condition allows it. Higher altitude suppresses glow; low speed cools it. Visual tuning uses the existing 1600/3000-knot sea-level-equivalent thresholds and maximum intensity 3. These values are not surface temperatures.

Example carrier entries under `[Models]` (use a free launcher number and update the count):

```ini
NumberOfSubmunitionLaunchers=1
Submunition1Ammunition=usn_w88_mk5
Submunition1Count=1
Submunition1Stage=5
Submunition1Aim=Point
Submunition1Radius=0
Submunition1Position=0,0,0
Submunition1EjectVelocity=0,0,0
Submunition1InitialDrop=0
```

The active Trident override now configures eight single-round launchers, released when Stage 5 starts (currently the 180 s transition). Their stowed meshes occupy the eight plate mounts at 45-degree intervals, each tilted 6 degrees inward. The first mount is Unity `0,0.009923,0.058125`, converted to `Submunition1Position=0,0.666826267,3.906003906` metres. Positions/rotations follow the carrier root; the existing stage meshes contain no baked-in W88 copies. Each stowed copy disappears when its independent round launches, retaining the configured W88 glow. Ejection adds `0,0,2` m/s in carrier coordinates with no drop delay. The engine spawns at most four rounds per physics update, so the eight rounds span two updates.

The provisional spread uses `SubmunitionNAim=Point`, `SubmunitionNRadius=500` and `SubmunitionNInnerRadius=500` on all eight launchers. This samples eight random aimpoints on a 500 m ring, not equally spaced impact positions. Set each InnerRadius to 0 for a filled circle; change each Radius (and InnerRadius for a ring) to resize it. Native flight and the daughter's existing 150 m installation-error setting can move impacts away from those points. This is game tuning, and the radius remains adjustable. Carrier impact remains separate from daughter impact. The accompanying Trident correction sets Stage2SeparationTime=85 (65 + 20 seconds). Numeric separation values are absolute on the launch/controller clock, not durations since the preceding stage. Both nosecone halves now use zero position offsets and outward local velocities (+20,0,-5 and -20,0,-5 m/s).

Restart Sea Power after installing to register the new ammunition and OBJ. Native INI parsing, the installed stage/glow parser and guidance-key recognition passed offline against public release and the available beta snapshot. Geometry/UVs/collider bounds were checked; Blender preview is illustrative, not a screenshot from Sea Power. Asset loading, live reentry flight and Unity glow appearance still need an in-game test.
