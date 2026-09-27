# Trident I C4 and Mk 4 — fictional game variant

This is a deliberately fictional balance preset. Names identify the game variants; numerical settings are not historical performance, propulsion, deployment or nuclear-yield data.

## Files and use

- `ammunition/usn_ugm-96a.ini`: independent C4 ammunition definition based on the D5 configuration.
- `ammunition/usn_trident_c4.ini`: alias for the same C4 ammunition.
- `ammunition_overwrite/usn_ugm-96a_OVWR.ini`: stage motors, D5 visual assets, launch control and four RV mounts. Applies to the C4 names only.
- `ammunition/usn_w76_mk4.ini`: independent Mk4 daughter definition, using the existing Mk5 body and glow overlay.

Use `usn_ugm-96a` or `usn_trident_c4` in a launcher ammunition entry. No existing ship, launcher or scenario is reassigned. Keep AC Pack and its Euromod asset dependency enabled. Requires the installed MultiStageMissiles 1.5.1 and MissileControlMod 0.1.14 or compatible successors.

## Game settings

Configured launch-range bounds: 200–1600 nautical miles. `MaxVelocity=11000` knots is a native reference value, not a hard speed cap when ApplyKinematics is enabled. These settings do not prove that every allowed range is reachable; native prediction and gameplay flight still need checking.

| Visual stage | BurnTime (s) | Acceleration (game G) | Separation time (s) |
|---|---:|---:|---:|
| 1 | 40 | 2.5 | 46 |
| 2 | 15 | 3.5 | 61 |
| 3 | 25 | 3.5 | 88 |
| 4 | 30 | 3.0 | 120 |
| 5 | 0 | 0 | Final carrier |

All BurnTimeDelay values are zero. For submerged launches, numerical separation times use the launch controller's water-exit clock; each motor's BurnTime starts when its stage can burn. Separation can truncate a burn. Stage 1 includes clearance time before its first separation. Stage 2 and 3 represent one motor split by the nose-fairing jettison. The aerospike animation begins 5 seconds into Stage 1 and lasts 0.8 seconds. Exhaust-vector visuals cover both phases of motor 2.

Four rounds occupy alternate existing D5 mounts (1/3/5/7). All use the same game ejection setting. Mk4 has a game damage score of 25000, no thrust and the inherited 500 m random aimpoint ring. Impact positions retain native navigation error. It uses the corrected Mk5 nuclear visual mappings, including the air-destruction slot, and the same glow material/mask. The visual effect does not define damage or explosive yield. The carrier itself has Power=0 and no impact effects.

The full D5-size carrier and Mk5-size RV meshes remain placeholders. Launch, staging and flight are not claimed as in-game verified. Restart the game before using the new ammunition and test a fresh launch.
