# Retired Workshop mods kept for a SEST pack

A mod here was removed from the Steam Workshop, so no player can download it,
but a SEST pack carries its content. These are its text files as of the last
export that had them; `tools/export-mod-configs.ps1` prunes only numeric
folders at the top of `mods-source/`, so it leaves this folder alone.

| Folder | Mod | Removed | Carried by |
|---|---|---|---|
| `3514484654` | RAAF F-35A Lighting II (Greene) | found 5 Oct 2026 | `SEST_RAAF_F-35A_JATM` (`integration/raaf-f-35a-jatm`) |

The model, textures and weapon meshes were binary files the export never
copied. The F-35A's own model, textures and RAAF livery were recovered later
and live in `integration/raaf-f-35a-jatm/recovered/`; the weapon meshes were
not, so those rounds use models still in the collection (see
`integration/raaf-f-35a-jatm/build_patch.py`).
