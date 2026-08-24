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


## Fuel tanks: the mesh is coupled to the station geometry

`usn_tank_1200_f-18` is Murder Hornet's tank and its mesh really is the vanilla **F-15C** tank
(`ResourcesMesh=usaf_f-15c_tank_610` from `aircraft/usaf_f-15c/`) with `Fuel` raised 1800 → 4500.
The genuine Hornet article is `usn_tank_610_f-18`, the `f-18_fuletank` mesh from the F/A-18E/F mod.

Swapping every fit to the genuine one **was tried and reverted.** The tanks hung visibly low and
detached under the wing, because `f-18_fuletank` is a mesh pulled out of `fa-18e.obj` — a
whole-aircraft root — so its origin is wherever the tank sits on *that* model, while Murder Hornet
tuned stations 27/28 around the F-15C tank's origin instead. **The station positions and the tank
mesh are one unit; changing either alone breaks the fit.**

Which tank is correct is therefore a property of the airframe, not a global preference, and the
SEST fits now copy whatever the airframe already flies:

| Airframe | Wing tank | Why |
|---|---|---|
| `usn_ea-18g` | `usaf_tank_610_f-15` | its own fits use it |
| `usn_ea-18g_2020` / `_2020s` | `usn_tank_610_f-18` | theirs use it |
| `usn_fa-18e/f/f_blk3` | `usn_tank_1200_f-18` | theirs use it |

What *was* genuinely wrong is the fuel, and that needs no geometry change. The pack ships an
override of `ammunition/usn_tank_1200_f-18.ini` — byte-identical mesh block, `Fuel` back to **1800**
— so every tank across all six airframes now carries the same 1800 the vanilla F-15 tank and the
real Hornet tank both use. That closes the range gap without moving anything: NGJ MALICE showed
~1433 nm against the SEAD fits' ~860 purely because 4500 is 2.5× 1800.

## The pylon convention

One rule for where things hang on the Growler, matching both the real EA-18G and this model:

| Pylon | \|x\| | Carries |
|---|---|---|
| centreline | 0 | fuel |
| fuselage | < 0.025 | AIM-120D3 |
| **inboard wing** | ~0.033 | **fuel** |
| **mid wing** | ~0.048–0.055 | **NGJ pods — kept clear of stores** |
| **outboard wing** | 0.0629 | **AGM-88G / AIM-424 / AIM-260 / fuel** |
| wingtip | 0.0947 | (unused) |

The mid-wing rule is the one that matters. `ALQ-249` and `NGL-LB` are baked into the airframe at
that pylon and **cannot be moved from the ini** — they are submodels with no `Position` key. So
anything hung there intersects them. That is what the AGM-88G pair on stations 13/14 was doing; it
was never the fuel tanks, which sit a whole pylon further inboard.

**Consequence: the outboard pylon is a single pair, stations 3 and 4.** Under this convention a
Growler carries **two** heavy weapons, not four or six. The four- and six-AGM fits cannot exist as
such, so they are re-cut to differ by fuel instead of by weapon count:

| Fit | Outboard | Fuselage | Inboard | Centreline |
|---|---|---|---|---|
| `MurderHornetSEADHeavy` | 2× AGM-88G | 2× AMRAAM | — | — |
| `MurderHornetSEADHeavyTanks` | 2× AGM-88G | 2× AMRAAM | 2× tank | — |
| `MurderHornetLightsOut` | 2× AGM-88G | 2× AMRAAM | 2× tank | tank |
| `SEST_MaliceNGJ` | 2× AIM-424 | 2× AMRAAM | 2× tank | — |
| `SEST_NGJLongRange` | — | 2× AMRAAM | 2× tank | tank |

The build **fails** if any Growler loadout puts a store on the mid-wing pylon. The 2020 and 2020s
Growlers already complied and were not touched.

## Other stores near the tanks

The build also reports stores that sit as close to a fuel tank as the confirmed AGM-88G case
**and** are at least as heavy (0.0181 separation, 468 kg). Both halves matter — distance alone
flags about 20 per airframe, because SDBs (93 kg) and AMRAAM (162 kg) sit beside tanks routinely
and are fine. On the Super Hornets it names LRASM, AIM-174B, GBU-31 and JSOW fits. Those are
upstream's and are **not** changed — they are flagged for a human to look at.

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
