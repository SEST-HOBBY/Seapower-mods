# SEST RAAF F-35A JATM

AIM-260 loadout options for Greene's **RAAF F-35A**, which ships with today's AIM-120C-7 and
already has JSM anti-ship fits — this patch adds the future air-to-air arsenal, following the
mod's own Stealth / non-Stealth loadout convention.

## The three new loadouts

| Loadout | Stores |
|---|---|
| Intercept Stealth (AIM-260) | 6× AIM-260 internal, all pylons off — clean-signature fit |
| Intercept (AIM-260) | 6× internal + 2× AIM-9X wingtip |
| Intercept Beast (10× AIM-260) | 6× internal + 4× AIM-260 on wing pylons + 2× AIM-9X |

The AIM-260 comes from the **Dingtools Weapon Pack** (`dts_aim-260` internal, `dts_aim-260_w`
external); the AIM-9X is bundled with the RAAF mod itself.

## Install

1. Copy `SEST_RAAF_F-35A_JATM/` into `Sea Power_Data\StreamingAssets\`.
2. In the Mod Manager, place it **above** the RAAF F-35A mod. Keep Dingtools Weapon Pack installed.

## Rebuilding after an upstream update

```bash
python3 integration/raaf-f-35a-jatm/build_patch.py
```

Regenerates from `mods-source/3514484654`, inserting the new keys ahead of the upstream
`AvailableLoadouts` line's trailing comment, and validates every ammunition reference.
