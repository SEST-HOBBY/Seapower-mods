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

## 4. Second capture: Steelfin and the afternoon updates

Capture `908e1a70` on `chore/workshop-refresh-20261017b` (taken 15:35, after
the player started and quit the game once): Steelfin (3820576916), newly
subscribed, and fresh exports of the F-35C Alt. Loadouts, the Euromod
Anchorchain Expansion Pack, Main Pack, British, South Korean and RAN packs and
the PLAAF Aircraft Pack. U.S. Navy 2027 Capabilities (3606774881) is unchanged
in the export: Steam still dates it 10 Oct, so whatever update the Workshop
showed had not touched its config files.

- **Steelfin** (19 files, no DLL, no dependencies). The Anduril interceptor
  as its own mod: the ship round `usn_steelfin`, the air-launched
  `usn_steelfin_air`, a Steelfin cruiser (`usn_cg_steelfin`, a copy of the
  vanilla Bunker Hill with Steelfin in every Mk 41 magazine, in service
  2027-2100), a land container launcher with its own radar
  (`usa_steelfin_launcher`), its weapon and radar systems and a test
  scenario. The two rounds were already shipped by five mods (Saronic
  Corsair and Anduril Maritime Drones the ship round; YF-23, FQ-44 Fury and
  MV-75 the air round); this mod's copies differ from theirs only in the
  three camera distances, and its material file is byte-identical. Placed
  directly above Saronic Corsair ASV so its own copies win; catalogued (206
  mods); `check_mod_conflicts` finds nothing SEST fields. No SEST mission
  places its units, so the campaign coverage rule carries a written excuse
  for it, as for Anduril Maritime Drones. The world campaign's buy list
  does not take the Steelfin cruiser: its unit and variants files are
  `#!copy` overlays of the Bunker Hill, which the arsenal reader does not
  follow, so it finds no unit type or nation in them.
- **Steelfin loadout name.** SEST Collection Fixes named the YF-23, Fury and
  MV-75 "Steelfin" fit "Steelfin (air-defence interceptor)" on 16 Oct,
  because no mod named it. The Steelfin mod now names it "Steelfin". The
  entry stays (none of the three aircraft mods requires the Steelfin mod, so
  without it the picker would read MISSING TEXT) but now carries the
  author's text, "Steelfin".
- **F-35C Alt. Loadouts** (3607989779). Only rounds changed: AIM-120D-3 and
  AIM-260A get more drag and a terminal loft, the GBU-31(V)4 an impact fuze,
  a very large impact and an 8 m error radius, and the three JDAMs gain
  frontal and side areas. This mod outranks the F-22 and US Naval Aviation
  copies, so these are the rounds the collection flies. Its `usn_f-35c.ini`
  is unchanged, so SEST F-35C JATM (built on it) rebuilds identical.
- **Euromod - Modern Royal Australian Navy** (v1.0.0.2). The Hobart's EOST
  material folder is corrected and the LHD-CV Canberra's deck ammunition
  rises from 55,000 to 135,000 points. SEST RAN Fleet's Hobart picks up the
  fix on rebuild; the Canberra SEST sails is the amphibious hull, which did
  not change.
- **Euromod - South Korea Navy.** The Marado (LPH-6112) is now its own unit,
  `ko_lph-6112`, instead of Variant2 of the Dokdo (`ko_lph-6111`); the ROK
  MH-60R gets a name and a corrected material path, and the Dokdo's sensor
  fit is rewritten (12 sensors, was 8). SEST's world campaign places one
  `ko_lph-6111`, which keeps its Variant1 (Dokdo); its buy list takes the
  Marado on rebuild (tier 2, South Korea's 16th ship type), and SEST
  Replenishment ships the reload flag for both hulls.
- **Euromod - Main Pack and British Navy.** The Main Pack now ships the
  Starstreak (`rn_starstreak`) and an air-launched copy (`rn_starstreak_air`);
  neither was in the previous export, so the British pack's Army Air Corps
  Apache (`raac_ah_mk_1`) had named a round nothing defined. It now carries
  the air copy. SEST does not field that Apache.
- **PLAAF Aircraft Pack.** Missile retunes (the PL-15 and PL-15S to 125 NM
  from 108, the PL-17 to 320 NM from 250, shorter seeker and terminal ranges
  on these and the PL-12/12A) that do not reach the game: those five files
  are shipped by mods placed higher (the PLA & PLAN & PLAAF AEP at position
  4 wins the PL-15, PL-15S and PL-17; 3436170138 the PL-12 and PL-12A), and
  the PLAAF pack sits at position 187. What does reach the game is the
  `Volume=` it adds to the Kh-29TE, PL-2, PL-5B and its bomb racks, which
  only it ships.
- **Euromod - Anchorchain Expansion Pack.** Hull Damage (a new plugin), new
  kinetic-kill and high-speed warhead effects with matching ammunition
  overlays, retuned rocket smoke, and three experimental "worker" plugins
  (CombatWorker 0.2.0, ParallelRangeProbe 0.12.0, UiWorkerProbe 0.2.0). Their
  README says they have not been tested in game. In this session's log
  CombatWorker switched itself off at start ("Conflicting hook:
  io.github.yourname.second-thrust"), because the PLA & PLAN & PLAAF AEP's
  SecondThrustMod hooks the same thrust method; the game runs on its own
  code for that, which is harmless. The other two started. If the game
  stutters or stalls after this update, these two are the first suspects.
  Their README gives a per-session off switch (`off` written to
  `Mods\<name>\live\mode.request` under the game's LocalLow folder) and
  CombatWorker an `Enabled=` line in its settings.ini; the other two follow
  the AC Pack's own checkbox.

The SEST plugin in the log is still the Workshop copy of 16 Oct (31,232
bytes); 1.2.2 reaches the PC with the next sync.

Checks: gates 11 of 12 (`check_inventory`, the four CR-stripped mods, as
before); campaign tests 201, tool tests 105. `check_mod_conflicts 3820576916`:
two whole-file collisions (the Steelfin rounds), none with anything SEST
fields.

Before the next upload, add to collection 3812390790: Euromod - Modern Royal
Australian Navy (3820759806, also a Required Item of the SEST item, since
SEST RAN Fleet patches its ships) and Steelfin (3820576916). SETUP now checks
for Steelfin, as for every mod in LOAD-ORDER.txt, but no SEST file needs it,
so it belongs in the collection rather than the Required Items.
