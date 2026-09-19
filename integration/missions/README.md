# SEST Missions

Missions deployed by `tools/install-sest-packs.ps1` into
`StreamingAssets\user\missions\user_missions\`: new files are added, files with the same name
are overwritten, nothing is deleted and no backup copies are made (git is the history, so
`tools\import-mission.ps1` anything you edited in game before you install). The
`* backup-*.ini` files still in this folder are leftovers of the old backup scheme and are not
deployed; `install-sest-packs.ps1 -PurgeBackups` removes the ones already in the game.

- **SEST ANL Convoy - Coral Sea** — escort six ANL/RAN merchantmen (Auxilliary Merchant Pack)
  from the reef passage toward Port Moresby with HMAS Hobart, two Anzacs and HMAS Supply
  (SEST RAN Fleet) against a PLAN diesel patrol line (Kilo + two Type 039 variants).
  Free-play escort scenario, no scripted triggers.

- **SEST Indo-Pacific Land Assets** — a clean sandbox save, September 2026, built by
  `build_indo_pacific_showcase.py` to show the collection's modern land units placed the way
  they would really be deployed. 63 sites, 959 land units, 265 distinct unit types (187 of them
  from mods — every modded land unit the region can justify appears at least once). Blue: the
  northern RAAF bases with Patriot, THAAD and NASAMS, the US Marine rotation and a French
  battle group with SAMP/T at Darwin, Pine Gap, the EDCA sites in the Philippines with Typhon,
  NMESIS and a Patriot battalion line-up of every generation, a JGSDF Type 12 detachment at
  Batanes, PNG forward bases. Red: PLA garrisons on Fiery Cross, Subi, Mischief and Woody
  Island with HQ-9B/16/17/19/22 and YJ-12/62/83, a Russian S-400 regiment and Bastion battery
  at Biak, DF-21/26 and CJ-10 batteries in Papua, PLA combined-arms battalions at the Belt-and-
  Road industrial parks of Halmahera and Sulawesi, lodgements at Dili and Rabaul, and an
  Iranian-armed insurgent enclave in Mindanao with every technical the pickup mod makes.
  Neutral: TNI bases, Indonesian refineries and LNG plants, Malaysian and Bruneian ports,
  bridges, the Timor Sea rigs. A small naval layer on each side gives the defences a threat
  axis. Regenerate with `python3 integration/missions/build_indo_pacific_showcase.py`
  (`--density standard` or `light` for fewer defence units); every coordinate is real and
  nudged onto land by the mask, the reef bases and rigs excepted.

- **SEST Banda Front** — the showcase narrowed to one active zone, built by `build_banda_front.py`
  on the same datum: Borneo and Java through Sulawesi, the Moluccas, Timor and Papua to northern
  Australia and the Bismarck Sea, with the Sulu corner (Sabah, Zamboanga, Jolo, Marawi, Balabac)
  kept exactly as the showcase has it. Gone: the Philippines north of Mindanao, the Spratly and
  Paracel bases, Natuna, Australia south of Tindal, the Solomons. Added: 25 Borneo and Java sites
  (RMAF Labuan and Kuching, Bintulu LNG, Miri, Seria, Sandakan, Tawau, Pontianak, Tarakan, the
  Nusantara capital, Banjarmasin; Halim with a NASAMS battery, Tanjung Priok, Cilegon, Balongan,
  Cilacap, Semarang, Iswahyudi, Juanda, Koarmada II, the Suramadu bridge, Paiton, Bali, Ketapang),
  PLA lodgements at the Chinese-financed industrial parks (Tanah Kuning, Kendawangan, Batang with
  a PLAN amphibious group offshore, Tanjung Jati) and militant camps at Lahad Datu and Poso.
  Western Mindanao Command fields an air wing: six A-10C, six F-16CM, two MQ-9A, two MQ-9 ER,
  four Marine UH-1Y and two Navy HH-60 for CSAR; the two US destroyers stand in the Celebes Sea.
  Civil traffic is 27 ships on the real lanes (Lombok–Makassar VLCC and iron-ore route, the Java
  Sea container run, Darwin LNG north through the Banda and Molucca Seas, Tangguh LNG past
  Halmahera, Torres Strait, Vitiaz Strait, the Pelni liners, the Bali–Lombok and Surabaya–
  Banjarmasin ferries, Zamboanga–Sandakan, fishing fleets in the Arafura, Timor, Banda, Sulu and
  Celebes Seas) and 25 aircraft (A330/A320/A380 in Garuda, Lion, Qantas, SIA, Cathay, Air China,
  JAL, AirAsia, Korean, Asiana, PAL and Cebu Pacific liveries on real city pairs; Cessna 340s,
  Bonanzas and Hughes 500s on the short hops and rig runs). 72 sites, 794 land units, 199 types.
  Regenerate with `python3 integration/missions/build_banda_front.py`.

  Lanes are threaded through water by `sea_routes.py`: each lane is a chain of via points naming
  the corridor, and A* over the 1 km land mask (0.025° grid, a mild penalty for hugging the
  beach) joins them, keeping every via point and dropping the rest to the turns. Routed lanes are
  cached in `banda_front_lanes.json`, keyed on their via points, so a rebuild is instant and only
  a changed lane is re-routed; the generator then re-checks every leg against the mask at half-
  mile spacing before writing.

- **SEST Banda Front Lean** — the Banda Front editor save, every land site cut back to its core.
  The save (`SEST Banda Front edited.ini`, the hand-edited copy, authoritative and never
  rewritten) is read by `trim_land_sites.py`, which writes this copy beside it: the same 114 sites
  (106 formations plus the eight bridges and rigs the editor leaves outside any formation), the
  same positions and spread, 794 land units down to 396. Each site keeps its airbase, port, bridge
  or rig model, one search radar, ONE SAM battery (its fire-control radar and three launchers)
  and the THAAD or S-400 long-range section where it has one, the fuel farm, the ammo dump, a
  command element, one of each kind of industrial building, up to two anti-ship launchers, two
  ballistic-missile TELs, two drone launchers and, in a combat group, one vehicle of each class;
  the gun rings, the SHORAD swarm, the second and third batteries with their search radars,
  trucks, tents, bunkers and the crowd of technicals go. Every neutral land unit whose file can
  spawn aircraft - eleven TNI, RMAF, Balinese and Halim airfields on the vanilla `airfield_small_1`
  and Modern US `airfield_us` files, and the four Timor Sea helo rigs - carries `CustomAirGroup=True`
  with nothing under it, so no neutral E-3, P-3 or Sea King takes off on its own; blue and red air
  groups are as in the save. Regenerate with `python3 integration/missions/trim_land_sites.py`
  (`--dry-run` prints the plan and the numbers; `--tels`, `--coastal`, `--tbm`, `--drones`,
  `--technicals`, `--no-bmd` and `--cluster-nm` move the line; the output is byte-identical on
  every re-run).

  Two things the save itself carries, which the trim reports and leaves alone: the editor lays a
  saved formation out as rings at its 1.5 nm spacing, so a launcher stands 1-9 nm from the radar
  that guides it (outside the 0.8 nm guidance radius the generator honoured) in the save and in
  the Lean copy alike; and `check_weapon_employment.py` lists the same findings for the save, the
  generated original and the Lean copy (the NASAMS and SLAMRAAM launchers' datalink rounds, the
  three MLRS magazines, the Su-57's KH-58 seat), none of them introduced here.

- **NORTHERN FRONT II** — the user's Northern Front editor save, upgraded: the two `airbase_us`
  stand-ins are now the real `airbase_raaf_darwin` / `airbase_raaf_scherger` (their custom
  mission air groups are preserved), the date moves to 2026-08-24, and a five-ship civilian
  shipping lane plus a three-whale humpback pod (biologic sonar contacts) run along the
  Darwin–fleet axis. The original NORTHERN FRONT save is untouched.

## U.S. Navy 2027 hulls

`retarget_usn2027_hulls.py` moves a mission's U.S. Navy 2027 destroyers onto the Modern US Navy
hulls they are aliased to (`usn_ddg_arleigh_flt2A_119_2027` becomes `usn_ddg_burke_f2a_119`,
the Flight III becomes `usn_ddg_burke_f3_125`), dropping loadout variants the target does not
offer. U.S. Navy 2027 has no hulls of its own, only `#!alias` patches, and Modern US Navy renames
hulls almost daily; a mission that names the 2027 id inherits every rename as a crash or a ship
that never spawns. Runs as step 6d of the refresh chain; idempotent.

## Land defence and site builder

`build_land_defence.py` does for a Sea Power mission what Nuclear Option's editor does for a
base: name the asset, get the defences. It finds every airbase, port, installation, missile
site, TBM and drone launcher group on both sides, reads which air-defence layers each already
has (classifying every existing unit by the longest AAW missile it fires), and lays out only
the missing layers around it — gun ring on the perimeter, SHORAD a mile out, a medium battery
on the flank, an area battery forward, a search radar off to the side, BMD behind in the heavy
posture — oriented on the threat axis to the enemy side's units.

The kit is the collection's **modern** equipment by default (S-400, HQ-9B/16B/17, PAC-3 and
THAAD, NASAMS, Tor and Pantsir, SAMP/T, David's Sling), chosen by the site's nation; `--era
cold-war` gives vanilla S-300PS / Hawk / Rapier layouts instead. Every unit is resolved through
the load order, the variant whose `Nation` matches is picked, a battery is only used when its
radar really provides the guidance system its launchers name, and every launcher is placed
inside its radar's `ExternalGuidingSystemSearchRadius`. With the land-mask package installed
nothing is stood up in the sea (a rig at sea is skipped, not flooded).

```bash
python3 integration/missions/build_land_defence.py                       # plan for the active mission
python3 integration/missions/build_land_defence.py --write               # apply it
python3 integration/missions/build_land_defence.py --around Townsville --posture heavy --coastal --write
python3 integration/missions/build_land_defence.py --build fob --at -11.55 130.95 \
    --side Taskforce2 --nation china --label "Melville FOB" --posture heavy --coastal --write
python3 integration/missions/build_land_defence.py --list-sites          # what it sees, and what each site has
python3 integration/missions/build_land_defence.py --catalog             # what each doctrine resolves to, and from which mod
```

`--build` also creates the site itself (`fob`, `depot`, `radar_station`, `coastal_battery`,
`tbm_battery`, `drone_site`, `hq`) at a latitude/longitude before defending it. Re-runs add
nothing to a site that already has its layers, so the pass is safe in the refresh chain:
`tools\refresh-mission.ps1 -LandDefence` (with `-Posture heavy` for the full stack).

## Trimming a site back to its core

`trim_land_sites.py` is the other direction: a mission whose sites have grown into swarms (the
builder's layers on top of a generated site, or a save you have been adding to) is read, and a
copy is written in which every formation keeps the units that make it a recognisable
installation and loses the clutter, by rule and in file order, so the result is the same bytes
every time. No site is deleted: every formation keeps at least one member (its first member
when that unit carries the site's name), every unit outside a formation is kept, and the number
of formations per side is checked to be identical before the copy is written. A launcher is
kept only together with the radar that guides it; a battery is its radar plus the first
`--tels` launchers bound to it, ranked area over medium over SHORAD and by range. The builder's
`<site> Air Defence` layer defers to the site's own hand-placed battery and radar where it has
them. Every neutral unit that could spawn aircraft is given an empty `CustomAirGroup=True`
(`--keep-neutral-air` to leave them). The source is verified before, the result is verified
after, and every kept unit's block is checked byte for byte against the source before anything
is written.

```bash
python3 integration/missions/trim_land_sites.py --dry-run                    # the plan and the numbers
python3 integration/missions/trim_land_sites.py                              # SEST Banda Front edited -> SEST Banda Front Lean
python3 integration/missions/trim_land_sites.py --source "X" --out "X Lean" --tels 4 --no-bmd
```

Removal lives in `build_land_defence.py`'s `Mission` class next to the add path:
`remove_land_units(side, names)` deletes the blocks, renumbers the survivors densely, rewrites
every `<side>_FormationN` line (refusing to empty one), drops and renames every `NameOverride`
key, sets `NumberOf<side>LandUnits`, and stops on anything that still names a deleted unit;
`set_custom_air_group`, `set_name` and `set_description` do what they say; and `verify()` now
also checks that no formation is empty, that numbering is dense and in order for every side
and class, and that every unit named anywhere in the file exists.
