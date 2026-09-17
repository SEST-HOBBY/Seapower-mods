# SEST Missions

Missions deployed by `tools/install-sest-packs.ps1` into
`StreamingAssets\user\missions\user_missions\` (additive — never touches your own missions).

- **SEST ANL Convoy - Coral Sea** — escort six ANL/RAN merchantmen (Auxilliary Merchant Pack)
  from the reef passage toward Port Moresby with HMAS Hobart, two Anzacs and HMAS Supply
  (SEST RAN Fleet) against a PLAN diesel patrol line (Kilo + two Type 039 variants).
  Free-play escort scenario, no scripted triggers.

- **NORTHERN FRONT II** — the user's Northern Front editor save, upgraded: the two `airbase_us`
  stand-ins are now the real `airbase_raaf_darwin` / `airbase_raaf_scherger` (their custom
  mission air groups are preserved), the date moves to 2026-08-24, and a five-ship civilian
  shipping lane plus a three-whale humpback pod (biologic sonar contacts) run along the
  Darwin–fleet axis. The original NORTHERN FRONT save is untouched.

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
