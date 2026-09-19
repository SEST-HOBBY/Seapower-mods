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
