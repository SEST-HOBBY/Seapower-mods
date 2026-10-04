# SEST F-35C JATM

AIM-260 loadout options for the F-35C that the **Gerald R. Ford JSF air wing** flies
(`usn_cvn_ford_jsf` spawns 24× `usn_f-35c`).

## The three new loadouts

| Loadout | In-game name | Stores |
|---|---|---|
| `Intercept260` | SEST Intercept (6x AIM-260 int) | 6× AIM-260 internal (sidekick bay fit) + 2× AIM-9X wingtip — pylons stay off, signature stays clean |
| `Intercept260Beast` | SEST Intercept Beast (10x AIM-260) | 6× internal + 4× AIM-260 on wing pylons + 2× AIM-9X |
| `Malice424` | SEST Intercept MALICE (2x AIM-424 int) | 2× **AIM-424 MALICE** on the big bay stations + 2× AIM-260 on the bay door rails — full stealth |

The AIM-260 comes from the **Dingtools Weapon Pack** (`dts_aim-260` internal, `dts_aim-260_w`
external, matching dingtools' own internal/external carriage convention on the F-15EX).

## The AIM-424 MALICE

`ammunition/sest_aim-424.ini` is the Raytheon AIM-424 LRAAM, revealed by the US Navy on
22 August 2026 and already in flight test. Per the Navy fact file: a solid-propellant round
4.11 m long on the same 34.3 cm diameter as the SM-6, 680 kg (1,500 lb), blast-fragmentation
warhead, and a range **in excess of 250 nm** — modelled here at **290 nm**, just under the
AIM-174B's 316. Active-radar terminal homing with datalink midcourse plus a passive
anti-emitter mode, which is what makes it an AEW- and tanker-killer rather than just a long
AMRAAM. Bay-sized: Navy imagery shows it in the F-35C internal bay, and here it rides the same
internal stations JSM does.

The 3D model is a stand-in on US Naval Aviation's AGM-88G assets, the block proven to load;
that mod's own AIM-424 mesh is untested in this round. The seeker figures are this repo's
estimates; the Navy disclosed none. See `integration/common/aim424.py` for the source or the
reasoning behind each key.

## Why the base is F-35C Alt. Loadouts' F-35C

`aircraft/usn_f-35c.ini` is defined by two subscribed mods — **F-35C Lightning II Alt.
Loadouts** (3607989779, the richest F-35C in the collection: its own JATM, SEAD, JSOW and
AGM-158C/D fits, on the MyGo airframe) and **US Naval Aviation** (3737267013). The deprecated
MyGo standalone (3508978375) was the third until it was unsubscribed on 20 Sep 2026. Only the
highest-listed file wins, and a whole-file override replaces every loadout the player had, so
this patch is based on the Alt. Loadouts file, carries over the loadouts only USNA defines
(AirToAir, AntiShip, Ferry, CAS, Strike and the rest), and adds the three above. It also ships
USNA's 13-squadron `usn_f-35c_squadrons.ini`, trimmed to the one serial-number node the MyGo
airframe has.

Bonus fix: USNA's file declares `[WeaponSystem1AntiShip]` twice (the second copy lacks
`ReadyUpTime`); the merge carries only the first, more complete one.

## Install

1. Nothing to copy or place by hand. `tools/build_all.py` consolidates this pack into
   `SEST_Integration`, the one SEST entry in the Mod Manager, which stays first, above every
   Workshop mod (`data/load-order.tokens.txt`), and so above F-35C Alt. Loadouts and US Naval
   Aviation, whose files it replaces. On the gaming PC `tools\sync-sest.ps1` deploys it and
   writes that order; a Workshop subscriber gets it inside the SEST Integration Pack and runs
   `SETUP - double-click me.cmd` in the pack folder, with the game closed, to write the same
   order.
2. Keep Dingtools Weapon Pack (the AIM-260) installed. In today's order a store and a
   system also resolve from U.S. Navy 2027 Capabilities and one system from the MH-60R mod
   (`python3 tools/check_dependencies.py` names the winning provider of each).
3. Ford JSF variant → F-35C flights → the three SEST loadouts appear in the picker.

## Rebuilding after an upstream update

```bash
python3 integration/f-35c-jatm/build_patch.py
```

Regenerates from `mods-source/3607989779` (F-35C Alt. Loadouts), carrying over the loadouts
only `mods-source/3737267013` (US Naval Aviation) defines, and fails loudly if either upstream
changed its layout or if Alt. Loadouts claimed the loadout keys.
