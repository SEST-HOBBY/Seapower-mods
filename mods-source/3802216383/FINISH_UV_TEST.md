R10.33 hull finish and UV test

Photo-guided neutral gray hull/island finish and matte dark flight deck. Original texture images, including 4K hull and deck detail, remain byte-for-byte unchanged. Weathering, hull numbers, painted markings and tie-down detail are retained. Color is a visual approximation from reference photographs, not a calibrated paint specification.

Projected paint UVs replace single-point UV sampling on the bow plinth, aft CIWS sponson/inner shell and stern repair: 112 faces, 336 added UV coordinates. These pieces now use the existing detailed hull-small texture, at an 8 metre tile scale. Original UV coordinates elsewhere are retained. Removed 918 exactly coincident hull triangles; no distinct surface or vertex positions were removed. Original normals retained. Existing atlas distortion around some stern fittings remains; this is not a complete re-unwrapping of the source ship.

Reduced specular intensity and corrected shininess to the shader's supported range. Offline Blender material/UV previews inspected; Blender does not reproduce the game shader exactly. Final brightness, gloss, distant texture filtering and UV seams require daylight in-game testing.

Checks passed: valid OBJ indices; identical vertex positions and distinct surface geometry; original normal and UV arrays retained; all original texture bytes unchanged; animations and sensor files unchanged; both vessel configurations unchanged except mesh reference and the four material assignments. VLS, crane, CIWS, radar, sonar, rigging and native flag settings preserved. Existing unconfirmed runtime behavior remains unconfirmed.

Replace the previous DDH181_Hyuga_SeaPower_Config folder with this version; do not merge. No direct game installation performed.
