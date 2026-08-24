# SEST Growler NGJ + MALICE

Additive compatibility patch for the modern EA-18G Growlers and the F/A-18F
Block III Super Hornet in this collection. It does not edit Workshop folders.

## What it changes

| Aircraft ID | Source used by the patch | Result |
|---|---|---|
| `usn_ea-18g` | U.S. Navy 2027 Capabilities (`3606774881`) | Replaces the active ALQ-99 systems and meshes with AN/ALQ-249 NGJ plus NGL-LB/ALQ-249 pod meshes; adds both MALICE fits |
| `usn_ea-18g_2020s` | F/A-18E/F (`3426791311`) | Preserves its native NGJ implementation and adds both MALICE fits |
| `usn_ea-18g_2020` | US Naval Aviation (`3737267013`) | Preserves its native NGJ implementation and adds both MALICE fits |
| `usn_fa-18f_blk3` | U.S. Navy 2027 Capabilities (`3606774881`) | Adds the four-MALICE Block III fit |

New selectable loadouts:

- **NGJ MALICE** — 2x AIM-424 MALICE, 2x AIM-120D3, 2x 610-gallon tanks, NGJ pods retained.
- **NGJ MALICE Heavy** — 4x AIM-424 MALICE, 2x AIM-120D3, 2x 610-gallon tanks, NGJ pods retained.
- **Block III MALICE** — 4x AIM-424 MALICE, 4x AIM-120D3, 2x AIM-9X, centerline tank.

The pack includes the same `sest_aim-424` definition used by the existing SEST
F-35 and F-15EX patches. US Naval Aviation supplies its AGM-88G AARGM-ER 3D
model.

## Build

From the repository root:

```powershell
py -3 .\integration\growler-ngj-malice\build_patch.py
```

The builder writes `SEST_Growler_NGJ_MALICE` from exported upstream files and
fails closed if an upstream loadout, sensor, station, or ammunition dependency
has changed.

## Install and order

Run `tools\install-sest-packs.ps1`, enable **SEST Growler NGJ + MALICE**, and
place it **above** all three dependencies in Sea Power's Mod Manager:

1. SEST Growler NGJ + MALICE
2. U.S. Navy 2027 Capabilities
3. F/A-18E/F
4. US Naval Aviation

Top of the Mod Manager list wins file conflicts.


## Fuel tanks: the Hornets were wearing Eagle tanks

`usn_tank_1200_f-18` is Murder Hornet's tank and it is the **vanilla F-15C tank** under a Hornet
name — `ResourcesMesh=usaf_f-15c_tank_610` out of `aircraft/usaf_f-15c/`, with `Fuel` raised from
1800 to 4500. `usaf_tank_610_f-15` is that same F-15 tank unmodified. The genuine article is
`usn_tank_610_f-18`: the `f-18_fuletank` mesh from the F/A-18E/F mod, at 1800.

Every fit in this pack now hangs `usn_tank_610_f-18` — 44 to 50 swaps per Super Hornet.

That closes the range gap that made the MALICE fit look magic:

| Fit | Tanks | External fuel |
|---|---|---|
| MH SEAD+Extra Fuel | 2× 610 (was an F-15 tank) | 3,600 |
| NGJ MALICE — before | 2× "1200" (F-15 mesh, 4500 fuel) | 9,000 |
| **NGJ MALICE — now** | 2× 610 | **3,600** |
| **NGJ Long Range — new** | 3× 610 | **5,400** |

The ~1433 nm combat radius on the MALICE fit was never the missile. It was 2.5× the fuel.

## Stores that clip the tanks

`MurderHornetSEADHeavyTanks` carried four AGM-88G, and the pair on stations 13/14 **intersects the
wing tanks** — confirmed in game. The geometry says why: those stations sit 0.0181 from the tank on
the same wing, and an AARGM-ER is long while a 610-gal tank is fat. The pair on stations 3/4 is
0.0323 away and clear.

Stations 13/14 are now cleared from that fit, leaving 2× AGM-88G + 2 tanks + 2 AMRAAM — which is
also the real Growler SEAD-with-fuel configuration.

The build reports other candidates rather than guessing at them. The filter is **distance AND
size**: at or inside the confirmed 0.0181 separation, and at least the confirmed 468 kg. Distance
alone flags about 20 stores per airframe and is useless — Murder Hornet routinely parks SDBs
(93 kg) and AMRAAM (162 kg) beside the tanks and those are fine. With both halves it flags five
loadouts per Super Hornet worth eyeballing:

| Loadout | Store | Mass | Separation |
|---|---|---|---|
| `MH_AntiShipEF` | LRASM | 1450 kg | 0.01802 |
| `MurderHornetPenetrator` | AIM-174B | 860 kg | 0.01802 |
| `MH_QCSK31EF` / `MH_GBU-31EF` | GBU-31 | 946 kg | 0.01749 |
| `MH_AGM-154EF` | JSOW | 600 kg | 0.01794 |

These are upstream's loadouts and are **not** changed — they are flagged for you to look at, since
only you can see whether they actually intersect.

## NGJ Long Range (3 tanks)

A maximum-persistence jamming fit: no anti-radiation missiles, three tanks, two AMRAAM for
self-defence. The NGJ pods do the work.

Three is the ceiling, not a choice. The Growler model carries exactly **one** pair of wing tank
pylons — the `fule_tank_point` mesh at stations 27/28 — plus the centreline. Stations 13/14 look
like outboard pylons but carry `sead_point`/`aam_point` racks, so a tank there would hang in mid-air
with nothing under it. Four wing tanks is not possible on this airframe.

The fit is added **only where a centreline station exists**. `usn_ea-18g` has Station29; the 2020
and 2020s Growlers do not, and the build skips them with a note rather than emitting a reference to
a station that isn't there.
