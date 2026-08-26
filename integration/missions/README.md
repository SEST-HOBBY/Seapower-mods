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

- **SEST NF3 - \*** (11 scenarios) — small standalone fights carved out of NORTHERN FRONT III
  by `make_scenarios.py`, from 10 units (Northern Fleet Sortie) to 83 (Sanctioned Convoy).
  Every unit keeps the type, loadout, position and waypoints it has in the parent mission, and
  the parent is never modified — re-import a newer save, re-run, and the scenarios match it.
  See `scenarios/README.md`, which is generated alongside them.

## What actually reaches the game

`data/deploy-missions.txt` is the keep list. Without it the installer shipped every `.ini` here
recursively — 69 files, including 21 timestamped backups and nine whose internal name is
`_TempMission`, which is why the mission browser filled up. The manifest cuts that to 15: the
active NORTHERN FRONT III, one backup of it, the two SEST-authored missions and every carved
scenario.

The repo still keeps all 69 — they are your saves, and git is where they live safely. Only the
game-side list changed.

`tools/prune-missions.ps1` removes what earlier installs already deployed. It is a dry run by
default, archives rather than deletes unless told otherwise, and refuses to delete a mission the
repo has never seen without an explicit flag.
