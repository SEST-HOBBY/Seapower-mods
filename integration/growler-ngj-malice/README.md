# SEST Growler NGJ + MALICE

Additive compatibility patch for the modern EA-18G Growlers and the F/A-18F
Block III Super Hornet in this collection. It does not edit Workshop folders.

## What it changes

| Aircraft ID | Source used by the patch | Result |
|---|---|---|
| `usn_ea-18g` | U.S. Navy 2027 Capabilities (`3606774881`) | Replaces the active ALQ-99 systems and meshes with AN/ALQ-249 NGJ plus NGL-LB/ALQ-249 pod meshes; adds both MALICE fits |
| `usn_ea-18g_2020s` | F/A-18E/F (`3426791311`) | Preserves its native NGJ implementation and adds both MALICE fits |
| `usn_ea-18g_2020` | US Naval Aviation (`3737267013`) | Preserves its native NGJ implementation and adds both MALICE fits |
| `usn_fa-18f_blk3` | U.S. Navy 2027 Capabilities (`3606774881`) | Adds the four-MALICE Block III fit |

New selectable loadouts:

- **NGJ MALICE** — 2x AIM-424 MALICE, 2x AIM-120D3, 2x 610-gallon tanks, NGJ pods retained.
- **NGJ MALICE Heavy** — 4x AIM-424 MALICE, 2x AIM-120D3, 2x 610-gallon tanks, NGJ pods retained.
- **Block III MALICE** — 4x AIM-424 MALICE, 4x AIM-120D3, 2x AIM-9X, centerline tank.

The pack includes the same `sest_aim-424` definition used by the existing SEST
F-35 and F-15EX patches. US Naval Aviation supplies its AGM-88G AARGM-ER 3D
model.

## Build

From the repository root:

```powershell
py -3 .\integration\growler-ngj-malice\build_patch.py
```

The builder writes `SEST_Growler_NGJ_MALICE` from exported upstream files and
fails closed if an upstream loadout, sensor, station, or ammunition dependency
has changed.

## Install and order

Run `tools\install-sest-packs.ps1`, enable **SEST Growler NGJ + MALICE**, and
place it **above** all three dependencies in Sea Power's Mod Manager:

1. SEST Growler NGJ + MALICE
2. U.S. Navy 2027 Capabilities
3. F/A-18E/F
4. US Naval Aviation

Top of the Mod Manager list wins file conflicts.
