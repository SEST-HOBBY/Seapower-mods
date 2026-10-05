# SEST RAAF F-35A JATM

**This pack now carries the RAAF F-35A itself.** Greene's mod (Workshop 3514484654)
was removed from the Workshop in October 2026. The pack ships the files of it that
won the load order - the aircraft, its RAAF squadrons, animations, gun pod, AIM-120C-7,
GBU-31(V)1, GBU-53, JSM and JSM land-attack, and the names only it defined - from the
last export (`mods-source/_retired/3514484654`), with every model reference moved to a
model still in the collection: US Naval Aviation's F-35C (which the RAAF mod was built
from; every part it names exists on it), JSM and GBU-53, and the GBU-31 model a live
round uses. The RAAF livery texture went with the mod, so the aircraft wears the
F-35C's default grey. Stats, loadouts, squadrons and callsigns are Greene's.

AIM-260 loadout options for Greene's **RAAF F-35A**, which ships with today's AIM-120C-7 and
already has JSM anti-ship fits — this patch adds the future air-to-air arsenal, following the
mod's own Stealth / non-Stealth loadout convention.

## The four new loadouts

| Loadout | Stores |
|---|---|
| Intercept Stealth (AIM-260) | 6× AIM-260 internal, all pylons off — clean-signature fit |
| Intercept (AIM-260) | 6× internal + 2× AIM-9X wingtip |
| Intercept Beast (10× AIM-260) | 6× internal + 4× AIM-260 on wing pylons + 2× AIM-9X |
| Intercept MALICE (2× AIM-424 int) | 2× **AIM-424 MALICE** on the big bay stations + 2× AIM-260 on the bay door rails — full stealth |

The AIM-260 comes from the **Dingtools Weapon Pack** (`dts_aim-260` internal, `dts_aim-260_w`
external); the AIM-9X is bundled with the RAAF mod itself. The AIM-424 MALICE ships inside
this pack (`ammunition/sest_aim-424.ini`, identical copy in the F-35C pack): the Raytheon
LRAAM the US Navy revealed on 22 August 2026 — 680 kg on the SM-6's 34.3 cm diameter, 290 nm
here against the Navy's stated "in excess of 250", with a passive anti-emitter mode. Keep
**US Naval Aviation** enabled: the missile renders on its AGM-88G model, the stand-in proven
to load.

## Install

1. Copy `SEST_RAAF_F-35A_JATM/` into `Sea Power_Data\StreamingAssets\`.
2. Keep US Naval Aviation and the Dingtools Weapon Pack installed. The RAAF F-35A mod itself is no longer needed (or available).

## Rebuilding after an upstream update

```bash
python3 integration/raaf-f-35a-jatm/build_patch.py
```

Regenerates from `mods-source/_retired/3514484654`, inserting the new keys ahead of the upstream
`AvailableLoadouts` line's trailing comment, and validates every ammunition reference.
