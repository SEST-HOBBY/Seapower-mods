# SEST RAN Fleet

The Royal Australian Navy, cloned from its real European design donors in the Euromod packs.
This is the honest way to build the RAN from this collection — most of its ships literally
*are* European designs. Every clone is a **new unit id**: the Spanish/British donors are
untouched and both fleets coexist in the editor.

## The fleet — 7 classes, 26 named hulls

| Class | Donor hull | Hulls | Air group |
|---|---|---|---|
| **Hobart-class DDG** | F-100 Álvaro de Bazán (the actual parent design) | Hobart · Brisbane · Sydney | 1× MH-60R |
| **Anzac-class FFH** *(stand-in)* | Type 23 MLU (no MEKO 200 in the collection) | Anzac · Arunta · Warramunga · Stuart · Parramatta · Ballarat · Toowoomba · Perth | 1× MH-60R |
| **Canberra-class LHD** | Juan Carlos I (the actual parent design) | Canberra · Adelaide | 4× MH-60R + 4× S-70B-2 (no fixed-wing — RAN LHDs fly helicopters only) |
| **HMAS Choules LSD** *(stand-in)* | Galicia LPD | Choules | 2× MH-60R |
| **Supply-class AOR** *(stand-in)* | Teide-class oiler (Cold War Spanish pack) | Supply · Stalwart | — |
| **Collins-class SSG** *(stand-in)* | S-80 Plus | Collins · Farncomb · Waller · Dechaineux · Sheean · Rankin | — |
| **Arafura-class OPV** *(stand-in)* | Meteoro-class BAM | Arafura · Eyre · Pilbara · Gippsland | — |

All units are `Nation=Australia` with the Australian ensign and transparent hull numbers
(the donors' Spanish/British pennant textures are not reused). Frigate/destroyer/LHD
`AircraftSupported` lists are extended so MH-60R and S-70B-2 can cross-deck anywhere in
the fleet.

## Dependencies

Euromod Main Pack · Spanish Navy Mod (Modern) · Spanish Navy Mod (Cold War — Teide donor) ·
Modern British Navy (Type 23 donor) · an MH-60R source (US Naval Aviation) · S-70B-2 Seahawk
(Pog Frog). Clones reference donor meshes/systems cross-mod, so the donor packs must stay
installed and enabled.

## Install

1. Copy `SEST_RAN_Fleet/` into `Sea Power_Data\StreamingAssets\`.
2. Place it **below** the Euromod packs in the Mod Manager (it only adds new units, so
   ordering is forgiving).
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
