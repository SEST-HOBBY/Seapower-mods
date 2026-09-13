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

`ammunition/sest_aim-424.ini` is the Raytheon AIM-424 LRAAM, revealed by the US Navy on
22 August 2026 and already in flight test. Two-stage solid-propellant, 4.11 m on the same
34.3 cm body as the SM-6, blast-fragmentation warhead, and a Navy-stated range **in excess
of 250 nm** — modelled here at **290 nm**, just under the AIM-174B's 316. Active-radar
terminal homing with datalink midcourse plus a passive anti-emitter mode, which is what
makes it an AEW- and tanker-killer rather than just a long AMRAAM. Bay-sized: the Navy has
confirmed it fits the F-35 internal bay, and here it rides the same internal stations JSM
does.

The 3D model is a stand-in — no AIM-424 mesh exists, so it renders on US Naval Aviation's
AGM-88G assets. Mass and seeker figures are this repo's estimates; the Navy disclosed
neither. See `integration/common/aim424.py` for the reasoning behind each.

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
