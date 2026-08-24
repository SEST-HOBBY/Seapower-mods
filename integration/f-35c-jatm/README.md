# SEST F-35C JATM

AIM-260 loadout options for the F-35C that the **Gerald R. Ford JSF air wing** flies
(`usn_cvn_ford_jsf` spawns 24× `usn_f-35c`).

## The three new loadouts

| Loadout | In-game name | Stores |
|---|---|---|
| `Intercept260` | Intercept (AIM-260, stealth) | 6× AIM-260 internal (sidekick bay fit) + 2× AIM-9X wingtip — pylons stay off, signature stays clean |
| `Intercept260Beast` | Intercept Beast (10× AIM-260) | 6× internal + 4× AIM-260 on wing pylons + 2× AIM-9X |
| `Malice424` | Intercept MALICE (2× AIM-424 int) | 2× **AIM-424 MALICE** on the big bay stations + 2× AIM-260 on the bay door rails — full stealth |

The AIM-260 comes from the **Dingtools Weapon Pack** (`dts_aim-260` internal, `dts_aim-260_w`
external, matching dingtools' own internal/external carriage convention on the F-15EX).

## The AIM-424 MALICE

`ammunition/sest_aim-424.ini` is a what-if very-long-range AAM this pack ships itself: the
AGM-88G AARGM-ER airframe (3D model provided by US Naval Aviation's own AGM-88G assets)
with AIM-174B-class flight and seeker behaviour (active-radar terminal, datalink midcourse,
120 nm reach) plus a passive anti-emitter mode inherited from its AARGM DNA — good against
AEW aircraft and jammers. Bay-sized: it rides the same internal stations JSM does.

## Why the base is US Naval Aviation's F-35C

`aircraft/usn_f-35c.ini` is defined by THREE subscribed mods — the deprecated MyGo standalone,
F-35C Alt. Loadouts (which has its own JATM fits but is built on the deprecated airframe), and
**US Naval Aviation** (the maintained one). Only the highest-listed file wins. This patch is a
fourth override based on USNA's file, so the Ford's wing gets the maintained airframe *and*
JATM options.

Bonus fix: USNA's file declares `[WeaponSystem1AntiShip]` twice (exact duplicate); the patch
removes the second copy.

## Install

1. Copy `SEST_F-35C_JATM/` into `Sea Power_Data\StreamingAssets\`.
2. In the Mod Manager, place it **above** US Naval Aviation, F-35C Alt. Loadouts, the
   deprecated MyGo F-35C, and Modern US Navy. Keep Dingtools Weapon Pack installed.
3. Ford JSF variant → F-35C flights → the two Intercept loadouts appear in the picker.

## Rebuilding after an upstream update

```bash
python3 integration/f-35c-jatm/build_patch.py
```

Regenerates from `mods-source/3737267013` and fails loudly if upstream changed its layout,
already took the AntiShip fix, or claimed the loadout keys.
