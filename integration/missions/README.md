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
