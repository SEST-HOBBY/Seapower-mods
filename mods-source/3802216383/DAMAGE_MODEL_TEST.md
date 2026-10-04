R10.41 damage model fit test — Hyuga and Ise

Changes:
* 33 declared collision volumes, up from 22. Eleven hull envelopes clipped from the current painted hull geometry replace three coarse boxes. This restores upper-hull coverage and follows the fore/aft taper more closely; these remain simplified boxes, not an exact watertight collision mesh.
* Propeller hitboxes fitted to the actual local meshes and mount positions, including full rotational sweep. CIWS hitboxes moved to current mounts with swept-assembly allowance; separate magazine volumes placed underneath.
* Dedicated damage volumes for the main OPS-20 scanner and auxiliary navigation scanner. Tactical datalink separated from the fixed-array volume. Fixed-array and CIC volumes moved into the forward island region. These internal/system locations are model-based gameplay approximations, not a verified Hyuga compartment plan. One logical FCS-3 sensor remains: this is not independent per-face radar damage.
* CompartmentsHeight reduced from 0.25 to 0.15255 to match the modeled waterline-to-flight-deck height. Native definitions identify this setting as affecting buoyancy-compartment height and missile aimpoint; intact trim, flooding and sinking need testing.
* Dedicated damaged variants for Hull, New_HullTexture, Hull_RedDark, New_HullSmall and New_Black. Two modest inward waterline dents use the same deformation across adjoining materials. Local triangles subdivided to support curvature and UVs/normals retained/interpolated. Intact geometry preserved exactly. Native ResourcesDamagedMesh / DamagedMesh bindings used, following stock vessel definitions.

Damage visual limits:
The damaged-state geometry is a generic buckled-hull appearance, not a procedural hole at the actual strike location. The engine controls damage-state activation and impact effects; swap timing has not been tested in game. This build does not implement severed hull sections, custom compartment flooding simulation, or a validated real-world number of torpedoes required to sink the ship.

Preserved:
Armor, displacement, density, four damage-control teams, main machinery volume and rudder setup retained. Hangar remains one logical flight-deck system using the native single Collider binding, with the existing geometrically fitted volume. No unsupported multi-collider system syntax added. Weapons, radar/sonar ranges, torpedo and VLS animations, crane, crew, safety fittings, flag, textures and two named variants retained.

Validation:
33 unique collider declarations, positive extents and all system/collider references verified. All damaged mesh references and OBJ indices valid. Original root geometry remains an exact prefix of the new OBJ. Original other assets, textures, systems and animations are byte-identical. Propeller hitboxes contain mesh positions over 37 sampled rotations; radar boxes contain the native scanner's full rotational envelope. Intact/damaged port and starboard previews inspected. These are offline checks, not in-game confirmation.

Suggested test:
1. Load a fresh Hyuga or Ise and verify intact appearance, waterline/trim and movement first.
2. Apply one torpedo hit and inspect flooding, propulsion loss and the damage-control display. Compare fore, amidships and aft hits in separate fresh runs.
3. Check direct hits near CIWS/scanners for the intended system losses, then inspect the damaged appearance when the game activates it.
4. Continue a damaged run to check progressive flooding and sinking. Record any floating fittings or premature mesh swaps.

Install by replacing the previous DDH181_Hyuga_SeaPower_Config folder; do not merge. No direct game installation performed. Existing Euromod dependencies remain required.
