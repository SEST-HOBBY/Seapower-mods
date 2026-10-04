R10.50 VLS LOADOUT CORRECTION

Corrected the inherited 48 ESSM / 4 ASROC loadout to 16 ESSM / 12 VL-ASROC, representing the published Hyuga-class baseline. Four Mk41 cells are quad-packed for ESSM, twelve hold one ASROC each. The JMSDF official Maizuru page confirms the aft VLS supports anti-air missiles and ASROC but does not publish the exact split or suffixes. WeaponSystems.net class specifications list the 16/12 load. This is a published-reference baseline, not a verified manifest for every ship/date. Exact physical allocation among the sixteen cells is a mod implementation choice, not a documented real loading plan.

Retained the Asahi-compatible Euromod ammunition IDs usn_rim-162b (ESSM Block I, non-Aegis Mk41 per the installed definition) and usn_rum-139c (ASW missile with usn_mk54_asroc torpedo submunition). Their exact Japanese operational subvariants are not independently verified. No shared Euromod weapon performance definitions or ranges changed. Ship-launched Mk54 tube torpedoes remain the existing gameplay proxy and are outside this VLS correction.

All sixteen existing physical cell positions, rotations, hatch meshes and open/close animation bindings are preserved exactly. Cells 1-4 now belong to ESSM, 5-16 to ASROC. The two launcher definitions still provide four and one attachment positions respectively. Magazine counts exactly match 4x4 and 12x1 capacity. No added reserve missiles. Geometry, UVs, materials, radar/sonar settings, torpedo tube launch correction, flag removal and confirmed R10.48 wall repair remain unchanged. Includes R10.49 reference-card work.

Verified all sixteen cells are assigned once, unchanged cell transforms/hatch bindings, four edited weapon/magazine sections only, intact animations and model assets. Runtime firing, guidance, depletion and ASROC payload deployment still need an in-game test with this configuration and the installed dependency versions.

Install: close Sea Power, back up the previous mod folder outside StreamingAssets and replace the entire DDH181_Hyuga_SeaPower_Config folder. Do not merge or enable both local and Workshop copies. Restart and spawn a fresh ship. The reference should show RIM-162B x16 and RUM-139C x12. Remove old standalone Ise vessel files through clean replacement; select Ise as a Hyuga Class variant. No game installation or Workshop upload performed by Codex.

Sources:
https://www.mod.go.jp/msdf/maizuru/units/
https://weaponsystems.net/system/574-Hyuga%2Bclass
Installed Euromod Main Pack: ammunition/usn_rim-162b.ini, ammunition/usn_rum-139c.ini, systems/weapons.ini.
Asahi reference: vessels/jmsdf_dd_asahi.ini.
