R10.51 — IN-GAME SCALE CORRECTION

Both Hyuga and Ise use the corrected shared model. Uniform factor: 1.45.
The previous assumption of 100 metres per model unit was not supported by
stock game geometry. Stock Long Beach 73/83 meshes measure 3.182892799 units
long (m_LocalAABB.z extent doubled); the ship's published overall length is
219.837 metres. This implies approximately 1.448 times the old conversion.
A rounded 1.45 correction matches that reference within approximately 0.2%.
The full Hyuga OBJ including protrusions becomes 2.872031145 units, about
90.2% of the stock Long Beach mesh. The nominal class dimensions stay 197x33m.
Long Beach's INI Length=210 is not its published overall length and was not
used to derive the factor. The Modern US Navy Burke cannot be called oversized
from the old 100m/unit assumption; that earlier conclusion is withdrawn.

Scaled all local OBJ vertices, equipment placement, model-space sensor and
weapon origins, cover pivots, propellers, local flight-deck taxi paths,
launch/recovery/elevator points, elevator translation travel, damage boxes,
compartment height, center of mass, smoke/wake/audio positions, camera framing,
and hull-attached foam dimensions. Native/dependency model roots are scaled
once, with child offsets and scales left intact to avoid double scaling.

Preserved textures, UVs, normals, face winding and the R10.48 wall repair,
removed flag, aft CIWS rotation, weapon IDs/counts (16 ESSM and 12 ASROC),
radar/sonar ranges, speed, displacement, animation angles and timings.
Shared projectiles are not enlarged; the tube-specific weapon's existing
nose-based setback remains unchanged behind each repositioned muzzle.
Navigation circuits/holding routes, deployment cable lengths/depths, effect
offsets in physical units, and shared dependency files remain unchanged.

Close Sea Power. Back up the old mod folder outside the game's mod folders.
Replace the entire DDH181_Hyuga_SeaPower_Config folder; do not merge. Enable
only one local/Workshop copy. Restart and spawn fresh Hyuga/Ise units.
Test against Long Beach: Hyuga should be about 90% as long. Check helicopter
deck contact and both elevators, VLS hatches/launches, all torpedo tube launches,
CIWS, waterline and wakes. These runtime checks are still required.
No game installation or Workshop upload performed.

Earlier retained manifests/reports describe historical builds; this scale
report and scale_correction_manifest.json supersede their coordinate values.
