R10.48 REAR ISLAND WALL REPAIR

R10.46 material rollback and R10.47 glass reflection test did not resolve the reported issue. The user clarified that the wall was visible from the wrong side. The affected New_HullTexture aft-island region contains single-sided wall/window-surround faces. The surrounding source parts commonly contain opposite-facing pairs.

Added 674 reverse-wound faces with corresponding reversed normals to the aft-island region of New_HullTexture, plus the identical 674-face repair to New_HullTexture_Damaged. Original vertices, UV coordinates, textures and material settings are retained. The original faces are retained so both sides have coverage. Added normals are declared before face references to preserve OBJ importer compatibility. The root mesh is now jmsdf_ddh_hyuga_r10_48.obj.

A direct OBJ-face preview that explicitly excludes back-facing triangles reproduced missing exterior wall/window-surround areas in R10.44 and showed continuous exterior wall coverage in R10.48. The earlier unrestricted Blender render was double-sided and masked the defect. Standard Blender mesh validation can also discard coincident reverse faces, so the final diagnostic preserved the source face list directly before culling.

Based on R10.44: flag removed on both ships, recessed torpedo launch origins retained, matte dark finish retained. The unsuccessful material experiments from R10.46/47 are not carried forward. All material/texture, weapon, sensor, animation and damage-configuration files match R10.44. Only the root OBJ and its vessel reference change in the gameplay/model payload.

Checks passed: 619342 total faces; every vertex/UV/normal index is valid at its point of use; values are finite; exactly 1348 reverse faces added across intact/damaged mesh groups; original geometry positions/UV records preserved; ZIP and checksums validated. In-game confirmation is still required. Not installed or uploaded by Codex.

Close Sea Power, back up the old local folder outside StreamingAssets, replace DDH181_Hyuga_SeaPower_Config with this full package folder (do not merge), restart, and spawn a fresh ship. Enable only one Hyuga package while testing. Repeat the rear-island orbit from both sides. Update the existing Workshop item only after confirming the fix in game.
