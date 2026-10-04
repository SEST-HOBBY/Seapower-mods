R10.29 VLS hatch and launch alignment test

Separated all 16 original lids into local hinged submodels. Preserved their closed positions. Added 32 open/close animations using Asahi's NumberOfHatchesPerContainer, ContainerN_Hatch1 and ContainerN_Open/CloseHatchAnimation pattern, with the same 1.2-second timing. Rotation uses each Hyuga lid's longitudinal outer hinge axis, opening outward to 95 degrees. Dark aperture surfaces conceal the underlying static deck skin; these are visual recesses, not full-depth cell interiors.
Retained the existing 12 quad-packed ESSM cells (48 rounds) and 4 ASROC cells. Launch origins now use the measured individual lid centers, including their small row offsets, with the spawn depth approximately five metres below the hatch as in Asahi. Four inherited ESSM attachment offsets fit inside each lid footprint. No changes to missile performance or inventory.
VLS damage collider moved from its incorrect forward position to the aft launcher footprint.

Offline verification: closed-pose lid reconstruction, all OBJ indices, 32 animation references, 16 container/hatch links, ESSM four-round footprint fit, preservation of sonar/radars/CIWS, and open/closed Blender previews passed. These are static/config checks, not in-game firing validation.
In a fresh scenario, fire ESSM and ASROC separately. Check the selected lid opens before launch, the round exits through that cell, and the lid closes afterward. Check later rounds in a quad pack too. All-lids-open preview is a geometry check only; runtime hatch timing and firing order remain unverified.
Replace the previous mod folder; do not merge. No direct game installation performed. Asahi/Euromod animation configuration credited as the reference; ship's original lid geometry retained.
