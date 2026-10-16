# Workshop refresh, 17 October 2026

Capture `7fdb7be8` on `chore/workshop-refresh-20261017`: Euromod - Modern Royal
Australian Navy (3820759806), newly subscribed, plus updates to the Euromod
Italian (Modern and Cold War), Scandinavian, South Korean, British and Main
packs. Merged into `feature/workshop-update-20261017`.

## 1. Euromod - Modern Royal Australian Navy

Version 1.0.0.1, posted 16 Oct, updated 17 Oct; requires Euromod Main, US
Naval Aviation and the French Helicopter Package, all in the collection.
Ships: Hobart, Anzac (eight hulls, each with an S-70B-2 and an MH-60R variant)
and a wartime Anzac, Canberra and Adelaide (amphibious, air assault and an
LHD-CV carrier conversion), Collins, the Adelaide FFG upgrade and a
Quickmatch-class future destroyer; about twenty RAAF, RAN and Army aircraft.

Its Hobart, Anzac, Canberra and Collins use the unit ids SEST's campaigns
use. Before this change SEST RAN Fleet's stand-ins (Hobart on the Spanish
F-100, Canberra on the Juan Carlos, Collins on the S-80) and the old Anzac
mod would have hidden all four. Decision (the user, 17 Oct): SEST moves onto
the mod's ships.

- `integration/ran-fleet/build_fleet.py`: the four are patches of the mod's
  files (`"euromod": True`). Kept from SEST: the RAN MH-60R air group
  (`usn_mh-60r` Squadron20, the one the rosters sell), AircraftSupported for
  both RAN Seahawks and the mod's own (`ran_mh-60r`, `ran_S-70B-2_Seahawk`),
  the Canberra's CH-53E and MV-22B, the reload flag, and HMAS names for
  Variant1..N. Dropped as redundant on these hulls: the NSM swap, Tomahawk
  refresh, Mk41 repair, combat-system and Phalanx swaps, and the stand-ins'
  variants files (the mod's carry real hull numbers and emblems). The NSM
  guidance check now reads a loadout's own block (`[WeaponSystem7Late]`):
  Hobart 10 NSM mounts across its fits, Anzac 2, each with a sensor.
- Variant numbering matches: the mod's Variant1-8 are FFH-150..157 in the
  same order, Hobart 1-3, Canberra 1-2 and Collins 1-6 as before, so no
  mission's named ship changes.
- Load order: directly above the Anzac Class Frigate mod, so its own Anzac
  variants win; catalog entry added (205 mods).
- Name Fixes: the pin on the old Anzac mod's "Frigate Helicopter" class
  name is retired; the winning name is the mod's "Anzac-class, Anzac".

## 2. Dated fits

`pick_loadout` wrote `Default` when a mission named no fit. The mod's ships
date their fits (`LoadoutDate_<fit>=year`, the stock mechanism), and Default
is the oldest: the Anzac's carries no NSM. The builder now takes the latest
fit in service by the mission's year, ties to the first offered. Across all
SEST missions: Anzac -> AMCAP Late (59 placements), Hobart -> Late (21),
Collins -> Phase 6 Modernisation (10), Canberra -> AmphibiousAssault (its
only fit), and four others in 2028 missions -> Late (two Udaloys, an Italian
FREMM, an Adelaide short hull). The campaign gates (opening ranges, closure,
pacing, reach) pass on the new fits. Test added.

## 3. Checks

Gates 11 of 12 (`check_inventory`, the four CR-stripped mods); campaign
tests 201, tool tests 105.

Before the next upload: add Euromod - Modern Royal Australian Navy
(3820759806) to collection 3812390790 and to the SEST item's Required Items.
