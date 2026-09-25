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

- **NORTHERN FRONT II** — the user's Northern Front editor save, upgraded: the two `airbase_us`
  stand-ins are now the real `airbase_raaf_darwin` / `airbase_raaf_scherger` (their custom
  mission air groups are preserved), the date moves to 2026-08-24, and a five-ship civilian
  shipping lane plus a three-whale humpback pod (biologic sonar contacts) run along the
  Darwin–fleet axis. The original NORTHERN FRONT save is untouched.

## The editor-crash sweep

An aircraft or helicopter entry with no `LoadoutVariant=` whose winning unit file offers no
`Default` loadout crashes the mission editor's map panel ("An item with the same key has
already been added. Key: plaaf_kj-500"). The editor leaves the key out whenever a loadout was
never picked by hand, so it comes back with every save. The refresh chain fixes the mission it
refreshes; the installer deploys every mission here, so the rest are swept too:

```bash
python3 integration/missions/fix_loadout_variants.py --all          # report; exits 1 if any would change
python3 integration/missions/fix_loadout_variants.py --all --write  # write the type's first loadout
python3 tools/preflight.py --all                                    # fails on this crash, lists the rest
```

`--all` means what the installer deploys: every `.ini` here and under `scenarios/`, except
the stamped backups, which are snapshots and are left as they are. `preflight --all` also lists
every other dangling reference, mostly units and fits the older saves name that mods have
since dropped or renamed; those are for information and do not fail it. The sweep is
idempotent: the 25 Sep 2026 run wrote 32 `LoadoutVariant` lines into 9 files, and a second
run found nothing.

## Briefing maps

Every `SEST *.ini` has a `<mission>_briefing/` folder beside it: `BriefingMap_en.xml`
plus the chart it binds (`Assets[sest_<name>_map]`). Without that folder the right-hand
pane of the briefing screen is blank. The charts are generated from the missions' own
unit positions and committed:

```bash
pip install pillow
python3 integration/missions/build_briefing_maps.py
```

Re-run after moving units in a mission. The installer copies the folders next to the
missions. The campaign's own missions get theirs from the same renderer
(`briefing_maps.py`) when the campaign pack is built.
