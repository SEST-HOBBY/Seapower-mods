# Collection cleanup

Generated from your actual data, not guesswork: every unit type referenced by your four missions,
every aircraft in the SEST RAAF Bases and RAN Fleet air groups, and every ammunition id in every
SEST loadout, resolved through `data/load-order.tokens.txt` to whichever mod actually **wins** the
file.

**137 entries in the load order. 68 workshop mods are required. The rest are listed below.**

Your stated keepers are all safe — and note every one of them is currently won by a SEST pack,
which overrides the base mod rather than replacing it, so the base mods must stay:

| You fly | Won by | Base mod that must stay |
|---|---|---|
| E/A-18G Growler (2020s) | `SEST_Growler_NGJ_MALICE` | F/A-18E/F (3426791311) |
| E/A-18G Growler (2020) | `SEST_Growler_NGJ_MALICE` | US Naval Aviation (3737267013) |
| Super Hornets E / F / F Blk III | `SEST_Growler_NGJ_MALICE` | U.S. Navy 2027 (3606774881) |
| F-35C | `SEST_F-35C_JATM` | F-35C Alt. Loadouts (3607989779) |
| F-35A (RAAF) | `SEST_RAAF_F-35A_JATM` | RAAF F-35A (3514484654) |
| Zumwalt (CPS) | `SEST_Zumwalt_CPS` | Modern US Navy + Euromod |

## Keep despite looking unused

- **Mogami-class frigate** (`3456859157`) — **SEST JMSDF Mogami is built from it** - integration/jmsdf-mogami/build_patch.py reads this mod. Dropping it breaks that pack.
- **J-20A** (`3591563716`) — unused *today* only because you deleted the Eastern Sweep formation. add_red_air_group.py can restore it and needs plaaf_j-20a.

## Unsubscribe candidates

### Carrier patches for carriers you don't field

| Mod | Workshop id | Why |
|---|---|---|
| Flight Deck Ops | `3373960386` | patches America / Forrestal / Kitty Hawk. Your missions fly the Ford, Varyag and Type 004. |
| Air Deck Operations Upgrade - Nimitz (2000s) | `3461091581` | patches the Nimitz. Not in any mission. |
| Nimitz Expanded | `3432592449` | same. |
| PLAN Type 001 Liaoning | `3774859959` | your PLAN carrier is plan_cvn_004. |
| Type003 CV-18 Fujian | `3663564190` | same. |

### Legacy US air you don't fly

| Mod | Workshop id | Why |
|---|---|---|
| F-117 | `3448845252` | nothing you reference |
| A-10 | `3414146266` | usa_a-10c is won by the A-10C mod; this one loses. |
| F-16C Fighting Falcon | `3758320372` | loses its 3 shared ids to Navy 2027 and F/A-18E/F. |
| MIG-29A & F-16A | `3416372890` | nothing you reference |
| VH-3D Marine One | `3478767194` | nothing you reference |
| KC-135 Stratotanker | `3722749887` | usaf_kc-135a is VANILLA - the mod loses. |
| B-52G with AGM-86 | `3394781441` | you fly the dingtools B-52H. |
| Virginia / Seawolf / Ohio subs | `3433957933` | Modern US Navy supplies the subs you use. |

### Russian legacy air

| Mod | Workshop id | Why |
|---|---|---|
| MIG-29 Family | `3417446309` | nothing you reference |
| Mig-35 | `3659742367` | nothing you reference |
| Mi-24 Hind | `3513571010` | nothing you reference |
| Mi-8EW | `3458148344` | nothing you reference |
| Mi-8T/TV | `3465256032` | nothing you reference |
| Su-25 Frogfoot | `3451166840` | nothing you reference |
| Su-30SM2 | `3762023575` | nothing you reference |
| Su-57 | `3503594612` | nothing you reference |
| Tu-160 | `3509329205` | nothing you reference |
| Tu-16N tanker | `3673908868` | nothing you reference |
| Tu-214R Family | `3780118683` | nothing you reference |
| Tu-95K-22 | `3411341227` | nothing you reference |
| Tu-95MS (X-101) | `3715323261` | you use the AS-15 Tu-95MS instead. |
| IL-78 tanker | `3717610332` | nothing you reference |
| Beriev A-50 / Il-76 | `3524112296` | nothing you reference |
| MORE SU24M VARIANTS | `3716049886` | nothing you reference |
| P-750 Meteorit-A | `3587091564` | nothing you reference |

### PLA legacy air and ground

| Mod | Workshop id | Why |
|---|---|---|
| PLAAF J-11 | `3436170138` | nothing you reference |
| PLAAF J-11BS | `3729578404` | nothing you reference |
| PLAAF J-8 | `3433577445` | nothing you reference |
| PLAAF Su-27UBK | `3729579342` | nothing you reference |
| J10C | `3481228992` | nothing you reference |
| Y-20 / KJ-3000 | `3782020901` | nothing you reference |
| PLA Z-21 | `3774746803` | nothing you reference |
| Ka-27RLD / Ka-31 | `3776340577` | nothing you reference |
| KJ-500 | `3637954857` | PLAN Pack wins plaaf_kj-500; this one loses. |
| Modern Chinese Airbase | `3631042692` | nothing you reference |
| Modern Russian Airbase | `3629269283` | nothing you reference |

### European navies and air you don't field

| Mod | Workshop id | Why |
|---|---|---|
| Italian Navy mod | `3505420313` | loses its 2 shared ids. |
| Modern Italian Navy - Euromod | `3488139470` | nothing you reference |
| Spanish Navy (Cold War) | `3630495619` | nothing you reference |
| Type 23 Frigate | `3378409795` | [OLD], own unit ids. |
| Westland Lynx HAS.3 | `3373356293` | [OLD]. |
| Sea Lynx | `3455931957` | nothing you reference |
| Eurofighter Typhoon | `3587877691` | nothing you reference |
| French army vehicles | `3736147136` | nothing you reference |
| French Helicopter Package | `3567228449` | nothing you reference |

### Misc

| Mod | Workshop id | Why |
|---|---|---|
| Humpback Whale | `3384079999` | bio_humpback_whale is VANILLA - the mod adds nothing you use. |
| Buildings and Objectives | `3600788156` | nothing you reference |
| Pickup | `3681873198` | nothing you reference |
| SEJJIL ballistic missiles | `3551676319` | you use SCUD-B and Iskander. |
| JGSDF Type 12 SSM | `3470643173` | nothing you reference |
| MH-60R | `3590477166` | Navy 2027 wins usn_mh-60r. |


**56 mods.** Each supplies nothing your missions, bases or loadouts reference, and nothing depends on it.

## How to do it safely

1. Unsubscribe in Steam, a group at a time — not all at once.
2. Re-run the tooling, which will tell you immediately if something broke:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1
powershell -ExecutionPolicy Bypass -File .\tools\show-load-order.ps1 -DiffOnly
```

   `show-load-order` reports canonical entries the game no longer has, so anything you removed by
   accident shows up by name.
3. Rebuild the packs. Every builder validates its references and **fails loudly** rather than
   emitting something broken, so a missing dependency surfaces here rather than in game:

```bash
for b in integration/*/build_patch.py integration/*/build_pack.py; do python3 "$b"; done
```

4. Prune `data/load-order.tokens.txt` of the removed ids and re-run `set-mod-order.ps1`.

## What this does NOT tell you

Only that nothing you currently field uses these. If you build a mission with a MiG-29 or a Nimitz
later, you will want that mod back. This is a list of what is inert for *your* current content, not
a judgement on the mods.
