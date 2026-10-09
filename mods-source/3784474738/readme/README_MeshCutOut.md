# Mesh CutOut

Requires AnchorChain. For the main mesh, add the CutOut keys to `[Models]`, alongside the existing `ResourcesMesh` entry. For a submodel, add them to its existing mesh section listed under `[Submodels]` in the vessel INI. The section's original `Mesh`, `RootMesh`, material and parent settings stay in place. Without CutOut keys, the section loads normally.

For the main mesh:

```ini
[Models]
ResourcesMesh=existing_main_mesh
; Keep the existing ResourcesFolder, ResourcesRoot and material settings.
CutOutRootMesh=vessels/cutouts/cutout_box.obj
CutOutMesh=cutout_box
CutOutPosition=0,0,0
CutOutRotation=0,0,0
CutOutScale=1,1,1
```

Keep your existing `ResourcesMesh` value. Add the keys to the existing `[Models]` section; no additional Submodels entry is needed for the main mesh. These settings affect only the main mesh and its LODs. Submodels use their own independent CutOut settings. Coordinates refer to the selected main mesh's local space.

For a submodel:

```ini
[Submodels]
SubModel1=RadarHousing

[RadarHousing]
Mesh=existing_radar_mesh
; Keep the existing resource/material/parent settings here.
CutOutRootMesh=vessels/cutouts/cutout_box.obj
CutOutMesh=cutout_box
CutOutPosition=0,0,0
CutOutRotation=0,0,0
CutOutScale=1,1,1
```

`RadarHousing` and `existing_radar_mesh` are placeholders: use your existing section and mesh name. Add the keys to that section; do not create a second visible copy of it. Keep the section's existing `SubModelN` entry.

| Key | Meaning |
| --- | --- |
| `CutOutRootMesh` | Full game resource path to the cutter OBJ/root, relative to a mod's content root, without the mod folder name. Required together with `CutOutMesh`. |
| `CutOutMesh` | Name of the cutter mesh/object inside that resource. It is loaded as geometry only and is never displayed. |
| `CutOutPosition` | `x,y,z` translation in the target mesh's local coordinates; default `0,0,0`. SP model units are normally metres. |
| `CutOutRotation` | `x,y,z` Unity Euler angles in degrees; default `0,0,0`. |
| `CutOutScale` | `x,y,z` scale of the cutter vertices before rotation/translation; default `1,1,1`. All components must be nonzero. Negative/mirrored scale is supported. |

The included `cutout_box.obj` is a closed 1 x 1 x 1 box centred at the origin. For example, `CutOutScale=2,3,4` makes it 2 x 3 x 4 model units. To use your own cutter, replace the resource path and object name. Apply transforms in your modelling tool before exporting: only mesh vertex positions are used; an imported cutter object's separate transform is not used. Coordinate orientation follows SP's OBJ importer.

To combine shapes in a modelling tool, join them into one exported mesh object while keeping the solids as separate geometry islands. Do not bridge their vertices or give them coincident shared edges/faces; those cases are ambiguous and may be rejected. Overlapping volumes are supported when their surface topology remains separate. All bodies use the same CutOutPosition/Rotation/Scale; place individual bodies in the mesh before export.

The volumes inside all cutter bodies are removed. Triangles crossing its boundary are split; UV channels, normals, tangents, vertex colours and material slots are carried over. The same local cut is applied to the selected main mesh's or submodel's existing `_lodN` meshes. Each result is a runtime mesh copy. Original files, shared resource meshes, materials and shaders are not edited. There is no per-frame clipping calculation. Existing colliders are not changed.

Small exported face deviations up to 0.002% of a body's diagonal are tolerated during convexity validation. This does not enlarge the clipping or vertex-welding tolerance. Materially concave bodies remain unsupported. A rejection identifies the affected body and its plane deviation in the log.

Limits:

- One cutter mesh per section may contain up to 64 disconnected, closed, convex bodies: cubes, unequal-sided boxes, wedges, pyramids or other convex shapes. All bodies are subtracted; the space between them remains visible. Open, concave, flat, duplicate-face or non-manifold bodies reject the entire cutter with a `[MeshCutOut]` log entry. Export triangulated geometry. UV/normal seams are welded for cutter validation only.
- The configured object needs a direct, static `MeshFilter`. Moving/rotating that submodel is fine. Skinned meshes and blend shapes are unsupported. Child mesh sections must be configured separately. Both the main `[Models] ResourcesMesh` entry and ordinary submodel sections are supported.
- Cut surfaces remain open: no end caps or interior walls are generated. Add separate replacement geometry if needed.
- Damage replacement meshes are separate and remain unchanged. LODs must share the same local coordinate convention.
- CPU-unreadable originals use a synchronous GPU-buffer readback once during loading. This may add loading time. If buffer access fails or returns unusable data, the section keeps its original meshes. The GPU path still needs in-game validation on the intended hardware.
- Maximum cutter in total: 4096 vertices, 8192 triangles, 64 bodies; maximum 128 distinct planes per body. Maximum target: 2 million vertices; maximum result: 1 million triangles per LOD and 16384 fragments per source triangle.

Restart SP after installing/replacing the DLL. Reload the unit/mission after INI or cutter changes; restart if the game has cached an older OBJ. Removing the CutOut keys restores ordinary rendering on the next fresh load.

Compiled, offline geometry-tested and API-checked against the installed public game and saved release/beta assemblies. In-game appearance, GPU readback, loading cost and lifecycle behaviour remain to be verified.

## Keep only the inside (reverse mode)

Add `CutOutMeshReverse=true` alongside the other CutOut keys, in `[Models]` for the main hull or in the existing submodel section:

```ini
CutOutRootMesh=vessels/cutouts/cutout_box.obj
CutOutMesh=cutout_box
CutOutMeshReverse=true
CutOutPosition=0,0,0
CutOutRotation=0,0,0
CutOutScale=1,1,1
```

Only the original surface inside the cutter remains visible. With multiple cutter solids, the areas inside ANY of them are kept; overlaps are rendered once and the gaps between solids are removed. This affects the selected mesh and its LODs. It does not create caps or interior geometry and does not change colliders. Omit the key or set it to `false` for normal cutout mode (remove the inside).

## Reload models and materials: Ctrl + F10

Select your own ship or submarine and press **Ctrl + F10** after saving your changes. This respawns the unit using fresh vessel INI settings, material INIs and OBJ files, including the CutOut cutter meshes. Cutouts and reverse cutouts are recalculated for the new unit and its LODs.

Both Ctrl keys work. Normal F10 keeps its usual debug-panel behaviour. The shortcut is inactive while typing, rebinding keys, or using a menu or console. The usual respawn resets apply.

Only OBJ and material-INI resources requested during this respawn are refreshed, once per resource. Existing units retain their meshes and materials. Basegame resources and texture images remain cached: changed texture assignments work, but replacing image-file contents is not covered by this shortcut. Newly added files may still require a restart if the game's file index has not discovered them.

Restart Sea Power once after installing this DLL. Thereafter, use Ctrl + F10 for edits to existing OBJ and material-INI files. Superseded assets may remain in memory while editing; restarting releases them.
