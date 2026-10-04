R10.40 safety fittings audit and test

Changes shared by Hyuga DDH-181 and Ise DDH-182:
- Existing flight-deck net panels used the invisible ships/materials/trans material. Restored the original new_wire.png alpha texture with the installed game's Marmoset/Transparent/Cutout/Diffuse IBL shader, retaining original UV mapping. Added reverse faces for underside visibility: 174 original front triangles plus 174 backs. Original lowered frames retained.
- Added eight shielded life-raft canisters, retaining bands and hull-mounted cradles to the starboard aft station above the boat bay. The reference row is longer; the modeled row is shortened to preserve the current model's stair landing clearance. Dimensions, spacing and canister details are photo-guided approximations, not verified equipment measurements or an exact real-ship count.
- Audited visible bow/stern deck edges, island/platform rails, side platforms and boat-bay protection in model previews. Existing railings and access openings retained. No additional fixed rails across flight paths, elevators, landing spots or VLS. Rafts below flight-deck height and outside the usable deck footprint.

References:
https://aobamil.sakura.ne.jp/shasin/hyuga/hyuga.html
https://aobamil.sakura.ne.jp/shasin/hyuga/IMG_8201.jpg (raised/lowered net mesh)
https://aobamil.sakura.ne.jp/shasin/hyuga/IMG_8314.jpg (shielded raft station)
User-supplied DDH-181-Hyuga-025.jpg (starboard aft raft-row position).

Limits: photo-based visual audit, not a complete engineering inventory. Hidden life-raft stations and every individual rail/gate/corner-frame detail cannot be confirmed from available photos. Bare support/corner frames without an existing net panel were retained where their infill could not be established. No automatic liferaft deployment or new safety-net raising animation added; nets remain in the source lowered configuration. No gameplay collision changes.

Verification: original mesh preserved as an exact text prefix; all original textures, other ship assets, crew, weapons, sensors, variants and animations preserved. New OBJ indices valid. Native shader and alpha texture verified. Bow, stern, raft close-up and starboard aft renders inspected; raft row kept aft of the stair landing and forward of the antenna gallery. Offline checks passed. In-game loading, net visibility at distance and raft placement still require the user's test.

Replace the previous DDH181_Hyuga_SeaPower_Config folder; do not merge. No direct game installation performed.
