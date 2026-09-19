# SEST USN 2027 Fixes

One file: `vessels/usn_ddg_arleigh_flt3_2027.ini`, U.S. Navy 2027's Flight III Arleigh Burke,
flattened so it no longer depends on a Modern US Navy hull that no longer exists.

**Why.** U.S. Navy 2027 (3606774881) is entirely `#!alias` patches over Modern US Navy
(3390330875) hulls, and Modern US Navy renames hulls almost daily. Its v567 (18 Sep 2026)
retired `usn_ddg_burke_f3.ini`; the 2027 Flight III patch still aliases it. The game then
fails to locate the base, the patch's own `[FlightDeck]` asks for an `[AirGroup]` the base
would have carried, and startup dies with `KeyNotFoundException: 'AirGroup'`.

**Why not re-point the alias.** The patch overwrites weapon slots 2 to 9 as Mk 41 cells; in
both new Flight III layouts slot 2 is gone and slot 3 is the Phalanx. The hull the game ran
happily until the rename was *old base + patch*, so that is what ships here: the retired base
(vendored under `donors/`, byte-faithful from the 2026-09-19 export) with the live patch merged
over it the way the alias mechanism does, section by section, key by key, patch wins.

**Retire it** when U.S. Navy 2027 re-points its alias: the builder exits with a message the
moment the live patch no longer targets `usn_ddg_burke_f3.ini`.

```bash
python3 integration/usn-2027-fixes/build_pack.py
python3 tools/check_alias_bases.py      # names any other alias whose base has moved
```
