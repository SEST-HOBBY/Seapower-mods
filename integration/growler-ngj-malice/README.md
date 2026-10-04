# SEST Growler NGJ + MALICE

Compatibility patch for the modern EA-18G Growlers and the F/A-18E/F Super
Hornets in this collection. It does not edit Workshop folders.

## What it changes

| Aircraft ID | Source used by the patch | Result |
|---|---|---|
| `usn_ea-18g` | U.S. Navy 2027 Capabilities (`3606774881`) | Replaces the active ALQ-99 systems and meshes with AN/ALQ-249 NGJ plus NGL-LB/ALQ-249 pod meshes; adds the NGJ MALICE fit |
| `usn_ea-18g_2020` | US Naval Aviation (`3737267013`) | Preserves its native NGJ implementation and adds the NGJ MALICE fit |
| `usn_fa-18f_blk3` | U.S. Navy 2027 Capabilities (`3606774881`) | Adds the four-MALICE Block III fit |
| `usn_fa-18f`, `usn_fa-18e` | U.S. Navy 2027 Capabilities (`3606774881`) | Adds the same Block III fit (same APG-79 radar class and station layout) |

`usn_ea-18g_2020s` is no longer patched: its only provider, F/A-18E/F (`3426791311`), was
unsubscribed on 20 Sep 2026, and the id left the collection with it.

New selectable loadouts:

- **NGJ MALICE** — 2x AIM-424 MALICE, 2x AIM-260, 2x 610-gallon tanks, NGJ pods retained.
- **Block III MALICE** — 4x AIM-424 MALICE, 2x AIM-120D3, 2x AIM-260, 2x AIM-9X, centerline tank.
- **SEAD120D** (`SEST_SEAD120D`, `usn_ea-18g` only) — the conventional EW/SEAD fit:
  2x AGM-88G outboard, 2x AIM-120D (`usn_aim-120d-3`, the round U.S. Navy 2027 hangs
  on stations 11/12), 2x wing tanks, NGJ pods retained. No AIM-260, no AIM-424. The
  pylon convention below puts the AIM-260 on 11/12 of every fit it re-cuts, so
  before this fit the 2027 Growler had nothing a campaign keeping JATM out of its
  2028 core could fly. It is `MurderHornetLightsOut`'s re-cut seats with the
  AIM-260 swapped back, derived from the same plan in the builder, and it is
  appended last so the airframe's default fit does not move. `usn_ea-18g_2020`
  does not need it: its own `SEAD` fit already hangs the AIM-120D.

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

This pack has no Mod Manager entry of its own. `tools/build_all.py` consolidates it into
`SEST_Integration`, the one SEST entry, which stays first, above every Workshop mod
(`data/load-order.tokens.txt`). On the gaming PC `tools\sync-sest.ps1` deploys it and
writes that order; a Workshop subscriber gets it inside the SEST Integration Pack and runs
`SETUP - double-click me.cmd` in the pack folder, with the game closed, to write the same
order. Top of the Mod Manager list wins file conflicts, and this pack replaces files that
U.S. Navy 2027 Capabilities, US Naval Aviation, Murder Hornet with AIM-174B and Red Storm
Arsenal also ship. In today's order its stores and systems resolve from the first two of
those and from F-35C Lightning II Alt. Loadouts, the Dingtools Weapon Pack, the Italian Navy
mod and Custom Loadout Editor (`python3 tools/check_dependencies.py` names the winning
provider of each).


## Fuel tanks: the mesh is coupled to the station geometry

Superseded in part (see TANK MESH HISTORY in `build_patch.py`): `f-18_fuletank` rides low at
any station, because its origin comes from a whole-aircraft root, so the pack now also
overrides `ammunition/usn_tank_610_f-18.ini` to render the F-15C 610 tank mesh. Tank ids still
never swap, and `Fuel` stays 1800. In today's sources all five airframes' own fits hang
`usn_tank_610_f-18`, so that is the id the SEST fits copy. The coupling argument and the table
below are the record of round 1; the fuel fix after them still stands.

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
| `usn_ea-18g_2020` | `usn_tank_610_f-18` | its own fits use it |
| `usn_fa-18e/f/f_blk3` | `usn_tank_1200_f-18` | theirs use it |

What *was* genuinely wrong is the fuel, and that needs no geometry change. The pack ships an
override of `ammunition/usn_tank_1200_f-18.ini` — byte-identical mesh block, `Fuel` back to **1800**
— so every tank across all five airframes now carries the same 1800 the vanilla F-15 tank and the
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

| Fit (`usn_ea-18g`) | Outboard | Fuselage | Inboard | Centreline |
|---|---|---|---|---|
| `MurderHornetSEADHeavy` | 2× AGM-88G | 2× AIM-260 | 2× tank | EW |
| `MurderHornetSEADHeavyTanks` | 2× AGM-88G | 2× AIM-260 | 2× tank | EW |
| `MurderHornetLightsOut` | 2× AGM-88G | 2× AIM-260 | 2× tank | EW |
| `SEST_MaliceNGJ` | 2× AIM-424 | 2× AIM-260 | 2× tank | EW |
| `SEST_NGJLongRange` | 2× AIM-260 | 2× AIM-260 | 2× tank | EW |
| `SEST_SEAD120D` | 2× AGM-88G | 2× AIM-120D | 2× tank | EW |

The build **fails** if any Growler loadout puts a store on the mid-wing pylon.

**Every Growler fit flies full** (26 September): both wing tanks inboard, the outboard pair filled,
and the tank pylon never hidden under a tank. `MurderHornetSEADHeavy` used to be the clean,
no-fuel fit, and as the airframe's first fit it is what a Growler parked on an airbase launches
with, so an RAAF Growler in a Tasman mission flew with bare inboard pylons. `SEST_NGJLongRange`
used to leave the outboard pair empty; it now carries two more AIM-260 there. `MurderHornetLightsOut`
hid the tank pylon under its tanks, so they floated. `verify_full_growler_fits` now fails the build
on any of the three, on both Growler airframes (`usn_ea-18g_2020`'s `SEST_NGJLongRange` got the
same outboard pair).

## Other stores near the tanks

The build also reports stores that sit as close to a fuel tank as the confirmed AGM-88G case
**and** are at least as heavy (0.0181 separation, 468 kg). Both halves matter — distance alone
flags about 20 per airframe, because SDBs (93 kg) and AMRAAM (162 kg) sit beside tanks routinely
and are fine. On the Super Hornets it names LRASM, AIM-174B, GBU-31 and JSOW fits. Those are
upstream's and are **not** changed — they are flagged for a human to look at.

## NGJ Long Range (2 tanks)

A maximum-persistence escort jamming fit: no anti-radiation missiles, both wing tanks, four
AIM-260 (outboard and fuselage) for self-defence. The NGJ pods do the work.

Two is the ceiling, not a choice. The Growler model carries exactly **one** pair of wing tank
pylons — the `fule_tank_point` mesh at stations 27/28. Stations 13/14 look like outboard pylons
but carry `sead_point`/`aam_point` racks, so a tank there would hang in mid-air with nothing under
it, and the centreline is the EW station: an earlier three-tank version put its third tank there,
inside the Growler's centre jamming equipment. Four wing tanks is not possible on this airframe.

Because the fit no longer needs a centreline station, both Growlers, `usn_ea-18g` and
`usn_ea-18g_2020`, carry it.
