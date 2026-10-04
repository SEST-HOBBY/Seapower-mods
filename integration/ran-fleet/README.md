# SEST RAN Fleet

The Royal Australian Navy, cloned from its real European design donors in the Euromod packs.
This is the honest way to build the RAN from this collection — most of its ships literally
*are* European designs. Every clone is a **new unit id**: the Spanish donors are untouched
and both fleets coexist in the editor. The Anzac is the exception: since 20 Sep 2026 the
collection has the real ship (Anzac Class Frigate, 3440622312), so that entry patches the
mod's own `ran_ffh_anzac` in place rather than cloning a stand-in.

## The fleet — 7 classes, 26 named hulls

| Class | Donor hull | Hulls | Air group |
|---|---|---|---|
| **Hobart-class DDG** | F-100 Álvaro de Bazán (the actual parent design) | Hobart · Brisbane · Sydney | 1× MH-60R |
| **Anzac-class FFH** | none: the Anzac Class Frigate mod's own ASMD hull, patched in place | Anzac · Arunta · Warramunga · Stuart · Parramatta · Ballarat · Toowoomba · Perth | 1× MH-60R |
| **Canberra-class LHD** | Juan Carlos I (the actual parent design) | Canberra · Adelaide | 4× MH-60R + 4× S-70B-2 (no fixed-wing — RAN LHDs fly helicopters only) |
| **HMAS Choules LSD** *(stand-in)* | Galicia LPD | Choules | 2× MH-60R |
| **Supply-class AOR** *(stand-in)* | Teide-class oiler (Cold War Spanish pack) | Supply · Stalwart | — |
| **Collins-class SSG** *(stand-in)* | S-80 Plus | Collins · Farncomb · Waller · Dechaineux · Sheean · Rankin | — |
| **Arafura-class OPV** *(stand-in)* | Meteoro-class BAM | Arafura · Eyre · Pilbara · Gippsland | — |

All units are `Nation=Australia` with the Australian ensign. The clones carry transparent
hull numbers (the Spanish donors' pennant textures are not reused); the Anzac keeps its
mod's own FFH 150-157 hull numbers and emblems. Frigate/destroyer/LHD
`AircraftSupported` lists are extended so MH-60R and S-70B-2 can cross-deck anywhere in
the fleet.

Replenishment at sea: HMAS Supply and Stalwart carry a working supply system (half a mile,
12 kn for the oiler and 16 for the receiver, nothing dearer than 8000 points, so NSM,
Tomahawk, SM-6 and torpedoes pass), and every hull's magazine-less launchers carry
`ReloadableWithoutMagazine=True` so a supplier can refill them. Both come from
`integration/common/ras.py`, the table SEST Replenishment At Sea uses for the hulls it owns;
this pack applies them because it ships these files.

## Dependencies

Euromod Main Pack · Spanish Navy Mod (Modern) · Spanish Navy Mod (Cold War — Teide donor) ·
Anzac Class Frigate (3440622312, the hull the Anzac entry patches; tagged deprecated on the
Workshop and kept on purpose as the only Anzac) · an MH-60R source (U.S. Navy 2027
Capabilities, whose copy outranks US Naval Aviation's and the MH-60R mod's) · S-70B-2
Seahawk (Pog Frog, 3403661005; also tagged deprecated and kept as the only source). Clones
reference donor meshes/systems cross-mod, so the donor packs must stay installed and
enabled. Modern British Navy is no longer a donor here: the Anzac was its only customer.

`python3 tools/check_dependencies.py` derives the list from the files, meshes apart. It also
credits Euromod Anchorchain Expansion Pack, whose weapon-effect and sonar-audio mapping files
carry sections named after the Hobart's Mk41 and DE1160 sonar (the systems themselves are
defined by Euromod Main and the Spanish packs), and Charles De Gaulle & Modern French Navy,
which outranks Spanish Navy Mod (Modern) for the SIMBAD definition the Arafura names.

## Install

1. Nothing to copy or place by hand. `tools/build_all.py` consolidates this pack into
   `SEST_Integration`, the one SEST entry in the Mod Manager, which stays first, above every
   Workshop mod (`data/load-order.tokens.txt`). On the gaming PC `tools\sync-sest.ps1`
   deploys it and writes that order; a Workshop subscriber gets it inside the SEST
   Integration Pack and runs `SETUP - double-click me.cmd` in the pack folder, with the game
   closed, to write the same order.
2. The pack is not purely additive: its Anzac entry is a patched copy of the Anzac Class
   Frigate mod's `ran_ffh_anzac.ini`, so it has to outrank that mod, which the consolidated
   pack's place at the top does.
3. The RAN appears under Australia in the mission editor's vessel list.

## First-flight checks

- The Australian ensign relies on the game's `flag_australia` texture (referenced by vanilla
  UI config). If ships show a blank flag, tell me and I'll point the variants at whatever
  flag texture your build ships.
- Not modeled: Hunter-class FFG (no Type 26 in the collection — the Modern British pack
  stops at Type 23/45) and MRH90 troop lift on the LHDs. Both are easy additions if a donor
  appears.

## Rebuilding

```bash
python3 integration/ran-fleet/build_fleet.py
```

Validates donor files and helicopter ids against `mods-source/` before emitting.
