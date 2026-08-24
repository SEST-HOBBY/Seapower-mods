# SEST Zumwalt CPS Fix

Repairs the DDG-1000 CPS variant in Mitchell600's **Modern US Navy** (Workshop item 3390330875)
so its hypersonic launcher actually exists.

## The symptom

The Zumwalt's IRCPS doesn't fire.

## The cause

`vessels/usn_ddg-1000_cps.ini` declares **`[WeaponSystem1]` twice** — once as the LMVLS
(the Advanced Payload Module that replaced the AGS guns, holding 12 rounds of `usn_ircps`)
and again as the first MK57 cell block. There is no `[WeaponSystem2]`:

```ini
[WeaponSystem1]  # LMVLS      <- SystemName=eu_lmvls_apm, AssociatedMagazine=WeaponMagazine_LMVLS
[WeaponSystem1]  # MK57 1     <- same section key
[WeaponSystem3]  # MK57 2
```

A section-keyed loader cannot return two systems from one key, so one of them is silently dropped.
And the IRCPS can only be launched from that one system — `mods-source/3629144864/ammunition/usn_ircps.ini`
declares `NumberOfLaunchers=1` / `Launcher1=eu_lmvls_apm`. Lose the LMVLS and the weapon is not on the ship.

Three independent lines of evidence:

1. **It is unique.** Sweeping all 734 units in `mods-source/` that declare weapon systems, this is the
   only file with a duplicate weapon-system number. Gaps, by contrast, appear in 83 shipped units that
   work fine — so the missing `[WeaponSystem2]` is harmless on its own. It's the duplicate that costs a launcher.
2. **Vanilla proves duplicates collapse silently.** `mods-source/_vanilla/original/vessels/fr_ss_agosta.ini`
   declares `[SensorSystem6]` twice with two genuinely different sonars (`DSUV-22`, `DUUX-2`),
   `NumberOfSensorSystems=8`, and no `[SensorSystem7]`. That sub loads and plays — because losing a
   redundant passive sonar is invisible. Losing a ship's only hypersonic launcher is not.
3. **The author's own backups have it right.** Both working copies in
   `mods-source/3390330875/ships/usn_ddg-1000/alt/` read `[WeaponSystem1] # LMVLS` then
   `[WeaponSystem2] # MK57 1`. Every other MK57 was correctly bumped by one (MK57 2 is
   `[WeaponSystem3]` … MK57 20 is `[WeaponSystem21]`). The shipped file is a regression — a single
   lost renumber.

### Second defect: the LMVLS has no fire control

Its entire sensor list is `AssociatedSensors=SensorSystem12`, on a hull that declares 11 sensors.

The CPS hull was derived from the base `usn_ddg-1000.ini` by consolidating four nav radars into two,
shifting everything after them down by 2 — the SM Datalink moved from `SensorSystem13` to
`SensorSystem11`, and 12 became the old towed-array slot. The MK57s were updated
(`SensorSystem3,SensorSystem11,SensorSystem12` — correct, plus a stale trailing entry) but the LMVLS
was not, leaving it with **no valid sensor at all**.

A dangling sensor reference is on its own tolerated — 30 units in the collection have one, including
the entire US Navy 2027 Arleigh Burke fleet — but those all keep a valid sensor alongside it.

The correct value is read off the control hull, not invented: all 20 VLS blocks in `usn_ddg-1000.ini`
use `SensorSystem3,SensorSystem13` (SPY-3 + SM Datalink), and CPS `SensorSystem11` is the byte-identical
SM Datalink block (`SystemName=eu_JUWL`). So the CPS equivalent is `SensorSystem3,SensorSystem11`.

## What this patch changes

23 lines, all edits in place — the file's line count is unchanged, and the build fails if it isn't:

| Change | Lines |
|---|---|
| `[WeaponSystem1]  # MK57 1` → `[WeaponSystem2]` — matches the scheme every other MK57 already follows, and the author's own backups | 1 |
| LMVLS `AssociatedSensors=SensorSystem12` → `SensorSystem3,SensorSystem11` | 1 |
| Stale trailing `SensorSystem12` dropped from the MK57 blocks (already inert; consistency only) | 20 |
| `[WeaponSystem23]` comment `#Mk46 GWS 1` → `#Mk46 GWS 2` (comment only — it's a different mount) | 1 |

Deliberately **not** changed: `NumberOfWeaponSystems=23` (already correct once renumbered, 1..23
contiguous); the `Container1_Hatch=` idiom (576 uses across the collection); anything in Euromod's
`usn_ircps.ini` (cross-mod edits affect every consumer, and none of them can make a launcher exist).

## Install

1. `tools\install-sest-packs.ps1`, or copy `SEST_Zumwalt_CPS/` into `Sea Power_Data\StreamingAssets\`.
2. It must sit **ABOVE Modern US Navy** in the Mod Manager — it carries a full replacement copy of
   `vessels/usn_ddg-1000_cps.ini` and the higher-listed mod wins the file.
   `data/load-order.tokens.txt` already places it there.
3. **Euromod must stay enabled.** The LMVLS launcher (`eu_lmvls_apm`, `eu_lmvls`) and the IRCPS
   ammunition both live in Euromod (3629144864), not in Modern US Navy.

## Verifying it worked

Put a Zumwalt CPS in a mission and open its weapons panel. Before the fix, either the LMVLS or the
first MK57 block is missing. After it you should see **22 launchers**: the LMVLS with 12× IRCPS,
plus 20 MK57 blocks and 2 Mk46 gun mounts. Assign an IRCPS to a land or surface target and it
should accept the assignment and launch.

## Rebuilding after an upstream update

```bash
python3 integration/zumwalt-cps/build_patch.py
```

It refuses to build if Modern US Navy has fixed the duplicate itself, if the two `[WeaponSystem1]`
blocks are no longer LMVLS-then-MK57, if a `[WeaponSystem2]` has appeared, or if `usn_ircps` stops
binding to `eu_lmvls_apm`. It then validates the result: contiguous section numbering, every
`AssociatedSensors`/`AssociatedMagazine` resolving, every launcher retaining at least one usable
sensor, every ammunition id resolving, every `SystemName` defined in the right `systems/` file, and
every `ContainerBase`/`Collider` resolving to a submodel section in the file or a primitive shape.
