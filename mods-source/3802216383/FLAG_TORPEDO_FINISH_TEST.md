R10.44 flag removal, torpedo launch-origin and dark-material test

Removed the Hyuga_Naval_Ensign submodel and its native animated-flag binding from both named ships. Submodel numbers remain contiguous. Rigging and fixed staff retained; variant flag texture metadata retained because it does not instantiate cloth geometry. Unused flag assets are no longer referenced by any active flag submodel.

The local Hyuga_HOS303_SingleTube attachment is moved aft along each tube's local launch axis by the largest forward bound of the installed usn_mk46 / usn_mk46_dummy meshes plus 2cm. The Euromod Mk54 ship torpedo uses those meshes. The front bounds are approximately 1.8301m ahead of their origin, explaining why the previous muzzle-centered spawn showed half the torpedo outside. All six projected nose positions now start 2cm behind their original muzzle planes. Container positions/yaws, covers, hatch animations and magazine counts are unchanged. Only the Hyuga-specific weapon-system definition changes; no global torpedo ammunition file overridden. In-game launch timing and ejection/collision behavior still need testing.

Disabled specular intensity, specular colour and Fresnel reflection in nine local dark-painted materials: black, black plain, deep gray, vents, funnel outlets, both flight-deck materials, elevator box and rigging. Texture colours/UVs retained. Glass and other materials unchanged. Lit surfaces may still brighten naturally, and any highlights already present in textures are not removed.

Verified: no active animated flag binding; contiguous submodels; correct launch displacement on all six axes; native launch/body mesh bounds inspected; only the requested vessel binding, local weapon attachment and nine materials changed. Geometry, textures, sensors, damage model and all animation files preserved byte-for-byte. Offline checks passed. Not installed or tested in game.

Test a fresh Hyuga/Ise, check the mast and dark surfaces, then observe a torpedo launch from each side. Replace the previous DDH181_Hyuga_SeaPower_Config folder; do not merge.
