# SEST A-10C+

A selectable upgraded A-10C as a **new unit id**, `usaf_a-10c_plus`, sitting beside the
standard one rather than replacing it. Built from the A-10C mod (Workshop `3459682829`).

## What it adds

| | standard A-10C | A-10C+ |
|---|---|---|
| Maverick IR head | declared, **not registered** | registered and working |
| Litening targeting pod | — | `SensorSystem4` |
| AN/AAQ-28 laser designator | — | `SensorSystem5` |
| self-defence rails | AIM-9M | **AIM-9X**, all 11 loadouts |
| squadrons declared / defined | 7 / 2 | 2 / 2 |

## The author already designed this aircraft

The standard A-10C's hardpoint declares:

```
AssociatedSensors=SensorSystem2,SensorSystem5
```

while the file declares **three** sensors. `SensorSystem5` has never existed. The same mod
also ships, in its own `systems/sensors.ini`, a **Litening** pod and an **AN/AAQ-28** laser
designator that no aircraft in the collection references — defined, complete, unused.

The dangling slot and the two orphaned definitions are one unfinished thought. This pack
finishes it: the Litening at 4, the designator at 5, and the author's existing reference
resolves without being edited.

## Why a new unit and not a loadout

Sensors are declared per aircraft file. A loadout changes what hangs on the pylons and
nothing else, so an upgraded variant carrying a targeting pod has to be its own unit id —
the same reason the replenishment pack clones hulls rather than adding fits.

## The sensors are defined under our own names

`systems/` files merge **key by key** across the whole load order, and the highest mod wins
each key. Six mods define `[Litening]` and `[AN/AAQ-28]`, and the A-10C mod's copies sit
sixth. Referencing them by name would not give this aircraft the A-10C mod's pod at all — it
would silently bind to Euromod JMSDF's, which is worse where it matters:

| | intended (A-10C mod) | what a bare name gets (JMSDF) |
|---|---:|---:|
| identification multiplier | 2.2 | 3.0 |
| detection multiplier | 4.0 | 3.4 |
| looking down at clutter | 0.95 | 0.75 |
| **night vision** | **1.0** | **0.5** |
| designator range | 20 nm | 15 nm |

Worse at night than the Maverick head it is meant to beat. So the pack ships its own
`systems/sensors.ini` defining `SEST_A10C_FLIR` and `SEST_A10C_LASER`, lifted verbatim from
the A-10C mod, and the aircraft references those. Nothing can outrank a name nothing else
uses, and the builder refuses to run if either name ever appears upstream.

The FLIR copy also carries `UseIRValues=True`. That is not a performance key — the engine's
own comment says it affects the encyclopedia's type display — but the donor pod is
`Kind=Visual` and reads as a plain optical sight without it. 108 sensors across the
collection set it for the same reason.

This defect was raised by the other agent working this repo, and it was right.

## Why no ground-search radar

The real A-10C has none, and inventing one would be the only figure in this pack with
nothing behind it. The **Litening pod is the ground sensor**, and it is a large improvement
in exactly that role:

| | A-10_IR (Maverick head) | Litening |
|---|---:|---:|
| identification range multiplier | 1.8 | **2.2** |
| detection range multiplier | 3.2 | **4.0** |
| looking down at ground clutter | 0.7 | **0.95** |

## Two bugs, fixed in both aircraft

These are defects rather than upgrades, so **SEST Allied Fixes applies them to the standard
A-10C too**. Both packs call `integration/common/a10c.py` so the pair cannot drift.

**The infrared head was never registered.** `[SensorSystem2]` carries no `ModuleType=Sensor`
and no `Mount`. Of 2167 aircraft sensor blocks in this collection, 2126 declare
`ModuleType=Sensor`; this is one of the 41 that do not, and `usa_a-10a.ini` from the same
author is another. That is why the aircraft reads as having no infrared sensor at all.

**Seven squadrons, two liveries.** `usa_a-10c_squadrons.ini` declares `NumberOfSquadrons=7`
and defines two; the language file names two. Five squadrons resolve to no livery texture,
which is the likeliest reason the aircraft only ever appears in one scheme.

## What this pack cannot do

**Add a livery.** A skin is a `.png` texture, and `tools/export-mod-configs.ps1` copies text
configs only, so no texture is in this repo. The two liveries the mod does ship,
`a-10_81st_tfw.png` and `a-10_91st_tfw.png`, are in your game install and should both become
reachable now that the squadron count matches.

## Dependencies and load order

- **A-10C** (`3459682829`) — the base airframe, and both new sensors' definitions.
- **U.S. Navy 2027** (`3606774881`) — `usn_aim-9x`.

Deploys inside the consolidated SEST Integration Pack at tier 0.

## Build

```
python3 integration/a10c-plus/build_patch.py
```
